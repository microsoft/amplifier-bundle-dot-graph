# Integration-Mapper: Knowledge and Behavior Layer

## Cross-Boundary Integration Points

### Boundary 1: Bundle Entry (bundle.md) ↔ Behavior Chain
`bundle.md` includes `dot-graph:behaviors/dot-graph` which transitively includes:
- dot-core (tools + 2 general agents)
- dot-discovery (5 discovery agents + context)
Three levels of composition. The bundle.md consumer gets the full set without knowing the layers.

### Boundary 2: dot-core.yaml ↔ External Tool Modules
- `tool-dot-graph` — sourced from GitHub subdirectory (`modules/tool-dot-graph`)
- `tool-skills` — external module (`amplifier-module-tool-skills`), configured with 5 skill URLs
Both are external dependencies referenced by URL. If GitHub is unreachable, module loading fails.

### Boundary 3: Skills ↔ Agents (knowledge injection)
Skills are loaded lazily via `load_skill` tool or eagerly via tool-skills module.
Discovery agents reference skills via `@dot-graph:skills/*` in their prompts.
The bundle registers all 5 skills under the `dot-graph` namespace so they're accessible.
**Effect:** Agent behavior (diagram quality, analysis depth) depends on whether skills are loaded.

### Boundary 4: dot-discovery.yaml ↔ dot-core.yaml (inheritance)
dot-discovery INCLUDES dot-core. This means a session with dot-discovery:
- Gets all of dot-core (tool-dot-graph tool + tool-skills + dot-author + diagram-reviewer)
- PLUS 5 discovery agents
- PLUS discovery-awareness.md context
**Risk:** Double-inclusion if a consumer includes both dot-core and dot-discovery directly. Behavior specification says "includes" but the deduplication mechanism is unknown.

### Boundary 5: Context Files ↔ Agent Sessions
- `dot-awareness.md`: always included via bundle.md (every session using this bundle)
- `discovery-awareness.md`: only included when using dot-discovery behavior
Context files provide "background knowledge" — they're included verbatim in the session context.
This means every agent in a dot-graph bundle session has DOT graph awareness by default.

## Composition Effects

**Layered knowledge amplification:** Skills + behaviors + context form a knowledge stack:
1. Context (always-on background awareness)
2. Skills (on-demand deep references)
3. Agent definitions (role + methodology)
4. Tool (programmatic capability)
Each layer amplifies the others. A dot-author with no skills is less capable than with 5 skills.

**Implicit coupling via behavior version:** All behaviors are version 0.2.0 but they reference each other by path (not version). If dot-core changes, dot-discovery implicitly changes because it includes dot-core by path.
