"""
Tests for skills/dot-graph-intelligence/SKILL.md existence and required content.
TDD: This test is written BEFORE the skills/dot-graph-intelligence/SKILL.md file is created.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
SKILL_PATH = REPO_ROOT / "skills" / "dot-graph-intelligence" / "SKILL.md"


@pytest.fixture(scope="module")
def skill_content():
    """Read SKILL.md once per test module."""
    return SKILL_PATH.read_text()


# --- File existence ---


def test_skill_file_exists():
    """skills/dot-graph-intelligence/SKILL.md must exist."""
    assert SKILL_PATH.exists(), (
        f"skills/dot-graph-intelligence/SKILL.md not found at {SKILL_PATH}"
    )


# --- Frontmatter ---


def test_frontmatter_has_name(skill_content):
    """YAML frontmatter must have name: dot-graph-intelligence."""
    assert "name: dot-graph-intelligence" in skill_content, (
        "Frontmatter must contain 'name: dot-graph-intelligence'"
    )


def test_frontmatter_description_starts_with_use_when(skill_content):
    """Description must start with 'Use when...'."""
    assert "Use when" in skill_content, "Description must contain 'Use when'"


def test_frontmatter_mentions_programmatic_analysis(skill_content):
    """Description must mention programmatic graph structure analysis."""
    content_lower = skill_content.lower()
    assert "programmatic" in content_lower or "analyz" in content_lower, (
        "Description must mention programmatic analysis"
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


def test_overview_mentions_zero_llm_tokens(skill_content):
    """Overview must mention zero LLM tokens principle."""
    content_lower = skill_content.lower()
    assert "zero" in content_lower or "token" in content_lower, (
        "Overview must mention zero LLM tokens"
    )


def test_overview_has_core_principle_code_vs_judgment(skill_content):
    """Overview must mention core principle about code vs judgment."""
    content_lower = skill_content.lower()
    assert "code" in content_lower and (
        "judgment" in content_lower or "judge" in content_lower
    ), "Overview must mention code vs judgment principle"


# --- When to Use decision diagram in DOT ---


def test_has_when_to_use_section(skill_content):
    """Must contain a When to Use section."""
    content_lower = skill_content.lower()
    assert "when to use" in content_lower, "Must contain a 'When to Use' section"


def test_when_to_use_has_dot_diagram(skill_content):
    """When to Use must contain a DOT decision diagram."""
    assert "```dot" in skill_content, "Must contain a DOT code block"


# --- Operations Reference table ---


def test_has_operations_reference(skill_content):
    """Must contain an Operations Reference table."""
    content_lower = skill_content.lower()
    assert "operation" in content_lower and "reference" in content_lower, (
        "Must contain an Operations Reference section"
    )


def test_operations_reference_has_eight_operations(skill_content):
    """Operations Reference table must have at least 8 operations."""
    operations = [
        "reachability",
        "unreachable",
        "cycles",
        "paths",
        "critical_path",
        "subgraph_extract",
        "diff",
        "stats",
    ]
    content_lower = skill_content.lower()
    found = sum(1 for op in operations if op.lower() in content_lower)
    assert found >= 8, (
        f"Expected all 8 operations in reference table, found {found}: {[op for op in operations if op.lower() not in content_lower]}"
    )


def test_operations_table_has_question_column(skill_content):
    """Operations Reference table must have a question column."""
    content_lower = skill_content.lower()
    assert "question" in content_lower, "Operations table must have a question column"


def test_operations_table_has_input_column(skill_content):
    """Operations Reference table must have an input column."""
    content_lower = skill_content.lower()
    assert "input" in content_lower, "Operations table must have an input column"


def test_operations_table_has_output_column(skill_content):
    """Operations Reference table must have an output column."""
    content_lower = skill_content.lower()
    assert "output" in content_lower, "Operations table must have an output column"


# --- The Analysis Loop ---


def test_has_analysis_loop(skill_content):
    """Must contain The Analysis Loop section."""
    content_lower = skill_content.lower()
    assert "analysis loop" in content_lower, "Must contain an Analysis Loop section"


def test_analysis_loop_has_seven_steps(skill_content):
    """Analysis Loop must have at least 7 steps."""
    lines = skill_content.splitlines()
    in_loop = False
    loop_items = 0
    for line in lines:
        line_lower = line.lower()
        if "analysis loop" in line_lower:
            in_loop = True
        if (
            in_loop
            and (
                line.strip().startswith("- ")
                or line.strip().startswith("* ")
                or (
                    len(line.strip()) > 2
                    and line.strip()[0].isdigit()
                    and line.strip()[1] in (".", ")")
                )
            )
            and line.strip() not in ("-", "*")
        ):
            loop_items += 1
        # Stop at next ## section
        if (
            in_loop
            and line.startswith("## ")
            and "analysis loop" not in line_lower
            and loop_items > 0
        ):
            break
    assert loop_items >= 7, (
        f"Expected at least 7 Analysis Loop steps, found {loop_items}"
    )


# --- Interpretation Guide ---


def test_has_interpretation_guide(skill_content):
    """Must contain an Interpretation Guide section."""
    content_lower = skill_content.lower()
    assert "interpretation" in content_lower, "Must contain an Interpretation Guide"


def test_interpretation_guide_covers_cycles(skill_content):
    """Interpretation Guide must cover cycles."""
    content_lower = skill_content.lower()
    assert "cycle" in content_lower or "cycles" in content_lower, (
        "Interpretation Guide must cover cycles"
    )


def test_interpretation_guide_covers_unreachable(skill_content):
    """Interpretation Guide must cover unreachable nodes."""
    content_lower = skill_content.lower()
    assert "unreachable" in content_lower, (
        "Interpretation Guide must cover unreachable nodes"
    )


def test_interpretation_guide_covers_high_density(skill_content):
    """Interpretation Guide must cover high density."""
    content_lower = skill_content.lower()
    assert "density" in content_lower or "high density" in content_lower, (
        "Interpretation Guide must cover high density"
    )


def test_interpretation_guide_covers_multiple_components(skill_content):
    """Interpretation Guide must cover multiple components."""
    content_lower = skill_content.lower()
    assert "component" in content_lower or "disconnected" in content_lower, (
        "Interpretation Guide must cover multiple components"
    )


# --- Code vs LLM Decision Matrix ---


def test_has_code_vs_llm_decision_matrix(skill_content):
    """Must contain a Code vs LLM Decision Matrix table."""
    content_lower = skill_content.lower()
    assert "decision matrix" in content_lower or (
        "code" in content_lower and "llm" in content_lower and "matrix" in content_lower
    ), "Must contain a Code vs LLM Decision Matrix"


def test_decision_matrix_has_ten_tasks(skill_content):
    """Code vs LLM Decision Matrix must have at least 10 tasks."""
    lines = skill_content.splitlines()
    in_matrix = False
    matrix_rows = 0
    for line in lines:
        line_lower = line.lower()
        # Only trigger on the actual section header, not any line with code+llm
        if line.startswith("##") and "decision matrix" in line_lower:
            in_matrix = True
            continue
        if in_matrix and "|" in line and "---" not in line:
            # Skip header rows (contains "task" or "use code" column name)
            if "task" not in line_lower and "use code" not in line_lower:
                matrix_rows += 1
        # Stop at next ## section
        if in_matrix and line.startswith("## ") and "matrix" not in line_lower:
            break
    assert matrix_rows >= 10, (
        f"Expected at least 10 rows in the Decision Matrix, found {matrix_rows}"
    )
