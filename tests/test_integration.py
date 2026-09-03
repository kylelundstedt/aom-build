"""Cross-module integration: routing → delegation → evidence → publication trace.

Each module has its own unit tests; this file proves the modules compose into
the end-to-end chain described in contracts/README.md using the mutually
consistent contract examples plus live adapter/engine output.
"""

from __future__ import annotations

import copy
import json

import pytest

from aom import routing
from aom.contracts import repo_root
from aom.shelley_adapter import (
    AdapterError,
    CompletedResult,
    ShelleyWorkerAdapter,
    fixtures_dir,
)
from aom.snapshot import build_snapshot, render_markdown
from aom.trace import InMemoryBackend, TraceLog, evidence_satisfies, resolve_published
from tests.test_shelley_adapter import FakeRunner, full_capabilities


def fixture_text(name: str) -> str:
    return (fixtures_dir() / name).read_text()


def example(name: str) -> dict:
    path = repo_root() / "contracts" / "examples" / f"{name}.example.json"
    return json.loads(path.read_text())


@pytest.fixture()
def resolved_policy() -> dict:
    """The committed policy with fable/qwen resolved, as they will be post D-decision."""
    policy = routing.load_policy(repo_root() / "config" / "worker-routing.v1.json")
    patched = copy.deepcopy(policy)
    patched["worker_catalog"]["fable"]["availability"] = "verify_on_target"
    patched["worker_catalog"]["fable"]["target_model"] = "placeholder-fable"
    patched["worker_catalog"]["qwen_local"]["availability"] = "verify_on_target"
    patched["worker_catalog"]["qwen_local"]["target_model"] = "placeholder-qwen"
    return patched


def test_full_chain_composes(resolved_policy, tmp_path):
    log = TraceLog(InMemoryBackend())

    # 1. Routing decision from the live engine.
    decision = routing.decide(
        resolved_policy,
        task_ref={"domain": "work", "id": "FREDDIE-184", "revision": 7},
        inputs={
            "task_type": "product_change",
            "assurance": "high",
            "classification": "confidential",
            "locality": "hosted_allowed",
            "ambiguity": "high",
            "parallelizable": True,
            "budget_class": "standard",
        },
    )
    log.append("routing-decision", decision)

    # 2. Delegation attempt from the live adapter over fixture CLI output.
    runner = FakeRunner()
    runner.add(
        ("shelley", "client", "chat"),
        CompletedResult(returncode=0, stdout=fixture_text("chat_ok.json")),
    )
    adapter = ShelleyWorkerAdapter(runner=runner, capabilities=full_capabilities(), store={})
    attempt = adapter.create_run(
        {
            "delegation_id": "delegate-FREDDIE-184-implement",
            "attempt": 1,
            "task_ref": {"domain": "work", "id": "FREDDIE-184", "revision": 7},
            "accountable_agent_id": "freddie-product-hermes",
            "routing_decision_ref": {"domain": "routing", "id": decision["decision_id"]},
            "stage_id": "implement",
            "workspace": {
                "vm": "freddie-sflld",
                "path": "/home/exedev/freddie-sflld-worktrees/FREDDIE-184",
                "mode": "isolated_worktree",
            },
            "constraints": {
                "classification": "confidential",
                "data_locality": "hosted_allowed",
                "network": "restricted",
                "side_effects": "repository_write",
            },
            "idempotency_key": "FREDDIE-184:implement:1",
            "requested_role": "implementation",
            "requested_model": "gpt-5.6-luna",
            "prompt": "Implement the approved change.",
        }
    )
    log.append("delegation-attempt", attempt)

    # 3. Evidence + publication from the consistent contract examples, rebound
    #    to the live run id.
    evidence = example("evidence-manifest.v1")
    evidence["subject_ref"]["id"] = attempt["worker"]["run_id"]
    log.append("evidence-manifest", evidence)
    publication = example("publication-resolution.v1")
    log.append("publication-resolution", publication)

    # 4. Chain assembles without evidence gaps for the attempt.
    chain = log.chain_for_task("FREDDIE-184")
    assert chain["routing_decisions"] and chain["attempts"] and chain["evidence"]
    assert not any(g.startswith("attempt_without_evidence") for g in chain["gaps"])

    # 5. Evidence gate passes for the evidenced commit, fails for another.
    ok, reason = evidence_satisfies(evidence, evidence["commits"][0])
    assert ok, reason
    bad, reason = evidence_satisfies(evidence, "f" * 40)
    assert not bad and reason == "commit_not_in_evidence"

    # 6. Publication authority ignores a conflicting memory claim.
    resolved = resolve_published(
        log,
        "product:freddie-sflld",
        "production",
        memory_claims=[{"memory_id": "mem-stale", "version": "synthetic-92"}],
    )
    assert resolved["resolution"]["version"] == "synthetic-93"
    assert resolved["stale_memory_flags"] == ["mem-stale"]

    # 7. Management snapshot projects the live attempt.
    snapshot = build_snapshot(
        kanban_summary=[{"status": "running", "count": 1}],
        delegations=[attempt],
        publications=[
            {
                "domain": "publication",
                "id": publication["product_id"],
                "version": publication["version"],
            }
        ],
        source_revisions={"trace_log": len(log.entries())},
        attention_items=[],
    )
    assert snapshot["authority"] == "none_projection_only"
    assert snapshot["active_delegations"][0]["run_ref"]["id"] == attempt["worker"]["run_id"]
    md = render_markdown(snapshot)
    assert attempt["worker"]["actual_model"] in md


def test_committed_policy_fails_closed_on_unresolved_fable():
    """The real committed policy must refuse high-assurance routing today."""
    policy = routing.load_policy(repo_root() / "config" / "worker-routing.v1.json")
    with pytest.raises(routing.RoutingError) as exc:
        routing.decide(
            policy,
            task_ref={"domain": "work", "id": "FREDDIE-1"},
            inputs={
                "task_type": "product_change",
                "assurance": "high",
                "classification": "confidential",
                "locality": "hosted_allowed",
                "ambiguity": "low",
                "parallelizable": False,
                "budget_class": "standard",
            },
        )
    assert exc.value.code == "no_eligible_worker"


def test_vm_only_never_reaches_runner(resolved_policy):
    """Locality is enforced before any Shelley invocation."""
    calls: list[list[str]] = []

    class SpyRunner:
        def run(self, argv):
            calls.append(argv)
            raise AssertionError("runner must not be called")

    caps = full_capabilities()
    adapter = ShelleyWorkerAdapter(runner=SpyRunner(), capabilities=caps, store={})
    with pytest.raises(AdapterError) as exc:
        adapter.create_run(
            {
                "delegation_id": "d1",
                "attempt": 1,
                "task_ref": {"domain": "work", "id": "T1"},
                "accountable_agent_id": "freddie-product-hermes",
                "routing_decision_ref": {"domain": "routing", "id": "r1"},
                "stage_id": "execute",
                "workspace": {"vm": "freddie-sflld", "path": "/tmp/w", "mode": "read_only"},
                "constraints": {
                    "classification": "confidential",
                    "data_locality": "vm_only",
                    "network": "none",
                    "side_effects": "read_only",
                },
                "idempotency_key": "T1:execute:1",
                "requested_role": "local_processing",
                "requested_model": "gpt-5.6-luna",
                "prompt": "local work",
            }
        )
    assert exc.value.code == "policy_denied"
    assert calls == []
