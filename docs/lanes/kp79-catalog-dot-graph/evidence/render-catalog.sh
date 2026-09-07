#!/usr/bin/env bash
# Reproduce the delegate agent-catalog measurement in this lane's DONE-NOTE. $0, no LLM call.
#
#   ./render-catalog.sh <path-to-amplifier-bundle-dot-graph-checkout>
#
# Renders the delegate tool's own description -- the string injected into the head of every
# session on every turn -- from a scratch bundle containing ONLY the given checkout plus
# tool-delegate, and prints the byte size of this bundle's slice of the "Available agents:" block.
set -euo pipefail
REPO="$(cd "${1:?usage: render-catalog.sh <repo-checkout>}" && pwd)"
WORK="$(mktemp -d)"; trap 'amplifier bundle remove kp79-scratch >/dev/null 2>&1 || true; rm -rf "$WORK"' EXIT
cat > "$WORK/bundle.md" <<YAML
---
bundle:
  name: kp79-scratch
  version: 0.0.1
  description: Scratch session for rendering the delegate agent catalog.
includes:
  - bundle: $REPO/bundle.md
session:
  raw: true
  orchestrator:
    module: loop-streaming
    source: git+https://github.com/microsoft/amplifier-module-loop-streaming@main
  context:
    module: context-simple
    source: git+https://github.com/microsoft/amplifier-module-context-simple@main
tools:
  - module: tool-delegate
    source: git+https://github.com/microsoft/amplifier-foundation@main#subdirectory=modules/tool-delegate
---
YAML
amplifier bundle add "file://$WORK" --name kp79-scratch >/dev/null
amplifier tool info delegate -b kp79-scratch --format json 2>/dev/null | sed -n '/^{/,$p' | python3 -c '
import json,re,sys
d=json.load(sys.stdin)["config_summary"]["description"]
cat=d[d.index("Available agents:\n")+len("Available agents:\n"):]
s=[m.start() for m in re.finditer(r"(?m)^  - [A-Za-z0-9_.-]+:[A-Za-z0-9_.-]+: ", cat)]
tot=0
for i,x in enumerate(s):
    blk=cat[x:(s[i+1] if i+1<len(s) else len(cat))]
    if blk.startswith("  - dot-graph:"):
        tot+=len(blk.encode()); print(f"{blk.split(chr(58))[1]:<34}{len(blk.encode()):>7}")
print(f"{chr(45)*41}\ndot-graph catalog slice{tot:>18} bytes")
print(f"full catalog{len(cat.encode()):>29} bytes ({len(s)} entries)")
'
