---
name: parallax-investigation
description: Use when you need true understanding of a complex system — not a quick answer. Parallax Discovery is a multi-agent, multi-pass investigation methodology that combines three perspectives (code tracing, behavior observation, integration mapping) to produce verified, evidence-backed findings.
---

# Parallax Discovery Methodology

## Overview

**Parallax Discovery** is a multi-agent, multi-pass investigation methodology named after astronomical parallax — just as astronomers triangulate depth by observing stars from multiple positions, this methodology triangulates truth by examining code from multiple perspectives.

Use Parallax Discovery when you need **true understanding**, not a quick answer:

- Unfamiliar or complex codebases
- Debugging subtle, intermittent, or cross-cutting issues
- Architecture review before major refactoring
- Onboarding investigation to map system structure
- Security audits requiring evidence-backed findings

A single agent reading code produces a single perspective. Parallax produces three, then reconciles them.

---

## The Three-Perspective Model

Each perspective is a distinct agent role. Together they form a **triplicate team**. All agents in a team run with **fresh context** (`context_depth='none'`) — this is non-negotiable. Prior session state contaminates findings.

### Agent 1: Code Tracer (HOW)
- Traces actual execution paths through source files using LSP
- Uses `goToDefinition`, `incomingCalls`, `outgoingCalls`, `findReferences`
- **Requires file:line evidence** for every significant finding
- Produces `findings.md`, `evidence.md`, `diagram.dot`

### Agent 2: Behavior Observer (WHAT)
- Examines **10+ real instances** minimum — patterns emerge from many, not one
- Catalogs structure, quantifies prevalence, identifies anti-patterns
- Distinguishes what actually exists vs. what documentation claims
- Produces `catalog.md`, `patterns.md`, `findings.md`, `diagram.dot`

### Agent 3: Integration Mapper (WHERE/WHY)
- Maps how mechanisms integrate across component boundaries
- Finds **composition effects** — emergent behavior at boundaries
- Identifies cross-cutting concerns that single-perspective agents miss
- Produces `integration-map.md`, `findings.md`, `diagram.dot`

---

## The No-Fiat Rule

**Discrepancies between agents are valuable signals, not failures.**

When two agents disagree:

1. **Never reconcile by picking the more plausible answer** — this is the no-fiat rule
2. **Assign a tracking ID** (D-01, D-02, D-NN)
3. **Record both claims** with full evidence citations
4. **Mark OPEN** if unresolvable from available evidence
5. Unresolved discrepancies become recommendations for the next wave

A discrepancy marks exactly where design and reality have separated. Suppressing it destroys the investigation's most valuable finding.

---

## Wave Structure

### Wave 1 — Discovery
**Goal:** Cast a wide net. Identify patterns, mechanisms, and boundaries.

- Dispatch triplicate teams per topic (code-tracer + behavior-observer + integration-mapper)
- Each team investigates independently with zero shared context
- DOT diagrams are **discovery tools**, not just outputs — draw what you find
- After all teams complete, lead-investigator reconciles findings across teams

### Wave 2 — Verification
**Goal:** Focused deep dives to resolve discrepancies from Wave 1.

- Targeted investigation of specific D-NN discrepancy items
- `evidence.md` with file:line citations is required for every finding
- Wave 2 produces RESOLVED / PARTIALLY RESOLVED / UNRESOLVED verdicts

### Wave 3 — Adversarial (optional)
**Goal:** Execution-based stress testing of consolidated findings.

- Dispatches **antagonist agents** with no prior findings context
- Writes test scripts and **runs actual code** to prove or disprove claims
- Code reading identifies mechanisms; execution proves impact
- Claims that survive adversarial testing are verified; refuted claims are corrected

---

## Fidelity Tiers

Choose fidelity based on investigation depth required:

| Tier | Agents | Use When |
|------|--------|----------|
| **quick** | 1 agent: code-tracer only | Fast initial scan, time-constrained |
| **standard** | 2 agents: code-tracer + integration-mapper | Default for most investigations |
| **deep** | 3 agents: full triplicate (all three) | High-stakes, unfamiliar, or complex systems |

Default fidelity is **standard**. Use the `fidelity` context variable to override.

---

## Investigation Frames (Lens)

The investigation `lens` context variable focuses agent attention:

| Frame | Lens Value | Focus |
|-------|-----------|-------|
| Architecture | `architecture` | System structure, module boundaries, coupling |
| Security | `security` | Attack surface, data flow, trust boundaries |
| Quality | `quality` | Code health, anti-patterns, technical debt |
| Onboarding | `onboarding` | Entry points, key concepts, learning path |
| Debugging | `debugging` | Failure modes, error paths, state transitions |

---

## Artifact Strategy

Each agent writes to an **isolated subdirectory** — no shared mutable state between agents.

```
.discovery/
  investigation/
    modules/
      {slug}/
        agents/
          code-tracer/
            findings.md
            evidence.md
            diagram.dot
            unknowns.md
          behavior-observer/
            catalog.md
            patterns.md
            findings.md
            diagram.dot
          integration-mapper/
            integration-map.md
            findings.md
            diagram.dot
  output/
    combined.md
    overview.dot
    synthesis.md
```

Artifacts are written **before** reconciliation. The lead-investigator reads all artifacts after the wave completes and produces the reconciliation document.

---

## Deep Reference

For full protocol specifications, see:

- `@parallax-discovery:context/methodology.md` — complete methodology reference
- `@parallax-discovery:context/triplicate-pattern.md` — triplicate team patterns
- `@parallax-discovery:context/artifact-strategy.md` — artifact directory conventions
- `@parallax-discovery:context/wave-protocol.md` — wave execution protocol
