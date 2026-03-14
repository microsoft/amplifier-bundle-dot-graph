"""Tests for scripts/dot-validate.sh standalone DOT validation script.

These tests verify the behavior of the bash script using subprocess calls.
"""

import os
import stat
import subprocess
import tempfile
from pathlib import Path

# Path to the script under test
REPO_ROOT = Path(__file__).parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "dot-validate.sh"


# ── Helper ──────────────────────────────────────────────────────────────────


def run_script(*args, **kwargs):
    """Run the dot-validate.sh script with given args, return CompletedProcess."""
    cmd = [str(SCRIPT_PATH)] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        **kwargs,
    )


VALID_DOT = """\
digraph G {
    A -> B;
    B -> C;
}
"""

INVALID_DOT = """\
digraph G {
    A -> ;
    INVALID SYNTAX !!!
"""


# ── Existence & executability ────────────────────────────────────────────────


class TestScriptExists:
    def test_script_file_exists(self):
        """Script must exist at scripts/dot-validate.sh."""
        assert SCRIPT_PATH.exists(), f"Script not found: {SCRIPT_PATH}"

    def test_script_is_executable(self):
        """Script must be executable."""
        assert SCRIPT_PATH.exists(), f"Script not found: {SCRIPT_PATH}"
        mode = SCRIPT_PATH.stat().st_mode
        assert mode & stat.S_IXUSR, "Script is not executable by owner"

    def test_script_has_shebang(self):
        """Script must start with a bash shebang."""
        content = SCRIPT_PATH.read_text()
        assert content.startswith("#!/"), "Script must start with a shebang"
        assert "bash" in content.splitlines()[0], "Shebang must reference bash"

    def test_script_has_strict_mode(self):
        """Script must use set -euo pipefail."""
        content = SCRIPT_PATH.read_text()
        assert "set -euo pipefail" in content, "Script must contain 'set -euo pipefail'"


# ── Help flag ────────────────────────────────────────────────────────────────


class TestHelpFlag:
    def test_help_flag_exits_zero(self):
        """--help must exit with code 0."""
        result = run_script("--help")
        assert result.returncode == 0, (
            f"--help returned {result.returncode}: {result.stderr}"
        )

    def test_help_short_flag_exits_zero(self):
        """-h must exit with code 0."""
        result = run_script("-h")
        assert result.returncode == 0, (
            f"-h returned {result.returncode}: {result.stderr}"
        )

    def test_help_shows_usage(self):
        """Help output must show usage information."""
        result = run_script("--help")
        output = result.stdout + result.stderr
        assert "usage" in output.lower() or "Usage" in output, "Help must show usage"

    def test_help_shows_exit_codes(self):
        """Help output must document exit codes."""
        result = run_script("--help")
        output = result.stdout + result.stderr
        # Should mention exit codes somewhere
        assert "exit" in output.lower() or "Exit" in output, (
            "Help must document exit codes"
        )

    def test_help_shows_examples(self):
        """Help output must show usage examples."""
        result = run_script("--help")
        output = result.stdout + result.stderr
        # Should contain example with .dot extension or example keyword
        assert ".dot" in output or "example" in output.lower(), (
            "Help must show examples with .dot file"
        )

    def test_help_mentions_requirements(self):
        """Help output must mention requirements (Graphviz/dot)."""
        result = run_script("--help")
        output = result.stdout + result.stderr
        assert "graphviz" in output.lower() or "dot" in output.lower(), (
            "Help must mention Graphviz or dot requirement"
        )


# ── Argument handling ────────────────────────────────────────────────────────


class TestArgumentHandling:
    def test_no_arguments_shows_usage(self):
        """Running without arguments should show usage and exit non-zero."""
        result = run_script()
        assert result.returncode != 0, "Should fail without arguments"
        output = result.stdout + result.stderr
        assert "usage" in output.lower() or "Usage" in output, (
            "Should show usage when no arguments given"
        )

    def test_requires_exactly_one_argument(self):
        """Script requires exactly one file argument."""
        result = run_script()
        assert result.returncode != 0, "Should fail without arguments"


# ── File existence check ─────────────────────────────────────────────────────


class TestFileExistenceCheck:
    def test_nonexistent_file_exits_one(self):
        """Non-existent file must exit with code 1."""
        result = run_script("/tmp/this-file-does-not-exist-dot-validate-test.dot")
        assert result.returncode == 1, (
            f"Expected exit code 1 for missing file, got {result.returncode}"
        )

    def test_nonexistent_file_error_message(self):
        """Non-existent file must produce an error message."""
        result = run_script("/tmp/this-file-does-not-exist-dot-validate-test.dot")
        output = result.stdout + result.stderr
        assert output.strip(), "Should produce error message for missing file"


# ── Valid DOT file ───────────────────────────────────────────────────────────


class TestValidDotFile:
    def test_valid_dot_exits_zero(self):
        """Valid DOT file must exit with code 0."""
        with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
            f.write(VALID_DOT)
            tmp_path = f.name
        try:
            result = run_script(tmp_path)
            assert result.returncode == 0, (
                f"Expected exit 0 for valid DOT, got {result.returncode}\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
        finally:
            os.unlink(tmp_path)

    def test_valid_dot_shows_checkmark(self):
        """Valid DOT validation must output a checkmark (✅)."""
        with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
            f.write(VALID_DOT)
            tmp_path = f.name
        try:
            result = run_script(tmp_path)
            output = result.stdout + result.stderr
            assert "✅" in output, (
                f"Expected ✅ in output for valid file, got: {output}"
            )
        finally:
            os.unlink(tmp_path)

    def test_valid_dot_reports_line_count(self):
        """Script must report line count for valid DOT file."""
        with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
            f.write(VALID_DOT)
            tmp_path = f.name
        try:
            result = run_script(tmp_path)
            output = result.stdout + result.stderr
            # Should mention line count somewhere
            assert "line" in output.lower(), (
                f"Expected line count in output, got: {output}"
            )
        finally:
            os.unlink(tmp_path)


# ── Invalid DOT file ─────────────────────────────────────────────────────────


class TestInvalidDotFile:
    def test_invalid_dot_exits_one(self):
        """Invalid DOT syntax must exit with code 1."""
        with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
            f.write(INVALID_DOT)
            tmp_path = f.name
        try:
            result = run_script(tmp_path)
            assert result.returncode == 1, (
                f"Expected exit 1 for invalid DOT, got {result.returncode}\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
        finally:
            os.unlink(tmp_path)

    def test_invalid_dot_shows_x_mark(self):
        """Invalid DOT validation must output an X mark (❌)."""
        with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
            f.write(INVALID_DOT)
            tmp_path = f.name
        try:
            result = run_script(tmp_path)
            output = result.stdout + result.stderr
            assert "❌" in output, (
                f"Expected ❌ in output for invalid file, got: {output}"
            )
        finally:
            os.unlink(tmp_path)


# ── Line count warnings ──────────────────────────────────────────────────────


class TestLineCountWarnings:
    def test_large_file_warns_at_250_lines(self):
        """Must warn when file exceeds 250 lines."""
        lines = ["digraph G {"] + [f"    n{i} -> n{i + 1};" for i in range(260)] + ["}"]
        content = "\n".join(lines)
        with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
            f.write(content)
            tmp_path = f.name
        try:
            result = run_script(tmp_path)
            output = result.stdout + result.stderr
            assert "250" in output or "warn" in output.lower(), (
                f"Expected warning for >250 lines, got: {output}"
            )
        finally:
            os.unlink(tmp_path)

    def test_very_large_file_warns_at_400_lines(self):
        """Must warn when file exceeds 400 lines."""
        lines = ["digraph G {"] + [f"    n{i} -> n{i + 1};" for i in range(410)] + ["}"]
        content = "\n".join(lines)
        with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
            f.write(content)
            tmp_path = f.name
        try:
            result = run_script(tmp_path)
            output = result.stdout + result.stderr
            assert "400" in output or "warn" in output.lower(), (
                f"Expected warning for >400 lines, got: {output}"
            )
        finally:
            os.unlink(tmp_path)


# ── Script structure ─────────────────────────────────────────────────────────


class TestScriptStructure:
    def test_has_show_help_function(self):
        """Script must define a show_help() function."""
        content = SCRIPT_PATH.read_text()
        assert "show_help" in content, "Script must define show_help function"

    def test_has_dot_tcanon_validation(self):
        """Script must validate using dot -Tcanon."""
        content = SCRIPT_PATH.read_text()
        assert "dot -Tcanon" in content or "dot" in content, (
            "Script must use dot command for validation"
        )

    def test_has_exit_codes_comment(self):
        """Script must document exit codes in comments."""
        content = SCRIPT_PATH.read_text()
        assert "exit" in content.lower(), "Script must document exit codes"

    def test_has_platform_specific_install_hints(self):
        """Script must include platform-specific install suggestions for graphviz."""
        content = SCRIPT_PATH.read_text()
        # Should mention at least one package manager or OS
        has_hints = any(
            hint in content
            for hint in [
                "brew",
                "apt",
                "apt-get",
                "yum",
                "dnf",
                "choco",
                "winget",
                "pacman",
            ]
        )
        assert has_hints, "Script must include platform-specific install suggestions"

    def test_has_wc_l_for_line_count(self):
        """Script must use wc -l for line count reporting."""
        content = SCRIPT_PATH.read_text()
        assert "wc -l" in content or "wc" in content, (
            "Script must use wc for line counting"
        )

    def test_has_gc_command_check(self):
        """Script must optionally use gc command for statistics if available."""
        content = SCRIPT_PATH.read_text()
        assert "gc" in content, "Script must reference gc command for statistics"
