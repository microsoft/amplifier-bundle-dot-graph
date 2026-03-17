# Integration-Mapper Unknowns: Knowledge and Behavior Layer

1. **Double-inclusion deduplication** — If a consumer includes both dot-core and dot-discovery, are tools/agents registered twice? The behavior composition spec doesn't clarify deduplication.

2. **context/dot-awareness.md content** — Referenced from bundle.md but contents not examined. What context does every bundle session get by default?

3. **context/discovery-awareness.md content** — Referenced from dot-discovery.yaml but file not found in scan. Is it missing or in a different location?

4. **tool-skills external module** — How does it serve skills? Does it load them into the session context eagerly or serve them via tool calls? The interaction between tool-skills and agent skill-loading is unclear.

5. **Behavior versioning** — dot-core and dot-discovery both reference each other by path. What happens when the bundle is cached and a newer version is published? Are URLs pinned to @main?
