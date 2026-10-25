#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

repo = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('login_patch', repo / 'patches/update-login-locales.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    source = Path(sys.argv[1])
    for relative in ('@xen-orchestra/lite/src/components/AppLogin.vue', '@xen-orchestra/web-core/lib/locales'):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if (source / relative).is_dir(): shutil.copytree(source / relative, target)
        else: shutil.copy2(source / relative, target)
    locale_dir = root / '@xen-orchestra/web-core/lib/locales'
    before = {p.stem: json.loads(p.read_text()) for p in locale_dir.glob('*.json')}
    module.apply(root)
    text = (root / '@xen-orchestra/lite/src/components/AppLogin.vue').read_text()
    assert ':label="t(\'username\')"' in text
    assert "{{ t('login') }}" in text
    assert "const login = ref('root')" in text
    assert 'name="login" readonly type="text"' in text
    for p in locale_dir.glob('*.json'):
        after = json.loads(p.read_text())
        assert all(after.get(k) for k in module.KEYS), p.stem
        assert all(after[k] == v for k, v in before[p.stem].items() if k not in module.KEYS), p.stem
    assert json.loads((locale_dir / 'fr.json').read_text())['username'] == "Nom d'utilisateur"
    assert json.loads((locale_dir / 'ja.json').read_text())['username'] == 'ユーザー名'
    try: module.apply(root)
    except ValueError: pass
    else: raise AssertionError('Unexpected upstream label must fail loudly')
print('Login label, locale completeness, scope and drift regressions passed')
