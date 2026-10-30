#!/usr/bin/env python3
"""Validate the complete ordered diff series before applying anything."""
from pathlib import Path
import re
import sys
import tomllib


def read_series(directory):
    root = Path(directory)
    names = (root / 'series').read_text().splitlines()
    if not names or len(names) != len(set(names)):
        raise ValueError('empty series or duplicate entries')
    prefixes = set()
    for name in names:
        if name == 'xoa-button-empty.patch':
            continue
        if not re.fullmatch(r'[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*\.patch', name):
            raise ValueError(f'invalid patch name: {name}')
        if name[:3] in prefixes:
            raise ValueError('duplicate numeric prefix')
        prefixes.add(name[:3])
    if set(names) != {p.name for p in root.glob('*.patch')}:
        raise ValueError('missing or unlisted patch')
    entries = tomllib.loads((root / 'metadata.toml').read_text())['patches']
    ids = [entry['id'] for entry in entries]
    order = {Path(name).stem: index for index, name in enumerate(names)}
    if len(ids) != len(set(ids)) or set(ids) != set(order):
        raise ValueError('metadata IDs must match series exactly')
    for entry in entries:
        for field in ('description', 'target', 'upstream_commit', 'maintainer'):
            if not isinstance(entry[field], str) or not entry[field].strip():
                raise ValueError(f'invalid {field}')
        if entry['status'] not in ('active', 'deprecated', 'superseded'):
            raise ValueError('invalid patch status')
        for field in ('dependencies', 'applies_to'):
            if not isinstance(entry[field], list) or any(not isinstance(v, str) for v in entry[field]):
                raise ValueError(f'invalid {field}')
        for dependency in entry['dependencies']:
            if dependency not in order or order[dependency] >= order[entry['id']]:
                raise ValueError(f'dependency must precede {entry["id"]}: {dependency}')
    return [root / name for name in names]


if __name__ == '__main__':
    try:
        print('\n'.join(str(path) for path in read_series(sys.argv[1])))
    except (ValueError, KeyError, OSError) as error:
        sys.exit(str(error))
