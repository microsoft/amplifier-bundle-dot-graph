"""
Tests for behaviors/dot-discovery.yaml existence and required content.
This behavior provides the discovery pipeline capability and includes
dot-core as a dependency.
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
    """bundle.version must be '0.1.0'."""
    assert data["bundle"]["version"] == "0.1.0", (
        f"bundle.version must be '0.1.0', got: {data['bundle'].get('version')}"
    )


def test_behavior_bundle_description(data):
    """bundle.description must be present and non-empty."""
    assert "description" in data["bundle"], "bundle must have 'description' key"
    assert data["bundle"]["description"], "bundle.description must not be empty"


# --- includes section ---


def test_behavior_has_includes_key(data):
    """behaviors/dot-discovery.yaml must include dot-core as a dependency."""
    assert "includes" in data, "behaviors/dot-discovery.yaml must have 'includes' key"


def test_behavior_includes_is_list(data):
    """includes must be a list."""
    assert isinstance(data["includes"], list), "includes must be a list"


def test_behavior_includes_dot_core(data):
    """includes must reference 'dot-graph:behaviors/dot-core'."""
    bundle_refs = [
        item.get("bundle") for item in data["includes"] if isinstance(item, dict)
    ]
    assert "dot-graph:behaviors/dot-core" in bundle_refs, (
        f"includes must contain 'dot-graph:behaviors/dot-core', got: {bundle_refs}"
    )


# --- context section ---


def test_behavior_has_context_key(data):
    """behaviors/dot-discovery.yaml must have a 'context' key."""
    assert "context" in data, "behaviors/dot-discovery.yaml must have 'context' key"


def test_behavior_context_has_include(data):
    """context must have an 'include' key."""
    assert "include" in data["context"], "context must have an 'include' key"


def test_behavior_context_includes_discovery_awareness(data):
    """context.include must contain 'dot-graph:context/discovery-awareness.md'."""
    assert "dot-graph:context/discovery-awareness.md" in data["context"]["include"], (
        f"context.include must contain 'dot-graph:context/discovery-awareness.md', "
        f"got: {data['context']['include']}"
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


def test_behavior_agents_total_count(data):
    """agents.include must contain exactly 9 agent references."""
    actual = data["agents"]["include"]
    assert len(actual) == 9, (
        f"agents.include must have exactly 9 agents, got {len(actual)}: {actual}"
    )
