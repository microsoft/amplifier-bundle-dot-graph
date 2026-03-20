# Module Synthesis: Documentation Governance & Awareness Hierarchy

**Module**: Documentation Governance & Awareness Hierarchy
**Scope**: `amplifier/docs/`, `amplifier/context/`, `amplifier/outlines/`, governance enforcement in `amplifier/recipes/`
**Investigation sources**: 6 bottom-up level synthesizers (docs, context, outlines, behaviors, agents, recipes) + 1 top-down subsystem synthesizer
**Fidelity**: standard
**Date**: 2026-03-19

---

## Executive Summary

The Documentation Governance module comprises three core directories (`docs/`, `context/`, `outlines/`) plus enforcement mechanisms in `recipes/` that together define where documentation lives, how it reaches AI agents, and how compliance is checked. The dominant finding across all 7 investigation sources is that governance operates through **advisory convention rather than mechanical enforcement** — the "Golden Rule" (dependency-based awareness) has zero automated checking, enforcement recipes run manually and check only surface-level boilerplate, and the content delivery mechanism (@-mention protocol) degrades silently when namespaces are missing. MODULES.md is a single point of failure consumed by 3 recipes via 3 independent fetch mechanisms with no abstraction layer. Only 1 of 3 context files has an outline specification, breaking the generation pipeline pattern for 2/3 of the context layer.

---

## Consensus Findings

| ID | Finding | Sources Confirming | Confidence |
|----|---------|-------------------|------------|
| C-01 | REPOSITORY_RULES.md is the governance anchor but is isolated from peer documentation | bottom-up/docs, topdown/subsystem | HIGH |
| C-02 | MODULES.md is a single point of failure (SPOF) consumed via 3 independent fetch mechanisms | bottom-up/docs, bottom-up/recipes, topdown/subsystem | HIGH |
| C-03 | Context files form a balanced ~6.5KB injection triad (architecture/operations/recipes) | bottom-up/context, bottom-up/behaviors | HIGH |
| C-04 | Document generation is a two-stage manual-handoff pipeline (outline → document) | bottom-up/outlines, bottom-up/recipes | HIGH |
| C-05 | @-mention protocol is the sole delivery mechanism for all governance content | bottom-up/agents, bottom-up/behaviors, topdown/subsystem | HIGH |
| C-06 | Hub-and-spoke navigation pattern governs both docs and agent architecture | bottom-up/docs, bottom-up/agents | HIGH |
| C-07 | Governance enforcement is advisory/periodic, never automated/continuous | bottom-up/recipes, topdown/subsystem | HIGH |
| C-08 | `foundation:zen-architect` is the universal agent dependency across all 6 recipes | bottom-up/recipes, topdown/subsystem | HIGH |
| C-09 | YAML frontmatter convention is incomplete (6/10 docs files have it, 4 do not) | bottom-up/docs | MEDIUM |
| C-10 | 13+ broken documentation references exist (files/dirs referenced but not present) | bottom-up/docs | MEDIUM |
| C-11 | Model tier strategy (haiku/sonnet/opus) is copy-pasted across recipes with no central definition | bottom-up/recipes | MEDIUM |
| C-12 | Outline specs encode a 37-repo allowed_source_repos scope gate with no visible enforcement mechanism | bottom-up/outlines | MEDIUM |
| C-13 | Only 1 of 3 context files has an outline spec — pipeline coverage is 33% | bottom-up/outlines, topdown/subsystem | MEDIUM |

### C-01: REPOSITORY_RULES.md — Governance Anchor, Peer Isolate

REPOSITORY_RULES.md (585 lines, 18KB) defines the core governance principles: single source of truth, link-don't-duplicate, dependency-based awareness (the "Golden Rule"), and the awareness hierarchy by repository type. The bottom-up docs/ synthesizer found it "isolated from the cross-reference graph" — no peer documents link to or from it. The top-down subsystem synthesis confirmed it as a Tier 1 @-mention reference loaded by the amplifier-expert agent, making the @-mention protocol its only delivery path to AI agents.

**Evidence**: bottom-up/docs §Governance Layer (Standalone Meta-Docs); topdown/subsystem Flow 5 (Governance Rules → Expert Agent).

### C-02: MODULES.md — Ecosystem Registry SPOF

MODULES.md (25KB, 323 lines) is the canonical registry of all Amplifier ecosystem repositories. Three enforcement recipes consume it through three independent mechanisms: `curl -sL` from GitHub raw URL (repo-audit), `curl` + URL extraction (ecosystem-audit), and `gh api` + `base64 -d` (ecosystem-activity-report). No abstraction layer exists — each recipe independently implements its own fetch. The top-down synthesis explicitly classifies this as **TIGHT coupling**: "all fetches bypass `amplifier:` namespace resolution. No abstraction layer. Each recipe independently implements its own fetch."

**Evidence**: topdown/subsystem Flow 5 (MODULES.md Bypass — TIGHT); bottom-up/recipes Connection 1 and 2; bottom-up/docs finding (25KB largest doc, living catalog).

### C-03: Context Injection Triad

The `context/` directory contains three nearly identically sized files (~6.3–6.7KB each) forming a coordinated knowledge injection layer: `ecosystem-overview.md` (architectural orientation), `development-hygiene.md` (operational safety), `recipes-usage.md` (workflow execution). The bottom-up context/ synthesizer identified this as a "Documentation Knowledge Triad" with deliberate size budgeting. The bottom-up behaviors/ synthesizer confirmed these are consumed via behavior bundles: `amplifier-dev-behavior` injects `development-hygiene.md`, `amplifier-expert-behavior` injects `ecosystem-overview.md`.

Additionally, both `ecosystem-overview.md` and `recipes-usage.md` embed **specialist delegation tables** that route readers to deeper experts (`amplifier-expert`, `foundation-expert`, `core-expert`, `recipe-author`), implementing a shallow-context-then-delegate pattern.

**Evidence**: bottom-up/context §Boundary Pattern (Documentation Knowledge Triad + Specialist Delegation Registry); bottom-up/behaviors §Boundary Patterns.

### C-04: Two-Stage Document Generation Pipeline

The `outlines/` directory holds structured JSON specifications (currently 1 file: `development-hygiene_outline.json`) that drive LLM-based document generation. The outline spec draws from two upstream source documents (`docs/LOCAL_DEVELOPMENT.md` — 12 section references, `docs/USER_ONBOARDING.md` — 4 section references) and targets `context/development-hygiene.md` as output. The `document-generation.yaml` recipe reads the outline as mandatory input. This pipeline requires manual user handoff between stages — it is not an automated recipe invocation chain.

**Evidence**: bottom-up/outlines §Boundary Patterns; bottom-up/recipes Connection 3.

### C-05: @-mention as Sole Governance Delivery Mechanism

All governance content reaches AI agents exclusively through the @-mention protocol (`parse_mentions()` → `BaseMentionResolver` → `ContentDeduplicator` → system prompt assembly). REPOSITORY_RULES.md is loaded via `@amplifier:docs/REPOSITORY_RULES.md`. Context files are loaded via `context.include` in behavior YAMLs. If the resolver fails or a namespace is missing, agents operate without governance knowledge silently — no errors, no warnings, no fallback.

**Evidence**: topdown/subsystem Flow 3 (@-mention Delivery Chain); bottom-up/agents §Boundary Patterns; bottom-up/behaviors findings.

### C-06: Hub-and-Spoke Navigation

Two independent investigation streams identified hub-and-spoke as the dominant navigation pattern:
- **Documentation**: README.md functions as multi-audience hub routing to user tier, developer trilogy, and ecosystem docs (bottom-up/docs)
- **Agent architecture**: amplifier-expert.md functions as gateway agent routing to spoke experts (core-expert, foundation-expert, recipe-author) (bottom-up/agents)

This parallel structure suggests hub-and-spoke is a deliberate cross-layer design pattern, not coincidence.

**Evidence**: bottom-up/docs §Hub-and-Spoke Navigation; bottom-up/agents §Ecosystem Router / Gateway Agent.

### C-07: Advisory Governance — No Continuous Enforcement

All governance enforcement is either:
- **Advisory**: expert agent provides guidance, not blocking enforcement
- **Periodic**: recipes run manually, not on every commit or PR
- **Narrow**: only boilerplate compliance is checked (README sections, MODULES.md listing)

The "Golden Rule" (dependency-based awareness) — the most important governance principle — has zero mechanical enforcement anywhere. The top-down synthesis explicitly flags this: "The enforcement gap means the most important governance principle is advisory-only."

**Evidence**: topdown/subsystem §Emergent Patterns §4 (Infrastructure Robustness vs. Policy Fragility); bottom-up/recipes §Pattern 3 (Staged Recipes).

### C-08: Universal Agent Dependency — `foundation:zen-architect`

`foundation:zen-architect` is used by all 6 recipes in the recipes/ directory for analysis, synthesis, content generation, and report writing. `foundation:explorer` is the second most widespread (4 of 6 recipes). This creates a universal shared dependency: zen-architect's behavior, capabilities, and model selection directly affect every governance recipe's output.

**Evidence**: bottom-up/recipes §Shared Agent Usage table; topdown/subsystem Flow 4.

### C-09: Incomplete Frontmatter Convention [single-source: bottom-up/docs]

Six of ten docs/ files carry structured YAML frontmatter with `last_updated`, `status`, and `audience` fields. Four files lack it: MODULES.md, DEVELOPER.md, REPOSITORY_RULES.md, and ADR_TEMPLATE.md. Notable: the governance anchor itself (REPOSITORY_RULES.md) does not follow the metadata convention it implicitly governs.

**Evidence**: bottom-up/docs §Files and Symbols table.

### C-10: 13+ Broken Documentation References [single-source: bottom-up/docs]

Multiple referenced files do not exist: SCENARIO_TOOLS_GUIDE.md, TROUBLESHOOTING.md, AMPLIFIER_AS_LINUX_KERNEL.md, three `context/` philosophy docs (KERNEL_PHILOSOPHY.md, IMPLEMENTATION_PHILOSOPHY.md, MODULAR_DESIGN_PHILOSOPHY.md), and the `decisions/` and `schemas/` directories. These represent either planned-but-unbuilt content or relocated content with stale references.

**Evidence**: bottom-up/docs §Missing References table (13 distinct items).

### C-11: Model Tier Strategy — Copy-Pasted Convention [single-source: bottom-up/recipes]

Three recipes (`document-generation`, `repo-activity-analysis`, `ecosystem-activity-report`) use per-step model selection (haiku for parsing/classification, sonnet for analysis/synthesis, opus for generation). This cost-optimization strategy is encoded independently in each recipe with no central `model-tiers.yaml` or shared include. Each recipe can drift independently.

**Evidence**: bottom-up/recipes §Pattern 5 (Model Tier Strategy).

### C-12: Outline Scope Gate Without Enforcement [single-source: bottom-up/outlines]

The `development-hygiene_outline.json` spec lists 37 Amplifier ecosystem repositories in its `allowed_source_repos` field, intended to scope which repos may contribute source material during LLM-based generation. However, the enforcement mechanism for this gate is not visible from the outline alone — the generation pipeline must enforce it, but no investigation source has traced whether it does.

**Evidence**: bottom-up/outlines §Structural Decomposition; §Uncertainties §4.

### C-13: Incomplete Pipeline Coverage

Only 1 of 3 context files has an outline specification (`development-hygiene.md`). The other two (`ecosystem-overview.md`, `recipes-usage.md`) lack synthesis specs, breaking the generation pipeline pattern for 2/3 of the context layer. Without outline specs, these files have no reproducible generation process and may drift from quality standards that the pipeline enforces.

**Evidence**: topdown/subsystem Flow 1 ("Only 1 of 3 context files has an outline specification"); bottom-up/outlines §Uncertainties §1 ("Is this a growing collection, or a one-off?").

---

## Cross-Cutting Insights

### XC-01: Convention-Over-Code as Deliberate Architecture

Every layer of the documentation governance system relies on convention rather than code enforcement:
- Knowledge hierarchy tier priority is natural language instruction, not runtime enforcement
- Governance rules are prose principles, not automated checks
- Expert routing is convention in agent descriptions, not code
- Content budget management is informal sizing, not token counting
- Model tier strategy is copy-pasted YAML, not a shared configuration
- Rate limiting patterns are locally encoded per-recipe

Only two mechanisms are code-enforced across the entire governance stack: the @-mention resolver and ContentDeduplicator. This consistency across all 7 investigation sources suggests a deliberate architectural decision (convention-first design), not accumulated technical debt.

**Sources**: topdown/subsystem §Emergent Patterns §2; bottom-up/context, bottom-up/behaviors, bottom-up/agents, bottom-up/recipes.

### XC-02: Silent Degradation Chain Spans All Governance Layers

Missing prerequisites propagate silently across all governance layers without any error or warning:

```
Missing namespace in source_base_paths
  → @-mention returns None
    → governance tier silently absent
      → expert agent operates with reduced knowledge
        → governance rules not loaded
          → enforcement has no reference standard
```

This chain crosses docs/ (content origin), context/ (injection layer), behaviors/ (composition), agents/ (consumption), and recipes/ (enforcement). No diagnostic exists at any stage to detect the broken chain. The top-down synthesis identifies the compound point: if `BundleModuleResolver` fails to mount (non-fatal, warning only), ALL @-mention resolution fails, meaning ALL governance content vanishes with no error at the delivery layer.

**Sources**: topdown/subsystem §Emergent Patterns §5 (Silent Degradation Chain); bottom-up/behaviors §Uncertainties §4 (namespace coupling).

### XC-03: Parallel Governance Systems Without Cross-Reference

Three governance documents operate independently across the ecosystem:
1. `REPOSITORY_RULES.md` (amplifier repo) — awareness hierarchy, Golden Rule
2. `CONTEXT_POISONING.md` (amplifier-foundation) — context contamination prevention
3. `DOCUMENTATION_LINKING.md` (amplifier-core) — linking practices

No cross-reference connects these three systems. They could diverge without detection.

**Sources**: topdown/subsystem §Recommended Investigation §5.

### XC-04: Document Generation Maturity as Complexity Indicator

The document-generation recipe has gone through 8+ major versions (v8.1.0, 126KB, 3,033 lines with detailed in-file CHANGELOG). The outline-generation recipe went through 6 major versions with a CRITICAL FIX at v1.6.0 to correctly classify documents. This evolution trajectory — visible from both bottom-up (recipes/ findings) and top-down (subsystem synthesis) — indicates that mechanically encoding governance principles into executable pipelines is genuinely difficult and requires extensive iteration.

**Sources**: bottom-up/recipes §Uncertainty §5; topdown/subsystem Flow 7.

### XC-05: Specialist Delegation as Knowledge Compression Pattern

Both the agent layer and the context injection layer implement the same knowledge compression pattern: provide shallow orientation, then delegate to deeper specialists rather than duplicating their documentation. In agents, `amplifier-expert` routes to `core-expert`, `foundation-expert`, and `recipe-author`. In context files, delegation tables route readers to the same specialists. This parallel delegation structure is a cross-layer pattern reinforcing the hub-and-spoke architecture (C-06) beyond the navigation layer into the knowledge delivery layer itself.

**Sources**: bottom-up/agents §Ecosystem Router / Gateway Agent; bottom-up/context §Specialist Delegation Registry.

### XC-06: Circular Content Lifecycle (Subsystem-Level Pattern)

The top-down synthesis reveals a circular lifecycle visible only when all module components are viewed together:

```
Documentation Governance (defines rules)
  → Context Layer (refines into token-optimized context)
    → Expert Agent (distills + routes via 5-tier hierarchy)
      → @-mention Protocol (delivers via system prompt)
        → Enforcement Recipes (check compliance + generate new docs)
          → cycle repeats
```

This cycle means that documentation is generated by recipes that are informed by the documentation they generate. The generation pipeline's 8+ major versions suggest this circular dependency is difficult to stabilize.

**Sources**: topdown/subsystem §Emergent Patterns §1 (Circular Content Lifecycle).

---

## Discrepancy Register

| ID | Description | Agents Involved | Impact | Status |
|----|-------------|----------------|--------|--------|
| D-01 | Governance scope: centralized vs. distributed | bottom-up/docs vs. topdown/subsystem | MEDIUM | OPEN |
| D-02 | Content budget: deliberate strategy vs. ad hoc sizing | bottom-up/context + bottom-up/behaviors vs. topdown/subsystem | MEDIUM | OPEN |
| D-03 | @-mention directory loading: eager vs. lazy | topdown/subsystem (unresolved) | HIGH | OPEN |
| D-04 | amplifier-dev-behavior: loaded or orphaned? | bottom-up/behaviors vs. topdown/subsystem | MEDIUM | OPEN |

### D-01: Governance Scope — Centralized or Distributed?

**Bottom-up/docs claim**: "REPOSITORY_RULES.md describes rules for the entire amplifier ecosystem (all repos). Why is it located in docs/ of a single repo? Is it mirrored?" — implies centralized governance in a single repo is anomalous.

**Top-down/subsystem claim**: Cross-repo governance includes CONTEXT_POISONING.md (foundation) and DOCUMENTATION_LINKING.md (core) as parallel governance documents — implies governance is actually distributed across repos with no coordination mechanism.

**Neither source resolves** whether REPOSITORY_RULES.md is the canonical source that others should reference, or whether distributed governance is intentional.

**Impact**: MEDIUM — determines whether governance drift between repos is a design flaw or an expected consequence.

**Resolution needed**: Survey all Amplifier ecosystem repos for governance-related documents. Determine whether cross-repo linking or synchronization exists.

### D-02: Content Budget — Deliberate or Ad Hoc?

**Bottom-up/context claim**: "sizes are nearly identical (~6300–6700 bytes each), suggesting deliberate design: these files are balanced, peer-level context documents" and "uniformity suggests a deliberate content budget for context injection."

**Bottom-up/behaviors claim**: "demoted to load-on-demand; an intentional demotion suggesting bundle authors manage context budget consciously" (re: recipes-usage.md being commented out in amplifier-expert.yaml).

**Top-down/subsystem claim**: "No token budget enforcement — full 5-tier resolution could exhaust context window" and recommends "Measure the full token budget: Instrument the system prompt factory to log token counts."

**Neither side has evidence** of a documented budget policy. The bottom-up sources infer deliberate sizing from observed uniformity; the top-down source observes no enforcement mechanism. Both could be true (informal budget with no enforcement).

**Impact**: MEDIUM — if context budget is deliberate, the ~6.5KB sizing is a design constraint to preserve; if ad hoc, the system may silently degrade as content grows.

**Resolution needed**: (1) Search for any documented context budget policy or sizing guideline. (2) Measure actual token cost of full governance content resolution. (3) Check git history for commit messages explaining the recipes-usage.md demotion rationale.

### D-03: Eager vs. Lazy @-mention Directory Loading

**Top-down/subsystem claim**: This is flagged as the highest-impact unresolved question — "Whether directory @-mentions (e.g., @amplifier:docs/) are eagerly or lazily loaded." If eager, every agent session that loads the amplifier-expert agent pays the full governance token cost (~90K characters from docs/ directory alone). If lazy, content is resolved on-demand.

**No investigation source has traced the resolver code** to determine the actual behavior. This discrepancy was identified in the top-down subsystem synthesis but remains unresolved by any investigation source.

**Impact**: HIGH — determines the practical token cost of governance content in every session. An eager load of all docs/ (~130KB+ across 10 files) could consume a significant fraction of the context window.

**Resolution needed**: Read `amplifier-foundation/amplifier_foundation/mentions/resolver.py` and trace the behavior of `_resolve_mention()` when given a directory path like `@amplifier:docs/`. Determine whether it lists and loads all files, loads only the directory listing, or defers loading to specific file requests.

### D-04: amplifier-dev-behavior — Loaded or Orphaned?

**Bottom-up/behaviors claim**: `amplifier-dev-behavior` (amplifier-dev.yaml) exists as a "Pure context-injection behavior — no agent, no tools; only injects a context document." Its uncertainty §1 asks: "Who composes these behaviors?" and notes "no inclusions within this directory pointing inward."

**Top-down/subsystem claim**: Flow 2 explicitly states: "Open question: is `amplifier-dev-behavior` ever loaded? No reference found in `bundle.md` or elsewhere."

**Both sources agree it exists** but neither found evidence it is actually loaded in any bundle composition. If it is never loaded, `development-hygiene.md` is injected only through the document generation pipeline (as output target), not as agent context — creating a dead path in the governance delivery chain.

**Impact**: MEDIUM — if the behavior is orphaned, operational safety knowledge (including the critical "NEVER: rm -rf ~/.amplifier/cache/" warning) may never reach agent sessions.

**Resolution needed**: (1) Search `bundle.md` and all bundle YAML files for references to `amplifier-dev-behavior`. (2) Trace `BundleRegistry._load_single()` to determine if it scans directories for all YAML files or only loads explicitly included bundles.

---

## Open Questions

1. **Enforcement gap feasibility**: Is the absence of Golden Rule enforcement a deliberate design choice (advisory governance is sufficient) or an unsolved engineering problem? The 8-version evolution of document-generation suggests mechanical enforcement is hard, not impossible.

2. **Outline pipeline completeness**: Only 1 outline spec exists (`development-hygiene_outline.json`). What drives the creation of new outlines? Are `ecosystem-overview.md` and `recipes-usage.md` manually maintained or awaiting their own outline specs?

3. **DEVELOPER.md reliability**: This file has an explicit caveat that it is "more aspirational and forward-looking than accurate today." It is loaded as AI agent context. How do agents distinguish aspirational from accurate content?

4. **Broken reference remediation**: Are the 13+ missing referenced files planned content, relocated content, or abandoned references? No investigation source traced their history.

5. **Frontmatter adoption**: Will the 4 governance/ecosystem files (REPOSITORY_RULES.md, MODULES.md, DEVELOPER.md, ADR_TEMPLATE.md) adopt the frontmatter convention? The governance anchor lacking its own metadata convention creates an inconsistency signal.

6. **App-layer spawn path**: The boundary between `delegate tool` and `PreparedBundle.spawn()` — mediated by `session_spawner.py` in `amplifier-app-cli` — is a blind spot. The behavior at spawn time that determines what governance content reaches child sessions is unverified.

7. **allowed_source_repos enforcement**: The outline spec's 37-repo scope gate has no visible enforcement. Does the generation pipeline actually restrict sources, or is this field advisory documentation?

8. **Naming variance in recipe contracts**: The `create_fix_prs` (plural) vs `create_fix_pr` (singular) naming inconsistency between the ecosystem-audit orchestrator and repo-audit worker is a symptom of the convention-over-code architecture (XC-01). How many similar contract mismatches exist?

9. **Outline source reference staleness**: The outline spec references specific content in source documents. The bottom-up/outlines synthesizer notes: "Since the outline's prompts reference specific line numbers in source files, it can become stale." No freshness-checking mechanism exists.

---

## Recommended Next Steps

1. **Resolve D-03 (eager vs. lazy loading)**: Trace the @-mention resolver implementation. This is the highest-impact open question — it determines the governance system's practical token cost.

2. **Resolve D-04 (amplifier-dev-behavior activation)**: Search all bundle manifests for references. If orphaned, either wire it into the composition or remove the dead behavior file.

3. **Measure full governance token budget**: Instrument the system prompt factory to log token counts when all tiers resolve with recursive loading. No measurement currently exists.

4. **Survey parallel governance systems**: Catalog all governance-related documents across the Amplifier ecosystem. Determine if REPOSITORY_RULES.md, CONTEXT_POISONING.md, and DOCUMENTATION_LINKING.md are intentionally independent or accidentally divergent.

5. **Abstract MODULES.md access**: The 3 independent fetch mechanisms are the most significant tight coupling. An `amplifier:docs/MODULES.md` @-mention would align with existing patterns and eliminate the bypass.

6. **Complete outline pipeline**: Create outline specs for `ecosystem-overview.md` and `recipes-usage.md` to achieve full pipeline coverage across the context triad.

7. **Audit broken references**: For each of the 13+ missing references, determine if the target was never created, relocated, or removed. Update references or create placeholder content.
