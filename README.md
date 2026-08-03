# xolite-ce

Packaging for **XO Lite Community / Home-laber Edition** (`xo-lite-ce`), the upstream [XO Lite](https://github.com/vatesfr/xen-orchestra) web UI rebuilt with patches so the "Deploy XOA" button installs a community-built XOA image instead of the Vates appliance.

The XVA URL is not hard-coded: it is resolved at runtime from `https://xo-image.yawn.fi/downloads/image.txt`, and the download is streamed through [`xoa-proxy`](../xoa-proxy) (a hard RPM dependency) to handle HTTPS and gzip for XAPI.

## Contents

- `UPSTREAM_TAG`: the upstream xen-orchestra tag the build is pinned to (currently `xo-lite-v0.21.0`).
- `SPECS/xo-lite-community.spec`: RPM spec. Installs to `/opt/xensource/www`, `Provides:`/`Obsoletes:` the stock `xo-lite` so it's a drop-in replacement on XCP-ng 8.3. The release counter is rewritten by CI from the `vX.Y.Z-ceN` tag so every CE build has a distinct, upgradeable NEVRA.
- `patches/xoa-deploy-patcher`: vendored Rust tool (source at [`../xoa-deploy-patcher`](../xoa-deploy-patcher)) that applies landmark-based patches to `xoa-deploy.vue` at build time and fails the build if upstream drifted.
- `patches/en-hl.json`, `patches/update_locales.sh`: Home-laber Edition locale strings.
- `patches/xolite-loader.html`, `patches/update-xolite-loader.sh`: replacement loader page (removes the `lite.xen-orchestra.com` remote-loading fallback).
- `xcp-ng-ce-public.asc`: public key used to sign the community RPM repo.

## Build

Builds run in CI (GitHub Actions, triggered by [`../buildorchestration`](../buildorchestration)): the upstream tag from `UPSTREAM_TAG` is fetched, patches applied, the Vue app built, and the result packaged with the spec above. The RPM ends up in the community repo consumed by [`../xcp-ng-ce-iso`](../xcp-ng-ce-iso).

## RPM repository (GitHub Pages)

Every release is republished as a signed, `yum`-resolvable repository hosted on
GitHub Pages at <https://vagrantin.github.io/xolite-ce/>, so an installed XCP-HL host
can `yum update xo-lite-ce` in place instead of reinstalling from the ISO.

### Recommended: install the whole repository set at once

The instructions below configure this one repository. On an XCP-HL host the
simpler route is the `xcp-hl-release` package, which owns
`/etc/yum.repos.d/xcp-hl.repo` and defines all three XCP-HL repositories
together, so repository configuration arrives through `yum` like any other
update instead of having to be re-downloaded by hand:

```bash
curl -o /etc/yum.repos.d/xcp-hl.repo \
  https://vagrantin.github.io/xcp-hl/xcp-hl.repo
rpm --import https://vagrantin.github.io/xcp-hl/xcp-ng-ce-public.asc
yum clean all && yum install xcp-hl-release
```

Hosts installed from a recent ISO already have it. See the
[Updates documentation](https://vagrantin.github.io/xcp-hl/updates.html).

On an XCP-ng 8.3 host, as root:

```bash
curl -o /etc/yum.repos.d/xcp-hl-xolite.repo \
  https://vagrantin.github.io/xolite-ce/xcp-hl-xolite.repo

rpm --import https://vagrantin.github.io/xolite-ce/xcp-ng-ce-public.asc

yum clean all
yum update xo-lite-ce
```

Note that `yum` never re-fetches a `.repo` file once it is installed, so a change
to the repository configuration published here only reaches a host that
downloads it again.

### How it is built

`.github/workflows/pages-repo.yml` builds and deploys the site. It is triggered by
`workflow_run` once *XOlite home-laber RPM* completes successfully, not by
`release: published`: that workflow publishes its release with the default
`GITHUB_TOKEN`, and events authored by that token deliberately do not start
further workflows. It can also be run manually with `workflow_dispatch`, which is
the only way to republish without cutting a release. The repository's Pages
source must be set to *GitHub Actions*.

The workflow downloads the `xo-lite-ce-*.rpm` assets from the five most recent
releases, indexes them with `createrepo_c`, and signs `repodata/repomd.xml` with
a detached armored signature. The `createrepo_c` flags are not decorative:
dom0 on XCP-ng 8.3 is CentOS 7 (yum 3.4.3, rpm 4.11.3), which predates zstd and
zchunk metadata and expects sqlite databases, so `--database
--compress-type=gz --checksum=sha256` are all required for the metadata to be
readable at all.

Only the five most recent releases are published, which bounds the site size and
leaves a rollback window:

```bash
yum --showduplicates list xo-lite-ce
yum downgrade xo-lite-ce-<version>
```

It also matters for correctness here. Republishing every release resurrected
pre-pin builds whose `Version` outranks the pinned `UPSTREAM_TAG`, so `yum`
offered an abandoned 0.22.x build as an upgrade.

`pages/` holds the files copied to the site root: `index.html` (the landing page)
and `xcp-hl-xolite.repo` (ready-made client config), published alongside
`xcp-ng-ce-public.asc`.

### Verification

The client config sets `repo_gpgcheck=1` and `gpgcheck=0`. That asymmetry is
deliberate: the RPMs are signed by a GPG *signing subkey*, and rpm 4.11 registers
only the primary key on import, so it reports `NOKEY` for any subkey-made
signature. Integrity therefore comes from the signed `repomd.xml`, which records
a SHA-256 of `primary.xml`, which records a SHA-256 of every package. This is the
same trust model apt uses, where the release file is signed and the individual
packages are not.

The signing subkeys expire **2027-05-10**. After that date verification fails
until they are extended and `xcp-ng-ce-public.asc` is refreshed here and
re-imported on every host.

## Project entry point

The entry point for the project is the [XCP-HL documentation website](https://vagrantin.github.io/xcp-hl/), and issues must be created on the [xcp-hl repository](https://github.com/Vagrantin/xcp-hl/issues) rather than on this one.
