# amplifier-bundle-dot-graph

General-purpose DOT/Graphviz infrastructure for the [Amplifier](https://github.com/microsoft/amplifier) ecosystem — knowledge, tools, and graph intelligence.

## Overview

This bundle provides DOT/Graphviz capabilities to any Amplifier session through a composable behavior. Include it in your bundle to get:

- **Agents**: `dot-author` (graph creation/editing) and `diagram-reviewer` (quality review with PASS/WARN/FAIL verdicts)
- **Tools**: `dot_validate`, `dot_render`, `dot_setup`, `dot_analyze`
- **Skills**: DOT syntax, patterns, analysis-as-reconciliation, quality standards, graph intelligence
- **Docs**: Full DOT language reference, pattern catalog, quality gates, Graphviz setup guide, graph analysis guide

## Usage

**Quick install (recommended):**

```bash
amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-dot-graph@main#subdirectory=behaviors/dot-graph.yaml --app
```

The `--app` flag makes DOT/Graphviz capabilities available across all your sessions automatically.

**Bundle composition:**

For bundle authors who want to include dot-graph in their own bundle:

```yaml
includes:
  - bundle: dot-graph:behaviors/dot-graph
```

This gives your session access to DOT authoring agents, validation/rendering tools, and the full knowledge layer.

## Architecture

The bundle follows a three-tier architecture:

1. **Knowledge Layer** (Tier 1): Skills, docs, context — works with zero dependencies
2. **Validation & Rendering** (Tier 2): Python tool module with `dot_validate`, `dot_render`, `dot_setup`
3. **Graph Intelligence** (Tier 3): NetworkX-backed analysis operations via `dot_analyze`

## Development

Run tests:

```bash
# Root-level bundle verification tests
python -m pytest tests/

# Module-level tests (requires PYTHONPATH)
cd modules/tool-dot-graph && python -m pytest
```

## Contributing

> [!NOTE]
> This project is not currently accepting external contributions, but we're actively working toward opening this up. We value community input and look forward to collaborating in the future. For now, feel free to fork and experiment!

Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
