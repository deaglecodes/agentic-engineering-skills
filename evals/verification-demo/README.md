# Verification receipt demo

This demonstrates an executable pack feature: combining individual command results with checks that unrelated files stayed unchanged. It is **not a second model benchmark**.

The comparator is a plain shell sequence, `check-one; check-two`, judged by its final exit code. That shortcut can return success after an earlier failure and does not examine unrelated files. Careful agents, existing CI runners, and correctly chained commands can already avoid the first problem. No claim is made that a coding agent without this pack necessarily makes these mistakes.

Five cases are defined in the script: a passing control, a failing-last-command control, and three examples of a misleading green status. Each condition runs the same commands and starting files in a separate disposable directory. The runner takes a snapshot before the simulated edit. No model calls, retries, or selected model outcomes are involved.

## Observed results

| Case | Required result | Plain shell sequence | Receipt runner |
| --- | --- | --- | --- |
| Clean control | Pass | Pass | Pass |
| Earlier check fails, later check passes | Fail | Pass | Fail |
| Last check fails control | Fail | Fail | Fail |
| Unrelated file changed before checks | Fail | Pass | Fail |
| Check changes a protected file | Fail | Pass | Fail |

The runner identified every demonstrated failure and passed the clean control. It reported zero false-success results versus three for the plain shell sequence. The scope is exactly these five selected demonstrations.

Run from the source checkout:

```sh
python3 -B evals/verification-demo/run.py
```

Save all results to a new file:

```sh
python3 -B evals/verification-demo/run.py --output /tmp/new-verification-demo.json
```

The script records source hashes and receipts. The checked-in [results](results.json) cover every case, including both controls. This is a feature demonstration chosen to exercise the mechanism, not a representative estimate of failure rates. The [earlier model pilot](../paired-pilot/results/2026-09-19/report.md) remains a correctness tie.
