from pathlib import Path
import importlib.util
import shutil
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('guest_patch',ROOT/'patches/add-guest-versions.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
SOURCE=Path(sys.argv.pop(1))
class Patch(unittest.TestCase):
    def test_pinned_source_and_fail_loudly_on_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/module.TARGET
            shutil.copytree(SOURCE/module.TARGET/'components',target/'components')
            (target/'libs').mkdir()
            module.apply(directory)
            page=target/'components/vm/system/VmGeneralInfo.vue'
            self.assertIn('<VmHlVersions :metrics="guestMetrics" />',page.read_text())
            self.assertTrue((target/'libs/hl-guest-identity.ts').exists())
            with self.assertRaises(ValueError):module.apply(directory)
            page.write_text('upstream drift')
            with self.assertRaises(ValueError):module.apply(directory)
if __name__=='__main__':unittest.main()
