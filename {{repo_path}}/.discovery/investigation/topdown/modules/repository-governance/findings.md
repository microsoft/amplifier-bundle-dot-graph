# Module Synthesis: Repository Governance & Awareness Hierarchy

**Module**: Repository Governance & Awareness Hierarchy
**Scope**: `amplifier/docs/REPOSITORY_RULES.md` (awareness hierarchy definition), `amplifier/docs/MODULES.md` (ecosystem registry), governance enforcement in `amplifier/recipes/`, cross-repo governance documents (CONTEXT_POISONING.md, DOCUMENTATION_LINKING.md), delivery via @-mention protocol through `amplifier/agents/`, `amplifier/behaviors/`, `amplifier/context/`
**Investigation sources**: 3 triplicate agents dispatched (code-tracer, behavior-observer, integration-mapper) produced no artifacts; synthesis drawn from primary source files and 3 prior module syntheses (documentation-governance, ecosystem-governance, top-down subsystem) totaling 11+ independent investigation perspectives
**Fidelity**: standard
**Date**: 2026-03-19

---

## Executive Summary

REPOSITORY_RULES.md defines a strict dependency-based awareness hierarchy governing what each of 6 repository types (Entry Point, Kernel, Libraries, Applications, Bundles, Modules) may reference, forming a directed acyclic graph (DAG) intended to prevent context poisoning through documentation duplication. This hierarchy is the architectural contract binding the entire multi-repo Amplifier ecosystem. However, all investigation perspectives converge on a critical finding: the hierarchy has **zero mechanical enforcement** of its most important principle (the "Golden Rule" -- dependency-based awareness). Enforcement recipes check only surface-level boilerplate compliance. The governance rules reach AI agents exclusively through the @-mention protocol, creating a single delivery path where silent failures can cause governance knowledge to vanish entirely. Three parallel governance documents exist across separate repositories (REPOSITORY_RULES.md, CONTEXT_POISONING.md, DOCUMENTATION_LINKING.md) with no cross-reference or coordination mechanism. Four discrepancies remain open, including whether the awareness DAG is actually respected across the ecosystem -- no comprehensive audit has ever been performed.

---

## Consensus Findings

| ID | Finding | Sources Confirming | Confidence |
|----|---------|-------------------|------------|
| C-01 | Dependency-based awareness hierarchy defines a strict DAG of allowed references | primary source (REPOSITORY_RULES.md), doc-governance C-01, ecosystem-governance C-05 | HIGH |
| C-02 | The "Golden Rule" has zero mechanical enforcement | doc-governance C-07, ecosystem-governance C-05, subsystem Flow 5/6 | HIGH |
| C-03 | REPOSITORY_RULES.md is the canonical governance document but is peer-isolated | doc-governance C-01, ecosystem-governance C-03, primary source | HIGH |
| C-04 | @-mention protocol is the sole delivery mechanism for governance rules to AI agents | doc-governance C-05, ecosystem-governance C-03, subsystem Flow 2/3 | HIGH |
| C-05 | Three parallel governance systems exist without cross-reference | doc-governance XC-03, ecosystem-governance D-02 | HIGH |
| C-06 | MODULES.md is a single point of failure consumed via 3 independent bypass mechanisms | doc-governance C-02, ecosystem-governance C-06, subsystem Flow 5 | HIGH |
| C-07 | Enforcement recipes check boilerplate only, not awareness-hierarchy compliance | doc-governance C-07, subsystem Flow 5/6, ecosystem-governance C-05 | HIGH |
| C-08 | 6 repository types form a layered reference permission model | primary source (REPOSITORY_RULES.md), ecosystem-overview.md | HIGH |
| C-09 | Convention-over-code is the dominant governance architecture | doc-governance XC-01, ecosystem-governance C-01, subsystem Emergent Pattern 2 | HIGH |
| C-10 | Silent degradation chain can cause governance to vanish from sessions undetected | doc-governance XC-02, ecosystem-governance C-04, subsystem Emergent Pattern 5 | HIGH |

### C-01: Dependency-Based Awareness Hierarchy Defines a Strict DAG

REPOSITORY_RULES.md (585 lines, 18KB) defines 6 repository types with explicit reference rules forming a directed acyclic graph:

| Repository Type | Can Reference | Cannot Reference |
|----------------|--------------|-----------------|
| **Entry Point** (amplifier) | Everything | -- |
| **Kernel** (amplifier-core) | Only Entry Point | Libraries, modules, apps |
| **Libraries** (amplifier-foundation) | Kernel + Entry + declared dependencies | Anything not in pyproject.toml |
| **Applications** (amplifier-app-cli) | Anything consumed | -- |
| **Bundles** (amplifier-bundle-*) | Modules, libraries (evolving) | -- |
| **Modules** (amplifier-module-*) | Only Kernel (+ possibly Entry) | Peers, libraries, apps |

The document includes a 4-question decision framework for evaluating references: (1) Is this in pyproject.toml? (2) Do I import code from it? (3) Is this amplifier-core and I'm a module/library? (4) Is this the entry point?

**Evidence**: REPOSITORY_RULES.md lines 22-100 (complete hierarchy definition); ecosystem-overview.md (simplified recap of types); doc-governance C-01 (confirmed as governance anchor).

### C-02: Zero Mechanical Enforcement of the Golden Rule

The "Golden Rule" -- a repository can only reference another if it has a declared dependency on it -- is the most important governance principle. Three independent investigation streams confirm it has zero automated checking:

- **Doc-governance C-07**: "All governance enforcement is either advisory (expert agent provides guidance), periodic (recipes run manually), or narrow (test_doc_sweep.sh checks 3 files for model names only)."
- **Ecosystem-governance C-05**: "The 'Golden Rule' has zero automated checking anywhere in the system."
- **Subsystem Flow 5/6**: Enforcement recipes check README sections and MODULES.md listing, not awareness-hierarchy compliance. The Golden Rule is not mechanically testable by any existing recipe.

The enforcement gap is especially notable because REPOSITORY_RULES.md itself includes a validation checklist (lines 452-461) that suggests manual review ("Check for duplication", "Respect the hierarchy") but no tooling to automate these checks.

**Evidence**: doc-governance C-07; ecosystem-governance C-05; REPOSITORY_RULES.md lines 452-461 (manual checklist); subsystem Flow 5 (enforcement bypasses).

### C-03: Canonical Governance Document Is Peer-Isolated

REPOSITORY_RULES.md defines governance for the entire multi-repo ecosystem but exists in a single repository (`amplifier/docs/`). No peer documentation files within the amplifier repo cross-reference it. It reaches AI agents solely through the @-mention protocol as a Tier 1 reference (`@amplifier:docs/REPOSITORY_RULES.md`), loaded as part of the `@amplifier:docs/` directory mention in the amplifier-expert agent.

The document itself acknowledges its location in the entry point repo (line 127: "Contains: Repository rules (this document)") but no mechanism ensures other repos' documentation actually links back to it.

**Evidence**: doc-governance C-01 ("isolated from cross-reference graph"); amplifier-expert.md line 90 (`@amplifier:docs/REPOSITORY_RULES.md` listed as Tier 1 key document); bundle.md line 38-39 (listed under "Repository Governance").

### C-04: @-mention Protocol as Sole Governance Delivery Path

All governance content reaches AI agents exclusively through the @-mention protocol (`parse_mentions()` -> `BaseMentionResolver` -> `ContentDeduplicator` -> system prompt assembly). REPOSITORY_RULES.md is delivered via `@amplifier:docs/`. Context files are loaded via `context.include` in behavior YAMLs. If the resolver fails or a namespace is missing, agents operate without governance knowledge silently.

The amplifier-expert.md agent explicitly references governance docs at Tier 1 (line 82-90) and includes REPOSITORY_RULES.md as a key document. The bundle.md includes `@amplifier:docs/` as a directory-level mention (line 29).

**Evidence**: doc-governance C-05; ecosystem-governance C-03; amplifier-expert.md lines 77-90; bundle.md line 29.

### C-05: Three Parallel Governance Systems Without Cross-Reference

Three governance documents operate independently across the ecosystem with no coordination:

1. **REPOSITORY_RULES.md** (amplifier repo) -- Awareness hierarchy, Golden Rule, reference permissions
2. **CONTEXT_POISONING.md** (amplifier-foundation repo) -- Context contamination prevention philosophy
3. **DOCUMENTATION_LINKING.md** (amplifier-core repo) -- Linking practices and standards

These documents address overlapping concerns (preventing documentation drift, managing cross-repo references) but do not reference each other. They could diverge without detection.

**Evidence**: doc-governance XC-03 (identified as cross-cutting insight); ecosystem-governance D-02 (flagged as open discrepancy).

### C-06: MODULES.md as Single Point of Failure

MODULES.md (25KB, 322 lines) is the canonical ecosystem registry consumed by 3 enforcement recipes through 3 independent fetch mechanisms that all bypass the @-mention namespace:

| Recipe | Mechanism | Bypass Type |
|--------|-----------|-------------|
| repo-audit | `curl -sL` from GitHub raw URL | Direct HTTP |
| ecosystem-audit | `curl` + URL extraction | Direct HTTP |
| ecosystem-activity-report | `gh api` + `base64 -d` | GitHub API |

The @-mention protocol (`@amplifier:docs/MODULES.md`) exists precisely to abstract content delivery, yet the most critical shared dependency bypasses it entirely. Format changes to MODULES.md would break silently across all three recipes.

**Evidence**: doc-governance C-02; ecosystem-governance C-06; subsystem Flow 5.

### C-07: Enforcement Recipes Check Boilerplate Only

The repo-audit and ecosystem-audit recipes check surface-level compliance:
- Does the README have required sections?
- Is the repo listed in MODULES.md?
- Are model names present in certain files?

They do NOT check:
- Whether a repo's documentation references only its declared dependencies (the Golden Rule)
- Whether cross-repo links follow the awareness hierarchy
- Whether content duplication exists between repos
- Whether link targets actually exist

**Evidence**: doc-governance C-07; subsystem Flow 5/6; ecosystem-governance C-05.

### C-08: Six Repository Types Form a Layered Reference Permission Model

The awareness hierarchy defines 6 distinct repository types with increasingly permissive reference rights:

```
Modules (most restricted) -> Kernel -> Libraries -> Bundles -> Applications -> Entry Point (least restricted)
```

This layering is not arbitrary -- it mirrors the dependency graph. Modules depend only on the kernel, so they may only reference the kernel. The entry point has visibility into the entire ecosystem, so it may reference everything. The discipline prevents lower layers from creating circular references or assumptions about higher layers.

**Evidence**: REPOSITORY_RULES.md lines 43-51 (table); lines 116-224 (detailed per-type definitions).

### C-09: Convention-Over-Code as Dominant Governance Architecture

Every layer of the governance system relies on convention rather than code:
- **Awareness rules**: Prose principles in REPOSITORY_RULES.md, not automated checks
- **Content placement**: Decision tree in documentation, not tooling enforcement
- **Link patterns**: Recommended patterns (GitHub URLs), not validation
- **Audit cadence**: "Quarterly review" recommendation, not automated scheduling
- **Knowledge hierarchy**: Natural language tier priority in amplifier-expert.md, not runtime enforcement

Only two mechanisms are code-enforced: the @-mention resolver and ContentDeduplicator.

**Evidence**: doc-governance XC-01; ecosystem-governance C-01; subsystem Emergent Pattern 2.

### C-10: Silent Degradation Chain

Missing prerequisites propagate silently across governance layers:

```
Module-source-resolver fails to mount (logger.warning only)
  -> @-mention namespace unavailable
    -> REPOSITORY_RULES.md not loaded
      -> amplifier-expert operates without governance knowledge
        -> Enforcement recipes have no reference standard
          -> Governance silently absent from all sessions
```

No diagnostic exists at any stage to detect the broken chain.

**Evidence**: doc-governance XC-02; ecosystem-governance C-04; subsystem Emergent Pattern 5.

---

## Cross-Cutting Insights

### XC-01: The Awareness DAG Is Architecturally Sound but Operationally Invisible

The dependency-based awareness hierarchy defines a clean DAG that correctly mirrors the code dependency graph. Its 6 repository types and 4-question decision framework are well-designed governance primitives. However, the DAG exists only in prose -- it is not encoded as data (no machine-readable awareness matrix), not validated by tooling, and not visualized in any operational dashboard. The governance architecture is sound in theory but invisible in practice.

**Sources**: REPOSITORY_RULES.md (complete hierarchy definition); all investigation streams confirming zero enforcement.

### XC-02: Governance Documents Violate Their Own Principles

REPOSITORY_RULES.md states "Docs are contract -- documentation defines what code must implement" (principle 6, line 19). Yet the document itself has no contract-enforcement mechanism. It also states "Single source of truth -- Content lives in ONE place" (principle 1, line 13), but three governance documents across three repos cover overlapping concerns without cross-referencing. The governance system does not satisfy its own stated principles.

Additionally, REPOSITORY_RULES.md lacks the YAML frontmatter convention (last_updated, status, audience) that 6 of the 10 other docs/ files follow (doc-governance C-08). The governance anchor does not comply with its sibling files' metadata standard.

**Sources**: REPOSITORY_RULES.md lines 13-19; doc-governance C-08 (frontmatter inconsistency); doc-governance XC-03 (parallel governance systems).

### XC-03: The Amplifier Bundle Itself Is the Governance Hub

The `amplifier` repo's `bundle.md` is the entry point bundle that includes `amplifier-foundation` and the `amplifier-expert-behavior`. This means the bundle composition chain -- `bundle.md` -> `amplifier-expert-behavior.yaml` -> `amplifier-expert.md` -> `@amplifier:docs/` -> `REPOSITORY_RULES.md` -- is the sole pathway by which governance rules enter any AI session. The amplifier bundle IS the governance delivery vehicle. Any modification to this composition chain (removing the behavior include, changing the agent's @-mentions, or renaming the docs directory) would silently disconnect governance from all sessions.

**Sources**: bundle.md (composition chain); amplifier-expert.yaml (behavior includes); amplifier-expert.md (5-tier hierarchy); ecosystem-governance C-03 (sole delivery mechanism).

### XC-04: Bundles Have the Loosest Governance Rules -- by Design or Omission

REPOSITORY_RULES.md states bundles have "looser rules, evolving" for what they can reference (line 176). This is the only repository type with explicitly qualified governance rules. Given that bundles are the primary composition mechanism for AI agent sessions, this looseness means the layer with the most direct impact on agent behavior has the least governance constraint. Whether this is intentional flexibility or incomplete governance is an open question.

**Sources**: REPOSITORY_RULES.md line 176; ecosystem-overview.md (bundles as composition packages).

---

## Discrepancy Register

| ID | Description | Sources Involved | Status | Impact |
|----|-------------|-----------------|--------|--------|
| D-01 | Is zero enforcement deliberate or unsolved? | doc-governance OQ-1, ecosystem-governance OQ-1 | OPEN | HIGH |
| D-02 | Is the awareness DAG actually respected across the ecosystem? | No investigation source has audited | OPEN | HIGH |
| D-03 | Governance scope: centralized vs. distributed | doc-governance D-01, ecosystem-governance D-02 | OPEN | MEDIUM |
| D-04 | How do child sessions inherit governance awareness? | ecosystem-governance OQ-3 | OPEN | MEDIUM |

### D-01: Is Zero Enforcement Deliberate or Unsolved?

**Claim A (implied by architecture)**: The convention-over-code pattern is consistent across ALL governance layers, suggesting a deliberate design philosophy. The "advisory governance" model may be intentional -- the ecosystem trusts contributors to follow rules without automation.

**Claim B (implied by evolution)**: The document-generation recipe required 8+ major versions (v8.1.0) to stabilize, and the outline-generation recipe needed a CRITICAL FIX at v1.6.0. This evolution trajectory suggests that mechanically encoding governance principles is genuinely difficult, not that it was intentionally avoided. The validation checklist in REPOSITORY_RULES.md (lines 452-461) suggests the authors wanted enforcement but settled for manual checklists.

**Impact**: HIGH -- determines whether the enforcement gap is a design decision to preserve or an engineering debt to address.

**Resolution needed**: Interview the REPOSITORY_RULES.md authors or check commit history for any comments about enforcement. Alternatively, prototype a minimal Golden Rule linter that checks pyproject.toml dependencies against cross-repo documentation references.

### D-02: Is the Awareness DAG Actually Respected?

**Claim A (assumed by governance)**: The hierarchy is described authoritatively, implying it is followed. The validation checklist suggests contributors should verify compliance.

**Claim B (no evidence either way)**: No investigation source has ever audited whether real repositories respect the awareness hierarchy. It is possible that modules reference peer modules, libraries reference apps, or the kernel references foundation -- all violations that would be invisible without a cross-repo audit. The only enforcement checks (repo-audit, ecosystem-audit) verify boilerplate, not awareness compliance.

**Impact**: HIGH -- if the hierarchy is widely violated, the governance system is aspirational documentation, not an architectural contract.

**Resolution needed**: Perform a cross-repo audit: for each Amplifier ecosystem repository, extract all cross-repo references (GitHub URLs, @-mentions, import statements) and validate them against the awareness DAG defined in REPOSITORY_RULES.md.

### D-03: Governance Scope -- Centralized or Distributed?

**Claim A (doc-governance D-01)**: REPOSITORY_RULES.md describes rules for the entire ecosystem but lives in a single repo. This centralization is anomalous for a multi-repo system.

**Claim B (ecosystem-governance D-02)**: Three governance documents operate independently across the ecosystem (REPOSITORY_RULES.md, CONTEXT_POISONING.md, DOCUMENTATION_LINKING.md). Governance is actually distributed with no coordination mechanism. Neither centralized nor distributed -- it's fragmented.

**Impact**: MEDIUM -- determines whether governance drift between repos is a design flaw or expected consequence.

**Resolution needed**: Survey all Amplifier ecosystem repos for governance-related documents. Determine whether REPOSITORY_RULES.md is the canonical source that others should reference, or whether each repo independently defines governance.

### D-04: How Do Child Sessions Inherit Governance Awareness?

**Claim A (implied by architecture)**: Every `type: agent` recipe step triggers full bundle recomposition including @-mention resolution (subsystem Flow 4). This suggests child sessions should receive the same governance content as parent sessions.

**Claim B (no verification)**: The boundary between `delegate tool` and `PreparedBundle.spawn()` -- mediated by `session_spawner.py` in `amplifier-app-cli` -- is a blind spot across all investigations. Whether child sessions actually receive governance content via @-mention resolution during spawn is unverified.

**Impact**: MEDIUM -- if child sessions do not inherit governance, multi-agent workflows operate without governance constraints.

**Resolution needed**: Trace the spawn path in `amplifier-app-cli/session_spawner.py` to determine whether child bundle composition includes `@amplifier:docs/` resolution.

---

## Open Questions

1. **Does the "evolving" bundle governance actually evolve?** REPOSITORY_RULES.md line 176 says bundles have "looser rules, evolving." Is there a tracking mechanism for this evolution? Has the rule been updated since initial authoring?

2. **What is the practical compliance rate?** Without a cross-repo audit, the awareness hierarchy's effectiveness is unknown. Even a sampling-based audit (check 5 random modules for peer references) would provide signal.

3. **Could the awareness DAG be encoded as machine-readable data?** A `governance-matrix.json` or similar artifact could express the DAG programmatically, enabling automated checking. The 4-question decision framework maps cleanly to a lookup table.

4. **How does the hierarchy handle transitive dependencies?** If Library A depends on Library B, can Library A reference Library B's dependencies? REPOSITORY_RULES.md specifies "declared dependency" (in pyproject.toml) but is silent on transitive dependencies.

5. **Should REPOSITORY_RULES.md live in the entry point repo?** As the canonical governance source for all repos, it is consumed primarily by the @-mention protocol from the amplifier bundle. Moving it to its own repo or making it a shared governance artifact could reduce the perception of single-repo ownership.

6. **What prevents the ecosystem-overview.md context file from diverging from REPOSITORY_RULES.md?** The context file (6.6KB) contains a simplified recap of the repository types and architecture. No mechanism synchronizes it with the authoritative REPOSITORY_RULES.md (18KB). If they diverge, AI agents receive conflicting governance signals depending on which file they load.

---

## Recommended Next Steps

1. **Perform a cross-repo awareness audit (D-02)** -- This is the highest-value action: validate whether real repositories respect the awareness DAG. Extract cross-repo references from 5-10 repos and check against REPOSITORY_RULES.md rules. This would either confirm governance compliance or reveal systemic violations.

2. **Encode the awareness DAG as machine-readable data** -- Transform the 6-type hierarchy and 4-question decision framework into a JSON/YAML schema that tooling can consume. This is a prerequisite for any automated enforcement.

3. **Prototype a minimal Golden Rule linter** -- A recipe that reads pyproject.toml dependencies and checks docs/ cross-repo references against declared dependencies would close the enforcement gap for the most important governance principle.

4. **Reconcile the three parallel governance documents (D-03)** -- Add cross-references between REPOSITORY_RULES.md, CONTEXT_POISONING.md, and DOCUMENTATION_LINKING.md, or consolidate overlapping concerns.

5. **Add YAML frontmatter to REPOSITORY_RULES.md** -- The governance anchor should comply with its sibling files' metadata convention (last_updated, status, audience).
