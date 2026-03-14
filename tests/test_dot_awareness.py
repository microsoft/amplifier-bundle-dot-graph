"""
Tests for context/dot-awareness.md existence and required content.
TDD: This test is written BEFORE the context/dot-awareness.md file is created.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DOT_AWARENESS_PATH = REPO_ROOT / "context" / "dot-awareness.md"


def test_dot_awareness_exists():
    """context/dot-awareness.md must exist."""
    assert DOT_AWARENESS_PATH.exists(), (
        f"context/dot-awareness.md not found at {DOT_AWARENESS_PATH}"
    )


def test_dot_awareness_line_count_under_40():
    """File must be under 40 lines (spec: ~35 lines)."""
    content = DOT_AWARENESS_PATH.read_text()
    lines = content.splitlines()
    assert len(lines) < 40, f"Expected < 40 lines, got {len(lines)}"


def test_dot_awareness_has_heading():
    """File must start with heading '# DOT/Graphviz Infrastructure'."""
    content = DOT_AWARENESS_PATH.read_text()
    assert "# DOT/Graphviz Infrastructure" in content, (
        "Must contain heading '# DOT/Graphviz Infrastructure'"
    )


def test_dot_awareness_has_all_7_value_propositions():
    """File must contain all 7 value propositions in table format."""
    content = DOT_AWARENESS_PATH.read_text()
    propositions = [
        "Dense representation",
        "Reconciliation forcing function",
        "Multi-scale navigation",
        "Analysis substrate",
        "Multi-modal bridge",
        "Workflow visualization",
        "Investigation artifact",
    ]
    for prop in propositions:
        assert prop in content, f"Missing value proposition: '{prop}'"


def test_dot_awareness_has_shape_vocabulary():
    """File must contain Quick Shape Vocabulary table with all required shapes."""
    content = DOT_AWARENESS_PATH.read_text()
    shapes = ["box", "ellipse", "diamond", "cylinder", "folder", "circle", "note"]
    for shape in shapes:
        assert shape in content, f"Missing shape in vocabulary: '{shape}'"


def test_dot_awareness_has_agents():
    """File must list agents: dot-author, diagram-reviewer."""
    content = DOT_AWARENESS_PATH.read_text()
    assert "dot-author" in content, "Missing agent: dot-author"
    assert "diagram-reviewer" in content, "Missing agent: diagram-reviewer"


def test_dot_awareness_has_tools():
    """File must list tools: dot_validate, dot_render, dot_setup, dot_analyze."""
    content = DOT_AWARENESS_PATH.read_text()
    tools = ["dot_validate", "dot_render", "dot_setup", "dot_analyze"]
    for tool in tools:
        assert tool in content, f"Missing tool: '{tool}'"


def test_dot_awareness_has_skills():
    """File must list skills: dot-syntax, dot-patterns, dot-as-analysis, dot-quality, dot-graph-intelligence."""
    content = DOT_AWARENESS_PATH.read_text()
    skills = [
        "dot-syntax",
        "dot-patterns",
        "dot-as-analysis",
        "dot-quality",
        "dot-graph-intelligence",
    ]
    for skill in skills:
        assert skill in content, f"Missing skill: '{skill}'"


def test_dot_awareness_has_delegation_guidance():
    """File must contain delegation guidance."""
    content = DOT_AWARENESS_PATH.read_text()
    # Should mention delegation to the dot-author agent
    assert "dot-author" in content, "Must reference dot-author agent for delegation"
    # Should contain 'delegate' or 'delegation' or 'Delegate'
    assert any(word in content for word in ["delegate", "delegation", "Delegate"]), (
        "Must contain delegation guidance"
    )
