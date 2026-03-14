"""Tests for tool-dot-graph module skeleton.

Verifies the stub mount() function exists, is callable, and can be imported.
"""

import inspect
from unittest.mock import MagicMock

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
async def test_mount_returns_none():
    """mount() stub returns None when called."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    result = await mount(coordinator)
    assert result is None


@pytest.mark.asyncio
async def test_mount_logs_stub_message(caplog):
    """mount() logs the expected stub message."""
    import logging

    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    with caplog.at_level(logging.INFO, logger="amplifier_module_tool_dot_graph"):
        await mount(coordinator)

    assert any(
        "tool-dot-graph mounted (stub" in record.message for record in caplog.records
    ), (
        f"Expected stub log message not found. Records: {[r.message for r in caplog.records]}"
    )
