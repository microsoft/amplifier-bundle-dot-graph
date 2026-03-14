"""
Tests for agents/dot-author.md existence and required content.
TDD: This test is written BEFORE the agents/dot-author.md file is created.
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
DOT_AUTHOR_PATH = REPO_ROOT / "agents" / "dot-author.md"


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file. Returns (frontmatter_dict, body)."""
    if not content.startswith("---"):
        return {}, content
    end = content.index("---", 3)
    yaml_block = content[3:end].strip()
    body = content[end + 3 :].strip()
    return yaml.safe_load(yaml_block), body


# --- File existence and frontmatter ---


def test_dot_author_agent_exists():
    """agents/dot-author.md must exist."""
    assert DOT_AUTHOR_PATH.exists(), (
        f"agents/dot-author.md not found at {DOT_AUTHOR_PATH}"
    )


def test_dot_author_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = DOT_AUTHOR_PATH.read_text()
    assert content.startswith("---"), (
        "agents/dot-author.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/dot-author.md must have closing --- for frontmatter"
    )


def test_dot_author_frontmatter_has_meta_name():
    """Frontmatter must contain meta.name = 'dot-author'."""
    content = DOT_AUTHOR_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "dot-author", (
        f"meta.name must be 'dot-author', got: {frontmatter['meta'].get('name')}"
    )


def test_dot_author_frontmatter_has_description():
    """Frontmatter must have meta.description."""
    content = DOT_AUTHOR_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_dot_author_description_has_three_examples():
    """Description must contain 3 <example> blocks."""
    content = DOT_AUTHOR_PATH.read_text()
    assert content.count("<example>") >= 3, (
        f"Description must contain at least 3 <example> blocks, found {content.count('<example>')}"
    )


def test_dot_author_frontmatter_has_model_role_coding():
    """Frontmatter must have model_role: coding."""
    content = DOT_AUTHOR_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "coding", (
        f"model_role must be 'coding', got: {frontmatter['model_role']}"
    )


# --- Markdown body structure ---


def test_dot_author_body_has_main_heading():
    """Markdown body must contain heading '# DOT Author Agent'."""
    content = DOT_AUTHOR_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert "# DOT Author Agent" in body, (
        "Body must contain '# DOT Author Agent' heading"
    )


def test_dot_author_body_has_execution_model_statement():
    """Body must contain execution model / one-shot sub-session statement."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "one-shot" in content.lower() or "one shot" in content.lower(), (
        "Body must contain execution model statement (one-shot sub-session)"
    )


def test_dot_author_body_has_your_expertise_section():
    """Body must contain 'Your Expertise' section."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "Your Expertise" in content, "Body must contain 'Your Expertise' section"


def test_dot_author_body_has_knowledge_base_section():
    """Body must contain 'Knowledge Base' section."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "Knowledge Base" in content, "Body must contain 'Knowledge Base' section"


def test_dot_author_knowledge_base_has_six_mentions():
    """Knowledge Base must contain 6 @mention references."""
    content = DOT_AUTHOR_PATH.read_text()
    required_mentions = [
        "DOT-SYNTAX-REFERENCE.md",
        "DOT-PATTERNS.md",
        "DOT-QUALITY-STANDARDS.md",
        "GRAPHVIZ-SETUP.md",
        "GRAPH-ANALYSIS-GUIDE.md",
        "dot-instructions.md",
    ]
    for mention in required_mentions:
        assert mention in content, f"Knowledge Base must @mention '{mention}'"


def test_dot_author_has_generate_dot_capability():
    """Body must contain 'Generate DOT from Scratch' capability section."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "Generate DOT from Scratch" in content, (
        "Body must contain 'Generate DOT from Scratch' capability section"
    )


def test_dot_author_generate_dot_has_five_steps():
    """Generate DOT section must have 5 numbered steps."""
    content = DOT_AUTHOR_PATH.read_text()
    # Find section start
    assert "Generate DOT from Scratch" in content, "Missing Generate DOT section"
    # The section has 5 steps - verify by checking for at least 5 numbered items in context
    # We look for numbered items after "Generate DOT"
    idx = content.index("Generate DOT from Scratch")
    section = content[idx : idx + 1500]
    step_count = sum(
        1 for i in range(1, 6) if f"{i}." in section or f"{i}. " in section
    )
    assert step_count >= 5, (
        f"Generate DOT section must have at least 5 steps, found indicators for {step_count}"
    )


def test_dot_author_has_review_refine_capability():
    """Body must contain 'Review and Refine Existing DOT' capability section."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "Review and Refine Existing DOT" in content, (
        "Body must contain 'Review and Refine Existing DOT' capability section"
    )


def test_dot_author_has_convert_descriptions_capability():
    """Body must contain 'Convert Descriptions to DOT' capability section."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "Convert Descriptions to DOT" in content, (
        "Body must contain 'Convert Descriptions to DOT' capability section"
    )


def test_dot_author_has_explain_dot_structures_capability():
    """Body must contain 'Explain DOT Structures' capability section."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "Explain DOT Structures" in content, (
        "Body must contain 'Explain DOT Structures' capability section"
    )


def test_dot_author_has_quality_standards_section():
    """Body must contain 'Quality Standards' section."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "Quality Standards" in content, (
        "Body must contain 'Quality Standards' section"
    )


def test_dot_author_quality_standards_has_line_count_targets():
    """Quality Standards section must mention line count targets."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "100" in content and "200" in content, (
        "Quality Standards must mention line count targets (100-200 for overview)"
    )


def test_dot_author_quality_standards_mentions_legend():
    """Quality Standards section must mention legend requirement."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "legend" in content.lower(), (
        "Quality Standards must mention legend requirement"
    )


def test_dot_author_quality_standards_mentions_clusters():
    """Quality Standards section must mention cluster usage."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "cluster" in content.lower(), "Quality Standards must mention cluster usage"


def test_dot_author_quality_standards_mentions_snake_case():
    """Quality Standards section must mention snake_case node IDs."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "snake_case" in content, "Quality Standards must mention snake_case node IDs"


def test_dot_author_quality_standards_no_orphans():
    """Quality Standards must mention no orphan nodes."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "orphan" in content.lower(), "Quality Standards must mention no orphan nodes"


def test_dot_author_quality_standards_no_shape_record():
    """Quality Standards must mention no shape=record."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "shape=record" in content, "Quality Standards must mention 'no shape=record'"


def test_dot_author_quality_standards_no_hardcoded_positions():
    """Quality Standards must mention no hardcoded positions."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "hardcoded" in content.lower() or "pos=" in content, (
        "Quality Standards must mention no hardcoded positions"
    )


def test_dot_author_quality_standards_graph_level_attributes():
    """Quality Standards must mention graph-level attributes."""
    content = DOT_AUTHOR_PATH.read_text()
    assert (
        "fontname" in content
        or "graph-level" in content.lower()
        or "rankdir" in content
    ), "Quality Standards must mention graph-level attributes (fontname, rankdir)"


def test_dot_author_has_progressive_disclosure_section():
    """Body must contain 'Progressive Disclosure' section."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "Progressive Disclosure" in content, (
        "Body must contain 'Progressive Disclosure' section"
    )


def test_dot_author_has_output_format_section():
    """Body must contain 'Output Format' section."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "Output Format" in content, "Body must contain 'Output Format' section"


def test_dot_author_has_when_tools_unavailable_section():
    """Body must contain 'When Tools Are Unavailable' section."""
    content = DOT_AUTHOR_PATH.read_text()
    assert (
        "When Tools Are Unavailable" in content or "Tools Are Unavailable" in content
    ), "Body must contain 'When Tools Are Unavailable' section"


def test_dot_author_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = DOT_AUTHOR_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    # Verify it's near the end (within last 100 chars)
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
