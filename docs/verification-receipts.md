# Verification receipts

Run a project's checks separately and save a machine-readable result. A failed check stays failed even when a later command succeeds. Optional protected files are checked against a snapshot taken before edits.

Requires Python 3.9+ on macOS or Linux. Uses the standard library. Works with any coding agent, or directly from a terminal.

## Define the checks

Create `ae-checks.json` in the target project. Use its actual test and lint commands. This Python example protects an unrelated notes file:

```json
{
  "schema": 1,
  "checks": [
    {"name": "unit tests", "argv": ["python3", "-B", "-m", "unittest", "-v"], "timeout_seconds": 120},
    {"name": "diff whitespace", "argv": ["git", "diff", "--check"], "timeout_seconds": 10}
  ],
  "protect": ["notes.md"]
}
```

`protect` names exact relative files that should stay unchanged, including existing uncommitted work. It can be empty. Do not protect a file the task needs to edit. Missing files can be protected against creation. Directories, paths outside the project, and symlinks are refused. File contents and permission bits are compared; contents are not copied into snapshots.

Each check runs its `argv` directly from the project directory. Put separate checks in separate entries. The runner does not parse a shell command string. If you explicitly invoke a shell or a script that hides its own failures, its reported exit code remains your responsibility.

## Before editing

After installing the pack, run from the target project:

```sh
evidence_dir="$(mktemp -d)"
printf '%s\n' "$evidence_dir"
./.agentic-engineering/pack/scripts/verify.sh snapshot \
  --plan ae-checks.json --output "$evidence_dir/before.json"
```

Keep `evidence_dir` for the final check. If the agent starts a new shell for each tool call, use the printed directory path explicitly in later calls. From the source checkout, use `./scripts/verify.sh` and `--target /path/to/project`; pass the corresponding plan path explicitly.

## After editing

```sh
./.agentic-engineering/pack/scripts/verify.sh run \
  --plan ae-checks.json --baseline "$evidence_dir/before.json" \
  --output "$evidence_dir/receipt.json"
```

Example output for a failing test followed by successful lint:

```text
FAILED           unit tests (exit 1)
PASSED           lint (exit 0)
FAIL  1/2 checks; receipt saved
```

The receipt records every check's result, duration, exit code, output size and hash, protected-file comparisons, and the check-plan hash. Keep the plan with the receipt to recover the exact commands. The JSON omits raw command output and arguments. Use `--show-output` to print diagnostics, or rerun a failed command directly. Names and protected paths remain visible, so review a receipt before sharing it.

- Exit `0`: every check passed, the plan stayed unchanged, and protected files matched before and after checks.
- Exit `1`: a check failed, timed out, could not start, or a protected file or plan changed.
- Exit `2`: invalid setup, a mismatched snapshot, or a receipt could not be written. This is not a pass.

Timeouts default to 120 seconds per check. The runner terminates the process group on timeout. Snapshot and receipt outputs must be new files; existing evidence is never overwritten. If checks legitimately change, review the plan and take a new snapshot before further work. A changed plan cannot reuse the earlier snapshot.

## Boundaries

The runner detects changes; it does not prevent or restore them. Only listed paths are protected, at the comparison times. A receipt is a local record of the checks that ran, not tamper-proof attestation, proof of test quality, or evidence that later edits were verified. Review the diff and choose checks that actually establish the requested behavior.

Commands execute with your normal permissions and can have side effects. Use already-authorized project checks; the runner is not a sandbox or deployment approval system. It does not automatically hook into an agent's finish action. Small tasks with one direct check may not need a saved receipt.

See the [reproducible mechanism demo](../evals/verification-demo/README.md). It demonstrates this tool's behavior and does not measure model coding quality.
