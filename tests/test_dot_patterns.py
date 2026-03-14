"""
Tests for docs/DOT-PATTERNS.md existence and required content.
TDD: This test is written BEFORE the docs/DOT-PATTERNS.md file is created.
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
DOT_PATTERNS_PATH = REPO_ROOT / "docs" / "DOT-PATTERNS.md"


@pytest.fixture(scope="module")
def doc_content():
    """Read DOT-PATTERNS.md once per test module."""
    return DOT_PATTERNS_PATH.read_text()


# --- File existence and size ---


def test_dot_patterns_exists():
    """docs/DOT-PATTERNS.md must exist."""
    assert DOT_PATTERNS_PATH.exists(), (
        f"docs/DOT-PATTERNS.md not found at {DOT_PATTERNS_PATH}"
    )


def test_dot_patterns_line_count_in_range(doc_content):
    """File must be approximately 250-300 lines."""
    lines = doc_content.splitlines()
    assert 220 <= len(lines) <= 350, (
        f"Expected 220-350 lines (target 250-300), got {len(lines)}"
    )


# --- Contains all 10 patterns ---


def test_has_ten_patterns(doc_content):
    """File must contain all 10 patterns (Pattern 1 through Pattern 10)."""
    for i in range(1, 11):
        assert (
            f"Pattern {i}" in doc_content
            or f"## {i}." in doc_content
            or f"## Pattern {i}" in doc_content
        ), f"Missing Pattern {i}"


# --- DOT code blocks ---


def test_has_ten_dot_code_blocks(doc_content):
    """File must contain at least 10 DOT code blocks (one per pattern)."""
    dot_blocks = re.findall(r"```dot", doc_content)
    assert len(dot_blocks) >= 10, (
        f"Expected at least 10 DOT code blocks, found {len(dot_blocks)}"
    )


def test_dot_code_blocks_have_digraph(doc_content):
    """DOT code blocks must contain digraph declarations."""
    assert "digraph" in doc_content, "Must contain digraph declarations"


# --- Pattern 1: Simple DAG/Workflow ---


def test_pattern_1_simple_dag(doc_content):
    """Pattern 1: Simple DAG must use rankdir=LR."""
    assert "rankdir=LR" in doc_content, "Pattern 1 must use rankdir=LR"


def test_pattern_1_uses_ellipse(doc_content):
    """Pattern 1: Simple DAG must use ellipse shape for start/done."""
    assert "ellipse" in doc_content, "Pattern 1 must use ellipse shape"


# --- Pattern 2: Conditional Branching ---


def test_pattern_2_has_diamond(doc_content):
    """Pattern 2: Conditional Branching must use diamond shape."""
    assert "shape=diamond" in doc_content, "Pattern 2 must have diamond decision node"


def test_pattern_2_has_yes_no_edges(doc_content):
    """Pattern 2: Conditional Branching must have yes/no edge labels."""
    assert "yes" in doc_content.lower() or "Yes" in doc_content, (
        "Pattern 2 must have yes path"
    )
    assert "no" in doc_content.lower() or "No" in doc_content, (
        "Pattern 2 must have no path"
    )


# --- Pattern 3: Fan-Out/Fan-In Parallel ---


def test_pattern_3_has_component(doc_content):
    """Pattern 3: Fan-Out/Fan-In must use component shape."""
    assert "component" in doc_content, "Pattern 3 must use component shape for fan-out"


def test_pattern_3_has_dispatch_and_collect(doc_content):
    """Pattern 3: Fan-Out/Fan-In must have dispatch and collect nodes."""
    assert "dispatch" in doc_content.lower() or "fan" in doc_content.lower(), (
        "Pattern 3 must have dispatch/fan-out node"
    )
    assert "collect" in doc_content.lower() or "fan_in" in doc_content.lower(), (
        "Pattern 3 must have collect/fan-in node"
    )


# --- Pattern 4: Layered Architecture ---


def test_pattern_4_has_clusters(doc_content):
    """Pattern 4: Layered Architecture must use cluster subgraphs."""
    assert "subgraph cluster_" in doc_content, "Pattern 4 must use cluster_ subgraphs"


def test_pattern_4_has_four_layers(doc_content):
    """Pattern 4: Layered Architecture must have 4 named layers."""
    layers = ["presentation", "api", "domain", "data"]
    for layer in layers:
        assert layer in doc_content.lower(), f"Pattern 4 must contain layer: {layer}"


def test_pattern_4_has_cylinder(doc_content):
    """Pattern 4: Layered Architecture must use cylinder for data stores."""
    assert "cylinder" in doc_content, (
        "Pattern 4 must use cylinder shape for data stores"
    )


# --- Pattern 5: State Machine ---


def test_pattern_5_has_doublecircle(doc_content):
    """Pattern 5: State Machine must use doublecircle for terminal state."""
    assert "doublecircle" in doc_content, (
        "Pattern 5 must use doublecircle for terminal state"
    )


def test_pattern_5_has_point_start(doc_content):
    """Pattern 5: State Machine must use point shape for start."""
    assert "shape=point" in doc_content, (
        "Pattern 5 must use shape=point for initial state"
    )


# --- Pattern 6: Dependency Graph ---


def test_pattern_6_has_rankdir_bt(doc_content):
    """Pattern 6: Dependency Graph must use rankdir=BT (bottom-to-top)."""
    assert "rankdir=BT" in doc_content, (
        "Pattern 6 must use rankdir=BT for bottom-to-top layout"
    )


# --- Pattern 7: Legend ---


def test_pattern_7_has_cluster_legend(doc_content):
    """Pattern 7: Legend must use cluster_legend subgraph."""
    assert "cluster_legend" in doc_content, "Pattern 7 must use cluster_legend subgraph"


def test_pattern_7_has_shape_examples(doc_content):
    """Pattern 7: Legend must show service/store/external/decision shapes."""
    assert "external" in doc_content.lower() or "decision" in doc_content.lower(), (
        "Pattern 7 must include external or decision shape examples"
    )


# --- Pattern 8: Retry Loop ---


def test_pattern_8_has_retry_loop(doc_content):
    """Pattern 8: Retry Loop must have retry logic."""
    assert "retry" in doc_content.lower() or "Retry" in doc_content, (
        "Pattern 8 must have retry logic"
    )


def test_pattern_8_has_dashed_edge(doc_content):
    """Pattern 8: Retry Loop must have dashed back-edge."""
    assert "dashed" in doc_content, "Pattern 8 must use dashed style for back-edge"


# --- Pattern 9: Data Flow ---


def test_pattern_9_has_data_stores(doc_content):
    """Pattern 9: Data Flow must have cylinder data stores."""
    assert "cylinder" in doc_content, "Pattern 9 must use cylinder for data stores"


def test_pattern_9_has_tab_shape(doc_content):
    """Pattern 9: Data Flow must use tab shape for reports."""
    assert "tab" in doc_content.lower(), "Pattern 9 must use tab shape for reports"


# --- Pattern 10: Progressive Disclosure ---


def test_pattern_10_has_progressive_disclosure(doc_content):
    """Pattern 10: Progressive Disclosure pattern."""
    assert "progressive" in doc_content.lower() or "Progressive" in doc_content, (
        "Pattern 10 must describe progressive disclosure"
    )


def test_pattern_10_has_note_shape(doc_content):
    """Pattern 10: Progressive Disclosure must use note shape."""
    assert "note" in doc_content, (
        "Pattern 10 must use note shape for collapsed cluster summaries"
    )


def test_pattern_10_has_file_naming(doc_content):
    """Pattern 10: Progressive Disclosure must include file naming convention."""
    assert "overview" in doc_content.lower() or "detail" in doc_content.lower(), (
        "Pattern 10 must include file naming convention (overview/detail)"
    )


# --- Use-when guidance ---


def test_has_use_when_guidance(doc_content):
    """Each pattern must include 'Use when' guidance."""
    use_when_count = doc_content.lower().count("use when")
    assert use_when_count >= 8, (
        f"Expected at least 8 'Use when' guidance sections, found {use_when_count}"
    )
