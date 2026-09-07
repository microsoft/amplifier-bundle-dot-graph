"""
Tests for behaviors/dot-core.yaml existence and required content.
This behavior contains the core DOT/Graphviz capabilities extracted
from the original monolithic dot-graph.yaml.
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
BEHAVIOR_PATH = REPO_ROOT / "behaviors" / "dot-core.yaml"


@pytest.fixture(scope="module")
def data() -> dict:
    """Load behaviors/dot-core.yaml once per test module."""
    return yaml.safe_load(BEHAVIOR_PATH.read_text())


def _get_tool(data: dict, module_name: str) -> dict | None:
    """Return the tool entry with the given module name, or None if not found."""
    return next(
        (
            t
            for t in data["tools"]
            if isinstance(t, dict) and t.get("module") == module_name
        ),
        None,
    )


# --- File existence ---


def test_behavior_file_exists():
    """behaviors/dot-core.yaml must exist."""
    assert BEHAVIOR_PATH.exists(), (
        f"behaviors/dot-core.yaml not found at {BEHAVIOR_PATH}"
    )


def test_behavior_file_is_valid_yaml():
    """behaviors/dot-core.yaml must be valid YAML."""
    content = BEHAVIOR_PATH.read_text()
    parsed = yaml.safe_load(content)
    assert isinstance(parsed, dict), "behaviors/dot-core.yaml must parse to a dict"


# --- Top-level keys ---


def test_behavior_has_bundle_key(data):
    """behaviors/dot-core.yaml must have a top-level 'bundle' key."""
    assert "bundle" in data, "behaviors/dot-core.yaml must have 'bundle' key"


def test_behavior_has_tools_key(data):
    """behaviors/dot-core.yaml must have a top-level 'tools' key."""
    assert "tools" in data, "behaviors/dot-core.yaml must have 'tools' key"


def test_behavior_has_agents_key(data):
    """behaviors/dot-core.yaml must have a top-level 'agents' key."""
    assert "agents" in data, "behaviors/dot-core.yaml must have 'agents' key"


# --- bundle section ---


def test_behavior_bundle_name(data):
    """bundle.name must be 'dot-graph-core'."""
    assert data["bundle"]["name"] == "dot-graph-core", (
        f"bundle.name must be 'dot-graph-core', got: {data['bundle'].get('name')}"
    )


def test_behavior_bundle_version(data):
    """bundle.version must be '0.3.0'."""
    assert data["bundle"]["version"] == "0.3.0", (
        f"bundle.version must be '0.3.0', got: {data['bundle'].get('version')}"
    )


def test_behavior_bundle_description(data):
    """bundle.description must be present and non-empty."""
    assert "description" in data["bundle"], "bundle must have 'description' key"
    assert data["bundle"]["description"], "bundle.description must not be empty"


# --- tools section ---


def test_behavior_tools_is_list(data):
    """tools must be a list."""
    assert isinstance(data["tools"], list), "tools must be a list"


def test_behavior_tools_has_tool_dot_graph(data):
    """tools must contain a module entry with module 'tool-dot-graph'."""
    module_names = [t.get("module") for t in data["tools"] if isinstance(t, dict)]
    assert "tool-dot-graph" in module_names, (
        f"tools must contain module 'tool-dot-graph', found: {module_names}"
    )


def test_behavior_tools_dot_graph_has_source(data):
    """tool-dot-graph entry must have a source field."""
    tool = _get_tool(data, "tool-dot-graph")
    assert tool is not None, "Must have tool-dot-graph entry"
    assert "source" in tool, "tool-dot-graph must have a 'source' field"


def test_behavior_tools_dot_graph_source_value(data):
    """tool-dot-graph source must point to the correct git URL with subdirectory."""
    tool = _get_tool(data, "tool-dot-graph")
    assert tool is not None, "Must have tool-dot-graph entry"
    expected_source = "git+https://github.com/microsoft/amplifier-bundle-dot-graph@main#subdirectory=modules/tool-dot-graph"
    assert tool["source"] == expected_source, (
        f"tool-dot-graph source must be '{expected_source}', got: {tool.get('source')}"
    )


def test_behavior_tools_has_tool_skills(data):
    """tools must contain a module entry with module 'tool-skills'."""
    module_names = [t.get("module") for t in data["tools"] if isinstance(t, dict)]
    assert "tool-skills" in module_names, (
        f"tools must contain module 'tool-skills', found: {module_names}"
    )


def test_behavior_tools_skills_has_config(data):
    """tool-skills entry must have config.skills."""
    tool = _get_tool(data, "tool-skills")
    assert tool is not None, "Must have tool-skills entry"
    assert "config" in tool, "tool-skills must have a 'config' field"
    assert "skills" in tool["config"], "tool-skills config must have 'skills' field"


# --- agents section ---


def test_behavior_agents_has_include(data):
    """agents must have an 'include' key."""
    assert "include" in data["agents"], "agents must have an 'include' key"


def test_behavior_agents_include_is_list(data):
    """agents.include must be a list."""
    assert isinstance(data["agents"]["include"], list), "agents.include must be a list"


def test_behavior_agents_includes_dot_author(data):
    """agents.include must contain 'dot-graph:dot-author'."""
    assert "dot-graph:dot-author" in data["agents"]["include"], (
        f"agents.include must contain 'dot-graph:dot-author', got: {data['agents']['include']}"
    )


def test_behavior_agents_includes_diagram_reviewer(data):
    """agents.include must contain 'dot-graph:diagram-reviewer'."""
    assert "dot-graph:diagram-reviewer" in data["agents"]["include"], (
        f"agents.include must contain 'dot-graph:diagram-reviewer', got: {data['agents']['include']}"
    )


# --- context: dot-awareness.md reaches a model via @-mention ---
#
# behaviors/dot-core.yaml deliberately carries NO `context` key. The
# dot-awareness.md content was moved to an @-mention in its primary sink,
# agents/dot-author.md, so it is not injected into always-on context for
# sessions that never touch DOT. See the NOTE at the bottom of
# behaviors/dot-core.yaml and BUNDLE_GUIDE.md
# §"Behavior context.include Policy".
#
# The tests below assert the invariant the old `context.include` tests were
# protecting -- that the awareness doc still reaches a model -- at its new
# location, and pin the token-reduction decision so always-on context
# cannot be reintroduced silently.

AWARENESS_DOC = REPO_ROOT / "context" / "dot-awareness.md"
AWARENESS_MENTION = "@dot-graph:context/dot-awareness.md"


def test_behavior_carries_no_always_on_context(data):
    """behaviors/dot-core.yaml must NOT declare a top-level 'context' key."""
    assert "context" not in data, (
        "behaviors/dot-core.yaml must not reintroduce always-on context; "
        "dot-awareness.md is @-mentioned from agents/dot-author.md instead"
    )


def test_dot_awareness_doc_exists():
    """context/dot-awareness.md must exist to be @-mentioned."""
    assert AWARENESS_DOC.exists(), f"dot-awareness.md not found at {AWARENESS_DOC}"


def test_dot_awareness_is_at_mentioned_by_an_agent():
    """At least one agent must @-mention dot-awareness.md."""
    agents_dir = REPO_ROOT / "agents"
    sinks = [
        path.name
        for path in sorted(agents_dir.glob("*.md"))
        if AWARENESS_MENTION in path.read_text(encoding="utf-8")
    ]
    assert sinks, (
        f"no agent in agents/ @-mentions {AWARENESS_MENTION}; the awareness "
        "doc is orphaned and reaches no model"
    )
