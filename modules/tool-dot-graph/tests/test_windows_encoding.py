"""Windows-compatibility tests for tool-dot-graph (UTF-8 in temp file + graphviz).

render_dot / validate_dot write the DOT to a temp file for graphviz and read
graphviz stderr back. Both were text-mode with no `encoding=`, so on Windows the
locale codepage (cp1252) was used:
- writing a DOT with non-ASCII labels (people names, CJK, Cyrillic) ->
  UnicodeEncodeError before graphviz even runs;
- decoding graphviz stderr (which echoes the offending DOT source, incl. the
  non-ASCII label) -> UnicodeDecodeError for any byte undefined in cp1252.

The render operation had NO enclosing try/except in the tool, so this crashed
the whole tool call. Fix: pin encoding="utf-8" (+ errors="replace" on the
subprocess reads) everywhere, matching the module's other file I/O.

The source-inspection tests have real teeth on Linux (the un-fixed source has
bare text=True temp writes / subprocess reads); the render roundtrip has teeth
on Windows.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest
from amplifier_module_tool_dot_graph.render import render_dot
from amplifier_module_tool_dot_graph.validate import validate_dot

_MOD = Path(__file__).resolve().parents[1] / "amplifier_module_tool_dot_graph"
_FILES = ["render.py", "validate.py", "setup_helper.py", "assemble.py"]

# A DOT whose node label carries non-ASCII incl. Cyrillic 'э' (U+044D -> UTF-8
# 0xD1 0x8D; 0x8D is undefined in cp1252, so a cp1252 decode/encode raises).
_NONASCII_DOT = 'digraph G { a [label="caf\u00e9 \u65e5\u672c\u8a9e \u044d"]; a -> b; }'


def _dumps_balanced_calls(src: str, name: str):
    """Yield the full argument text of every `name(...)` call (paren-depth aware)."""
    for m in re.finditer(re.escape(name) + r"\(", src):
        start = m.end() - 1
        depth = 0
        for i in range(start, len(src)):
            if src[i] == "(":
                depth += 1
            elif src[i] == ")":
                depth -= 1
                if depth == 0:
                    yield src[start + 1 : i]
                    break


def test_subprocess_and_tempfile_pin_utf8():
    """Teeth on Linux: un-fixed source has bare text=True / temp writes."""
    offenders = []
    for rel in _FILES:
        src = (_MOD / rel).read_text(encoding="utf-8")
        for call in _dumps_balanced_calls(src, "subprocess.run"):
            if "text=True" in call and "encoding=" not in call:
                offenders.append(f"{rel}:subprocess.run")
        for call in _dumps_balanced_calls(src, "NamedTemporaryFile"):
            if 'mode="w"' in call and "encoding=" not in call:
                offenders.append(f"{rel}:NamedTemporaryFile(mode='w')")
    assert not offenders, (
        f"text-mode subprocess/tempfile without encoding= in: {sorted(set(offenders))}"
    )


def test_assemble_read_text_pins_utf8():
    src = (_MOD / "assemble.py").read_text(encoding="utf-8")
    assert ".read_text()" not in src, (
        "bare read_text() (no encoding) still present in assemble.py"
    )


@pytest.mark.skipif(shutil.which("dot") is None, reason="graphviz not installed")
def test_render_nonascii_dot_does_not_crash():
    """Teeth on Windows: the un-fixed temp write / stderr decode crashed here."""
    result = render_dot(_NONASCII_DOT, output_format="svg")
    # Must return a dict (success or a clean error), never raise Unicode*Error.
    assert isinstance(result, dict)
    assert result.get("success") is True, result


@pytest.mark.skipif(shutil.which("dot") is None, reason="graphviz not installed")
def test_validate_nonascii_dot_does_not_crash():
    result = validate_dot(_NONASCII_DOT)
    assert isinstance(result, dict)
    assert "valid" in result
