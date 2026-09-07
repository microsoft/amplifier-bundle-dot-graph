"""
Tests for behaviors/dot-discovery.yaml existence and required content.
This behavior provides the discovery pipeline capability.
dot-core is provided via the dot-graph.yaml umbrella and is not re-included here.
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
BEHAVIOR_PATH = REPO_ROOT / "behaviors" / "dot-discovery.yaml"


@pytest.fixture(scope="module")
def data() -> dict:
    """Load behaviors/dot-discovery.yaml once per test module."""
    return yaml.safe_load(BEHAVIOR_PATH.read_text())


# --- File existence ---


def test_behavior_file_exists():
    """behaviors/dot-discovery.yaml must exist."""
    assert BEHAVIOR_PATH.exists(), (
        f"behaviors/dot-discovery.yaml not found at {BEHAVIOR_PATH}"
    )


def test_behavior_file_is_valid_yaml():
    """behaviors/dot-discovery.yaml must be valid YAML."""
    content = BEHAVIOR_PATH.read_text()
    parsed = yaml.safe_load(content)
    assert isinstance(parsed, dict), "behaviors/dot-discovery.yaml must parse to a dict"


# --- bundle section ---


def test_behavior_has_bundle_key(data):
    """behaviors/dot-discovery.yaml must have a top-level 'bundle' key."""
    assert "bundle" in data, "behaviors/dot-discovery.yaml must have 'bundle' key"


def test_behavior_bundle_name(data):
    """bundle.name must be 'dot-graph-discovery'."""
    assert data["bundle"]["name"] == "dot-graph-discovery", (
        f"bundle.name must be 'dot-graph-discovery', got: {data['bundle'].get('name')}"
    )


def test_behavior_bundle_version(data):
    """bundle.version must be '0.2.0'."""
    assert data["bundle"]["version"] == "0.2.0", (
        f"bundle.version must be '0.2.0', got: {data['bundle'].get('version')}"
    )


def test_behavior_bundle_description(data):
    """bundle.description must be present and non-empty."""
    assert "description" in data["bundle"], "bundle must have 'description' key"
    assert data["bundle"]["description"], "bundle.description must not be empty"


# --- includes section ---


def test_behavior_does_not_have_includes_key(data):
    """behaviors/dot-discovery.yaml must NOT have an 'includes' key.

    dot-core is included by the dot-graph.yaml umbrella behavior which includes
    both dot-core and dot-discovery. Re-including dot-core here would cause
    double-injection of its context.
    """
    assert "includes" not in data, (
        "behaviors/dot-discovery.yaml must NOT have 'includes' key "
        "(dot-core is already included by dot-graph.yaml umbrella — do not re-include here)"
    )


def test_behavior_does_not_include_dot_core_directly(data):
    """dot-graph:behaviors/dot-core must NOT be in an includes block.

    dot-core is already provided via the dot-graph.yaml umbrella behavior.
    Direct re-inclusion here would cause double-injection.
    """
    includes = data.get("includes")
    if includes is None:
        # Pass-through guard — the primary check is test_behavior_does_not_have_includes_key
        return
    bundle_refs = [item.get("bundle") for item in includes if isinstance(item, dict)]
    assert "dot-graph:behaviors/dot-core" not in bundle_refs, (
        "dot-graph:behaviors/dot-core must NOT be directly included in dot-discovery.yaml "
        "(already provided by dot-graph.yaml umbrella)"
    )


# --- context: discovery-awareness.md reaches a model via @-mention ---
#
# behaviors/dot-discovery.yaml deliberately carries NO `context` key. The
# discovery-awareness.md content was moved to an @-mention in the
# discovery agents' shared sink so it is not injected into always-on
# context for sessions that never run discovery. See the NOTE at the
# bottom of behaviors/dot-discovery.yaml and BUNDLE_GUIDE.md
# §"Behavior context.include Policy".

DISCOVERY_AWARENESS_DOC = REPO_ROOT / "context" / "discovery-awareness.md"
DISCOVERY_AWARENESS_MENTION = "@dot-graph:context/discovery-awareness.md"


def test_behavior_carries_no_always_on_context(data):
    """behaviors/dot-discovery.yaml must NOT declare a top-level 'context' key."""
    assert "context" not in data, (
        "behaviors/dot-discovery.yaml must not reintroduce always-on context; "
        "discovery-awareness.md is @-mentioned from an agent instead"
    )


def test_discovery_awareness_doc_exists():
    """context/discovery-awareness.md must exist to be @-mentioned."""
    assert DISCOVERY_AWARENESS_DOC.exists(), (
        f"discovery-awareness.md not found at {DISCOVERY_AWARENESS_DOC}"
    )


def test_discovery_awareness_is_at_mentioned_by_an_agent():
    """At least one agent must @-mention discovery-awareness.md."""
    agents_dir = REPO_ROOT / "agents"
    sinks = [
        path.name
        for path in sorted(agents_dir.glob("*.md"))
        if DISCOVERY_AWARENESS_MENTION in path.read_text(encoding="utf-8")
    ]
    assert sinks, (
        f"no agent in agents/ @-mentions {DISCOVERY_AWARENESS_MENTION}; the "
        "awareness doc is orphaned and reaches no model"
    )


# --- agents section ---


def test_behavior_has_agents_key(data):
    """behaviors/dot-discovery.yaml must have a top-level 'agents' key."""
    assert "agents" in data, "behaviors/dot-discovery.yaml must have 'agents' key"


def test_behavior_agents_has_include(data):
    """agents must have an 'include' key."""
    assert "include" in data["agents"], "agents must have an 'include' key"


def test_behavior_agents_includes_all_discovery_agents(data):
    """agents.include must contain the original 5 discovery agent references."""
    expected_agents = [
        "dot-graph:discovery-prescan",
        "dot-graph:discovery-code-tracer",
        "dot-graph:discovery-behavior-observer",
        "dot-graph:discovery-integration-mapper",
        "dot-graph:discovery-synthesizer",
    ]
    actual = data["agents"]["include"]
    for agent in expected_agents:
        assert agent in actual, f"agents.include must contain '{agent}', got: {actual}"


def test_behavior_agents_includes_level_synthesizer(data):
    """agents.include must contain 'dot-graph:discovery-level-synthesizer'."""
    actual = data["agents"]["include"]
    assert "dot-graph:discovery-level-synthesizer" in actual, (
        f"agents.include must contain 'dot-graph:discovery-level-synthesizer', got: {actual}"
    )


def test_behavior_agents_includes_subsystem_synthesizer(data):
    """agents.include must contain 'dot-graph:discovery-subsystem-synthesizer'."""
    actual = data["agents"]["include"]
    assert "dot-graph:discovery-subsystem-synthesizer" in actual, (
        f"agents.include must contain 'dot-graph:discovery-subsystem-synthesizer', got: {actual}"
    )


def test_behavior_agents_includes_overview_synthesizer(data):
    """agents.include must contain 'dot-graph:discovery-overview-synthesizer'."""
    actual = data["agents"]["include"]
    assert "dot-graph:discovery-overview-synthesizer" in actual, (
        f"agents.include must contain 'dot-graph:discovery-overview-synthesizer', got: {actual}"
    )


def test_behavior_agents_includes_combiner(data):
    """agents.include must contain 'dot-graph:discovery-combiner'."""
    actual = data["agents"]["include"]
    assert "dot-graph:discovery-combiner" in actual, (
        f"agents.include must contain 'dot-graph:discovery-combiner', got: {actual}"
    )


def test_behavior_agents_includes_architecture_writer(data):
    """agents.include must contain 'dot-graph:discovery-architecture-writer'."""
    actual = data["agents"]["include"]
    assert "dot-graph:discovery-architecture-writer" in actual, (
        f"agents.include must contain 'dot-graph:discovery-architecture-writer', got: {actual}"
    )


def test_behavior_agents_total_count(data):
    """agents.include must contain exactly 11 agent references (10 original + discovery-orchestrator)."""
    actual = data["agents"]["include"]
    assert len(actual) == 11, (
        f"agents.include must have exactly 11 agents, got {len(actual)}: {actual}"
    )
