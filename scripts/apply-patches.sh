#!/usr/bin/env bash
# Check the complete series before writing source changes.
set -euo pipefail
repo=$(cd "$(dirname "$0")/.." && pwd)
source_dir=$(cd "${1:?upstream source directory required}" && pwd)
patch_list=$(python3 "$repo/scripts/list-patches.py" "$repo/patches")
mapfile -t patches <<< "$patch_list"
git -C "$source_dir" apply --check "${patches[@]}"
git -C "$source_dir" apply "${patches[@]}"
