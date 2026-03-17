"""Integration tests for the real DotGraphTool (Phase 4 complete).

24 tests covering:
- Operation routing: validate, render, setup, analyze (stats, cycles, error cases), unknown (8 tests)
- Input schema: setup operation in enum, options sub-properties, analyze options (3 tests)
- Mount contract: real tool version 0.4.0, tool can actually validate (3 tests)
- Error handling: invalid layer name returns structured error, not exception (1 test)
- Layer selection: syntax-only, structural-only layers (1 test)
- Render: mocked render operation (1 test)
- Prescan routing: prescan routes correctly, missing repo_path error (2 tests)
- Assemble routing: assemble routes correctly, missing manifest error (2 tests)
- Input schema: prescan/assemble in enum and options (2 tests)
- Mount contract: version 0.4.0 assertion (1 test)

These tests verify that __init__.py routes operations to the real
validate, render, setup_helper, analyze, prescan, and assemble modules.
"""

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

SIMPLE_DOT = "digraph G { a -> b }"
INVALID_DOT = "this is not dot content !!!###"


def _parse_output(result: Any) -> dict:
    """Assert result.output is a non-None string and parse it as JSON."""
    assert isinstance(result.output, str), (
        f"result.output must be a str, got {type(result.output)}: {result.output!r}"
    )
    return json.loads(result.output)


# ---------------------------------------------------------------------------
# Operation routing tests (8 tests)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validate_operation_routes_correctly():
    """validate operation calls validate.validate_dot and returns ToolResult with valid key."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({"operation": "validate", "dot_content": SIMPLE_DOT})

    assert result.success is True, "Valid DOT must return success=True"
    data = _parse_output(result)
    assert "valid" in data, "Output must contain 'valid' key from validate_dot()"
    assert data["valid"] is True, "Simple valid DOT must return valid=True"


@pytest.mark.asyncio
async def test_validate_invalid_dot_returns_failure():
    """validate operation returns success=False for invalid DOT content."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({"operation": "validate", "dot_content": INVALID_DOT})

    assert result.success is False, "Invalid DOT must return success=False"
    data = _parse_output(result)
    assert "valid" in data, "Output must contain 'valid' key"
    assert data["valid"] is False, "Invalid DOT must have valid=False"


@pytest.mark.asyncio
async def test_validate_invalid_layer_returns_structured_error():
    """Invalid layer name in options returns success=False with structured error, not raised ValueError.

    Regression test for: execute() must catch ValueError from validate_dot() and return
    a ToolResult(success=False, ...) instead of propagating the exception to the caller.
    """
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute(
        {
            "operation": "validate",
            "dot_content": "digraph G {}",
            "options": {"layers": ["bogus"]},
        }
    )

    assert result.success is False, (
        "Invalid layer name must return success=False (not raise ValueError)"
    )
    data = _parse_output(result)
    assert "valid" in data, "Structured error must include 'valid' key"
    assert data["valid"] is False, "Invalid layer must produce valid=False"
    assert "issues" in data, "Structured error must include 'issues' key"
    assert len(data["issues"]) > 0, (
        "Issues list must be non-empty for invalid layer name"
    )
    error_issue = data["issues"][0]
    assert "message" in error_issue, "Each issue must have a 'message' field"
    assert (
        "bogus" in error_issue["message"] or "layer" in error_issue["message"].lower()
    ), (
        f"Error message must mention the invalid layer or 'layer', got: {error_issue['message']!r}"
    )


@pytest.mark.asyncio
async def test_validate_with_layer_option():
    """validate operation passes layers option through to validate_dot."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute(
        {
            "operation": "validate",
            "dot_content": SIMPLE_DOT,
            "options": {"layers": ["syntax"]},
        }
    )

    assert result.success is True
    data = _parse_output(result)
    assert "issues" in data, "Output must contain 'issues' key"
    # Only syntax layer ran — no structural issues should appear
    structural_issues = [i for i in data["issues"] if i["layer"] == "structural"]
    assert len(structural_issues) == 0, (
        f"syntax-only validation must produce no structural issues, got: {structural_issues}"
    )


@pytest.mark.asyncio
async def test_setup_operation_returns_environment():
    """setup operation calls check_environment() and returns environment info."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({"operation": "setup"})

    assert result.success is True, "setup must return success=True"
    data = _parse_output(result)
    assert "graphviz" in data, "Environment result must include 'graphviz' key"
    assert "pydot" in data, "Environment result must include 'pydot' key"


@pytest.mark.asyncio
async def test_analyze_stats_routes_correctly():
    """analyze operation with analysis=stats routes to analyze_dot and returns node_count=2."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute(
        {
            "operation": "analyze",
            "dot_content": SIMPLE_DOT,
            "options": {"analysis": "stats"},
        }
    )

    assert result.success is True, (
        f"analyze stats must return success=True for valid DOT, got: {result.output!r}"
    )
    data = _parse_output(result)
    assert "node_count" in data, "stats result must include 'node_count'"
    assert data["node_count"] == 2, (
        f"SIMPLE_DOT 'digraph G {{a -> b}}' has 2 nodes, got node_count={data['node_count']}"
    )


@pytest.mark.asyncio
async def test_analyze_missing_analysis_returns_error():
    """analyze operation without 'analysis' in options returns success=False with error."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute(
        {
            "operation": "analyze",
            "dot_content": SIMPLE_DOT,
            "options": {},
        }
    )

    assert result.success is False, (
        "analyze without 'analysis' key must return success=False"
    )
    data = _parse_output(result)
    assert "error" in data, "Missing analysis key must return 'error' in response"


@pytest.mark.asyncio
async def test_analyze_cycles_routes_correctly():
    """analyze operation with analysis=cycles returns has_cycles=False for a DAG."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute(
        {
            "operation": "analyze",
            "dot_content": SIMPLE_DOT,
            "options": {"analysis": "cycles"},
        }
    )

    assert result.success is True, (
        f"analyze cycles must return success=True for valid DAG, got: {result.output!r}"
    )
    data = _parse_output(result)
    assert "has_cycles" in data, "cycles result must include 'has_cycles'"
    assert data["has_cycles"] is False, (
        f"SIMPLE_DOT 'digraph G {{a -> b}}' is a DAG with no cycles, got has_cycles={data['has_cycles']}"
    )


@pytest.mark.asyncio
async def test_analyze_invalid_dot_returns_error():
    """analyze operation with invalid DOT content returns success=False with error."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute(
        {
            "operation": "analyze",
            "dot_content": INVALID_DOT,
            "options": {"analysis": "stats"},
        }
    )

    assert result.success is False, "analyze with invalid DOT must return success=False"
    data = _parse_output(result)
    assert "error" in data, "Invalid DOT analyze must return 'error' in response"


@pytest.mark.asyncio
async def test_unknown_operation_returns_error():
    """Unknown operation returns success=False with error containing operation name and supported list."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({"operation": "frobnicate"})

    assert result.success is False, "Unknown operation must return success=False"
    data = _parse_output(result)
    assert "error" in data, "Unknown operation response must have 'error' key"
    assert "frobnicate" in data["error"], (
        f"Error must mention the unknown operation name, got: {data['error']!r}"
    )
    assert "supported" in data, (
        "Unknown operation response must include 'supported' list"
    )
    assert isinstance(data["supported"], list), "'supported' must be a list"


@pytest.mark.asyncio
async def test_render_operation_routes_correctly():
    """render operation calls render.render_dot and returns ToolResult."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    mock_render_result = {
        "success": True,
        "output_path": "/tmp/test_output.svg",
        "format": "svg",
        "engine": "dot",
        "size_bytes": 1234,
    }
    with patch(
        "amplifier_module_tool_dot_graph.render.render_dot",
        return_value=mock_render_result,
    ):
        tool = DotGraphTool()
        result = await tool.execute({"operation": "render", "dot_content": SIMPLE_DOT})

    assert result.success is True, "Mocked render must return success=True"
    data = _parse_output(result)
    assert data["output_path"] == "/tmp/test_output.svg", (
        f"Render output must include output_path, got: {data}"
    )


# ---------------------------------------------------------------------------
# Input schema tests (3 tests)
# ---------------------------------------------------------------------------


def test_input_schema_includes_setup_operation():
    """input_schema operation enum includes all 6 operations: validate, render, setup, analyze, prescan, assemble."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    schema = tool.input_schema

    op_enum = schema["properties"]["operation"]["enum"]
    assert "validate" in op_enum, "Schema enum must include 'validate'"
    assert "render" in op_enum, "Schema enum must include 'render'"
    assert "setup" in op_enum, "Schema enum must include 'setup'"
    assert "analyze" in op_enum, "Schema enum must include 'analyze'"
    assert "prescan" in op_enum, "Schema enum must include 'prescan'"
    assert "assemble" in op_enum, "Schema enum must include 'assemble'"


def test_input_schema_documents_options():
    """input_schema options property has sub-properties: format, engine, layers."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    schema = tool.input_schema

    assert "options" in schema["properties"], "Schema must include 'options' property"
    options = schema["properties"]["options"]

    assert "properties" in options, (
        "options must have 'properties' key (sub-schema with format, engine, layers)"
    )
    option_props = options["properties"]

    assert "format" in option_props, "options.properties must include 'format'"
    assert "engine" in option_props, "options.properties must include 'engine'"
    assert "layers" in option_props, "options.properties must include 'layers'"


def test_input_schema_documents_analyze_options():
    """input_schema options property includes analyze-specific sub-properties."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    schema = tool.input_schema

    assert "options" in schema["properties"], "Schema must include 'options' property"
    option_props = schema["properties"]["options"]["properties"]

    assert "analysis" in option_props, (
        "options.properties must include 'analysis' for analyze operation"
    )
    assert "source_node" in option_props, (
        "options.properties must include 'source_node' for reachability/paths operations"
    )
    assert "target_node" in option_props, (
        "options.properties must include 'target_node' for paths operation"
    )
    assert "cluster_name" in option_props, (
        "options.properties must include 'cluster_name' for subgraph_extract operation"
    )
    assert "dot_content_b" in option_props, (
        "options.properties must include 'dot_content_b' for diff operation"
    )


# ---------------------------------------------------------------------------
# Mount contract tests (3 tests)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mount_registers_real_tool():
    """mount() returns version 0.4.0, indicating the real implementation with prescan/assemble routing."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    result = await mount(coordinator)

    assert result["version"] == "0.4.0", (
        f"Expected version 0.4.0 (prescan/assemble routing complete), got: {result['version']!r}"
    )
    assert result["name"] == "tool-dot-graph", (
        f"Expected name 'tool-dot-graph', got: {result['name']!r}"
    )
    assert "dot_graph" in result["provides"], (
        f"Expected 'dot_graph' in provides, got: {result['provides']}"
    )


@pytest.mark.asyncio
async def test_mounted_tool_can_validate():
    """Tool registered by mount() can actually validate DOT content end-to-end."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    await mount(coordinator)

    args, _ = coordinator.mount.call_args
    tool = args[1]  # second positional arg is the tool instance

    result = await tool.execute({"operation": "validate", "dot_content": SIMPLE_DOT})

    assert result.success is True, (
        "Mounted tool must validate simple DOT as success=True"
    )
    data = _parse_output(result)
    assert data["valid"] is True, (
        f"Mounted tool validate must return valid=True for simple DOT, got: {data}"
    )


# ---------------------------------------------------------------------------
# Prescan routing tests (2 new tests) — RED phase
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_prescan_routes_correctly():
    """prescan operation calls prescan.prescan_repo with repo_path and returns result."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    mock_prescan_result = {
        "success": True,
        "repo_path": "/tmp/test_repo",
        "file_count": 42,
        "modules": [],
    }
    with patch(
        "amplifier_module_tool_dot_graph.prescan.prescan_repo",
        return_value=mock_prescan_result,
    ) as mock_prescan:
        tool = DotGraphTool()
        result = await tool.execute(
            {"operation": "prescan", "options": {"repo_path": "/tmp/test_repo"}}
        )

    assert result.success is True, (
        f"prescan with valid repo_path must return success=True, got: {result.output!r}"
    )
    mock_prescan.assert_called_once_with("/tmp/test_repo")
    data = _parse_output(result)
    assert data["file_count"] == 42, (
        f"prescan result must pass through file_count, got: {data}"
    )


@pytest.mark.asyncio
async def test_prescan_missing_repo_path_error():
    """prescan without repo_path in options returns success=False with error."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({"operation": "prescan", "options": {}})

    assert result.success is False, (
        "prescan without repo_path must return success=False"
    )
    data = _parse_output(result)
    assert "error" in data, "Missing repo_path must return 'error' in response"


# ---------------------------------------------------------------------------
# Assemble routing tests (3 new tests) — RED phase
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_assemble_routes_correctly():
    """assemble operation calls assemble.assemble_hierarchy with manifest and output_dir."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    mock_assemble_result = {
        "success": True,
        "output_dir": "/tmp/test_output",
        "graphs_written": 3,
    }
    with patch(
        "amplifier_module_tool_dot_graph.assemble.assemble_hierarchy",
        return_value=mock_assemble_result,
    ) as mock_assemble:
        tool = DotGraphTool()
        result = await tool.execute(
            {
                "operation": "assemble",
                "options": {
                    "manifest": {"modules": []},
                    "output_dir": "/tmp/test_output",
                },
            }
        )

    assert result.success is True, (
        f"assemble with valid manifest and output_dir must return success=True, got: {result.output!r}"
    )
    mock_assemble.assert_called_once_with({"modules": []}, "/tmp/test_output", render_png=True)
    data = _parse_output(result)
    assert data["graphs_written"] == 3, (
        f"assemble result must pass through graphs_written, got: {data}"
    )


@pytest.mark.asyncio
async def test_assemble_missing_manifest_error():
    """assemble without manifest in options returns success=False with error."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute(
        {"operation": "assemble", "options": {"output_dir": "/tmp/test_output"}}
    )

    assert result.success is False, (
        "assemble without manifest must return success=False"
    )
    data = _parse_output(result)
    assert "error" in data, "Missing manifest must return 'error' in response"


@pytest.mark.asyncio
async def test_assemble_missing_output_dir_error():
    """assemble without output_dir in options returns success=False with error."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute(
        {"operation": "assemble", "options": {"manifest": {"modules": []}}}
    )

    assert result.success is False, (
        "assemble without output_dir must return success=False"
    )
    data = _parse_output(result)
    assert "error" in data, "Missing output_dir must return 'error' in response"


# ---------------------------------------------------------------------------
# Input schema new operations test (1 new test) — RED phase
# ---------------------------------------------------------------------------


def test_input_schema_includes_prescan_assemble():
    """input_schema includes prescan/assemble in enum and new option properties."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    schema = tool.input_schema

    op_enum = schema["properties"]["operation"]["enum"]
    assert "prescan" in op_enum, "Schema enum must include 'prescan'"
    assert "assemble" in op_enum, "Schema enum must include 'assemble'"

    option_props = schema["properties"]["options"]["properties"]
    assert "repo_path" in option_props, (
        "options.properties must include 'repo_path' for prescan operation"
    )
    assert "manifest" in option_props, (
        "options.properties must include 'manifest' for assemble operation"
    )
    assert "output_dir" in option_props, (
        "options.properties must include 'output_dir' for assemble operation"
    )
    assert "invalidated_modules" in option_props, (
        "options.properties must include 'invalidated_modules' for incremental assembly"
    )


# ---------------------------------------------------------------------------
# Mount version 0.4.0 test (1 new test) — RED phase
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mount_returns_version_040():
    """mount() metadata version is 0.4.0 (prescan/assemble routing added)."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    result = await mount(coordinator)

    assert result["version"] == "0.4.0", (
        f"Expected version 0.4.0 (prescan/assemble routing complete), got: {result['version']!r}"
    )
