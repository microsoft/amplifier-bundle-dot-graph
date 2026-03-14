"""
Tests for skills/dot-as-analysis/SKILL.md existence and required content.
TDD: This test is written BEFORE the skills/dot-as-analysis/SKILL.md file is created.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
SKILL_PATH = REPO_ROOT / "skills" / "dot-as-analysis" / "SKILL.md"


@pytest.fixture(scope="module")
def skill_content():
    """Read SKILL.md once per test module."""
    return SKILL_PATH.read_text()


# --- File existence ---


def test_skill_file_exists():
    """skills/dot-as-analysis/SKILL.md must exist."""
    assert SKILL_PATH.exists(), (
        f"skills/dot-as-analysis/SKILL.md not found at {SKILL_PATH}"
    )


# --- Frontmatter ---


def test_frontmatter_has_name(skill_content):
    """YAML frontmatter must have name: dot-as-analysis."""
    assert "name: dot-as-analysis" in skill_content, (
        "Frontmatter must contain 'name: dot-as-analysis'"
    )


def test_frontmatter_description_starts_with_use_when(skill_content):
    """Description must start with 'Use when...'."""
    assert "Use when" in skill_content, "Description must contain 'Use when'"


def test_frontmatter_mentions_hidden_issues(skill_content):
    """Description must mention analyzing systems to surface hidden issues."""
    content_lower = skill_content.lower()
    assert (
        "analyz" in content_lower
        or "surface" in content_lower
        or "hidden" in content_lower
    ), "Description must mention analyzing systems or surfacing hidden issues"


def test_frontmatter_delimiters(skill_content):
    """File must have YAML frontmatter delimiters (---)."""
    lines = skill_content.splitlines()
    assert lines[0].strip() == "---", "First line must be '---' (frontmatter start)"
    closing = any(line.strip() == "---" for line in lines[1:10])
    assert closing, "Must have closing '---' frontmatter delimiter"


# --- Overview section ---


def test_has_overview_section(skill_content):
    """Must have an Overview section."""
    assert "## Overview" in skill_content or "# Overview" in skill_content, (
        "Must contain an Overview section"
    )


def test_overview_mentions_analysis_instrument(skill_content):
    """Overview must mention DOT as analysis instrument."""
    content_lower = skill_content.lower()
    assert "instrument" in content_lower or "analysis" in content_lower, (
        "Overview must mention DOT as analysis instruments"
    )


def test_overview_has_core_principle_about_completeness(skill_content):
    """Overview must mention core principle about completeness."""
    content_lower = skill_content.lower()
    assert "complete" in content_lower or "completeness" in content_lower, (
        "Overview must mention core principle about completeness"
    )


# --- The Reconciliation Workflow ---


def test_has_reconciliation_workflow(skill_content):
    """Must contain a Reconciliation Workflow section."""
    content_lower = skill_content.lower()
    assert "reconciliation" in content_lower or "reconcile" in content_lower, (
        "Must contain a Reconciliation Workflow section"
    )


def test_reconciliation_has_four_phases(skill_content):
    """Reconciliation Workflow must have 4 phases."""
    content_lower = skill_content.lower()
    phases = ["introspect", "represent", "reconcile", "surface"]
    found = sum(1 for p in phases if p in content_lower)
    assert found >= 4, (
        f"Expected all 4 phases (introspect/represent/reconcile/surface), found {found}"
    )


def test_reconcile_phase_has_findings_table(skill_content):
    """Reconcile phase must have a findings table."""
    # Check for table rows (pipe characters)
    lines = skill_content.splitlines()
    table_rows = [line for line in lines if "|" in line and "---" not in line]
    assert len(table_rows) >= 6, (
        f"Expected at least 6 table rows (findings table), found {len(table_rows)}"
    )


# --- Anti-Rationalization Table ---


def test_has_anti_rationalization_table(skill_content):
    """Must contain an Anti-Rationalization Table."""
    content_lower = skill_content.lower()
    assert "rationalization" in content_lower or "anti-rational" in content_lower, (
        "Must contain an Anti-Rationalization Table"
    )


def test_anti_rationalization_has_seven_entries(skill_content):
    """Anti-Rationalization table must have at least 7 rationalizations."""
    lines = skill_content.splitlines()
    in_section = False
    table_rows = 0
    for line in lines:
        if "rationalization" in line.lower():
            in_section = True
        if (
            in_section
            and "|" in line
            and "---" not in line
            and "rationalization" not in line.lower()
        ):
            table_rows += 1
        # Stop at next ## section
        if (
            in_section
            and line.startswith("## ")
            and "rationalization" not in line.lower()
            and table_rows > 0
        ):
            break
    assert table_rows >= 7, (
        f"Expected at least 7 anti-rationalization rows, found {table_rows}"
    )


# --- When to Use section ---


def test_has_when_to_use_section(skill_content):
    """Must contain a When to Use section."""
    content_lower = skill_content.lower()
    assert "when to use" in content_lower, "Must contain a 'When to Use' section"


def test_when_to_use_has_high_value_scenario(skill_content):
    """When to Use must include high value scenarios."""
    content_lower = skill_content.lower()
    assert "high value" in content_lower or "high-value" in content_lower, (
        "Must include high value scenarios"
    )


def test_when_to_use_has_low_value_scenario(skill_content):
    """When to Use must include low value scenarios."""
    content_lower = skill_content.lower()
    assert "low value" in content_lower or "low-value" in content_lower, (
        "Must include low value scenarios"
    )


# --- Example of reconciliation-driven bug discovery ---


def test_has_example_section(skill_content):
    """Must contain an example of reconciliation-driven bug discovery."""
    content_lower = skill_content.lower()
    assert "example" in content_lower, "Must contain an example section"


def test_example_mentions_bug_discovery(skill_content):
    """Example must be about bug discovery through reconciliation."""
    content_lower = skill_content.lower()
    assert (
        "bug" in content_lower
        or "discover" in content_lower
        or "discrepanc" in content_lower
    ), "Example must mention bug discovery or discrepancy"
