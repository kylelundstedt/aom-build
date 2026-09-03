"""Delegation trace log and evidence gating.

Append-only correlator over the four traceable contract kinds:

* routing-decision.v1
* delegation-attempt.v1
* evidence-manifest.v1
* publication-resolution.v1

This module is the *only* place that answers "what is the current
publication?" — see :func:`resolve_published`.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Protocol

from aom.contracts import validate

__all__ = [
    "AppendOnlyBackend",
    "AuthorityError",
    "InMemoryBackend",
    "JsonlBackend",
    "TraceLog",
    "evidence_satisfies",
    "resolve_published",
]

# kind → contract key
_CONTRACTS: dict[str, str] = {
    "routing-decision": "routing-decision.v1",
    "delegation-attempt": "delegation-attempt.v1",
    "evidence-manifest": "evidence-manifest.v1",
    "publication-resolution": "publication-resolution.v1",
}


# ---------------------------------------------------------------------------
# backends
# ---------------------------------------------------------------------------


class AppendOnlyBackend(Protocol):
    """A minimal append-only storage backend."""

    def write(self, entry: dict[str, Any]) -> None:
        """Append *entry* permanently. Must not mutate or delete prior entries."""
        ...

    def read_all(self) -> list[dict[str, Any]]:
        """Return all entries in insertion order."""
        ...


class InMemoryBackend:
    """In-memory list backend (for tests / ephemeral use)."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def write(self, entry: dict[str, Any]) -> None:
        self._entries.append(deepcopy(entry))

    def read_all(self) -> list[dict[str, Any]]:
        return deepcopy(self._entries)


class JsonlBackend:
    """JSONL file backend: one JSON object per line, append-only."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        # Touch so read_all works on a fresh backend.
        self._path.touch(exist_ok=True)

    def write(self, entry: dict[str, Any]) -> None:
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def read_all(self) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        with self._path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries


# ---------------------------------------------------------------------------
# TraceLog
# ---------------------------------------------------------------------------


class TraceLog:
    """Append-only delegation trace log.

    Each entry is a wrapper dict::

        {"kind": <kind>, "record": <validated-contract-record>}

    stored via an injected :class:`AppendOnlyBackend`.
    """

    def __init__(self, backend: AppendOnlyBackend) -> None:
        self._backend = backend

    def append(self, kind: str, record: dict[str, Any]) -> dict[str, Any]:
        """Validate *record* against the contract for *kind*, then append.

        Returns the stored wrapper entry (a copy).

        :raises KeyError: if *kind* is not one of the four traceable kinds.
        :raises aom.contracts.ContractError: if *record* fails validation.
        """
        if kind not in _CONTRACTS:
            raise KeyError(f"unknown trace kind: {kind!r}")
        validated = validate(_CONTRACTS[kind], deepcopy(record))
        entry = {"kind": kind, "record": validated}
        self._backend.write(entry)
        return deepcopy(entry)

    def entries(self) -> list[dict[str, Any]]:
        """Return a deep copy of all entries (mutation-safe)."""
        return self._backend.read_all()

    def chain_for_task(self, task_id: str) -> dict[str, Any]:
        """Assemble the navigable trace chain for *task_id*.

        Walks all entries and collects:

        * routing decisions whose ``task_ref.id == task_id``
        * delegation attempts whose ``task_ref.id == task_id``
        * evidence manifests whose ``subject_ref.id`` matches any attempt's
          ``worker.run_id``
        * publication resolutions referenced by attempts via ``candidate_ref``
          (optional — the publication-resolution ``product_id`` must match the
          candidate ref id).

        Returns a dict with keys ``task_id``, ``routing_decisions``,
        ``attempts``, ``evidence``, ``publications``, ``gaps``.

        ``gaps`` is a list of typed strings:

        * ``"no_routing_decision"`` — no routing decision for this task
        * ``"attempt_without_evidence:<run_id>"`` — an attempt has no matching
          evidence manifest
        * ``"evidence_pending:<evidence_id>"`` — capture_state is pending
        * ``"evidence_mismatched:<evidence_id>"`` — capture_state is mismatched
        * ``"evidence_unavailable:<evidence_id>"`` — capture_state is unavailable
        """
        routing_decisions: list[dict[str, Any]] = []
        attempts: list[dict[str, Any]] = []
        evidence: list[dict[str, Any]] = []
        publications: list[dict[str, Any]] = []
        gaps: list[str] = []

        all_entries = self.entries()

        # First pass: routing decisions and attempts for this task.
        for entry in all_entries:
            kind = entry["kind"]
            rec = entry["record"]
            if kind == "routing-decision":
                if rec.get("task_ref", {}).get("id") == task_id:
                    routing_decisions.append(rec)
            elif kind == "delegation-attempt" and rec.get("task_ref", {}).get("id") == task_id:
                attempts.append(rec)

        if not routing_decisions:
            gaps.append("no_routing_decision")

        # Collect run_ids and candidate_ref ids from attempts.
        run_ids: set[str] = set()
        candidate_ref_ids: set[str] = set()
        for att in attempts:
            worker = att.get("worker") or {}
            run_id = worker.get("run_id")
            if run_id:
                run_ids.add(run_id)
            cand = att.get("candidate_ref")
            if cand and cand.get("domain") == "publication":
                candidate_ref_ids.add(cand.get("id", ""))

        # Second pass: evidence manifests and publication resolutions.
        evidence_by_run: dict[str, dict[str, Any]] = {}
        for entry in all_entries:
            kind = entry["kind"]
            rec = entry["record"]
            if kind == "evidence-manifest":
                subject_id = rec.get("subject_ref", {}).get("id", "")
                if subject_id in run_ids:
                    evidence.append(rec)
                    evidence_by_run[subject_id] = rec
            elif kind == "publication-resolution":
                if rec.get("product_id") in candidate_ref_ids:
                    publications.append(rec)

        # Gap detection: attempts without evidence.
        for att in attempts:
            run_id = (att.get("worker") or {}).get("run_id")
            if run_id and run_id not in evidence_by_run:
                gaps.append(f"attempt_without_evidence:{run_id}")

        # Gap detection: evidence in non-durable states.
        for ev in evidence:
            ev_id = ev.get("evidence_id", "")
            state = ev.get("capture_state")
            if state == "pending":
                gaps.append(f"evidence_pending:{ev_id}")
            elif state == "mismatched":
                gaps.append(f"evidence_mismatched:{ev_id}")
            elif state == "unavailable":
                gaps.append(f"evidence_unavailable:{ev_id}")

        return {
            "task_id": task_id,
            "routing_decisions": routing_decisions,
            "attempts": attempts,
            "evidence": evidence,
            "publications": publications,
            "gaps": gaps,
        }


# ---------------------------------------------------------------------------
# evidence gating
# ---------------------------------------------------------------------------


def evidence_satisfies(manifest: dict[str, Any], candidate_commit: str | None) -> tuple[bool, str]:
    """Acceptance gate for an evidence manifest.

    Returns ``(True, "ok")`` when the manifest is durable AND verified AND the
    *candidate_commit* is either ``None`` or present in
    ``manifest["commits"]``.

    Otherwise returns ``(False, reason)`` where *reason* is one of:

    * ``"pending"`` — capture_state is ``"pending"``
    * ``"unavailable"`` — capture_state is ``"unavailable"``
    * ``"mismatched"`` — capture_state is ``"mismatched"`` (always False)
    * ``"not_verified"`` — capture_state is durable but ``verified_at`` absent
    * ``"commit_not_in_evidence"`` — durable + verified but the candidate
      commit is not in the manifest's commits list
    * ``"ok"`` — all conditions satisfied
    """
    state = manifest.get("capture_state")

    if state == "pending":
        return False, "pending"
    if state == "unavailable":
        return False, "unavailable"
    if state == "mismatched":
        return False, "mismatched"

    # From here we expect durable (the only remaining valid enum value).
    if state != "durable":
        return False, "pending"  # defensive default for unexpected states

    if not manifest.get("verified_at"):
        return False, "not_verified"

    if candidate_commit is not None:
        commits = manifest.get("commits", [])
        if candidate_commit not in commits:
            return False, "commit_not_in_evidence"

    return True, "ok"


# ---------------------------------------------------------------------------
# publication authority
# ---------------------------------------------------------------------------


class AuthorityError(Exception):
    """Raised when a state-authority query cannot be answered."""


def resolve_published(
    trace_log: TraceLog,
    product_id: str,
    channel: str,
    memory_claims: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Answer "what is the current publication for (product_id, channel)?".

    This is the **only** function allowed to answer current-publication
    queries. It picks the publication-resolution entry with the highest
    ``registry_revision`` among entries matching *product_id* and *channel*.

    Memory claims **never** substitute for a resolution — if no
    publication-resolution entry exists, :class:`AuthorityError` is raised
    with message ``"no_publication_resolution"``.

    When *memory_claims* disagree with the resolver's version, the returned
    dict includes an extra top-level key ``"stale_memory_flags"`` listing the
    memory ids whose version differs. Because the publication-resolution.v1
    schema has ``additionalProperties: false``, we cannot embed the flag list
    inside the validated record. Instead we return a **wrapper**::

        {
            "resolution": <validated publication-resolution record>,
            "stale_memory_flags": [<memory_id>, ...],  # may be empty
        }

    When *memory_claims* is ``None`` or empty, ``stale_memory_flags`` is an
    empty list.

    :raises AuthorityError: ``"no_publication_resolution"`` when no matching
        publication-resolution entry exists.
    """
    matching: list[dict[str, Any]] = []
    for entry in trace_log.entries():
        if entry["kind"] != "publication-resolution":
            continue
        rec = entry["record"]
        if rec.get("product_id") == product_id and rec.get("channel") == channel:
            matching.append(rec)

    if not matching:
        raise AuthorityError("no_publication_resolution")

    # Highest registry_revision wins. Revisions may be int or string.
    def _rev_key(r: dict[str, Any]) -> tuple[int, int | str]:
        rev = r.get("registry_revision")
        if isinstance(rev, int):
            return (1, rev)
        try:
            return (1, int(rev))
        except (TypeError, ValueError):
            return (0, str(rev))

    best = max(matching, key=_rev_key)
    resolved_version = best.get("version")

    stale_flags: list[str] = []
    if memory_claims:
        for claim in memory_claims:
            claim_id = claim.get("memory_id") or claim.get("id", "")
            claim_version = claim.get("version")
            if claim_version is not None and claim_version != resolved_version and claim_id:
                stale_flags.append(claim_id)

    return {
        "resolution": best,
        "stale_memory_flags": stale_flags,
    }
