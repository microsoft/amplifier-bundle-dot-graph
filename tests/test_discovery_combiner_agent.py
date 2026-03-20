"""
Tests for agents/discovery-combiner.md existence and required content.
TDD: This test is written BEFORE the agents/discovery-combiner.md file is created.
"""

from pathlib import Path

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
COMBINER_AGENT_PATH = REPO_ROOT / "agents" / "discovery-combiner.md"


# --- File existence and frontmatter ---


def test_discovery_combiner_agent_exists():
    """agents/discovery-combiner.md must exist."""
    assert COMBINER_AGENT_PATH.exists(), (
        f"agents/discovery-combiner.md not found at {COMBINER_AGENT_PATH}"
    )


def test_discovery_combiner_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = COMBINER_AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-combiner.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-combiner.md must have closing --- for frontmatter"
    )


def test_discovery_combiner_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-combiner'."""
    content = COMBINER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-combiner", (
        f"meta.name must be 'discovery-combiner', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_combiner_frontmatter_has_description():
    """Frontmatter must have meta.description (non-empty)."""
    content = COMBINER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_discovery_combiner_description_has_two_examples():
    """Description must contain at least 2 <example> blocks."""
    content = COMBINER_AGENT_PATH.read_text()
    assert content.count("<example>") >= 2, (
        f"Description must contain at least 2 <example> blocks, found {content.count('<example>')}"
    )


def test_discovery_combiner_frontmatter_model_role_coding():
    """Frontmatter must have model_role: reasoning."""
    content = COMBINER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "coding", (
        f"model_role must be 'reasoning', got: {frontmatter['model_role']}"
    )


def test_discovery_combiner_frontmatter_has_tool_dot_graph():
    """Frontmatter must declare tool-dot-graph in tools."""
    content = COMBINER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" in frontmatter, "Frontmatter must have 'tools' key"
    tool_names = [
        t.get("module", "") for t in frontmatter["tools"] if isinstance(t, dict)
    ]
    assert "tool-dot-graph" in tool_names, (
        f"tools must include 'tool-dot-graph', got: {tool_names}"
    )


# --- Markdown body structure ---


def test_discovery_combiner_body_has_main_heading():
    """Markdown body must contain a heading about Combiner, Convergence, or Divergence."""
    content = COMBINER_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert any(
        keyword in body
        for keyword in [
            "Combiner",
            "combiner",
            "Convergence",
            "convergence",
            "Divergence",
            "divergence",
        ]
    ), "Body must contain a heading about Combiner, Convergence, or Divergence"


def test_discovery_combiner_body_mentions_convergence_and_divergence():
    """Body must mention both convergence and divergence."""
    content = COMBINER_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    lower = body.lower()
    assert "convergence" in lower or "converge" in lower, (
        "Body must mention convergence"
    )
    assert "divergence" in lower or "diverge" in lower, "Body must mention divergence"


def test_discovery_combiner_body_prohibits_reconciling_divergences():
    """Body must prohibit reconciling divergences (anti-rationalization rule)."""
    content = COMBINER_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    lower = body.lower()
    assert any(
        phrase in lower
        for phrase in [
            "do not reconcile",
            "don't reconcile",
            "not reconcile",
            "anti-rationalization",
            "do not pick",
            "track both",
        ]
    ), "Body must prohibit reconciling divergences (anti-rationalization rule)"


def test_discovery_combiner_references_instruction_file():
    """Body must @mention discovery-combiner-instructions context file."""
    content = COMBINER_AGENT_PATH.read_text()
    assert "discovery-combiner-instructions" in content, (
        "Body must reference @dot-graph:context/discovery-combiner-instructions"
    )


def test_discovery_combiner_requires_diagram_dot_output():
    """Body must require diagram.dot as an output artifact."""
    content = COMBINER_AGENT_PATH.read_text()
    assert "diagram.dot" in content, (
        "Body must require diagram.dot as an output artifact"
    )


def test_discovery_combiner_has_required_artifacts_section():
    """Body must contain 'Required Artifacts' section."""
    content = COMBINER_AGENT_PATH.read_text()
    assert "Required Artifacts" in content, (
        "Body must contain 'Required Artifacts' section"
    )


def test_discovery_combiner_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = COMBINER_AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
