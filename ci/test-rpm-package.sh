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
cp SPECS/xo-lite-community.spec "$top/SPECS/"
tar -czf "$top/SOURCES/xo-lite-ce-0.21.0.tar.gz" -C "$tmp" xo-lite-ce-0.21.0

# Same environment as the real build: the runner's rpm 6 declares
# rpmlib(LargeFiles), which dom0's rpm 4.11 rejects.
docker run --rm --user root \
  -v "$top:/root/rpmbuild" \
  rockylinux:9 \
  bash -c 'dnf -y -q install rpm-build && rpmbuild -bb /root/rpmbuild/SPECS/xo-lite-community.spec \
  --define "_topdir /root/rpmbuild" \
  --define "_version 0.21.0" --define "_release 0" --define "_shortcommit fixture"'
sudo chown -R "$(id -u):$(id -g)" "$top"
mapfile -t rpms < <(find "$top/RPMS" -type f -name '*.rpm')
[[ ${#rpms[@]} -eq 1 ]]
bash "$repo/ci/check-rpm-payload.sh" "${rpms[0]}" "$repo/LICENSE"
