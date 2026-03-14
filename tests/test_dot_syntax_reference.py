"""
Tests for docs/DOT-SYNTAX-REFERENCE.md existence and required content.
TDD: This test is written BEFORE the docs/DOT-SYNTAX-REFERENCE.md file is created.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DOT_SYNTAX_REF_PATH = REPO_ROOT / "docs" / "DOT-SYNTAX-REFERENCE.md"


# --- File existence and size ---


def test_dot_syntax_reference_exists():
    """docs/DOT-SYNTAX-REFERENCE.md must exist."""
    assert DOT_SYNTAX_REF_PATH.exists(), (
        f"docs/DOT-SYNTAX-REFERENCE.md not found at {DOT_SYNTAX_REF_PATH}"
    )


def test_dot_syntax_reference_line_count_in_range():
    """File must be approximately 350-400 lines (±15% tolerance)."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    lines = content.splitlines()
    assert 300 <= len(lines) <= 450, (
        f"Expected 300-450 lines (target 350-400), got {len(lines)}"
    )


# --- Grammar section ---


def test_has_grammar_section():
    """File must contain a Grammar section."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "Grammar" in content, "Must contain a Grammar section"


def test_has_bnf_abstract_grammar():
    """Grammar section must include BNF abstract grammar."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "stmt_list" in content, "Must include BNF grammar with stmt_list"
    assert "edgeRHS" in content, "Must include BNF grammar with edgeRHS"
    assert "compass_pt" in content, "Must include BNF grammar with compass_pt"


def test_has_graph_types_table():
    """Must have a Graph Types table covering digraph/graph/strict variants."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "digraph" in content, "Must mention digraph"
    assert "strict" in content, "Must mention strict graph variant"
    # Must have a table (pipe-delimited rows)
    pipe_lines = [ln for ln in content.splitlines() if ln.strip().startswith("|")]
    assert len(pipe_lines) >= 10, (
        f"Expected at least 10 table rows total, got {len(pipe_lines)}"
    )


def test_has_id_types_table():
    """Must have an ID Types table with alphanumeric/numeral/quoted/HTML types."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "alphanumeric" in content.lower() or "Alphabetic" in content, (
        "Must mention alphanumeric/alphabetic ID type"
    )
    assert "numeral" in content.lower() or "Numeral" in content, (
        "Must mention numeral ID type"
    )
    assert "quoted" in content.lower() or "Double-quoted" in content, (
        "Must mention quoted string ID type"
    )
    assert "HTML" in content, "Must mention HTML ID type"


def test_has_case_insensitive_keywords():
    """Must mention case-insensitive keywords."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert (
        "case-insensitive" in content.lower() or "case insensitive" in content.lower()
    ), "Must mention that keywords are case-insensitive"


# --- Nodes section ---


def test_has_nodes_section():
    """File must contain a Nodes section."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "Nodes" in content or "Node" in content, "Must contain a Nodes section"


def test_has_node_declaration_examples():
    """Nodes section must include implicit/explicit/multi-attribute declaration examples."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "implicit" in content.lower() or "Implicit" in content, (
        "Must show implicit node declaration"
    )
    assert "explicit" in content.lower() or "Explicit" in content, (
        "Must show explicit node declaration"
    )


def test_has_basic_shapes_table():
    """Must have a Basic Shapes table with at least 8 shapes."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    basic_shapes = [
        "box",
        "ellipse",
        "circle",
        "diamond",
        "rectangle",
        "point",
        "plaintext",
        "none",
    ]
    found = sum(1 for s in basic_shapes if s in content)
    assert found >= 6, f"Expected at least 6 of the 8 basic shapes, found {found}"


def test_has_extended_shapes_table():
    """Must have Extended Shapes table with shapes like cylinder, folder, note, etc."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    extended_shapes = [
        "cylinder",
        "folder",
        "note",
        "tab",
        "component",
        "hexagon",
        "doublecircle",
    ]
    found = sum(1 for s in extended_shapes if s in content)
    assert found >= 5, f"Expected at least 5 extended shapes, found {found}"


def test_has_special_shapes_including_record():
    """Must mention special shapes including deprecated record."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "record" in content, (
        "Must mention 'record' shape (including deprecated note)"
    )


def test_has_node_style_attributes():
    """Must have Node Style Attributes table with at least 16 attributes."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    node_attrs = [
        "label",
        "shape",
        "color",
        "fillcolor",
        "style",
        "fontname",
        "fontsize",
        "fontcolor",
        "width",
        "height",
        "fixedsize",
        "tooltip",
        "URL",
        "penwidth",
        "margin",
        "peripheries",
    ]
    found = sum(1 for a in node_attrs if a in content)
    assert found >= 12, (
        f"Expected at least 12 of 16 node style attributes, found {found}"
    )


# --- Edges section ---


def test_has_edges_section():
    """File must contain an Edges section."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "Edge" in content or "Edges" in content, "Must contain an Edges section"


def test_has_edge_declaration_examples():
    """Must show edge declaration examples: simple, attributed, chain, fan-out."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "->" in content, "Must show directed edge operator '->'"
    assert "--" in content, "Must show undirected edge operator '--'"


def test_has_edge_attributes_table():
    """Must have an Edge Attributes table with at least 14 attributes."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    edge_attrs = [
        "label",
        "color",
        "style",
        "weight",
        "arrowhead",
        "arrowtail",
        "dir",
        "headlabel",
        "taillabel",
        "constraint",
        "minlen",
        "penwidth",
        "ltail",
        "lhead",
    ]
    found = sum(1 for a in edge_attrs if a in content)
    assert found >= 10, f"Expected at least 10 of 14 edge attributes, found {found}"


# --- Graph Attributes section ---


def test_has_graph_attributes_section():
    """File must contain a Graph Attributes section."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "Graph Attribute" in content or "graph attribute" in content.lower(), (
        "Must contain Graph Attributes section"
    )


def test_has_common_graph_attributes():
    """Must have Common Graph Attributes table with at least 17 attributes."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    graph_attrs = [
        "rankdir",
        "ranksep",
        "nodesep",
        "bgcolor",
        "label",
        "fontname",
        "fontsize",
        "size",
        "ratio",
        "margin",
        "pad",
        "splines",
        "compound",
        "newrank",
        "concentrate",
        "overlap",
        "dpi",
    ]
    found = sum(1 for a in graph_attrs if a in content)
    assert found >= 12, f"Expected at least 12 of 17 graph attributes, found {found}"


def test_has_default_attribute_statements():
    """Must show Default Attribute Statements examples."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "node [" in content or "node[" in content, (
        "Must show default node attribute statement"
    )
    assert "edge [" in content or "edge[" in content, (
        "Must show default edge attribute statement"
    )


# --- Subgraphs and Clusters section ---


def test_has_subgraphs_section():
    """File must contain a Subgraphs section."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "Subgraph" in content or "subgraph" in content, (
        "Must contain Subgraphs section"
    )


def test_has_cluster_naming_requirement():
    """Must show cluster subgraph naming requirement (cluster_ prefix)."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "cluster_" in content, "Must show cluster_ naming convention"


def test_has_rank_control():
    """Must cover rank control with rank=same/min/max/source/sink."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "rank=same" in content or "rank=min" in content, (
        "Must show rank control subgraphs"
    )
    for rank_val in ["same", "min", "max", "source", "sink"]:
        assert rank_val in content, f"Must mention rank={rank_val}"


def test_has_compound_edges():
    """Must cover edges between clusters with compound=true."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "compound=true" in content or "compound" in content, (
        "Must mention compound edges between clusters"
    )


# --- HTML Labels section ---


def test_has_html_labels_section():
    """File must contain an HTML Labels section."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "HTML" in content and "Label" in content, "Must contain HTML Labels section"


def test_has_html_table_example():
    """Must contain a TABLE/TR/TD example with PORT connections."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "TABLE" in content, "Must show TABLE element"
    assert "<TR>" in content or "TR" in content, "Must show TR element"
    assert "<TD" in content or "TD" in content, "Must show TD element"
    assert "PORT" in content, "Must show PORT connections"


def test_has_html_elements_table():
    """Must have a Supported HTML Elements table with at least 9 elements."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    html_elements = ["TABLE", "TR", "TD", "FONT", "BR", "HR", "IMG", "<B>", "<I>"]
    found = sum(1 for e in html_elements if e in content)
    assert found >= 7, f"Expected at least 7 of 9 HTML elements, found {found}"


# --- Ports and Compass Points section ---


def test_has_ports_section():
    """File must contain a Ports and Compass Points section."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "Compass" in content or "compass" in content, (
        "Must contain Ports and Compass Points section"
    )


def test_has_compass_points():
    """Must show all 8 compass points."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    # All 8 compass points are abbreviated — verify key ones are mentioned
    assert "ne" in content and "sw" in content and "nw" in content, (
        "Must show compass points ne, sw, nw at minimum"
    )


# --- Layout Engines section ---


def test_has_layout_engines_section():
    """File must contain a Layout Engines section."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "Layout Engine" in content or "Layout engine" in content, (
        "Must contain Layout Engines section"
    )


def test_has_eight_engines_table():
    """Must have table of 8 layout engines with algorithm descriptions."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    engines = ["dot", "neato", "fdp", "sfdp", "twopi", "circo", "osage", "patchwork"]
    found = sum(1 for e in engines if e in content)
    assert found >= 7, f"Expected at least 7 of 8 layout engines, found {found}"


def test_has_engine_selection_heuristic():
    """Must include an engine selection heuristic/guide."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "DAG" in content or "hierarchy" in content.lower(), (
        "Must include engine selection guidance"
    )


# --- Output Formats section ---


def test_has_output_formats_section():
    """File must contain an Output Formats section."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "Output Format" in content or "output format" in content.lower(), (
        "Must contain Output Formats section"
    )


def test_has_five_primary_formats():
    """Must have table of 5 primary output formats."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    formats = ["SVG", "PNG", "PDF", "JSON", "DOT"]
    found = sum(1 for f in formats if f in content)
    assert found >= 4, f"Expected at least 4 of 5 output formats, found {found}"


def test_has_rendering_commands():
    """Must include rendering commands with validation and statistics."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "-T" in content, "Must show -T flag for output format selection"
    assert "dot -T" in content or "dot -" in content, "Must show dot rendering commands"


# --- Color Specification section ---


def test_has_color_specification_section():
    """File must contain a Color Specification section."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "Color" in content, "Must contain Color Specification section"


def test_has_color_formats():
    """Must cover name/hex/hex+alpha/HSV/color lists."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "#" in content, "Must show hex color format"
    assert "HSV" in content or "hsv" in content, "Must mention HSV color format"


# --- String Features section ---


def test_has_string_features_section():
    """File must contain a String Features section."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "String" in content, "Must contain String Features section"


def test_has_string_features():
    """Must cover newlines, concatenation, escapes, justification."""
    content = DOT_SYNTAX_REF_PATH.read_text()
    assert "\\n" in content or "newline" in content.lower(), (
        "Must mention newlines in string features"
    )
    assert "concatenat" in content.lower() or "+" in content, (
        "Must mention string concatenation"
    )
