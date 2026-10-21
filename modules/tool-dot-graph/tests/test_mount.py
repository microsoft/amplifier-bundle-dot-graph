"""Tests for tool-dot-graph module.

Verifies that mount() registers the real Phase 2 tool with the coordinator,
satisfying the Amplifier protocol_compliance requirement and exercising the
validate/render/setup routing implementation.
"""

import inspect
import json
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest


def test_module_imports():
    """Module can be imported without errors."""
    import amplifier_module_tool_dot_graph  # noqa: F401


def test_mount_is_callable():
    """mount is an importable callable."""
    from amplifier_module_tool_dot_graph import mount

    assert callable(mount)


def test_mount_is_coroutine_function():
    """mount is an async (coroutine) function."""
    from amplifier_module_tool_dot_graph import mount

    assert inspect.iscoroutinefunction(mount), "mount must be async def"


def test_mount_signature():
    """mount accepts coordinator and optional config parameters."""
    from amplifier_module_tool_dot_graph import mount

    sig = inspect.signature(mount)
    params = list(sig.parameters.keys())
    assert "coordinator" in params, "mount must have 'coordinator' parameter"
    assert "config" in params, "mount must have 'config' parameter"


def test_mount_config_defaults_to_none():
    """mount's config parameter defaults to None."""
    from amplifier_module_tool_dot_graph import mount

    sig = inspect.signature(mount)
    config_param = sig.parameters["config"]
    assert config_param.default is None, "config must default to None"


@pytest.mark.asyncio
async def test_mount_registers_tool_with_coordinator():
    """mount() calls coordinator.mount() to register a tool — satisfies protocol_compliance."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    await mount(coordinator)

    assert coordinator.mount.called, (
        "coordinator.mount() must be called — the validator requires a tool to be mounted"
    )


@pytest.mark.asyncio
async def test_mount_registers_tool_under_tools_namespace():
    """mount() registers the tool under the 'tools' namespace."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    await mount(coordinator)

    # First positional arg must be "tools"
    args, kwargs = coordinator.mount.call_args
    assert args[0] == "tools", (
        f"Tool must be registered under 'tools' namespace, got: {args[0]!r}"
    )


@pytest.mark.asyncio
async def test_mount_registers_tool_with_name_kwarg():
    """mount() passes name= kwarg when registering the tool."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    await mount(coordinator)

    args, kwargs = coordinator.mount.call_args
    assert "name" in kwargs, (
        "coordinator.mount() must receive a 'name' keyword argument"
    )
    assert isinstance(kwargs["name"], str) and kwargs["name"], (
        "Tool name must be a non-empty string"
    )


@pytest.mark.asyncio
async def test_mounted_tool_has_name_property():
    """The tool passed to coordinator.mount() has a 'name' property."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    await mount(coordinator)

    args, _ = coordinator.mount.call_args
    tool = args[1]  # second positional arg is the tool instance
    assert hasattr(tool, "name"), "Tool must have a 'name' property"
    assert isinstance(tool.name, str) and tool.name, (
        "Tool name must be a non-empty string"
    )


@pytest.mark.asyncio
async def test_mounted_tool_has_description_property():
    """The tool passed to coordinator.mount() has a 'description' property."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    await mount(coordinator)

    args, _ = coordinator.mount.call_args
    tool = args[1]
    assert hasattr(tool, "description"), "Tool must have a 'description' property"
    assert isinstance(tool.description, str) and tool.description, (
        "Tool description must be a non-empty string"
    )


@pytest.mark.asyncio
async def test_mounted_tool_has_input_schema_property():
    """The tool passed to coordinator.mount() has an 'input_schema' dict property."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    await mount(coordinator)

    args, _ = coordinator.mount.call_args
    tool = args[1]
    assert hasattr(tool, "input_schema"), "Tool must have an 'input_schema' property"
    assert isinstance(tool.input_schema, dict), "input_schema must be a dict"
    assert tool.input_schema.get("type") == "object", (
        "input_schema must have type: object"
    )


@pytest.mark.asyncio
async def test_mounted_tool_name_matches_registration_name():
    """The tool's name property matches the name kwarg passed to coordinator.mount()."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    await mount(coordinator)

    args, kwargs = coordinator.mount.call_args
    tool = args[1]
    assert tool.name == kwargs["name"], (
        f"tool.name ({tool.name!r}) must match name kwarg ({kwargs['name']!r})"
    )


@pytest.mark.asyncio
async def test_mount_returns_module_metadata():
    """mount() returns a metadata dict (not None) after registering the tool."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    result = await mount(coordinator)

    assert result is not None, "mount() must return module metadata dict, not None"
    assert isinstance(result, dict), f"mount() must return a dict, got {type(result)}"
    assert "name" in result, "metadata must include 'name'"
    assert "version" in result, "metadata must include 'version'"
    assert "provides" in result, "metadata must include 'provides'"


@pytest.mark.asyncio
async def test_mounted_tool_execute_is_callable():
    """The mounted tool has a callable execute method."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    await mount(coordinator)

    args, _ = coordinator.mount.call_args
    tool = args[1]
    assert callable(tool.execute), "Tool must have a callable execute method"


@pytest.mark.asyncio
async def test_mounted_tool_execute_returns_result():
    """The mounted tool's execute() returns a result object with success and output fields."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    await mount(coordinator)

    args, _ = coordinator.mount.call_args
    tool = args[1]

    result = await tool.execute({})

    assert result is not None, "execute() must return a result, not None"
    assert hasattr(result, "success"), "Result must have 'success' attribute"
    assert hasattr(result, "output"), "Result must have 'output' attribute"


@pytest.mark.asyncio
async def test_mount_configures_trusted_render_output_root(tmp_path):
    """mount() passes trusted render_output_root configuration to the tool."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    await mount(coordinator, {"render_output_root": str(tmp_path)})

    args, _ = coordinator.mount.call_args
    tool = args[1]
    assert tool.render_output_root == str(tmp_path.resolve())
    description = tool.input_schema["properties"]["options"]["properties"][
        "output_path"
    ]["description"]
    assert "relative or absolute" in description.lower()
    assert "replaced" in description.lower()
    assert "allow_overwrite" not in tool.input_schema["properties"]["options"]["properties"]


@pytest.mark.asyncio
@pytest.mark.parametrize("explicit", [False, True])
async def test_mount_uses_session_root_unless_explicitly_configured(tmp_path, monkeypatch, explicit):
    """Session working directory, not process cwd, is the default render root."""
    from amplifier_module_tool_dot_graph import mount

    process_root = tmp_path / "process"
    process_root.mkdir()
    monkeypatch.chdir(process_root)
    coordinator = MagicMock()
    coordinator.mount = AsyncMock()
    session_root = tmp_path / "session"
    coordinator.get_capability.return_value = str(session_root)
    explicit_root = tmp_path / "configured"
    config = {"render_output_root": explicit_root} if explicit else None

    await mount(coordinator, config)

    tool = coordinator.mount.call_args.args[1]
    expected = explicit_root if explicit else session_root
    assert tool.render_output_root == str(expected.resolve())
    if not explicit:
        coordinator.get_capability.assert_called_once_with("session.working_dir")


@pytest.mark.asyncio
async def test_mount_falls_back_to_process_cwd_without_session_root(tmp_path, monkeypatch):
    from amplifier_module_tool_dot_graph import mount

    monkeypatch.chdir(tmp_path)
    coordinator = MagicMock()
    coordinator.mount = AsyncMock()
    coordinator.get_capability.return_value = None
    await mount(coordinator)
    tool = coordinator.mount.call_args.args[1]
    assert tool.render_output_root == str(Path.cwd().resolve())


@pytest.mark.skipif(shutil.which("dot") is None, reason="graphviz CLI not installed")
@pytest.mark.parametrize("explicit", [False, True])
async def test_mounted_render_writes_in_session_or_configured_root(tmp_path, monkeypatch, explicit):
    """Verify mount root selection by inspecting actual renderer artifacts."""
    from amplifier_module_tool_dot_graph import mount

    process_root = tmp_path / "process"
    process_root.mkdir()
    monkeypatch.chdir(process_root)
    session_root = tmp_path / "session"
    configured_root = tmp_path / "configured"
    coordinator = MagicMock()
    coordinator.mount = AsyncMock()
    coordinator.get_capability.return_value = str(session_root)
    await mount(
        coordinator, {"render_output_root": configured_root} if explicit else None
    )
    tool = coordinator.mount.call_args.args[1]
    result = await tool.execute(
        {
            "operation": "render",
            "dot_content": "digraph G { a -> b }",
            "options": {"output_path": "diagram.svg"},
        }
    )
    assert result.success, result.output
    root = configured_root if explicit else session_root
    destination = root / "diagram.svg"
    assert Path(json.loads(result.output)["output_path"]) == destination.resolve()
    assert destination.read_bytes().startswith(b"<?xml")
    assert list(process_root.iterdir()) == []
    assert not (session_root if explicit else configured_root).exists()
