"""Shelley worker adapter (contracts/shelley-worker-adapter.md).

Fixture/fake-driven façade over the experimental Shelley CLI. The real
binary is NEVER invoked by tests; all command execution goes through an
injected ``CommandRunner``. Every returned record is validated against
``delegation-attempt.v1`` via :mod:`aom.contracts`.

Security invariants enforced here:

- Commands are always argument arrays (never shell strings).
- Policy checks (data locality, workspace path) happen before any runner
  call.
- Raw CLI stdout is never exposed to callers; warnings are typed strings.
- ``cancel`` is unsupported by the verified CLI (v0.959) and always raises
  ``unsupported`` — the adapter never fakes success.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from aom.contracts import validate

ADAPTER_VERSION = "0.1.0"
ADAPTER_REVISION_START = 1
PRODUCER = {"id": "shelley-worker-adapter", "version": ADAPTER_VERSION}
CONTRACT = "delegation-attempt.v1"

ERROR_CODES = frozenset(
    {
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
)

ACTIVE_STATES = frozenset({"accepted", "running"})

# Models are considered hosted unless explicitly known to be VM-local
# endpoints. Fail closed: unknown → hosted → vm_only tasks are denied.
_VM_LOCAL_MODEL_PREFIXES = ("vm:", "local:", "ollama:")

_MARKER_TEMPLATE = "[AOM-DELEGATION:{delegation_id}:{attempt}]"


@dataclass
class CompletedResult:
    """Minimal completed-process shape returned by a CommandRunner."""

    returncode: int
    stdout: str
    stderr: str = ""


@runtime_checkable
class CommandRunner(Protocol):
    def run(self, argv: list[str]) -> CompletedResult: ...


class SubprocessRunner:
    """Thin wrapper over subprocess.run. argv is always a list; shell=True
    is never used and no prompt text is ever interpolated into a shell."""

    def __init__(self, timeout: float = 300.0):
        self.timeout = timeout

    def run(self, argv: list[str]) -> CompletedResult:
        if not isinstance(argv, list) or not all(isinstance(a, str) for a in argv):
            raise AdapterError("invalid_request", "argv must be a list[str]")
        try:
            proc = subprocess.run(
                argv,
                shell=False,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except FileNotFoundError as exc:
            raise AdapterError("provider_unavailable", str(exc)) from exc
        except subprocess.TimeoutExpired as exc:
            raise AdapterError("timeout", str(exc)) from exc
        return CompletedResult(
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )


class AdapterError(Exception):
    """Typed adapter failure. ``code`` is one of the contract error codes."""

    def __init__(self, code: str, detail: str = ""):
        if code not in ERROR_CODES:
            raise ValueError(f"unknown adapter error code: {code!r}")
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}" if detail else code)


def fixtures_dir() -> Path:
    """Directory with canned Shelley CLI outputs used by tests."""
    return Path(__file__).resolve().parents[2] / "fixtures" / "shelley"


def _fixture(name: str) -> str:
    return (fixtures_dir() / name).read_text()


# ---------------------------------------------------------------------------
# Capability probe (fail-closed drift guard)
# ---------------------------------------------------------------------------

_EXPECTED_SUBCOMMANDS = ("chat", "read", "list", "search", "archive")


def _parse_help_subcommands(help_text: str) -> set[str]:
    """Extract subcommand tokens from `shelley client help` output.

    The verified help lists subcommands as an indented word followed by a
    description. Unparseable/empty output yields an empty set, which fails
    every capability closed.
    """
    found: set[str] = set()
    for line in help_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        token = stripped.split()[0]
        if token in _EXPECTED_SUBCOMMANDS or token in ("help", "version"):
            found.add(token)
    return found


def probe_capabilities(runner: CommandRunner) -> dict[str, Any]:
    """Probe the installed Shelley CLI and return a capability map.

    Runs ``shelley client help`` and parses which subcommands are present.
    Any subcommand missing from the help output (or unparseable output)
    means the corresponding capability is False, and callers get
    ``AdapterError("unsupported")`` — this is the fail-closed drift guard.
    ``cancel`` is always False: the verified CLI has no cancel.
    """
    result = runner.run(["shelley", "client", "help"])
    if result.returncode != 0:
        result = runner.run(["shelley", "client", "-h"])
    subcommands: set[str] = set()
    if result.returncode == 0 and result.stdout.strip():
        subcommands = _parse_help_subcommands(result.stdout)

    read_ok = "read" in subcommands
    if "search" in subcommands:
        search_command: str | None = "search"
    elif "list" in subcommands:
        search_command = "list"
    else:
        search_command = None
    caps: dict[str, Any] = {
        "create": "chat" in subcommands,
        "continue": "chat" in subcommands,
        "read": read_ok,
        # -wait is a flag of `read`; verified help mentions it, but the flag
        # is only usable if `read` exists.
        "wait": read_ok and "-wait" in result.stdout,
        "search": search_command is not None,
        # Internal detail: which subcommand backs the search capability.
        "search_command": search_command,
        "archive": "archive" in subcommands,
        "cancel": False,
        "shelley_version": _probe_version(runner),
    }
    return caps


def _probe_version(runner: CommandRunner) -> str | None:
    try:
        result = runner.run(["shelley", "version"])
    except AdapterError:
        return None
    if result.returncode != 0:
        return None
    out = result.stdout.strip()
    if not out:
        return None
    try:
        parsed = json.loads(out)
    except json.JSONDecodeError:
        return out  # tolerate plain-text version output
    if isinstance(parsed, dict):
        version = parsed.get("version")
        return str(version) if version is not None else None
    if isinstance(parsed, str):
        return parsed
    return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _marker(delegation_id: str, attempt: int) -> str:
    return _MARKER_TEMPLATE.format(delegation_id=delegation_id, attempt=attempt)


def _is_hosted_model(model_id: str) -> bool:
    if not model_id:
        return True  # fail closed: unknown model → hosted
    lowered = model_id.strip().lower()
    return not lowered.startswith(_VM_LOCAL_MODEL_PREFIXES)


def _parse_json_lines(text: str) -> list[dict[str, Any]]:
    """Tolerant JSON-lines parser: skips blank lines; a non-blank line that
    is not a JSON object is a provider shape change, not garbage to ignore."""
    out: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AdapterError(
                "provider_output_changed", f"non-JSON line in CLI output: {line!r}"
            ) from exc
        if not isinstance(parsed, dict):
            raise AdapterError("provider_output_changed", f"JSON line is not an object: {line!r}")
        out.append(parsed)
    return out


def derive_state(messages: list[dict[str, Any]]) -> str:
    """Derive lifecycle state from provider messages.

    Heuristic, intentionally isolated so it is easy to change: the run is
    "completed" if the latest agent (assistant) message marks end_of_turn
    true; otherwise "running". "completed" means the turn ended, NOT that
    Hermes accepted the work.
    """
    latest_agent: dict[str, Any] | None = None
    for msg in messages:
        if msg.get("type") in ("assistant", "agent"):
            latest_agent = msg
    if latest_agent is not None and latest_agent.get("end_of_turn") is True:
        return "completed"
    return "running"


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


@dataclass
class ShelleyWorkerAdapter:
    """Façade over the Shelley CLI implementing the worker adapter contract.

    ``store`` is injected dict-like persistence for pending/accepted
    attempts, keyed by idempotency_key (tests pass a plain dict).
    """

    runner: CommandRunner
    capabilities: Mapping[str, Any]
    store: MutableMapping[str, dict[str, Any]] = field(default_factory=dict)

    # -- internal -----------------------------------------------------------

    def _require(self, capability: str) -> None:
        if not self.capabilities.get(capability, False):
            raise AdapterError(
                "unsupported", f"capability {capability!r} not advertised by shelley probe"
            )

    def _invoke(self, argv: list[str]) -> CompletedResult:
        result = self.runner.run(argv)
        if result.returncode != 0:
            raise AdapterError(
                "provider_unavailable",
                f"{argv[1:3]} exited {result.returncode}: {result.stderr.strip()}",
            )
        return result

    def _validate(self, record: dict[str, Any]) -> dict[str, Any]:
        return validate(CONTRACT, record)

    def _shelley_version(self) -> str | None:
        version = self.capabilities.get("shelley_version")
        return str(version) if version is not None else None

    def _base_record(self, request: Mapping[str, Any], run_id: str) -> dict[str, Any]:
        """Record skeleton shared by pending and accepted states. The worker
        block is present from the start (schema requires it);
        conversation_id is empty until bound."""
        now = _utc_now()
        worker: dict[str, Any] = {
            "backend": "shelley",
            "run_id": run_id,
            "conversation_id": "",
            "requested_role": str(request.get("requested_role") or ""),
            "requested_model": str(request.get("requested_model") or ""),
            "actual_model": str(request.get("requested_model") or ""),
            "adapter_version": ADAPTER_VERSION,
        }
        if self._shelley_version() is not None:
            worker["shelley_version"] = self._shelley_version()
        return {
            "schema": "iv.aom/delegation-attempt/v1",
            "delegation_id": request["delegation_id"],
            "attempt": int(request["attempt"]),
            "task_ref": dict(request["task_ref"]),
            "accountable_agent_id": request["accountable_agent_id"],
            "routing_decision_ref": dict(request["routing_decision_ref"]),
            "stage_id": request["stage_id"],
            "workspace": dict(request["workspace"]),
            "constraints": dict(request["constraints"]),
            "idempotency_key": request["idempotency_key"],
            "worker": worker,
            "state": "pending",
            "adapter_revision": 0,
            "warnings": [],
            "created_at": now,
            "updated_at": now,
            "producer": dict(PRODUCER),
        }

    def _touch(self, record: dict[str, Any]) -> dict[str, Any]:
        record["updated_at"] = _utc_now()
        return record

    def _warn(self, record: dict[str, Any], warning: str) -> None:
        if warning not in record["warnings"]:
            record["warnings"].append(warning)

    def _save(self, record: dict[str, Any]) -> dict[str, Any]:
        self._validate(record)
        self.store[record["idempotency_key"]] = record
        return record

    # -- validation of the create request ------------------------------------

    def _validate_request(self, request: Mapping[str, Any]) -> None:
        for field_name in (
            "delegation_id",
            "attempt",
            "task_ref",
            "accountable_agent_id",
            "routing_decision_ref",
            "stage_id",
            "workspace",
            "constraints",
            "idempotency_key",
            "prompt",
        ):
            if field_name not in request:
                raise AdapterError("invalid_request", f"missing field: {field_name}")
        workspace = request["workspace"]
        path = workspace.get("path", "") if isinstance(workspace, Mapping) else ""
        if not isinstance(path, str) or not path.startswith("/"):
            raise AdapterError(
                "workspace_unavailable", f"workspace.path must be absolute: {path!r}"
            )
        constraints = request["constraints"]
        if not isinstance(constraints, Mapping):
            raise AdapterError("invalid_request", "constraints must be an object")
        for key in ("classification", "data_locality", "network", "side_effects"):
            if key not in constraints:
                raise AdapterError("invalid_request", f"constraints missing: {key}")
        # Policy: local/private work must not be routed to a hosted model.
        # Checked BEFORE any runner invocation.
        if constraints["data_locality"] == "vm_only" and _is_hosted_model(
            str(request.get("requested_model") or "")
        ):
            raise AdapterError(
                "policy_denied",
                "vm_only data locality cannot use a hosted model: "
                f"{request.get('requested_model')!r}",
            )

    # -- operations -----------------------------------------------------------

    def create_run(self, request: dict[str, Any]) -> dict[str, Any]:
        """Create a run (at-least-once semantics; see contract).

        Order: validate → persist pending record → invoke CLI → bind
        conversation_id or leave pending for reconciliation.
        """
        self._require("create")
        self._validate_request(request)

        delegation_id = request["delegation_id"]
        attempt = int(request["attempt"])
        run_id = f"run-{delegation_id}-{attempt}"
        marker = _marker(delegation_id, attempt)
        prompt = f"{marker}\n{request['prompt']}"

        # Crash-consistency ordering: the pending record must be durable
        # BEFORE the CLI is invoked.
        record = self._save(self._base_record(request, run_id))

        argv = ["shelley", "client", "chat", "-p", prompt]
        if request.get("requested_model"):
            argv += ["-model", str(request["requested_model"])]
        argv += ["-cwd", str(request["workspace"]["path"])]

        result = self.runner.run(argv)
        if result.returncode != 0:
            # Ambiguous: the worker may or may not have started. Leave the
            # record pending; reconcile() owns the search.
            self._warn(record, "retry_allowed")
            return self._save(self._touch(record))

        try:
            parsed = json.loads(result.stdout)
        except json.JSONDecodeError:
            parsed = None
        conversation_id = parsed.get("conversation_id") if isinstance(parsed, dict) else None
        if not conversation_id:
            # Ambiguous create: never fabricate success.
            self._warn(record, "retry_allowed")
            return self._save(self._touch(record))

        record["worker"]["conversation_id"] = str(conversation_id)
        record["state"] = "accepted"
        record["adapter_revision"] = ADAPTER_REVISION_START
        return self._save(self._touch(record))

    def reconcile(self, idempotency_key: str) -> dict[str, Any]:
        """Reconcile an ambiguous create by searching for the delegation
        marker. 0 matches → pending + retry_allowed; 1 → bind + accepted;
        >1 → duplicate_risk and stop (never pick one silently)."""
        record = self.store.get(idempotency_key)
        if record is None:
            raise AdapterError(
                "conversation_not_found", f"no pending record for {idempotency_key!r}"
            )
        self._require("search")

        marker = _marker(record["delegation_id"], int(record["attempt"]))
        if self.capabilities.get("search_command") == "list":
            argv = ["shelley", "client", "list", "-limit", "10", "-q", marker]
        else:
            argv = ["shelley", "client", "search", "-limit", "10", marker]
        result = self._invoke(argv)
        matches = [m for m in _parse_json_lines(result.stdout) if m.get("conversation_id")]

        if len(matches) == 0:
            self._warn(record, "retry_allowed")
            return self._save(self._touch(record))
        if len(matches) == 1:
            record["worker"]["conversation_id"] = str(matches[0]["conversation_id"])
            record["state"] = "accepted"
            record["adapter_revision"] = max(
                int(record["adapter_revision"]), ADAPTER_REVISION_START
            )
            record["warnings"] = [w for w in record["warnings"] if w != "retry_allowed"]
            self._warn(record, "recovered_by_reconciliation")
            return self._save(self._touch(record))
        # Multiple conversations match one marker: stop automatic progress.
        record["state"] = "duplicate_risk"
        self._warn(record, "duplicate_risk")
        return self._save(self._touch(record))

    def append_turn(
        self, run_record: dict[str, Any], prompt: str, expected_revision: int
    ) -> dict[str, Any]:
        """Append a turn to an existing conversation with optimistic
        concurrency via adapter_revision."""
        self._require("continue")
        record = self._require_record(run_record)
        if expected_revision != record.get("adapter_revision"):
            raise AdapterError(
                "revision_conflict",
                f"expected revision {expected_revision}, "
                f"record is at {record.get('adapter_revision')}",
            )
        if record["state"] not in ACTIVE_STATES:
            raise AdapterError(
                "invalid_request", f"cannot append to run in state {record['state']!r}"
            )
        conversation_id = record["worker"].get("conversation_id")
        if not conversation_id:
            raise AdapterError("conversation_not_found", "run has no bound conversation_id")

        marker = _marker(record["delegation_id"], int(record["attempt"]))
        argv = [
            "shelley",
            "client",
            "chat",
            "-c",
            str(conversation_id),
            "-p",
            f"{marker}\n{prompt}",
        ]
        self._invoke(argv)

        record["adapter_revision"] = int(record["adapter_revision"]) + 1
        if record["state"] == "accepted":
            record["state"] = "running"
        return self._save(self._touch(record))

    def get_run(self, run_record: dict[str, Any]) -> dict[str, Any]:
        """Refresh lifecycle state by reading the conversation."""
        messages = self._read(run_record)
        record = self._require_record(run_record)
        if record["state"] in ACTIVE_STATES:
            record["state"] = derive_state(messages)
        return self._save(self._touch(record))

    def read_messages(self, run_record: dict[str, Any]) -> list[dict[str, Any]]:
        """Return parsed provider messages (JSON objects only — raw CLI
        stdout is never exposed to callers)."""
        return self._read(run_record)

    def _read(self, run_record: dict[str, Any]) -> list[dict[str, Any]]:
        self._require("read")
        conversation_id = self._require_record(run_record)["worker"].get("conversation_id")
        if not conversation_id:
            raise AdapterError("conversation_not_found", "run has no bound conversation_id")
        result = self._invoke(["shelley", "client", "read", str(conversation_id)])
        return _parse_json_lines(result.stdout)

    def archive(self, run_record: dict[str, Any]) -> dict[str, Any]:
        """Archive the conversation. Archiving an active run is an
        exception: the archive still happens but the record carries the
        ``archived_while_active`` warning for caller policy to surface."""
        self._require("archive")
        record = self._require_record(run_record)
        was_active = record["state"] in ACTIVE_STATES
        conversation_id = record["worker"].get("conversation_id")
        if not conversation_id:
            raise AdapterError("conversation_not_found", "run has no bound conversation_id")
        result = self.runner.run(["shelley", "client", "archive", str(conversation_id)])
        if result.returncode != 0:
            raise AdapterError(
                "archive_failed",
                f"archive exited {result.returncode}: {result.stderr.strip()}",
            )
        record["state"] = "archived"
        if was_active:
            self._warn(record, "archived_while_active")
        return self._save(self._touch(record))

    def cancel(self, run_record: dict[str, Any]) -> dict[str, Any]:
        """Cancel is not supported by the verified Shelley CLI. Never fake
        success."""
        raise AdapterError(
            "unsupported", "shelley client has no cancel subcommand (verified v0.959)"
        )

    # -- record resolution -----------------------------------------------------

    def _require_record(self, run_record: dict[str, Any]) -> dict[str, Any]:
        """Resolve a run reference: the in-memory record itself, or an
        idempotency key / minimal record resolvable through the store."""
        if "state" in run_record and "worker" in run_record:
            return run_record
        key = run_record.get("idempotency_key")
        if isinstance(key, str) and key in self.store:
            return self.store[key]
        raise AdapterError(
            "conversation_not_found",
            f"run record not found: {run_record.get('idempotency_key')!r}",
        )
