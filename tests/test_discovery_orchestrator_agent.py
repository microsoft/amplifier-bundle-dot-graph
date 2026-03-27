"""
Tests for agents/discovery-orchestrator.md, behaviors/dot-discovery.yaml orchestrator inclusion,
and context/discovery-awareness.md orchestrator reference.
TDD: This test is written BEFORE the agents/discovery-orchestrator.md file is created.
"""

from pathlib import Path

import yaml

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
ORCHESTRATOR_AGENT_PATH = REPO_ROOT / "agents" / "discovery-orchestrator.md"
BEHAVIOR_PATH = REPO_ROOT / "behaviors" / "dot-discovery.yaml"
AWARENESS_PATH = REPO_ROOT / "context" / "discovery-awareness.md"


# --- File existence and frontmatter ---


def test_discovery_orchestrator_agent_exists():
    """agents/discovery-orchestrator.md must exist."""
    assert ORCHESTRATOR_AGENT_PATH.exists(), (
        f"agents/discovery-orchestrator.md not found at {ORCHESTRATOR_AGENT_PATH}"
    )


def test_discovery_orchestrator_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = ORCHESTRATOR_AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-orchestrator.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-orchestrator.md must have closing --- for frontmatter"
    )


def test_discovery_orchestrator_meta_name():
    """Frontmatter must contain meta.name = 'discovery-orchestrator'."""
    content = ORCHESTRATOR_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-orchestrator", (
        f"meta.name must be 'discovery-orchestrator', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_orchestrator_model_role_fast():
    """Frontmatter must have model_role: fast (pure routing logic, not analysis)."""
    content = ORCHESTRATOR_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "fast", (
        f"model_role must be 'fast', got: {frontmatter['model_role']}"
    )


def test_discovery_orchestrator_description_has_trigger_investigate():
    """Description must contain 'investigate this codebase' trigger phrase."""
    content = ORCHESTRATOR_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    description = frontmatter.get("meta", {}).get("description", "")
    assert "investigate this codebase" in description, (
        "Description must contain 'investigate this codebase' trigger phrase"
    )


def test_discovery_orchestrator_description_has_trigger_map_architecture():
    """Description must contain 'map the architecture' trigger phrase."""
    content = ORCHESTRATOR_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    description = frontmatter.get("meta", {}).get("description", "")
    assert "map the architecture" in description, (
        "Description must contain 'map the architecture' trigger phrase"
    )


def test_discovery_orchestrator_description_has_trigger_run_discovery():
    """Description must contain 'run discovery' trigger phrase."""
    content = ORCHESTRATOR_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    description = frontmatter.get("meta", {}).get("description", "")
    assert "run discovery" in description, (
        "Description must contain 'run discovery' trigger phrase"
    )


def test_discovery_orchestrator_body_references_quick_pipeline():
    """Body must reference 'quick/discovery-pipeline.yaml'."""
    content = ORCHESTRATOR_AGENT_PATH.read_text()
    assert "quick/discovery-pipeline.yaml" in content, (
        "Body must reference 'quick/discovery-pipeline.yaml'"
    )


def test_discovery_orchestrator_body_references_deep_pipeline():
    """Body must reference 'deep/discovery-pipeline.yaml'."""
    content = ORCHESTRATOR_AGENT_PATH.read_text()
    assert "deep/discovery-pipeline.yaml" in content, (
        "Body must reference 'deep/discovery-pipeline.yaml'"
    )


def test_discovery_orchestrator_does_not_investigate_codebase():
    """Body must explicitly state it does not investigate the codebase."""
    content = ORCHESTRATOR_AGENT_PATH.read_text()
    lower = content.lower()
    assert any(
        phrase in lower
        for phrase in [
            "does not investigate",
            "do not investigate",
            "not investigate the codebase",
            "does not investigate the codebase",
        ]
    ), "Body must explicitly state it does not investigate the codebase"


def test_discovery_orchestrator_references_recipes_tool():
    """Body must reference the 'recipes' tool for invocation."""
    content = ORCHESTRATOR_AGENT_PATH.read_text()
    # Check body (after frontmatter) for 'recipes' tool reference
    _, body = _parse_frontmatter(content)
    assert "recipes" in body, (
        "Body must reference the 'recipes' tool for invocation"
    )


def test_discovery_orchestrator_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = ORCHESTRATOR_AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
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
