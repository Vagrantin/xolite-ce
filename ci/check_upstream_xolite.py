#!/usr/bin/env python3
"""Alert when the pinned XO Lite falls behind XCP-ng 8.3 updates."""

import argparse
import gzip
import hashlib
import io
from pathlib import Path
import re
import sys
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen
import xml.etree.ElementTree as ET

REPO = "https://updates.xcp-ng.org/8/8.3/updates/x86_64/"
TAG = re.compile(r"xo-lite-v(\d+)\.(\d+)\.(\d+)\Z")
VERSION = re.compile(r"(\d+)\.(\d+)\.(\d+)\Z")
REPO_NS = "{http://linux.duke.edu/metadata/repo}"
PKG_NS = "{http://linux.duke.edu/metadata/common}"


def parse_tag(value):
    match = TAG.fullmatch(value.strip())
    if not match:
        raise ValueError(f"invalid UPSTREAM_TAG: {value!r}")
    return tuple(map(int, match.groups()))


def primary_location(repomd):
    root = ET.fromstring(repomd)
    for data in root.findall(f"{REPO_NS}data"):
        if data.get("type") != "primary":
            continue
        location = data.find(f"{REPO_NS}location")
        checksum = data.find(f"{REPO_NS}checksum")
        if location is None or checksum is None or checksum.get("type") != "sha256":
            break
        href = location.get("href", "")
        if not re.fullmatch(r"repodata/[a-zA-Z0-9._-]+-primary\.xml\.gz", href):
            raise ValueError(f"unexpected primary metadata location: {href}")
        if not re.fullmatch(r"[a-fA-F0-9]{64}", checksum.text or ""):
            raise ValueError("invalid primary metadata checksum")
        return href, checksum.text.lower()
    raise ValueError("repomd.xml has no gzip primary metadata with SHA-256")


def latest_xolite(primary_gz):
    newest = None
    with gzip.GzipFile(fileobj=io.BytesIO(primary_gz)) as stream:
        for _, elem in ET.iterparse(stream, events=("end",)):
            if elem.tag != f"{PKG_NS}package":
                continue
            name = elem.findtext(f"{PKG_NS}name")
            arch = elem.findtext(f"{PKG_NS}arch")
            if name == "xo-lite" and arch == "noarch":
                version = elem.find(f"{PKG_NS}version")
                match = VERSION.fullmatch(version.get("ver", "")) if version is not None else None
                if not match:
                    raise ValueError("unexpected xo-lite RPM version")
                value = tuple(map(int, match.groups()))
                newest = max(newest, value) if newest else value
            elem.clear()
    if newest is None:
        raise ValueError("no xo-lite.noarch in XCP-ng 8.3 updates metadata")
    return newest


def fetch_latest():
    with urlopen(urljoin(REPO, "repodata/repomd.xml"), timeout=30) as response:
        href, expected = primary_location(response.read())
    url = urljoin(REPO, href)
    if urlparse(url).netloc != urlparse(REPO).netloc:
        raise ValueError("primary metadata escaped repository host")
    with urlopen(url, timeout=30) as response:
        primary = response.read()
    if hashlib.sha256(primary).hexdigest() != expected:
        raise ValueError("primary metadata SHA-256 mismatch")
    return latest_xolite(primary)


def format_version(version):
    return ".".join(map(str, version))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-only", action="store_true", help="report lag without failing")
    parser.add_argument("--previous-tag", help="prior pin from the PR base for rollback detection")
    args = parser.parse_args()
    pin = parse_tag(Path("UPSTREAM_TAG").read_text())
    if args.previous_tag and pin < parse_tag(args.previous_tag):
        print("::warning::XO Lite pin moved backwards while Obsoletes is unversioned; review xcp-hl#42")
        return 1
    latest = fetch_latest()
    print(f"XO Lite CE pin: {format_version(pin)}; XCP-ng 8.3 updates: {format_version(latest)}")
    if latest[0] != pin[0] or latest[1] - pin[1] >= 2:
        message = "XO Lite CE pin is at least two minor releases behind XCP-ng updates (or major version changed); revisit xcp-hl#42"
        print(f"::warning::{message}")
        return 0 if args.report_only else 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f"XO Lite drift check failed: {exc}", file=sys.stderr)
        sys.exit(2)
