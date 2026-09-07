"""
Tests for agents/discovery-behavior-observer.md existence and required content.
TDD: This test is written BEFORE the agents/discovery-behavior-observer.md file is created.
"""

from pathlib import Path

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
BEHAVIOR_OBSERVER_AGENT_PATH = REPO_ROOT / "agents" / "discovery-behavior-observer.md"

# Always-on catalog budget for meta.description (chars).
# See foundation:context/shared/description-authoring-principles.md V3.
DESCRIPTION_CHAR_BUDGET = 600


# --- File existence and frontmatter ---


def test_discovery_behavior_observer_agent_exists():
    """agents/discovery-behavior-observer.md must exist."""
    assert BEHAVIOR_OBSERVER_AGENT_PATH.exists(), (
        f"agents/discovery-behavior-observer.md not found at {BEHAVIOR_OBSERVER_AGENT_PATH}"
    )


def test_discovery_behavior_observer_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-behavior-observer.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-behavior-observer.md must have closing --- for frontmatter"
    )


def test_discovery_behavior_observer_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-behavior-observer'."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-behavior-observer", (
        f"meta.name must be 'discovery-behavior-observer', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_behavior_observer_frontmatter_has_description():
    """Frontmatter must have meta.description (non-empty)."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_discovery_behavior_observer_description_has_no_examples():
    """meta.description must carry ZERO <example>/<commentary> blocks, within budget.

    Policy: foundation:context/shared/description-authoring-principles.md V3.
    Every agent description is concatenated into the delegate tool's own
    description, which loads on EVERY turn of EVERY session whether or not this
    agent is ever delegated to. An example block is therefore paid for per turn
    and teaches the model nothing an explicit WHEN clause cannot state directly.
    """
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
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


def test_discovery_behavior_observer_frontmatter_model_role_research():
    """Frontmatter must have model_role: research."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "research", (
        f"model_role must be 'research', got: {frontmatter['model_role']}"
    )


def test_discovery_behavior_observer_frontmatter_has_tool_dot_graph():
    """Frontmatter must declare tool-dot-graph in tools."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" in frontmatter, "Frontmatter must have 'tools' key"
    tool_names = [
        t.get("module", "") for t in frontmatter["tools"] if isinstance(t, dict)
    ]
    assert "tool-dot-graph" in tool_names, (
        f"tools must include 'tool-dot-graph', got: {tool_names}"
    )


# --- Markdown body structure ---


def test_discovery_behavior_observer_body_has_main_heading():
    """Markdown body must contain a heading about behavior observation."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert (
        "Behavior Observer" in body or "behavior-observer" in body or "Behavior" in body
    ), "Body must contain a heading about behavior observation"


def test_discovery_behavior_observer_body_identifies_as_what_agent():
    """Body must identify as the WHAT agent."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert "WHAT" in content, "Body must identify as the WHAT agent"


def test_discovery_behavior_observer_body_mentions_fresh_context():
    """Body must mention fresh context / zero prior context mandate."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert (
        "fresh context" in content.lower()
        or "zero prior" in content.lower()
        or "fresh" in content.lower()
    ), "Body must mention fresh context / zero prior context mandate"


def test_discovery_behavior_observer_body_mentions_ten_plus_instances():
    """Body must mention examining 10+ instances."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert "10" in content or "ten" in content.lower(), (
        "Body must mention examining 10+ instances"
    )


def test_discovery_behavior_observer_references_instruction_file():
    """Body must @mention discovery-behavior-observer-instructions context file."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert "discovery-behavior-observer-instructions" in content, (
        "Body must reference @dot-graph:context/discovery-behavior-observer-instructions"
    )


def test_discovery_behavior_observer_requires_diagram_dot_output():
    """Body must require diagram.dot as an output artifact."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert "diagram.dot" in content, (
        "Body must require diagram.dot as an output artifact"
    )


def test_discovery_behavior_observer_has_required_artifacts_section():
    """Body must contain 'Required Artifacts' section."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert "Required Artifacts" in content, (
        "Body must contain 'Required Artifacts' section"
    )


def test_discovery_behavior_observer_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
