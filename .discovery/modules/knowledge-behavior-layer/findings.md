# Synthesized Findings: Knowledge and Behavior Layer

## Consensus Findings

### 1. Three-Level Behavior Composition
The bundle composes via a 3-level chain:
`bundle.md → dot-graph.yaml → [dot-core.yaml + dot-discovery.yaml]`
dot-discovery also includes dot-core, creating potential double-inclusion.
**Confidence: HIGH** — directly verified from YAML files.

### 2. dot-core is the Foundation
dot-core provides the essential infrastructure: tool-dot-graph (6 operations) +
tool-skills (serves 5 skills) + dot-author + diagram-reviewer.
Every session using this bundle gets dot-core's capabilities.
**Confidence: HIGH** — YAML structure is unambiguous.

### 3. Skills Are Served via External Tool Module
The 5 skills are NOT loaded into the session context directly.
They're served via `tool-skills` (an external module) using skill URLs pointing to this repo.
This means: skill content is dynamically loaded on demand, not baked in.
**Confidence: HIGH** — behavior YAML config shows URL references.

### 4. Context Files Always Injected
`dot-awareness.md` is referenced from bundle.md — it's always in context.
`discovery-awareness.md` is in dot-discovery.yaml — only for discovery sessions.
These files give every agent DOT graph awareness by default.
**Confidence: HIGH** — YAML structure confirms injection.

### 5. External GitHub URL Dependencies
Both `tool-dot-graph` and `tool-skills` are loaded from GitHub URLs at session startup.
This creates a network dependency. The tools reference `@main` (latest), meaning changes
to the GitHub repo immediately affect all sessions — no version pinning.
**Confidence: HIGH** — observed URL patterns in behavior YAML.

## Open Discrepancies

### Discrepancy A: Missing context files
Code-tracer noted `discovery-awareness.md` was not found in the repo scan.
Integration-mapper also couldn't find it.
**Unresolved:** Is `discovery-awareness.md` missing from the repo or is it in a location
that wasn't scanned (e.g., context/ directory excluded from directory tree)?

### Discrepancy B: Double-inclusion behavior
Both agents noted dot-discovery includes dot-core AND dot-graph includes both.
**Unresolved:** If a session includes dot-graph (which includes both), are dot-core
tools and agents registered twice? The deduplication mechanism is unknown.
