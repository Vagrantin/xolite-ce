#!/usr/bin/env bash
# Keep the source pipeline shared by packaged builds and source validation.
set -euo pipefail
repo=$(cd "$(dirname "$0")/.." && pwd)
source_dir=$(cd "${1:?upstream source directory required}" && pwd)
bash "$repo/scripts/apply-patches.sh" "$source_dir"
cd "$source_dir"
ln -s "$repo/patches" patches
bash patches/update_locales.sh
python3 patches/update-login-locales.py .
python3 patches/update-ja-pool-dashboard.py .
python3 patches/add-host-versions.py .
python3 patches/add-guest-versions.py .
bash patches/update-xolite-loader.sh
python3 patches/cleanup-deploy-secrets.py @xen-orchestra/lite/src/pages/xoa-deploy.vue
