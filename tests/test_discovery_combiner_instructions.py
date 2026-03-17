"""
Tests for context/discovery-combiner-instructions.md existence and required content.
Covers the Convergence and Divergence Analysis Methodology for the combiner agent.
"""

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
COMBINER_INSTRUCTIONS_PATH = (
    REPO_ROOT / "context" / "discovery-combiner-instructions.md"
)


@pytest.fixture(scope="module")
def content():
    """Read the combiner instructions file once for all tests in this module."""
    if not COMBINER_INSTRUCTIONS_PATH.exists():
        pytest.skip(
            "Instructions file not found — see test_combiner_instructions_exists"
        )
    return COMBINER_INSTRUCTIONS_PATH.read_text(encoding="utf-8")


def test_combiner_instructions_exists():
    """context/discovery-combiner-instructions.md must exist."""
    assert COMBINER_INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-combiner-instructions.md not found at "
        f"{COMBINER_INSTRUCTIONS_PATH}"
    )


def test_combiner_instructions_line_count(content):
    """File must be between 80 and 180 lines (spec: 80-180 lines)."""
    lines = content.splitlines()
    assert 80 <= len(lines) <= 180, f"Expected 80-180 lines, got {len(lines)}"


def test_combiner_instructions_has_heading(content):
    """File must contain a heading about combining, convergence, or divergence."""
    assert any(
        keyword in content
        for keyword in [
            "Combiner",
            "combiner",
            "Convergence",
            "convergence",
            "Divergence",
            "divergence",
            "Combining",
            "combining",
        ]
    ), "Must contain a heading about combining, convergence, or divergence"


def test_combiner_instructions_read_order_top_down_first(content):
    """File must prescribe reading top-down first before bottom-up."""
    # Must mention top-down and bottom-up, with top-down coming first
    assert "top-down" in content.lower() or "top down" in content.lower(), (
        "Must mention top-down reading"
    )
    assert "bottom-up" in content.lower() or "bottom up" in content.lower(), (
        "Must mention bottom-up reading"
    )
    # Top-down must appear before bottom-up in the reading protocol
    lower = content.lower()
    td_pos = lower.find("top-down")
    if td_pos == -1:
        td_pos = lower.find("top down")
    bu_pos = lower.find("bottom-up")
    if bu_pos == -1:
        bu_pos = lower.find("bottom up")
    assert td_pos < bu_pos, (
        "top-down must appear before bottom-up (read top-down first)"
    )


def test_combiner_instructions_four_categories(content):
    """File must mention at least 3 of the 4 finding categories."""
    lower = content.lower()
    categories_found = 0
    # Convergence — both found it
    if "convergence" in lower:
        categories_found += 1
    # Top-down only — aspirational
    if "top-down only" in lower or "top down only" in lower:
        categories_found += 1
    # Bottom-up only — hidden complexity
    if "bottom-up only" in lower or "bottom up only" in lower:
        categories_found += 1
    # Divergence — different characterizations
    if "divergence" in lower:
        categories_found += 1
    assert categories_found >= 3, (
        f"Must mention at least 3 of 4 categories (Convergence, Top-down only, "
        f"Bottom-up only, Divergence). Found {categories_found}."
    )


def test_combiner_instructions_color_scheme(content):
    """File must mention color scheme for the four categories."""
    # Must mention colors — either by hex codes or color names
    has_hex = any(
        color in content for color in ["#c8e6c9", "#fff9c4", "#bbdefb", "#ffcdd2"]
    )
    has_color_name = any(
        color in content.lower() for color in ["green", "amber", "blue", "red"]
    )
    assert has_hex or has_color_name, (
        "Must mention color scheme (hex codes or color names) for the four categories"
    )


def test_combiner_instructions_divergence_id_format(content):
    """File must mention D-01 divergence ID format."""
    assert any(fmt in content for fmt in ["D-01", "D-02", "D-NN", "D-0"]), (
        "Must mention D-01 divergence ID format"
    )


def test_combiner_instructions_anti_rationalization(content):
    """File must prohibit reconciling divergences (anti-rationalization rule)."""
    lower = content.lower()
    assert any(
        phrase in lower
        for phrase in [
            "do not reconcile",
            "don't reconcile",
            "not reconcile",
            "anti-rationalization",
            "anti rationalization",
            "do not pick",
            "track both",
        ]
    ), "Must prohibit reconciling divergences (anti-rationalization rule)"


def test_combiner_instructions_divergence_value(content):
    """File must state that divergences are the most valuable finding."""
    lower = content.lower()
    assert any(
        phrase in lower
        for phrase in [
            "most valuable",
            "most valuable finding",
            "divergences are the most valuable",
            "divergence is the most valuable",
        ]
    ), "Must state that divergences are the most valuable finding"


def test_combiner_instructions_mentions_diagram_dot(content):
    """File must mention diagram.dot as a required artifact."""
    assert "diagram.dot" in content, "Must mention diagram.dot as a required artifact"
