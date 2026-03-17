"""
Tests for context/discovery-level-synthesizer-instructions.md existence and required content.
Covers the Bottom-Up Level Synthesis Methodology for the level synthesizer agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LEVEL_SYNTHESIZER_INSTRUCTIONS_PATH = (
    REPO_ROOT / "context" / "discovery-level-synthesizer-instructions.md"
)


def test_level_synthesizer_instructions_exists():
    """context/discovery-level-synthesizer-instructions.md must exist."""
    assert LEVEL_SYNTHESIZER_INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-level-synthesizer-instructions.md not found at "
        f"{LEVEL_SYNTHESIZER_INSTRUCTIONS_PATH}"
    )


def test_level_synthesizer_instructions_line_count():
    """File must be between 80 and 180 lines (spec: 80-180 lines)."""
    content = LEVEL_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 80 <= len(lines) <= 180, f"Expected 80-180 lines, got {len(lines)}"


def test_level_synthesizer_instructions_has_heading():
    """File must contain a heading about level synthesis or bottom-up."""
    content = LEVEL_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert any(
        keyword in content
        for keyword in [
            "Level Synthesis",
            "level synthesis",
            "Bottom-Up",
            "bottom-up",
            "Bottom Up",
            "Level Synthesizer",
            "level synthesizer",
        ]
    ), "Must contain a heading about level synthesis or bottom-up"


def test_level_synthesizer_instructions_mentions_fresh_context():
    """File must mention fresh context or clean slate mandate."""
    content = LEVEL_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "fresh context",
            "clean slate",
            "zero prior",
            "no prior",
            "clean start",
        ]
    ), "Must mention fresh context or clean slate mandate"


def test_level_synthesizer_instructions_mentions_cross_child_connections():
    """File must mention cross-child connections."""
    content = LEVEL_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "cross-child",
            "cross child",
            "spanning multiple child",
            "multiple child",
        ]
    ), "Must mention cross-child connections"


def test_level_synthesizer_instructions_mentions_at_least_2_shapes():
    """File must mention at least 2 semantic shapes from the vocabulary."""
    content = LEVEL_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    shapes = ["note", "box", "cylinder", "component", "diamond", "hexagon"]
    found = [shape for shape in shapes if shape in content.lower()]
    assert len(found) >= 2, (
        f"Must mention at least 2 semantic shapes from vocabulary "
        f"(note, box, cylinder, component, diamond, hexagon), found: {found}"
    )


def test_level_synthesizer_instructions_mentions_diagram_dot():
    """File must mention diagram.dot as a required artifact."""
    content = LEVEL_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert "diagram.dot" in content, "Must mention diagram.dot as a required artifact"


def test_level_synthesizer_instructions_mentions_findings_md():
    """File must mention findings.md as a required artifact."""
    content = LEVEL_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert "findings.md" in content, "Must mention findings.md as a required artifact"
