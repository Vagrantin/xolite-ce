#!/bin/bash
# Sign RPMs with rpm 4 inside rockylinux:9: the runner's rpm 6 writes only the
# new OpenPGP signature tag, which XCP-ng 8.3 dom0 rpm 4.11 cannot read.
# rockylinux:9's rpm emits a legacy header signature, same environment the
# xcp-hl-release RPM is signed in. Reads: /signing.key, /signing/*.rpm.
set -euxo pipefail

test -s /signing.key
ls /signing/*.rpm | head -1 | grep -q '\.rpm$'

dnf -y -q install rpm-sign pinentry

mkdir -pm 700 /root/.gnupg
echo allow-loopback-pinentry > /root/.gnupg/gpg-agent.conf
gpg --batch --pinentry-mode loopback \
    --passphrase "${GPG_PASSPHRASE}" \
    --import /signing.key

# Pre-cache the passphrase in gpg-agent; rpmsign signs transparently after this.
echo "${GPG_PASSPHRASE}" | gpg --batch --pinentry-mode loopback \
    --passphrase-fd 0 --quiet --no-tty \
    -u "XCP-ng Community Edition" \
    --sign --output /dev/null /dev/null

cat > /root/.rpmmacros <<'MACROS'
%_gpg_name XCP-ng Community Edition
%__gpg_sign_cmd %{__gpg} gpg --batch --no-verbose --no-armor \
  --no-secmem-warning --pinentry-mode loopback \
  -u "%{_gpg_name}" -sbo %{__signature_filename} \
  --digest-algo sha256 %{__plaintext_filename}
MACROS

rpm --version
for rpm_file in /signing/*.rpm; do
    rpmsign --addsign "${rpm_file}"
    echo "Signed: ${rpm_file}"
done
