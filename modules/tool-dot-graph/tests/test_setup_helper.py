"""Tests for setup_helper.py — environment detection for graphviz, pydot, networkx."""

from unittest.mock import patch


def test_check_environment_returns_dict():
    """check_environment() returns dict with graphviz, pydot, networkx keys."""
    from amplifier_module_tool_dot_graph.setup_helper import check_environment

    result = check_environment()

    assert isinstance(result, dict), "check_environment() must return a dict"
    assert "graphviz" in result, "Result must have 'graphviz' key"
    assert "pydot" in result, "Result must have 'pydot' key"
    assert "networkx" in result, "Result must have 'networkx' key"


def test_graphviz_status_has_installed_key():
    """graphviz status always includes 'installed' as bool."""
    from amplifier_module_tool_dot_graph.setup_helper import _check_graphviz

    result = _check_graphviz()

    assert "installed" in result, "graphviz status must have 'installed' key"
    assert isinstance(result["installed"], bool), "'installed' must be a bool"


def test_graphviz_installed_includes_version_and_engines():
    """When graphviz IS installed, version and engines populated, 'dot' in engines."""
    from amplifier_module_tool_dot_graph.setup_helper import _check_graphviz

    result = _check_graphviz()

    # graphviz IS installed in this environment (verified: /usr/bin/dot)
    assert result["installed"] is True, "graphviz must be detected as installed"
    assert result["version"] is not None, "version must be populated when installed"
    assert isinstance(result["version"], str), "version must be a string"
    assert isinstance(result["engines"], list), "engines must be a list"
    assert "dot" in result["engines"], "'dot' engine must be in engines list"


def test_graphviz_not_installed_returns_hint():
    """When graphviz NOT on PATH (mock shutil.which), returns install_hint, empty engines."""
    from amplifier_module_tool_dot_graph.setup_helper import _check_graphviz

    # Mock shutil.which to simulate graphviz not being installed
    with patch("shutil.which", return_value=None):
        result = _check_graphviz()

    assert result["installed"] is False, "installed must be False when graphviz not on PATH"
    assert "install_hint" in result, "Must include install_hint when not installed"
    assert isinstance(result["install_hint"], str) and result["install_hint"], (
        "install_hint must be a non-empty string"
    )
    assert result["engines"] == [], "engines must be empty list when not installed"
    assert result["version"] is None, "version must be None when not installed"


def test_pydot_detected():
    """pydot always detected (declared dependency)."""
    from amplifier_module_tool_dot_graph.setup_helper import _check_pydot

    result = _check_pydot()

    assert isinstance(result, dict), "_check_pydot() must return a dict"
    assert "installed" in result, "pydot status must have 'installed' key"
    assert "version" in result, "pydot status must have 'version' key"
    assert result["installed"] is True, "pydot must be detected as installed (it's a dependency)"
    assert result["version"] is not None, "pydot version must be populated when installed"


def test_networkx_detected():
    """networkx always detected (declared dependency)."""
    from amplifier_module_tool_dot_graph.setup_helper import _check_networkx

    result = _check_networkx()

    assert isinstance(result, dict), "_check_networkx() must return a dict"
    assert "installed" in result, "networkx status must have 'installed' key"
    assert "version" in result, "networkx status must have 'version' key"
    assert result["installed"] is True, "networkx must be detected as installed (it's a dependency)"
    assert result["version"] is not None, "networkx version must be populated when installed"


def test_install_hint_is_nonempty_string():
    """_install_hint() returns useful string."""
    from amplifier_module_tool_dot_graph.setup_helper import _install_hint

    result = _install_hint()

    assert isinstance(result, str), "_install_hint() must return a string"
    assert len(result) > 0, "_install_hint() must return a non-empty string"
    # Should contain something useful (a command or URL)
    assert any(
        keyword in result.lower()
        for keyword in ["brew", "apt", "dnf", "winget", "choco", "graphviz.org", "install"]
    ), f"install hint should contain useful guidance, got: {result!r}"
