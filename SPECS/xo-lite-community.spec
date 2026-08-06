Summary: Xen Orchestra Lite (Home-laber Edition)
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
Obsoletes: xo-lite <= %{version}-%{release}
Requires: xoa-proxy
# Carries the XCP-HL repo config onto hosts installed from the ISO, where
# nothing else depends on a -release package.
Requires: xcp-hl-release

BuildArch: noarch

Source0: xo-lite-ce-%{version}.tar.gz

%description
Xen Orchestra Lite (Home-laber Edition), patched to deploy a community-built
XOA image. The XVA URL is resolved at runtime from
https://xo-image.yawn.fi/downloads/image.txt

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
