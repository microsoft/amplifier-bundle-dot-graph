"""Tests for render.py — graphviz CLI rendering wrapper."""

import errno
import json
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
    """Direct callers must explicitly opt in before replacing an existing image."""
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


@pytest.mark.parametrize("absolute", [False, True])
@pytest.mark.parametrize(
    "folder",
    ["outside", "space # and 'quote", 'double"quote', "line\nbreak", "unicode-\u03bb", "unicode-\U0001f600"],
)
def test_escape_guidance_has_full_paths_and_inline_configuration(
    tmp_path: Path, monkeypatch, absolute: bool, folder: str
):
    """Guidance uses the configured root, not cwd, and quotes configuration safely."""
    if os.name == "nt" and any(char in folder for char in '"\n'):
        pytest.skip("filename is not supported on Windows")
    root = tmp_path.resolve() / "workspace"
    root.mkdir()
    requested = root.parent / folder / "diagram.svg"
    relative = Path("..") / folder / "diagram.svg"
    monkeypatch.chdir(tmp_path.parent)
    with (
        patch(
            "amplifier_module_tool_dot_graph.render.setup_helper.check_environment",
            return_value=_installed_graphviz_env(),
        ),
        patch("amplifier_module_tool_dot_graph.render.subprocess.run") as run,
    ):
        result = render_dot(
            _SIMPLE_DOT, output_path=str(requested if absolute else relative),
            output_root=root, allow_absolute_output_path=True,
        )
    assert set(result) == {"success", "error"}
    assert not result["success"]
    error = result["error"]
    full_request = requested if absolute else root / relative
    assert error.startswith("output_path must remain within the configured output root")
    assert f"Could not save:\n  {full_request}" in error
    assert f"Diagrams can currently be saved inside:\n  {root}" in error
    assert f'Ask me: "Save the diagram to {root / "diagram.svg"} instead."' in error
    assert "No file was written." in error
    assert "OPTION 1" in error and "OPTION 2" in error
    assert "For the dot_graph render operation" in error
    fragment = error.split("\ntools:\n", 1)[1].split("\n\n", 1)[0]
    assert fragment.startswith("  - module: tool-dot-graph\n    config:\n")
    quoted_parent = fragment.split("render_output_root: ", 1)[1]
    # Root tests additionally verify YAML parsing and mounting for non-BMP characters.
    assert json.loads(quoted_parent) == str(requested.parent)
    assert "fragment, not a replacement file" in error
    assert "Preserve the entry's source, other config keys and other settings" in error
    assert "rather than adding a duplicate" in error
    assert "Find where tool-dot-graph is configured" in error
    assert "Start a new session" in error
    assert f"then retry {full_request}" in error
    assert "replaces the current permitted folder; it does not add a second folder" in error
    assert "No configuration was changed" in error
    assert ".amplifier/" not in error
    assert "docs/" not in error
    assert not requested.exists()
    assert list(root.iterdir()) == []
    run.assert_not_called()


@pytest.mark.parametrize("collision", ["directory", "symlink", "file", "all"])
def test_guidance_does_not_suggest_a_colliding_or_redirected_destination(
    tmp_path: Path, collision: str
):
    root = tmp_path.resolve() / "workspace"
    root.mkdir()
    destination = root / "diagram.png"
    if collision == "symlink":
        try:
            destination.symlink_to(tmp_path / "do-not-touch.png")
        except OSError:
            pytest.skip("symlinks are not available in this environment")
    elif collision == "file":
        destination.write_bytes(b"keep")
    else:
        destination.mkdir()
    if collision == "all":
        (root / "diagram-in-root.png").mkdir()
    before = set(root.iterdir())
    with (
        patch(
            "amplifier_module_tool_dot_graph.render.setup_helper.check_environment",
            return_value=_installed_graphviz_env(),
        ),
        patch("amplifier_module_tool_dot_graph.render.subprocess.run") as run,
    ):
        result = render_dot(
            _SIMPLE_DOT, output_format="png", output_path="../diagram.txt",
            output_root=root,
        )
    error = result["error"]
    assert not result["success"]
    assert f'Save the diagram to {destination} instead.' not in error
    if collision == "all":
        assert f"Choose a new .png filename directly inside {root}" in error
        assert "Save the diagram to" not in error
    else:
        assert f'Save the diagram to {root / "diagram-in-root.png"} instead.' in error
    assert set(root.iterdir()) == before
    run.assert_not_called()


@pytest.mark.parametrize("parent_link", [False, True])
def test_symlink_guidance_shows_redirect_without_suggesting_a_wider_root(
    tmp_path: Path, parent_link: bool
):
    root = tmp_path.resolve() / "workspace"
    root.mkdir()
    outside = root.parent / "outside"
    outside.mkdir()
    target = outside / "diagram.svg"
    target.write_bytes(b"keep")
    link = root / ("linked" if parent_link else "diagram.svg")
    try:
        link.symlink_to(outside if parent_link else target, target_is_directory=parent_link)
    except OSError:
        pytest.skip("symlinks are not available in this environment")
    requested = link / "diagram.svg" if parent_link else link
    with (
        patch(
            "amplifier_module_tool_dot_graph.render.setup_helper.check_environment",
            return_value=_installed_graphviz_env(),
        ),
        patch("amplifier_module_tool_dot_graph.render.subprocess.run") as run,
    ):
        result = render_dot(
            _SIMPLE_DOT, output_path=str(requested), output_root=root,
            allow_absolute_output_path=True,
        )
    error = result["error"]
    assert not result["success"]
    assert f"Could not save:\n  {requested}" in error
    assert f"This path resolves to:\n  {target}" in error
    assert "Remove or avoid the redirect rather than permitting its target" in error
    assert "render_output_root:" not in error
    assert "OPTION 2" not in error
    safe = root / ("diagram.svg" if parent_link else "diagram-in-root.svg")
    assert f'Save the diagram to {safe} instead.' in error
    assert not safe.exists()
    assert link.is_symlink()
    assert target.read_bytes() == b"keep"
    run.assert_not_called()


def test_parent_recheck_reuses_guidance_without_permitting_redirect(tmp_path: Path):
    """A parent redirected after initial resolution still gets containment guidance."""
    root = tmp_path.resolve() / "workspace"
    root.mkdir()
    outside = root.parent / "outside"
    outside.mkdir()
    probe = root / "probe"
    try:
        probe.symlink_to(outside, target_is_directory=True)
        probe.unlink()
    except OSError:
        pytest.skip("symlinks are not available in this environment")
    requested = root / "nested" / "diagram.svg"

    def redirect_parent(*args, **kwargs):
        requested.parent.symlink_to(outside, target_is_directory=True)

    with (
        patch(
            "amplifier_module_tool_dot_graph.render.setup_helper.check_environment",
            return_value=_installed_graphviz_env(),
        ),
        patch("amplifier_module_tool_dot_graph.render.Path.mkdir", side_effect=redirect_parent),
        patch("amplifier_module_tool_dot_graph.render.subprocess.run") as run,
    ):
        result = render_dot(
            _SIMPLE_DOT, output_path=str(requested), output_root=root,
            allow_absolute_output_path=True,
        )
    error = result["error"]
    assert error.startswith("output_path parent escapes the configured output root")
    assert f"Could not save:\n  {requested}" in error
    assert f"This path resolves to:\n  {outside / 'diagram.svg'}" in error
    assert "No file was written." in error
    assert "OPTION 2" not in error
    assert list(outside.iterdir()) == []
    run.assert_not_called()


@skip_if_no_graphviz
@pytest.mark.parametrize("existing", [False, True])
def test_atomic_replacement_stages_on_destination_filesystem(tmp_path: Path, existing: bool):
    """The final rename must not cross from system temp to a mounted workspace."""
    destination = tmp_path / "diagram.svg"
    if existing:
        destination.write_bytes(b"previous image")
    real_replace = os.replace

    def same_filesystem_replace(source, target):
        if Path(source).parent.parent.resolve() != destination.parent.resolve():
            raise OSError(errno.EXDEV, "Invalid cross-device link")
        assert Path(source).read_bytes().startswith(b"<?xml")
        if existing:
            assert destination.read_bytes() == b"previous image"
        else:
            assert not destination.exists()
        real_replace(source, target)

    with patch(
        "amplifier_module_tool_dot_graph.render.os.replace",
        side_effect=same_filesystem_replace,
    ) as replace:
        result = render_dot(
            _SIMPLE_DOT, output_path="diagram.svg", output_root=tmp_path,
            allow_overwrite=True,
        )
    assert result["success"], result
    replace.assert_called_once()
    assert destination.read_bytes().startswith(b"<?xml")
    assert list(tmp_path.iterdir()) == [destination]


@skip_if_no_graphviz
@pytest.mark.parametrize("existing", [False, True])
def test_failed_final_replace_leaves_no_partial_output(tmp_path: Path, existing: bool):
    destination = tmp_path / "diagram.svg"
    if existing:
        destination.write_bytes(b"previous image")
    with patch(
        "amplifier_module_tool_dot_graph.render.os.replace",
        side_effect=PermissionError("destination is not writable"),
    ):
        result = render_dot(
            _SIMPLE_DOT, output_path="diagram.svg", output_root=tmp_path,
            allow_overwrite=True,
        )
    assert not result["success"]
    assert "Failed to render output" in result["error"]
    if existing:
        assert destination.read_bytes() == b"previous image"
        assert list(tmp_path.iterdir()) == [destination]
    else:
        assert list(tmp_path.iterdir()) == []


@skip_if_no_graphviz
def test_final_replace_does_not_follow_a_destination_symlink(tmp_path: Path):
    """A symlink inserted after validation is replaced, never opened for writing."""
    outside = tmp_path / "outside.svg"
    outside.write_bytes(b"keep outside")
    root = tmp_path / "workspace"
    root.mkdir()
    destination = root / "diagram.svg"
    destination.write_bytes(b"previous image")
    try:
        probe = root / "probe"
        probe.symlink_to(outside)
        probe.unlink()
    except OSError:
        pytest.skip("symlinks are not available in this environment")
    real_replace = os.replace

    def replace_after_symlink_swap(source, target):
        destination.unlink()
        destination.symlink_to(outside)
        real_replace(source, target)

    with patch(
        "amplifier_module_tool_dot_graph.render.os.replace",
        side_effect=replace_after_symlink_swap,
    ):
        result = render_dot(
            _SIMPLE_DOT, output_path="diagram.svg", output_root=root,
            allow_overwrite=True,
        )
    assert result["success"], result
    assert not destination.is_symlink()
    assert destination.read_bytes().startswith(b"<?xml")
    assert outside.read_bytes() == b"keep outside"
    assert list(root.iterdir()) == [destination]


def test_directory_output_is_rejected_before_graphviz(tmp_path: Path):
    destination = tmp_path / "diagram.svg"
    destination.mkdir()
    with (
        patch(
            "amplifier_module_tool_dot_graph.render.setup_helper.check_environment",
            return_value=_installed_graphviz_env(),
        ),
        patch("amplifier_module_tool_dot_graph.render.subprocess.run") as run,
    ):
        result = render_dot(
            _SIMPLE_DOT, output_path="diagram.svg", output_root=tmp_path,
            allow_overwrite=True,
        )
    assert not result["success"]
    assert "regular file" in result["error"]
    assert destination.is_dir()
    run.assert_not_called()


@pytest.mark.parametrize("stage", ["mkstemp", "mkdir", "TemporaryDirectory"])
def test_output_preparation_and_staging_errors_are_structured(tmp_path: Path, stage: str):
    destination = tmp_path / "diagram.svg"
    destination.write_bytes(b"previous image")
    failing_function = (
        "amplifier_module_tool_dot_graph.render.Path.mkdir" if stage == "mkdir"
        else f"amplifier_module_tool_dot_graph.render.tempfile.{stage}"
    )
    with (
        patch(
            "amplifier_module_tool_dot_graph.render.setup_helper.check_environment",
            return_value=_installed_graphviz_env(),
        ),
        patch(failing_function, side_effect=PermissionError("cannot stage output")),
        patch("amplifier_module_tool_dot_graph.render.subprocess.run") as run,
    ):
        result = render_dot(
            _SIMPLE_DOT, output_path=None if stage == "mkstemp" else "diagram.svg",
            output_root=tmp_path, allow_overwrite=True,
        )
    assert not result["success"]
    assert "cannot stage output" in result["error"]
    assert destination.read_bytes() == b"previous image"
    assert list(tmp_path.iterdir()) == [destination]
    run.assert_not_called()


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
