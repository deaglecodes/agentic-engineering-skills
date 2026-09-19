# Paired coding pilot

This is a small, transparent pilot of the installed pack's incremental effect on a coding agent. It uses authored, runnable Python projects with deliberately seeded bugs, not a sample of production issues. There is no model judge and no expected winner.

[19 September 2026 results](results/2026-09-19/report.md): both conditions passed all six runs; the pack used more time and reported input tokens. The public evidence includes final code, patches, checks, and machine-readable run records.

## Frozen design

- Three tasks: exact invoice rounding, stable team-event pagination, and safe nested settings updates.
- Two conditions: the normal coding agent with common containment instructions; the same agent with the installed Codex adapter added and its local skill/tool files available.
- Two repetitions per task and condition: 12 runs. All are sequential. Repetition 1 runs without-pack then with-pack; repetition 2 reverses that order.
- Model: GPT-6 Astra, medium reasoning, identical 180-second wall-clock limit per run. No automatic retries of scored runs.
- Every run starts from the same task files and the same unrelated, uncommitted edit in notes.md.
- The treatment pack is frozen at commit `f2c2de2`. The runner archives that version before setup, so neither the task graders nor reference solutions in this newer suite are present in the installed pack.
- Every task has two visible tests and eight held-out test methods. The method count is the denominator; multiple failing cases inside one method count as one failed method.
- Strict success requires normal completion within the time limit, all eight held-out checks, the original visible tests, and preservation of the unrelated user edit and installed pack. Modified visible tests cannot improve the score: the evaluator runs an immutable copy of the original tests.
- Report correctness, strict successes, user-edit preservation, visible-test preservation, recorded commands, wall time, and CLI-reported token usage separately. Token counts are not dollar costs. This pilot does not collect reliable billing data.

The baseline is a normally instructed Codex agent, not a bare language model. Both conditions retain Codex's built-in instructions. User config, memory, plugins, apps, hooks, network search, and multi-agent tools are disabled using per-run flags. The named skill catalog budget is restricted. Automatic project-document loading is limited, and the installed adapter text is injected explicitly through `developer_instructions` to control the condition. This tests the instruction-and-reference content; it does not test whether every agent product automatically discovers the installation. A preflight model self-report still mentioned AGENTS guidance, so complete removal of background/account instruction effects is not established.

## Run

Python 3.9+, Git, and an authenticated Codex CLI supporting the chosen model are required. No Python packages are installed.

Check that each broken starter fails and each independent reference repair passes:

```sh
python3 -B evals/paired-pilot/run.py --check
```

Run all 12 trials. The output directory must not already exist:

```sh
python3 -B evals/paired-pilot/run.py --codex /path/to/codex --output /path/to/new-pilot-run
```

The runner preserves a manifest, every completed result, model events, command results, patches, final source, and evaluator outputs. It does not automatically commit, push, or publish any transcript. Review artifacts for private paths or account information before sharing. It leaves global configuration and authentication files unchanged.

The graders and reference fixes live outside each agent workspace. The common prompt forbids parent-directory access. Workspace-write is not a guarantee that all reads outside the workspace are technically impossible; this is a cooperative evaluation, not an adversarial isolation test.

## Interpretation

Six observations per condition across just three tasks cannot establish general superiority or a reliable effect size. The tests cover only the documented cases. These tasks may be too easy to distinguish a strong model, and authoring them alongside the pack introduces selection bias. A tie is a valid result. A positive pilot would need independent tasks, more repetitions, other models, and real user evaluation before marketing a performance benefit.
