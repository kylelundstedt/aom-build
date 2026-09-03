"""Tests for aom.snapshot — management snapshot generator."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from aom.contracts import ContractError, validate
from aom.snapshot import build_snapshot, render_markdown, write_snapshot

EXAMPLES = Path(__file__).resolve().parents[1] / "contracts" / "examples"


@pytest.fixture
def delegation_attempt():
    return json.loads((EXAMPLES / "delegation-attempt.v1.example.json").read_text())


@pytest.fixture
def publication_resolution():
    return json.loads((EXAMPLES / "publication-resolution.v1.example.json").read_text())


def _base_kwargs(**overrides):
    """Minimal valid kwargs for build_snapshot."""
    defaults = {
        "kanban_summary": [{"status": "running", "count": 1}],
        "delegations": [],
        "publications": [],
        "source_revisions": {"kanban": 42},
        "attention_items": [],
        "now": datetime(2026, 9, 3, 14, 8, 0, tzinfo=UTC),
    }
    defaults.update(overrides)
    return defaults


# ---------------------------------------------------------------------------
# build_snapshot
# ---------------------------------------------------------------------------


class TestBuildSnapshot:
    def test_validates_against_schema(self):
        snap = build_snapshot(**_base_kwargs())
        # Should not raise.
        validate("management-snapshot.v1", snap)
        assert snap["schema"] == "iv.aom/management-snapshot/v1"
        assert snap["authority"] == "none_projection_only"

    def test_snapshot_id_format(self):
        snap = build_snapshot(**_base_kwargs())
        assert snap["snapshot_id"] == "snapshot-20260903T140800Z"

    def test_stale_after_is_ttl(self):
        snap = build_snapshot(**_base_kwargs(ttl_seconds=600))
        assert snap["generated_at"] == "2026-09-03T14:08:00Z"
        assert snap["stale_after"] == "2026-09-03T14:18:00Z"

    def test_empty_source_revisions_raises(self):
        with pytest.raises(ValueError):
            build_snapshot(**_base_kwargs(source_revisions={}))

    def test_duplicate_risk_generates_critical_attention(self, delegation_attempt):
        d = dict(delegation_attempt)
        d["state"] = "duplicate_risk"
        snap = build_snapshot(**_base_kwargs(delegations=[d]))
        criticals = [a for a in snap["attention_items"] if a["severity"] == "critical"]
        assert len(criticals) == 1
        assert criticals[0]["title"] == "Delegation duplicate risk"
        assert criticals[0]["decision_required"] is True

    def test_duplicate_risk_included_in_active(self, delegation_attempt):
        d = dict(delegation_attempt)
        d["state"] = "duplicate_risk"
        snap = build_snapshot(**_base_kwargs(delegations=[d]))
        assert len(snap["active_delegations"]) == 1
        assert snap["active_delegations"][0]["state"] == "duplicate_risk"

    def test_completed_excluded_from_active(self, delegation_attempt):
        d = dict(delegation_attempt)
        d["state"] = "completed"
        snap = build_snapshot(**_base_kwargs(delegations=[d]))
        assert snap["active_delegations"] == []

    def test_archived_excluded_from_active(self, delegation_attempt):
        d = dict(delegation_attempt)
        d["state"] = "archived"
        snap = build_snapshot(**_base_kwargs(delegations=[d]))
        assert snap["active_delegations"] == []

    def test_failed_excluded_from_active(self, delegation_attempt):
        d = dict(delegation_attempt)
        d["state"] = "failed"
        snap = build_snapshot(**_base_kwargs(delegations=[d]))
        assert snap["active_delegations"] == []

    def test_running_included_in_active(self, delegation_attempt):
        snap = build_snapshot(**_base_kwargs(delegations=[delegation_attempt]))
        assert len(snap["active_delegations"]) == 1
        ad = snap["active_delegations"][0]
        assert ad["model"] == "gpt-5.6-luna"
        assert ad["run_ref"]["id"] == "run-FREDDIE-184-implement-1"
        assert ad["deep_link"] == "shelley://conversation/8e7c-example"

    def test_accepted_included_in_active(self, delegation_attempt):
        d = dict(delegation_attempt)
        d["state"] = "accepted"
        snap = build_snapshot(**_base_kwargs(delegations=[d]))
        assert len(snap["active_delegations"]) == 1

    def test_evidence_gaps_generate_warnings(self):
        snap = build_snapshot(**_base_kwargs(evidence_gaps=["attempt_without_evidence:run-1"]))
        warnings = [a for a in snap["attention_items"] if a["severity"] == "warning"]
        assert any("attempt_without_evidence:run-1" in a["title"] for a in warnings)

    def test_recent_publications_built(self, publication_resolution):
        snap = build_snapshot(**_base_kwargs(publications=[publication_resolution]))
        assert len(snap["recent_publications"]) == 1
        pub = snap["recent_publications"][0]
        assert pub["domain"] == "publication"
        assert pub["id"] == "product:freddie-sflld"

    def test_work_summary_passthrough(self):
        ws = [{"status": "running", "count": 3}, {"status": "blocked", "count": 1}]
        snap = build_snapshot(**_base_kwargs(kanban_summary=ws))
        assert snap["work_summary"] == ws

    def test_attention_items_passthrough(self, delegation_attempt):
        item = {
            "severity": "warning",
            "title": "Something needs attention",
            "source_ref": {"domain": "work", "id": "FREDDIE-184"},
            "decision_required": False,
        }
        snap = build_snapshot(**_base_kwargs(attention_items=[item]))
        # The passed-in item should be present.
        titles = [a["title"] for a in snap["attention_items"]]
        assert "Something needs attention" in titles

    def test_invalid_snapshot_raises(self):
        # An attention item missing source_ref should fail validation.
        bad_item = {"severity": "warning", "title": "No source"}
        with pytest.raises(ContractError):
            build_snapshot(**_base_kwargs(attention_items=[bad_item]))


# ---------------------------------------------------------------------------
# render_markdown
# ---------------------------------------------------------------------------


class TestRenderMarkdown:
    def test_contains_attention_titles(self, delegation_attempt):
        d = dict(delegation_attempt)
        d["state"] = "duplicate_risk"
        snap = build_snapshot(**_base_kwargs(delegations=[d]))
        md = render_markdown(snap)
        assert "Delegation duplicate risk" in md

    def test_contains_model_names(self, delegation_attempt):
        snap = build_snapshot(**_base_kwargs(delegations=[delegation_attempt]))
        md = render_markdown(snap)
        assert "gpt-5.6-luna" in md

    def test_contains_timestamps(self):
        snap = build_snapshot(**_base_kwargs())
        md = render_markdown(snap)
        assert "2026-09-03T14:08:00Z" in md
        assert "2026-09-03T14:13:00Z" in md

    def test_no_html(self):
        snap = build_snapshot(**_base_kwargs())
        md = render_markdown(snap)
        assert "<" not in md or "<" not in md.replace("| --- |", "")
        # More directly: no HTML tags.
        assert not any(line.strip().startswith("<") for line in md.splitlines())


# ---------------------------------------------------------------------------
# write_snapshot
# ---------------------------------------------------------------------------


class TestWriteSnapshot:
    def test_writes_both_files(self, tmp_path):
        snap = build_snapshot(**_base_kwargs())
        write_snapshot(snap, tmp_path)
        json_path = tmp_path / "snapshot.json"
        md_path = tmp_path / "aom-management-snapshot.md"
        assert json_path.is_file()
        assert md_path.is_file()
        # JSON is valid and matches.
        loaded = json.loads(json_path.read_text())
        assert loaded["schema"] == "iv.aom/management-snapshot/v1"
        # Markdown is non-empty.
        assert len(md_path.read_text()) > 10

    def test_creates_dir(self, tmp_path):
        snap = build_snapshot(**_base_kwargs())
        target = tmp_path / "subdir" / "nested"
        write_snapshot(snap, target)
        assert (target / "snapshot.json").is_file()
        assert (target / "aom-management-snapshot.md").is_file()
