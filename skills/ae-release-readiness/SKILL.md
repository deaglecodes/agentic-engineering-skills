---
name: ae-release-readiness
description: Use before tagging, announcing, or promoting a release. Confirm docs, changelog, security policy, install paths, CI, smoke tests, caveats, and public claims are ready.
metadata:
  short-description: Public release readiness gate
---

# Release Readiness

## When To Use

Use this skill before version tags, release notes, public promotion, marketplace publication, plugin packaging, or a maintainer asking whether a repo is ready.

## Workflow

1. Confirm the version target and release scope.
2. Check changelog, README, roadmap, security policy, contribution guide, and release checklist.
3. Validate install and uninstall paths for each supported agent.
4. Run local validation and CI-equivalent checks.
5. Run a fresh-install smoke test in a temp directory.
6. Scan public files for secrets and overclaims.
7. Prepare PR title, PR body, suggested commit message, and release caveats.

## Do

- Keep release claims honest and evidence-based.
- Include downgrade, disable, uninstall, and restore paths.
- Mark experimental or example-only pieces clearly.
- Verify package/plugin metadata before publication.

## Don't

- Do not push to main as part of readiness unless explicitly asked.
- Do not publish packages or marketplace listings without approval.
- Do not hide failing validation behind "minor caveat" language.
- Do not claim broad agent compatibility without install and smoke-test paths.

## Expected Output

Report release status, files changed, commands run and results, smoke-test result, caveats, suggested commit message, PR title/body, and whether public promotion is advisable.

## Verification Checklist

- `scripts/validate-repo.sh` passes or failures are documented.
- Fresh-install smoke test was run.
- Release assets exist and are current.
- Agent adapters have install, uninstall, smoke prompt, and limitations.
- No global user config was mutated during smoke testing.

## Failure Modes

- Local validation fails.
- Smoke test requires unavailable tools.
- Official packaging docs do not support a desired field.
- The release still depends on manual review for unsupported ecosystems.
