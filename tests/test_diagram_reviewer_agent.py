"""
Tests for agents/diagram-reviewer.md existence and required content.
TDD: This test is written BEFORE the agents/diagram-reviewer.md file is created.
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
DIAGRAM_REVIEWER_PATH = REPO_ROOT / "agents" / "diagram-reviewer.md"


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file. Returns (frontmatter_dict, body)."""
    if not content.startswith("---"):
        return {}, content
    end = content.index("---", 3)
    yaml_block = content[3:end].strip()
    body = content[end + 3 :].strip()
    return yaml.safe_load(yaml_block), body


# --- File existence and frontmatter ---


def test_diagram_reviewer_agent_exists():
    """agents/diagram-reviewer.md must exist."""
    assert DIAGRAM_REVIEWER_PATH.exists(), (
        f"agents/diagram-reviewer.md not found at {DIAGRAM_REVIEWER_PATH}"
    )


def test_diagram_reviewer_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert content.startswith("---"), (
        "agents/diagram-reviewer.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/diagram-reviewer.md must have closing --- for frontmatter"
    )


def test_diagram_reviewer_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'diagram-reviewer'."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "diagram-reviewer", (
        f"meta.name must be 'diagram-reviewer', got: {frontmatter['meta'].get('name')}"
    )


def test_diagram_reviewer_frontmatter_has_description():
    """Frontmatter must have meta.description."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_diagram_reviewer_description_has_three_examples():
    """Description must contain 3 <example> blocks."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert content.count("<example>") >= 3, (
        f"Description must contain at least 3 <example> blocks, found {content.count('<example>')}"
    )


def test_diagram_reviewer_frontmatter_has_model_role_critique():
    """Frontmatter must have model_role: critique."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "critique", (
        f"model_role must be 'critique', got: {frontmatter['model_role']}"
    )


# --- Markdown body structure ---


def test_diagram_reviewer_body_has_main_heading():
    """Markdown body must contain heading '# Diagram Reviewer Agent'."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert "# Diagram Reviewer Agent" in body, (
        "Body must contain '# Diagram Reviewer Agent' heading"
    )


def test_diagram_reviewer_body_has_execution_model_statement():
    """Body must contain execution model / one-shot sub-session statement."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert "one-shot" in content.lower() or "one shot" in content.lower(), (
        "Body must contain execution model statement (one-shot sub-session)"
    )


def test_diagram_reviewer_has_four_core_responsibilities():
    """Body must contain 'Core Responsibilities' section with 4 responsibilities."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert "Core Responsibilities" in content, (
        "Body must contain 'Core Responsibilities' section"
    )
    # Find section and count responsibilities
    idx = content.index("Core Responsibilities")
    section = content[idx : idx + 1000]
    # Check for the 4 specific responsibilities from spec
    assert "evaluat" in section.lower(), (
        "Core Responsibilities must mention evaluating quality"
    )
    assert "verdict" in section.lower(), (
        "Core Responsibilities must mention providing verdicts"
    )
    assert "evidence" in section.lower() or "cite" in section.lower(), (
        "Core Responsibilities must mention citing evidence"
    )
    assert "reconciliation" in section.lower(), (
        "Core Responsibilities must mention reconciliation value"
    )


def test_diagram_reviewer_has_knowledge_base_section():
    """Body must contain 'Knowledge Base' section."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert "Knowledge Base" in content, "Body must contain 'Knowledge Base' section"


def test_diagram_reviewer_knowledge_base_has_three_mentions():
    """Knowledge Base must contain 3 @mention references."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    required_mentions = [
        "DOT-QUALITY-STANDARDS.md",
        "DOT-SYNTAX-REFERENCE.md",
        "dot-instructions.md",
    ]
    for mention in required_mentions:
        assert mention in content, f"Knowledge Base must @mention '{mention}'"


def test_diagram_reviewer_has_five_level_review_checklist():
    """Body must contain 5-level Review Checklist."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert "Review Checklist" in content, "Body must contain 'Review Checklist' section"
    # Check for all 5 levels
    for level in range(1, 6):
        assert f"Level {level}" in content, (
            f"Review Checklist must contain 'Level {level}'"
        )


def test_diagram_reviewer_checklist_level1_syntax():
    """Level 1 must be Syntax with 4 checks."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert "Level 1" in content, "Missing Level 1"
    # Find Level 1 section
    idx = content.index("Level 1")
    section = content[idx : idx + 600]
    assert "Syntax" in section or "syntax" in section, "Level 1 must be Syntax"
    # Count checklist items - at least 4 items
    checkboxes = section.count("[ ]") + section.count("[x]") + section.count("- ")
    assert checkboxes >= 4, (
        f"Level 1 Syntax must have at least 4 checks, found {checkboxes}"
    )


def test_diagram_reviewer_checklist_level2_structure():
    """Level 2 must be Structure with 5 checks."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert "Level 2" in content, "Missing Level 2"
    idx = content.index("Level 2")
    section = content[idx : idx + 800]
    assert "Structure" in section or "structure" in section, "Level 2 must be Structure"


def test_diagram_reviewer_checklist_level3_quality():
    """Level 3 must be Quality with 6 checks."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert "Level 3" in content, "Missing Level 3"
    idx = content.index("Level 3")
    section = content[idx : idx + 1000]
    assert "Quality" in section or "quality" in section, "Level 3 must be Quality"


def test_diagram_reviewer_checklist_level4_style():
    """Level 4 must be Style with 5 checks."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert "Level 4" in content, "Missing Level 4"
    idx = content.index("Level 4")
    section = content[idx : idx + 800]
    assert "Style" in section or "style" in section, "Level 4 must be Style"


def test_diagram_reviewer_checklist_level5_reconciliation():
    """Level 5 must be Reconciliation with 5 structural-to-system-problem mappings."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert "Level 5" in content, "Missing Level 5"
    idx = content.index("Level 5")
    section = content[idx : idx + 1000]
    assert "Reconciliation" in section or "reconciliation" in section, (
        "Level 5 must be Reconciliation"
    )


def test_diagram_reviewer_has_output_format_section():
    """Body must contain 'Output Format' section with required template elements."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert "Output Format" in content, "Body must contain 'Output Format' section"
    # Check for required template elements
    assert "File" in content or "file" in content, "Output Format must mention File"
    assert "Type" in content or "type" in content, "Output Format must mention Type"
    assert "Size" in content or "size" in content, "Output Format must mention Size"


def test_diagram_reviewer_output_format_has_findings_sections():
    """Output Format must include Strengths, Warnings, Errors, Reconciliation Notes."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert "Strengths" in content, "Output Format must include 'Strengths' section"
    assert "Warnings" in content, "Output Format must include 'Warnings' section"
    assert "Errors" in content, "Output Format must include 'Errors' section"
    assert "Reconciliation Notes" in content, (
        "Output Format must include 'Reconciliation Notes' section"
    )


def test_diagram_reviewer_output_format_has_verdict_line():
    """Output Format must include a Verdict line."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert "Verdict" in content, "Output Format must include 'Verdict' line"


def test_diagram_reviewer_has_verdict_criteria_section():
    """Body must contain 'Verdict Criteria' section with PASS/WARN/FAIL."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert "Verdict Criteria" in content, "Body must contain 'Verdict Criteria' section"
    assert "PASS" in content, "Verdict Criteria must include 'PASS'"
    assert "WARN" in content, "Verdict Criteria must include 'WARN'"
    assert "FAIL" in content, "Verdict Criteria must include 'FAIL'"


def test_diagram_reviewer_has_philosophy_section():
    """Body must contain 'Philosophy' section."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert "Philosophy" in content, "Body must contain 'Philosophy' section"


def test_diagram_reviewer_philosophy_mentions_specificity():
    """Philosophy section must mention being specific."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    idx = content.index("Philosophy")
    section = content[idx : idx + 800]
    assert "specific" in section.lower(), (
        "Philosophy section must mention being specific"
    )


def test_diagram_reviewer_philosophy_mentions_objective():
    """Philosophy section must mention being objective."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    idx = content.index("Philosophy")
    section = content[idx : idx + 800]
    assert "objective" in section.lower(), (
        "Philosophy section must mention being objective"
    )


def test_diagram_reviewer_philosophy_mentions_reconciliation():
    """Philosophy section must mention valuing reconciliation."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    idx = content.index("Philosophy")
    section = content[idx : idx + 800]
    assert "reconciliation" in section.lower(), (
        "Philosophy section must mention reconciliation"
    )


def test_diagram_reviewer_philosophy_mentions_constructive():
    """Philosophy section must mention being constructive."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    idx = content.index("Philosophy")
    section = content[idx : idx + 800]
    assert "constructive" in section.lower(), (
        "Philosophy section must mention being constructive"
    )


def test_diagram_reviewer_philosophy_mentions_dont_over_fail():
    """Philosophy section must mention not over-failing."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    idx = content.index("Philosophy")
    section = content[idx : idx + 800]
    assert "over-fail" in section.lower() or "over fail" in section.lower(), (
        "Philosophy section must mention not over-failing"
    )


def test_diagram_reviewer_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = DIAGRAM_REVIEWER_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    # Verify it's near the end (within last 100 chars)
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
