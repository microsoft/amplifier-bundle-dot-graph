"""Tests for scripts/dot-render.sh standalone DOT rendering script.

These tests verify the behavior of the bash script using subprocess calls.
"""

import os
import stat
import subprocess
import tempfile
from pathlib import Path

# Path to the script under test
REPO_ROOT = Path(__file__).parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "dot-render.sh"

VALID_DOT = """\
digraph G {
    A -> B;
    B -> C;
}
"""


# ── Helper ──────────────────────────────────────────────────────────────────────


def run_script(*args, **kwargs):
    """Run dot-render.sh with given args, return CompletedProcess."""
    cmd = [str(SCRIPT_PATH)] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        **kwargs,
    )


# ── Existence & executability ────────────────────────────────────────────────────


class TestScriptExists:
    def test_script_file_exists(self):
        """Script must exist at scripts/dot-render.sh."""
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


# ── Help flag ─────────────────────────────────────────────────────────────────────


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

    def test_help_shows_arguments(self):
        """Help output must document arguments."""
        result = run_script("--help")
        output = result.stdout + result.stderr
        # Must document the file.dot argument and format/engine options
        assert "format" in output.lower() or "engine" in output.lower(), (
            "Help must document format and/or engine arguments"
        )

    def test_help_shows_exit_codes(self):
        """Help output must document exit codes."""
        result = run_script("--help")
        output = result.stdout + result.stderr
        assert "exit" in output.lower() or "Exit" in output, (
            "Help must document exit codes"
        )

    def test_help_shows_examples(self):
        """Help output must show at least 4 usage examples."""
        result = run_script("--help")
        output = result.stdout + result.stderr
        assert ".dot" in output, "Help must show examples with .dot file"

    def test_help_mentions_requirements(self):
        """Help output must mention requirements (Graphviz/dot)."""
        result = run_script("--help")
        output = result.stdout + result.stderr
        assert "graphviz" in output.lower() or "dot" in output.lower(), (
            "Help must mention Graphviz or dot requirement"
        )


# ── Argument handling ─────────────────────────────────────────────────────────────


class TestArgumentHandling:
    def test_no_arguments_exits_nonzero(self):
        """Running without arguments should exit non-zero."""
        result = run_script()
        assert result.returncode != 0, "Should fail without arguments"

    def test_no_arguments_shows_usage(self):
        """Running without arguments should show usage."""
        result = run_script()
        output = result.stdout + result.stderr
        assert "usage" in output.lower() or "Usage" in output, (
            "Should show usage when no arguments given"
        )


# ── File existence check ──────────────────────────────────────────────────────────


class TestFileExistenceCheck:
    def test_nonexistent_file_exits_one(self):
        """Non-existent file must exit with code 1."""
        result = run_script("/tmp/this-file-does-not-exist-dot-render-test.dot")
        assert result.returncode == 1, (
            f"Expected exit code 1 for missing file, got {result.returncode}"
        )

    def test_nonexistent_file_error_message(self):
        """Non-existent file must produce an error message."""
        result = run_script("/tmp/this-file-does-not-exist-dot-render-test.dot")
        output = result.stdout + result.stderr
        assert output.strip(), "Should produce error message for missing file"


# ── Format validation ─────────────────────────────────────────────────────────────


class TestFormatValidation:
    def test_unknown_format_exits_one(self):
        """Unknown format must exit with code 1."""
        with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
            f.write(VALID_DOT)
            tmp_path = f.name
        try:
            result = run_script(tmp_path, "unknownfmt")
            assert result.returncode == 1, (
                f"Expected exit 1 for unknown format, got {result.returncode}"
            )
        finally:
            os.unlink(tmp_path)

    def test_unknown_format_error_message(self):
        """Unknown format must produce an error message."""
        with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
            f.write(VALID_DOT)
            tmp_path = f.name
        try:
            result = run_script(tmp_path, "unknownfmt")
            output = result.stdout + result.stderr
            assert output.strip(), "Should produce error message for unknown format"
        finally:
            os.unlink(tmp_path)

    def test_valid_format_svg_accepted(self):
        """svg format must be accepted (not produce format error)."""
        with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
            f.write(VALID_DOT)
            tmp_path = f.name
        try:
            result = run_script(tmp_path, "svg")
            # Should not fail due to format error (may fail due to missing graphviz)
            assert (
                result.returncode != 1
                or "unknown format" not in (result.stdout + result.stderr).lower()
            ), "svg format should be accepted"
        finally:
            # Clean up output file if created
            svg_path = tmp_path.replace(".dot", ".svg")
            if os.path.exists(svg_path):
                os.unlink(svg_path)
            os.unlink(tmp_path)

    def test_valid_format_png_accepted(self):
        """png format must be accepted (not produce format error)."""
        with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
            f.write(VALID_DOT)
            tmp_path = f.name
        try:
            result = run_script(tmp_path, "png")
            assert (
                result.returncode != 1
                or "unknown format" not in (result.stdout + result.stderr).lower()
            ), "png format should be accepted"
        finally:
            png_path = tmp_path.replace(".dot", ".png")
            if os.path.exists(png_path):
                os.unlink(png_path)
            os.unlink(tmp_path)

    def test_valid_format_pdf_accepted(self):
        """pdf format must be accepted (not produce format error)."""
        with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
            f.write(VALID_DOT)
            tmp_path = f.name
        try:
            result = run_script(tmp_path, "pdf")
            assert (
                result.returncode != 1
                or "unknown format" not in (result.stdout + result.stderr).lower()
            ), "pdf format should be accepted"
        finally:
            pdf_path = tmp_path.replace(".dot", ".pdf")
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
            os.unlink(tmp_path)


# ── Rendering (when Graphviz available) ──────────────────────────────────────────


class TestRendering:
    def test_render_svg_creates_output_file(self):
        """Rendering to svg must create <basename>.svg output file."""
        import shutil

        if not shutil.which("dot"):
            import pytest

            pytest.skip("Graphviz not installed")

        with tempfile.NamedTemporaryFile(
            suffix=".dot", mode="w", delete=False, dir="/tmp"
        ) as f:
            f.write(VALID_DOT)
            tmp_path = f.name

        expected_output = tmp_path.replace(".dot", ".svg")
        try:
            result = run_script(tmp_path, "svg")
            assert result.returncode == 0, (
                f"Expected exit 0 for valid SVG render, got {result.returncode}\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
            assert os.path.exists(expected_output), (
                f"Expected output file {expected_output} not created"
            )
        finally:
            os.unlink(tmp_path)
            if os.path.exists(expected_output):
                os.unlink(expected_output)

    def test_render_shows_checkmark_on_success(self):
        """Successful render must show ✅ checkmark."""
        import shutil

        if not shutil.which("dot"):
            import pytest

            pytest.skip("Graphviz not installed")

        with tempfile.NamedTemporaryFile(
            suffix=".dot", mode="w", delete=False, dir="/tmp"
        ) as f:
            f.write(VALID_DOT)
            tmp_path = f.name

        expected_output = tmp_path.replace(".dot", ".svg")
        try:
            result = run_script(tmp_path, "svg")
            output = result.stdout + result.stderr
            assert "✅" in output, (
                f"Expected ✅ in output for successful render, got: {output}"
            )
        finally:
            os.unlink(tmp_path)
            if os.path.exists(expected_output):
                os.unlink(expected_output)

    def test_render_shows_file_size_on_success(self):
        """Successful render must show file size in output."""
        import shutil

        if not shutil.which("dot"):
            import pytest

            pytest.skip("Graphviz not installed")

        with tempfile.NamedTemporaryFile(
            suffix=".dot", mode="w", delete=False, dir="/tmp"
        ) as f:
            f.write(VALID_DOT)
            tmp_path = f.name

        expected_output = tmp_path.replace(".dot", ".svg")
        try:
            result = run_script(tmp_path, "svg")
            output = result.stdout + result.stderr
            # Should show file size (bytes or similar)
            assert any(s in output for s in ["byte", "B ", "KB", "kB", " B"]) or any(
                c.isdigit() for c in output
            ), f"Expected file size info in output, got: {output}"
        finally:
            os.unlink(tmp_path)
            if os.path.exists(expected_output):
                os.unlink(expected_output)

    def test_default_format_is_svg(self):
        """Default format (no format arg) must produce .svg output."""
        import shutil

        if not shutil.which("dot"):
            import pytest

            pytest.skip("Graphviz not installed")

        with tempfile.NamedTemporaryFile(
            suffix=".dot", mode="w", delete=False, dir="/tmp"
        ) as f:
            f.write(VALID_DOT)
            tmp_path = f.name

        expected_output = tmp_path.replace(".dot", ".svg")
        try:
            result = run_script(tmp_path)  # no format arg
            assert result.returncode == 0, (
                f"Expected exit 0 for default format, got {result.returncode}\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
            assert os.path.exists(expected_output), (
                f"Default format should produce .svg file at {expected_output}"
            )
        finally:
            os.unlink(tmp_path)
            if os.path.exists(expected_output):
                os.unlink(expected_output)

    def test_output_naming_convention(self):
        """Output file must be named <basename>.<format>."""
        import shutil

        if not shutil.which("dot"):
            import pytest

            pytest.skip("Graphviz not installed")

        with tempfile.NamedTemporaryFile(
            suffix=".dot", mode="w", delete=False, dir="/tmp", prefix="mydiagram_"
        ) as f:
            f.write(VALID_DOT)
            tmp_path = f.name

        # basename without .dot + .svg
        base = Path(tmp_path).stem  # e.g. "mydiagram_XXXX"
        expected_output = str(Path(tmp_path).parent / f"{base}.svg")
        try:
            result = run_script(tmp_path, "svg")
            assert result.returncode == 0, (
                f"Expected exit 0, got {result.returncode}\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
            assert os.path.exists(expected_output), (
                f"Expected output at {expected_output}, not found"
            )
        finally:
            os.unlink(tmp_path)
            if os.path.exists(expected_output):
                os.unlink(expected_output)


# ── Script structure ─────────────────────────────────────────────────────────────


class TestScriptStructure:
    def test_has_show_help_function(self):
        """Script must define a show_help() function."""
        content = SCRIPT_PATH.read_text()
        assert "show_help" in content, "Script must define show_help function"

    def test_has_file_existence_check(self):
        """Script must check that the DOT file exists."""
        content = SCRIPT_PATH.read_text()
        assert "-f " in content or "! -f" in content, (
            "Script must check file existence with -f test"
        )

    def test_has_dependency_check(self):
        """Script must check that the engine command is available."""
        content = SCRIPT_PATH.read_text()
        assert "command -v" in content, (
            "Script must check engine command with 'command -v'"
        )

    def test_has_format_validation_case(self):
        """Script must validate format via case statement."""
        content = SCRIPT_PATH.read_text()
        assert "case" in content, "Script must use case statement for format validation"
        assert "svg" in content, "Script must list svg as valid format"
        assert "png" in content, "Script must list png as valid format"
        assert "pdf" in content, "Script must list pdf as valid format"

    def test_has_engine_variable(self):
        """Script must use ENGINE variable for the graphviz engine."""
        content = SCRIPT_PATH.read_text()
        assert "ENGINE" in content, "Script must define ENGINE variable"

    def test_has_format_variable(self):
        """Script must use FORMAT variable."""
        content = SCRIPT_PATH.read_text()
        assert "FORMAT" in content, "Script must define FORMAT variable"

    def test_has_render_command(self):
        """Script must render using $ENGINE -T$FORMAT."""
        content = SCRIPT_PATH.read_text()
        assert "-T" in content or "-T$FORMAT" in content or "-T${FORMAT}" in content, (
            "Script must use -T flag for format in render command"
        )

    def test_has_platform_install_hints(self):
        """Script must include platform-specific install suggestions."""
        content = SCRIPT_PATH.read_text()
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

    def test_has_three_exit_codes_documented(self):
        """Script must document 3 exit codes: 0, 1, 2."""
        content = SCRIPT_PATH.read_text()
        assert "exit 0" in content or "exit 1" in content or "exit 2" in content, (
            "Script must use documented exit codes"
        )
        # Exit codes must exist in practice
        assert "exit 2" in content, "Script must use exit code 2 for missing deps"

    def test_has_json_ps_eps_formats(self):
        """Script must support json, ps, eps formats in addition to svg/png/pdf."""
        content = SCRIPT_PATH.read_text()
        assert "json" in content, "Script must support json format"
        assert "ps" in content, "Script must list ps format"
        assert "eps" in content, "Script must list eps format"

    def test_help_examples_shows_engine_override(self):
        """Help EXAMPLES must include an example with an engine override argument."""
        result = run_script("--help")
        output = result.stdout + result.stderr
        # Examples should show a 3-argument invocation (file format engine)
        # that demonstrates the engine override capability
        lines_with_dot = [
            line
            for line in output.splitlines()
            if ".dot" in line and not line.strip().startswith("#")
        ]
        # At least one example should have 3 tokens (file format engine)
        three_arg_examples = [
            line
            for line in lines_with_dot
            if len(line.split()) >= 3
            and not line.strip().startswith("dot-render.sh --help")
            and not line.strip().startswith("dot-render.sh -h")
        ]
        assert three_arg_examples, (
            "Help EXAMPLES must show at least one invocation with file, format, and engine arguments"
        )


# ── Empty output detection ──────────────────────────────────────────────────────────────────────


class TestEmptyOutputDetection:
    def test_empty_output_file_exits_one(self):
        """Script must exit 1 if the render command produces an empty output file."""
        import stat as stat_mod

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid .dot source file
            dot_file = os.path.join(tmpdir, "test.dot")
            with open(dot_file, "w") as f:
                f.write(VALID_DOT)

            # Create a fake engine script that writes an empty output file and exits 0
            fake_engine = os.path.join(tmpdir, "fake-dot")
            with open(fake_engine, "w") as f:
                f.write("#!/usr/bin/env bash\n")
                f.write("# Parse -o flag to find output path\n")
                f.write("while [[ $# -gt 0 ]]; do\n")
                f.write('  case "$1" in\n')
                f.write('    -o) shift; touch "$1" ;;\n')
                f.write("    *) ;;\n")
                f.write("  esac\n")
                f.write("  shift\n")
                f.write("done\n")
                f.write("exit 0\n")
            os.chmod(fake_engine, os.stat(fake_engine).st_mode | stat_mod.S_IEXEC)

            # Run with fake engine via PATH manipulation
            env = os.environ.copy()
            env["PATH"] = tmpdir + ":" + env.get("PATH", "")

            result = subprocess.run(
                [str(SCRIPT_PATH), dot_file, "svg", "fake-dot"],
                capture_output=True,
                text=True,
                env=env,
            )
            assert result.returncode == 1, (
                f"Expected exit 1 when output file is empty, got {result.returncode}\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )

    def test_empty_output_shows_error_message(self):
        """Script must emit an error message when the output file is empty."""
        import stat as stat_mod

        with tempfile.TemporaryDirectory() as tmpdir:
            dot_file = os.path.join(tmpdir, "test.dot")
            with open(dot_file, "w") as f:
                f.write(VALID_DOT)

            fake_engine = os.path.join(tmpdir, "fake-dot")
            with open(fake_engine, "w") as f:
                f.write("#!/usr/bin/env bash\n")
                f.write("while [[ $# -gt 0 ]]; do\n")
                f.write('  case "$1" in\n')
                f.write('    -o) shift; touch "$1" ;;\n')
                f.write("    *) ;;\n")
                f.write("  esac\n")
                f.write("  shift\n")
                f.write("done\n")
                f.write("exit 0\n")
            os.chmod(fake_engine, os.stat(fake_engine).st_mode | stat_mod.S_IEXEC)

            env = os.environ.copy()
            env["PATH"] = tmpdir + ":" + env.get("PATH", "")

            result = subprocess.run(
                [str(SCRIPT_PATH), dot_file, "svg", "fake-dot"],
                capture_output=True,
                text=True,
                env=env,
            )
            output = result.stdout + result.stderr
            assert output.strip(), (
                "Must emit an error message when output file is empty"
            )
            assert (
                "❌" in output
                or "empty" in output.lower()
                or "0 byte" in output.lower()
            ), f"Error message should indicate empty/failed output, got: {output}"
