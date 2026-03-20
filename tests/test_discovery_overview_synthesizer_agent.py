"""
Tests for agents/discovery-overview-synthesizer.md existence and required content.
TDD: This test is written BEFORE the agents/discovery-overview-synthesizer.md file is created.
"""

from pathlib import Path

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
OVERVIEW_SYNTHESIZER_AGENT_PATH = (
    REPO_ROOT / "agents" / "discovery-overview-synthesizer.md"
)


# --- File existence and frontmatter ---


def test_discovery_overview_synthesizer_agent_exists():
    """agents/discovery-overview-synthesizer.md must exist."""
    assert OVERVIEW_SYNTHESIZER_AGENT_PATH.exists(), (
        f"agents/discovery-overview-synthesizer.md not found at {OVERVIEW_SYNTHESIZER_AGENT_PATH}"
    )


def test_discovery_overview_synthesizer_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = OVERVIEW_SYNTHESIZER_AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-overview-synthesizer.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-overview-synthesizer.md must have closing --- for frontmatter"
    )


def test_discovery_overview_synthesizer_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-overview-synthesizer'."""
    content = OVERVIEW_SYNTHESIZER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-overview-synthesizer", (
        f"meta.name must be 'discovery-overview-synthesizer', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_overview_synthesizer_frontmatter_has_description():
    """Frontmatter must have meta.description (non-empty)."""
    content = OVERVIEW_SYNTHESIZER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_discovery_overview_synthesizer_description_has_two_examples():
    """Description must contain at least 2 <example> blocks in the YAML frontmatter."""
    content = OVERVIEW_SYNTHESIZER_AGENT_PATH.read_text()
    # Count only within the raw YAML frontmatter block to avoid false positives from the body
    end = content.index("---", 3)
    yaml_block = content[3:end]
    assert yaml_block.count("<example>") >= 2, (
        f"Description must contain at least 2 <example> blocks, found {yaml_block.count('<example>')}"
    )


def test_discovery_overview_synthesizer_frontmatter_model_role_coding():
    """Frontmatter must have model_role: reasoning."""
    content = OVERVIEW_SYNTHESIZER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "coding", (
        f"model_role must be 'reasoning', got: {frontmatter['model_role']}"
    )


def test_discovery_overview_synthesizer_frontmatter_has_tool_dot_graph():
    """Frontmatter must declare tool-dot-graph in tools."""
    content = OVERVIEW_SYNTHESIZER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" in frontmatter, "Frontmatter must have 'tools' key"
    tool_names = [
        t.get("module", "") for t in frontmatter["tools"] if isinstance(t, dict)
    ]
    assert "tool-dot-graph" in tool_names, (
        f"tools must include 'tool-dot-graph', got: {tool_names}"
    )


# --- Markdown body structure ---


def test_discovery_overview_synthesizer_body_has_main_heading():
    """Markdown body must contain a heading about Overview Synthesizer or System-Level."""
    content = OVERVIEW_SYNTHESIZER_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert (
        "Overview Synthesizer" in body
        or "System-Level" in body
        or "overview synthesizer" in body.lower()
        or "system-level" in body.lower()
    ), "Body must contain a heading about Overview Synthesizer or System-Level"


def test_discovery_overview_synthesizer_body_mentions_subsystem():
    """Body must mention 'subsystem' as the unit of analysis at overview level."""
    content = OVERVIEW_SYNTHESIZER_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert "subsystem" in body.lower(), (
        "Body must mention 'subsystem' as the unit of analysis"
    )


def test_discovery_overview_synthesizer_references_instruction_file():
    """Body must @mention discovery-overview-synthesizer-instructions context file."""
    content = OVERVIEW_SYNTHESIZER_AGENT_PATH.read_text()
    assert "discovery-overview-synthesizer-instructions" in content, (
        "Body must reference @dot-graph:context/discovery-overview-synthesizer-instructions.md"
    )


def test_discovery_overview_synthesizer_requires_diagram_dot_output():
    """Body must require diagram.dot as an output artifact."""
    content = OVERVIEW_SYNTHESIZER_AGENT_PATH.read_text()
    assert "diagram.dot" in content, (
        "Body must require diagram.dot as an output artifact"
    )


def test_discovery_overview_synthesizer_has_required_artifacts_section():
    """Body must contain 'Required Artifacts' section."""
    content = OVERVIEW_SYNTHESIZER_AGENT_PATH.read_text()
    assert "Required Artifacts" in content, (
        "Body must contain 'Required Artifacts' section"
    )


def test_discovery_overview_synthesizer_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = OVERVIEW_SYNTHESIZER_AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
