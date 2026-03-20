"""
Tests for agents/discovery-prescan.md existence and required content.
TDD: This test is written BEFORE the agents/discovery-prescan.md file is created.
"""

from pathlib import Path

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
PRESCAN_AGENT_PATH = REPO_ROOT / "agents" / "discovery-prescan.md"


# --- File existence and frontmatter ---


def test_discovery_prescan_agent_exists():
    """agents/discovery-prescan.md must exist."""
    assert PRESCAN_AGENT_PATH.exists(), (
        f"agents/discovery-prescan.md not found at {PRESCAN_AGENT_PATH}"
    )


def test_discovery_prescan_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = PRESCAN_AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-prescan.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-prescan.md must have closing --- for frontmatter"
    )


def test_discovery_prescan_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-prescan'."""
    content = PRESCAN_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-prescan", (
        f"meta.name must be 'discovery-prescan', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_prescan_frontmatter_has_description():
    """Frontmatter must have meta.description (non-empty)."""
    content = PRESCAN_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_discovery_prescan_description_has_two_examples():
    """Description must contain at least 2 <example> blocks."""
    content = PRESCAN_AGENT_PATH.read_text()
    assert content.count("<example>") >= 2, (
        f"Description must contain at least 2 <example> blocks, found {content.count('<example>')}"
    )


def test_discovery_prescan_frontmatter_model_role_general():
    """Frontmatter must have model_role: reasoning."""
    content = PRESCAN_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "general", (
        f"model_role must be 'reasoning', got: {frontmatter['model_role']}"
    )


def test_discovery_prescan_has_no_tools():
    """Prescan agent needs no tools (receives inventory as input)."""
    content = PRESCAN_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" not in frontmatter, (
        "Prescan agent should not declare any tools — it receives inventory as input"
    )


# --- Markdown body structure ---


def test_discovery_prescan_body_has_main_heading():
    """Markdown body must contain a heading with 'Prescan'."""
    content = PRESCAN_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert "Prescan" in body, "Body must contain 'Prescan' in the main heading"


def test_discovery_prescan_body_mentions_structural_inventory():
    """Body must mention 'structural inventory' as input."""
    content = PRESCAN_AGENT_PATH.read_text()
    assert "structural inventory" in content.lower(), (
        "Body must mention 'structural inventory' as input"
    )


def test_discovery_prescan_body_discusses_topic_selection():
    """Body must discuss topic selection."""
    content = PRESCAN_AGENT_PATH.read_text()
    assert "topic" in content.lower(), "Body must discuss topic selection"
    assert "select" in content.lower() or "selection" in content.lower(), (
        "Body must discuss topic selection"
    )


def test_discovery_prescan_references_instruction_file():
    """Body must @mention discovery-prescan-instructions context file."""
    content = PRESCAN_AGENT_PATH.read_text()
    assert "discovery-prescan-instructions" in content, (
        "Body must reference @dot-graph:context/discovery-prescan-instructions"
    )


def test_discovery_prescan_has_your_knowledge_section():
    """Body must contain 'Your Knowledge' section."""
    content = PRESCAN_AGENT_PATH.read_text()
    assert "Your Knowledge" in content or "Knowledge" in content, (
        "Body must contain a 'Your Knowledge' (or similar) section"
    )


def test_discovery_prescan_has_your_role_section():
    """Body must contain 'Your Role' section."""
    content = PRESCAN_AGENT_PATH.read_text()
    assert "Your Role" in content or "## Role" in content, (
        "Body must contain a 'Your Role' section"
    )


def test_discovery_prescan_has_required_artifacts_section():
    """Body must contain 'Required Artifacts' section."""
    content = PRESCAN_AGENT_PATH.read_text()
    assert "Required Artifacts" in content, (
        "Body must contain 'Required Artifacts' section"
    )


def test_discovery_prescan_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = PRESCAN_AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
