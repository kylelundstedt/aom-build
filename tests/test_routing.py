"""Tests for the worker-routing engine (aom.routing)."""

from __future__ import annotations

import copy
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from aom.contracts import validate
from aom.routing import (
    RoutingError,
    decide,
    load_policy,
    record_deviation,
)

CONFIG = Path(__file__).resolve().parents[1] / "config" / "worker-routing.v1.json"


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


@pytest.fixture()
def policy():
    return load_policy(CONFIG)


def _resolved_policy():
    """Return an in-memory policy copy where fable and qwen_local are resolved."""
    pol = load_policy(CONFIG)
    pol = copy.deepcopy(pol)
    pol["worker_catalog"]["fable"]["availability"] = "verify_on_target"
    pol["worker_catalog"]["qwen_local"]["availability"] = "verify_on_target"
    return pol


def _task_ref():
    return {"domain": "work", "id": "FREDDIE-184", "revision": 7}


def _inputs(**overrides):
    base = {
        "task_type": "product_change",
        "assurance": "high",
        "classification": "confidential",
        "locality": "hosted_allowed",
        "ambiguity": "high",
        "parallelizable": True,
        "budget_class": "standard",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# load_policy
# ---------------------------------------------------------------------------


class TestLoadPolicy:
    def test_loads_and_has_digest(self, policy):
        assert policy["schema"] == "iv.aom/worker-routing-policy/v1"
        assert policy["__digest"].startswith("sha256:")
        assert len(policy["__digest"]) == len("sha256:") + 64

    def test_rejects_wrong_schema(self, tmp_path):
        bad = {"schema": "something-else/v2", "policy_id": "x", "version": 1}
        p = tmp_path / "bad.json"
        p.write_text(json.dumps(bad))
        with pytest.raises(RoutingError) as exc:
            load_policy(p)
        assert exc.value.code == "invalid_inputs"

    def test_digest_matches_file_sha256(self, policy):
        import hashlib

        raw = CONFIG.read_bytes()
        expected = "sha256:" + hashlib.sha256(raw).hexdigest()
        assert policy["__digest"] == expected


# ---------------------------------------------------------------------------
# decide — happy / failure paths
# ---------------------------------------------------------------------------


class TestDecide:
    def test_high_assurance_product_change_fails_no_eligible_worker(self, policy):
        """Real current state: fable is unresolved → formulate stage fails."""
        with pytest.raises(RoutingError) as exc:
            decide(policy, _task_ref(), _inputs())
        assert exc.value.code == "no_eligible_worker"

    def test_resolved_policy_full_4_stage_decision_validates(self):
        pol = _resolved_policy()
        decision = decide(
            pol,
            _task_ref(),
            _inputs(),
            now=datetime(2026, 9, 3, 14, 1, 0, tzinfo=UTC),
        )
        validate("routing-decision.v1", decision)
        assert decision["strategy"]["strategy_id"] == "high_assurance_product_change"
        stage_ids = [s["id"] for s in decision["strategy"]["stages"]]
        assert stage_ids == ["formulate", "critique", "implement", "final_review"]
        # formulate → fable, critique → sol, implement → [luna, qwen_local], final_review → sol
        by_id = {s["id"]: s for s in decision["strategy"]["stages"]}
        assert by_id["formulate"]["candidate_workers"] == ["fable"]
        assert by_id["critique"]["candidate_workers"] == ["sol"]
        assert by_id["implement"]["candidate_workers"] == ["luna", "qwen_local"]
        assert by_id["final_review"]["candidate_workers"] == ["sol"]
        # independent_of preserved
        assert by_id["critique"]["independent_of"] == ["formulate"]
        assert by_id["final_review"]["independent_of"] == ["implement"]
        # digest matches loaded file
        assert decision["policy"]["digest"] == pol["__digest"]

    def test_vm_only_local_sensitive_fails(self, policy):
        """vm_only + local_sensitive: qwen_local unresolved → no_eligible_worker."""
        with pytest.raises(RoutingError) as exc:
            decide(
                policy,
                _task_ref(),
                _inputs(
                    task_type="free_form",
                    assurance="standard",
                    locality="vm_only",
                    ambiguity="low",
                    parallelizable=False,
                ),
            )
        assert exc.value.code in ("no_eligible_worker", "policy_denied")

    def test_vm_only_hosted_only_locality_violation(self):
        """A test policy where the only eligible worker for a vm_only task is hosted."""
        pol = _resolved_policy()
        # Make the local_sensitive strategy's only eligible worker a hosted one.
        pol["strategies"]["local_sensitive"]["stages"][0]["eligible"] = ["luna"]
        with pytest.raises(RoutingError) as exc:
            decide(
                pol,
                _task_ref(),
                _inputs(
                    task_type="free_form",
                    assurance="standard",
                    locality="vm_only",
                    ambiguity="low",
                    parallelizable=False,
                ),
            )
        assert exc.value.code == "locality_violation"

    def test_read_only_grounding_review_high_vs_standard(self):
        """grounding_review stage is included when assurance=high, excluded when standard."""
        pol = _resolved_policy()
        # read_only_context's when has side_effects: read_only which isn't in our
        # inputs, so it won't match. We add a synthetic input key via a test-only
        # strategy that uses only our allowed fields. Actually simpler: directly
        # test the required_when logic by constructing a strategy that matches.
        #
        # But the policy strategy won't match. So let's build a minimal test by
        # adding a strategy to the policy that exercises required_when.
        pol = copy.deepcopy(pol)
        pol["strategies"]["test_readonly"] = {
            "when": {"task_type": "free_form", "assurance": ["standard", "high"]},
            "stages": [
                {"id": "research", "role": "evidence_retrieval", "eligible": ["luna"]},
                {
                    "id": "grounding_review",
                    "role": "source_grounding_review",
                    "eligible": ["sol"],
                    "required_when": {"assurance": "high"},
                },
            ],
        }

        # high assurance → grounding_review included
        dec_high = decide(
            pol,
            _task_ref(),
            _inputs(
                task_type="free_form",
                assurance="high",
                locality="hosted_allowed",
                ambiguity="low",
                parallelizable=False,
            ),
        )
        ids_high = [s["id"] for s in dec_high["strategy"]["stages"]]
        assert "grounding_review" in ids_high

        # standard assurance → grounding_review excluded
        dec_std = decide(
            pol,
            _task_ref(),
            _inputs(
                task_type="free_form",
                assurance="standard",
                locality="hosted_allowed",
                ambiguity="low",
                parallelizable=False,
            ),
        )
        ids_std = [s["id"] for s in dec_std["strategy"]["stages"]]
        assert "grounding_review" not in ids_std

    def test_invalid_inputs_missing_key(self, policy):
        bad = _inputs()
        del bad["assurance"]
        with pytest.raises(RoutingError) as exc:
            decide(policy, _task_ref(), bad)
        assert exc.value.code == "invalid_inputs"

    def test_invalid_inputs_bad_enum(self, policy):
        with pytest.raises(RoutingError) as exc:
            decide(policy, _task_ref(), _inputs(assurance="mega"))
        assert exc.value.code == "invalid_inputs"

    def test_unknown_strategy(self, policy):
        """Inputs that don't match any strategy → unknown_strategy."""
        with pytest.raises(RoutingError) as exc:
            decide(
                policy,
                _task_ref(),
                _inputs(
                    task_type="nonexistent_type",
                    assurance="standard",
                    locality="hosted_allowed",
                    ambiguity="low",
                    parallelizable=False,
                ),
            )
        assert exc.value.code == "unknown_strategy"

    def test_decision_validates_and_matches_digest(self):
        pol = _resolved_policy()
        decision = decide(pol, _task_ref(), _inputs())
        # Should not raise
        validate("routing-decision.v1", decision)
        assert decision["policy"]["digest"] == pol["__digest"]
        assert decision["policy"]["id"] == pol["policy_id"]
        assert decision["policy"]["version"] == pol["version"]

    def test_decision_is_deep_copy_not_shared(self):
        pol = _resolved_policy()
        decision = decide(pol, _task_ref(), _inputs())
        # Mutating the returned dict must not affect a second call.
        decision["strategy"]["stages"][0]["candidate_workers"].append("hacked")
        decision2 = decide(pol, _task_ref(), _inputs())
        assert "hacked" not in decision2["strategy"]["stages"][0]["candidate_workers"]

    def test_independence_violation_single_worker(self):
        """If independent stages share the same single candidate → independence_violation."""
        pol = _resolved_policy()
        pol = copy.deepcopy(pol)
        # Make formulate and critique both have only sol as eligible.
        pol["strategies"]["high_assurance_product_change"]["stages"][0]["eligible"] = ["sol"]
        pol["strategies"]["high_assurance_product_change"]["stages"][1]["eligible"] = ["sol"]
        with pytest.raises(RoutingError) as exc:
            decide(pol, _task_ref(), _inputs())
        assert exc.value.code == "independence_violation"


# ---------------------------------------------------------------------------
# record_deviation
# ---------------------------------------------------------------------------


class TestRecordDeviation:
    def test_deviation_new_id_original_unchanged(self):
        pol = _resolved_policy()
        decision = decide(
            pol,
            _task_ref(),
            _inputs(),
            now=datetime(2026, 9, 3, 14, 1, 0, tzinfo=UTC),
        )
        original_copy = copy.deepcopy(decision)

        dev = record_deviation(
            decision,
            stage_id="formulate",
            reason="fable unavailable",
            replacement_worker="sol",
            now=datetime(2026, 9, 3, 14, 5, 0, tzinfo=UTC),
        )

        # New id
        assert dev["decision_id"] != decision["decision_id"]
        assert "-dev1" in dev["decision_id"]

        # Original unchanged
        assert decision == original_copy

        # Deviation validates
        validate("routing-decision.v1", dev)

        # Deviation links to prior
        fb = dev["strategy"]["fallbacks"]
        assert any(
            f.get("deviation", {}).get("prior_decision_id") == decision["decision_id"] for f in fb
        )

    def test_deviation_replacement_worker_added(self):
        pol = _resolved_policy()
        decision = decide(
            pol,
            _task_ref(),
            _inputs(),
            now=datetime(2026, 9, 3, 14, 1, 0, tzinfo=UTC),
        )
        dev = record_deviation(
            decision,
            stage_id="formulate",
            reason="fable unavailable",
            replacement_worker="luna",
        )
        formulate = next(s for s in dev["strategy"]["stages"] if s["id"] == "formulate")
        assert "luna" in formulate["candidate_workers"]
        assert "deviations" in formulate.get("constraints", {})
