# Subprocess Session Isolation Design

## Goal

Implement opt-in subprocess isolation for Amplifier agent sessions to prevent memory exhaustion during parallel recipe execution.

## Background

Three forces compound to cause OOM kills during parallel recipe execution:

1. **SimpleContextManager.self.messages never shrinks (by design)**: Every agent session keeps its full uncompacted conversation history in `self.messages`. A 38-call agent with 190 tool results accumulates ~10-20MB permanently in memory. Compaction creates ephemeral views for LLM requests but never touches the source list.

2. **Parallel execution makes all session lifetimes overlap**: `asyncio.gather(*tasks)` in `_execute_loop_parallel` holds ALL N parallel sessions alive simultaneously. With `parallel: true` on 4 topics x 2 agents, peak RSS can reach 3.2GB+ just for one wave of parallel sessions.

3. **Python's allocator never returns freed pages to the OS**: After sessions complete, `gc.collect()` breaks reference cycles but pymalloc keeps the pages. Each wave of parallel sessions sets a new RSS floor that never decreases. Multiple waves (topdown + bottomup + combine) compound.

**Result**: A single python3 process grows to 35-37GB RSS and gets OOM-killed.

**Previous fixes** (sub-recipe return trimming, `gc.collect`, checkpoint trimming) addressed the recipe executor's context dict but NOT the session-level message history or the Python allocator behavior. They helped for serial execution but don't solve the fundamental problem.

## Approach

A reusable utility in `amplifier-foundation` that any app can use. When enabled, each agent sub-session runs in its own Python process. When the process exits, the OS reclaims ALL memory immediately — eliminating the RSS watermark accumulation that causes OOM kills.

The CLI's `session_spawner` calls it, but so could any custom app. This is not a kernel change — the kernel already provides the extension points (`session.spawn` capability, `parent_id`, `session:fork` event).

### Why Foundation Layer (Not CLI, Not Kernel)

- **Not CLI-only**: Other apps that embed Amplifier should be able to use subprocess isolation without depending on the CLI.
- **Not kernel**: The kernel deliberately provides "mechanism not policy." Process isolation is a policy decision. The kernel's `session.spawn` capability is an extension point that the app layer fills.
- **Foundation is reusable**: Any app imports the utility. The CLI is just one consumer.

## Architecture

### What Crosses the Process Boundary

Today when `session_spawner` creates a child session, it shares these objects:

| Object | Direction | Subprocess Mode Handling |
|--------|-----------|--------------------------|
| config dict | parent → child | Serialized as JSON to temp file. Config is already a plain dict. |
| prompt string | parent → child | Included in the JSON temp file. |
| parent_id | parent → child | Included in the JSON temp file. |
| project_path | parent → child | Included in the JSON temp file. |
| API keys | parent → child | Inherited via environment variables (child inherits env from parent). |
| approval_system | bidirectional | **Simplified**: Recipe-dispatched agents auto-approve. For sessions needing interactive approval, fall back to in-process mode. |
| display_system | child → parent | **Simplified**: No real-time streaming. Child output appears as single result when complete. Recipe engine shows progress at step level. |
| spawn_fn (recursive) | child → grandchild | Child registers its own `session.spawn` capability. If child delegates, it spawns another subprocess. Recursion works naturally. |
| result string | child → parent | Child writes to stdout. Parent reads it. Same contract as today. |

### IPC Protocol

Minimal — no sockets, no gRPC, no message queues. Just files and stdio:

- **Parent → child**: Temp JSON file with `{config, prompt, parent_id, project_path}`
- **Child → parent**: Result string on stdout
- **Error signaling**: Non-zero exit code + stderr

## Components

### The Subprocess Runner (`amplifier_foundation/subprocess_runner.py`)

A single new file (~100-150 lines) with two sides connected by the IPC channel described above.

#### Parent-Side API

```python
async def run_session_in_subprocess(config, prompt, parent_id, project_path, timeout=1800):
    """Run an AmplifierSession in an isolated subprocess. Returns result string."""
```

Under the hood:
1. Serialize config + prompt + parent_id + project_path to a temp JSON file
2. Spawn child: `asyncio.create_subprocess_exec(sys.executable, "-m", "amplifier_foundation.subprocess_runner", temp_file_path)`
3. Child reads JSON, creates `AmplifierSession`, initializes, executes, writes result to stdout
4. Parent reads result from stdout
5. Child process exits — OS reclaims ALL memory

#### Child-Side Entry Point (`python -m amplifier_foundation.subprocess_runner`)

1. Read config JSON from temp file (path passed as `argv[1]`)
2. Create `AmplifierSession(config=config, parent_id=parent_id)`
3. Initialize (loads modules fresh — ~2-5 sec cost, negligible vs. 2-11 min per agent LLM time)
4. Execute(prompt)
5. Write result to stdout
6. Exit — OS reclaims everything

#### What the Child Process Has

- Its own module loader (loads orchestrator, providers, tools, hooks fresh)
- Its own `events.jsonl` (writes to the project's session directory)
- Its own context-intelligence hook (writes locally)
- Full filesystem access (same working directory as parent)
- Environment variables inherited from parent (API keys, etc.)
- Its own `session.spawn` capability (for recursive delegation — spawns further subprocesses)

#### What the Child Process Does NOT Have

- No display system (no streaming to parent terminal)
- No interactive approval system (auto-approves, or uses simple policy)
- No parent's in-memory state

### Opt-In Mechanism

#### Level 1: App-Layer Opt-In (`session_spawner.py` in `amplifier-app-cli`)

```python
async def spawn_fn(agent_name, task, parent_session, **kwargs):
    child_config = merge_agent_config(parent_session, agent_name)
    
    # Check if subprocess isolation is requested
    if kwargs.get("subprocess") or child_config.get("spawn_mode") == "subprocess":
        from amplifier_foundation.subprocess_runner import run_session_in_subprocess
        return await run_session_in_subprocess(
            config=child_config,
            prompt=task,
            parent_id=parent_session.session_id,
            project_path=project_path,
        )
    else:
        # Current behavior: in-process (unchanged)
        child_session = AmplifierSession(config=child_config, ...)
        ...
```

#### Level 2: Recipe-Level Opt-In

Per-step:
```yaml
- id: "investigate-topics"
  type: "recipe"
  foreach: "{{topics}}"
  parallel: true
  subprocess: true    # NEW: run each iteration in its own process
```

Per-pipeline:
```yaml
context:
  spawn_mode: "subprocess"   # all agent steps use subprocess isolation
```

#### What Doesn't Change

- Interactive `delegate` calls from a user conversation → in-process (needs display/approval)
- Recipe steps without `subprocess: true` → in-process (current behavior)
- Any app that doesn't import the foundation utility → completely unaffected

## Data Flow

```
Recipe Executor
  │
  ├─ parallel: true, subprocess: true
  │
  ├─► spawn_fn(agent, task, subprocess=True)
  │     │
  │     ├─► Serialize config to /tmp/amp_XXXX.json
  │     ├─► asyncio.create_subprocess_exec(python -m subprocess_runner /tmp/amp_XXXX.json)
  │     │     │
  │     │     ├─► [CHILD PROCESS]
  │     │     │     Read /tmp/amp_XXXX.json
  │     │     │     Create AmplifierSession
  │     │     │     Initialize modules
  │     │     │     Execute prompt (LLM calls, tool use)
  │     │     │     Write result → stdout
  │     │     │     Exit (OS reclaims memory)
  │     │     │
  │     │     └─► Parent reads stdout → result string
  │     │
  │     └─► Return result (same contract as in-process mode)
  │
  └─► Collect results, continue pipeline
```

## Error Handling

- **Timeout**: Parent kills child process after configurable timeout (default 1800s). Returns timeout error to recipe executor, which handles it as a failed step.
- **Non-zero exit code**: Parent reads stderr, wraps it as an error result. Same error handling path as a failed in-process session.
- **Crash/segfault**: OS terminates child, parent sees unexpected EOF on stdout + non-zero exit code. Handled same as non-zero exit.
- **Temp file cleanup**: Parent deletes temp JSON file in a `finally` block regardless of success/failure.

## Repos Involved and Change Scope

### Repo 1: `amplifier-foundation` (new utility, pure addition)

| Change | Scope |
|--------|-------|
| New file: `amplifier_foundation/subprocess_runner.py` | ~100-150 lines |
| `run_session_in_subprocess()` parent-side async function | Core API |
| `__main__` block child-side entry point | Child bootstrap |
| JSON serialization/deserialization of config + result | IPC |
| Timeout handling, exit code error detection, stderr capture | Error handling |

No changes to existing foundation code.

### Repo 2: `amplifier-app-cli` (opt-in wiring)

| Change | Scope |
|--------|-------|
| Modified file: `session_spawner.py` | ~20 lines changed |
| Import `run_session_in_subprocess` from foundation | Conditional import |
| Check for `subprocess=True` kwarg or `spawn_mode` in config | Branch logic |
| Call subprocess runner when opted in | New code path |

No changes to existing behavior for users who don't opt in.

**No changes to `amplifier-core`.** No changes to any modules.

## Backward Compatibility

- Default behavior **unchanged** — in-process spawning unless explicitly opted in
- No new dependencies — uses only stdlib (`asyncio`, `json`, `sys`, `tempfile`)
- Child process uses the same `AmplifierSession` API that already exists
- Config dict serialization is safe — it's already a plain dict with JSON-compatible values
- Event logs write to the same project directory — observability unchanged
- Session lineage tracking via `parent_id` — unchanged

## Testing Strategy

- **Unit test subprocess_runner**: Spawn a minimal session in subprocess, verify result returns correctly
- **Unit test error handling**: Subprocess timeout, non-zero exit code, stderr capture
- **Unit test config serialization**: Verify round-trip of config dict through JSON
- **Integration test**: Run a recipe with `subprocess: true` and verify output matches in-process execution
- **Memory test**: Run parallel recipe with `subprocess: true` and verify RSS stays bounded
- **Backward compatibility**: Run existing recipes WITHOUT subprocess flag and verify behavior unchanged

## Explicitly Out of Scope

- Real-time streaming from child to parent terminal (use in-process mode for that)
- Interactive approval proxying (use in-process mode for that)
- Context-simple's unbounded message history (separate concern, arguably correct behavior)
- Python allocator behavior (OS-level constraint, cannot be changed — subprocess isolation avoids the problem instead)

## Open Questions

1. **Automatic subprocess for parallel steps?** Should the recipe executor pass `subprocess: true` automatically when `parallel: true` is set? Or keep them as independent opt-in flags? *Proposed*: Independent, since parallel in-process is valid for light workloads.

2. **Max subprocess limit?** Should there be a `max_subprocess` limit (similar to `max_concurrent_llm`) to prevent fork-bombing? *Proposed*: Yes, default 4, configurable.

3. **Bundle resolution in child?** How should the child process handle bundle resolution? Does it need to re-resolve bundles or can it use pre-resolved paths from the parent config? *Proposed*: Parent passes fully-resolved config with absolute paths.
