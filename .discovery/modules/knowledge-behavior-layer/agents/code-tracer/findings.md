# Code-Tracer Findings: Knowledge and Behavior Layer

## Behaviors (3 YAML files)

### dot-graph.yaml (top-level behavior, v0.2.0)
```yaml
bundle: dot-graph-behavior
includes:
  - bundle: dot-graph:behaviors/dot-core
  - bundle: dot-graph:behaviors/dot-discovery
```
This is a COMPOSITION behavior — it has no agents/tools of its own.
It's referenced from `bundle.md` as the bundle's default behavior.

### dot-core.yaml (v0.2.0)
```yaml
bundle: dot-graph-core
tools:
  - module: tool-dot-graph              # The 6-operation DOT tool
  - module: tool-skills                 # Skills infrastructure
    config:
      skills:
        - "git+https://github.com/.../amplifier-bundle-dot-graph@main#subdirectory=skills"
agents:
  include:
    - dot-graph:dot-author
    - dot-graph:diagram-reviewer
```
Provides: dot_graph tool + all 5 skills + 2 general DOT agents.

### dot-discovery.yaml (v0.1.0)
```yaml
bundle: dot-graph-discovery
includes:
  - bundle: dot-graph:behaviors/dot-core  # inherits dot-core
agents:
  include:
    - dot-graph:discovery-prescan
    - dot-graph:discovery-code-tracer
    - dot-graph:discovery-behavior-observer
    - dot-graph:discovery-integration-mapper
    - dot-graph:discovery-synthesizer
context:
  include:
    - dot-graph:context/discovery-awareness.md
```
Adds 5 discovery agents + discovery context to the core base.

## Skills (5 directories)
- **dot-syntax**: DOT/Graphviz syntax reference
- **dot-patterns**: Template library (DAG, state machine, layered arch, fan-out, legend)
- **dot-quality**: Quality standards checker  
- **dot-graph-intelligence**: Graph analysis operations (reachability, cycles, paths)
- **dot-as-analysis**: Analysis methodology (draw what you believe, reconcile against reality)

## Bundle Entry Point
`bundle.md`:
```yaml
bundle:
  name: dot-graph
  version: 0.2.0
includes:
  - bundle: dot-graph:behaviors/dot-graph
```
The bundle includes its top-level behavior which composes core + discovery.

## Composition Chain
```
bundle.md → dot-graph.yaml → dot-core.yaml + dot-discovery.yaml
dot-core.yaml → tool-dot-graph + tool-skills (with 5 skills) + dot-author + diagram-reviewer
dot-discovery.yaml → dot-core.yaml + 5 discovery agents + discovery-awareness.md
```
