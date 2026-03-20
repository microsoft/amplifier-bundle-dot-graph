# Level Synthesis: amplifier/context

**Directory:** `/home/bkrabach/dev/dot-graph-bundle/amplifier/context`  
**Level slug:** `context`  
**Fidelity tier:** standard  
**Child directories synthesized:** none (leaf directory)

---

## Files and Symbols at This Level

This directory contains exactly 3 markdown documentation files. There are no subdirectories and no code. All files are context documents intended to be loaded into agent/LLM sessions to provide background knowledge about the Amplifier ecosystem.

| File | Size | Purpose |
|------|------|---------|
| `development-hygiene.md` | 6.3 KB | Installation architecture, cache safety, dev patterns, settings scope hierarchy, module resolution order, shadow environments |
| `ecosystem-overview.md` | 6.7 KB | Architectural overview: kernel/foundation/modules/bundles/agents/recipes, philosophy (Mechanism Not Policy, Ruthless Simplicity, Event-First Observability) |
| `recipes-usage.md` | 6.7 KB | Practical how-to for using the recipes tool: repo-activity-analysis, multi-repo-activity-report, context variables, MODULES.md repo discovery, output structure |

**Key symbols / concepts introduced at this level:**
- Module resolution order (6-level priority chain)
- Settings scope hierarchy (local > project > global)
- Cache safety invariant (`amplifier reset`, never `rm -rf ~/.amplifier/cache/`)
- 5 module types: Provider, Tool, Orchestrator, Context, Hook
- "Agents ARE bundles" — agents use the same file format as bundles
- Shadow environments for isolated testing
- `MODULES.md` as ecosystem registry (repo discovery source)

---

## Cross-File Connections

This directory has no child subdirectories, so "cross-child" connections become cross-file connections — shared concepts and data sources that appear in two or more of the three documents.

### 1. Module System (all three files)
- **`ecosystem-overview.md`** defines the 5 module types and their contracts
- **`development-hygiene.md`** explains how modules are installed (clone to cache → editable install), the 6-step module resolution order, and how to override modules locally via `.amplifier/settings.yaml`
- **`recipes-usage.md`** depends on the `tool-recipes` module (provided by the `recipes` bundle)
- **Pattern:** The three files together form a complete picture: what modules ARE (overview) → how they are loaded/resolved (hygiene) → how a specific module-backed tool is used (recipes-usage)

### 2. Bundles (ecosystem-overview + recipes-usage)
- **`ecosystem-overview.md`** establishes the bundle concept as the primary composition unit, and declares that agents ARE bundles (same file format, different frontmatter convention)
- **`recipes-usage.md`** opens with "Ensure the `recipes` bundle is loaded" — the recipes tool is delivered as a bundle, reinforcing the bundle-as-package pattern
- **Pattern:** Bundles are the delivery mechanism for all ecosystem capabilities; the overview establishes this; recipes-usage demonstrates it in practice

### 3. Recipes Concept (ecosystem-overview + recipes-usage)
- **`ecosystem-overview.md`** introduces recipes conceptually: "Multi-step AI agent orchestration for repeatable workflows — declarative YAML, context accumulation, approval gates, resumability"
- **`recipes-usage.md`** is the operational companion: how to invoke, what variables to pass, what output to expect, how to extract repo lists from MODULES.md
- **Pattern:** Classic concept-introduction → operational-how-to pairing; the two files are tightly coupled and complement each other

### 4. Settings Configuration (development-hygiene + ecosystem-overview)
- **`development-hygiene.md`** provides the settings scope hierarchy table (local > project > global), the full module resolution order, and example `.amplifier/settings.yaml` for local source overrides
- **`ecosystem-overview.md`** references project-local source overrides as a dev pattern in the "Getting Started for Module Developers" section
- **Pattern:** The hygiene doc owns the operational detail; the overview doc references the concept at a higher level

### 5. MODULES.md as Registry (ecosystem-overview + recipes-usage)
- **`ecosystem-overview.md`** mentions MODULES.md indirectly — the `amplifier-expert` agent has access to it for ecosystem questions
- **`recipes-usage.md`** gives concrete grep/jq commands for extracting repository URLs from MODULES.md to build a repos manifest for multi-repo analysis
- **Pattern:** MODULES.md serves dual roles: documentation and machine-readable repo registry. The two files show both dimensions.

### 6. Cache and Installation Lifecycle (development-hygiene only, but referenced conceptually)
- **`development-hygiene.md`** introduces the critical safety invariant: cache = running code; never delete directly; use `amplifier reset` instead
- This concept is not repeated in the other two files but is architecturally foundational — understanding that "the actual running code is the code in `~/.amplifier/cache/`" explains why local source overrides (covered in all three files via settings.yaml) matter

---

## Boundary Patterns

### Pattern 1: Three-Layer Documentation Stack
The directory implements a **concept → operations → task** documentation stack:
1. **Concept layer** (`ecosystem-overview.md`) — what Amplifier IS, architectural vocabulary, philosophy
2. **Operations layer** (`development-hygiene.md`) — how to safely work with the installation, settings precedence, testing isolation
3. **Task layer** (`recipes-usage.md`) — how to accomplish a specific workflow (ecosystem activity reporting)

This pattern means agents loading all three files get: vocabulary, operational context, and task guidance — everything needed for autonomous operation.

### Pattern 2: Context Sink (All Three Files)
All three documents are **context sinks** — they are designed to be loaded wholesale into agent sessions via `@mention` references rather than queried selectively. Their uniform ~6.5KB size suggests intentional sizing to fit within context budgets while remaining comprehensive.

### Pattern 3: Cross-Reference to Expert Agents
Both `ecosystem-overview.md` and `recipes-usage.md` explicitly route deeper questions to specialist agents:
- `amplifier:amplifier-expert` — ecosystem modules, repos, governance
- `foundation:foundation-expert` — bundle authoring
- `core:core-expert` — kernel internals
- `recipes:recipe-author` — recipe authoring

This pattern establishes the context files as "enough to act" but deliberately not "everything" — deeper knowledge lives in specialist agent bundles.

---

## Uncertainties for Next Level Up

1. **Who loads these files?** — The `bundle.md` or agent config at the parent level (`amplifier/`) will reveal which bundles `@mention` these context files. The relationship between this `context/` directory and the parent bundle's instruction set is not visible at this level.

2. **Are all three files always loaded together, or selectively?** — The parent bundle config determines whether agents get all three files or just specific ones based on their role.

3. **Is there a `context/` directory in other bundles that follows the same structure?** — If this is a convention (concept + hygiene + task guides), the parent level should confirm whether other sibling bundles replicate this pattern.

4. **MODULES.md location** — Referenced prominently in `recipes-usage.md` but lives outside this directory (likely in `amplifier/docs/`). The parent level should surface this dependency.

5. **Shadow environments** — `development-hygiene.md` references `@shadow:context/shadow-instructions.md` but that path is not in this directory. The parent level should map this cross-bundle dependency.

---

## Summary

The `amplifier/context` directory is a **three-file context documentation layer** for the Amplifier ecosystem bundle. The files are not code — they are knowledge artifacts sized for LLM context windows. The dominant structural pattern is a **concept → operations → task** stack: ecosystem-overview establishes vocabulary, development-hygiene provides operational safety rules and configuration hierarchy, and recipes-usage demonstrates the pattern applied to a concrete workflow. The strongest cross-file connection is the **module/bundle ecosystem** that appears in all three files, progressing from conceptual definition through installation mechanics to practical bundle-based tool invocation.
