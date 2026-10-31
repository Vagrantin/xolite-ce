#!/usr/bin/env bash
# Check the real package before signing or publishing. Does not install it.
set -euo pipefail
rpm_path=${1:?RPM required}
project_license=${2:?project LICENSE required}
compressor=$(rpm -qp --qf '%{PAYLOADCOMPRESSOR}' "$rpm_path")
[[ "$compressor" == xz ]] || { echo "dom0 requires xz, got $compressor" >&2; exit 1; }
# Dom0 rpm 4.11 rejects rpmlib(LargeFiles); some rpms inject it at build time.
if rpm -qp --requires "$rpm_path" 2>/dev/null | grep -q 'rpmlib(LargeFiles)'; then
  echo "RPM declares rpmlib(LargeFiles), which XCP-ng 8.3 dom0 rejects" >&2
  exit 1
fi
[[ $(rpm -qp --qf '%{NAME}' "$rpm_path") == xo-lite-ce ]]
[[ $(rpm -qp --qf '%{LICENSE}' "$rpm_path") == AGPL-3.0-only ]]
license_path=/usr/share/licenses/xo-lite-ce/PROJECT-LICENSE
files=$(rpm -qp --qf '[%{FILENAMES}\t%{FILEFLAGS:fflags}\n]' "$rpm_path")
awk -F '\t' -v path="$license_path" '$1 == path && $2 ~ /l/ { found=1 } END { exit !found }' <<< "$files"
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
rpm2cpio "$rpm_path" | cpio --quiet -i --to-stdout -- ".$license_path" > "$tmp"
cmp "$project_license" "$tmp"
echo 'RPM uses xz and ships the exact project license as a flagged license file'
