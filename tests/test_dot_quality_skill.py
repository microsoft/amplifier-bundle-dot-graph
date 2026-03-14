"""
Tests for skills/dot-quality/SKILL.md existence and required content.
TDD: This test is written BEFORE the skills/dot-quality/SKILL.md file is created.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
SKILL_PATH = REPO_ROOT / "skills" / "dot-quality" / "SKILL.md"


@pytest.fixture(scope="module")
def skill_content():
    """Read SKILL.md once per test module."""
    return SKILL_PATH.read_text()


# --- File existence ---


def test_skill_file_exists():
    """skills/dot-quality/SKILL.md must exist."""
    assert SKILL_PATH.exists(), f"skills/dot-quality/SKILL.md not found at {SKILL_PATH}"


# --- Frontmatter ---


def test_frontmatter_has_name(skill_content):
    """YAML frontmatter must have name: dot-quality."""
    assert "name: dot-quality" in skill_content, (
        "Frontmatter must contain 'name: dot-quality'"
    )


def test_frontmatter_description_starts_with_use_when(skill_content):
    """Description must start with 'Use when...'."""
    assert "Use when" in skill_content, "Description must contain 'Use when'"


def test_frontmatter_mentions_quality_standards(skill_content):
    """Description must mention quality standards enforcement."""
    content_lower = skill_content.lower()
    assert "quality" in content_lower or "standard" in content_lower, (
        "Description must mention quality or standards"
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


def test_overview_mentions_structural_claims(skill_content):
    """Overview must mention core principle about structural claims."""
    content_lower = skill_content.lower()
    assert "structural" in content_lower or "structure" in content_lower, (
        "Overview must mention structural claims"
    )


# --- The Iron Law ---


def test_has_iron_law(skill_content):
    """Must contain The Iron Law section."""
    content_lower = skill_content.lower()
    assert "iron law" in content_lower, "Must contain 'Iron Law'"


def test_iron_law_mentions_title(skill_content):
    """Iron Law must mention NO DIAGRAM WITHOUT A TITLE."""
    content_upper = skill_content.upper()
    assert "TITLE" in content_upper and "DIAGRAM" in content_upper, (
        "Iron Law must include 'NO DIAGRAM WITHOUT A TITLE'"
    )


def test_iron_law_mentions_color_legend(skill_content):
    """Iron Law must mention NO COLOR WITHOUT A LEGEND."""
    content_upper = skill_content.upper()
    assert "COLOR" in content_upper and "LEGEND" in content_upper, (
        "Iron Law must include 'NO COLOR WITHOUT A LEGEND'"
    )


# --- Quality Checklist ---


def test_has_quality_checklist(skill_content):
    """Must contain a Quality Checklist section."""
    content_lower = skill_content.lower()
    assert "checklist" in content_lower, "Must contain a Quality Checklist"


def test_checklist_has_must_have_tier(skill_content):
    """Quality Checklist must have a Must Have / FAIL tier."""
    content_lower = skill_content.lower()
    assert "must have" in content_lower or "must-have" in content_lower, (
        "Must contain a 'Must Have' tier"
    )
    assert "fail" in content_lower, "Must contain 'FAIL' tier marker"


def test_checklist_has_should_have_tier(skill_content):
    """Quality Checklist must have a Should Have / WARN tier."""
    content_lower = skill_content.lower()
    assert "should have" in content_lower or "should-have" in content_lower, (
        "Must contain a 'Should Have' tier"
    )
    assert "warn" in content_lower, "Must contain 'WARN' tier marker"


def test_checklist_has_nice_to_have_tier(skill_content):
    """Quality Checklist must have a Nice to Have / INFO tier."""
    content_lower = skill_content.lower()
    assert "nice to have" in content_lower or "nice-to-have" in content_lower, (
        "Must contain a 'Nice to Have' tier"
    )
    assert "info" in content_lower, "Must contain 'INFO' tier marker"


def test_must_have_tier_has_four_items(skill_content):
    """Must Have tier must have at least 4 items."""
    lines = skill_content.splitlines()
    in_must_have = False
    must_have_items = 0
    for line in lines:
        line_lower = line.lower()
        if "must have" in line_lower or "must-have" in line_lower:
            in_must_have = True
        if (
            in_must_have
            and (line.strip().startswith("- ") or line.strip().startswith("* "))
            and line.strip() not in ("-", "*")
        ):
            must_have_items += 1
        # Stop at next section (should have or other)
        if (
            in_must_have
            and ("should have" in line_lower or "should-have" in line_lower)
            and must_have_items > 0
        ):
            break
    assert must_have_items >= 4, (
        f"Expected at least 4 Must Have items, found {must_have_items}"
    )


def test_should_have_tier_has_six_items(skill_content):
    """Should Have tier must have at least 6 items."""
    lines = skill_content.splitlines()
    in_should_have = False
    should_have_items = 0
    for line in lines:
        line_lower = line.lower()
        if "should have" in line_lower or "should-have" in line_lower:
            in_should_have = True
        if (
            in_should_have
            and (line.strip().startswith("- ") or line.strip().startswith("* "))
            and line.strip() not in ("-", "*")
        ):
            should_have_items += 1
        # Stop at next section
        if (
            in_should_have
            and ("nice to have" in line_lower or "nice-to-have" in line_lower)
            and should_have_items > 0
        ):
            break
    assert should_have_items >= 6, (
        f"Expected at least 6 Should Have items, found {should_have_items}"
    )


def test_nice_to_have_tier_has_four_items(skill_content):
    """Nice to Have tier must have at least 4 items."""
    lines = skill_content.splitlines()
    in_nice = False
    nice_items = 0
    for line in lines:
        line_lower = line.lower()
        if "nice to have" in line_lower or "nice-to-have" in line_lower:
            in_nice = True
        if (
            in_nice
            and (line.strip().startswith("- ") or line.strip().startswith("* "))
            and line.strip() not in ("-", "*")
        ):
            nice_items += 1
        # Stop at next ## section
        if (
            in_nice
            and line.startswith("## ")
            and "nice" not in line_lower
            and nice_items > 0
        ):
            break
    assert nice_items >= 4, (
        f"Expected at least 4 Nice to Have items, found {nice_items}"
    )


# --- Line Count Targets table ---


def test_has_line_count_targets(skill_content):
    """Must contain a Line Count Targets table."""
    content_lower = skill_content.lower()
    assert "line count" in content_lower or "line-count" in content_lower, (
        "Must contain a Line Count Targets section"
    )


# --- Anti-Pattern Red Flags table ---


def test_has_anti_pattern_red_flags(skill_content):
    """Must contain an Anti-Pattern Red Flags table."""
    content_lower = skill_content.lower()
    assert "red flag" in content_lower or "anti-pattern" in content_lower, (
        "Must contain an Anti-Pattern Red Flags section"
    )


def test_anti_pattern_red_flags_has_seven(skill_content):
    """Anti-Pattern Red Flags table must have at least 7 flags."""
    lines = skill_content.splitlines()
    in_section = False
    flag_rows = 0
    for line in lines:
        line_lower = line.lower()
        if "red flag" in line_lower or "anti-pattern" in line_lower:
            in_section = True
        if in_section and "|" in line and "---" not in line:
            # Skip header rows
            if "flag" not in line_lower and "pattern" not in line_lower:
                flag_rows += 1
        # Stop at next ## section
        if (
            in_section
            and line.startswith("## ")
            and "red flag" not in line_lower
            and "anti-pattern" not in line_lower
            and flag_rows > 0
        ):
            break
    assert flag_rows >= 7, (
        f"Expected at least 7 anti-pattern red flag rows, found {flag_rows}"
    )


# --- Shape Vocabulary Compliance ---


def test_has_shape_vocabulary_section(skill_content):
    """Must contain a Shape Vocabulary Compliance section."""
    content_lower = skill_content.lower()
    assert "shape" in content_lower and "vocabular" in content_lower, (
        "Must contain a Shape Vocabulary section"
    )


# --- The Quality Gate ---


def test_has_quality_gate(skill_content):
    """Must contain The Quality Gate section."""
    content_lower = skill_content.lower()
    assert "quality gate" in content_lower, "Must contain a Quality Gate section"


def test_quality_gate_has_seven_steps(skill_content):
    """Quality Gate must have at least 7 steps."""
    lines = skill_content.splitlines()
    in_gate = False
    gate_items = 0
    for line in lines:
        line_lower = line.lower()
        if "quality gate" in line_lower:
            in_gate = True
        if (
            in_gate
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
            gate_items += 1
        # Stop at end of file or next section
        if (
            in_gate
            and line.startswith("## ")
            and "quality gate" not in line_lower
            and gate_items > 0
        ):
            break
    assert gate_items >= 7, (
        f"Expected at least 7 Quality Gate steps, found {gate_items}"
    )
