"""Graphviz CLI rendering wrapper for DOT content.

Renders DOT content to SVG, PNG, PDF, JSON, PS, or EPS via graphviz subprocess.
Uses setup_helper for environment detection and graceful degradation.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path, PureWindowsPath

from amplifier_module_tool_dot_graph import setup_helper

# Supported output formats.
SUPPORTED_FORMATS = ("svg", "png", "pdf", "json", "ps", "eps")

# Supported layout engines.
SUPPORTED_ENGINES = ("dot", "neato", "fdp", "sfdp", "twopi", "circo")

# Subprocess timeout for graphviz rendering (seconds).
_RENDER_TIMEOUT_SECS = 30


def _output_root_error(
    reason: str,
    candidate_path: Path,
    root_path: Path,
    resolved_output_path: Path,
    output_format: str,
) -> str:
    """Explain a rejected save without changing configuration or reserving a path."""
    requested_path = (
        candidate_path if candidate_path.is_absolute() else root_path / candidate_path
    )
    full_path = Path(os.path.abspath(requested_path))
    message = (
        f"{reason}\n\nCould not save:\n  {requested_path}\n\n"
        f"Diagrams can currently be saved inside:\n  {root_path}\n\n"
        "No file was written.\n\n"
    )
    redirected = full_path != resolved_output_path
    if redirected:
        message += (
            f"This path resolves to:\n  {resolved_output_path}\n\n"
            "A symlink redirects this path outside the permitted folder. "
            "Remove or avoid the redirect rather than permitting its target.\n\n"
        )

    filename = Path(full_path.name or "diagram").with_suffix(f".{output_format}").name
    alternatives = (
        root_path / filename,
        root_path / f"{Path(filename).stem}-in-root.{output_format}",
        root_path / f"diagram-in-root.{output_format}",
    )
    message += "OPTION 1 — Save without changing configuration\n\n"
    for alternative in alternatives:
        if (
            not alternative.exists()
            and not alternative.is_symlink()
            and alternative.resolve(strict=False).is_relative_to(root_path)
        ):
            message += f'Ask me: "Save the diagram to {alternative} instead."\n\n'
            break
    else:
        message += (
            f'Ask me: "Choose a new .{output_format} filename directly inside '
            f'{root_path}, avoiding existing files, directories and symlinks."\n\n'
        )
    if redirected:
        return message + "No configuration was changed by this failed save."

    requested_parent = full_path.parent
    return message + (
        "OPTION 2 — Change the permitted output folder\n\n"
        "For the dot_graph render operation, update config.render_output_root "
        "in the existing tool-dot-graph entry of the bundle or application "
        "configuration used for this session:\n\n"
        "tools:\n"
        "  - module: tool-dot-graph\n"
        "    config:\n"
        f"      render_output_root: {json.dumps(str(requested_parent), ensure_ascii=False)}\n\n"
        "This is a fragment, not a replacement file. Preserve the entry's source, "
        "other config keys and other settings; update the existing entry rather "
        "than adding a duplicate.\n\n"
        'If you need help finding it, ask me: "Find where tool-dot-graph is '
        f"configured and set render_output_root to {requested_parent}, "
        'preserving my other settings."\n\n'
        "Start a new session with that configuration, then retry "
        f"{requested_path}. This replaces the current permitted folder; "
        "it does not add a second folder. "
        "No configuration was changed by this failed save."
    )


def render_dot(
    dot_content: str,
    output_format: str = "svg",
    engine: str = "dot",
    output_path: str | None = None,
    *,
    output_root: str | os.PathLike[str] | None = None,
    allow_absolute_output_path: bool = False,
    allow_overwrite: bool = False,
) -> dict:
    """Render DOT content to a file using the graphviz CLI.

    Args:
        dot_content: Raw DOT graph string.
        output_format: Output format — one of SUPPORTED_FORMATS. Default 'svg'.
        engine: Layout engine — one of SUPPORTED_ENGINES. Default 'dot'.
        output_path: Destination path. Must be relative to output_root unless
            allow_absolute_output_path is enabled by a trusted internal caller.
            Auto-generated in the system temp dir if None.
        output_root: Trusted root that contains an explicit output_path.
        allow_absolute_output_path: Allow a contained absolute output_path.
            Intended only for trusted internal callers.
        allow_overwrite: Replace an existing destination. Intended only for
            trusted internal callers.

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
    auto_output_path = output_path is None
    try:
        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=f".{output_format}")
            os.close(fd)
        else:
            if output_root is None:
                return {
                    "success": False,
                    "error": "Explicit output_path requires a trusted output_root",
                }

            raw_output_path = os.fspath(output_path)
            windows_path = PureWindowsPath(raw_output_path)
            candidate_path = Path(raw_output_path).expanduser()
            # Foreign Windows paths must not become literal relative filenames on
            # POSIX, even when contained native absolute paths are allowed.
            if (windows_path.drive or windows_path.root) and not candidate_path.is_absolute():
                return {
                    "success": False,
                    "error": "output_path must use a native path within the configured output root",
                }
            if candidate_path.is_absolute() and not allow_absolute_output_path:
                return {
                    "success": False,
                    "error": "output_path must be relative to the configured output root",
                }

            root_path = Path(output_root).expanduser().resolve()
            if candidate_path.is_absolute():
                resolved_output_path = candidate_path.resolve(strict=False)
            else:
                resolved_output_path = (root_path / candidate_path).resolve(strict=False)

            try:
                resolved_output_path.relative_to(root_path)
            except ValueError:
                return {
                    "success": False,
                    "error": _output_root_error(
                        "output_path must remain within the configured output root",
                        candidate_path, root_path, resolved_output_path, output_format,
                    ),
                }

            if resolved_output_path.suffix.lower() != f".{output_format}":
                return {
                    "success": False,
                    "error": (
                        f"output_path must end with '.{output_format}' "
                        f"for format '{output_format}'"
                    ),
                }

            resolved_output_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                resolved_output_path.parent.resolve(strict=True).relative_to(root_path)
            except (FileNotFoundError, ValueError):
                return {
                    "success": False,
                    "error": _output_root_error(
                        "output_path parent escapes the configured output root",
                        candidate_path, root_path,
                        resolved_output_path.resolve(strict=False), output_format,
                    ),
                }

            if resolved_output_path.exists():
                if not resolved_output_path.is_file():
                    return {
                        "success": False,
                        "error": "output_path must be a regular file",
                    }
                if not allow_overwrite:
                    return {
                        "success": False,
                        "error": "output_path already exists; overwriting is not permitted",
                    }
            output_path = str(resolved_output_path)
    except (OSError, ValueError) as exc:
        return {
            "success": False,
            "error": f"Failed to prepare output_path: {exc}",
        }

    # --- Render ---
    succeeded = False
    created_output = auto_output_path
    try:
        # Keep staged output on the destination filesystem so os.replace stays
        # atomic even when the workspace and system temp directory are on different volumes.
        with tempfile.TemporaryDirectory(
            prefix="dot-graph-render-", dir=Path(output_path).parent
        ) as temp_dir:
            tmp_dot_path = Path(temp_dir) / "input.dot"
            rendered_path = Path(temp_dir) / f"output.{output_format}"
            tmp_dot_path.write_text(dot_content, encoding="utf-8")

            result = subprocess.run(
                [
                    engine,
                    f"-T{output_format}",
                    str(tmp_dot_path),
                    "-o",
                    str(rendered_path),
                ],
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

            if not rendered_path.exists() or rendered_path.stat().st_size == 0:
                return {
                    "success": False,
                    "error": "Render produced empty output",
                }

            if auto_output_path or allow_overwrite:
                os.replace(rendered_path, output_path)
            else:
                with (
                    rendered_path.open("rb") as source,
                    open(output_path, "xb") as target,
                ):
                    created_output = True
                    shutil.copyfileobj(source, target)

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
            "error": f"Failed to render output: {exc}",
        }
    finally:
        if created_output and not succeeded and os.path.exists(output_path):
            os.unlink(output_path)
