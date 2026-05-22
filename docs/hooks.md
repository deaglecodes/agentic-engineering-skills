# Hook Usage

Hooks are optional guardrails. They do not replace human review.

## Verify Before Finish

Run before publishing, committing, or handing work back:

```sh
./hooks/verify-before-finish.sh
```

It checks:

- Git whitespace errors.
- Credential-like patterns across source, docs, adapters, and skills.
- Whether `rg` is present and runnable.

## Package Install Gate

Run before agent-driven package installs:

```sh
./hooks/block-risky-package-install.sh npm
./hooks/block-risky-package-install.sh pnpm
./hooks/block-risky-package-install.sh yarn
./hooks/block-risky-package-install.sh bun
./hooks/block-risky-package-install.sh uv
./hooks/block-risky-package-install.sh pip
```

The hook blocks supported tools unless the 7-day release-age setting is active. It also blocks unsupported package managers such as RubyGems, Bundler, Homebrew, Cargo, Go modules, and Composer because this pack cannot enforce a native 7-day release-age delay for them.

## Agent Integration

Use these scripts as command hooks where your agent supports them. For agents that do not support hooks, run them manually before approving package installs or final changes.
