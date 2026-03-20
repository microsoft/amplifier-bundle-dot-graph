# Subsystem Synthesis: Top-Down Discovery

**Subsystem:** topdown-discovery
**Scope:** amplifier bundle — 6 top-down investigation modules
**Modules synthesized:**
1. agent-behavior-architecture (agents/, behaviors/, context/, outlines/, bundle.md)
2. bundle-composition (amplifier-foundation registry, amplifier-core loader)
3. documentation-governance (docs/, context/, outlines/, governance recipes)
4. ecosystem-governance (meta-synthesis across all governance layers)
5. expert-agent-knowledge (expert agent's knowledge hierarchy, routing, modes)
6. recipe-orchestration (executor engine, 6 production recipes)
**Date:** 2026-03-20

---

## Executive Summary

The top-down discovery subsystem reveals a system whose cross-module architecture is dominated by two structural properties: (1) a single shared protocol — the @-mention resolver — carries ALL knowledge delivery across ALL modules, and (2) a circular content lifecycle connects documentation governance through behavior composition through agent knowledge through bundle composition through recipe execution back to documentation generation. Fifteen distinct cross-module data flows were identified. Two are tightly coupled: MODULES.md consumed by 3 recipes via 3 independent fetch mechanisms that bypass @-mention resolution entirely, and the recipe engine's 9+ duck-typed `getattr()` surfaces on the kernel coordinator. A subsystem-spanning silent degradation chain compounds across all five non-meta modules — module loading failures, @-mention resolution failures, and recipe observability gaps all degrade silently with no diagnostic at any stage.

---

## Cross-Module Data Flows

15 distinct flows identified crossing module boundaries:

| # | Source Module | Target Module | Type / Data | Transformation | Coupling |
|---|-------------|--------------|------------|----------------|----------|
| 1 | doc-governance | agent-behavior | Source docs (125KB, 10 files) | Refinement pipeline: docs → outlines → context | Clean |
| 2 | agent-behavior | expert-knowledge (via @-mention) | Refined context (~20KB, 3 files) | Injected via behavior `context.include` | Clean |
| 3 | agent-behavior | expert-knowledge | Agent + context wiring | `agents.include` + `context.include` in behavior YAML | Clean |
| 4 | bundle-composition | @-mention protocol | `source_base_paths` dict | Accumulated during `Bundle.compose()` merge; first-reg wins | Clean |
| 5 | @-mention protocol | expert-knowledge | Resolved governance content | `parse_mentions()` → `BaseMentionResolver` → `ContentDeduplicator` → system prompt | Clean |
| 6 | doc-governance | expert-knowledge (via @-mention) | REPOSITORY_RULES.md | `@amplifier:docs/` Tier 1 reference | Clean |
| 7 | expert-knowledge | recipe-orchestration (via spokes) | zen-architect dependency | All 6 recipes use `foundation:zen-architect` | Clean |
| 8 | doc-governance | recipe-orchestration | MODULES.md (25KB) | 3 independent fetch mechanisms: `curl -sL`, `curl` + extract, `gh api` + `base64 -d` | **TIGHT** |
| 9 | recipe-orchestration | bundle-composition | `session.spawn` capability | `get_capability('session.spawn')` — single formal kernel integration | Clean |
| 10 | recipe-orchestration | bundle-composition | 9+ coordinator surfaces | Duck-typed `getattr()` with fallback; cancellation, hooks, config, display, routing, bundles | **TIGHT** |
| 11 | recipe-orchestration | doc-governance | Generated documentation | Recipes produce new docs, completing circular lifecycle | Clean |
| 12 | bundle-composition | @-mention protocol | `module-source-resolver` mount | Foundation provides resolver, core consumes it via coordinator mount point | Clean |
| 13 | bundle-composition | expert-knowledge | Silent degradation | Non-fatal module load (`logger.warning`) → @-mention returns `None` → reduced knowledge | Hidden |
| 14 | expert-knowledge | recipe-orchestration | Convention-based delegation | Expert routes to spoke agents; recipes consume spoke agents directly | Loose |
| 15 | agent-behavior | bundle-composition | Bundle entry wiring | `bundle.md` → `behaviors/amplifier-expert` → composition pipeline | Clean |

---

## Shared Interfaces

### @-mention Protocol (ALL modules)

The single most important cross-module interface. Every module either produces content for @-mention delivery or consumes content through it. The protocol (`parse_mentions()` → `BaseMentionResolver` → `ContentDeduplicator`) lives in amplifier-foundation, not in the amplifier bundle — making it an external dependency that the entire subsystem relies on. Five of six modules reference it directly.

**Modules involved:** bundle-composition (provides `source_base_paths`), agent-behavior (uses `context.include`), expert-knowledge (28 @-mentions in agent file), doc-governance (governance rules delivered via Tier 1), recipe-orchestration (enforcement recipes could use it but bypass it for MODULES.md).

### source_base_paths Dict (bundle-composition → all @-mention consumers)

The namespace-to-path mapping produced by `Bundle.compose()` during bundle loading. It uses "first registration wins" merge semantics, making it sensitive to load ordering in diamond dependency scenarios. This dict enables ALL @-mention resolution — if it is empty or incomplete, governance content silently vanishes.

**Modules involved:** bundle-composition (produces), expert-knowledge (consumes indirectly), doc-governance (consumes indirectly), agent-behavior (consumes via behavior context resolution).

### System Prompt Factory (bundle-composition → expert-knowledge)

Per-request assembly mechanism that re-reads context files and re-resolves @-mentions on every `get_messages_for_request()` call. No caching. This is the serialization boundary where composed bundle content becomes the expert agent's active knowledge.

**Modules involved:** bundle-composition (implements), expert-knowledge (consumes).

### session.spawn Capability (bundle-composition → recipe-orchestration)

The single formal kernel capability the recipe engine consumes. `get_capability('session.spawn')` at `executor.py:1559` is the only typed integration point. Everything else the recipe engine accesses on the coordinator (9+ surfaces) uses duck-typed `getattr()`.

**Modules involved:** bundle-composition (provides via kernel), recipe-orchestration (consumes).

### Context Dict (recipe-orchestration, cross-cutting)

The overloaded universal medium within recipe-orchestration that simultaneously serves as execution state, data bus, template variable store, checkpoint payload, and cross-recipe interface. Every boundary within the recipe system passes through context dict. Checkpoint trimming (>100KB → placeholder) and template escaping failures attack this single surface.

**Modules involved:** recipe-orchestration (owns), bundle-composition (provides session context that seeds it).

---

## Coupling Assessment

| Module Pair | Coupling Type | Evidence | Risk |
|------------|--------------|---------|------|
| doc-governance → recipe-orchestration (MODULES.md) | **TIGHT** | 3 independent fetch mechanisms (`curl -sL`, `curl` + extract, `gh api` + `base64 -d`) bypass @-mention namespace resolution. Each recipe independently implements its own fetch with no abstraction layer. | HIGH — change to MODULES.md format or location breaks 3-4 recipes independently |
| recipe-orchestration → bundle-composition (coordinator) | **TIGHT** | 9+ coordinator surfaces accessed via duck-typed `getattr()` with fallback values. The module declares one formal capability (`session.spawn`) but functionally depends on cancellation, hooks, config, display, routing, and bundle resolution — all through untyped attribute lookups. | HIGH — invisible dependency graph; coordinator changes silently degrade recipe behavior |
| doc-governance → agent-behavior (content pipeline) | **Clean** | Content flows through a defined pipeline: docs → outlines → context. Namespace-mediated composition at every step. | LOW |
| agent-behavior → expert-knowledge (behavior wiring) | **Clean** | `agents.include` and `context.include` use `amplifier:` namespace references, not direct file imports. | LOW |
| bundle-composition → expert-knowledge (@-mention chain) | **Clean** | `source_base_paths` → `BaseMentionResolver` → `SystemPromptFactory` → agent. Well-defined protocol at each boundary. | LOW |
| bundle-composition → all modules (silent degradation) | **Hidden** | Non-fatal module loading (`logger.warning` only) compounds with @-mention returning `None` on missing content. No diagnostic exists at any stage. | HIGH — invisible failure mode spanning all modules |
| expert-knowledge → recipe-orchestration (agent dependency) | **Loose** | Recipes reference spoke agents by namespace (`foundation:zen-architect`). No direct code coupling. | LOW |
| recipe-orchestration → doc-governance (doc generation) | **Clean** | Recipes produce documentation as file output. No structural coupling — only content lifecycle dependency. | LOW |

---

## Emergent Patterns

### 1. Circular Content Lifecycle (subsystem-defining pattern)

The dominant architectural pattern visible only at the subsystem level — no single module sees the full loop:

```
Documentation Governance (defines rules, 125KB docs)
  → Agent & Behavior Architecture (refines into ~20KB context)
    → Expert Agent Knowledge (aggregates + routes via 5-tier hierarchy)
      → Bundle Composition (assembles via @-mention into system prompt)
        → Recipe Orchestration (executes enforcement, generates new docs)
          → Documentation Governance (updated docs, cycle repeats)
```

Evidence that this cycle is difficult to stabilize: `document-generation.yaml` is at v8.1.0 (126KB, 3,033 lines, 7+ major versions with in-file changelog). The cycle means documentation is generated by recipes informed by the documentation they generate.

### 2. Single Protocol Monopoly (@-mention)

The @-mention protocol is simultaneously: the sole knowledge delivery mechanism, the sole governance content delivery mechanism, and the sole cross-bundle reference mechanism. This monopoly creates a single point of failure that spans all 5 non-meta modules. The bundle-composition module's `source_base_paths` dict is the enabler — if it is empty, ALL governance content vanishes from ALL sessions.

### 3. Convention-Over-Code at Every Module Boundary

All six modules independently identify convention-over-code as a defining characteristic. Only two mechanisms are code-enforced across the ENTIRE subsystem: the @-mention resolver and ContentDeduplicator. Everything else — tier priority, expert routing, mode dispatch, thin/heavy bundle split, token budgets, model tier strategy, recipe conventions — is natural language or YAML convention with no mechanical enforcement.

### 4. Infrastructure Robustness vs. Policy Fragility

The bundle-composition module reveals well-engineered code infrastructure: cycle detection, diamond deduplication, three-layer caching, polyglot transport dispatch, parallel activation. Yet the governance system built on this infrastructure is entirely advisory — convention-based rules, periodic-only enforcement, no continuous compliance checking. The code layer has the mechanisms to enforce governance (module validation, protocol checking, mount point gating), but the governance layer uses none of them.

### 5. Five-SPOF Sequential Chain

A sequential chain of single points of failure spans four modules:
1. **MODULES.md** (doc-governance) — sole ecosystem registry, 3 fetch bypasses
2. **@-mention resolver** (bundle-composition → expert-knowledge) — sole delivery mechanism, returns None silently
3. **module-source-resolver mount** (bundle-composition) — non-fatal failure disables ALL @-mention resolution
4. **System Prompt Factory** (bundle-composition → expert-knowledge) — per-request re-read, no caching
5. **amplifier-expert.md** (expert-knowledge) — sole agent, 15KB knowledge monopoly, no fallback

Any single failure in this chain silently degrades all downstream modules.

---

## Recommended Investigation

1. **Resolve the eager vs. lazy @-mention loading discrepancy** — Identified independently by FOUR modules (doc-governance, expert-knowledge, agent-behavior, ecosystem-governance). Determines whether each session pays ~20KB or ~200KB in governance token cost (10x difference). Trace `_resolve_mention()` in `amplifier-foundation/amplifier_foundation/mentions/resolver.py` for directory path arguments.

2. **Measure actual cross-module token budget** — No measurement exists anywhere in the subsystem. The content pipeline produces ~20KB of context files, but the expert's 28 @-mentions (10 directory-level) could expand the actual cost dramatically. The System Prompt Factory re-reads on every request with no measurement.

3. **Abstract MODULES.md access** — The tightest coupling in the subsystem. Three independent fetch mechanisms across 4 recipes bypass the @-mention protocol that everything else uses. An `@amplifier:docs/MODULES.md` @-mention would align with existing patterns and eliminate the bypass.

4. **Formalize recipe-coordinator contract** — The 9+ duck-typed `getattr()` surfaces are the second-tightest coupling. Evaluate which surfaces should be registered as formal capabilities vs. remaining as convention.

5. **Add diagnostic to silent degradation chain** — The compound silent degradation (module loading → @-mention → enforcement) spans all modules with zero visibility. A session-startup governance validation or health check would surface the broken chain. This is the subsystem's most significant cross-cutting risk.

6. **Verify amplifier-dev-behavior activation** — Flagged independently by THREE modules. If orphaned, operational safety knowledge never reaches agent sessions, breaking the content pipeline for 1/3 of the context triad.

7. **Investigate whether module validation could extend to governance content** — The code infrastructure validates module structure (`_validate_module()`). No equivalent validates governance content integrity, completeness, or freshness. The infrastructure exists; the governance layer doesn't use it.
