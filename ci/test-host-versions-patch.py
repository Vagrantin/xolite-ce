from pathlib import Path
import importlib.util
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('patch',ROOT/'patches/add-host-versions.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
SOURCE=Path(sys.argv.pop(1))
class Patch(unittest.TestCase):
    def test_pinned_source_and_drift_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/module.TARGET
            shutil.copytree(SOURCE/module.TARGET/'components',target/'components')
            (target/'libs').mkdir()
            module.apply(directory)
            page=target/'components/host/system/HostSystemGeneralInformation.vue'
            self.assertIn('<HostHlVersions :host="host" />',page.read_text())
            self.assertTrue((target/'libs/hl-host-versions.ts').exists())
            with self.assertRaises(ValueError): module.apply(directory)
            page.write_text('upstream drift')
            with self.assertRaises(ValueError): module.apply(directory)
if __name__=='__main__':unittest.main()
