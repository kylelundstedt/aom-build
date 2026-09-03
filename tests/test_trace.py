"""Tests for aom.trace — delegation trace log + evidence gating."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aom.contracts import ContractError
from aom.trace import (
    AuthorityError,
    InMemoryBackend,
    JsonlBackend,
    TraceLog,
    evidence_satisfies,
    resolve_published,
)

# ---------------------------------------------------------------------------
# fixtures — load the mutually-consistent contract examples
# ---------------------------------------------------------------------------

EXAMPLES = Path(__file__).resolve().parents[1] / "contracts" / "examples"


@pytest.fixture
def routing_decision():
    return json.loads((EXAMPLES / "routing-decision.v1.example.json").read_text())


@pytest.fixture
def delegation_attempt():
    return json.loads((EXAMPLES / "delegation-attempt.v1.example.json").read_text())


@pytest.fixture
def evidence_manifest():
    return json.loads((EXAMPLES / "evidence-manifest.v1.example.json").read_text())


@pytest.fixture
def publication_resolution():
    return json.loads((EXAMPLES / "publication-resolution.v1.example.json").read_text())


@pytest.fixture
def populated_trace(
    routing_decision, delegation_attempt, evidence_manifest, publication_resolution
):
    """A TraceLog with the four mutually-consistent example records."""
    trace = TraceLog(InMemoryBackend())
    trace.append("routing-decision", routing_decision)
    trace.append("delegation-attempt", delegation_attempt)
    trace.append("evidence-manifest", evidence_manifest)
    trace.append("publication-resolution", publication_resolution)
    return trace


# ---------------------------------------------------------------------------
# append / validation
# ---------------------------------------------------------------------------


class TestAppend:
    def test_append_validates_and_returns_entry(self, routing_decision):
        trace = TraceLog(InMemoryBackend())
        entry = trace.append("routing-decision", routing_decision)
        assert entry["kind"] == "routing-decision"
        assert entry["record"]["decision_id"] == "route-FREDDIE-184-v1"

    def test_append_rejects_invalid_record(self, routing_decision):
        trace = TraceLog(InMemoryBackend())
        bad = dict(routing_decision)
        bad.pop("decided_at")  # remove required field
        with pytest.raises(ContractError):
            trace.append("routing-decision", bad)

    def test_append_rejects_unknown_kind(self):
        trace = TraceLog(InMemoryBackend())
        with pytest.raises(KeyError):
            trace.append("bogus", {})

    def test_append_only_does_not_mutate_earlier(self, routing_decision, delegation_attempt):
        trace = TraceLog(InMemoryBackend())
        trace.append("routing-decision", routing_decision)
        trace.append("delegation-attempt", delegation_attempt)
        entries = trace.entries()
        assert len(entries) == 2
        # Mutate the returned copy; internal state must be unaffected.
        entries[0]["record"]["decision_id"] = "tampered"
        entries2 = trace.entries()
        assert entries2[0]["record"]["decision_id"] == "route-FREDDIE-184-v1"


# ---------------------------------------------------------------------------
# entries() copy safety
# ---------------------------------------------------------------------------


class TestEntriesCopy:
    def test_entries_returns_copies(self, routing_decision):
        trace = TraceLog(InMemoryBackend())
        trace.append("routing-decision", routing_decision)
        e1 = trace.entries()
        e2 = trace.entries()
        assert e1 == e2
        e1[0]["record"]["decision_id"] = "changed"
        assert e2[0]["record"]["decision_id"] == "route-FREDDIE-184-v1"


# ---------------------------------------------------------------------------
# chain_for_task
# ---------------------------------------------------------------------------


class TestChainForTask:
    def test_full_chain_assembles(self, populated_trace):
        chain = populated_trace.chain_for_task("FREDDIE-184")
        assert chain["task_id"] == "FREDDIE-184"
        assert len(chain["routing_decisions"]) == 1
        assert len(chain["attempts"]) == 1
        assert len(chain["evidence"]) == 1
        # Publication is optional via candidate_ref; the example attempt has no
        # candidate_ref with domain "publication", so publications may be empty.
        # The key must exist regardless.
        assert "publications" in chain
        assert "gaps" in chain

    def test_chain_routing_links_to_task(self, populated_trace):
        chain = populated_trace.chain_for_task("FREDDIE-184")
        rd = chain["routing_decisions"][0]
        assert rd["task_ref"]["id"] == "FREDDIE-184"

    def test_chain_evidence_links_to_attempt_run(self, populated_trace):
        chain = populated_trace.chain_for_task("FREDDIE-184")
        att = chain["attempts"][0]
        ev = chain["evidence"][0]
        assert ev["subject_ref"]["id"] == att["worker"]["run_id"]

    def test_chain_no_gaps_for_consistent_fixture(self, populated_trace):
        chain = populated_trace.chain_for_task("FREDDIE-184")
        # The example evidence is durable + verified, so no evidence gaps.
        # There IS a routing decision, so no "no_routing_decision" gap.
        assert "no_routing_decision" not in chain["gaps"]
        assert not any(g.startswith("attempt_without_evidence") for g in chain["gaps"])
        assert not any(g.startswith("evidence_pending") for g in chain["gaps"])

    def test_no_routing_decision_gap(self, delegation_attempt):
        trace = TraceLog(InMemoryBackend())
        trace.append("delegation-attempt", delegation_attempt)
        chain = trace.chain_for_task("FREDDIE-184")
        assert "no_routing_decision" in chain["gaps"]

    def test_attempt_without_evidence_gap(self, routing_decision, delegation_attempt):
        trace = TraceLog(InMemoryBackend())
        trace.append("routing-decision", routing_decision)
        trace.append("delegation-attempt", delegation_attempt)
        # No evidence manifest appended.
        chain = trace.chain_for_task("FREDDIE-184")
        assert any(
            g == "attempt_without_evidence:run-FREDDIE-184-implement-1" for g in chain["gaps"]
        )

    def test_evidence_pending_gap(self, routing_decision, delegation_attempt, evidence_manifest):
        trace = TraceLog(InMemoryBackend())
        trace.append("routing-decision", routing_decision)
        trace.append("delegation-attempt", delegation_attempt)
        pending = dict(evidence_manifest)
        pending["capture_state"] = "pending"
        pending.pop("verified_at", None)
        trace.append("evidence-manifest", pending)
        chain = trace.chain_for_task("FREDDIE-184")
        assert "evidence_pending:evidence-FREDDIE-184" in chain["gaps"]

    def test_evidence_mismatched_gap(self, routing_decision, delegation_attempt, evidence_manifest):
        trace = TraceLog(InMemoryBackend())
        trace.append("routing-decision", routing_decision)
        trace.append("delegation-attempt", delegation_attempt)
        mismatched = dict(evidence_manifest)
        mismatched["capture_state"] = "mismatched"
        trace.append("evidence-manifest", mismatched)
        chain = trace.chain_for_task("FREDDIE-184")
        assert "evidence_mismatched:evidence-FREDDIE-184" in chain["gaps"]

    def test_empty_chain_for_nonexistent_task(self, populated_trace):
        chain = populated_trace.chain_for_task("NONEXISTENT")
        assert chain["routing_decisions"] == []
        assert chain["attempts"] == []
        assert chain["evidence"] == []
        assert "no_routing_decision" in chain["gaps"]


# ---------------------------------------------------------------------------
# evidence_satisfies
# ---------------------------------------------------------------------------


class TestEvidenceSatisfies:
    def test_durable_verified_commit_match_ok(self, evidence_manifest):
        commit = evidence_manifest["commits"][0]
        ok, reason = evidence_satisfies(evidence_manifest, commit)
        assert ok is True
        assert reason == "ok"

    def test_durable_verified_no_candidate_ok(self, evidence_manifest):
        ok, reason = evidence_satisfies(evidence_manifest, None)
        assert ok is True
        assert reason == "ok"

    def test_pending_false(self, evidence_manifest):
        m = dict(evidence_manifest)
        m["capture_state"] = "pending"
        ok, reason = evidence_satisfies(m, None)
        assert ok is False
        assert reason == "pending"

    def test_mismatched_false(self, evidence_manifest):
        m = dict(evidence_manifest)
        m["capture_state"] = "mismatched"
        ok, reason = evidence_satisfies(m, None)
        assert ok is False
        assert reason == "mismatched"

    def test_unavailable_false(self, evidence_manifest):
        m = dict(evidence_manifest)
        m["capture_state"] = "unavailable"
        ok, reason = evidence_satisfies(m, None)
        assert ok is False
        assert reason == "unavailable"

    def test_durable_no_verified_at_false(self, evidence_manifest):
        m = dict(evidence_manifest)
        m.pop("verified_at")
        ok, reason = evidence_satisfies(m, None)
        assert ok is False
        assert reason == "not_verified"

    def test_commit_not_in_evidence(self, evidence_manifest):
        ok, reason = evidence_satisfies(evidence_manifest, "ffff0000ffff0000")
        assert ok is False
        assert reason == "commit_not_in_evidence"


# ---------------------------------------------------------------------------
# resolve_published
# ---------------------------------------------------------------------------


def _make_pub(product_id, channel, version, revision):
    return {
        "schema": "iv.aom/publication-resolution/v1",
        "product_id": product_id,
        "channel": channel,
        "version": version,
        "manifest_ref": {
            "uri": f"product-registry://{product_id}/{version}",
            "digest": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
        },
        "publication_event_id": f"event-{version}",
        "registry_revision": revision,
        "published_at": "2026-09-03T13:00:00Z",
        "resolved_at": "2026-09-03T14:07:00Z",
        "producer": {"id": "freddie-wap-adapter", "version": "0.1.0"},
    }


class TestResolvePublished:
    def test_highest_revision_wins(self):
        trace = TraceLog(InMemoryBackend())
        trace.append("publication-resolution", _make_pub("p1", "prod", "v1", 100))
        trace.append("publication-resolution", _make_pub("p1", "prod", "v2", 200))
        trace.append("publication-resolution", _make_pub("p1", "prod", "v0", 50))
        result = resolve_published(trace, "p1", "prod")
        assert result["resolution"]["version"] == "v2"
        assert result["resolution"]["registry_revision"] == 200

    def test_no_entries_raises(self):
        trace = TraceLog(InMemoryBackend())
        with pytest.raises(AuthorityError, match="no_publication_resolution"):
            resolve_published(trace, "p1", "prod")

    def test_channel_filtering(self):
        trace = TraceLog(InMemoryBackend())
        trace.append("publication-resolution", _make_pub("p1", "prod", "v1", 100))
        trace.append("publication-resolution", _make_pub("p1", "staging", "v2", 200))
        result = resolve_published(trace, "p1", "prod")
        assert result["resolution"]["version"] == "v1"

    def test_stale_memory_flag(self):
        trace = TraceLog(InMemoryBackend())
        trace.append("publication-resolution", _make_pub("p1", "prod", "v2", 200))
        claims = [{"memory_id": "mem-001", "version": "v1"}]
        result = resolve_published(trace, "p1", "prod", memory_claims=claims)
        assert result["resolution"]["version"] == "v2"
        assert "mem-001" in result["stale_memory_flags"]

    def test_matching_memory_no_flags(self):
        trace = TraceLog(InMemoryBackend())
        trace.append("publication-resolution", _make_pub("p1", "prod", "v2", 200))
        claims = [{"memory_id": "mem-001", "version": "v2"}]
        result = resolve_published(trace, "p1", "prod", memory_claims=claims)
        assert result["stale_memory_flags"] == []

    def test_no_memory_claims_no_flags(self):
        trace = TraceLog(InMemoryBackend())
        trace.append("publication-resolution", _make_pub("p1", "prod", "v2", 200))
        result = resolve_published(trace, "p1", "prod")
        assert result["stale_memory_flags"] == []


# ---------------------------------------------------------------------------
# JSONL backend round-trip
# ---------------------------------------------------------------------------


class TestJsonlBackend:
    def test_roundtrip_chain(
        self,
        tmp_path,
        routing_decision,
        delegation_attempt,
        evidence_manifest,
        publication_resolution,
    ):
        path = tmp_path / "trace.jsonl"
        backend = JsonlBackend(path)
        trace = TraceLog(backend)
        trace.append("routing-decision", routing_decision)
        trace.append("delegation-attempt", delegation_attempt)
        trace.append("evidence-manifest", evidence_manifest)
        trace.append("publication-resolution", publication_resolution)

        # Reload from disk.
        backend2 = JsonlBackend(path)
        trace2 = TraceLog(backend2)
        chain = trace2.chain_for_task("FREDDIE-184")
        assert len(chain["routing_decisions"]) == 1
        assert len(chain["attempts"]) == 1
        assert len(chain["evidence"]) == 1

    def test_append_only_on_disk(self, tmp_path, routing_decision):
        path = tmp_path / "trace.jsonl"
        backend = JsonlBackend(path)
        trace = TraceLog(backend)
        trace.append("routing-decision", routing_decision)
        # File should have exactly one line.
        lines = path.read_text().strip().split("\n")
        assert len(lines) == 1
