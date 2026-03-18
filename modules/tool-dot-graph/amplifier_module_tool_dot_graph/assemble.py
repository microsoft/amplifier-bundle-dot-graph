"""Hierarchical DOT Assembly — filesystem plumbing only.

Copies per-module DOT files to an output directory, discovers agent-produced
DOT files, and writes manifest.json.

Public API: assemble_hierarchy(manifest, output_dir, render_png=False) -> dict
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from pathlib import Path

from amplifier_module_tool_dot_graph import render as _render

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def assemble_hierarchy(
    manifest: dict,
    output_dir: str,
    render_png: bool = False,
) -> dict:
    """Copy per-module DOT files, discover agent outputs, write manifest.json.

    Args:
        manifest: Dict with 'modules' and 'subsystems' keys describing the structure.
            modules: {mod_name: {dot_path: str, subsystem: str}}
            subsystems: {ss_name: {modules: [mod_name]}}
        output_dir: Directory to write output files.
        render_png: If True, render discovered DOT files to PNG via graphviz.
            Render failures are non-fatal and recorded in 'warnings'.
            Default: False.

    Returns:
        On success:
            {
                success: True,
                outputs: {overview: str|None, subsystems: {name: path}},
                stats: {subsystems: int, modules: int},
                warnings: [str],
            }
        On failure:
            {success: False, error: str}
    """
    # --- Validate manifest ---
    if not manifest or not isinstance(manifest, dict):
        return _error("Manifest must be a non-empty dict")

    if "modules" not in manifest:
        return _error("Manifest is missing required 'modules' key")

    if "subsystems" not in manifest:
        return _error("Manifest is missing required 'subsystems' key")

    modules_def: dict = manifest["modules"]
    subsystems_def: dict = manifest["subsystems"]

    warnings: list[str] = []

    # --- Create output directories ---
    os.makedirs(output_dir, exist_ok=True)
    subsystems_dir = str(Path(output_dir) / "subsystems")
    os.makedirs(subsystems_dir, exist_ok=True)

    # --- Copy per-module DOT files to subsystems/ ---
    for mod_name, mod_info in modules_def.items():
        dot_path = mod_info.get("dot_path", "")
        if not dot_path or not Path(dot_path).exists():
            warnings.append(
                f"Module '{mod_name}': DOT file '{dot_path}' not found — skipped"
            )
            continue
        dest = str(Path(subsystems_dir) / f"{mod_name}.dot")
        try:
            shutil.copy2(dot_path, dest)
        except OSError as exc:
            warnings.append(
                f"Module '{mod_name}': could not copy DOT file '{dot_path}': {exc}"
            )

    # --- Discover agent-produced DOTs ---
    # Subsystem DOTs: any .dot files present in subsystems/ directory
    subsystem_paths: dict[str, str] = {}
    for dot_file in sorted(Path(subsystems_dir).glob("*.dot")):
        name = dot_file.stem
        subsystem_paths[name] = str(dot_file)

    # Overview DOT: look for overview.dot in output root
    overview_path_candidate = str(Path(output_dir) / "overview.dot")
    overview_path: str | None = (
        overview_path_candidate if Path(overview_path_candidate).exists() else None
    )

    # --- Write manifest.json ---
    manifest_data = {
        "modules": modules_def,
        "subsystems": subsystems_def,
        "overview_path": overview_path,
    }
    manifest_json_path = str(Path(output_dir) / "manifest.json")
    Path(manifest_json_path).write_text(json.dumps(manifest_data, indent=2))

    # --- Optionally render discovered DOT files to PNG ---
    if render_png:
        dot_paths_to_render: list[str] = list(subsystem_paths.values())
        if overview_path:
            dot_paths_to_render.append(overview_path)
        for dot_path in dot_paths_to_render:
            png_path = dot_path.replace(".dot", ".png")
            try:
                dot_content = Path(dot_path).read_text()
                render_result = _render.render_dot(dot_content, "png", "dot", png_path)
                if not render_result.get("success"):
                    warnings.append(
                        f"PNG render failed for '{dot_path}': "
                        f"{render_result.get('error', 'unknown error')}"
                    )
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"PNG render error for '{dot_path}': {exc}")
                logger.debug("PNG render exception for %s", dot_path, exc_info=True)

    stats = {
        "subsystems": len(subsystems_def),
        "modules": len(modules_def),
    }

    return {
        "success": True,
        "outputs": {
            "overview": overview_path,
            "subsystems": subsystem_paths,
        },
        "stats": stats,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Error helper
# ---------------------------------------------------------------------------


def _error(message: str) -> dict:
    """Build a standardized error response dict."""
    return {"success": False, "error": message}
