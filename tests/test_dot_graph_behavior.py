"""
Tests for behaviors/dot-graph.yaml existence and required content.
After Phase A restructuring, this behavior is a thin composition that
includes dot-core + dot-discovery sub-behaviors. It does not declare
tools, agents, or context directly — those live in the sub-behaviors.
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
BEHAVIOR_PATH = REPO_ROOT / "behaviors" / "dot-graph.yaml"


@pytest.fixture(scope="module")
def data() -> dict:
    """Load behaviors/dot-graph.yaml once per test module."""
    return yaml.safe_load(BEHAVIOR_PATH.read_text())


# --- File existence ---


def test_behavior_file_exists():
    """behaviors/dot-graph.yaml must exist."""
    assert BEHAVIOR_PATH.exists(), (
        f"behaviors/dot-graph.yaml not found at {BEHAVIOR_PATH}"
    )


def test_behavior_file_is_valid_yaml():
    """behaviors/dot-graph.yaml must be valid YAML."""
    content = BEHAVIOR_PATH.read_text()
    parsed = yaml.safe_load(content)
    assert isinstance(parsed, dict), "behaviors/dot-graph.yaml must parse to a dict"


# --- bundle section ---


def test_behavior_has_bundle_key(data):
    """behaviors/dot-graph.yaml must have a top-level 'bundle' key."""
    assert "bundle" in data, "behaviors/dot-graph.yaml must have 'bundle' key"


def test_behavior_bundle_name(data):
    """bundle.name must be 'dot-graph-behavior'."""
    assert data["bundle"]["name"] == "dot-graph-behavior", (
        f"bundle.name must be 'dot-graph-behavior', got: {data['bundle'].get('name')}"
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


# --- includes section (composition) ---


def test_behavior_has_includes_key(data):
    """behaviors/dot-graph.yaml must have an 'includes' key."""
    assert "includes" in data, "behaviors/dot-graph.yaml must have 'includes' key"


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


def test_behavior_includes_dot_discovery(data):
    """includes must reference 'dot-graph:behaviors/dot-discovery'."""
    bundle_refs = [
        item.get("bundle") for item in data["includes"] if isinstance(item, dict)
    ]
    assert "dot-graph:behaviors/dot-discovery" in bundle_refs, (
        f"includes must contain 'dot-graph:behaviors/dot-discovery', got: {bundle_refs}"
    )


# --- composition purity ---


def test_behavior_has_no_tools_key(data):
    """Composition behavior should not declare tools directly — those live in dot-core."""
    assert "tools" not in data, (
        "dot-graph.yaml is a composition — tools belong in dot-core.yaml"
    )


def test_behavior_has_no_agents_key(data):
    """Composition behavior should not declare agents directly — those live in sub-behaviors."""
    assert "agents" not in data, (
        "dot-graph.yaml is a composition — agents belong in sub-behaviors"
    )


def test_behavior_has_no_context_key(data):
    """Composition behavior should not declare context directly — those live in sub-behaviors."""
    assert "context" not in data, (
        "dot-graph.yaml is a composition — context belongs in sub-behaviors"
    )
