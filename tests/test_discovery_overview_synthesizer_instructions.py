"""
Tests for context/discovery-overview-synthesizer-instructions.md existence and required content.
Covers the System-Level Pattern Finder Methodology for the overview synthesizer agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
OVERVIEW_SYNTHESIZER_INSTRUCTIONS_PATH = (
    REPO_ROOT / "context" / "discovery-overview-synthesizer-instructions.md"
)


def test_overview_synthesizer_instructions_exists():
    """context/discovery-overview-synthesizer-instructions.md must exist."""
    assert OVERVIEW_SYNTHESIZER_INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-overview-synthesizer-instructions.md not found at "
        f"{OVERVIEW_SYNTHESIZER_INSTRUCTIONS_PATH}"
    )


def test_overview_synthesizer_instructions_line_count():
    """File must be between 80 and 180 lines (spec: 80-180 lines)."""
    content = OVERVIEW_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 80 <= len(lines) <= 180, f"Expected 80-180 lines, got {len(lines)}"


def test_overview_synthesizer_instructions_has_heading():
    """File must contain a heading about overview synthesis or system-level."""
    content = OVERVIEW_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert any(
        keyword in content
        for keyword in [
            "Overview Synthesis",
            "overview synthesis",
            "Overview Synthesizer",
            "overview synthesizer",
            "System-Level",
            "system-level",
            "System Level",
            "system level",
            "Pattern Finder",
            "pattern finder",
        ]
    ), "Must contain a heading about overview synthesis or system-level"


def test_overview_synthesizer_instructions_every_node_is_subsystem():
    """File must state that every node represents an entire subsystem."""
    content = OVERVIEW_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "every node represents",
            "each node represents",
            "node represents a subsystem",
            "node represents an entire subsystem",
            "nodes represent subsystems",
            "nodes represent entire subsystems",
        ]
    ), "Must state that every node represents an entire subsystem"


def test_overview_synthesizer_instructions_mentions_quality_gate():
    """File must mention quality gate with 80 nodes or 250 lines."""
    content = OVERVIEW_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert "80" in content or "250" in content, (
        "Must mention quality gate — 80 nodes limit or 250 lines (diagram.dot)"
    )


def test_overview_synthesizer_instructions_references_dot_quality():
    """File must reference the dot-quality skill or standard."""
    content = OVERVIEW_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "dot-quality",
            "dot quality",
            "dot_quality",
        ]
    ), "Must reference the dot-quality skill or standard"


def test_overview_synthesizer_instructions_mentions_diagram_dot():
    """File must mention diagram.dot as a required artifact."""
    content = OVERVIEW_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert "diagram.dot" in content, "Must mention diagram.dot as a required artifact"


def test_overview_synthesizer_instructions_mentions_findings_md():
    """File must mention findings.md as a required artifact."""
    content = OVERVIEW_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert "findings.md" in content, "Must mention findings.md as a required artifact"
