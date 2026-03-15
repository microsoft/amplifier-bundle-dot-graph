"""
DOT graph tool module for Amplifier.

Provides tools for generating, validating, rendering, and analyzing DOT-format graphs
using pydot and networkx.

Routes tool calls to validate, render, setup_helper, and analyze modules.
"""

import json
import logging
from typing import Any

from amplifier_core import ToolResult

from amplifier_module_tool_dot_graph import analyze, render, setup_helper, validate

logger = logging.getLogger(__name__)


class DotGraphTool:
    """DOT graph tool routing validate, render, setup, and analyze operations.

    Provides:
    - Validation: three-layer syntax, structural, and render-quality checks via pydot
    - Rendering: graphviz CLI wrapper for SVG/PNG/PDF output
    - Setup: environment check for graphviz, pydot, and networkx availability
    - Analysis: reachability, cycle detection, critical path, and structural diff via networkx
      Operations: stats, reachability, unreachable, cycles, paths,
                  critical_path, subgraph_extract, diff
    """

    @property
    def name(self) -> str:
        return "dot_graph"

    @property
    def description(self) -> str:
        return """DOT graph tool — validate, render, and analyze DOT-format graphs.

Operations:
- validate: Parse and validate DOT content through up to three layers (syntax, structural, render)
- render: Render DOT content to SVG, PNG, PDF, or other formats via graphviz CLI
- setup: Check environment for graphviz, pydot, and networkx availability
- analyze: Structural graph analysis via networkx
  - stats: Node count, edge count, density, DAG detection, connected components
  - reachability: All nodes reachable from a source node
  - unreachable: Nodes with no incoming edges (excluding known entry points)
  - cycles: Detect all simple cycles in a directed graph
  - paths: All simple paths between two nodes (capped at 100)
  - critical_path: Longest path in a DAG
  - subgraph_extract: Extract a named cluster subgraph into standalone DOT
  - diff: Structural differences between two DOT graphs"""

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["validate", "render", "setup", "analyze"],
                    "description": "Operation to perform on the DOT graph",
                },
                "dot_content": {
                    "type": "string",
                    "description": "DOT graph content as a string",
                },
                "options": {
                    "type": "object",
                    "description": "Operation-specific options (format, layout engine, analysis type, etc.)",
                    "properties": {
                        "format": {
                            "type": "string",
                            "description": (
                                "Output format for render operation "
                                "(svg, png, pdf, json, ps, eps)"
                            ),
                        },
                        "engine": {
                            "type": "string",
                            "description": (
                                "Layout engine for render operation "
                                "(dot, neato, fdp, sfdp, twopi, circo)"
                            ),
                        },
                        "output_path": {
                            "type": "string",
                            "description": (
                                "Output file path for render operation "
                                "(auto-generated in temp dir if not provided)"
                            ),
                        },
                        "layers": {
                            "type": "array",
                            "description": (
                                "Validation layers to run "
                                "(syntax, structural, render). Defaults to all three."
                            ),
                            "items": {"type": "string"},
                        },
                        "analysis": {
                            "type": "string",
                            "enum": [
                                "stats",
                                "reachability",
                                "unreachable",
                                "cycles",
                                "paths",
                                "critical_path",
                                "subgraph_extract",
                                "diff",
                            ],
                            "description": "Analysis operation to perform (required for analyze operation)",
                        },
                        "source_node": {
                            "type": "string",
                            "description": (
                                "Source node name for reachability and paths analysis operations"
                            ),
                        },
                        "target_node": {
                            "type": "string",
                            "description": "Target node name for paths analysis operation",
                        },
                        "cluster_name": {
                            "type": "string",
                            "description": "Cluster name to extract for subgraph_extract analysis operation",
                        },
                        "dot_content_b": {
                            "type": "string",
                            "description": "Second DOT graph string to compare against for diff analysis operation",
                        },
                    },
                },
            },
            "required": ["operation"],
        }

    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """Execute a DOT graph operation.

        Args:
            input_data: Operation parameters (operation, dot_content, options)

        Returns:
            ToolResult with operation results as JSON in the output field
        """
        operation = input_data.get("operation", "unknown")
        dot_content = input_data.get("dot_content", "")
        options: dict[str, Any] = input_data.get("options") or {}

        if operation == "validate":
            layers = options.get("layers")
            try:
                result = validate.validate_dot(dot_content, layers=layers)
            except ValueError as exc:
                error_result = {
                    "valid": False,
                    "issues": [
                        {"layer": "syntax", "severity": "error", "message": str(exc)}
                    ],
                    "stats": {"nodes": 0, "edges": 0, "clusters": 0, "lines": 0},
                }
                return ToolResult(success=False, output=json.dumps(error_result))
            return ToolResult(success=result["valid"], output=json.dumps(result))

        if operation == "render":
            output_format = options.get("format", "svg")
            engine = options.get("engine", "dot")
            output_path = options.get("output_path")
            result = render.render_dot(dot_content, output_format, engine, output_path)
            return ToolResult(success=result["success"], output=json.dumps(result))

        if operation == "setup":
            result = setup_helper.check_environment()
            return ToolResult(success=True, output=json.dumps(result))

        if operation == "analyze":
            result = analyze.analyze_dot(dot_content, options)
            return ToolResult(success=result["success"], output=json.dumps(result))

        # Unknown operation
        result = {
            "error": f"Unknown operation '{operation}'",
            "supported": ["validate", "render", "setup", "analyze"],
        }
        return ToolResult(success=False, output=json.dumps(result))


async def mount(
    coordinator: Any, config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Mount the dot_graph tool into the coordinator.

    Registers the real tool implementation with validate, render, setup, and analyze routing.

    Args:
        coordinator: The Amplifier coordinator instance
        config: Optional module configuration

    Returns:
        Module metadata dict
    """
    tool = DotGraphTool()

    await coordinator.mount("tools", tool, name=tool.name)

    logger.info(
        "tool-dot-graph mounted: registered 'dot_graph' tool "
        "with validate/render/setup/analyze routing (v0.3.0)"
    )

    return {
        "name": "tool-dot-graph",
        "version": "0.3.0",
        "provides": ["dot_graph"],
    }
