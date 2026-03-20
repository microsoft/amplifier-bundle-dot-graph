# Level Synthesis: amplifier/behaviors

**Directory:** `/home/bkrabach/dev/dot-graph-bundle/amplifier/behaviors`
**Level slug:** `behaviors`
**Fidelity:** standard
**Children synthesized:** 0 (leaf-level directory)

---

## Files and Symbols at This Level

This is a **leaf-level directory** containing exactly two Amplifier bundle definition files. There are no subdirectories and no child syntheses to incorporate.

| File | Bundle Name | Version | Description |
|------|-------------|---------|-------------|
| `amplifier-dev.yaml` | `amplifier-dev-behavior` | 1.0.0 | Development hygiene and best practices for Amplifier CLI users |
| `amplifier-expert.yaml` | `amplifier-expert-behavior` | 1.0.0 | Authoritative consultant for the complete Amplifier ecosystem |

### amplifier-dev.yaml

A **pure context injection behavior**. Contains only a `bundle:` header and a `context.include` referencing `amplifier:context/development-hygiene.md`. No agent is composed — the behavior augments the runtime context of the session with development discipline guidance only.

```yaml
bundle:
  name: amplifier-dev-behavior
  version: 1.0.0
  description: Development hygiene and best practices for Amplifier CLI users
context:
  include:
    - amplifier:context/development-hygiene.md
```

### amplifier-expert.yaml

An **agent + context composition behavior**. Includes both an agent reference (`amplifier:amplifier-expert`) and a context file (`amplifier:context/ecosystem-overview.md`). The comment in the file notes that `recipes-usage.md` was demoted to a soft reference (load on demand), indicating intentional progressive-loading design.

```yaml
bundle:
  name: amplifier-expert-behavior
  version: 1.0.0
  description: Authoritative consultant for the complete Amplifier ecosystem
agents:
  include:
    - amplifier:amplifier-expert
context:
  include:
    - amplifier:context/ecosystem-overview.md
    # recipes-usage.md demoted to soft reference (load on demand)
```

---

## Cross-Child Connections

**None.** This is a leaf-level directory with no subdirectory children. No cross-child connections exist.

At the **peer level** (between the two co-resident files), the following shared structural elements are observed:

1. **Shared bundle schema** — Both files use identical top-level schema: `bundle: { name, version, description }` / `context: { include: [...] }`. They are instances of the same bundle format.
2. **Shared external namespace** — Both reference `amplifier:` as their resource namespace for context files and agents, establishing a consistent intra-ecosystem dependency pattern.
3. **Coordinated versioning** — Both at v1.0.0, indicating they ship as a pair.

---

## Boundary Patterns

### Pattern 1: Behavior Composition Layer

The `behaviors/` directory acts as a **thin composition layer** — it assembles pre-existing context and agent definitions into named, versioned behavior bundles. No new logic, types, or implementations are defined here. The directory's purpose is to create stable, reusable configuration units from components defined elsewhere (`context/`, `agents/`).

**Participants:**
- `amplifier-dev.yaml` → `amplifier:context/development-hygiene.md`
- `amplifier-expert.yaml` → `amplifier:context/ecosystem-overview.md` + `amplifier:amplifier-expert`

### Pattern 2: Two Behavior Archetypes

Two archetypal behavior patterns are visible at this level:

| Archetype | Example | Composition |
|-----------|---------|-------------|
| **Context-only** | `amplifier-dev` | Injects guidance/discipline via a context document; no agent capability added |
| **Agent + context** | `amplifier-expert` | Composes an agent definition AND a context document; enables active expert consultation |

This suggests the behavior system supports a spectrum from lightweight (informational context loading) to heavyweight (full agent persona activation).

### Pattern 3: Progressive Context Loading

`amplifier-expert.yaml` contains a note indicating that `recipes-usage.md` was explicitly **demoted to a soft/on-demand reference**. This hints at a performance-conscious design: heavy context (recipes documentation) is not pre-loaded into every session, only pulled in when relevant. The behaviors directory is one control point for this optimization.

---

## Uncertainties for Next Level Up

The following questions exceed what can be answered from this directory alone and should be investigated at the parent (`amplifier/`) level or above:

1. **Agent definition location** — `amplifier:amplifier-expert` is referenced in `amplifier-expert.yaml` but the agent's definition lives in `amplifier/agents/`. What is the full definition of that agent, and how deeply does `amplifier-expert-behavior` depend on it?

2. **Behavior loading trigger** — How are these behavior bundles activated? Is `behaviors/` scanned automatically at bundle load time, or are individual files selectively activated by recipes or the CLI?

3. **Context file contents** — The behaviors reference `development-hygiene.md` and `ecosystem-overview.md` from `amplifier:context/`. The content of those documents determines the behavioral impact of each bundle; this directory only holds the wiring, not the substance.

4. **Peer behaviors in sibling bundles** — Do other bundles in the repository (e.g., `amplifier-bundle-recipes/`, `amplifier-bundle-dev-machine/`) have their own `behaviors/` directories? If so, this may be an ecosystem-wide pattern worth mapping.

5. **Versioning lifecycle** — Both bundles are v1.0.0. Is there a release coordination mechanism across behaviors, context, and agents that keeps them in sync?
