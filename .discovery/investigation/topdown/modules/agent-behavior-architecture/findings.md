# Module Synthesis: Agent & Behavior Definition Architecture

**Module:** Agent & Behavior Definition Architecture
**Scope:** `amplifier/agents/`, `amplifier/behaviors/`, `amplifier/context/`, `amplifier/outlines/`, root `bundle.md`
**Investigation sources synthesized:** 8 (bottom-up agents/, bottom-up behaviors/, bottom-up context/, bottom-up outlines/, top-down expert-agent-knowledge, top-down subsystem, agent-constellation code-tracer, agent-constellation integration-mapper)
**Fidelity:** standard
**Date:** 2026-03-19

---

## Executive Summary

The Agent & Behavior Definition Architecture defines how AI agents are structurally declared, how behaviors compose agent capabilities with context knowledge, and how the entire definition pipeline flows from authoritative documentation through outline specifications to token-optimized context files. Eight investigation perspectives converge on eight structural consensus findings: (1) agents use a dual-layer YAML-frontmatter + Markdown-body definition format with no schema enforcement, (2) behaviors implement a deliberate thin-bundle pattern splitting "active" (agent+context) from "passive" (context-only) injection, (3) a multi-stage content refinement pipeline (docs → outlines → context → behaviors → agents) is the dominant architectural pattern, (4) the architecture is convention-driven with only two code-enforced mechanisms, (5) a hub-and-spoke routing pattern connects the sole expert agent to three spoke experts, (6) three trigger-phrase-dispatched operating modes govern response behavior, (7) all cross-boundary references use namespace-mediated composition via the @-mention protocol, and (8) token budgets are deliberately managed but never measured. Four discrepancies remain open — the most significant being whether directory-level @-mentions eagerly or lazily load content, which determines whether the expert's system prompt is ~20KB or ~200KB.

---

## Consensus Findings

### C-01: Dual-Layer Agent Definition Format (HIGH confidence)

**Sources:** bottom-up agents/, top-down expert-agent-knowledge, agent-constellation code-tracer, primary source

Agent definitions use a combined YAML frontmatter + Markdown body format within a single `.md` file:

| Layer | Purpose | Consumer |
|-------|---------|----------|
| YAML `meta` block | `name`, `model_role`, `description` (condensed summary with usage examples) | Other agents (delegator-facing interface) |
| Markdown body | Full instruction set: operating modes, knowledge tiers, philosophy, decision frameworks, anti-patterns, response templates, collaboration map | The agent itself (runtime instructions) |

The bottom-up agents/ analysis identifies this as a "two-layer description pattern" — the `meta.description` is an external interface for callers, while the body is the agent's internal operating manual. The top-down expert-knowledge synthesis confirms the same structure. The agent-constellation code-tracer confirms this pattern applies consistently across all 7 agents in the dot-graph bundle (discovery-prescan, discovery-code-tracer, discovery-behavior-observer, discovery-integration-mapper, discovery-synthesizer, dot-author, diagram-reviewer), providing cross-bundle evidence of the pattern's universality. Only one agent file exists in the amplifier bundle (`amplifier-expert.md`, 15.1 KB).

**Confidence:** HIGH — independently confirmed by three analysis streams and cross-bundle pattern evidence.

### C-02: Thin Bundle Behavior Pattern with Active/Passive Split (HIGH confidence)

**Sources:** bottom-up behaviors/, top-down expert-agent-knowledge, bottom-up subsystem, top-down subsystem

The `behaviors/` directory contains exactly two thin-bundle YAML files that compose capabilities rather than define them:

| Bundle | Has Agent? | Has Context? | Pattern |
|--------|-----------|-------------|---------|
| `amplifier-expert-behavior` | Yes (`amplifier:amplifier-expert`) | Yes (`ecosystem-overview.md`) | Active capability injection |
| `amplifier-dev-behavior` | No | Yes (`development-hygiene.md`) | Passive context injection |

All four investigation streams independently identify these as **composable thin bundles** — they reference external artifacts via the `amplifier:` namespace rather than containing implementation. The bottom-up behaviors/ analysis names the split "context-only vs agent+context divergence." The top-down expert-knowledge synthesis calls it the "thin/heavy split (context gate)." The bottom-up subsystem synthesis confirms the wiring: behaviors → context via `context.include`, behaviors → agents via `agents.include`.

**Confidence:** HIGH — four independent sources converge.

### C-03: Multi-Stage Content Refinement Pipeline (HIGH confidence)

**Sources:** bottom-up subsystem, bottom-up context/, bottom-up outlines/, top-down expert-agent-knowledge

Content flows through a multi-stage pipeline spanning four directories:

```
docs/ (authoritative long-form, ~125KB total)
  -> outlines/ (synthesis specifications with section-level LLM prompts)
    -> context/ (agent-optimized ~6.5KB summaries, 3 balanced files)
      -> behaviors/ (session activation declarations)
        -> agents/ (runtime knowledge base consumption)
```

The bottom-up subsystem synthesis names this the "Three-Layer Context Pipeline" and identifies it as "the dominant architectural pattern." The bottom-up context/ analysis identifies the "Documentation Knowledge Triad" — three context files deliberately balanced at ~6.3-6.7KB each (architecture, operations, recipes). The bottom-up outlines/ analysis confirms the pipeline input: `development-hygiene_outline.json` reads from `docs/LOCAL_DEVELOPMENT.md` (12 section references) and `docs/USER_ONBOARDING.md` (4 references) to produce `context/development-hygiene.md`.

**Confidence:** HIGH — pipeline traced end-to-end across four bottom-up analyses.

### C-04: Convention-Over-Code Architecture (HIGH confidence)

**Sources:** top-down subsystem, bottom-up agents/, bottom-up behaviors/, top-down expert-agent-knowledge, agent-constellation integration-mapper

Every investigation stream independently identifies that the agent and behavior definition architecture relies on conventions rather than code enforcement:

- **Agent format:** YAML+Markdown convention, no schema validation (bottom-up agents/)
- **Tier priority:** Natural language ordering in instruction text, not runtime enforcement (top-down subsystem, bottom-up agents/)
- **Expert routing:** Hub-and-spoke delegation described in prose, not coded dispatch (top-down subsystem, bottom-up agents/)
- **Mode dispatch:** RESEARCH/GUIDE/VALIDATE modes via trigger-phrase matching, not classified inputs (bottom-up agents/)
- **Thin/heavy split:** Behavioral distinction is a YAML pattern, not a framework feature (bottom-up behaviors/, top-down expert-knowledge)
- **Token budget:** Managed by file size balance (~6.5KB each) and manual YAML comment demotion, not measurement (bottom-up context/, bottom-up behaviors/)
- **Agent prompt contract:** The recipe's prompt IS the API contract — "there is no function signature, only a natural language spec" (agent-constellation integration-mapper)

The top-down subsystem synthesis names this "Convention-Over-Code Architecture" as a subsystem-defining pattern. Only two mechanisms are code-enforced across the entire definition architecture: the @-mention resolver and ContentDeduplicator. Everything else is convention.

**Confidence:** HIGH — independently identified by all streams.

### C-05: Hub-and-Spoke Agent Routing (HIGH confidence)

**Sources:** bottom-up agents/, top-down expert-agent-knowledge, top-down subsystem

The sole agent (`amplifier-expert`) acts as an ecosystem gateway that classifies queries and routes to three spoke experts:

- `core:core-expert` — deep kernel contracts and module protocols
- `foundation:foundation-expert` — bundle composition, patterns, and examples
- `recipes:recipe-author` — multi-step workflow authoring

The bottom-up agents/ analysis calls this the "Ecosystem Router / Gateway Agent" pattern — "single source of truth design pattern applied at the agent layer." The top-down expert-knowledge synthesis calls it "Hub Agent" and "context sink." Both agree routing is convention-based — the expert's instruction text describes when to delegate, but no code enforces routing rules.

**Confidence:** HIGH — structural agreement across three sources.

### C-06: Three Operating Modes with Trigger-Phrase Dispatch (HIGH confidence)

**Sources:** bottom-up agents/, top-down expert-agent-knowledge (partial), primary source

The expert agent implements three activation modes, each with dedicated response templates:

| Mode | Trigger Phrases | Response Focus |
|------|----------------|----------------|
| RESEARCH | "what is", "how does", "what can" | Factual explanation from knowledge tiers |
| GUIDE | "how should I", "what pattern for" | Prescriptive recommendation |
| VALIDATE | "is this right", review requests | Assessment against philosophy/patterns |

The bottom-up agents/ analysis classifies this as a "Mode-Dispatched Persona" pattern — a lightweight persona dispatch avoiding monolithic instructions. The top-down expert-knowledge synthesis acknowledges the three modes but treats the expert as a single entity without deep mode analysis. The agent-constellation code-tracer provides analogous evidence that discovery agents use `model_role: reasoning` as a different kind of mode specification, confirming the pattern of agent-level mode declarations.

**Confidence:** HIGH — directly confirmed by primary source inspection.

### C-07: Namespace-Mediated Composition (HIGH confidence)

**Sources:** bottom-up subsystem, bottom-up behaviors/, top-down subsystem, top-down bundle-composition, agent-constellation integration-mapper

All cross-boundary references in the agent/behavior definition architecture use the `amplifier:` namespace protocol:

- `behaviors/ -> context/`: `context.include: amplifier:context/development-hygiene.md`
- `behaviors/ -> agents/`: `agents.include: amplifier:amplifier-expert`
- `agents/ -> docs/`: `@amplifier:docs/` @-mention references
- `agents/ -> external`: `@core:docs/`, `@foundation:docs/`, `@foundation:context/`, `@recipes:docs/`
- `bundle.md -> behaviors/`: `includes: amplifier:behaviors/amplifier-expert`

The bottom-up subsystem synthesis classifies all of these as **clean coupling** — "mediated by the `amplifier:` namespace resolver; behaviors reference context files by stable path, not by internal structure." The top-down bundle-composition analysis confirms namespace resolution flows through `BundleRegistry._load_single()`. The agent-constellation integration-mapper confirms the same pattern applies to discovery agents: `agent: "dot-graph:discovery-prescan"` — bundle namespace resolution is the universal dispatch mechanism.

**Confidence:** HIGH — independently confirmed by five investigation streams.

### C-08: Deliberate Token Budget Management (MEDIUM confidence)

**Sources:** bottom-up behaviors/, bottom-up context/, top-down expert-agent-knowledge

Multiple streams identify conscious token budget management with no measurement infrastructure:

- `recipes-usage.md` deliberately demoted from `context.include` to a YAML comment ("soft reference / load on demand") in `amplifier-expert.yaml` (bottom-up behaviors/)
- Three context files are balanced at ~6.3-6.7KB each, suggesting "a deliberate content budget for context injection" (bottom-up context/)
- The top-down expert-knowledge synthesis flags "No token budget enforcement" as an open question
- The outline spec constrains generation parameters: `max_response_tokens: 8000`, `temperature: 0.2` (bottom-up outlines/)

**Confidence:** MEDIUM — evidence of deliberate management is clear, but no investigation stream measured actual token costs.

---

## Cross-Cutting Insights

### X-01: Single-Agent Knowledge Monopoly as Architectural Risk

The entire `agents/` directory contains exactly one file (`amplifier-expert.md`, 15.1 KB). This single document carries the complete ecosystem knowledge routing: 5-tier knowledge hierarchy, 3-mode persona dispatch, 3 spoke expert routing rules, 7 philosophy principles, 6 anti-patterns, and decision frameworks. The bottom-up agents/ analysis asks: "Is `amplifier-expert.md` the only agent, or does the bundle register additional agents from elsewhere?" The answer from file inspection: it is the only agent.

**Implication:** If this document is malformed, stale, or absent, ALL ecosystem knowledge routing fails with no fallback. The top-down expert-knowledge synthesis calls this "Knowledge Monopoly." The bottom-up subsystem synthesis notes that `bundle.md` includes only `amplifier:behaviors/amplifier-expert`, confirming a single-path dependency chain: `bundle.md` → `amplifier-expert-behavior` → `amplifier-expert.md`.

**Contrast from agent-constellation:** The dot-graph bundle defines 7 agents with complementary roles (prescan, 3 investigation agents, synthesizer, dot-author, diagram-reviewer), showing that the single-agent pattern is a *design choice* specific to the amplifier bundle, not an ecosystem constraint. Other bundles distribute knowledge across multiple specialized agents.

### X-02: Documentation-as-Architecture Fragility

The entire agent and behavior definition architecture is pure documentation — no executable code, no tests, no runtime schema validation, no type checking. The bottom-up agents/ analysis notes the expert's "canonical vocabulary" (module types table, decision frameworks, anti-pattern list) exists only in instruction text. The bottom-up behaviors/ analysis confirms behavior bundles are "thin bundles" referencing external artifacts. The bottom-up context/ analysis calls the context layer "a pure documentation layer."

**Implication:** This creates maximum flexibility (any change is a text edit) with zero mechanical protection against drift, staleness, or contradiction. The only guard against context poisoning is a philosophy document about context poisoning loaded as Tier 3 knowledge — a self-referential defense.

### X-03: Parallel Hub-and-Spoke Pattern Across Layers

Two independent investigation streams identified hub-and-spoke as the dominant navigation pattern at different layers:

- **Documentation layer:** README.md routes to audience-tiered docs (bottom-up docs/)
- **Agent layer:** amplifier-expert.md routes to spoke experts (bottom-up agents/)
- **Context layer:** ecosystem-overview.md is the "hub" referencing both other context files (bottom-up context/)

This triple hub-and-spoke suggests a deliberate cross-layer design pattern, not coincidence. Every layer has a single gateway that routes to specialized children.

### X-04: Outline Pipeline Incompleteness

The bottom-up outlines/ analysis found exactly one outline spec (`development-hygiene_outline.json`), which produces `context/development-hygiene.md`. But the `context/` directory contains THREE files. The bottom-up subsystem synthesis asks: "Are there outline specs for the other two context files (`ecosystem-overview.md`, `recipes-usage.md`)? If not, how are those maintained?"

**Implication:** Two of three context files lack synthesis specifications, meaning they are either manually maintained or maintained via a different (undiscovered) mechanism. This breaks the pipeline pattern for 2/3 of the context layer.

### X-05: File-System-Mediated Agent Coordination as Universal Pattern

The agent-constellation investigation reveals that cross-agent coordination occurs exclusively through the file system — agents write to designated directories (`agents/code-tracer/`, `agents/integration-mapper/`), and the synthesizer reads from `agents/*/`. No direct agent-to-agent calls exist. This is the same pattern used by the behavior layer: behaviors reference agents and context via file paths, not programmatic APIs.

**Implication:** The entire agent architecture — from behavior composition to discovery pipeline coordination — relies on file-system paths as the sole coordination mechanism. Path coupling is implicit, not schema-enforced. If directory structures change, coordination breaks silently.

### X-06: Silent Degradation Chain Spans Full Architecture

The top-down subsystem synthesis documents an end-to-end silent degradation chain: "Missing namespace in source_base_paths → @-mention returns None → tier silently absent → expert operates with reduced knowledge → governance rules not loaded → enforcement has no reference." The bottom-up behaviors/ analysis confirms: "If the amplifier bundle is not present in the environment, these behavior bundles produce no value." The documentation-governance investigation found 13 referenced files that don't exist.

**Implication:** At no point in the chain — from missing files to absent tiers to reduced knowledge — does any mechanism surface an error, warning, or degradation notice. The agent simply becomes less knowledgeable, and the user has no way to know.

---

## Open Discrepancies

| ID | Description | Perspective A | Perspective B | Evidence | Status |
|----|------------|---------------|---------------|----------|--------|
| D-01 | **Is amplifier-dev-behavior ever loaded?** | Bottom-up subsystem: `bundle.md` only includes `amplifier:behaviors/amplifier-expert` — `amplifier-dev` is not referenced | Bottom-up behaviors/: `amplifier-dev.yaml` exists as a complete behavior bundle with `context.include: amplifier:context/development-hygiene.md` | The file exists and is structurally valid, but no investigation stream found any reference that loads it. It could be (a) auto-discovered by the bundle loader, (b) referenced by an external bundle not examined, or (c) orphaned. | **OPEN** |
| D-02 | **Is the dual-layer description pattern enforced or conventional?** | Bottom-up agents/: flags that "Whether this two-layer description pattern is enforced or just conventional is unclear from a single file" | Top-down bundle-composition: describes `Bundle.compose()` parsing at bundle.py:176-211 but does not address agent description parsing specifically; agent-constellation code-tracer confirms 7 agents all follow the pattern | The YAML frontmatter + Markdown body format appears in all examined agent files across two bundles, but no schema or validation enforces it. Cross-bundle consistency suggests a strong convention, but no mechanical enforcement has been found. | **OPEN** |
| D-03 | **Content and constraints of common-agent-base.md** | Bottom-up agents/: "Its content could impose additional operating constraints not apparent from this file alone" | Top-down expert-knowledge: flags as D-03 "content was not examined by any investigation stream" | The agent appends `@foundation:context/shared/common-agent-base.md` at the end of its instructions. This file was NOT read by any investigation stream. It could add safety guardrails, tool instructions, or operating constraints that modify the effective agent behavior. | **OPEN** |
| D-04 | **Eager vs. lazy loading of directory @-mentions** | Top-down subsystem: flags as highest-impact unresolved question — "determines whether the expert's system prompt is ~20KB or ~200KB" | Bottom-up agents/: lists directory @-mentions (`@core:docs/`, `@foundation:context/`) as references but does not investigate resolution behavior | The agent uses 5 directory-level @-mentions. Whether `@core:docs/` eagerly loads all files in that directory or lazily resolves individual paths at query time has massive token budget implications. No stream traced the resolver code for directory arguments. | **OPEN** |

### Resolution Recommendations

- **D-01:** Trace `BundleRegistry._load_single()` for bundle discovery behavior — does it scan directories for all YAML files, or only load explicitly included bundles? Alternatively, search the entire ecosystem for references to `amplifier-dev-behavior` or `amplifier:behaviors/amplifier-dev`.
- **D-02:** Read the bundle parser in amplifier-foundation to determine whether YAML frontmatter extraction is a required parsing step or an optional convention. Examine additional agent definitions across other bundles (amplifier-foundation, amplifier-core, amplifier-bundle-recipes) to see if the pattern is truly universal or if exceptions exist.
- **D-03:** Read `amplifier-foundation/context/shared/common-agent-base.md` and document its contents. This is a simple file read — no code tracing required.
- **D-04:** Read `amplifier-foundation/amplifier_foundation/mentions/resolver.py` and trace `_resolve_mention()` for directory path arguments. Determine if `os.listdir()` or equivalent is called for directory-level @-mentions. This is the **highest-priority discrepancy** — it determines the expert's actual token footprint.

---

## Open Questions

1. **What is the actual token cost of a fully-resolved agent session?** No measurement exists. The context files suggest ~20KB, but directory-level @-mentions could expand to ~200KB. The top-down subsystem synthesis recommends instrumenting the system prompt factory.

2. **How do peer spoke experts discover each other?** The hub agent routes to `core:core-expert`, `foundation:foundation-expert`, and `recipes:recipe-author`. Whether these agents are defined in parallel `agents/` directories within their respective bundles — and whether this is a consistent structural pattern — remains unverified.

3. **Why does the outline pipeline cover only 1 of 3 context files?** If `ecosystem-overview.md` and `recipes-usage.md` lack outline specifications, they may drift from the refinement pipeline's quality standards.

4. **What happens when the sole agent is absent?** If `amplifier-expert-behavior` fails to load (missing namespace, malformed YAML), there is no fallback knowledge routing. Is this an acceptable degradation mode or a critical gap?

5. **Are the 13 broken doc links in docs/ affecting the agent's knowledge tiers?** The documentation-governance investigation found 13 referenced files that don't exist. If the expert's Tier 1 `@amplifier:docs/` mentions resolve these broken links, they silently return nothing — compounding the silent degradation chain.

6. **Are unknowns.md files consumed by any mechanism?** The agent-constellation integration-mapper notes that investigation agents write `unknowns.md` files, but no agent reads them. Whether unknowns feed back into future investigation cycles or are informational-only is unspecified.

7. **What is the actual recipes-usage.md inclusion status?** The behavior YAML comments it out as a "soft reference (load on demand)," while the agent's instruction text says "see amplifier:context/recipes-usage.md (load on demand)." Whether this means never injected, injected via a different path, or loaded only when explicitly referenced during conversation is unresolved.

---

## Agent Coverage Assessment

| Perspective | Source | Coverage |
|-------------|--------|----------|
| File structure & content | Bottom-up agents/, behaviors/, context/, outlines/ | Detailed file-by-file analysis |
| Cross-module data flows | Bottom-up subsystem, top-down subsystem | Comprehensive flow mapping |
| Bundle composition mechanics | Top-down bundle-composition (code-tracer) | Code-level evidence from amplifier-foundation |
| Knowledge delivery chain | Top-down expert-agent-knowledge | Full synthesis across 4 streams |
| Agent definition patterns (cross-bundle) | Agent-constellation code-tracer, integration-mapper | 7 agents across dot-graph bundle analyzed |
| Agent coordination mechanisms | Agent-constellation integration-mapper | File-system handoff, recipe dispatch, quality gates |
| Runtime behavior | None | **GAP** — no execution-based verification |

**Critical Gap:** No investigation stream launched the agent, observed actual system prompt assembly, measured token counts, or tested degradation behavior. All findings are based on code reading and documentation analysis. The agent-constellation unknowns from both code-tracer and integration-mapper reinforce this gap — questions about runtime model dispatch, cross-step context transfer, and synthesizer retry semantics all require execution-based verification to resolve.
