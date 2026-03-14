"""Environment detection for tool-dot-graph dependencies.

Detects availability of graphviz CLI, pydot, and networkx.
Returns structured status dicts for use by validate.py and render.py.
"""

import platform
import shutil
import subprocess


def check_environment() -> dict:
    """Top-level environment check.

    Returns:
        dict with keys: graphviz, pydot, networkx — each containing
        availability status and version info.
    """
    return {
        "graphviz": _check_graphviz(),
        "pydot": _check_pydot(),
        "networkx": _check_networkx(),
    }


def _check_graphviz() -> dict:
    """Detect graphviz CLI installation, version, and available engines.

    Returns:
        When installed: {installed: True, version: str, engines: list[str]}
        When not installed: {installed: False, version: None, engines: [], install_hint: str}
    """
    dot_path = shutil.which("dot")

    if dot_path is None:
        return {
            "installed": False,
            "version": None,
            "engines": [],
            "install_hint": _install_hint(),
        }

    # Graphviz found — get version (dot -V prints to stderr)
    version = None
    try:
        result = subprocess.run(
            ["dot", "-V"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # Version appears in stderr: "dot - graphviz version X.Y.Z (N)"
        stderr_output = result.stderr.strip()
        if stderr_output:
            version = stderr_output
    except (subprocess.TimeoutExpired, OSError):
        pass

    # Check which engines are available
    engine_names = ["dot", "neato", "fdp", "sfdp", "twopi", "circo"]
    engines = [name for name in engine_names if shutil.which(name) is not None]

    return {
        "installed": True,
        "version": version,
        "engines": engines,
    }


def _check_pydot() -> dict:
    """Detect pydot Python package.

    Returns:
        {installed: bool, version: str|None}
    """
    try:
        import pydot

        version = getattr(pydot, "__version__", None)
        return {"installed": True, "version": version}
    except ImportError:
        return {"installed": False, "version": None}


def _check_networkx() -> dict:
    """Detect networkx Python package.

    Returns:
        {installed: bool, version: str|None}
    """
    try:
        import networkx

        version = getattr(networkx, "__version__", None)
        return {"installed": True, "version": version}
    except ImportError:
        return {"installed": False, "version": None}


def _install_hint() -> str:
    """Platform-appropriate install guidance for Graphviz.

    Returns:
        Human-readable installation instructions tailored to the current OS.
    """
    system = platform.system()

    if system == "Darwin":
        return "Install Graphviz via Homebrew: brew install graphviz"
    elif system == "Linux":
        return (
            "Install Graphviz via package manager: "
            "sudo apt install graphviz  (Debian/Ubuntu)  "
            "or  sudo dnf install graphviz  (Fedora/RHEL)"
        )
    elif system == "Windows":
        return (
            "Install Graphviz via winget: winget install graphviz  "
            "or  choco install graphviz  (Chocolatey)  "
            "or download from https://graphviz.org/download/"
        )
    else:
        return "Install Graphviz from https://graphviz.org/download/"
