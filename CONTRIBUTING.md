# Contributing

Thanks for helping improve Agentic Engineering Skills.

## Rules

- Keep skills concise and focused.
- Put reusable behavior in `skills/`; keep adapters short.
- Do not include real credentials, private config, cookies, keys, or `.env` contents.
- Use plain English. The target user may not be an engineer.
- Keep package-age examples at 7 days unless the project deliberately changes policy.

## Checks

Run before opening a pull request:

```sh
./scripts/verify-pack.sh
./scripts/secret-scan.sh .
./scripts/test-fixtures.sh
```

If you edit shell scripts, also run:

```sh
bash -n scripts/*.sh
sh -n hooks/*.sh
```

## Pull Request Notes

Include:

- What changed.
- Why it changed.
- Which checks passed.
- Any remaining risk or limitation.
