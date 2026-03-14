#!/usr/bin/env bash
# dot-render.sh — Standalone DOT file renderer
#
# Usage:
#   dot-render.sh <file.dot> [format] [engine]
#   dot-render.sh --help
#
# Arguments:
#   file.dot   Required. Path to the DOT source file to render.
#   format     Output format. Defaults to svg.
#              Supported: svg, png, pdf, json, ps, eps
#   engine     Graphviz layout engine. Defaults to dot.
#              Others: neato, fdp, sfdp, twopi, circo
#
# Output naming:
#   <basename>.<format>  — written to the same directory as the input file.
#   Example: diagram.dot → diagram.svg
#
# Exit codes:
#   0  Success — output file created
#   1  Error — file not found, unknown format, or render failure
#   2  Missing dependency — Graphviz engine not installed

set -euo pipefail

# ── Help ──────────────────────────────────────────────────────────────────────────

show_help() {
    cat <<'EOF'
dot-render.sh — Standalone DOT file renderer

USAGE
    dot-render.sh <file.dot> [format] [engine]
    dot-render.sh --help | -h

ARGUMENTS
    file.dot   Required. Path to the Graphviz DOT source file.
    format     Output format (default: svg).
               Supported: svg, png, pdf, json, ps, eps
    engine     Graphviz layout engine (default: dot).
               Alternatives: neato, fdp, sfdp, twopi, circo

OUTPUT
    Output is written to <basename>.<format> in the same directory as the
    input file.  For example:
        diagrams/architecture.dot  →  diagrams/architecture.svg

EXIT CODES
    0   Success — output file created
    1   Error — file not found, unknown format, or render failure
    2   Missing dependency — required Graphviz engine not on PATH

REQUIREMENTS
    Graphviz must be installed and the engine command (default: dot) must be
    available on PATH.

    Install Graphviz:
      macOS:    brew install graphviz
      Ubuntu:   sudo apt-get install graphviz
      Fedora:   sudo dnf install graphviz
      Arch:     sudo pacman -S graphviz
      Windows:  winget install graphviz   OR   choco install graphviz

EXAMPLES
    dot-render.sh diagram.dot
    dot-render.sh diagram.dot png
    dot-render.sh diagram.dot pdf neato
    dot-render.sh --help
EOF
}

# ── Argument parsing ──────────────────────────────────────────────────────────────

if [[ $# -eq 0 ]]; then
    echo "Usage: dot-render.sh <file.dot> [format] [engine]  |  dot-render.sh --help" >&2
    exit 1
fi

if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
    exit 0
fi

DOT_FILE="$1"
FORMAT="${2:-svg}"
ENGINE="${3:-dot}"

# ── Check 1: File exists ──────────────────────────────────────────────────────────

if [[ ! -f "$DOT_FILE" ]]; then
    echo "❌  File not found: $DOT_FILE" >&2
    exit 1
fi

# ── Check 2: Engine command available ────────────────────────────────────────────

if ! command -v "$ENGINE" &>/dev/null; then
    echo "❌  Graphviz engine '$ENGINE' not found on PATH." >&2
    echo "" >&2
    echo "Install Graphviz:" >&2
    echo "  macOS:    brew install graphviz" >&2
    echo "  Ubuntu:   sudo apt-get install graphviz" >&2
    echo "  Fedora:   sudo dnf install graphviz" >&2
    echo "  Arch:     sudo pacman -S graphviz" >&2
    echo "  Windows:  winget install graphviz   OR   choco install graphviz" >&2
    exit 2
fi

# ── Check 3: Validate format ──────────────────────────────────────────────────────

case "$FORMAT" in
    svg|png|pdf|json|ps|eps)
        ;;
    *)
        echo "❌  Unknown format: '$FORMAT'" >&2
        echo "    Supported formats: svg, png, pdf, json, ps, eps" >&2
        exit 1
        ;;
esac

# ── Compute output path ───────────────────────────────────────────────────────────

DIR="$(dirname "$DOT_FILE")"
BASE="$(basename "$DOT_FILE" .dot)"
OUTPUT="${DIR}/${BASE}.${FORMAT}"

# ── Render ────────────────────────────────────────────────────────────────────────

echo "Rendering: $DOT_FILE  →  $OUTPUT"
echo "  engine: $ENGINE   format: $FORMAT"
echo ""

if "$ENGINE" -T"$FORMAT" "$DOT_FILE" -o "$OUTPUT" 2>&1; then
    SIZE=$(wc -c < "$OUTPUT")
    if [[ "$SIZE" -eq 0 ]]; then
        echo "❌  Render produced an empty file: $OUTPUT" >&2
        exit 1
    fi
    echo "✅  Rendered successfully: $OUTPUT  (${SIZE} bytes)"
else
    echo "❌  Render failed: $ENGINE -T$FORMAT $DOT_FILE -o $OUTPUT" >&2
    exit 1
fi

exit 0
