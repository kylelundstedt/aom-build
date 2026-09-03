"""Disposable management snapshot generator.

Produces a ``management-snapshot.v1`` record — a non-authoritative
projection for the Scarf/ScarfGo dashboard. Nothing here is a state
authority; the ``authority`` field is literally ``"none_projection_only"``.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from aom.contracts import validate

__all__ = [
    "build_snapshot",
    "render_markdown",
    "write_snapshot",
]

# Delegation states included in the "active" projection.
_ACTIVE_STATES = {"accepted", "running", "duplicate_risk"}


def _utcnow(now: datetime | None) -> datetime:
    """Return a timezone-aware UTC datetime."""
    if now is None:
        return datetime.now(tz=UTC)
    if now.tzinfo is None:
        # Treat naive datetimes as UTC.
        return now.replace(tzinfo=UTC)
    return now.astimezone(UTC)


def _rfc3339(dt: datetime) -> str:
    """Format *dt* as an RFC 3339 UTC timestamp."""
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_snapshot(
    *,
    kanban_summary: list[dict[str, Any]],
    delegations: list[dict[str, Any]],
    publications: list[dict[str, Any]],
    source_revisions: dict[str, Any],
    attention_items: list[dict[str, Any]],
    now: datetime | None = None,
    ttl_seconds: int = 300,
    producer_version: str = "0.1.0",
    evidence_gaps: list[str] | None = None,
) -> dict[str, Any]:
    """Build a ``management-snapshot.v1`` record.

    Parameters
    ----------
    kanban_summary:
        Passthrough into ``work_summary``.
    delegations:
        List of ``delegation-attempt.v1`` records. Only attempts in states
        ``accepted``, ``running``, or ``duplicate_risk`` are included in
        ``active_delegations``.
    publications:
        List of ``publication-resolution.v1`` records (or refs) used to
        populate ``recent_publications``.
    source_revisions:
        Must be non-empty (``ValueError`` otherwise).
    attention_items:
        Each must have ``severity``, ``title``, and ``source_ref``.
    now:
        Override for the current time (testing). Defaults to UTC now.
    ttl_seconds:
        Seconds until the snapshot is stale.
    producer_version:
        Version string for the snapshot producer.
    evidence_gaps:
        Optional list of gap strings; each produces a warning attention item.

    Returns
    -------
    dict
        A record validated against ``management-snapshot.v1``.

    :raises ValueError: if *source_revisions* is empty.
    :raises aom.contracts.ContractError: if the assembled record fails
        validation.
    """
    if not source_revisions:
        raise ValueError("source_revisions must be non-empty")

    generated_dt = _utcnow(now)
    stale_dt = generated_dt + timedelta(seconds=ttl_seconds)
    generated_at = _rfc3339(generated_dt)
    stale_after = _rfc3339(stale_dt)

    # snapshot_id: "snapshot-<utcstamp>"
    stamp = generated_dt.strftime("%Y%m%dT%H%M%SZ")
    snapshot_id = f"snapshot-{stamp}"

    # Build attention items, adding auto-generated ones.
    items: list[dict[str, Any]] = list(attention_items)

    # duplicate_risk delegations → critical attention item.
    for d in delegations:
        if d.get("state") == "duplicate_risk":
            task_ref = d.get("task_ref", {"domain": "work", "id": "unknown"})
            items.append(
                {
                    "severity": "critical",
                    "title": "Delegation duplicate risk",
                    "detail": (
                        f"Delegation {d.get('delegation_id', '?')} is in "
                        "duplicate_risk state and requires a decision."
                    ),
                    "source_ref": task_ref,
                    "decision_required": True,
                }
            )

    # evidence_gaps → warning attention items.
    if evidence_gaps:
        for gap in evidence_gaps:
            items.append(
                {
                    "severity": "warning",
                    "title": f"Evidence gap: {gap}",
                    "detail": f"Trace chain has evidence gap: {gap}",
                    "source_ref": {"domain": "evidence", "id": gap},
                    "decision_required": False,
                }
            )

    # Build active_delegations from delegation-attempt records.
    active_delegations: list[dict[str, Any]] = []
    for d in delegations:
        state = d.get("state")
        if state not in _ACTIVE_STATES:
            continue
        worker = d.get("worker") or {}
        task_ref = d.get("task_ref")
        run_id = worker.get("run_id", "")
        model = worker.get("actual_model", "")
        conversation_id = worker.get("conversation_id", "")
        active_entry: dict[str, Any] = {
            "task_ref": task_ref,
            "run_ref": {"domain": "worker", "id": run_id},
            "model": model,
            "state": state,
            "deep_link": f"shelley://conversation/{conversation_id}",
        }
        active_delegations.append(active_entry)

    # Build recent_publications as refs.
    recent_publications: list[dict[str, Any]] = []
    for p in publications:
        # Accept either full publication-resolution records or ref dicts.
        if "product_id" in p:
            recent_publications.append(
                {
                    "domain": "publication",
                    "id": p["product_id"],
                    "version": p.get("version", ""),
                }
            )
        elif "domain" in p and "id" in p:
            recent_publications.append(p)
        else:
            # Best-effort: include as-is if it looks like a ref.
            recent_publications.append(p)

    snapshot = {
        "schema": "iv.aom/management-snapshot/v1",
        "snapshot_id": snapshot_id,
        "authority": "none_projection_only",
        "generated_at": generated_at,
        "stale_after": stale_after,
        "source_revisions": source_revisions,
        "attention_items": items,
        "work_summary": kanban_summary,
        "active_delegations": active_delegations,
        "recent_publications": recent_publications,
        "producer": {"id": "scarf-snapshot-generator", "version": producer_version},
    }

    return validate("management-snapshot.v1", snapshot)


def render_markdown(snapshot: dict[str, Any]) -> str:
    """Render a short human-readable markdown report from a snapshot.

    Suitable for the Scarf ``markdown_file`` widget. Plain markdown, no HTML.
    """
    lines: list[str] = []

    lines.append("# Management Snapshot")
    lines.append("")
    lines.append(f"- **Generated:** {snapshot.get('generated_at', '?')}")
    lines.append(f"- **Stale after:** {snapshot.get('stale_after', '?')}")
    lines.append(f"- **Authority:** {snapshot.get('authority', '?')}")
    lines.append("")

    # Attention items
    items = snapshot.get("attention_items", [])
    if items:
        lines.append("## Attention Items")
        lines.append("")
        for item in items:
            sev = item.get("severity", "info")
            title = item.get("title", "")
            prefix = {
                "critical": "🟥 CRITICAL",
                "warning": "🟧 WARNING",
                "info": "ℹ️ INFO",
            }.get(sev, sev.upper())
            line = f"- **{prefix}** — {title}"
            if item.get("decision_required"):
                line += " _(decision required)_"
            lines.append(line)
        lines.append("")

    # Active delegations
    active = snapshot.get("active_delegations", [])
    if active:
        lines.append("## Active Delegations")
        lines.append("")
        lines.append("| Task | Run | Model | State |")
        lines.append("| --- | --- | --- | --- |")
        for d in active:
            task_id = (d.get("task_ref") or {}).get("id", "?")
            run_id = (d.get("run_ref") or {}).get("id", "?")
            model = d.get("model", "?")
            state = d.get("state", "?")
            lines.append(f"| {task_id} | {run_id} | {model} | {state} |")
        lines.append("")

    # Recent publications
    pubs = snapshot.get("recent_publications", [])
    if pubs:
        lines.append("## Recent Publications")
        lines.append("")
        for p in pubs:
            pid = p.get("id", "?")
            ver = p.get("version", "?")
            lines.append(f"- {pid} @ {ver}")
        lines.append("")

    return "\n".join(lines)


def write_snapshot(snapshot: dict[str, Any], dir_path: str | Path) -> None:
    """Write *snapshot* as ``snapshot.json`` and ``aom-management-snapshot.md``
    into *dir_path*.

    Creates *dir_path* if it does not exist.
    """
    out = Path(dir_path)
    out.mkdir(parents=True, exist_ok=True)

    (out / "snapshot.json").write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (out / "aom-management-snapshot.md").write_text(render_markdown(snapshot), encoding="utf-8")
