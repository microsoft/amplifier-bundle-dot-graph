"""
Tests for agents/discovery-orchestrator.md, behaviors/dot-discovery.yaml orchestrator inclusion,
and context/discovery-awareness.md orchestrator reference.
TDD: This test is written BEFORE the agents/discovery-orchestrator.md file is created.
"""

from pathlib import Path

import pytest
import yaml

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
ORCHESTRATOR_AGENT_PATH = REPO_ROOT / "agents" / "discovery-orchestrator.md"
BEHAVIOR_PATH = REPO_ROOT / "behaviors" / "dot-discovery.yaml"
AWARENESS_PATH = REPO_ROOT / "context" / "discovery-awareness.md"


@pytest.fixture(scope="module")
def agent_content() -> str:
    """Load agents/discovery-orchestrator.md once per test module."""
    return ORCHESTRATOR_AGENT_PATH.read_text()


@pytest.fixture(scope="module")
def agent_frontmatter(agent_content: str) -> dict:
    """Parse frontmatter dict from the agent file once per test module."""
    fm, _ = _parse_frontmatter(agent_content)
    return fm


@pytest.fixture(scope="module")
def agent_body(agent_content: str) -> str:
    """Parse body text from the agent file once per test module."""
    _, body = _parse_frontmatter(agent_content)
    return body


# --- File existence and frontmatter ---


def test_discovery_orchestrator_agent_exists():
    """agents/discovery-orchestrator.md must exist."""
    assert ORCHESTRATOR_AGENT_PATH.exists(), (
        f"agents/discovery-orchestrator.md not found at {ORCHESTRATOR_AGENT_PATH}"
    )


def test_discovery_orchestrator_has_yaml_frontmatter(agent_content):
    """File must start with YAML frontmatter delimited by ---."""
    assert agent_content.startswith("---"), (
        "agents/discovery-orchestrator.md must start with YAML frontmatter (---)"
    )
    assert agent_content.count("---") >= 2, (
        "agents/discovery-orchestrator.md must have closing --- for frontmatter"
    )


def test_discovery_orchestrator_meta_name(agent_frontmatter):
    """Frontmatter must contain meta.name = 'discovery-orchestrator'."""
    assert "meta" in agent_frontmatter, "Frontmatter must have 'meta' key"
    assert agent_frontmatter["meta"]["name"] == "discovery-orchestrator", (
        f"meta.name must be 'discovery-orchestrator', got: {agent_frontmatter['meta'].get('name')}"
    )


def test_discovery_orchestrator_model_role_fast(agent_frontmatter):
    """Frontmatter must have model_role: fast (pure routing logic, not analysis)."""
    assert "model_role" in agent_frontmatter, "Frontmatter must have 'model_role' key"
    assert agent_frontmatter["model_role"] == "fast", (
        f"model_role must be 'fast', got: {agent_frontmatter['model_role']}"
    )


def test_discovery_orchestrator_description_has_trigger_investigate(agent_frontmatter):
    """Description must contain 'investigate this codebase' trigger phrase."""
    description = agent_frontmatter.get("meta", {}).get("description", "")
    assert "investigate this codebase" in description, (
        "Description must contain 'investigate this codebase' trigger phrase"
    )


def test_discovery_orchestrator_description_has_trigger_map_architecture(
    agent_frontmatter,
):
    """Description must contain 'map the architecture' trigger phrase."""
    description = agent_frontmatter.get("meta", {}).get("description", "")
    assert "map the architecture" in description, (
        "Description must contain 'map the architecture' trigger phrase"
    )


def test_discovery_orchestrator_description_has_trigger_run_discovery(
    agent_frontmatter,
):
    """Description must contain 'run discovery' trigger phrase."""
    description = agent_frontmatter.get("meta", {}).get("description", "")
    assert "run discovery" in description, (
        "Description must contain 'run discovery' trigger phrase"
    )


def test_discovery_orchestrator_body_references_quick_pipeline(agent_content):
    """Body must reference 'quick/discovery-pipeline.yaml'."""
    assert "quick/discovery-pipeline.yaml" in agent_content, (
        "Body must reference 'quick/discovery-pipeline.yaml'"
    )


def test_discovery_orchestrator_body_references_deep_pipeline(agent_content):
    """Body must reference 'deep/discovery-pipeline.yaml'."""
    assert "deep/discovery-pipeline.yaml" in agent_content, (
        "Body must reference 'deep/discovery-pipeline.yaml'"
    )


def test_discovery_orchestrator_does_not_investigate_codebase(agent_content):
    """Body must explicitly state it does not investigate the codebase."""
    lower = agent_content.lower()
    assert any(
        phrase in lower
        for phrase in [
            "does not investigate",
            "do not investigate",
            "not investigate the codebase",
            "does not investigate the codebase",
        ]
    ), "Body must explicitly state it does not investigate the codebase"


def test_discovery_orchestrator_references_recipes_tool(agent_body):
    """Body must reference the 'recipes' tool for invocation."""
    assert "recipes" in agent_body, (
        "Body must reference the 'recipes' tool for invocation"
    )


def test_discovery_orchestrator_ends_with_common_agent_base(agent_content):
    """File must end with @foundation:context/shared/common-agent-base.md."""
    assert "@foundation:context/shared/common-agent-base.md" in agent_content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = agent_content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )


def test_dot_discovery_behavior_includes_orchestrator():
    """behaviors/dot-discovery.yaml must include 'dot-graph:discovery-orchestrator' in agents.include."""
    data = yaml.safe_load(BEHAVIOR_PATH.read_text())
    actual = data["agents"]["include"]
    assert "dot-graph:discovery-orchestrator" in actual, (
        f"agents.include must contain 'dot-graph:discovery-orchestrator', got: {actual}"
    )


def test_dot_discovery_orchestrator_is_first_agent():
    """dot-graph:discovery-orchestrator must be the FIRST entry in agents.include."""
    data = yaml.safe_load(BEHAVIOR_PATH.read_text())
    actual = data["agents"]["include"]
    assert actual[0] == "dot-graph:discovery-orchestrator", (
        f"First agent must be 'dot-graph:discovery-orchestrator', got: {actual[0]}"
    )


def test_discovery_awareness_references_orchestrator():
    """context/discovery-awareness.md must reference 'discovery-orchestrator'."""
    content = AWARENESS_PATH.read_text()
    assert "discovery-orchestrator" in content, (
        "context/discovery-awareness.md must reference 'discovery-orchestrator'"
    )
