# Installed host versions

On a host's System tab, General information lists `xcp-hl-release`, `xo-lite-ce`,
`xoa-proxy` and the XCP-HL ISO build number. These are installed values, fetched
from that host through the read-only `xcp-hl-versions` XAPI plugin packaged by
`xcp-hl-release` (xcp-hl#281). The selected host's XAPI authorization applies.

The card refreshes when opened or when the selected host changes. An unavailable
plugin, failed connection, denied request or missing package displays the existing
localized Unknown label. The ISO row can also read `software_version.build_number`
from XAPI. No failed inventory request prevents the rest of the System tab loading.

The separate XOA-HL appliance's application/image versions remain on its About
page. They are guest values: XO Lite cannot read the guest filesystem through
XAPI. This display does not guess them from current release tags or change
XenStore/guest metric identity publication (xcp-hl#30).

Validation on a released host must compare every row with `rpm -q` and
`BUILD_NUMBER` in `/etc/xensource-inventory`; also check host switching and a host
without the inventory plugin. Source pin remains `xo-lite-v0.21.0`.
