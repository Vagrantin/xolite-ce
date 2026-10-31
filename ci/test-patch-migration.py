#!/usr/bin/env python3
"""Compare complete legacy and unified-diff pipelines on the immutable migration baseline."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile

REPO = Path(__file__).resolve().parents[1]
PAGE = '@xen-orchestra/lite/src/pages/xoa-deploy.vue'


def run(*args, cwd=None):
    subprocess.run([str(arg) for arg in args], cwd=cwd, check=True)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root):
    result = {}
    for path in root.rglob('*'):
        if path == root / 'patches':
            continue
        if path.is_symlink():
            result[str(path.relative_to(root))] = {'symlink': os.readlink(path)}
        elif path.is_file():
            result[str(path.relative_to(root))] = {'sha256': digest(path), 'git_mode': '100755' if path.stat().st_mode & 0o111 else '100644'}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('upstream', type=Path)
    parser.add_argument('legacy', type=Path)
    parser.add_argument('patcher_source', type=Path)
    parser.add_argument('--rebuilt-binary', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    record = json.loads((REPO / 'docs/patch-migration.json').read_text())
    for directory, pin in ((args.upstream, record['upstream_commit']),
                           (args.legacy, record['legacy_commit']),
                           (args.patcher_source, record['source_commit'])):
        actual = subprocess.check_output(['git', '-C', str(directory), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != pin:
            raise SystemExit(f'migration baseline mismatch: {directory}')
    binary = (args.legacy / record['legacy_binary_path']).resolve()
    source = args.patcher_source / record['source_path']
    if digest(binary) != record['legacy_binary_sha256'] or digest(source) != record['source_sha256']:
        raise SystemExit('legacy artifact or source hash mismatch')
    archive = subprocess.check_output(['git', '-C', str(args.upstream), 'archive', record['upstream_commit']])
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        old, new = root / 'old', root / 'new'
        for tree in (old, new):
            tree.mkdir()
            with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
                stream.extractall(tree, filter='data')
        print("Extracted both upstream trees", flush=True)
        original = snapshot(old)
        if digest(old / PAGE) != record['deploy_before_sha256']:
            raise SystemExit('unexpected original deploy page')
        run('git', 'apply', args.legacy.resolve() / 'patches/xoa-button-empty.patch', cwd=old)
        (old / 'patches').symlink_to(args.legacy.resolve() / 'patches', target_is_directory=True)
        run('bash', 'patches/update_locales.sh', cwd=old)
        for name in ('update-login-locales.py', 'update-ja-pool-dashboard.py',
                     'add-host-versions.py', 'add-guest-versions.py'):
            run('python3', f'patches/{name}', '.', cwd=old)
        run('bash', 'patches/update-xolite-loader.sh', cwd=old)
        run(binary, old / PAGE)
        if digest(old / PAGE) != record['deploy_after_sha256']:
            raise SystemExit('unexpected legacy deploy output')
        if args.rebuilt_binary:
            rebuilt_page = root / 'rebuilt.vue'
            rebuilt_page.write_bytes((new / PAGE).read_bytes())
            run(args.rebuilt_binary.resolve(), rebuilt_page)
            if rebuilt_page.read_bytes() != (old / PAGE).read_bytes():
                raise SystemExit('pinned source rebuild differs from vendored executable')
        run('python3', 'patches/cleanup-deploy-secrets.py', PAGE, cwd=old)
        run('bash', REPO / 'scripts/patch-source.sh', new)
        for tree in (old, new):
            package = json.loads((tree / '@xen-orchestra/lite/package.json').read_text())
            needs_robots = subprocess.run(['dpkg', '--compare-versions', package['version'], 'lt', '0.22.0']).returncode
            if needs_robots == 0:
                run('cp', tree / 'packages/xo-server/robots.txt', tree / '@xen-orchestra/lite/public/robots.txt')
        print("Completed both source pipelines", flush=True)
        old_state, new_state = snapshot(old), snapshot(new)
        if old_state != new_state:
            changed = sorted(key for key in old_state.keys() | new_state.keys()
                             if old_state.get(key) != new_state.get(key))
            details = {key: {'legacy': old_state.get(key), 'new': new_state.get(key)} for key in changed}
            raise SystemExit(f'pipeline output differs: {details}')
        changed = {key: value for key, value in new_state.items() if original.get(key) != value}
        report = {'provenance': record, 'compared_files': len(new_state), 'changed_files': changed,
                  'rebuilt_source_matches': args.rebuilt_binary is not None}
        if args.rebuilt_binary:
            report['rebuilt_binary_sha256'] = digest(args.rebuilt_binary)
        if args.report:
            args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
        print(f'Complete pipelines match: {len(new_state)} files, {len(changed)} changed files')


if __name__ == '__main__':
    main()
