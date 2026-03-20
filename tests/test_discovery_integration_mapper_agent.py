"""
Tests for agents/discovery-integration-mapper.md existence and required content.
TDD: This test is written BEFORE the agents/discovery-integration-mapper.md file is created.
"""

from pathlib import Path

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
INTEGRATION_MAPPER_AGENT_PATH = REPO_ROOT / "agents" / "discovery-integration-mapper.md"


# --- File existence and frontmatter ---


def test_discovery_integration_mapper_agent_exists():
    """agents/discovery-integration-mapper.md must exist."""
    assert INTEGRATION_MAPPER_AGENT_PATH.exists(), (
        f"agents/discovery-integration-mapper.md not found at {INTEGRATION_MAPPER_AGENT_PATH}"
    )


def test_discovery_integration_mapper_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = INTEGRATION_MAPPER_AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-integration-mapper.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-integration-mapper.md must have closing --- for frontmatter"
    )


def test_discovery_integration_mapper_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-integration-mapper'."""
    content = INTEGRATION_MAPPER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-integration-mapper", (
        f"meta.name must be 'discovery-integration-mapper', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_integration_mapper_frontmatter_has_description():
    """Frontmatter must have meta.description (non-empty)."""
    content = INTEGRATION_MAPPER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_discovery_integration_mapper_description_has_two_examples():
    """Description must contain at least 2 <example> blocks."""
    content = INTEGRATION_MAPPER_AGENT_PATH.read_text()
    assert content.count("<example>") >= 2, (
        f"Description must contain at least 2 <example> blocks, found {content.count('<example>')}"
    )


def test_discovery_integration_mapper_frontmatter_model_role_coding():
    """Frontmatter must have model_role: reasoning."""
    content = INTEGRATION_MAPPER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "coding", (
        f"model_role must be 'reasoning', got: {frontmatter['model_role']}"
    )


def test_discovery_integration_mapper_frontmatter_has_tool_dot_graph():
    """Frontmatter must declare tool-dot-graph in tools."""
    content = INTEGRATION_MAPPER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" in frontmatter, "Frontmatter must have 'tools' key"
    tool_names = [
        t.get("module", "") for t in frontmatter["tools"] if isinstance(t, dict)
    ]
    assert "tool-dot-graph" in tool_names, (
        f"tools must include 'tool-dot-graph', got: {tool_names}"
    )


# --- Markdown body structure ---


def test_discovery_integration_mapper_body_has_main_heading():
    """Markdown body must contain a heading about integration mapping."""
    content = INTEGRATION_MAPPER_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert (
        "Integration Mapper" in body
        or "integration-mapper" in body
        or "Integration" in body
    ), "Body must contain a heading about integration mapping"


def test_discovery_integration_mapper_body_identifies_as_where_or_why_agent():
    """Body must identify as the WHERE or WHY agent."""
    content = INTEGRATION_MAPPER_AGENT_PATH.read_text()
    assert "WHERE" in content or "WHY" in content, (
        "Body must identify as the WHERE or WHY agent"
    )


def test_discovery_integration_mapper_body_mentions_fresh_context():
    """Body must mention fresh context / zero prior context mandate."""
    content = INTEGRATION_MAPPER_AGENT_PATH.read_text()
    assert (
        "fresh context" in content.lower()
        or "zero prior" in content.lower()
        or "fresh" in content.lower()
    ), "Body must mention fresh context / zero prior context mandate"


def test_discovery_integration_mapper_body_discusses_boundaries():
    """Body must discuss integration boundaries."""
    content = INTEGRATION_MAPPER_AGENT_PATH.read_text()
    assert "boundar" in content.lower(), "Body must discuss integration boundaries"


def test_discovery_integration_mapper_references_instruction_file():
    """Body must @mention discovery-integration-mapper-instructions context file."""
    content = INTEGRATION_MAPPER_AGENT_PATH.read_text()
    assert "discovery-integration-mapper-instructions" in content, (
        "Body must reference @dot-graph:context/discovery-integration-mapper-instructions"
    )


def test_discovery_integration_mapper_requires_diagram_dot_output():
    """Body must require diagram.dot as an output artifact."""
    content = INTEGRATION_MAPPER_AGENT_PATH.read_text()
    assert "diagram.dot" in content, (
        "Body must require diagram.dot as an output artifact"
    )


def test_discovery_integration_mapper_has_required_artifacts_section():
    """Body must contain 'Required Artifacts' section."""
    content = INTEGRATION_MAPPER_AGENT_PATH.read_text()
    assert "Required Artifacts" in content, (
        "Body must contain 'Required Artifacts' section"
    )


def test_discovery_integration_mapper_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = INTEGRATION_MAPPER_AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
