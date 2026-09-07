"""
Tests for agents/discovery-code-tracer.md existence and required content.
TDD: This test is written BEFORE the agents/discovery-code-tracer.md file is created.
"""

from pathlib import Path

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
CODE_TRACER_AGENT_PATH = REPO_ROOT / "agents" / "discovery-code-tracer.md"

# Always-on catalog budget for meta.description (chars).
# See foundation:context/shared/description-authoring-principles.md V3.
DESCRIPTION_CHAR_BUDGET = 600


# --- File existence and frontmatter ---


def test_discovery_code_tracer_agent_exists():
    """agents/discovery-code-tracer.md must exist."""
    assert CODE_TRACER_AGENT_PATH.exists(), (
        f"agents/discovery-code-tracer.md not found at {CODE_TRACER_AGENT_PATH}"
    )


def test_discovery_code_tracer_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = CODE_TRACER_AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-code-tracer.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-code-tracer.md must have closing --- for frontmatter"
    )


def test_discovery_code_tracer_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-code-tracer'."""
    content = CODE_TRACER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-code-tracer", (
        f"meta.name must be 'discovery-code-tracer', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_code_tracer_frontmatter_has_description():
    """Frontmatter must have meta.description (non-empty)."""
    content = CODE_TRACER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_discovery_code_tracer_description_has_no_examples():
    """meta.description must carry ZERO <example>/<commentary> blocks, within budget.

    Policy: foundation:context/shared/description-authoring-principles.md V3.
    Every agent description is concatenated into the delegate tool's own
    description, which loads on EVERY turn of EVERY session whether or not this
    agent is ever delegated to. An example block is therefore paid for per turn
    and teaches the model nothing an explicit WHEN clause cannot state directly.
    """
    content = CODE_TRACER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    description = frontmatter["meta"]["description"]
    assert description.count("<example>") == 0, (
        f"meta.description must contain ZERO <example> blocks, "
        f"found {description.count('<example>')}"
    )
    assert description.count("<commentary>") == 0, (
        f"meta.description must contain ZERO <commentary> tags, "
        f"found {description.count('<commentary>')}"
    )
    assert len(description) <= DESCRIPTION_CHAR_BUDGET, (
        f"meta.description is {len(description)} chars, over the "
        f"{DESCRIPTION_CHAR_BUDGET}-char always-on catalog budget"
    )


def test_discovery_code_tracer_frontmatter_model_role_coding():
    """Frontmatter must have model_role: coding."""
    content = CODE_TRACER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "coding", (
        f"model_role must be 'coding', got: {frontmatter['model_role']}"
    )


def test_discovery_code_tracer_frontmatter_has_tool_dot_graph():
    """Frontmatter must declare tool-dot-graph in tools."""
    content = CODE_TRACER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" in frontmatter, "Frontmatter must have 'tools' key"
    tool_names = [
        t.get("module", "") for t in frontmatter["tools"] if isinstance(t, dict)
    ]
    assert "tool-dot-graph" in tool_names, (
        f"tools must include 'tool-dot-graph', got: {tool_names}"
    )


# --- Markdown body structure ---


def test_discovery_code_tracer_body_has_main_heading():
    """Markdown body must contain a heading about code tracing."""
    content = CODE_TRACER_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert "Code Tracer" in body or "code-tracer" in body or "Code Trace" in body, (
        "Body must contain a heading about code tracing"
    )


def test_discovery_code_tracer_body_identifies_as_how_agent():
    """Body must identify as the HOW agent."""
    content = CODE_TRACER_AGENT_PATH.read_text()
    assert "HOW" in content, "Body must identify as the HOW agent"


def test_discovery_code_tracer_body_mentions_fresh_context():
    """Body must mention fresh context / zero prior context mandate."""
    content = CODE_TRACER_AGENT_PATH.read_text()
    assert (
        "fresh context" in content.lower()
        or "zero prior" in content.lower()
        or "fresh" in content.lower()
    ), "Body must mention fresh context / zero prior context mandate"


def test_discovery_code_tracer_body_mentions_independent_perspective():
    """Body must mention independent perspective."""
    content = CODE_TRACER_AGENT_PATH.read_text()
    assert "independent" in content.lower() or "clean slate" in content.lower(), (
        "Body must mention independent perspective"
    )


def test_discovery_code_tracer_references_instruction_file():
    """Body must @mention discovery-code-tracer-instructions context file."""
    content = CODE_TRACER_AGENT_PATH.read_text()
    assert "discovery-code-tracer-instructions" in content, (
        "Body must reference @dot-graph:context/discovery-code-tracer-instructions"
    )


def test_discovery_code_tracer_requires_diagram_dot_output():
    """Body must require diagram.dot as an output artifact."""
    content = CODE_TRACER_AGENT_PATH.read_text()
    assert "diagram.dot" in content, (
        "Body must require diagram.dot as an output artifact"
    )


def test_discovery_code_tracer_has_required_artifacts_section():
    """Body must contain 'Required Artifacts' section."""
    content = CODE_TRACER_AGENT_PATH.read_text()
    assert "Required Artifacts" in content, (
        "Body must contain 'Required Artifacts' section"
    )


def test_discovery_code_tracer_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = CODE_TRACER_AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
