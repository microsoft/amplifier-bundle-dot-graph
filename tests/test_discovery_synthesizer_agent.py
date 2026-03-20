"""
Tests for agents/discovery-synthesizer.md existence and required content.
TDD: This test is written BEFORE the agents/discovery-synthesizer.md file is created.
"""

from pathlib import Path

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
SYNTHESIZER_AGENT_PATH = REPO_ROOT / "agents" / "discovery-synthesizer.md"


# --- File existence and frontmatter ---


def test_discovery_synthesizer_agent_exists():
    """agents/discovery-synthesizer.md must exist."""
    assert SYNTHESIZER_AGENT_PATH.exists(), (
        f"agents/discovery-synthesizer.md not found at {SYNTHESIZER_AGENT_PATH}"
    )


def test_discovery_synthesizer_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = SYNTHESIZER_AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-synthesizer.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-synthesizer.md must have closing --- for frontmatter"
    )


def test_discovery_synthesizer_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-synthesizer'."""
    content = SYNTHESIZER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-synthesizer", (
        f"meta.name must be 'discovery-synthesizer', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_synthesizer_frontmatter_has_description():
    """Frontmatter must have meta.description (non-empty)."""
    content = SYNTHESIZER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_discovery_synthesizer_description_has_two_examples():
    """Description must contain at least 2 <example> blocks."""
    content = SYNTHESIZER_AGENT_PATH.read_text()
    assert content.count("<example>") >= 2, (
        f"Description must contain at least 2 <example> blocks, found {content.count('<example>')}"
    )


def test_discovery_synthesizer_frontmatter_model_role_coding():
    """Frontmatter must have model_role: reasoning."""
    content = SYNTHESIZER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "coding", (
        f"model_role must be 'reasoning', got: {frontmatter['model_role']}"
    )


def test_discovery_synthesizer_frontmatter_has_tool_dot_graph():
    """Frontmatter must declare tool-dot-graph in tools."""
    content = SYNTHESIZER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" in frontmatter, "Frontmatter must have 'tools' key"
    tool_names = [
        t.get("module", "") for t in frontmatter["tools"] if isinstance(t, dict)
    ]
    assert "tool-dot-graph" in tool_names, (
        f"tools must include 'tool-dot-graph', got: {tool_names}"
    )


# --- Markdown body structure ---


def test_discovery_synthesizer_body_has_main_heading():
    """Markdown body must contain a heading about synthesis/reconciliation."""
    content = SYNTHESIZER_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert "Synthesizer" in body or "synthesizer" in body or "Reconcil" in body, (
        "Body must contain a heading about synthesis or reconciliation"
    )


def test_discovery_synthesizer_body_discusses_reconciliation():
    """Body must discuss reconciliation."""
    content = SYNTHESIZER_AGENT_PATH.read_text()
    assert "reconcil" in content.lower(), "Body must discuss reconciliation"


def test_discovery_synthesizer_body_mentions_discrepancy_tracking():
    """Body must mention discrepancy tracking."""
    content = SYNTHESIZER_AGENT_PATH.read_text()
    assert "discrepanc" in content.lower(), "Body must mention discrepancy tracking"


def test_discovery_synthesizer_body_mentions_consensus():
    """Body must mention consensus."""
    content = SYNTHESIZER_AGENT_PATH.read_text()
    assert "consensus" in content.lower(), "Body must mention consensus"


def test_discovery_synthesizer_body_prohibits_fiat():
    """Body must prohibit reconciliation by fiat."""
    content = SYNTHESIZER_AGENT_PATH.read_text()
    assert (
        "fiat" in content.lower()
        or "no fiat" in content.lower()
        or "not fiat" in content.lower()
    ), "Body must prohibit reconciliation by fiat"


def test_discovery_synthesizer_references_instruction_file():
    """Body must @mention discovery-synthesizer-instructions context file."""
    content = SYNTHESIZER_AGENT_PATH.read_text()
    assert "discovery-synthesizer-instructions" in content, (
        "Body must reference @dot-graph:context/discovery-synthesizer-instructions"
    )


def test_discovery_synthesizer_requires_diagram_dot_output():
    """Body must require diagram.dot as an output artifact."""
    content = SYNTHESIZER_AGENT_PATH.read_text()
    assert "diagram.dot" in content, (
        "Body must require diagram.dot as an output artifact"
    )


def test_discovery_synthesizer_has_required_artifacts_section():
    """Body must contain 'Required Artifacts' section."""
    content = SYNTHESIZER_AGENT_PATH.read_text()
    assert "Required Artifacts" in content, (
        "Body must contain 'Required Artifacts' section"
    )


def test_discovery_synthesizer_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = SYNTHESIZER_AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
