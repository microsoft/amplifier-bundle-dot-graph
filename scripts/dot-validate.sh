#!/usr/bin/env bash
# dot-validate.sh — Standalone DOT file syntax validator
#
# Usage:
#   dot-validate.sh <file.dot>
#   dot-validate.sh --help
#
# Checks performed:
#   1. File exists — the specified path resolves to a readable file
#   2. Graphviz available — the `dot` command is on PATH
#   3. DOT syntax valid — parses via `dot -Tcanon`; reports basic stats
#
# Exit codes:
#   0  Valid DOT file
#   1  Invalid or missing file (or DOT syntax error)
#   2  Missing dependency (Graphviz not installed)

set -euo pipefail

# ── Help ─────────────────────────────────────────────────────────────────────

show_help() {
    cat <<'EOF'
dot-validate.sh — Standalone DOT file syntax validator

USAGE
    dot-validate.sh <file.dot>
    dot-validate.sh --help | -h

DESCRIPTION
    Validates a Graphviz DOT file for syntax correctness and reports basic
    structural statistics.

CHECKS
    1. File exists     — verifies the path resolves to a readable file
    2. Graphviz available — confirms the `dot` command is on PATH
    3. DOT syntax valid — parses via `dot -Tcanon`; also reports line count
                          and, if `gc` is available, node/edge counts

EXIT CODES
    0   Valid DOT syntax
    1   Invalid file path or DOT syntax error
    2   Missing dependency (Graphviz / dot not installed)

REQUIREMENTS
    Graphviz must be installed and the `dot` command available on PATH.

    Install Graphviz:
      macOS:    brew install graphviz
      Ubuntu:   sudo apt-get install graphviz
      Fedora:   sudo dnf install graphviz
      Arch:     sudo pacman -S graphviz
      Windows:  winget install graphviz   OR   choco install graphviz

EXAMPLES
    dot-validate.sh diagram.dot
    dot-validate.sh path/to/architecture.dot
    dot-validate.sh --help
EOF
}

# ── Argument parsing ──────────────────────────────────────────────────────────

if [[ $# -eq 0 ]]; then
    echo "Usage: dot-validate.sh <file.dot>  |  dot-validate.sh --help" >&2
    exit 1
fi

if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
    exit 0
fi

if [[ $# -ne 1 ]]; then
    echo "Error: exactly one file argument required." >&2
    echo "Usage: dot-validate.sh <file.dot>  |  dot-validate.sh --help" >&2
    exit 1
fi

DOT_FILE="$1"

# ── Check 1: File exists ──────────────────────────────────────────────────────

if [[ ! -f "$DOT_FILE" ]]; then
    echo "❌  File not found: $DOT_FILE" >&2
    exit 1
fi

# ── Check 2: Graphviz available ───────────────────────────────────────────────

if ! command -v dot &>/dev/null; then
    echo "❌  Graphviz 'dot' command not found on PATH." >&2
    echo "" >&2
    echo "Install Graphviz:" >&2
    echo "  macOS:    brew install graphviz" >&2
    echo "  Ubuntu:   sudo apt-get install graphviz" >&2
    echo "  Fedora:   sudo dnf install graphviz" >&2
    echo "  Arch:     sudo pacman -S graphviz" >&2
    echo "  Windows:  winget install graphviz   OR   choco install graphviz" >&2
    exit 2
fi

# ── Check 3: DOT syntax validation ───────────────────────────────────────────

echo "Validating: $DOT_FILE"
echo ""

if dot_errors=$(dot -Tcanon "$DOT_FILE" 2>&1 >/dev/null); then
    echo "✅  DOT syntax valid"
    syntax_ok=true
else
    echo "❌  DOT syntax error:"
    echo "$dot_errors" | sed 's/^/    /'
    syntax_ok=false
fi

# ── Line count reporting ──────────────────────────────────────────────────────

line_count=$(wc -l < "$DOT_FILE")
echo ""
echo "Lines: $line_count"

if [[ "$line_count" -gt 400 ]]; then
    echo "⚠️   Warning: file exceeds 400 lines — consider splitting into subgraphs or separate files"
elif [[ "$line_count" -gt 250 ]]; then
    echo "⚠️   Warning: file exceeds 250 lines — diagram may be getting complex"
fi

# ── Optional: gc statistics ──────────────────────────────────────────────────

if command -v gc &>/dev/null && [[ "$syntax_ok" == "true" ]]; then
    echo ""
    echo "Graph statistics (gc):"
    gc "$DOT_FILE" 2>/dev/null | sed 's/^/  /' || true
fi

# ── Final exit ────────────────────────────────────────────────────────────────

if [[ "$syntax_ok" != "true" ]]; then
    exit 1
fi

exit 0
