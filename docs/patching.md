# Patch maintenance

This policy implements xcp-hl #43 and #16 for the unified-diff migration
from `xolite-ce@d452937`, pinned to `xo-lite-v0.21.0` at
`13f987ff3d34504a90b89178489e15fa2293d1b3`. It does not establish support
for another upstream version or change the published appliances.

## Shared maintenance rules

Keep upstream pins explicit. Keep source edits reviewable as unified diffs in
the consumer repository. Use `patches/series` as the single order for diffs.
New diff names must be `NNN-descriptive-name.patch` with unique numeric
prefixes. The existing `xoa-button-empty.patch` name remains valid. Never use
repeated letters to force ordering.

Document stable IDs, purpose, owner, upstream commit/version and dependencies
in `patches/metadata.toml`. Dependencies must precede their consumers. The
validator rejects malformed names, missing, duplicate and unlisted patches,
metadata mismatches and invalid dependency order. There is no shared schema
migration with XOA-HL; these are shared rules with component-specific tooling.

Run `python3 scripts/list-patches.py patches` and
`python3 ci/test-patch-series.py` before applying source edits. `scripts/apply-patches.sh`
checks the complete diff series before applying it. Do not skip failures or
use fuzzy fallback. Normal contextual diff matching replaces the old tool's
anchor-count checks; the equivalence claim below is scoped to the pinned input.

`bash scripts/patch-source.sh /path/to/clean/upstream` is the shared pipeline
for builds and validation. It applies the series, locale and host/guest
transformations, the local loader and deploy-secret cleanup. Existing
non-diff transformations remain explicit. Start with a clean upstream tree;
reapplying is an error. The build's version-dependent robots.txt copy remains
a separate unchanged packaging preparation step.

Source evidence: `xolite-ce/.github/workflows/build-xolite-ce.yml@d452937`
and the migration diff in this change. XOA-HL's precedent is
`xoa-hl/scripts/list-patches.sh@dc25ee0` and
`xoa-hl/patches/metadata.toml@dc25ee0`.

## Migration provenance

`docs/patch-migration.json` records the immutable legacy consumer and patcher
source commits, SHA-256 hashes for the vendored executable and Rust source,
and original/transformed deploy-page hashes. The diff was generated from the
vendored executable's output on that exact upstream input. The executable
is removed from the current build tree, not from history.

The source pin is `xoa-deploy-patcher/src/main.rs@dbd7c88816d7b724aaf0124bce5168c4d700dea1`.
The hash identifies the source inspected during migration. A rebuilt
executable need not have the same bytes as the vendored artifact. The CI
check rebuilds that pinned source and compares its deploy output with the
hashed vendored executable. This establishes behavioral correspondence on
the pinned input, not a claim of reproducible historical binary provenance.

`ci/test-patch-migration.py` verifies pins and hashes, then compares every
source file, Git executable mode and symlink target from the complete old and new
patch pipelines. It excludes only the temporary `patches` symlink used to
locate assets. It includes the unchanged robots.txt preparation step. It writes a report with the changed-file hashes and whether
rebuilt-source output was checked. No release, deployment or local build is
required to compare the legacy executable with the new diffs.

Offline example with existing pinned checkouts:

```sh
python3 ci/test-patch-migration.py /path/to/upstream /path/to/legacy-consumer \
  /path/to/legacy-patcher-source --report /path/to/result.json
```

All builds run in GitHub Actions. `.github/workflows/check-patch-series.yml`
compares both complete pipelines, checks source behavior, builds the patched
Vue application and checks its distribution output. It never publishes a
release. Existing packaging checks remain separate.

Keep the immutable migration record when changing upstream or product
behavior later. An intentional output change requires an explicit review of
the equality gate, rather than silently updating historical hashes. Add a
new version-scoped validation baseline for a new upstream pin.

Source application, hosted build validation, package validation and installed
acceptance must be reported separately. No running appliance was available
during this migration. In particular, deployment and installed no-phone-home
behavior still require installed acceptance.

## Offline migration checks

The series regression suite and `ci/check.sh` passed, including ShellCheck.
The existing pinned login, Japanese dashboard, host/guest patch and Node
checks passed. The Japanese workflow-order assertion now follows the shared
script rather than requiring inline commands in the packaging workflow.

The first migration comparator treated group-write permission as source
content and reported 0644 versus 0664 for an otherwise identical deploy page.
The comparator now uses Git's tracked executable mode, avoiding dependence on
the local umask while preserving byte and symlink comparisons.

The local comparison uses the recorded vendored executable. The pinned Rust
rebuild and patched Vue build are CI-only checks. RPM fixture builds are also
CI-only; no local package build or installed acceptance is claimed.

The offline complete-pipeline comparison passed for all 3,639 output files,
including 23 changed files, the unchanged robots.txt preparation step and
Git file modes. Source rebuild equivalence remains a hosted CI result.
