"""
Tests for context/discovery-subsystem-synthesizer-instructions.md existence and required content.
Covers the Seam-Finder Methodology for the subsystem synthesizer agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SUBSYSTEM_SYNTHESIZER_INSTRUCTIONS_PATH = (
    REPO_ROOT / "context" / "discovery-subsystem-synthesizer-instructions.md"
)


def test_subsystem_synthesizer_instructions_exists():
    """context/discovery-subsystem-synthesizer-instructions.md must exist."""
    assert SUBSYSTEM_SYNTHESIZER_INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-subsystem-synthesizer-instructions.md not found at "
        f"{SUBSYSTEM_SYNTHESIZER_INSTRUCTIONS_PATH}"
    )


def test_subsystem_synthesizer_instructions_line_count():
    """File must be between 80 and 180 lines (spec: 80-180 lines)."""
    content = SUBSYSTEM_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 80 <= len(lines) <= 180, f"Expected 80-180 lines, got {len(lines)}"


def test_subsystem_synthesizer_instructions_has_heading():
    """File must contain a heading about subsystem synthesis or seam finding."""
    content = SUBSYSTEM_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert any(
        keyword in content
        for keyword in [
            "Subsystem Synthesis",
            "subsystem synthesis",
            "Subsystem Synthesizer",
            "subsystem synthesizer",
            "Seam-Finder",
            "seam-finder",
            "Seam Finder",
            "seam finder",
        ]
    ), "Must contain a heading about subsystem synthesis or seam finding"


def test_subsystem_synthesizer_instructions_investigates_between_modules():
    """File must mention investigating spaces between modules, not internals."""
    content = SUBSYSTEM_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "between modules",
            "spaces between",
            "between components",
            "not internals",
            "not module internals",
        ]
    ), "Must mention investigating spaces between modules, not internals"


def test_subsystem_synthesizer_instructions_mentions_cross_module_connections():
    """File must mention cross-module connections or data flows."""
    content = SUBSYSTEM_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "cross-module",
            "cross module",
            "module boundary",
            "module boundaries",
            "flowing between",
            "data flow",
        ]
    ), "Must mention cross-module connections or data flows"


def test_subsystem_synthesizer_instructions_mentions_interface_boundary_hexagon():
    """File must mention interfaces, boundaries, or hexagon shape."""
    content = SUBSYSTEM_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in [
            "interface",
            "boundary",
            "hexagon",
        ]
    ), "Must mention interfaces, boundaries, or hexagon shape for interfaces"


def test_subsystem_synthesizer_instructions_mentions_diagram_dot():
    """File must mention diagram.dot as a required artifact."""
    content = SUBSYSTEM_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert "diagram.dot" in content, "Must mention diagram.dot as a required artifact"


def test_subsystem_synthesizer_instructions_mentions_findings_md():
    """File must mention findings.md as a required artifact."""
    content = SUBSYSTEM_SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert "findings.md" in content, "Must mention findings.md as a required artifact"
