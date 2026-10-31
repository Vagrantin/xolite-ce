#!/bin/bash
# Verify a signed RPM the way dom0 would read it: a legacy header signature
# must be present (rpm -Kv prints "Header ... Signature"), digests and
# signatures must verify against the community public key. Reads:
# /pubkey.asc, /signing/*.rpm.
set -euxo pipefail

test -s /pubkey.asc
ls /signing/*.rpm | head -1 | grep -q '\.rpm$'

rpm --version
rpmdb=$(mktemp -d)
rpm --dbpath "${rpmdb}" --import /pubkey.asc

for rpm_file in /signing/*.rpm; do
    echo "── checksig: ${rpm_file}"
    rpm --dbpath "${rpmdb}" --checksig "${rpm_file}"
    rpm --dbpath "${rpmdb}" --checksig "${rpm_file}" | grep -Fq "digests signatures OK"

    legacy_sig=$(rpm --dbpath "${rpmdb}" -Kv "${rpm_file}")
    echo "${legacy_sig}"
    printf '%s\n' "${legacy_sig}" | grep -qiE 'Header .*[Ss]ignature' \
        || { echo "❌ no legacy header signature; rpm 4.11 (dom0) sees this package as unsigned"; exit 1; }
done
echo "✅ signature readable by rpm 4.x header format"
