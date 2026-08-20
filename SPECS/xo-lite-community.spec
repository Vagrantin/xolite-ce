Summary: Xen Orchestra Lite for XCP-ng HomeLab Edition
Name:    xo-lite-ce
Version: %{_version}
# _release, _shortcommit and _version are all passed via --define from CI.
# The leading number in Release is the ce release counter, computed from the
# vX.Y.Z-ceN tag (or a run-number fallback) so every ce build has a distinct,
# upgradeable NEVRA; g<shortcommit> is the xolite-ce repo commit that
# produced the patch, since Version alone (the upstream xo-lite version)
# doesn't identify which patch revision built this RPM.
Release: %{_release}.g%{_shortcommit}.xcpng8.3%{?dist}
License: AGPL3-only
URL:     https://github.com/vatesfr/xen-orchestra
Provides: xo-lite = %{version}-%{release}
# Unversioned on purpose: a bounded obsoletes stops matching once upstream
# xo-lite outruns our version, losing the ISO dependency race to it.
Obsoletes: xo-lite
Requires: xoa-proxy
Requires: xcp-hl-release

BuildArch: noarch

Source0: xo-lite-ce-%{version}.tar.gz

%description
Xen Orchestra Lite, customised for XCP-ng HomeLab Edition (XCP-HL).

Upstream XO Lite deploys one hardcoded appliance image. This build turns the
Deploy XOA flow into a choice of image sources:

 * XOA-HL, the default, a Xen Orchestra appliance built from source for
   XCP-HL, resolved at deploy time from the latest published image release
 * the official Vates appliance, unchanged upstream behaviour
 * the Ronivay community image
 * any custom XVA URL, plain or gzipped, over HTTP or HTTPS

Every source except the Vates one is streamed into XAPI through xoa-proxy,
which handles gzip decompression and HTTPS, including self-signed
certificates.

This package replaces the stock xo-lite package. The interface is served by
XAPI from /opt/xensource/www, as usual.

%prep
%autosetup -p1

%install
install -d -m 755 %{buildroot}/opt/xensource/www
cp -a * %{buildroot}/opt/xensource/www
rm %{buildroot}/opt/xensource/www/LICENSE \
   %{buildroot}/opt/xensource/www/CHANGELOG.md

%files
%license LICENSE
%doc CHANGELOG.md
/opt/xensource/www/assets
/opt/xensource/www/robots.txt
/opt/xensource/www/build.json
/opt/xensource/www/favicon.svg
/opt/xensource/www/index.html
/opt/xensource/www/manifest.webmanifest
/opt/xensource/www/xolite.html

%changelog
* Mon Apr 06 2026 Home-laber Build <community@build> - 0.8.0-1.0.community.1
- Home-laber Edition: deploy URL sourced from xo-image.yawn.fi/downloads/image.txt
- Removed lite.xen-orchestra.com fallback loader from index.html
