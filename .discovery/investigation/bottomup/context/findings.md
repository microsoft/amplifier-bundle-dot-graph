# Level Synthesis: amplifier/context

**Directory:** `amplifier/context`
**Level slug:** `context`
**Fidelity:** standard
**Files at this level:** 3 markdown documentation files
**Child subdirectories:** none (leaf level)

---

## Files and Symbols at This Level

This is a leaf-level directory containing exactly three markdown documentation files. There are no subdirectories. All content lives directly at this level.

| File | Size | Role |
|------|------|------|
| `ecosystem-overview.md` | 6652 bytes | Architectural orientation — what Amplifier is, how the ecosystem is structured, design philosophy |
| `development-hygiene.md` | 6293 bytes | Operational safety and dev workflow — installation architecture, settings hierarchy, module resolution, shadow environments |
| `recipes-usage.md` | 6703 bytes | Recipe invocation guide — how to run recipes from session or CLI, generic recipe catalog, MODULES.md-based repo discovery |

**Sizes are nearly identical** (~6300–6700 bytes each), suggesting deliberate design: these files are balanced, peer-level context documents, not a primary + subordinate structure.

---

## Cross-File Connections

This level's primary signal: three files that each address a different layer of the same operational picture and explicitly reference each other's domain.

### 1. `ecosystem-overview.md` → `development-hygiene.md`
**What crosses:** The overview describes the ecosystem architecture (module types, bundle composition, settings system) at a conceptual level. `development-hygiene.md` provides the operational implementation of the same concepts — the 6-level module resolution order, the 3-scope settings hierarchy, and the precise directory structure that makes these concepts concrete.

**Shared concepts:** module resolution, settings scopes (`.amplifier/settings.yaml`), amplifier-foundation (shadow environments), amplifier-core (kernel)

### 2. `ecosystem-overview.md` → `recipes-usage.md`
**What crosses:** The overview introduces recipes and the `ecosystem-activity-report` recipe in passing (with CLI invocation examples). `recipes-usage.md` provides the complete how-to: generic recipe catalog, context variable reference, multi-step MODULES.md discovery workflow, output directory structure.

**Shared concepts:** `recipes` bundle, `amplifier tool invoke recipes`, `docs/MODULES.md`, `recipes:recipe-author` specialist agent

### 3. `ecosystem-overview.md` + `recipes-usage.md` → `docs/MODULES.md`
**What crosses:** Both files reference `docs/MODULES.md` as the canonical ecosystem repo registry. The overview uses it conceptually (ecosystem activity report); recipes-usage provides the precise `grep`/`jq` shell commands to extract repo URLs from it for multi-repo analysis.

**Significance:** `docs/MODULES.md` is an external shared dependency — neither file owns it, both depend on it for ecosystem-wide repo discovery.

### 4. `development-hygiene.md` internal: settings → resolution order
**What connects:** The settings scope hierarchy (local > project > global) directly feeds the 6-level module resolution order. These are documented as separate topics but form a single pipeline: settings define what source overrides exist; resolution order determines which source wins at runtime.

---

## Boundary Pattern

**Pattern name: Documentation Knowledge Triad**

The `context/` directory implements a coordinated three-document context injection pattern:

```
Architecture (overview) → Operations (hygiene) → Execution (recipes)
```

Each file is designed to be injected as background knowledge into AI agent sessions. Together they provide:
1. **What** the system is and why it's designed that way (`ecosystem-overview.md`)
2. **How** to work with it safely without breaking the installation (`development-hygiene.md`)
3. **How** to execute workflows and analyze the ecosystem (`recipes-usage.md`)

This is not a library or a module — it is a **documentation injection layer** for agent context. The files are consumed by the bundle loading system (`context/` is a conventional directory name in Amplifier bundles for auto-injected context).

**Secondary pattern: Specialist Delegation Registry**
Both `ecosystem-overview.md` and `recipes-usage.md` contain delegation tables pointing to specialist agents (`amplifier-expert`, `foundation-expert`, `core-expert`, `recipe-author`). This is a deliberate shallow-context pattern: provide enough for orientation, then delegate to deeper experts rather than duplicating their documentation.

---

## Key Findings

1. **Leaf-level directory, no children.** All synthesis is about relationships *between the three files*, not between subdirectories.

2. **`ecosystem-overview.md` is the hub.** It references concepts that both other files detail. It is the logical entry point and explicitly points readers to the other two files (via delegation tables and cross-references).

3. **`development-hygiene.md` contains the only critical/warning content.** The explicit `NEVER: rm -rf ~/.amplifier/cache/` warning and the `amplifier reset` safe pattern are unique to this file — neither other file covers operational safety hazards.

4. **`recipes-usage.md` is the most self-contained.** It provides a complete workflow (discover repos → filter → run recipe → find output) that can be executed without reading the other files, but is conceptually grounded by `ecosystem-overview.md`.

5. **All three files are approximately the same size (~6.5KB).** This uniformity suggests a deliberate content budget for context injection — each file stays under a threshold appropriate for inclusion as background context without overwhelming the session window.

6. **No Python, YAML, or code files at this level.** This is a pure documentation layer. The architectural significance is its role in the bundle system, not any executable behavior.

---

## Uncertainties for the Next Level Up

1. **How is this `context/` directory consumed?** What is the bundle loading mechanism that injects these files? Is it automatic (all `.md` files in `context/`) or explicit (listed in a bundle manifest)?

2. **Are these files versioned alongside the bundle?** If the `amplifier` bundle at the parent level has its own versioning, do these context files change when the ecosystem evolves (e.g., new module types get added)?

3. **Is there a priority or ordering** in how these three files are injected? Does `ecosystem-overview.md` always load first (as it is the conceptual entry point)?

4. **The `docs/MODULES.md` external dependency** — where does it live relative to the bundle root? The recipes reference it as `amplifier:docs/MODULES.md` suggesting it's in the amplifier bundle's `docs/` sibling directory.

5. **Shadow environments** are described in `development-hygiene.md` but the implementation lives in `amplifier-foundation`. Is there additional context about shadow environments in a sibling directory (e.g., `context/shadow-instructions.md` referenced in the file)?
