# Module Synthesis: Documentation Governance and Information Architecture

**Module**: Documentation Governance and Information Architecture
**Scope**: `amplifier/docs/`, `amplifier/context/`, `amplifier/outlines/`, governance enforcement in `amplifier/recipes/`
**Investigation sources**: 6 bottom-up level synthesizers (docs, context, outlines, behaviors, agents, recipes) + 1 top-down subsystem synthesizer
**Agent coverage**: 7 independent investigation perspectives
**Fidelity**: standard
**Date**: 2026-03-19

---

## Executive Summary

The Documentation Governance module comprises three core directories (`docs/`, `context/`, `outlines/`) plus enforcement mechanisms in `recipes/` that together define where documentation lives, how it reaches AI agents, and how compliance is checked. The dominant finding across all 7 investigation sources is that governance operates through **advisory convention rather than mechanical enforcement** — the "Golden Rule" (dependency-based awareness) has zero automated checking, enforcement recipes run manually and check only surface-level boilerplate, and the entire content delivery mechanism (@-mention protocol) degrades silently when namespaces are missing. MODULES.md is a single point of failure consumed by 3 recipes via 3 independent fetch mechanisms with no abstraction layer. The document generation pipeline has required 8+ major versions to stabilize, suggesting that mechanically encoding governance principles is genuinely difficult.

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
| C-08 | YAML frontmatter convention is incomplete (6/10 docs files have it, 4 do not) | bottom-up/docs | MEDIUM |
| C-09 | 13+ broken documentation references exist (files/dirs referenced but not present) | bottom-up/docs | MEDIUM |
| C-10 | Model tier strategy (haiku/sonnet/opus) is copy-pasted across recipes with no central definition | bottom-up/recipes | MEDIUM |
| C-11 | Outline specs encode a 37-repo allowed_source_repos scope gate with no visible enforcement mechanism | bottom-up/outlines | MEDIUM |

### C-01: REPOSITORY_RULES.md — Governance Anchor, Peer Isolate

REPOSITORY_RULES.md (585 lines, 18KB) defines the core governance principles: single source of truth, link-don't-duplicate, dependency-based awareness (the "Golden Rule"), and the awareness hierarchy by repository type. The bottom-up docs/ synthesizer found it "isolated from the cross-reference graph" — no peer documents link to or from it. The top-down subsystem synthesis confirmed it as a Tier 1 @-mention reference loaded by the amplifier-expert agent, making the @-mention protocol its only delivery path to AI agents.

**Evidence**: bottom-up/docs finding "Governance Layer (Standalone Meta-Docs)"; topdown/subsystem Flow 5 (Governance Rules → Expert Agent).

### C-02: MODULES.md — Ecosystem Registry SPOF

MODULES.md (25KB, 323 lines) is the canonical registry of all Amplifier ecosystem repositories. Three enforcement recipes consume it through three independent mechanisms: `curl -sL` from GitHub raw URL (repo-audit), `curl` + URL extraction (ecosystem-audit), and `gh api` + `base64 -d` (ecosystem-activity-report). No abstraction layer exists — each recipe independently implements its own fetch. No reverse-validation against live GitHub state exists.

**Evidence**: topdown/subsystem Flow 4 (MODULES.md Consumption); bottom-up/recipes Connection 1 and 2; bottom-up/docs finding (25KB largest doc, living catalog).

### C-03: Context Injection Triad

The `context/` directory contains three nearly identically sized files (~6.3–6.7KB each) forming a coordinated knowledge injection layer: `ecosystem-overview.md` (architectural orientation), `development-hygiene.md` (operational safety), `recipes-usage.md` (workflow execution). The bottom-up context/ synthesizer identified this as a "Documentation Knowledge Triad" with deliberate size budgeting. The bottom-up behaviors/ synthesizer confirmed these are consumed via behavior bundles: `amplifier-dev-behavior` injects `development-hygiene.md`, `amplifier-expert-behavior` injects `ecosystem-overview.md`.

Additionally, both `ecosystem-overview.md` and `recipes-usage.md` embed **specialist delegation tables** that route readers to deeper experts (`amplifier-expert`, `foundation-expert`, `core-expert`, `recipe-author`), implementing a shallow-context-then-delegate pattern rather than duplicating specialist knowledge.

**Evidence**: bottom-up/context findings §Boundary Pattern (Documentation Knowledge Triad + Specialist Delegation Registry); bottom-up/behaviors findings §Boundary Patterns.

### C-04: Two-Stage Document Generation Pipeline

The `outlines/` directory holds structured JSON specifications (currently 1 file: `development-hygiene_outline.json`) that drive LLM-based document generation. The outline spec encodes section prompts, source file references, model configuration, and allowed source repos. The `document-generation.yaml` recipe reads the outline as mandatory input. This pipeline requires manual user handoff between stages — it is not an automated recipe invocation chain.

**Evidence**: bottom-up/outlines findings §Boundary Patterns; bottom-up/recipes Connection 3.

### C-05: @-mention as Sole Governance Delivery Mechanism

All governance content reaches AI agents exclusively through the @-mention protocol (`parse_mentions()` → `BaseMentionResolver` → `ContentDeduplicator` → system prompt assembly). REPOSITORY_RULES.md is loaded via `@amplifier:docs/REPOSITORY_RULES.md`. Context files are loaded via `context.include` in behavior YAMLs. If the resolver fails or a namespace is missing, agents operate without governance knowledge silently — no errors, no warnings, no fallback.

**Evidence**: topdown/subsystem Flow 1 (@-mention Protocol); bottom-up/agents finding §Boundary Patterns; bottom-up/behaviors findings.

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
- **Narrow**: `test_doc_sweep.sh` checks 3 files for model names only

The "Golden Rule" (dependency-based awareness) — the most important governance principle — has zero mechanical enforcement anywhere. Enforcement recipes check only boilerplate compliance (README sections, MODULES.md listing), not awareness-hierarchy compliance.

**Evidence**: topdown/subsystem §Emergent Patterns §4 (Advisory Governance); bottom-up/recipes §Pattern 3 (Staged Recipes).

### C-08: Incomplete Frontmatter Convention [single-source: bottom-up/docs]

Six of ten docs/ files carry structured YAML frontmatter with `last_updated`, `status`, and `audience` fields. Four files lack it: MODULES.md, DEVELOPER.md, REPOSITORY_RULES.md, and ADR_TEMPLATE.md. Notable: the governance anchor itself (REPOSITORY_RULES.md) does not follow the metadata convention it implicitly governs.

**Evidence**: bottom-up/docs §Files and Symbols table.

### C-09: 13+ Broken Documentation References [single-source: bottom-up/docs]

Multiple referenced files do not exist: SCENARIO_TOOLS_GUIDE.md, TROUBLESHOOTING.md, AMPLIFIER_AS_LINUX_KERNEL.md, three `context/` philosophy docs (KERNEL_PHILOSOPHY.md, IMPLEMENTATION_PHILOSOPHY.md, MODULAR_DESIGN_PHILOSOPHY.md), and the `decisions/` and `schemas/` directories. These represent either planned-but-unbuilt content or relocated content with stale references.

**Evidence**: bottom-up/docs §Missing References table (13 distinct items).

### C-10: Model Tier Strategy — Copy-Pasted Convention [single-source: bottom-up/recipes]

Three recipes (`document-generation`, `repo-activity-analysis`, `ecosystem-activity-report`) use per-step model selection (haiku for parsing/classification, sonnet for analysis/synthesis, opus for generation). This cost-optimization strategy is encoded independently in each recipe with no central `model-tiers.yaml` or shared include. Each recipe can drift independently.

**Evidence**: bottom-up/recipes §Pattern 5 (Model Tier Strategy).

### C-11: Outline Scope Gate Without Enforcement [single-source: bottom-up/outlines]

The `development-hygiene_outline.json` spec lists 37 Amplifier ecosystem repositories in its `allowed_source_repos` field, intended to scope which repos may contribute source material during LLM-based generation. However, the enforcement mechanism for this gate is not visible from the outline alone — the generation pipeline must enforce it, but no investigation source has traced whether it does.

**Evidence**: bottom-up/outlines §Structural Decomposition of development-hygiene_outline.json; §Uncertainties for Next Level Up §4.

---

## Cross-Cutting Insights

### XC-01: Convention-Over-Code as Deliberate Architecture

Every layer of the documentation governance system relies on convention rather than code enforcement:
- Knowledge hierarchy tier priority is natural language instruction, not runtime enforcement
- Governance rules are prose principles, not automated checks
- Expert routing is convention in agent descriptions, not code
- Content budget management is informal sizing, not token counting
- Model tier strategy is copy-pasted YAML, not a shared configuration

Only two mechanisms are code-enforced across the entire governance stack: the @-mention resolver and ContentDeduplicator. This consistency across all investigation sources suggests a deliberate architectural decision (convention-first design), not accumulated technical debt.

**Sources**: topdown/subsystem §Emergent Patterns §1; bottom-up/context, bottom-up/behaviors, bottom-up/agents, bottom-up/recipes.

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

This chain crosses docs/ (content origin), context/ (injection layer), behaviors/ (composition), agents/ (consumption), and recipes/ (enforcement). No diagnostic exists at any stage to detect the broken chain.

**Sources**: topdown/subsystem §Emergent Patterns §2; bottom-up/behaviors §Uncertainties §4 (namespace coupling).

### XC-03: Parallel Governance Systems Without Cross-Reference

Three governance documents operate independently across the ecosystem:
1. `REPOSITORY_RULES.md` (amplifier repo) — awareness hierarchy, Golden Rule
2. `CONTEXT_POISONING.md` (amplifier-foundation) — context contamination prevention
3. `DOCUMENTATION_LINKING.md` (amplifier-core) — linking practices

No cross-reference connects these three systems. They could diverge without detection. The top-down investigation explicitly flagged this: "Reconcile the parallel governance systems — no cross-reference exists."

**Sources**: topdown/subsystem §Recommended Investigation §5; topdown/subsystem Flow 5.

### XC-04: Document Generation Maturity as Complexity Indicator

The document-generation recipe has gone through 8+ major versions (v8.1.0, 126KB, 3,033 lines with detailed in-file CHANGELOG). The outline-generation recipe went through 6 major versions with a CRITICAL FIX at v1.6.0 to correctly classify documents. This evolution trajectory — visible from both bottom-up (recipes/ findings) and top-down (subsystem synthesis) — indicates that mechanically encoding governance principles into executable pipelines is genuinely difficult and requires extensive iteration.

**Sources**: bottom-up/recipes §Uncertainty §5; topdown/subsystem Flow 10.

### XC-05: Specialist Delegation as Knowledge Compression Pattern

Both the agent layer and the context injection layer implement the same knowledge compression pattern: provide shallow orientation, then delegate to deeper specialists rather than duplicating their documentation. In agents, `amplifier-expert` routes to `core-expert`, `foundation-expert`, and `recipe-author`. In context files, delegation tables route readers to the same specialists. This parallel delegation structure is a cross-layer pattern reinforcing the hub-and-spoke architecture (C-06) beyond the navigation layer into the knowledge delivery layer itself.

**Sources**: bottom-up/agents §Ecosystem Router / Gateway Agent; bottom-up/context §Specialist Delegation Registry.

---

## Discrepancy Register

| ID | Description | Impact | Status |
|----|-------------|--------|--------|
| D-01 | Governance scope: centralized vs. distributed | MEDIUM | OPEN |
| D-02 | Content budget: deliberate strategy vs. ad hoc sizing | MEDIUM | OPEN |
| D-03 | @-mention directory loading: eager vs. lazy | HIGH | OPEN |

### D-01: Governance Scope — Centralized or Distributed?

**Bottom-up/docs claim**: "REPOSITORY_RULES.md describes rules for the entire amplifier ecosystem (all repos). Why is it located in docs/ of a single repo? Is it mirrored?" — implies centralized governance is anomalous.

**Top-down/subsystem claim**: Cross-repo governance includes CONTEXT_POISONING.md (foundation) and DOCUMENTATION_LINKING.md (core) as parallel governance documents — implies governance is actually distributed across repos with no coordination mechanism.

**Impact**: MEDIUM — determines whether governance drift between repos is a design flaw or an expected consequence.

**Resolution needed**: Survey all Amplifier ecosystem repos for governance-related documents. Determine whether REPOSITORY_RULES.md is the canonical source that others should reference, or whether each repo independently defines its own governance subset. Check for any cross-repo linking or synchronization mechanism.

### D-02: Content Budget — Deliberate or Ad Hoc?

**Bottom-up/context claim**: "sizes are nearly identical (~6300–6700 bytes each), suggesting deliberate design: these files are balanced, peer-level context documents" and "uniformity suggests a deliberate content budget for context injection."

**Bottom-up/behaviors claim**: "demoted to load-on-demand; an intentional demotion suggesting bundle authors manage context budget consciously" (re: recipes-usage.md being commented out in amplifier-expert.yaml).

**Top-down/subsystem claim**: "No token budget enforcement — full 5-tier resolution could exhaust context window" and recommends "Measure the full token budget: Instrument the system prompt factory to log token counts."

**Impact**: MEDIUM — if context budget is deliberate, the ~6.5KB sizing is a design constraint to preserve; if ad hoc, the system may silently degrade as content grows.

**Resolution needed**: (1) Search for any documented context budget policy or sizing guideline. (2) Measure actual token cost of full governance content resolution. (3) Check if the commented-out `recipes-usage.md` reference was accompanied by a commit message explaining the demotion rationale.

### D-03: Eager vs. Lazy @-mention Directory Loading

**Top-down/subsystem claim**: This is flagged as an unresolved question — "Whether directory @-mentions (e.g., @amplifier:docs/) are eagerly or lazily loaded." If eager, every agent session that loads the amplifier-expert agent pays the full governance token cost (~90K characters from docs/ directory alone). If lazy, content is resolved on-demand.

**No agent has traced the resolver code** to determine the actual behavior. This discrepancy was identified in the top-down subsystem synthesis but remains unresolved by any investigation source.

**Impact**: HIGH — determines the practical token cost of governance content in every session. An eager load of all docs/ (~130KB+ across 10 files) could consume a significant fraction of the context window.

**Resolution needed**: Read `amplifier-foundation/amplifier_foundation/mentions/resolver.py` and trace the behavior of `_resolve_mention()` when given a directory path like `@amplifier:docs/`. Determine whether it lists and loads all files, loads only the directory listing, or defers loading to specific file requests.

---

## Open Questions

1. **Enforcement gap feasibility**: Is the absence of Golden Rule enforcement a deliberate design choice (advisory governance is sufficient) or an unsolved engineering problem? The 8-version evolution of document-generation suggests mechanical enforcement is hard, not impossible.

2. **Outline pipeline completeness**: Only 1 outline spec exists (`development-hygiene_outline.json`). Is this a growing collection or a one-off? What drives the creation of new outlines? Where does the generation runner live?

3. **DEVELOPER.md reliability**: This file has an explicit caveat that it is "more aspirational and forward-looking than accurate today." It is loaded as AI agent context. How do agents distinguish aspirational from accurate content?

4. **Broken reference remediation**: Are the 13+ missing referenced files planned content, relocated content, or abandoned references? No investigation source traced their history.

5. **Frontmatter adoption**: Will the 4 governance/ecosystem files (REPOSITORY_RULES.md, MODULES.md, DEVELOPER.md, ADR_TEMPLATE.md) adopt the frontmatter convention? The governance anchor lacking its own metadata convention creates an inconsistency signal.

6. **App-layer spawn path**: The boundary between `delegate tool` and `PreparedBundle.spawn()` — mediated by `session_spawner.py` in `amplifier-app-cli` — is a blind spot across all investigation sources. The behavior at spawn time that determines what governance content reaches child sessions is unverified.

7. **allowed_source_repos enforcement**: The outline spec's 37-repo scope gate has no visible enforcement. Does the generation pipeline actually restrict sources, or is this field advisory documentation?

8. **Naming variance in recipe contracts**: The `create_fix_prs` (plural) vs `create_fix_pr` (singular) naming inconsistency between the ecosystem-audit orchestrator and repo-audit worker is a symptom of the convention-over-code architecture (XC-01). How many similar contract mismatches exist across other recipe pairs?

---

## Recommended Next Steps

1. **Resolve D-03 (eager vs. lazy loading)**: Trace the @-mention resolver implementation. This is the highest-impact open question — it determines the governance system's practical token cost.

2. **Measure full governance token budget**: Instrument the system prompt factory to log token counts when all tiers resolve with recursive loading. No measurement currently exists.

3. **Survey parallel governance systems**: Catalog all governance-related documents across the Amplifier ecosystem. Determine if REPOSITORY_RULES.md, CONTEXT_POISONING.md, and DOCUMENTATION_LINKING.md are intentionally independent or accidentally divergent.

4. **Audit broken references**: For each of the 13+ missing references, determine if the target was never created, was relocated, or was removed. Update references or create placeholder content.

5. **Prototype Golden Rule enforcement**: The 6-version outline classification evolution suggests that a targeted prototype testing dependency-based awareness checking would be valuable — even if only as a linting recipe, not a blocking gate.
