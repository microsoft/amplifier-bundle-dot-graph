# Code-Tracer Unknowns: Knowledge and Behavior Layer

1. **context/discovery-awareness.md** — Referenced in dot-discovery.yaml but not found in the repo's context/ directory during scan. Is this file missing or was it not scanned?

2. **tool-skills module** — Referenced in dot-core.yaml but not in this repo. External module. What does it do exactly? How does it serve skill content to agents?

3. **Skills loading** — Are skills loaded lazily (on demand via load_skill tool) or eagerly (at session start)? The discovery agents reference @dot-graph:skills/* in their prompts.

4. **Behavior composition order** — When dot-discovery includes dot-core, does it extend or override core behavior? What if they both define the same agent name?

5. **context/dot-awareness.md** — Referenced from bundle.md as inline content. This file provides context to any agent using the bundle but its contents were not examined.
