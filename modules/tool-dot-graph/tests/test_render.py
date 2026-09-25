"""Tests for render.py — graphviz CLI rendering wrapper."""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from amplifier_module_tool_dot_graph.render import render_dot

# Detect graphviz availability once for skip markers.
_GRAPHVIZ_INSTALLED = shutil.which("dot") is not None

skip_if_no_graphviz = pytest.mark.skipif(
    not _GRAPHVIZ_INSTALLED,
    reason="graphviz CLI not installed",
)

# Minimal valid DOT content for rendering tests.
_SIMPLE_DOT = "digraph G { A -> B; }"


# ---------------------------------------------------------------------------
# Successful rendering (requires graphviz)
# ---------------------------------------------------------------------------


@skip_if_no_graphviz
def test_render_svg_default():
    """render_dot() with default args produces SVG output file."""
    result = render_dot(_SIMPLE_DOT)

    assert result["success"] is True
    assert result["output_path"].endswith(".svg")
    assert os.path.exists(result["output_path"])
    assert result["size_bytes"] > 0

    # Cleanup
    os.unlink(result["output_path"])


@skip_if_no_graphviz
def test_render_png():
    """render_dot() with format='png' produces a PNG output file."""
    result = render_dot(_SIMPLE_DOT, output_format="png")

    assert result["success"] is True
    assert result["output_path"].endswith(".png")
    assert os.path.exists(result["output_path"])
    assert result["size_bytes"] > 0

    # Cleanup
    os.unlink(result["output_path"])


@skip_if_no_graphviz
def test_render_with_neato_engine():
    """render_dot() with engine='neato' uses neato for layout."""
    result = render_dot(_SIMPLE_DOT, engine="neato")

    assert result["success"] is True
    assert result["engine"] == "neato"
    assert os.path.exists(result["output_path"])

    # Cleanup
    os.unlink(result["output_path"])


@skip_if_no_graphviz
def test_render_custom_output_path():
    """render_dot() writes a relative output beneath the trusted root."""
    with tempfile.TemporaryDirectory() as output_root:
        result = render_dot(
            _SIMPLE_DOT,
            output_path="nested/custom.svg",
            output_root=output_root,
        )
        custom_path = Path(output_root) / "nested" / "custom.svg"
        assert result["success"] is True
        assert Path(result["output_path"]) == custom_path.resolve()
        assert custom_path.exists()
        assert result["size_bytes"] > 0


# ---------------------------------------------------------------------------
# Input validation (no graphviz needed)
# ---------------------------------------------------------------------------


def test_unsupported_format_returns_error():
    """render_dot() with unsupported format returns error dict immediately."""
    result = render_dot(_SIMPLE_DOT, output_format="gif")

    assert result["success"] is False
    assert "error" in result
    assert "Unsupported format" in result["error"]


def test_unsupported_engine_returns_error():
    """render_dot() with unsupported engine returns error dict immediately."""
    result = render_dot(_SIMPLE_DOT, engine="invalid_engine")

    assert result["success"] is False
    assert "error" in result
    assert "Unsupported engine" in result["error"]


# ---------------------------------------------------------------------------
# Graceful degradation
# ---------------------------------------------------------------------------


def test_no_graphviz_returns_install_hint():
    """When graphviz not installed (mocked), result contains install hint."""
    mock_env = {
        "graphviz": {
            "installed": False,
            "version": None,
            "engines": [],
            "install_hint": "Install Graphviz via package manager",
        },
        "pydot": {"installed": True, "version": "3.0.0"},
        "networkx": {"installed": True, "version": "3.0.0"},
    }

    with patch(
        "amplifier_module_tool_dot_graph.render.setup_helper.check_environment",
        return_value=mock_env,
    ):
        result = render_dot(_SIMPLE_DOT)

    assert result["success"] is False
    assert "error" in result
    assert "Graphviz not installed" in result["error"]
    assert "Install Graphviz" in result["error"]


def test_engine_not_available_returns_error():
    """When engine not on PATH (mocked), result includes available engines."""
    mock_env = {
        "graphviz": {
            "installed": True,
            "version": "2.43.0",
            "engines": ["dot", "fdp"],  # neato not available
        },
        "pydot": {"installed": True, "version": "3.0.0"},
        "networkx": {"installed": True, "version": "3.0.0"},
    }

    with patch(
        "amplifier_module_tool_dot_graph.render.setup_helper.check_environment",
        return_value=mock_env,
    ):
        result = render_dot(_SIMPLE_DOT, engine="neato")

    assert result["success"] is False
    assert "error" in result
    assert "Engine not found on PATH" in result["error"]
    assert "dot" in result["error"]  # available engines listed


# ---------------------------------------------------------------------------
# Output path confinement
# ---------------------------------------------------------------------------


def _installed_graphviz_env() -> dict:
    return {
        "graphviz": {
            "installed": True,
            "version": "test",
            "engines": ["dot"],
        },
        "pydot": {"installed": True, "version": "test"},
        "networkx": {"installed": True, "version": "test"},
    }


@pytest.mark.parametrize(
    "output_path",
    [
        "../outside.svg",
        "/tmp/outside.svg",
        r"C:\outside.svg",
        r"\\server\share\outside.svg",
    ],
)
def test_untrusted_output_path_escape_is_rejected_before_graphviz(
    tmp_path: Path, output_path: str
):
    """Traversal, absolute, drive, and UNC destinations fail before execution."""
    with (
        patch(
            "amplifier_module_tool_dot_graph.render.setup_helper.check_environment",
            return_value=_installed_graphviz_env(),
        ),
        patch(
            "amplifier_module_tool_dot_graph.render.subprocess.run"
        ) as subprocess_run,
    ):
        result = render_dot(
            _SIMPLE_DOT,
            output_path=output_path,
            output_root=tmp_path,
        )

    assert result["success"] is False
    assert "output_path" in result["error"]
    subprocess_run.assert_not_called()


def test_output_path_suffix_must_match_format(tmp_path: Path):
    """The selected format and destination suffix must agree."""
    with (
        patch(
            "amplifier_module_tool_dot_graph.render.setup_helper.check_environment",
            return_value=_installed_graphviz_env(),
        ),
        patch(
            "amplifier_module_tool_dot_graph.render.subprocess.run"
        ) as subprocess_run,
    ):
        result = render_dot(
            _SIMPLE_DOT,
            output_format="png",
            output_path="diagram.svg",
            output_root=tmp_path,
        )

    assert result["success"] is False
    assert "must end with '.png'" in result["error"]
    subprocess_run.assert_not_called()


def test_existing_output_is_not_overwritten(tmp_path: Path):
    """Agent-facing renders fail closed when the destination already exists."""
    destination = tmp_path / "diagram.svg"
    destination.write_text("keep", encoding="utf-8")

    with (
        patch(
            "amplifier_module_tool_dot_graph.render.setup_helper.check_environment",
            return_value=_installed_graphviz_env(),
        ),
        patch(
            "amplifier_module_tool_dot_graph.render.subprocess.run"
        ) as subprocess_run,
    ):
        result = render_dot(
            _SIMPLE_DOT,
            output_path="diagram.svg",
            output_root=tmp_path,
        )

    assert result["success"] is False
    assert "overwriting is not permitted" in result["error"]
    assert destination.read_text(encoding="utf-8") == "keep"
    subprocess_run.assert_not_called()


def test_symlink_escape_is_rejected(tmp_path: Path):
    """An existing symlink beneath the root cannot redirect the output outside."""
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    link = tmp_path / "linked"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlinks are not available in this environment")

    with (
        patch(
            "amplifier_module_tool_dot_graph.render.setup_helper.check_environment",
            return_value=_installed_graphviz_env(),
        ),
        patch(
            "amplifier_module_tool_dot_graph.render.subprocess.run"
        ) as subprocess_run,
    ):
        result = render_dot(
            _SIMPLE_DOT,
            output_path="linked/escape.svg",
            output_root=tmp_path,
        )

    assert result["success"] is False
    assert "configured output root" in result["error"]
    assert not (outside / "escape.svg").exists()
    subprocess_run.assert_not_called()


# ---------------------------------------------------------------------------
# Result structure
# ---------------------------------------------------------------------------


@skip_if_no_graphviz
def test_success_result_has_required_keys():
    """Successful render result contains all required keys."""
    result = render_dot(_SIMPLE_DOT)

    assert result["success"] is True
    assert "output_path" in result
    assert "format" in result
    assert "engine" in result
    assert "size_bytes" in result

    # Values are sensible types
    assert isinstance(result["output_path"], str)
    assert isinstance(result["format"], str)
    assert isinstance(result["engine"], str)
    assert isinstance(result["size_bytes"], int)

    # Cleanup
    os.unlink(result["output_path"])


def test_error_result_has_required_keys():
    """Error result always contains 'success' (False) and 'error' keys."""
    # Use unsupported format to trigger an error without needing graphviz.
    result = render_dot(_SIMPLE_DOT, output_format="bmp")

    assert "success" in result
    assert result["success"] is False
    assert "error" in result
    assert isinstance(result["error"], str)
    assert len(result["error"]) > 0
