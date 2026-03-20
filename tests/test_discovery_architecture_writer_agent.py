"""
Tests for agents/discovery-architecture-writer.md existence and required content.
TDD: This test is written BEFORE the agents/discovery-architecture-writer.md file is created.
"""

from pathlib import Path

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
ARCH_WRITER_AGENT_PATH = REPO_ROOT / "agents" / "discovery-architecture-writer.md"


# --- File existence and frontmatter ---


def test_discovery_architecture_writer_agent_exists():
    """agents/discovery-architecture-writer.md must exist."""
    assert ARCH_WRITER_AGENT_PATH.exists(), (
        f"agents/discovery-architecture-writer.md not found at {ARCH_WRITER_AGENT_PATH}"
    )


def test_discovery_architecture_writer_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = ARCH_WRITER_AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-architecture-writer.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-architecture-writer.md must have closing --- for frontmatter"
    )


def test_discovery_architecture_writer_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-architecture-writer'."""
    content = ARCH_WRITER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-architecture-writer", (
        f"meta.name must be 'discovery-architecture-writer', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_architecture_writer_frontmatter_has_description():
    """Frontmatter must have meta.description (non-empty)."""
    content = ARCH_WRITER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_discovery_architecture_writer_frontmatter_model_role_writing():
    """Frontmatter must have model_role: writing."""
    content = ARCH_WRITER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "writing", (
        f"model_role must be 'writing', got: {frontmatter['model_role']}"
    )


# --- Markdown body structure ---


def test_discovery_architecture_writer_body_mentions_overview_md():
    """Body must mention overview.md."""
    content = ARCH_WRITER_AGENT_PATH.read_text()
    assert "overview.md" in content, "Body must mention overview.md"


def test_discovery_architecture_writer_body_mentions_findings():
    """Body must mention findings (case insensitive)."""
    content = ARCH_WRITER_AGENT_PATH.read_text()
    assert "findings" in content.lower(), "Body must mention findings"


def test_discovery_architecture_writer_body_mentions_architect():
    """Body must mention architect (case insensitive)."""
    content = ARCH_WRITER_AGENT_PATH.read_text()
    assert "architect" in content.lower(), "Body must mention architect"


def test_discovery_architecture_writer_body_describes_overview_md_output():
    """Body must describe overview.md as an output artifact."""
    content = ARCH_WRITER_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert "overview.md" in body, "Body must describe overview.md as an output artifact"


def test_discovery_architecture_writer_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = ARCH_WRITER_AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
