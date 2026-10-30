#!/usr/bin/env python3
"""Check the actual pinned dashboard consumers and the CE patch sequence."""
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from unittest.mock import patch

repo = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, repo / f'patches/{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dashboard = load('update-ja-pool-dashboard')
login = load('update-login-locales')
overrides = json.loads((repo / 'patches/ja-pool-dashboard.json').read_text(encoding='utf-8'))
source = Path(sys.argv[1])
components = source / '@xen-orchestra/lite/src/components'
consumers = sorted((components / 'pool/dashboard').rglob('*.vue'))
assert consumers, 'Missing pinned pool dashboard components'
consumers += [components / 'pool/PoolTabBar.vue', components / 'modals/UnreachableHostsModal.vue']
keys = {m[1] for p in consumers for m in re.finditer(r"\bt\(['\"]([^'\"]+)['\"]", p.read_text(encoding='utf-8'))}
reported = {
    'hosts', 'vms', 'host:status:active', 'host:status:inactive',
    'vm:status:active', 'vm:status:inactive', 'action:load-now',
    'unreachable-hosts', 'following-hosts-unreachable',
    'allow-self-signed-ssl', 'unreachable-hosts-reload-page',
}
assert reported <= keys, 'Reported consumers changed; review the upstream pin'

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    locales = root / '@xen-orchestra/web-core/lib/locales'
    shutil.copytree(source / '@xen-orchestra/web-core/lib/locales', locales)
    app_login = root / '@xen-orchestra/lite/src/components/AppLogin.vue'
    app_login.parent.mkdir(parents=True)
    shutil.copy2(components / 'AppLogin.vue', app_login)
    login.apply(root)
    before = {p.name: p.read_bytes() for p in locales.glob('*.json')}
    ja_before = json.loads(before['ja.json'])
    dashboard.apply(root)
    japanese = json.loads((locales / 'ja.json').read_text(encoding='utf-8'))
    english = json.loads((locales / 'en.json').read_text(encoding='utf-8'))
    for key in keys:
        seen = set()
        while True:
            assert key not in seen, f'Circular link: {key}'
            seen.add(key)
            assert key in japanese, f'English fallback for {key}'
            value = japanese[key]
            assert isinstance(value, str) and value.strip(), key
            if not value.startswith('@:'):
                assert value != english[key], f'English translation for {key}'
                break
            key = value[2:]
    assert japanese['hosts'] == 'ホスト'
    assert japanese['vms'] == '仮想マシン'
    assert japanese['status:active'] == '稼働中'
    assert japanese['status:inactive'] == '非稼働'
    assert japanese['username'] == 'ユーザー名'
    assert all(japanese[k] == v for k, v in ja_before.items() if k not in overrides)
    assert all(p.read_bytes() == before[p.name] for p in locales.glob('*.json') if p.name != 'ja.json')
    applied = (locales / 'ja.json').read_bytes()
    dashboard.apply(root)
    assert (locales / 'ja.json').read_bytes() == applied, 'Patch must be idempotent'

    # Bad keys, lost placeholders and broken/circular links must fail before writing.
    invalid = [
        {**overrides, 'not-an-upstream-key': '不明'},
        {**overrides, 'n-missing': '未適用'},
        {**overrides, 'hosts': 'Hosts'},
        {**overrides, 'host:status:active': '@:missing-link'},
        {**overrides, 'status:active': '@:host:status:active'},
    ]
    for messages in invalid:
        manifest = root / 'ja-pool-dashboard.json'
        manifest.write_text(json.dumps(messages, ensure_ascii=False), encoding='utf-8')
        with patch.object(dashboard, '__file__', str(root / 'update-ja-pool-dashboard.py')):
            try:
                dashboard.apply(root)
            except ValueError:
                pass
            else:
                raise AssertionError('Invalid translation must fail')
        assert (locales / 'ja.json').read_bytes() == applied, 'Validation must precede writes'

workflow = (repo / '.github/workflows/build-xolite-ce.yml').read_text()
pipeline = (repo / 'scripts/patch-source.sh').read_text()
assert pipeline.index('python3 patches/update-login-locales.py .') < pipeline.index('python3 patches/update-ja-pool-dashboard.py .')
assert workflow.index('bash scripts/patch-source.sh xen-orchestra') < workflow.index('- name: Build XO Lite')
print(f'Japanese dashboard: {len(keys)} consumer keys, links, placeholders, scope and patch sequence passed')
