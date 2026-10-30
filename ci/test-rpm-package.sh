#!/usr/bin/env bash
# Build only in GitHub Actions: real spec and license, tiny UI packaging fixture.
set -euo pipefail
cd "$(dirname "$0")/.."
repo=$PWD
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
top="$tmp/rpmbuild"
mkdir -p "$top"/{SOURCES,SPECS,BUILD,BUILDROOT,RPMS,SRPMS}
fixture="$tmp/xo-lite-ce-0.21.0"
mkdir -p "$fixture/assets"
for file in index.html robots.txt favicon.svg manifest.webmanifest xolite.html build.json CHANGELOG.md; do printf 'packaging fixture\n' > "$fixture/$file"; done
printf 'upstream notice fixture\n' > "$fixture/LICENSE"
printf 'fixture\n' > "$fixture/assets/fixture.js"
cp LICENSE "$top/SOURCES/xo-lite-ce-LICENSE"
tar -czf "$top/SOURCES/xo-lite-ce-0.21.0.tar.gz" -C "$tmp" xo-lite-ce-0.21.0
rpmbuild -bb SPECS/xo-lite-community.spec --define "_topdir $top" \
  --define '_version 0.21.0' --define '_release 0' --define '_shortcommit fixture'
mapfile -t rpms < <(find "$top/RPMS" -type f -name '*.rpm')
[[ ${#rpms[@]} -eq 1 ]]
bash "$repo/ci/check-rpm-payload.sh" "${rpms[0]}" "$repo/LICENSE"
