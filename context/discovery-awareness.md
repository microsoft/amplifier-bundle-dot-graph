# Discovery Pipeline

You have access to a codebase discovery pipeline that systematically generates DOT graph representations of code architecture.

## When to Use Discovery

- **New codebase onboarding** — automatically map the architecture before diving in
- **Architecture documentation** — generate and maintain up-to-date architectural diagrams
- **Change impact analysis** — understand how changes propagate through the system

## Available Capabilities

**Agents**: `discovery-prescan` (topic selection), `discovery-code-tracer` (execution paths), `discovery-behavior-observer` (pattern catalog), `discovery-integration-mapper` (boundary mapping), `discovery-synthesizer` (consensus reconciliation)

**Recipes**: `discovery-pipeline` (full orchestrated pipeline with approval gates)

## Delegation

- **Codebase discovery** (generate architecture diagrams from code): delegate to the discovery pipeline recipe. It handles multi-agent investigation, consensus reconciliation, and hierarchical DOT assembly.
