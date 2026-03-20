# Level Synthesis: amplifier/agents

**Directory:** `/home/bkrabach/dev/dot-graph-bundle/amplifier/agents`
**Level slug:** `agents`
**Fidelity:** standard
**Synthesized:** 2026-03-20

---

## Files and Symbols at This Level

This is a **leaf-level directory** containing a single file with no subdirectories.

### `amplifier-expert.md`

An **Amplifier agent definition** file — the canonical format for declaring an agent within the Amplifier bundle system. The file uses a composite structure:

| Section | Content |
|---------|---------|
| YAML frontmatter (`meta:`) | `name: amplifier-expert`, `description: <rich agent description>`, `model_role: general` |
| Markdown body | Detailed agent instructions, knowledge base, operating modes, decision frameworks |
| Trailing include | `@foundation:context/shared/common-agent-base.md` — shared base wired in at load time |

**Agent role:** This agent is explicitly positioned as the *authoritative ecosystem router* — the entry point other agents consult before beginning Amplifier-related work. It does not implement functionality itself; it routes knowledge and validates alignment.

**Operating modes (3):**

- **RESEARCH** — activated by "what is", "how does", "what can" questions; provides structured ecosystem context
- **GUIDE** — activated by "how should I", "what pattern for" questions; provides implementation guidance with pattern references
- **VALIDATE** — activated by "is this right", "does this align", review requests; performs philosophy alignment checks

**Knowledge tiers (5):**

| Tier | Bundle | Key focus |
|------|--------|-----------|
| Tier 0 | `amplifier-core` | Ultra-thin kernel (~2,600 lines), Session, Coordinator, Module Protocols |
| Tier 1 | `amplifier` | Entry point docs, user guide, developer guide, module ecosystem |
| Tier 2 | `amplifier-foundation` | Bundle primitives, examples, behaviors, agents |
| Tier 3 | Core Philosophy | `@foundation:context/` philosophy documents |
| Tier 4 | Recipes | Multi-step workflow orchestration |

**External @-mention references (live links):**

- `@core:docs/` — kernel documentation
- `@amplifier:docs/` — entry point documentation
- `@foundation:docs/`, `@foundation:examples/`, `@foundation:behaviors/`, `@foundation:agents/`, `@foundation:context/`
- `@recipes:docs/`, `@recipes:examples/`
- `@foundation:context/shared/common-agent-base.md` — base include at file end

**Collaboration delegation pattern:**

- → `core:core-expert` — deep kernel contract questions, module protocol details, kernel-vs-module decisions
- → `foundation:foundation-expert` — bundle composition details, example patterns, application building
- → `recipes:recipe-author` — multi-step workflow authoring

**Philosophy principles encoded (7):**

1. Mechanism, Not Policy
2. Ruthless Simplicity
3. Bricks & Studs
4. Event-First Observability
5. Text-First
6. Don't Break Modules
7. Two-Implementation Rule

**Module types reference table (inline):** Provider, Tool, Orchestrator, Context, Hook, Agent — with contract signatures and examples.

---

## Cross-Child Connections

**None.** This is a leaf-level directory with a single file and no subdirectories. There are no cross-child connections to identify.

---

## Boundary Patterns

### Pattern: Ecosystem Knowledge Router

`amplifier-expert.md` embodies the **knowledge router** pattern — an agent that holds authoritative cross-cutting knowledge across all tiers of the ecosystem and routes queries to appropriate specialist agents. This pattern is architecturally distinct from capability agents (which implement tools or providers) and specialist agents (which go deep in one domain).

Characteristics of this pattern:
- Holds explicit tier hierarchy of knowledge sources
- Maintains a delegation map to deeper specialists
- Validates against philosophy before passing to implementers
- Is referenced from the bundle description (`description:` field) as the entry point
- Does NOT perform implementation work itself

### Pattern: Tiered Knowledge Base with Living References

The knowledge base is organized as a deliberate tier hierarchy from kernel → foundation → philosophy → recipes. Each tier maps to a specific external bundle via `@-mention` syntax, making all references **live** (resolved at runtime, not duplicated). This prevents documentation drift and is the canonical "single source of truth" approach for agent context.

### Pattern: Common Base Include

The `@foundation:context/shared/common-agent-base.md` trailing include is a **shared base injection** pattern — providing common agent behaviors (likely tool invocation instructions, format rules, safety guardrails) that all agents inherit without duplicating. This is an Amplifier convention for composable agent context.

---

## Uncertainties for Next Level Up

The parent synthesis (`amplifier/` directory level) should investigate:

1. **Sibling agents** — The `amplifier/agents/` directory currently holds only `amplifier-expert.md`. The parent level should confirm whether additional agents are defined at the `amplifier/` root or in sibling directories, and how they relate to `amplifier-expert`.

2. **Agent discovery mechanism** — How does the Amplifier runtime discover and load agent definitions from this directory? Is `amplifier/agents/` a registered scan path, or are agents explicitly declared in `bundle.md`?

3. **Hierarchy of `amplifier-expert` vs. peer agents** — `amplifier-expert.md` references `core:core-expert` and `foundation:foundation-expert`. Are those agents also defined in analogous `agents/` directories within `amplifier-core` and `amplifier-foundation` bundles? The routing topology only becomes clear at the cross-bundle level.

4. **Relationship between `agents/` and `behaviors/`** — The sibling `amplifier/behaviors/` directory presumably holds behavior fragments. Understanding whether agents compose behaviors or are self-contained is a parent-level question.

5. **`common-agent-base.md` contract** — The trailing include `@foundation:context/shared/common-agent-base.md` is referenced without inspection here. The parent level (or foundation bundle synthesis) should clarify what this base provides and what contract all agents implicitly accept.
