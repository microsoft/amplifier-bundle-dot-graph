# Discovery Pipeline

You have access to a codebase discovery pipeline that systematically generates DOT graph representations of code architecture.

## When to Use Discovery

- **New codebase onboarding** — automatically map the architecture before diving in
- **Architecture documentation** — generate and maintain up-to-date architectural diagrams
- **Change impact analysis** — understand how changes propagate through the system
- **Multi-module understanding** — map how components integrate across boundaries

## Fidelity Tiers

Discovery runs at three fidelity tiers: `quick` (patch affected files only), `standard` (2 agents per topic with consensus), `deep` (3 agents per topic with full reconciliation). Default is `standard`.

## Available Capabilities

**Investigation Agents:**
- `discovery-prescan` — selects investigation topics from structural inventory
- `discovery-code-tracer` — HOW: traces execution paths with file:line evidence
- `discovery-behavior-observer` — WHAT: catalogs 10+ real instances, quantifies patterns
- `discovery-integration-mapper` — WHERE/WHY: maps cross-boundary connections
- `discovery-synthesizer` — reconciles multi-agent outputs into consensus DOT

**Recipes:** `discovery-pipeline` (full orchestrated pipeline with approval gates)

## Delegation

- **Codebase discovery** (generate architecture diagrams from code): delegate to `discovery-orchestrator`. It translates natural language investigation requests into the correct pipeline recipe invocation (quick or deep `discovery-pipeline`). Do NOT invoke discovery agents or pipeline recipes directly — the orchestrator handles routing based on fidelity signal.
