#!/usr/bin/env python3
"""Apply the CE login label correction and explicit locale overrides to pinned XO."""
import json
from pathlib import Path
import sys

KEYS = ('username', 'password', 'login', 'keep-me-logged', 'login-only-on-master', 'password-invalid', 'error-occurred', 'you-are-currently-on', 'click-to-return-default-pool')


def apply(root):
    root = Path(root)
    patch_dir = Path(__file__).resolve().parent
    overrides = json.loads((patch_dir / 'login-locales.json').read_text())
    login_path = root / '@xen-orchestra/lite/src/components/AppLogin.vue'
    login = login_path.read_text()
    original = '<VtsInputWrapper :label="t(\'login\')">'
    replacement = '<VtsInputWrapper :label="t(\'username\')">'
    if login.count(original) != 1:
        raise ValueError('Expected one login field label; review the patch against the upstream pin')
    locales = root / '@xen-orchestra/web-core/lib/locales'
    prepared = {}
    for path in sorted(locales.glob('*.json')):
        data = json.loads(path.read_text())
        changes = overrides.get(path.stem, {})
        if set(changes) - set(KEYS):
            raise ValueError('Unexpected login override key')
        data.update(changes)
        for key in KEYS:
            if not isinstance(data.get(key), str) or not data[key].strip() or data[key] == key:
                raise ValueError(f'{path.stem}: missing login translation {key}')
        if '{0}' not in data['you-are-currently-on']:
            raise ValueError(f'{path.stem}: missing pool warning placeholder')
        if changes:
            prepared[path] = data
    if set(overrides) - {p.stem for p in locales.glob('*.json')}:
        raise ValueError('Override for a missing locale')
    # Validate all catalogs before making changes; never manufacture English fallbacks.
    login_path.write_text(login.replace(original, replacement))
    for path, data in prepared.items():
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    print(f'Login label corrected; {len(list(locales.glob("*.json")))} locale catalogs checked')


if __name__ == '__main__':
    apply(sys.argv[1] if len(sys.argv) > 1 else '.')
