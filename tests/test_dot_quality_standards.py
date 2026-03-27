"""
Tests for docs/DOT-QUALITY-STANDARDS.md existence and required content.
TDD: This test is written BEFORE the docs/DOT-QUALITY-STANDARDS.md file is created.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
DOC_PATH = REPO_ROOT / "docs" / "DOT-QUALITY-STANDARDS.md"


@pytest.fixture(scope="module")
def doc_content():
    """Read DOT-QUALITY-STANDARDS.md once per test module."""
    return DOC_PATH.read_text(encoding="utf-8")


# --- File existence and size ---


def test_file_exists():
    """docs/DOT-QUALITY-STANDARDS.md must exist."""
    assert DOC_PATH.exists(), f"docs/DOT-QUALITY-STANDARDS.md not found at {DOC_PATH}"


def test_line_count_in_range(doc_content):
    """File must be approximately 150-180 lines."""
    lines = doc_content.splitlines()
    assert 140 <= len(lines) <= 200, (
        f"Expected 140-200 lines (target 150-180), got {len(lines)}"
    )


# --- Line Count Targets table ---


def test_has_line_count_targets(doc_content):
    """Must contain a Line Count Targets table."""
    assert "Line Count" in doc_content, "Must contain Line Count Targets section"


def test_line_count_targets_has_overview(doc_content):
    """Line Count Targets must include overview row with 100-200/250 ranges."""
    assert "overview" in doc_content.lower(), "Must include 'overview' diagram type"
    assert "100" in doc_content, "Must include 100 in line count targets"
    assert "250" in doc_content, "Must include 250 (warn threshold) for overview"


def test_line_count_targets_has_detail(doc_content):
    """Line Count Targets must include detail row with 150-300/400 ranges."""
    assert "detail" in doc_content.lower(), "Must include 'detail' diagram type"
    assert "400" in doc_content, "Must include 400 (warn threshold) for detail"


def test_line_count_targets_has_inline(doc_content):
    """Line Count Targets must include inline row with 10-40/60 ranges."""
    assert "inline" in doc_content.lower(), "Must include 'inline' diagram type"
    assert "60" in doc_content, "Must include 60 (warn threshold) for inline"


def test_line_count_targets_has_quick_sketch(doc_content):
    """Line Count Targets must include quick sketch row."""
    content_lower = doc_content.lower()
    assert "quick" in content_lower or "sketch" in content_lower, (
        "Must include 'quick sketch' diagram type"
    )


# --- Node Count Guidelines table ---


def test_has_node_count_guidelines(doc_content):
    """Must contain a Node Count Guidelines section."""
    assert "Node Count" in doc_content, "Must contain Node Count Guidelines section"


def test_node_count_1_10_fine(doc_content):
    """Node Count Guidelines: 1-10 range must be marked fine/OK."""
    assert "1-10" in doc_content or "1–10" in doc_content, (
        "Must include 1-10 node count range"
    )


def test_node_count_11_25_clusters(doc_content):
    """Node Count Guidelines: 11-25 range should reference clusters."""
    assert "11-25" in doc_content or "11–25" in doc_content, (
        "Must include 11-25 node count range"
    )
    assert "cluster" in doc_content.lower(), "11-25 range should recommend clusters"


def test_node_count_26_40_approaching_limit(doc_content):
    """Node Count Guidelines: 26-40 range must indicate approaching limit."""
    assert "26-40" in doc_content or "26–40" in doc_content, (
        "Must include 26-40 node count range"
    )


def test_node_count_41_plus_too_many(doc_content):
    """Node Count Guidelines: 41+ must indicate too many."""
    assert "41+" in doc_content or "41 +" in doc_content or ">40" in doc_content, (
        "Must include 41+ node count range"
    )


# --- Required Elements section ---


def test_has_required_elements(doc_content):
    """Must contain a Required Elements section."""
    assert "Required Element" in doc_content or "Required element" in doc_content, (
        "Must contain Required Elements section"
    )


def test_always_required_has_graph_label(doc_content):
    """Always Required must include graph label."""
    assert "label" in doc_content.lower(), "Must include 'label' in required elements"


def test_always_required_has_fontname(doc_content):
    """Always Required must include fontname."""
    assert "fontname" in doc_content, "Must include 'fontname' in required elements"


def test_always_required_has_rankdir(doc_content):
    """Always Required must include rankdir."""
    assert "rankdir" in doc_content, "Must include 'rankdir' in required elements"


def test_required_for_large_graphs_has_legend(doc_content):
    """Required for >20 Nodes must include legend."""
    assert "legend" in doc_content.lower(), (
        "Must include 'legend' in large graph requirements"
    )


# --- Shape Vocabulary table ---


def test_has_shape_vocabulary(doc_content):
    """Must contain a Shape Vocabulary section."""
    assert "Shape" in doc_content and (
        "Vocabulary" in doc_content or "vocabulary" in doc_content
    ), "Must contain Shape Vocabulary section"


def test_shape_vocabulary_has_12_shapes(doc_content):
    """Shape Vocabulary must contain all 12 specified shapes."""
    required_shapes = [
        "box",
        "ellipse",
        "diamond",
        "cylinder",
        "hexagon",
        "component",
        "tripleoctagon",
        "parallelogram",
        "house",
        "folder",
        "note",
        "point",
    ]
    for shape in required_shapes:
        assert shape in doc_content, f"Shape vocabulary must include '{shape}'"


def test_shape_vocabulary_has_fill_color(doc_content):
    """Shape Vocabulary table must have a fill color column."""
    assert "fill" in doc_content.lower(), (
        "Shape vocabulary must include fill color information"
    )


# --- Color Semantics table ---


def test_has_color_semantics(doc_content):
    """Must contain a Color Semantics section."""
    assert "Color Semantic" in doc_content or "color semantic" in doc_content.lower(), (
        "Must contain Color Semantics section"
    )


def test_color_semantics_has_7_colors(doc_content):
    """Color Semantics must contain the 7 required colors."""
    # Per spec: default blue, green success, red error, yellow warning,
    # orange data, purple external, gray inactive
    required_colors = ["blue", "green", "red", "yellow", "orange", "purple", "gray"]
    for color in required_colors:
        assert color in doc_content.lower(), f"Color semantics must include '{color}'"


def test_color_semantics_has_meanings(doc_content):
    """Color Semantics must map colors to meanings."""
    semantic_terms = ["success", "error", "warning", "external", "inactive"]
    for term in semantic_terms:
        assert term in doc_content.lower(), (
            f"Color semantics must include meaning '{term}'"
        )


# --- Edge Style Semantics table ---


def test_has_edge_style_semantics(doc_content):
    """Must contain an Edge Style Semantics section."""
    assert "Edge Style" in doc_content or "edge style" in doc_content.lower(), (
        "Must contain Edge Style Semantics section"
    )


def test_edge_style_has_5_styles(doc_content):
    """Edge Style Semantics must contain the 5 required styles."""
    # Per spec: solid sync, dashed async, dotted weak, bold critical, red error
    required_styles = ["solid", "dashed", "dotted", "bold", "color=red"]
    for style in required_styles:
        assert style in doc_content.lower(), (
            f"Edge style semantics must include '{style}'"
        )


def test_edge_style_has_sync_async(doc_content):
    """Edge Style Semantics must include sync/async semantics."""
    assert "sync" in doc_content.lower() or "synchronous" in doc_content.lower(), (
        "Edge styles must include sync semantics"
    )
    assert "async" in doc_content.lower() or "asynchronous" in doc_content.lower(), (
        "Edge styles must include async semantics"
    )


# --- Anti-Patterns section ---


def test_has_anti_patterns_section(doc_content):
    """Must contain an Anti-Patterns section."""
    assert "Anti-Pattern" in doc_content or "anti-pattern" in doc_content.lower(), (
        "Must contain Anti-Patterns section"
    )


def test_anti_patterns_has_structural_table(doc_content):
    """Anti-Patterns must include a Structural subsection."""
    assert "Structural" in doc_content or "structural" in doc_content, (
        "Must contain Structural anti-patterns"
    )


def test_structural_anti_patterns_has_6(doc_content):
    """Structural anti-patterns table must have at least 6 entries."""
    # Check for all 6 known structural anti-pattern concepts
    # Note: "constraint" comes from "Add constraint=false" in the structural table
    # (avoids "rank" which would falsely match "rankdir" in Required Elements)
    structural_terms = ["cluster", "node", "edge", "constraint", "orphan", "cycle"]
    found = sum(1 for term in structural_terms if term in doc_content.lower())
    assert found >= 6, (
        f"Expected references to all 6 structural anti-pattern concepts, found {found}/6"
    )


def test_anti_patterns_has_style_table(doc_content):
    """Anti-Patterns must include a Style subsection header."""
    assert "### Style" in doc_content, (
        "Must contain '### Style' subsection header in Anti-Patterns"
    )


def test_anti_patterns_has_naming_table(doc_content):
    """Anti-Patterns must include a Naming subsection."""
    assert "Naming" in doc_content or "naming" in doc_content, (
        "Must contain Naming anti-patterns"
    )


def test_anti_patterns_has_severity(doc_content):
    """Anti-patterns tables must have severity column."""
    assert "severity" in doc_content.lower() or "Severity" in doc_content, (
        "Anti-patterns must include severity ratings"
    )


def test_anti_patterns_has_fix(doc_content):
    """Anti-patterns tables must have a fix/remedy column."""
    assert "fix" in doc_content.lower() or "Fix" in doc_content, (
        "Anti-patterns must include fix guidance"
    )


# --- Quality Gate Thresholds table ---


def test_has_quality_gate_thresholds(doc_content):
    """Must contain a Quality Gate Thresholds section."""
    assert "Quality Gate" in doc_content or "quality gate" in doc_content.lower(), (
        "Must contain Quality Gate Thresholds section"
    )


def test_quality_gates_has_8_checks(doc_content):
    """Quality Gate Thresholds table must define 8 checks with PASS/WARN/FAIL criteria."""
    # Verify the three column headers are present
    assert "PASS" in doc_content, "Quality gates must include PASS criteria"
    assert "WARN" in doc_content, "Quality gates must include WARN criteria"
    assert "FAIL" in doc_content, "Quality gates must include FAIL criteria"
    # Verify all 8 check rows are present by their identifying keywords
    required_checks = [
        "Line count",
        "Node count",
        "Required attributes",
        "Orphan node",
        "Cluster usage",
        "Legend present",
        "Color palette",
        "Naming convention",
    ]
    for check in required_checks:
        assert check.lower() in doc_content.lower(), (
            f"Quality gate thresholds must include '{check}' check"
        )


# --- The Reconciliation Principle section ---


def test_has_reconciliation_principle(doc_content):
    """Must contain The Reconciliation Principle section."""
    assert "Reconciliation" in doc_content or "reconciliation" in doc_content, (
        "Must contain The Reconciliation Principle section"
    )


def test_reconciliation_principle_explains_purpose(doc_content):
    """Reconciliation Principle must explain DOT diagrams as reconciliation artifacts."""
    content_lower = doc_content.lower()
    assert "artifact" in content_lower or "reconcil" in content_lower, (
        "Reconciliation Principle must describe diagrams as reconciliation artifacts"
    )


# --- Authoring Rules section ---


def test_quality_standards_requires_legend_for_multiple_edge_styles(doc_content):
    """Authoring Rules must require a legend when multiple edge styles are used."""
    content_lower = doc_content.lower()
    assert (
        "more than one edge style" in content_lower
        or "multiple edge styles" in content_lower
        or "multi-style" in content_lower
    ), (
        "Authoring Rules must mention multi-style edge diagram legend requirement "
        "(e.g. 'more than one edge style', 'multiple edge styles', or 'multi-style')"
    )


def test_quality_standards_legend_must_document_each_edge_style(doc_content):
    """Authoring Rules must state the legend must include a row for each edge style used."""
    content_lower = doc_content.lower()
    assert "legend" in content_lower, "Authoring Rules must mention 'legend'"
    assert "each" in content_lower or "row" in content_lower, (
        "Authoring Rules must state legend must document 'each' style or include a 'row' per style"
    )


def test_quality_standards_requires_shape_vocabulary_comment(doc_content):
    """Authoring Rules must require a shape vocabulary comment block in diagrams."""
    content_lower = doc_content.lower()
    assert (
        "shape vocabulary" in content_lower
        or "vocabulary comment" in content_lower
        or "comment block" in content_lower
        or "define your shape" in content_lower
        or "shape vocab" in content_lower
    ), (
        "Authoring Rules must describe the shape vocabulary comment block requirement "
        "(e.g. 'shape vocabulary', 'vocabulary comment', 'comment block', "
        "'define your shape', or 'shape vocab')"
    )


def test_quality_standards_prohibits_shape_reuse_across_roles(doc_content):
    """Authoring Rules must prohibit reusing a shape for a different semantic role."""
    content_lower = doc_content.lower()
    assert (
        "do not reuse" in content_lower
        or "not reuse a shape" in content_lower
        or "reuse a shape" in content_lower
        or "same shape for a different" in content_lower
        or "different semantic role" in content_lower
    ), (
        "Authoring Rules must prohibit shape reuse across different semantic roles "
        "(e.g. 'do not reuse', 'not reuse a shape', 'reuse a shape', "
        "'same shape for a different', or 'different semantic role')"
    )
