"""
Tests for skills/dot-patterns/SKILL.md existence and required content.
TDD: This test is written BEFORE the skills/dot-patterns/SKILL.md file is created.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
SKILL_PATH = REPO_ROOT / "skills" / "dot-patterns" / "SKILL.md"


@pytest.fixture(scope="module")
def skill_content():
    """Read SKILL.md once per test module."""
    return SKILL_PATH.read_text()


# --- File existence ---


def test_skill_file_exists():
    """skills/dot-patterns/SKILL.md must exist."""
    assert SKILL_PATH.exists(), (
        f"skills/dot-patterns/SKILL.md not found at {SKILL_PATH}"
    )


# --- Frontmatter ---


def test_frontmatter_has_name(skill_content):
    """YAML frontmatter must have name: dot-patterns."""
    assert "name: dot-patterns" in skill_content, (
        "Frontmatter must contain 'name: dot-patterns'"
    )


def test_frontmatter_description_starts_with_use_when(skill_content):
    """Description must start with 'Use when...'."""
    assert "Use when" in skill_content, "Description must contain 'Use when'"


def test_frontmatter_mentions_templates(skill_content):
    """Description must mention templates (copy-paste pattern)."""
    content_lower = skill_content.lower()
    assert "template" in content_lower or "copy" in content_lower, (
        "Description must mention templates or copy-paste"
    )


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


# --- Pattern Selection decision diagram in DOT ---


def test_has_pattern_selection_diagram(skill_content):
    """Must contain a Pattern Selection decision diagram in DOT."""
    content_lower = skill_content.lower()
    assert "pattern selection" in content_lower or "pattern select" in content_lower, (
        "Must contain a Pattern Selection section"
    )
    assert "```dot" in skill_content, "Must contain a DOT code block"


# --- 5 complete DOT templates ---


def test_has_dag_workflow_template(skill_content):
    """Must contain a DAG/Workflow template."""
    content_lower = skill_content.lower()
    assert "dag" in content_lower or "workflow" in content_lower, (
        "Must contain a DAG/Workflow template"
    )


def test_has_state_machine_template(skill_content):
    """Must contain a State Machine template."""
    content_lower = skill_content.lower()
    assert "state machine" in content_lower or "state_machine" in content_lower, (
        "Must contain a State Machine template"
    )


def test_has_layered_architecture_template(skill_content):
    """Must contain a Layered Architecture template."""
    content_lower = skill_content.lower()
    assert "layered" in content_lower or "architecture" in content_lower, (
        "Must contain a Layered Architecture template"
    )


def test_has_fan_out_fan_in_template(skill_content):
    """Must contain a Fan-Out/Fan-In template."""
    content_lower = skill_content.lower()
    assert (
        "fan-out" in content_lower
        or "fan_out" in content_lower
        or "fan out" in content_lower
    ), "Must contain a Fan-Out/Fan-In template"


def test_has_legend_template(skill_content):
    """Must contain a Legend template."""
    content_lower = skill_content.lower()
    assert "legend" in content_lower, "Must contain a Legend template"


def test_has_five_dot_code_blocks(skill_content):
    """Must have at least 5 DOT code blocks (one per template)."""
    import re

    dot_blocks = re.findall(r"```dot", skill_content)
    assert len(dot_blocks) >= 5, (
        f"Expected at least 5 DOT code blocks (one per template), found {len(dot_blocks)}"
    )


def test_dot_templates_have_digraph(skill_content):
    """DOT templates must include digraph declarations."""
    assert "digraph" in skill_content, "Templates must use digraph declarations"


# --- Template Checklist with 6 items ---


def test_has_template_checklist(skill_content):
    """Must contain a Template Checklist."""
    content_lower = skill_content.lower()
    assert "checklist" in content_lower, "Must contain a Template Checklist section"


def test_template_checklist_has_six_items(skill_content):
    """Template Checklist must have at least 6 items."""
    lines = skill_content.splitlines()
    in_checklist = False
    checklist_items = 0
    for line in lines:
        if "checklist" in line.lower():
            in_checklist = True
        if in_checklist and (
            line.strip().startswith("- [ ]")
            or line.strip().startswith("- [x]")
            or line.strip().startswith("* ")
            or (line.strip().startswith("- ") and line.strip() != "-")
        ):
            checklist_items += 1
        # Stop at next major section
        if (
            in_checklist
            and line.startswith("## ")
            and "checklist" not in line.lower()
            and checklist_items > 0
        ):
            break
    assert checklist_items >= 6, (
        f"Expected at least 6 checklist items, found {checklist_items}"
    )
