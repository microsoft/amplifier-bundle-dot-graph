# Integration-Mapper Unknowns: Agent Constellation

1. **Synthesizer file read scope** — Does discovery-synthesizer read ALL files in agents/*/ or only specific filenames (findings.md, diagram.dot)? The prompt says "read all agent artifacts" but doesn't enumerate files.

2. **Agent collaboration on unknowns** — Agents write unknowns.md files but no agent reads them. Are unknowns meant to feed back into a future investigation cycle? No mechanism exists for this.

3. **General agents vs discovery agents** — dot-author and diagram-reviewer are not in the discovery pipeline. Are they intended to be used AFTER discovery to create polished versions of the consensus diagrams?

4. **Parallel investigation** — The recipe's `foreach` for investigation topics runs sequentially by default. Does `parallel: true` work for recipe steps? Would parallel investigation cause file system conflicts?
