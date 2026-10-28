# Graphviz Setup Guide

> **Graphviz is OPTIONAL.** DOT authoring, syntax validation (via pydot), and graph
> analysis (via networkx) all work without it. Graphviz is only needed for rendering
> DOT source to images (PNG, SVG, PDF).

---

## Quick Check

```bash
dot -V
```

Expected output (your version may differ): `dot - graphviz version X.Y.Z (YYYYMMDD.HHMM)`

If you see `dot: command not found`, follow the platform instructions below.

---

## Installation by Platform

### macOS (Homebrew)

```bash
brew install graphviz
```

### Ubuntu / Debian

```bash
sudo apt update && sudo apt install graphviz
```

### Fedora / RHEL / CentOS

```bash
sudo dnf install graphviz
```

For older RHEL/CentOS: `sudo yum install graphviz`

### Windows

**choco:** `choco install graphviz`  
**winget:** `winget install Graphviz.Graphviz`  
**Direct download:** https://graphviz.org/download/ — add `C:\Program Files\Graphviz\bin` to PATH.

### Conda (Cross-Platform)

```bash
conda install -c conda-forge graphviz
```

### Docker — Alpine

```dockerfile
FROM python:3.12-alpine
RUN apk add --no-cache graphviz
```

### Docker — Ubuntu

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends graphviz \
    && rm -rf /var/lib/apt/lists/*
```

---

## Python Dependencies

```bash
pip install pydot networkx
```

Verify:

```python
import pydot; print(pydot.__version__)
import networkx; print(networkx.__version__)
```

### Package → Purpose

| Package    | Purpose                                  | Graphviz Required?          |
|------------|------------------------------------------|-----------------------------|
| `pydot`    | Parse, create, and validate DOT syntax   | No (parse/create); Yes (render) |
| `networkx` | Graph analysis: cycles, DAG check, paths | No                          |
| `graphviz` | Alternative Python binding for rendering | Yes                         |

---

## Verification

```bash
#!/bin/bash
echo "=== Graphviz CLI ==="
if command -v dot &>/dev/null; then
    dot -V && echo "✓ dot found"
else
    echo "✗ dot not found — install Graphviz to enable rendering"
fi

echo "=== Layout Engines ==="
for engine in dot neato fdp sfdp circo twopi osage; do
    command -v $engine &>/dev/null && echo "✓ $engine" || echo "✗ $engine (missing)"
done

echo "=== Python Packages ==="
python -c "import pydot; print(f'✓ pydot {pydot.__version__}')" 2>/dev/null \
    || echo "✗ pydot not installed"
python -c "import networkx; print(f'✓ networkx {networkx.__version__}')" 2>/dev/null \
    || echo "✗ networkx not installed"

echo "=== Render Test ==="
if command -v dot &>/dev/null; then
    echo 'digraph test { A -> B }' | dot -Tsvg > /tmp/test-render.svg \
        && echo "✓ SVG render OK" || echo "✗ SVG render failed"
else
    echo "— skipped (dot not installed)"
fi
```

## Safe output and recipe boundaries

`options.output_path` accepts relative or absolute paths beneath `render_output_root`.
The root defaults to the session working directory, or the process working
directory when no session directory is available; explicit module configuration
takes precedence. Paths escaping that canonical root (including through symlinks),
foreign Windows paths, directories, and suffix/format mismatches are rejected.
Existing image files can be rerendered: a successful render atomically replaces
the destination, while a failed render leaves it unchanged. Omitted paths still
use a temporary file. Assembly PNGs are written beside their DOT sources.

Discovery values pass through environment variables rather than executable
shell or Python source. Strings remain literal; lists and dictionaries are
JSON-serialized. Recipe Python steps use the runtime interpreter in isolated
mode and import installed dependencies, not code from the scanned checkout.
Topics must be 1-7 exact `name`/`slug`/`description` objects with unique lowercase
kebab-case slugs. Existing and recovered overview DOT must parse successfully;
artifact writes reject destination symlinks and escaping parent symlinks.

## Choosing where diagrams are saved

For the `dot_graph` **render** operation, a save outside the permitted folder
reports the full requested path and the current permitted folder. It offers a
full alternative path inside it when available, or asks for a new filename there.
No image is written and no configuration is changed by the rejected request.
Follow the applicable option directly from the error; no guide lookup is needed:

1. **Save now:** ask the assistant to save to the full alternative path shown.
   This keeps the current configuration. A suggested path is not reserved and
   does not guarantee filesystem write permissions.
2. **Choose a different folder:** update `config.render_output_root` in the
   existing `tool-dot-graph` entry of the bundle or application configuration
   used for the session. For example, to use `/path/to/chosen-folder`:

   ```yaml
   tools:
     - module: tool-dot-graph
       config:
         render_output_root: "/path/to/chosen-folder"
   ```

   This is a fragment, not a replacement file. Preserve the entry's `source`,
   other configuration keys and all other settings; update the existing entry
   rather than adding a duplicate. If you need help finding it, ask the assistant:
   "Find where tool-dot-graph is configured and set render_output_root to
   /path/to/chosen-folder, preserving my other settings."
   Start a new session with that configuration, then retry the full requested path.
   The new root **replaces** the old permitted folder; it does not add a second
   folder. Tool-call options cannot change this module configuration.

The error fills in the actual paths and an inline configuration fragment for the
requested file's immediate parent, not a broader home directory or filesystem root.
If a symlink redirects the save outside the permitted folder, the error instead
shows the requested and resolved paths and asks you to remove or avoid the
redirect; it does not suggest permitting the symlink target.

---

## Troubleshooting

### `dot: command not found`

**Diagnosis:** Graphviz not installed or not on PATH.  
**Fix:** Install via your platform method above. On Windows, ensure the `bin` folder is on PATH.
In conda environments, activate the environment first: `conda activate myenv`.

### Font Errors at Render Time

**Diagnosis:** `Warning: Could not load "/usr/share/fonts/..."` in render output.  
**Fix:** Install fonts — Ubuntu/Debian: `sudo apt install fonts-liberation`.
Set fallback: `graph [fontname="Helvetica"]`.

### pydot `InvocationException`

**Diagnosis:** `pydot.exceptions.InvocationException: GraphViz's executables not found`.
pydot is installed but cannot locate the `dot` binary.  
**Fix:** Install Graphviz (see above). In conda: install both `graphviz` and `python-graphviz`
in the same environment, then restart your Python process.

### SVG Output Shows Wrong Font

**Diagnosis:** SVG renders with a generic/fallback font instead of the intended font.  
**Fix:** Specify an installed system font in your DOT source:
```dot
graph [fontname="DejaVu Sans"]
node  [fontname="DejaVu Sans"]
edge  [fontname="DejaVu Sans"]
```
Run `fc-list` on Linux to list available fonts.

### Large Graph Renders Slowly

**Diagnosis:** Graphs with 100+ nodes take many seconds or minutes with the `dot` engine.  
**Fix:** Switch to a scalable layout engine. For 100–1000 nodes use `fdp`; for 1000+ nodes
use `sfdp`: `dot -Ksfdp -Tsvg graph.dot > out.svg`. Pre-process with `unflatten` to improve
aspect ratio: `unflatten -l 3 graph.dot | dot -Tsvg > out.svg`.
