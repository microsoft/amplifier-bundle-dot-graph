"""Graphviz CLI rendering wrapper for DOT content.

Renders DOT content to SVG, PNG, PDF, JSON, PS, or EPS via graphviz subprocess.
Uses setup_helper for environment detection and graceful degradation.
"""

from __future__ import annotations

import os
import subprocess
import tempfile

from amplifier_module_tool_dot_graph import setup_helper

# Supported output formats.
SUPPORTED_FORMATS = ("svg", "png", "pdf", "json", "ps", "eps")

# Supported layout engines.
SUPPORTED_ENGINES = ("dot", "neato", "fdp", "sfdp", "twopi", "circo")

# Subprocess timeout for graphviz rendering (seconds).
_RENDER_TIMEOUT_SECS = 30


def render_dot(
    dot_content: str,
    output_format: str = "svg",
    engine: str = "dot",
    output_path: str | None = None,
) -> dict:
    """Render DOT content to a file using the graphviz CLI.

    Args:
        dot_content: Raw DOT graph string.
        output_format: Output format — one of SUPPORTED_FORMATS. Default 'svg'.
        engine: Layout engine — one of SUPPORTED_ENGINES. Default 'dot'.
        output_path: Destination file path. Auto-generated in temp dir if None.

    Returns:
        On success:  {success: True, output_path: str, format: str, engine: str,
                      size_bytes: int}
        On failure:  {success: False, error: str}
    """
    # --- Input validation ---
    if output_format not in SUPPORTED_FORMATS:
        return {
            "success": False,
            "error": (
                f"Unsupported format '{output_format}'. "
                f"Supported formats: {', '.join(SUPPORTED_FORMATS)}"
            ),
        }

    if engine not in SUPPORTED_ENGINES:
        return {
            "success": False,
            "error": (
                f"Unsupported engine '{engine}'. "
                f"Supported engines: {', '.join(SUPPORTED_ENGINES)}"
            ),
        }

    # --- Environment check ---
    env = setup_helper.check_environment()
    graphviz_info = env.get("graphviz", {})

    if not graphviz_info.get("installed", False):
        hint = graphviz_info.get(
            "install_hint", "Install Graphviz from https://graphviz.org/"
        )
        return {
            "success": False,
            "error": f"Graphviz not installed. {hint}",
        }

    available_engines = graphviz_info.get("engines", [])
    if engine not in available_engines:
        return {
            "success": False,
            "error": (
                f"Engine not found on PATH. Available: {', '.join(available_engines)}"
            ),
        }

    # --- Determine output path ---
    # Track whether we generated the output path so we can clean it up on failure.
    auto_output_path = output_path is None
    if output_path is None:
        # NOTE: tempfile.mktemp() is deprecated due to TOCTOU race conditions.
        # It is intentional here: graphviz requires the output path to not exist
        # before writing, so NamedTemporaryFile(delete=False) + close would leave
        # an empty file that some graphviz versions refuse to overwrite.
        output_path = tempfile.mktemp(suffix=f".{output_format}")

    # --- Render ---
    tmp_dot_path: str | None = None
    succeeded = False
    try:
        # encoding="utf-8": DOT labels routinely carry non-ASCII (people names,
        # CJK, accented text). A text-mode write without an encoding uses the
        # locale codepage (cp1252) on Windows and raises UnicodeEncodeError before
        # graphviz even runs. Record the path BEFORE writing so the finally-block
        # cleanup still unlinks the temp file if the write raises.
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".dot", delete=False, encoding="utf-8"
        ) as tmp_dot:
            tmp_dot_path = tmp_dot.name
            tmp_dot.write(dot_content)

        result = subprocess.run(
            [engine, f"-T{output_format}", tmp_dot_path, "-o", output_path],
            capture_output=True,
            text=True,
            # graphviz emits UTF-8; its stderr echoes the offending DOT source
            # (incl. non-ASCII labels) on error. Without an explicit encoding a
            # cp1252 decode of that stderr crashes on Windows.
            encoding="utf-8",
            errors="replace",
            timeout=_RENDER_TIMEOUT_SECS,
        )

        if result.returncode != 0:
            stderr_msg = result.stderr.strip() or "unknown error"
            return {
                "success": False,
                "error": f"Render failed: {stderr_msg}",
            }

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return {
                "success": False,
                "error": "Render produced empty output",
            }

        succeeded = True
        return {
            "success": True,
            "output_path": output_path,
            "format": output_format,
            "engine": engine,
            "size_bytes": os.path.getsize(output_path),
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Render timed out (>{_RENDER_TIMEOUT_SECS}s)",
        }
    except OSError as exc:
        return {
            "success": False,
            "error": f"Failed to run graphviz: {exc}",
        }
    finally:
        if tmp_dot_path and os.path.exists(tmp_dot_path):
            os.unlink(tmp_dot_path)
        # Remove partial output when we generated the path and rendering failed.
        if auto_output_path and not succeeded and os.path.exists(output_path):
            os.unlink(output_path)
