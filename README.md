# xolite-ce

Packaging for **XO Lite Community / Home-laber Edition** (`xo-lite-ce`) — the upstream [XO Lite](https://github.com/vatesfr/xen-orchestra) web UI rebuilt with patches so the "Deploy XOA" button installs a community-built XOA image instead of the Vates appliance.

The XVA URL is not hard-coded: it is resolved at runtime from `https://xo-image.yawn.fi/downloads/image.txt`, and the download is streamed through [`xoa-proxy`](../xoa-proxy) (a hard RPM dependency) to handle HTTPS and gzip for XAPI.

## Contents

- `UPSTREAM_TAG` — the upstream xen-orchestra tag the build is pinned to (currently `xo-lite-v0.21.0`).
- `SPECS/xo-lite-community.spec` — RPM spec. Installs to `/opt/xensource/www`, `Provides:`/`Obsoletes:` the stock `xo-lite` so it's a drop-in replacement on XCP-ng 8.3. The release counter is rewritten by CI from the `vX.Y.Z-ceN` tag so every CE build has a distinct, upgradeable NEVRA.
- `patches/xoa-deploy-patcher` — vendored Rust tool (source at [`../xoa-deploy-patcher`](../xoa-deploy-patcher)) that applies landmark-based patches to `xoa-deploy.vue` at build time and fails the build if upstream drifted.
- `patches/en-hl.json`, `patches/update_locales.sh` — Home-laber Edition locale strings.
- `patches/xolite-loader.html`, `patches/update-xolite-loader.sh` — replacement loader page (removes the `lite.xen-orchestra.com` remote-loading fallback).
- `xcp-ng-ce-public.asc` — public key used to sign the community RPM repo.

## Build

Builds run in CI (GitHub Actions, triggered by [`../buildorchestration`](../buildorchestration)): the upstream tag from `UPSTREAM_TAG` is fetched, patches applied, the Vue app built, and the result packaged with the spec above. The RPM ends up in the community repo consumed by [`../xcp-ng-ce-iso`](../xcp-ng-ce-iso).
