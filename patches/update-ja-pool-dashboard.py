#!/usr/bin/env python3
"""Merge Japanese pool dashboard messages into the pinned web-core catalog."""
import json
from pathlib import Path
import re
import sys


def apply(root):
    locales = Path(root) / '@xen-orchestra/web-core/lib/locales'
    english = json.loads((locales / 'en.json').read_text(encoding='utf-8'))
    target = locales / 'ja.json'
    japanese = json.loads(target.read_text(encoding='utf-8'))
    overrides = json.loads(Path(__file__).with_name('ja-pool-dashboard.json').read_text(encoding='utf-8'))
    for key, value in overrides.items():
        if key not in english:
            raise ValueError(f'Unknown upstream key: {key}; review the upstream pin')
        if not isinstance(value, str) or not value.strip() or value == english[key]:
            # Shared linked messages are intentional, but must resolve in Japanese.
            if not isinstance(value, str) or not value.startswith('@:'):
                raise ValueError(f'Missing Japanese translation: {key}')
        if set(re.findall(r'\{([^{}]+)\}', value)) != set(re.findall(r'\{([^{}]+)\}', english[key])):
            raise ValueError(f'Changed interpolation placeholders: {key}')
    merged = {**japanese, **overrides}
    for key in overrides:
        seen = set()
        while merged[key].startswith('@:'):
            if key in seen:
                raise ValueError(f'Circular Japanese message link: {key}')
            seen.add(key)
            key = merged[key][2:]
            if key not in merged or not isinstance(merged[key], str) or not merged[key].strip():
                raise ValueError(f'Missing Japanese message link: {key}')
    target.write_text(json.dumps(merged, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'Japanese pool dashboard: {len(overrides)} messages applied')


if __name__ == '__main__':
    apply(sys.argv[1] if len(sys.argv) > 1 else '.')
