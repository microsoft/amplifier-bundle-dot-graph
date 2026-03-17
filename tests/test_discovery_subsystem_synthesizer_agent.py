"""
Tests for agents/discovery-subsystem-synthesizer.md existence and required content.
"""

from pathlib import Path

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
SUBSYSTEM_SYNTHESIZER_AGENT_PATH = (
    REPO_ROOT / "agents" / "discovery-subsystem-synthesizer.md"
)


# --- File existence and frontmatter ---


def test_discovery_subsystem_synthesizer_agent_exists():
    """agents/discovery-subsystem-synthesizer.md must exist."""
    assert SUBSYSTEM_SYNTHESIZER_AGENT_PATH.exists(), (
        f"agents/discovery-subsystem-synthesizer.md not found at {SUBSYSTEM_SYNTHESIZER_AGENT_PATH}"
    )


def test_discovery_subsystem_synthesizer_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = SUBSYSTEM_SYNTHESIZER_AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-subsystem-synthesizer.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-subsystem-synthesizer.md must have closing --- for frontmatter"
    )


def test_discovery_subsystem_synthesizer_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-subsystem-synthesizer'."""
    content = SUBSYSTEM_SYNTHESIZER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-subsystem-synthesizer", (
        f"meta.name must be 'discovery-subsystem-synthesizer', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_subsystem_synthesizer_frontmatter_has_description():
    """Frontmatter must have meta.description (non-empty)."""
    content = SUBSYSTEM_SYNTHESIZER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_discovery_subsystem_synthesizer_description_has_two_examples():
    """Description must contain at least 2 <example> blocks in the YAML frontmatter."""
    content = SUBSYSTEM_SYNTHESIZER_AGENT_PATH.read_text()
    # Count only within the raw YAML frontmatter block to avoid false positives from the body
    end = content.index("---", 3)
    yaml_block = content[3:end]
    assert yaml_block.count("<example>") >= 2, (
        f"Description must contain at least 2 <example> blocks, found {yaml_block.count('<example>')}"
    )


def test_discovery_subsystem_synthesizer_frontmatter_model_role_reasoning():
    """Frontmatter must have model_role: reasoning."""
    content = SUBSYSTEM_SYNTHESIZER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "reasoning", (
        f"model_role must be 'reasoning', got: {frontmatter['model_role']}"
    )


def test_discovery_subsystem_synthesizer_frontmatter_has_tool_dot_graph():
    """Frontmatter must declare tool-dot-graph in tools."""
    content = SUBSYSTEM_SYNTHESIZER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" in frontmatter, "Frontmatter must have 'tools' key"
    tool_names = [
        t.get("module", "") for t in frontmatter["tools"] if isinstance(t, dict)
    ]
    assert "tool-dot-graph" in tool_names, (
        f"tools must include 'tool-dot-graph', got: {tool_names}"
    )


# --- Markdown body structure ---


def test_discovery_subsystem_synthesizer_body_has_main_heading():
    """Markdown body must contain a heading about Subsystem Synthesizer or Seam."""
    content = SUBSYSTEM_SYNTHESIZER_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert (
        "Subsystem Synthesizer" in body
        or "Subsystem Seam" in body
        or "subsystem synthesizer" in body.lower()
        or "Seam" in body
    ), "Body must contain a heading about Subsystem Synthesizer or Seam"


def test_discovery_subsystem_synthesizer_investigates_between_modules():
    """Body must mention investigating what exists 'between' modules."""
    content = SUBSYSTEM_SYNTHESIZER_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert "between" in body.lower(), (
        "Body must mention investigating what exists 'between' modules"
    )
    assert "module" in body.lower(), (
        "Body must mention 'module' as the unit of analysis"
    )


def test_discovery_subsystem_synthesizer_references_instruction_file():
    """Body must @mention discovery-subsystem-synthesizer-instructions context file."""
    content = SUBSYSTEM_SYNTHESIZER_AGENT_PATH.read_text()
    assert "discovery-subsystem-synthesizer-instructions" in content, (
        "Body must reference @dot-graph:context/discovery-subsystem-synthesizer-instructions.md"
    )


def test_discovery_subsystem_synthesizer_requires_diagram_dot_output():
    """Body must require diagram.dot as an output artifact."""
    content = SUBSYSTEM_SYNTHESIZER_AGENT_PATH.read_text()
    assert "diagram.dot" in content, (
        "Body must require diagram.dot as an output artifact"
    )


def test_discovery_subsystem_synthesizer_has_required_artifacts_section():
    """Body must contain 'Required Artifacts' section."""
    content = SUBSYSTEM_SYNTHESIZER_AGENT_PATH.read_text()
    assert "Required Artifacts" in content, (
        "Body must contain 'Required Artifacts' section"
    )


def test_discovery_subsystem_synthesizer_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = SUBSYSTEM_SYNTHESIZER_AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
