import gzip
import unittest

import check_upstream_xolite as drift


class DriftCheckTests(unittest.TestCase):
    def test_primary_metadata_selects_newest_xolite_only(self):
        xml = b'''<metadata xmlns="http://linux.duke.edu/metadata/common">
          <package><name>xo-lite</name><arch>noarch</arch><version ver="0.24.0"/></package>
          <package><name>other</name><arch>noarch</arch><version ver="9.0.0"/></package>
          <package><name>xo-lite</name><arch>noarch</arch><version ver="0.26.0"/></package>
        </metadata>'''
        self.assertEqual(drift.latest_xolite(gzip.compress(xml)), (0, 26, 0))

    def test_repodata_location_and_tag_are_strict(self):
        repomd = b'''<repomd xmlns="http://linux.duke.edu/metadata/repo">
          <data type="primary"><checksum type="sha256">''' + b'a' * 64 + b'''</checksum>
          <location href="repodata/abc-primary.xml.gz"/></data></repomd>'''
        self.assertEqual(drift.primary_location(repomd), ("repodata/abc-primary.xml.gz", "a" * 64))
        self.assertEqual(drift.parse_tag("xo-lite-v0.21.0\n"), (0, 21, 0))
        with self.assertRaises(ValueError):
            drift.parse_tag("v0.21.0")
        with self.assertRaises(ValueError):
            drift.primary_location(repomd.replace(b"repodata/abc", b"../abc"))


if __name__ == "__main__":
    unittest.main()
