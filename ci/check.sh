#!/usr/bin/env bash
# What "checked" means for this repo (xcp-hl#148). Jenkins dev/xolite-ce runs it on every PR; run it locally too.
# Contract: exit 0 when clean; results under $CI_RESULTS; on failure $CI_RESULTS/current-step names the failed check.
# The build itself needs the upstream tree; the Test UI suite (xcp-hl#150) checks the installed result.
set -euo pipefail
cd "$(dirname "$0")/.."

OUT="${CI_RESULTS:-ci-results}"
mkdir -p "$OUT"
step() { echo "==> $1"; echo "$1" > "$OUT/current-step"; }

step "shellcheck (warnings and errors)"
git ls-files -z '*.sh' | xargs -0 shellcheck -S warning

step "en-hl.json: an object of strings"
jq -e 'type == "object" and ([.[] | type] | all(. == "string"))' patches/en-hl.json >/dev/null

step "loader stays local (no xen-orchestra.com)"
if grep -q 'xen-orchestra\.com' patches/xolite-loader.html; then
  echo "patches/xolite-loader.html names xen-orchestra.com" >&2
  exit 1
fi

step "UPSTREAM_TAG is one xo-lite tag"
grep -qxE 'xo-lite-v[0-9]+\.[0-9]+\.[0-9]+' UPSTREAM_TAG

rm -f "$OUT/current-step"
echo "all checks passed"
