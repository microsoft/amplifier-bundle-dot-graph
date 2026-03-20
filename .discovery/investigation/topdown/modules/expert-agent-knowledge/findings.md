# Synthesis: Expert Agent Knowledge Architecture

**Module:** Expert Agent Knowledge Architecture
**Scope:** `amplifier/agents/`, `amplifier/behaviors/`, `amplifier/context/`, `amplifier/outlines/`
**Investigation streams synthesized:** 8 (bottom-up agents/, bottom-up behaviors/, bottom-up context/, bottom-up outlines/, bottom-up subsystem synthesis, top-down subsystem synthesis, agent-behavior-architecture module synthesis, primary source verification)
**Source verification:** All consensus findings verified against primary source files
**Fidelity:** standard
**Date:** 2026-03-20

---

## Executive Summary

The Expert Agent Knowledge Architecture is a convention-driven, documentation-only knowledge delivery system centered on a single hub agent (`amplifier-expert.md`, 15,131 bytes) that aggregates cross-ecosystem knowledge via a 5-tier @-mention hierarchy and routes deep questions to 3 spoke experts. Eight investigation streams converge on 10 consensus findings: the knowledge hierarchy is purely documentary with no runtime enforcement, the @-mention protocol is the sole delivery mechanism with silent degradation on failure, the behavior layer implements a deliberate thin-bundle pattern with active/passive split, and a multi-stage context pipeline transforms dense documentation into token-efficient agent context. Four open discrepancies remain — the most significant being whether directory-level @-mentions eagerly load all contents or lazily resolve individual files, with ~10x token budget implications (~20KB vs ~200KB system prompt).

---

## Consensus Findings

### C-01: 5-Tier @-mention Knowledge Hierarchy (HIGH confidence)

**Sources:** bottom-up agents/, top-down subsystem synthesis, bottom-up subsystem synthesis, primary source verification

All investigation streams independently identify a tiered knowledge hierarchy in `amplifier-expert.md` organized as @-mention references:

| Tier | Namespace | Content Domain | Dir @-mentions | File @-mentions |
|------|-----------|---------------|----------------|-----------------|
| 0 | `@core:docs/` + `@core:docs/specs/` | Kernel internals (~2600 lines) | 2 | 3 |
| 1 | `@amplifier:docs/` | Entry-point documentation (user guides, MODULES.md, REPOSITORY_RULES.md) | 1 | 6 |
| 2 | `@foundation:docs/` + `examples/` + `behaviors/` + `agents/` | Foundation library (bundle composition, patterns, API reference) | 4 | 4 |
| 3 | `@foundation:context/` | Core philosophy (kernel philosophy, modular design, context poisoning) | 1 | 4 |
| 4 | `@recipes:docs/` + `@recipes:examples/` | Multi-step workflow documentation and examples | 2 | 0 |

Primary source verification confirms **28 @-mentions total** in the agent file (10 directory-level standalone, 18 file-level inline), plus 1 outside the tier system (`@foundation:context/shared/common-agent-base.md` at line 389). The interaction between directory and file-level @-mentions (deduplication behavior) is unresolved (see D-01).

**@-mention count discrepancy note:** Prior bottom-up analyses counted 22 @-mentions (10 directory + 12 file). Source re-verification found 18 file-level mentions, not 12. The additional 6 are Tier 1 `@amplifier:` file references (lines 85-90: README.md, USER_GUIDE.md, USER_ONBOARDING.md, DEVELOPER.md, MODULES.md, REPOSITORY_RULES.md). Whether the @-mention parser resolves inline list-item references vs. only standalone-line references is itself an open question tied to D-01.

### C-02: Hub-and-Spoke Agent Routing Architecture (HIGH confidence)

**Sources:** bottom-up agents/, top-down subsystem synthesis, bottom-up subsystem synthesis, primary source verification

The `amplifier-expert` agent acts as a central ecosystem router (hub) that delegates deep-domain questions to three spoke experts:

- `core:core-expert` — deep kernel contracts, module protocols, kernel-vs-module decisions (lines 75, 356)
- `foundation:foundation-expert` — bundle composition and examples (lines 114, 357)
- `recipes:recipe-author` — multi-step workflows (line 358)

All streams agree routing is **convention-based** — the expert's instruction text describes when to delegate (e.g., "When to consult core:core-expert"), but no code enforces routing rules. The bottom-up agents/ stream names this the "Ecosystem Router / Gateway Agent" pattern. The expert also provides context TO other agents (lines 360-364): zen-architect for architecture principles, modular-builder for implementation patterns.

### C-03: Convention-Over-Code Architecture (HIGH confidence)

**Sources:** top-down subsystem synthesis, bottom-up agents/, bottom-up behaviors/, agent-behavior-architecture module synthesis

Every investigation stream independently identifies that the knowledge architecture relies on conventions rather than code enforcement:

- **Tier priority:** Natural language instruction ordering, not runtime enforcement
- **Expert routing:** Hub-and-spoke is convention in agent descriptions, not coded dispatch
- **Mode dispatch:** RESEARCH/GUIDE/VALIDATE modes are trigger-phrase conventions, not classified inputs
- **Thin/heavy split:** Context gate is behavior YAML pattern, not framework feature
- **Token budget:** Managed by file size balance and manual YAML comment demotion, not measurement

Only two mechanisms are code-enforced across the entire architecture: the @-mention resolver and ContentDeduplicator.

### C-04: Thin Bundle Behavior Pattern (HIGH confidence)

**Sources:** top-down subsystem synthesis, bottom-up behaviors/, bottom-up subsystem synthesis, agent-behavior-architecture module synthesis

The behavior layer (`amplifier/behaviors/`) implements two distinct thin-bundle patterns:

| Bundle | Agent? | Context? | Pattern | Size |
|--------|--------|----------|---------|------|
| `amplifier-expert-behavior` | Yes (`amplifier:amplifier-expert`) | Yes (`ecosystem-overview.md`) | Active capability injection | 348B, 13 lines |
| `amplifier-dev-behavior` | No | Yes (`development-hygiene.md`) | Passive context injection | 202B, 8 lines |

Source verification confirms: `amplifier-expert.yaml` includes both `agents.include` (line 7-8) and `context.include` (line 10-12); `amplifier-dev.yaml` includes only `context.include` (line 6-8). The bottom-up behaviors/ stream explicitly names the "Context-only vs Agent+Context" divergence as an intentional active/passive split.

### C-05: @-mention Protocol as Sole Knowledge Delivery Mechanism (HIGH confidence)

**Sources:** top-down subsystem synthesis, bottom-up subsystem synthesis, bottom-up context/, bundle-composition module synthesis

The @-mention protocol (`parse_mentions()` -> `BaseMentionResolver` -> `ContentDeduplicator`) is the **sole mechanism** by which knowledge reaches agents at runtime. The protocol lives in `amplifier-foundation` (cross-repo dependency), not in this bundle. No alternative delivery mechanism was found by any stream.

The bundle-composition module synthesis confirms the full chain: `Bundle.compose()` produces `source_base_paths` -> `BaseMentionResolver` resolves `@namespace:path` -> `ContentDeduplicator` prevents duplicates -> `SystemPromptFactory` assembles per-request.

### C-06: Multi-Stage Context Pipeline (MEDIUM confidence)

**Sources:** bottom-up subsystem synthesis, bottom-up context/, bottom-up outlines/

Knowledge flows through a multi-stage refinement pipeline:

```
docs/ (authoritative long-form, ~125KB total)
  -> outlines/ (synthesis specifications with section-level prompts)
    -> context/ (agent-optimized ~6.5KB summaries, 3 files)
      -> behaviors/ (session activation declarations)
        -> agents/ (runtime knowledge base consumption)
```

**Confidence reduced to MEDIUM** because only 1 of 3 context files (`development-hygiene.md`) has a corresponding outline specification (`development-hygiene_outline.json`, 15,999 bytes), breaking the pipeline pattern for 2/3 of the context layer. The top-down stream doesn't independently trace this full chain.

### C-07: Silent Degradation Chain (MEDIUM confidence)

**Sources:** top-down subsystem synthesis, bottom-up behaviors/

The top-down synthesis documents a silent degradation chain: "Missing namespace in source_base_paths -> @-mention returns None -> tier silently absent -> expert operates with reduced knowledge -> governance rules not loaded -> enforcement has no reference." The bottom-up behaviors/ analysis notes "If the amplifier bundle is not present in the environment, these behavior bundles produce no value."

**Confidence MEDIUM** — top-down identifies the chain explicitly; bottom-up confirms the conditions but doesn't independently trace the full degradation path.

### C-08: Three Operating Modes with Trigger-Phrase Dispatch (HIGH confidence)

**Sources:** bottom-up agents/, primary source verification

The expert agent implements three activation modes verified at lines 20-48:

- **RESEARCH** — triggered by "what is", "how does", "what can" (line 22)
- **GUIDE** — triggered by "how should I", "what pattern for" (line 32)
- **VALIDATE** — triggered by "is this right", review requests (line 42)

Each mode has a dedicated response template (lines 294-348). The bottom-up agents/ stream names this a "Mode-Dispatched Persona" pattern. Note: the top-down synthesis does not independently identify the three modes, treating the expert as a single entity — this is a single-source finding elevated to HIGH confidence only because primary source verification confirms it.

### C-09: Documentation Knowledge Triad (HIGH confidence)

**Sources:** bottom-up context/, bottom-up subsystem synthesis, primary source verification

The `context/` directory implements a coordinated three-document injection pattern with deliberately balanced file sizes:

| File | Size | Role |
|------|------|------|
| `ecosystem-overview.md` | 6,652 bytes | Architectural orientation |
| `development-hygiene.md` | 6,293 bytes | Operational safety |
| `recipes-usage.md` | 6,703 bytes | Recipe invocation guide |

The near-identical sizes (~6.3-6.7KB) suggest a deliberate content budget for context injection. The bottom-up context/ stream explicitly names this the "Documentation Knowledge Triad" pattern and identifies `ecosystem-overview.md` as the hub file that references concepts detailed by the other two.

### C-10: Dual Common-Base Includes (HIGH confidence — source-verified)

**Sources:** primary source verification (bundle.md and amplifier-expert.md)

Two distinct common-base files are included at different composition levels:

| File | Included By | Level | Line |
|------|-------------|-------|------|
| `@foundation:context/shared/common-system-base.md` | `bundle.md` | Bundle composition — applies to all sessions | line 90 |
| `@foundation:context/shared/common-agent-base.md` | `amplifier-expert.md` | Agent instructions — appended to agent text | line 389 |

Neither file's content was examined by any investigation stream (see D-03).

---

## Cross-Cutting Insights

### X-01: Documentation-as-Architecture Anti-Fragility Risk

The entire knowledge architecture is documentation — no executable code, no tests, no runtime verification. This creates a paradox: the system is extremely flexible (any change to knowledge is a text edit) but has zero mechanical protection against drift, staleness, or contradiction between tiers. The only guard against context poisoning is a philosophy document about context poisoning (`CONTEXT_POISONING.md`) loaded as Tier 3 knowledge.

**Evidence:** Top-down identifies this as "Advisory Governance." Bottom-up agents/ notes the expert's "canonical vocabulary" (module types table, decision frameworks, anti-pattern list) is defined only in the agent's instruction text. The module type system explicitly excludes the agent layer from validation, caching, and lifecycle management (confirmed by agent-behavior-architecture and ecosystem-governance module syntheses).

### X-02: Token Budget as Unmonitored Architectural Constraint

Multiple streams identify token budget as a critical concern with no measurement infrastructure:

- The behavior YAML **deliberately demotes** `recipes-usage.md` from `context.include` to a comment (line 13), showing conscious token management
- The primary source uses **10 directory-level @-mentions** that could expand to large content volumes
- Source re-verification reveals **28 total @-mentions** (10 directory + 18 file), more than the "5 tiers" framing suggests
- The context files are deliberately balanced at ~6.5KB each, suggesting conscious budgeting
- Per-request prompt assembly with no caching (confirmed by bundle-composition module synthesis: "System prompt factory re-reads context files on every request")

The tension: architects clearly think about token budgets (evidence: demotion, balanced file sizes), but no measurement or enforcement mechanism exists. The actual token cost of full tier resolution is unknown. This is directly tied to D-01.

### X-03: Single-Agent Knowledge Monopoly

Only one agent definition exists in `agents/` — `amplifier-expert.md` (15,131 bytes). The entire ecosystem's knowledge routing depends on this single instruction document. If malformed, stale, or absent, all knowledge routing fails with no fallback. The top-down synthesis independently identifies a five-SPOF chain spanning four modules. This 15KB file is the critical junction where all ecosystem knowledge is aggregated and distributed.

### X-04: Incomplete Outline Pipeline Undermines Reproducibility

Only 1 of 3 context files has a corresponding outline specification (`development-hygiene_outline.json` -> `context/development-hygiene.md`). The other two context files (`ecosystem-overview.md`, `recipes-usage.md`) lack synthesis specs. This means two of the three Knowledge Triad documents cannot be reproducibly regenerated from source documentation — they must be maintained manually, creating asymmetric maintenance burden and drift risk.

---

## Discrepancy Register

| ID | Description | Impact | Status |
|----|------------|--------|--------|
| D-01 | Eager vs. lazy loading of directory @-mentions | HIGH | OPEN |
| D-02 | recipes-usage.md inclusion status | MEDIUM | OPEN |
| D-03 | common-agent-base.md and common-system-base.md content | MEDIUM | OPEN |
| D-04 | amplifier-dev-behavior activation path | MEDIUM | OPEN |

### D-01: Eager vs. Lazy Loading of Directory @-mentions (HIGH)

**Perspective A (top-down):** Flags this as unresolved: "Whether @amplifier:docs/ eagerly loads ~90K characters or lazily resolves" — determines ~20KB vs ~200KB prompt.

**Perspective B (bottom-up agents/):** Lists directory @-mentions as external references but does not investigate resolution behavior.

**Perspective C (bottom-up subsystem):** Calls it "lazy read" without execution-based evidence.

**Evidence:** Primary source uses 10 directory-level @-mentions. Resolution behavior determines whether the expert's system prompt is ~20KB or ~200KB — a 10x difference. Additionally, 18 file-level @-mentions may or may not be separately resolved depending on parser behavior — if the resolver only handles standalone-line mentions, many file references are purely documentary; if it resolves inline mentions, significant additional content is loaded.

**Resolution needed:** Read `amplifier-foundation/amplifier_foundation/mentions/resolver.py` and trace `_resolve_mention()` for directory arguments. Determine if `os.listdir()` or equivalent is called. Alternatively, instrument a session and measure actual system prompt size.

### D-02: recipes-usage.md Inclusion Status (MEDIUM)

**Perspective A (bottom-up behaviors/):** Notes the YAML comment "demoted to soft reference (load on demand)."

**Perspective B (bottom-up agents/):** Identifies the file in the expert's instruction text (line 154): "see amplifier:context/recipes-usage.md (load on demand)" — suggests the agent instructs users to request it.

**Evidence:** Behavior YAML line 13 reads `# recipes-usage.md demoted to soft reference (load on demand) - see amplifier-expert.md`. Agent text line 154 says "see `amplifier:context/recipes-usage.md` (load on demand)." Bundle.md line 86 also references it: `see @amplifier:context/recipes-usage.md for detailed instructions`.

**Resolution needed:** Instrument a real session with `amplifier-expert-behavior` loaded and observe whether `recipes-usage.md` content appears in the system prompt. Alternatively, trace `Bundle.compose()` to determine how commented-out YAML lines are handled.

### D-03: common-agent-base.md and common-system-base.md Content (MEDIUM)

**Perspective A (bottom-up agents/):** Flags: "Its content could impose additional operating constraints not apparent from this file alone."

**Perspective B (top-down, bottom-up subsystem):** Lists as external dependencies but doesn't examine content.

**Evidence:** Two distinct shared files are appended at different levels: `common-system-base.md` to `bundle.md` (line 90) and `common-agent-base.md` to `amplifier-expert.md` (line 389). Neither was examined by any investigation stream.

**Resolution needed:** Simple file reads of both files in `amplifier-foundation/context/shared/`. No code tracing required.

### D-04: amplifier-dev-behavior Activation (MEDIUM)

**Perspective A (bottom-up behaviors/):** Asks "Who composes these behaviors?" — no internal references load it.

**Perspective B (top-down):** Notes `bundle.md` only includes `amplifier:behaviors/amplifier-expert` (line 9) — no reference to `amplifier-dev` found.

**Evidence:** The `amplifier-dev-behavior` bundle exists (202 bytes, `behaviors/amplifier-dev.yaml`) but no investigation stream found any reference that loads it. It may be (a) auto-discovered by the bundle loader via directory scanning, (b) explicitly referenced by an external bundle, or (c) orphaned.

**Resolution needed:** Trace `BundleRegistry._load_single()` to determine whether the bundle loader scans directories for all YAML files or only loads explicitly included bundles. The bundle-composition module synthesis confirms three entry points funnel into `_load_single()` but doesn't address auto-discovery of sibling bundles.

---

## Open Questions

1. **What is the actual token cost of full tier resolution?** No measurement exists. Given the 28 @-mentions (10 directory-level + 18 file-level), the actual cost could be dramatically different from the ~20KB suggested by the three context files alone.

2. **How do peer experts discover each other?** The expert routes to `core:core-expert`, `foundation:foundation-expert`, and `recipes:recipe-author`. Are these agents defined in parallel `agents/` directories within their respective bundles?

3. **What happens when the expert is absent?** If the behavior fails to load (missing namespace, malformed YAML), there is no fallback knowledge routing. Is this an acceptable degradation mode?

4. **Are broken doc links affecting the expert?** If the expert's Tier 1 @-mentions resolve broken links in docs/, they would silently return nothing — compounding the silent degradation problem identified in C-07.

5. **Why does only 1 of 3 context files have an outline spec?** Is the pipeline incomplete, or are the other two maintained through a different mechanism?

6. **Does the @-mention parser resolve inline vs. standalone references differently?** This determines the true @-mention count (22 vs 28) and significantly affects token budget calculations.

---

## Agent Coverage Assessment

| Perspective | Source | Coverage |
|-------------|--------|----------|
| File-level structure | Bottom-up agents/, behaviors/, context/, outlines/ | Detailed file-by-file analysis across all 4 leaf directories |
| Cross-module integration | Top-down subsystem synthesis, bottom-up subsystem synthesis | Comprehensive data flow mapping |
| Behavioral patterns | Bottom-up agents/ (mode dispatch, gateway pattern) | Partial — single file, not runtime |
| Content pipeline | Bottom-up outlines/, bottom-up context/ | Pipeline traced from spec to output |
| Peer module context | Agent-behavior-architecture module synthesis | Cross-module consensus on shared findings |
| Runtime behavior | None | **GAP** — no execution-based verification |

**Missing:** No investigation stream performed runtime verification — launching the agent, observing actual system prompt assembly, measuring token counts, or testing degradation behavior. All findings are based on code reading and documentation analysis. Execution-based verification would resolve D-01 and D-02 definitively.

---

## Recommended Next Steps

1. **Resolve eager vs. lazy loading (D-01)** — Trace `_resolve_mention()` in `amplifier-foundation/amplifier_foundation/mentions/resolver.py` for directory arguments. This is the highest-impact open question across the entire investigation.

2. **Measure full token budget** — Instrument system prompt factory to log token counts when all 5 tiers resolve. No measurement exists.

3. **Read common-base files (D-03)** — Simple file reads of `common-system-base.md` and `common-agent-base.md` in `amplifier-foundation/context/shared/`. Low effort, resolves a medium-impact blind spot.

4. **Verify amplifier-dev-behavior activation (D-04)** — Trace `BundleRegistry._load_single()` for bundle discovery behavior.

5. **Complete outline pipeline (X-04)** — Create outline specs for `ecosystem-overview.md` and `recipes-usage.md` to enable reproducible regeneration.
