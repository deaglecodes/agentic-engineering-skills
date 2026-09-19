# Evals

These are lightweight behavior eval prompts. They are not a full automated benchmark; they are smoke checks for whether an agent follows the pack's intended workflow.

Run structural checks:

```sh
./scripts/run-evals-smoke.sh
```

Use them manually by pasting a prompt into an agent with the relevant adapter installed, then compare behavior against the expected behavior and pass criteria.

## Runnable comparison

The [verification receipt demo](verification-demo/README.md) exercises five specified tool behaviors against a plain shell sequence, including passing and failing controls. It is a mechanism demonstration without model calls. It does not supersede the model comparison below.

The [paired coding pilot](paired-pilot/README.md) compares the same coding agent with and without the installed pack on three runnable bug-fix tasks, with frozen external graders and two repetitions per condition. The task fixtures are authored examples, not sampled production issues. Its grader self-checks run in repository validation without making model calls; launching the full pilot is a separate explicit command.
