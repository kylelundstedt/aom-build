"""Worker-routing engine.

Loads a worker-routing policy, selects a strategy based on task inputs, and
produces an immutable routing decision that validates against the
``routing-decision.v1`` contract.

Design choices (documented for reviewers):
- ``required_capabilities`` in the decision is derived from the union of
  capabilities advertised in the policy ``worker_catalog`` for the eligible
  workers that survive filtering.  This keeps the decision self-describing
  without requiring every stage to re-declare capabilities.
- ``candidate_workers`` is the *filtered* eligible list (availability and
  locality filtering applied).  A stage with zero survivors is a hard error
  (``no_eligible_worker``) unless the strategy says ``fallback: "deny"`` in
  which case the whole decision is ``policy_denied``.
- ``decide`` returns a deep copy; the internal scratch dict is never returned
  directly.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aom.contracts import validate

POLICY_SCHEMA = "iv.aom/worker-routing-policy/v1"
DECISION_SCHEMA = "iv.aom/routing-decision/v1"

_REQUIRED_INPUT_KEYS = (
    "task_type",
    "assurance",
    "classification",
    "locality",
    "ambiguity",
    "parallelizable",
    "budget_class",
)

_VALID_INPUT_ENUMS = {
    "assurance": {"standard", "high", "publication_critical"},
    "classification": {"internal", "confidential", "personal", "published"},
    "locality": {"hosted_allowed", "vm_only", "named_endpoint_only"},
    "ambiguity": {"low", "medium", "high"},
    "budget_class": {"low", "standard", "high"},
}

# Worker catalog kinds that are *hosted* (not local / not named private endpoint).
_HOSTED_KINDS = {"shelley_model", "logical_mapping"}


class RoutingError(Exception):
    """A routing decision could not be produced.

    ``code`` is a machine-readable string from the mandatory set:
    policy_denied, no_eligible_worker, worker_unavailable, locality_violation,
    independence_violation, unknown_strategy, invalid_inputs.
    """

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def load_policy(path: str | Path) -> dict[str, Any]:
    """Load and structurally check a worker-routing policy JSON file.

    Returns the parsed policy dict (a deep copy of the file contents) and
    injects ``"__digest"`` = ``"sha256:<hex>"`` of the raw file bytes so that
    :func:`decide` can include it in decisions.
    """
    p = Path(path)
    raw = p.read_bytes()
    try:
        policy = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RoutingError("invalid_inputs", f"policy is not valid JSON: {exc}") from exc

    schema = policy.get("schema")
    if schema != POLICY_SCHEMA:
        raise RoutingError(
            "invalid_inputs",
            f"unsupported policy schema: {schema!r}; expected {POLICY_SCHEMA!r}",
        )

    for key in ("policy_id", "version", "worker_catalog", "strategies"):
        if key not in policy:
            raise RoutingError("invalid_inputs", f"policy missing required key: {key!r}")

    digest = "sha256:" + hashlib.sha256(raw).hexdigest()
    policy["__digest"] = digest
    return policy


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _match_clause(when: dict[str, Any], inputs: dict[str, Any]) -> int | None:
    """Return the number of matched keys, or ``None`` if no match.

    A ``when`` value may be a scalar (exact match) or a list (membership).
    """
    matched = 0
    for key, expected in when.items():
        if key not in inputs:
            return None
        actual = inputs[key]
        if isinstance(expected, list):
            if actual not in expected:
                return None
        else:
            if actual != expected:
                return None
        matched += 1
    return matched


def _validate_inputs(inputs: dict[str, Any]) -> None:
    if not isinstance(inputs, dict):
        raise RoutingError("invalid_inputs", "inputs must be an object")
    for key in _REQUIRED_INPUT_KEYS:
        if key not in inputs:
            raise RoutingError("invalid_inputs", f"inputs missing required key: {key!r}")
    # enum checks
    for key, allowed in _VALID_INPUT_ENUMS.items():
        val = inputs.get(key)
        if val not in allowed:
            raise RoutingError(
                "invalid_inputs",
                f"inputs[{key!r}]={val!r} not in {sorted(allowed)}",
            )
    if not isinstance(inputs["parallelizable"], bool):
        raise RoutingError("invalid_inputs", "inputs['parallelizable'] must be boolean")
    # task_type is a free-form string but must be a string
    if not isinstance(inputs["task_type"], str) or not inputs["task_type"]:
        raise RoutingError("invalid_inputs", "inputs['task_type'] must be a non-empty string")


def _select_strategy(
    strategies: dict[str, Any], inputs: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    best: tuple[str, dict[str, Any]] | None = None
    best_score = -1
    for strat_id, strat in strategies.items():
        score = _match_clause(strat.get("when", {}), inputs)
        if score is None:
            continue
        if score > best_score:
            best_score = score
            best = (strat_id, strat)
    if best is None:
        raise RoutingError("unknown_strategy", "no strategy matched the given inputs")
    return best


def _is_hosted(worker_entry: dict[str, Any]) -> bool:
    """A worker is *hosted* if its kind is a hosted/shelley kind.

    Named private endpoints and anything not in the hosted set are considered
    local / non-hosted.
    """
    return worker_entry.get("kind") in _HOSTED_KINDS


def _filter_workers(
    eligible: list[str],
    catalog: dict[str, Any],
    inputs: dict[str, Any],
) -> list[str]:
    """Apply availability + locality filtering to an eligible list."""
    locality = inputs.get("locality")
    strict_local = locality in ("vm_only", "named_endpoint_only")
    out: list[str] = []
    for w in eligible:
        entry = catalog.get(w)
        if entry is None:
            # Unknown worker id in policy — treat as ineligible (fail closed).
            continue
        availability = entry.get("availability")
        if availability == "unresolved":
            continue
        if strict_local and _is_hosted(entry):
            continue
        out.append(w)
    return out


def _capabilities_for(workers: list[str], catalog: dict[str, Any]) -> list[str]:
    """Union of catalog capabilities for the given workers, sorted, deduped."""
    caps: set[str] = set()
    for w in workers:
        entry = catalog.get(w, {})
        for c in entry.get("capabilities", []):
            caps.add(c)
    if not caps:
        # Fall back to a single placeholder so the schema's minItems:1 holds.
        # This branch should rarely fire because stages declare roles.
        caps = {"unspecified"}
    return sorted(caps)


def _check_independence(stages: list[dict[str, Any]]) -> None:
    """Enforce that independent stages don't share an identical single worker."""
    single: dict[str, str] = {}
    for st in stages:
        cands = st.get("candidate_workers", [])
        if len(cands) == 1:
            single[st["id"]] = cands[0]
    for st in stages:
        ind = st.get("independent_of")
        if not ind:
            continue
        for other_id in ind:
            if st["id"] in single and other_id in single and single[st["id"]] == single[other_id]:
                raise RoutingError(
                    "independence_violation",
                    f"stage {st['id']!r} is independent_of {other_id!r} but both have "
                    f"the same single candidate worker {single[st['id']]!r}",
                )


def _locality_violation_check(
    stage_id: str,
    eligible: list[str],
    catalog: dict[str, Any],
    inputs: dict[str, Any],
) -> None:
    """Raise locality_violation if a strict-locality stage *would* only use hosted workers.

    This is distinct from the silent filtering in ``_filter_workers``: if the
    *only* workers available for a vm_only/named_endpoint_only stage are hosted,
    we raise ``locality_violation`` rather than ``no_eligible_worker`` so the
    failure reason is precise.
    """
    locality = inputs.get("locality")
    if locality not in ("vm_only", "named_endpoint_only"):
        return
    non_hosted = [w for w in eligible if not _is_hosted(catalog.get(w, {}))]
    if not non_hosted and eligible:
        # All eligible are hosted → locality violation.
        raise RoutingError(
            "locality_violation",
            f"stage {stage_id!r} has only hosted workers for locality={locality!r}",
        )


def _rfc3339(dt: datetime) -> str:
    """Format a datetime as RFC3339 UTC with 'Z' suffix."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    dt_utc = dt.astimezone(UTC)
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def decide(
    policy: dict[str, Any],
    task_ref: dict[str, Any],
    inputs: dict[str, Any],
    *,
    producer_version: str = "0.1.0",
    now: datetime | None = None,
) -> dict[str, Any]:
    """Produce an immutable routing decision dict.

    See module docstring for behavior.  The returned dict validates against
    ``routing-decision.v1``.
    """
    _validate_inputs(inputs)
    if not isinstance(task_ref, dict) or "domain" not in task_ref or "id" not in task_ref:
        raise RoutingError("invalid_inputs", "task_ref must contain domain and id")

    catalog = policy["worker_catalog"]
    strategies = policy["strategies"]

    strat_id, strat = _select_strategy(strategies, inputs)

    fallback_deny = strat.get("fallback") == "deny"

    decision_stages: list[dict[str, Any]] = []
    for stage in strat.get("stages", []):
        # required_when gating
        rw = stage.get("required_when")
        if rw is not None and _match_clause(rw, inputs) is None:
            continue

        eligible_raw = stage.get("eligible", [])
        stage_id = stage["id"]

        # Locality violation: only hosted workers available for strict-local task.
        _locality_violation_check(stage_id, eligible_raw, catalog, inputs)

        filtered = _filter_workers(eligible_raw, catalog, inputs)

        if not filtered:
            if fallback_deny:
                raise RoutingError(
                    "policy_denied",
                    f"strategy {strat_id!r} has fallback=deny and stage "
                    f"{stage_id!r} has no eligible worker",
                )
            raise RoutingError(
                "no_eligible_worker",
                f"stage {stage_id!r} has no eligible workers after filtering",
            )

        out_stage: dict[str, Any] = {
            "id": stage_id,
            "role": stage["role"],
            "required_capabilities": _capabilities_for(filtered, catalog),
            "candidate_workers": list(filtered),
        }
        if "independent_of" in stage:
            out_stage["independent_of"] = list(stage["independent_of"])
        if "parallel_group" in stage:
            out_stage["parallel_group"] = stage["parallel_group"]
        decision_stages.append(out_stage)

    _check_independence(decision_stages)

    if not decision_stages:
        raise RoutingError(
            "no_eligible_worker",
            f"strategy {strat_id!r} produced no stages",
        )

    decided_at = _rfc3339(now or datetime.now(UTC))

    task_id = task_ref["id"]
    decision_id = f"route-{task_id}-{strat_id}-v1"

    decision: dict[str, Any] = {
        "schema": DECISION_SCHEMA,
        "decision_id": decision_id,
        "task_ref": copy.deepcopy(task_ref),
        "policy": {
            "id": policy["policy_id"],
            "version": policy["version"],
            "digest": policy["__digest"],
        },
        "inputs": copy.deepcopy(inputs),
        "strategy": {
            "strategy_id": strat_id,
            "stages": decision_stages,
        },
        "decided_at": decided_at,
        "producer": {"id": "worker-routing", "version": producer_version},
    }

    # carry forward policy-level fallbacks if present (as strategy fallbacks)
    if "fallbacks" in strat:
        decision["strategy"]["fallbacks"] = copy.deepcopy(strat["fallbacks"])
    elif fallback_deny:
        decision["strategy"]["fallbacks"] = [{"when": "worker_unavailable", "action": "deny"}]

    validate("routing-decision.v1", decision)
    return copy.deepcopy(decision)


def record_deviation(
    decision: dict[str, Any],
    stage_id: str,
    reason: str,
    replacement_worker: str | None,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a NEW decision recording a deviation for ``stage_id``.

    The original decision is never mutated.  The new decision:
    - has a decision_id suffixed with ``-dev<n>`` (n = number of deviations + 1)
    - links to the prior decision via a ``fallbacks`` entry on the strategy
    - records the deviation in the affected stage's ``constraints``
    """
    base = copy.deepcopy(decision)

    # Count existing deviations by scanning decision_id suffix.
    current_id = base["decision_id"]
    n = 1
    # If already has -devN, increment
    if "-dev" in current_id:
        _, _, suffix = current_id.rpartition("-dev")
        try:
            n = int(suffix) + 1
            base_id = current_id.rpartition("-dev")[0]
        except ValueError:
            base_id = current_id
    else:
        base_id = current_id

    base["decision_id"] = f"{base_id}-dev{n}"

    # Update decided_at
    base["decided_at"] = _rfc3339(now or datetime.now(UTC))

    # Record deviation on the affected stage constraints + update candidate list.
    for stage in base["strategy"]["stages"]:
        if stage["id"] == stage_id:
            constraints = stage.setdefault("constraints", {})
            deviations = constraints.setdefault("deviations", [])
            deviations.append(
                {
                    "reason": reason,
                    "replacement_worker": replacement_worker,
                    "prior_decision_id": decision["decision_id"],
                }
            )
            if replacement_worker is not None:
                # Add the replacement if not already present.
                cands = stage["candidate_workers"]
                if replacement_worker not in cands:
                    cands.append(replacement_worker)
            break

    # Link to prior decision via strategy fallbacks.
    fallbacks = base["strategy"].setdefault("fallbacks", [])
    fallbacks.append(
        {
            "when": "worker_unavailable",
            "action": "record_deviation_and_replan",
            "deviation": {
                "stage_id": stage_id,
                "reason": reason,
                "replacement_worker": replacement_worker,
                "prior_decision_id": decision["decision_id"],
            },
        }
    )

    validate("routing-decision.v1", base)
    return base
