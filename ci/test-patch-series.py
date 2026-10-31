#!/usr/bin/env python3
"""Check malformed series and atomic rejection of source drift."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('series', REPO / 'scripts/list-patches.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SeriesTests(unittest.TestCase):
    def fixture(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        shutil.copytree(REPO / 'patches', root / 'patches')
        return root / 'patches'

    def test_complete_series(self):
        self.assertEqual(len(module.read_series(REPO / 'patches')), 2)

    def test_rejects_duplicate_missing_unlisted_and_bad_names(self):
        for kind in ('duplicate', 'missing', 'unlisted', 'bad-name', 'duplicate-prefix'):
            with self.subTest(kind=kind):
                root = self.fixture()
                text = (root / 'series').read_text()
                if kind == 'duplicate': text += '010-xoa-deploy.patch\n'
                if kind == 'missing': (root / '010-xoa-deploy.patch').unlink()
                if kind == 'unlisted': (root / '020-extra.patch').touch()
                if kind in ('bad-name', 'duplicate-prefix'):
                    name = 'zzzz-extra.patch' if kind == 'bad-name' else '010-extra.patch'
                    (root / name).touch()
                    text += name + '\n'
                (root / 'series').write_text(text)
                with self.assertRaises(ValueError): module.read_series(root)

    def test_rejects_metadata_and_dependency_errors(self):
        for old, new in [('id = "010-xoa-deploy"', 'id = "missing"'),
                         ('dependencies = []', 'dependencies = ["missing"]'),
                         ('dependencies = []', 'dependencies = ["010-xoa-deploy"]')]:
            root = self.fixture()
            path = root / 'metadata.toml'
            path.write_text(path.read_text().replace(old, new, 1))
            with self.assertRaises(ValueError): module.read_series(root)

    def test_drift_and_repeat_leave_files_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            source.mkdir()
            for filename in ('a', 'b'):
                (source / filename).write_text('before\n')
            consumer = root / 'consumer'
            shutil.copytree(REPO / 'scripts', consumer / 'scripts')
            shutil.copytree(REPO / 'patches', consumer / 'patches')
            names = (consumer / 'patches/series').read_text().splitlines()
            for filename, name in zip(('a', 'b'), names):
                patch = consumer / 'patches' / name
                patch.write_text(f'--- a/{filename}\n+++ b/{filename}\n@@ -1 +1 @@\n-before\n+after\n')
            command = ['bash', str(consumer / 'scripts/apply-patches.sh'), str(source)]
            (source / 'b').write_text('drift\n')
            before = {p.name: p.read_bytes() for p in source.iterdir()}
            result = subprocess.run(command, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(before, {p.name: p.read_bytes() for p in source.iterdir()})
            (source / 'b').write_text('before\n')
            subprocess.run(command, check=True)
            before = {p.name: p.read_bytes() for p in source.iterdir()}
            result = subprocess.run(command, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(before, {p.name: p.read_bytes() for p in source.iterdir()})


if __name__ == '__main__':
    unittest.main()
