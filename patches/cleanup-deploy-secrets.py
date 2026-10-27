#!/usr/bin/env python3
"""Extend the pinned deployment's common XAPI cleanup; fail on source drift."""
import pathlib
import sys

OLD = "['admin-account', 'dns', 'gateway', 'ip', 'netmask', 'xoa-updater-credentials']"
NEW = "['admin-account', 'system-account-xoa-password', 'dns', 'gateway', 'ip', 'netmask', 'xoa-updater-credentials']"


def patch(source):
    if source.count(OLD) != 1:
        raise ValueError('Expected exactly one deployment cleanup landmark')
    return source.replace(OLD, NEW)


if __name__ == '__main__':
    path = pathlib.Path(sys.argv[1])
    path.write_text(patch(path.read_text()))
