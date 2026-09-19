# Paired coding pilot — 19 September 2026

**Both conditions passed all six runs. This pilot found no correctness advantage from the pack on these tasks.** The pack-equipped runs had an 18.3% higher median wall time and 1.54× the CLI-reported input tokens. These are descriptive observations from a small pilot, not a general performance estimate or a billing comparison.

## Observed results

| Metric | Without pack | With pack |
| --- | ---: | ---: |
| Strict successes | 6/6 | 6/6 |
| Held-out check executions passed | 48/48 | 48/48 |
| Original visible test suites passed | 6/6 | 6/6 |
| Unrelated user edit preserved | 6/6 | 6/6 |
| Median wall time per run | 85.89 s | 101.64 s |
| Reported input tokens, all six runs | 366,608 | 562,988 |
| Reported cached input tokens, included above | 279,040 | 419,712 |
| Reported output tokens, all six runs | 13,772 | 16,524 |

There are 24 distinct held-out test methods across three tasks, repeated twice per condition. The 48 executions are not 48 independent tasks. Every run completed normally within 180 seconds. All six treatment runs preserved their installed pack and recorded commands reading its skill files. All twelve agents recorded a unittest command and added regression tests. A separate replay of the published source passed every agent-authored test suite and reproduced all held-out scores; see [post-run audit](postrun-audit.json).

| Task | Repetition | Without: checks | With: checks | Without: seconds | With: seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| money | 1 | 8/8 | 8/8 | 81.48 | 103.97 |
| money | 2 | 8/8 | 8/8 | 81.97 | 99.31 |
| pagination | 1 | 8/8 | 8/8 | 85.47 | 105.28 |
| pagination | 2 | 8/8 | 8/8 | 89.21 | 98.05 |
| settings | 1 | 8/8 | 8/8 | 92.40 | 98.19 |
| settings | 2 | 8/8 | 8/8 | 86.32 | 118.78 |

## What was compared

The three authored Python projects contain seeded bugs in invoice rounding, team-event pagination, and nested settings-file updates. They are runnable engineering exercises with explicit contracts, **not sampled production issues**.

- Same GPT-6 Astra model name, medium reasoning, 180-second wall-clock limit, and two repetitions in each condition. No retries of scored runs.
- Twelve sequential runs. Repetition 1 used without-pack then with-pack; repetition 2 reversed that order.
- Identical application files, visible tests, task prompts, and unrelated uncommitted notes edit in both conditions. Input hashes are recorded in [runs.json](runs.json).
- With-pack adds the installed Codex adapter to explicit developer instructions and makes its local reference files available. Baseline receives the shared containment instructions only, in addition to Codex's built-in guidance.
- Strict success requires all eight external held-out methods, the original immutable visible tests, normal completion, and preservation of the user edit and installed pack. Agent changes to visible tests cannot improve the score. There is no model judge.
- Broken starters passed 2/8, 0/8, and 2/8 methods respectively; independently authored reference fixes passed 8/8 each before trials. The graders were committed before scoring began and were not changed in response to results.

Treatment source: [`f2c2de2`](https://github.com/deaglecodes/agentic-engineering-skills/commit/f2c2de2748ac0376926cf8abc3a3dbbba6cd3bb9). Frozen task/runner revision: [`b7b809a`](https://github.com/deaglecodes/agentic-engineering-skills/commit/b7b809a25585a0ff03e4a39b4fb519b5568af55e). Grader SHA-256: `b0e8d4f1e7105c1b67df344538516f0813853c8204255f50ca45be87337bc97c`. CLI: `codex-cli 0.155.0-alpha.9.2`. A named model was selected; a backend model snapshot was not pinned.

The controls follow the official Codex [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) and [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference). Per-run settings ignore user configuration and disable memory, plugins, apps, hooks, web search, and multi-agent tools; project-document and named-skill budgets are restricted. Full flags and common instructions are in the machine-readable record. No global configuration was changed.

Two setup failures occurred before any scored task launched: an older CLI rejected the model, and archive extraction needed compatibility with system Python. The installed app CLI and corrected runner were used for all twelve scored runs. No task outcome was discarded.

## Interpretation and limits

The baseline already solved every task. This creates a ceiling: this suite cannot show whether the pack helps on harder work, weaker models, larger repositories, or ambiguous requests. There are only three task types, authored alongside the pack; repeated attempts do not remove selection bias. The tests cover their documented cases, not every possible bug.

The pack caused additional instruction/reference reads, but the timing and token differences also include live service and cache variation. Input counts are cumulative across agent turns; cached tokens are included. Dollar costs and statistically reliable speed effects were not measured.

Explicit adapter injection evaluates pack content. It does not establish automatic discovery in every supported agent. Built-in instructions remained shared, and a preflight self-report mentioned AGENTS guidance despite a zero project-document budget, so complete removal of background/account guidance is unverified. Workspace-write plus containment instructions is a cooperative setup, not proof that outside reads were technically impossible.

The useful conclusion is that the pack is installable and its workflow references were used, while **a model-quality benefit remains unproven**. Keep the public positioning focused on its explicit workflow, reversible installation, and optional tooling. A stronger next evaluation would freeze independent repository issues before comparing conditions, including realistic dependency, scope, and verification decisions.

## Evidence and reproduction

- [Frozen protocol and run instructions](../../README.md), [runner](../../run.py), [graders](../../grade.py), and [reference repairs](../../reference).
- [Machine-readable runs, commands, final agent messages, and metrics](runs.json).
- [Final code, patches, original visible-test output, held-out output, and post-run regression output](artifacts).
- [Separate verification of published snapshots](postrun-audit.json).

Raw CLI event and diagnostic logs are retained locally and are not published because they can include account or filesystem details. Public records replace local path prefixes with placeholders. Published patches use zero context (`git apply --unidiff-zero`); replaying each patch reproduced the exported source and tests byte for byte. The exported application files are unchanged; final tests may be extended by the agents. `original_tests_preserved: false` records that extension, while `visible_pass` comes from the untouched evaluator copy.

Recompute the summary without model calls:

```sh
python3 -B evals/paired-pilot/summarize.py evals/paired-pilot/results/2026-09-19/runs.json
```

Replay one published repair against the frozen grader:

```sh
python3 -B evals/paired-pilot/grade.py settings evals/paired-pilot/results/2026-09-19/artifacts/settings-1-with-pack
```
