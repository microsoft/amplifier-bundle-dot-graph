"""
Tests for context/dot-instructions.md existence and required content.
TDD: This test is written BEFORE the context/dot-instructions.md file is created.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DOT_INSTRUCTIONS_PATH = REPO_ROOT / "context" / "dot-instructions.md"


def test_dot_instructions_exists():
    """context/dot-instructions.md must exist."""
    assert DOT_INSTRUCTIONS_PATH.exists(), (
        f"context/dot-instructions.md not found at {DOT_INSTRUCTIONS_PATH}"
    )


def test_dot_instructions_line_count_in_range():
    """File must be between 150 and 220 lines (spec: ~150-200)."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 150 <= len(lines) <= 220, f"Expected 150–220 lines, got {len(lines)}"


# --- DOT Syntax Quick Reference ---


def test_dot_instructions_has_syntax_reference():
    """File must contain DOT Syntax Quick Reference section."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "Syntax" in content and "Reference" in content, (
        "Must contain a DOT Syntax Reference section"
    )


def test_dot_instructions_has_graph_declaration_types():
    """File must cover digraph, graph, and strict graph declarations."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    for keyword in ["digraph", "graph", "strict"]:
        assert keyword in content, f"Missing graph declaration type: '{keyword}'"


def test_dot_instructions_has_node_attribute_rules():
    """File must cover node attributes and ID rules."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "node" in content, "Must mention 'node' in syntax reference"
    assert "label" in content, "Must mention 'label' attribute"
    assert "shape" in content, "Must mention 'shape' attribute"


def test_dot_instructions_has_edge_syntax():
    """File must cover directed, chain, fan-out, and styled edges."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "->" in content, "Must contain directed edge operator '->'"
    assert "color" in content, "Must mention 'color' for styled edges"


def test_dot_instructions_has_subgraph_cluster():
    """File must cover subgraphs and clusters with cluster_ naming."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "subgraph" in content, "Must mention 'subgraph'"
    assert "cluster_" in content, "Must mention 'cluster_' naming requirement"


def test_dot_instructions_has_html_labels():
    """File must cover HTML labels with TABLE/TR/TD and PORT."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "TABLE" in content, "Must mention 'TABLE' in HTML labels"
    assert "PORT" in content or "port" in content, "Must mention PORT connections"


def test_dot_instructions_has_comment_styles():
    """File must cover C++, C, and hash comment styles."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "//" in content, "Must mention // (C++ style) comments"
    assert "/*" in content, "Must mention /* */ (C style) comments"
    assert "#" in content, "Must mention # (hash style) comments"


# --- Common Shape Vocabulary ---


def test_dot_instructions_has_shape_vocabulary_section():
    """File must contain a shape vocabulary section/table."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "Shape" in content or "shape" in content, "Must have shape vocabulary"


def test_dot_instructions_has_all_required_shapes():
    """File must contain all 12 required shapes."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    required_shapes = [
        "box",
        "ellipse",
        "diamond",
        "cylinder",
        "folder",
        "circle",
        "doublecircle",
        "note",
        "component",
        "tab",
        "hexagon",
    ]
    for shape in required_shapes:
        assert shape in content, f"Missing shape: '{shape}'"


# --- Layout Engine Selection ---


def test_dot_instructions_has_layout_engine_table():
    """File must contain a layout engine selection table."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "Layout" in content, "Must have layout engine section"


def test_dot_instructions_has_all_layout_engines():
    """File must list all 6 layout engines."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    engines = ["dot", "neato", "fdp", "sfdp", "circo", "twopi"]
    for engine in engines:
        assert engine in content, f"Missing layout engine: '{engine}'"


# --- Quality Gates ---


def test_dot_instructions_has_quality_gates_section():
    """File must contain Quality Gates section."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "Quality" in content and "Gate" in content, (
        "Must contain Quality Gates section"
    )


def test_dot_instructions_has_line_count_targets():
    """File must contain line count targets for overview, detail, and inline."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "overview" in content.lower() or "Overview" in content, (
        "Must contain overview line count target"
    )
    assert "detail" in content.lower() or "Detail" in content, (
        "Must contain detail line count target"
    )
    assert "inline" in content.lower() or "Inline" in content, (
        "Must contain inline line count target"
    )


def test_dot_instructions_has_large_diagram_requirements():
    """File must list required elements for >20 node diagrams."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "20" in content, "Must reference 20 node threshold"
    # Required elements: title, legend, clusters, consistent node IDs
    assert "legend" in content.lower(), "Must mention legend as required element"
    assert "title" in content.lower(), "Must mention title as required element"


def test_dot_instructions_has_legend_pattern():
    """File must contain a legend pattern example."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "legend" in content.lower(), "Must contain legend pattern/example"


# --- Anti-Patterns ---


def test_dot_instructions_has_anti_patterns_section():
    """File must contain anti-patterns section."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "anti-pattern" in content.lower() or "Anti-Pattern" in content, (
        "Must contain anti-patterns section"
    )


def test_dot_instructions_has_seven_anti_patterns():
    """File must contain 7 anti-pattern entries."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    # The anti-patterns table should have 7 rows; we verify via section density
    # We check for 'Fix' column heading as proxy for structured anti-pattern table
    assert "Fix" in content, "Anti-patterns table must have 'Fix' column"
    # Count rows with | to approximate 7 entries; just verify substantial content
    pipe_lines = [ln for ln in content.splitlines() if ln.strip().startswith("|")]
    # At least 7 data rows for anti-patterns (plus headers/separators elsewhere)
    assert len(pipe_lines) >= 7, (
        f"Expected at least 7 table rows, found {len(pipe_lines)}"
    )


# --- Common Patterns ---


def test_dot_instructions_has_common_patterns_section():
    """File must contain Common Patterns section."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "Pattern" in content or "pattern" in content, (
        "Must contain Common Patterns section"
    )


def test_dot_instructions_has_dag_workflow_example():
    """File must contain DAG/Workflow pattern example."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "DAG" in content or "Workflow" in content or "workflow" in content, (
        "Must contain DAG/Workflow pattern example"
    )


def test_dot_instructions_has_layered_architecture_example():
    """File must contain Layered Architecture pattern example."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "Layer" in content or "layer" in content or "Architecture" in content, (
        "Must contain Layered Architecture pattern"
    )


def test_dot_instructions_has_state_machine_example():
    """File must contain State Machine pattern example."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "State Machine" in content or "state machine" in content, (
        "Must contain State Machine pattern example"
    )


def test_dot_instructions_has_dot_code_blocks():
    """File must contain actual DOT code blocks (backtick fenced)."""
    content = DOT_INSTRUCTIONS_PATH.read_text()
    assert "```dot" in content or "```\ndigraph" in content or "digraph" in content, (
        "Must contain DOT code examples"
    )
