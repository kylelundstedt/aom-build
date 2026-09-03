"""Tests for the Shelley worker adapter. Fully fixture/fake driven: the real
`shelley` binary is never invoked; all execution goes through FakeRunner."""

from __future__ import annotations

import json
from collections.abc import Callable
from copy import deepcopy

import pytest

from aom.contracts import validate
from aom.shelley_adapter import (
    AdapterError,
    CompletedResult,
    ShelleyWorkerAdapter,
    derive_state,
    fixtures_dir,
    probe_capabilities,
)

CONVERSATION_ID = "8e7c1a2b-0000-4000-8000-aa11bb22cc33"


def fixture_text(name: str) -> str:
    return (fixtures_dir() / name).read_text()


class FakeRunner:
    """Canned CommandRunner. Routes are (argv-prefix tuple) -> result or
    callable(argv) -> result. Every invocation is recorded."""

    def __init__(self) -> None:
        self.calls: list[list[str]] = []
        self.routes: list[
            tuple[tuple[str, ...], CompletedResult | Callable[[list[str]], CompletedResult]]
        ] = []

    def add(
        self,
        prefix: tuple[str, ...],
        result: CompletedResult | Callable[[list[str]], CompletedResult],
    ) -> None:
        self.routes.append((prefix, result))

    def run(self, argv: list[str]) -> CompletedResult:
        assert isinstance(argv, list), "runner must receive an argv list, never a shell string"
        assert all(isinstance(a, str) for a in argv)
        self.calls.append(list(argv))
        for prefix, result in self.routes:
            if tuple(argv[: len(prefix)]) == prefix:
                return result(argv) if callable(result) else result
        raise AssertionError(f"FakeRunner: no canned result for argv={argv!r}")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def full_capabilities(version: str | None = "0.959.914757635") -> dict:
    return {
        "create": True,
        "continue": True,
        "read": True,
        "wait": True,
        "search": True,
        "search_command": "search",
        "archive": True,
        "cancel": False,
        "shelley_version": version,
    }


def make_request(**overrides) -> dict:
    request = {
        "delegation_id": "delegate-FREDDIE-184-implement",
        "attempt": 1,
        "task_ref": {"domain": "work", "id": "FREDDIE-184", "revision": 7},
        "accountable_agent_id": "freddie-product-hermes",
        "routing_decision_ref": {
            "domain": "routing",
            "id": "route-FREDDIE-184-v1",
            "digest": "sha256:" + "c" * 64,
        },
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
            "deadline": "2026-09-04T18:00:00Z",
        },
        "idempotency_key": "FREDDIE-184:implement:1",
        "requested_role": "implementation",
        "requested_model": "gpt-5.6-luna",
        "prompt": "Implement the shelley worker adapter per the contract.",
    }
    request.update(overrides)
    return request


def make_adapter(
    runner: FakeRunner | None = None, capabilities: dict | None = None
) -> tuple[ShelleyWorkerAdapter, FakeRunner]:
    runner = runner or FakeRunner()
    adapter = ShelleyWorkerAdapter(
        runner=runner,
        capabilities=capabilities if capabilities is not None else full_capabilities(),
        store={},
    )
    return adapter, runner


def chat_ok(_argv: list[str]) -> CompletedResult:
    return CompletedResult(returncode=0, stdout=fixture_text("chat_ok.json"))


def adapter_with_accepted_run() -> tuple[ShelleyWorkerAdapter, FakeRunner, dict]:
    adapter, runner = make_adapter()
    runner.add(("shelley", "client", "chat"), chat_ok)
    record = adapter.create_run(make_request())
    assert record["state"] == "accepted"
    return adapter, runner, record


# ---------------------------------------------------------------------------
# Capability probe
# ---------------------------------------------------------------------------


def test_probe_full_help_advertises_all_except_cancel() -> None:
    runner = FakeRunner()
    runner.add(
        ("shelley", "client", "help"),
        CompletedResult(returncode=0, stdout=fixture_text("help_ok.txt")),
    )
    runner.add(
        ("shelley", "version"),
        CompletedResult(returncode=0, stdout=json.dumps({"version": "0.959.914757635"})),
    )
    caps = probe_capabilities(runner)
    assert caps == {
        "create": True,
        "continue": True,
        "read": True,
        "wait": True,
        "search": True,
        "search_command": "search",
        "archive": True,
        "cancel": False,
        "shelley_version": "0.959.914757635",
    }


def test_probe_missing_archive_fails_closed_and_archive_raises() -> None:
    runner = FakeRunner()
    runner.add(
        ("shelley", "client", "help"),
        CompletedResult(returncode=0, stdout=fixture_text("help_missing_archive.txt")),
    )
    runner.add(("shelley", "version"), CompletedResult(returncode=1, stdout=""))
    caps = probe_capabilities(runner)
    assert caps["archive"] is False
    assert caps["create"] is True
    assert caps["cancel"] is False
    assert caps["shelley_version"] is None

    # Archive on an adapter with this capability map must refuse before any
    # CLI call, even with a fully bound run.
    adapter, op_runner = make_adapter(capabilities=caps)
    op_runner.add(("shelley", "client", "chat"), chat_ok)
    record = adapter.create_run(make_request())
    calls_before = len(op_runner.calls)
    with pytest.raises(AdapterError) as excinfo:
        adapter.archive(record)
    assert excinfo.value.code == "unsupported"
    assert len(op_runner.calls) == calls_before  # no archive invocation


def test_probe_unparseable_help_fails_everything_closed() -> None:
    runner = FakeRunner()
    runner.add(
        ("shelley", "client", "help"),
        CompletedResult(returncode=0, stdout="\x00\x01 not help output\n"),
    )
    runner.add(("shelley", "version"), CompletedResult(returncode=1, stdout=""))
    caps = probe_capabilities(runner)
    for key in ("create", "continue", "read", "wait", "search", "archive"):
        assert caps[key] is False, key
    assert caps["cancel"] is False

    adapter = ShelleyWorkerAdapter(runner=FakeRunner(), capabilities=caps, store={})
    with pytest.raises(AdapterError) as excinfo:
        adapter.create_run(make_request())
    assert excinfo.value.code == "unsupported"


# ---------------------------------------------------------------------------
# create_run
# ---------------------------------------------------------------------------


def test_create_happy_path_record_validates_and_binds_conversation() -> None:
    adapter, runner = make_adapter()
    runner.add(("shelley", "client", "chat"), chat_ok)
    record = adapter.create_run(make_request())

    validate("delegation-attempt.v1", record)
    assert record["state"] == "accepted"
    assert record["adapter_revision"] == 1
    assert record["worker"]["backend"] == "shelley"
    assert record["worker"]["conversation_id"] == CONVERSATION_ID
    assert record["worker"]["requested_role"] == "implementation"
    assert record["worker"]["requested_model"] == "gpt-5.6-luna"
    assert record["worker"]["actual_model"] == "gpt-5.6-luna"
    assert record["worker"]["shelley_version"] == "0.959.914757635"
    assert record["warnings"] == []
    assert adapter.store[record["idempotency_key"]] is record

    argv = runner.calls[0]
    assert argv[:4] == ["shelley", "client", "chat", "-p"]
    assert "-model" in argv and argv[argv.index("-model") + 1] == "gpt-5.6-luna"
    assert "-cwd" in argv
    assert argv[argv.index("-cwd") + 1] == "/home/exedev/freddie-sflld-worktrees/FREDDIE-184"


def test_create_persists_pending_before_invoking_runner() -> None:
    runner = FakeRunner()
    observed_store_states: list[dict] = []

    def spy(argv: list[str]) -> CompletedResult:
        # At invocation time the store must already hold a pending record.
        observed_store_states.append(deepcopy(dict(adapter.store)))
        return chat_ok(argv)

    runner.add(("shelley", "client", "chat"), spy)
    adapter = ShelleyWorkerAdapter(runner=runner, capabilities=full_capabilities(), store={})
    record = adapter.create_run(make_request())

    assert len(observed_store_states) == 1
    pending = observed_store_states[0][record["idempotency_key"]]
    validate("delegation-attempt.v1", pending)
    assert pending["state"] == "pending"
    assert pending["worker"]["conversation_id"] == ""


def test_create_prepends_marker_and_prompt_is_single_argv_element() -> None:
    adapter, runner = make_adapter()
    runner.add(("shelley", "client", "chat"), chat_ok)
    adapter.create_run(make_request())

    argv = runner.calls[0]
    prompt = argv[argv.index("-p") + 1]
    assert prompt.startswith("[AOM-DELEGATION:delegate-FREDDIE-184-implement:1]\n")
    assert "Implement the shelley worker adapter" in prompt
    # The prompt — newlines and all — travels as ONE argv element; no shell
    # string is ever constructed from it.
    assert prompt.count("\n") == 1
    assert isinstance(argv, list)


def test_create_vm_only_with_hosted_model_policy_denied_runner_never_called() -> None:
    adapter, runner = make_adapter()
    request = make_request()
    request["constraints"]["data_locality"] = "vm_only"
    request["requested_model"] = "gpt-5.6-luna"  # hosted model id
    with pytest.raises(AdapterError) as excinfo:
        adapter.create_run(request)
    assert excinfo.value.code == "policy_denied"
    assert runner.calls == []
    assert adapter.store == {}  # denied before even the pending write


def test_create_vm_only_with_vm_local_model_allowed() -> None:
    adapter, runner = make_adapter()
    runner.add(("shelley", "client", "chat"), chat_ok)
    request = make_request()
    request["constraints"]["data_locality"] = "vm_only"
    request["requested_model"] = "vm:llama3.1-70b"
    record = adapter.create_run(request)
    validate("delegation-attempt.v1", record)
    assert record["state"] == "accepted"


def test_create_relative_workspace_path_invalid_request() -> None:
    adapter, runner = make_adapter()
    request = make_request()
    request["workspace"]["path"] = "relative/worktree"
    with pytest.raises(AdapterError) as excinfo:
        adapter.create_run(request)
    assert excinfo.value.code in ("invalid_request", "workspace_unavailable")
    assert runner.calls == []


def test_create_missing_constraints_invalid_request() -> None:
    adapter, runner = make_adapter()
    request = make_request()
    del request["constraints"]
    with pytest.raises(AdapterError) as excinfo:
        adapter.create_run(request)
    assert excinfo.value.code == "invalid_request"
    assert runner.calls == []


# ---------------------------------------------------------------------------
# Ambiguous create + reconcile
# ---------------------------------------------------------------------------


def _ambiguous_adapter() -> tuple[ShelleyWorkerAdapter, FakeRunner, dict]:
    adapter, runner = make_adapter()
    runner.add(
        ("shelley", "client", "chat"),
        CompletedResult(returncode=0, stdout=fixture_text("chat_garbage.txt")),
    )
    record = adapter.create_run(make_request())
    assert record["state"] == "pending"
    assert "retry_allowed" in record["warnings"]
    validate("delegation-attempt.v1", record)
    return adapter, runner, record


def test_reconcile_zero_matches_stays_pending_retry_allowed() -> None:
    adapter, runner, record = _ambiguous_adapter()
    runner.add(
        ("shelley", "client", "search"),
        CompletedResult(returncode=0, stdout=fixture_text("search_zero.jsonl")),
    )
    out = adapter.reconcile(record["idempotency_key"])
    validate("delegation-attempt.v1", out)
    assert out["state"] == "pending"
    assert "retry_allowed" in out["warnings"]
    # Reconciliation searched for the unique delegation marker.
    search_argv = runner.calls[-1]
    assert search_argv[:3] == ["shelley", "client", "search"]
    assert "[AOM-DELEGATION:delegate-FREDDIE-184-implement:1]" in search_argv


def test_reconcile_one_match_binds_and_marks_recovered() -> None:
    adapter, runner, record = _ambiguous_adapter()
    runner.add(
        ("shelley", "client", "search"),
        CompletedResult(returncode=0, stdout=fixture_text("search_one.jsonl")),
    )
    out = adapter.reconcile(record["idempotency_key"])
    validate("delegation-attempt.v1", out)
    assert out["state"] == "accepted"
    assert out["worker"]["conversation_id"] == CONVERSATION_ID
    assert "recovered_by_reconciliation" in out["warnings"]
    assert "retry_allowed" not in out["warnings"]


def test_reconcile_two_matches_duplicate_risk_never_picks_one() -> None:
    adapter, runner, record = _ambiguous_adapter()
    runner.add(
        ("shelley", "client", "search"),
        CompletedResult(returncode=0, stdout=fixture_text("search_two.jsonl")),
    )
    out = adapter.reconcile(record["idempotency_key"])
    validate("delegation-attempt.v1", out)
    assert out["state"] == "duplicate_risk"
    assert "duplicate_risk" in out["warnings"]
    # Must not silently bind either candidate.
    assert out["worker"]["conversation_id"] == ""


def test_reconcile_unknown_key_conversation_not_found() -> None:
    adapter, _ = make_adapter()
    with pytest.raises(AdapterError) as excinfo:
        adapter.reconcile("no-such-key")
    assert excinfo.value.code == "conversation_not_found"


# ---------------------------------------------------------------------------
# append_turn
# ---------------------------------------------------------------------------


def test_append_turn_happy_path_bumps_revision() -> None:
    adapter, runner, record = adapter_with_accepted_run()
    out = adapter.append_turn(record, "Please also add docstrings.", expected_revision=1)
    validate("delegation-attempt.v1", out)
    assert out["adapter_revision"] == 2
    assert out["state"] == "running"

    argv = runner.calls[-1]
    assert argv[:4] == ["shelley", "client", "chat", "-c"]
    assert argv[4] == CONVERSATION_ID
    prompt = argv[argv.index("-p") + 1]
    assert prompt.startswith("[AOM-DELEGATION:delegate-FREDDIE-184-implement:1]\n")
    assert "docstrings" in prompt


def test_append_turn_wrong_revision_conflict_and_no_cli_call() -> None:
    adapter, runner, record = adapter_with_accepted_run()
    calls_before = len(runner.calls)
    with pytest.raises(AdapterError) as excinfo:
        adapter.append_turn(record, "more work", expected_revision=99)
    assert excinfo.value.code == "revision_conflict"
    assert len(runner.calls) == calls_before


def test_append_turn_rejects_non_active_state() -> None:
    adapter, runner, record = adapter_with_accepted_run()
    runner.add(
        ("shelley", "client", "archive"),
        CompletedResult(returncode=0, stdout=""),
    )
    archived = adapter.archive(record)
    with pytest.raises(AdapterError) as excinfo:
        adapter.append_turn(archived, "too late", expected_revision=archived["adapter_revision"])
    assert excinfo.value.code == "invalid_request"


# ---------------------------------------------------------------------------
# read / get_run / derive_state
# ---------------------------------------------------------------------------


def test_read_completed_fixture_derives_completed() -> None:
    adapter, runner, record = adapter_with_accepted_run()
    runner.add(
        ("shelley", "client", "read"),
        CompletedResult(returncode=0, stdout=fixture_text("read_completed.jsonl")),
    )
    messages = adapter.read_messages(record)
    assert all(isinstance(m, dict) for m in messages)
    out = adapter.get_run(record)
    validate("delegation-attempt.v1", out)
    assert out["state"] == "completed"


def test_read_running_fixture_derives_running() -> None:
    adapter, runner, record = adapter_with_accepted_run()
    runner.add(
        ("shelley", "client", "read"),
        CompletedResult(returncode=0, stdout=fixture_text("read_running.jsonl")),
    )
    out = adapter.get_run(record)
    validate("delegation-attempt.v1", out)
    assert out["state"] == "running"


def test_read_non_json_line_provider_output_changed() -> None:
    adapter, runner, record = adapter_with_accepted_run()
    bad = fixture_text("read_running.jsonl") + "\nthis is not json at all\n"
    runner.add(("shelley", "client", "read"), CompletedResult(returncode=0, stdout=bad))
    with pytest.raises(AdapterError) as excinfo:
        adapter.read_messages(record)
    assert excinfo.value.code == "provider_output_changed"


def test_read_skips_blank_lines() -> None:
    adapter, runner, record = adapter_with_accepted_run()
    with_blanks = "\n\n" + fixture_text("read_completed.jsonl").replace("\n", "\n\n")
    runner.add(
        ("shelley", "client", "read"),
        CompletedResult(returncode=0, stdout=with_blanks),
    )
    messages = adapter.read_messages(record)
    assert derive_state(messages) == "completed"


def test_read_without_conversation_conversation_not_found() -> None:
    adapter, _ = make_adapter()
    adapter.store["k"] = adapter._base_record(make_request(), "run-x")  # pending, unbound
    with pytest.raises(AdapterError) as excinfo:
        adapter.read_messages(adapter.store["k"])
    assert excinfo.value.code == "conversation_not_found"


# ---------------------------------------------------------------------------
# archive / cancel
# ---------------------------------------------------------------------------


def test_archive_while_running_sets_warning() -> None:
    adapter, runner, record = adapter_with_accepted_run()
    assert record["state"] in ("accepted", "running")
    runner.add(
        ("shelley", "client", "archive"),
        CompletedResult(returncode=0, stdout=""),
    )
    out = adapter.archive(record)
    validate("delegation-attempt.v1", out)
    assert out["state"] == "archived"
    assert "archived_while_active" in out["warnings"]
    assert runner.calls[-1] == ["shelley", "client", "archive", CONVERSATION_ID]


def test_archive_cli_failure_raises_archive_failed() -> None:
    adapter, runner, record = adapter_with_accepted_run()
    runner.add(
        ("shelley", "client", "archive"),
        CompletedResult(returncode=1, stdout="", stderr="no such conversation"),
    )
    with pytest.raises(AdapterError) as excinfo:
        adapter.archive(record)
    assert excinfo.value.code == "archive_failed"
    assert record["state"] == "accepted"  # state not regressed by failure


def test_cancel_always_unsupported_never_fakes_success() -> None:
    adapter, runner, record = adapter_with_accepted_run()
    calls_before = len(runner.calls)
    with pytest.raises(AdapterError) as excinfo:
        adapter.cancel(record)
    assert excinfo.value.code == "unsupported"
    assert len(runner.calls) == calls_before  # no CLI invocation
    assert record["state"] == "accepted"


# ---------------------------------------------------------------------------
# Misc guarantees
# ---------------------------------------------------------------------------


def test_error_codes_match_contract() -> None:
    from aom.shelley_adapter import ERROR_CODES

    assert ERROR_CODES == {
        "unsupported",
        "invalid_request",
        "policy_denied",
        "provider_unavailable",
        "provider_output_changed",
        "model_unavailable",
        "workspace_unavailable",
        "timeout",
        "duplicate_risk",
        "conversation_not_found",
        "revision_conflict",
        "archive_failed",
    }
    with pytest.raises(ValueError):
        AdapterError("not_a_real_code")


def test_derive_state_heuristic_isolated() -> None:
    assert derive_state([]) == "running"
    assert derive_state([{"type": "user", "content": "hi"}]) == "running"
    assert derive_state([{"type": "assistant", "end_of_turn": True}]) == "completed"
    # Only the latest agent message decides; older end_of_turn doesn't stick
    # if a newer agent message is still in flight.
    msgs = [
        {"type": "assistant", "end_of_turn": True},
        {"type": "assistant", "end_of_turn": False},
    ]
    assert derive_state(msgs) == "running"


def test_all_returned_records_validate() -> None:
    """Sweep: every record returned across a full lifecycle validates."""
    adapter, runner = make_adapter()
    runner.add(("shelley", "client", "chat"), chat_ok)
    record = adapter.create_run(make_request())
    validate("delegation-attempt.v1", record)
    record = adapter.append_turn(record, "turn two", expected_revision=1)
    validate("delegation-attempt.v1", record)
    runner.add(
        ("shelley", "client", "read"),
        CompletedResult(returncode=0, stdout=fixture_text("read_completed.jsonl")),
    )
    record = adapter.get_run(record)
    validate("delegation-attempt.v1", record)
    assert record["state"] == "completed"
    runner.add(
        ("shelley", "client", "archive"),
        CompletedResult(returncode=0, stdout=""),
    )
    record = adapter.archive(record)
    validate("delegation-attempt.v1", record)
    # Completed (not active) → no archived_while_active warning.
    assert record["warnings"] == []
