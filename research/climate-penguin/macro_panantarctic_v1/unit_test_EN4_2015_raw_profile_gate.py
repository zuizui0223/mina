#!/usr/bin/env python3
"""Source-free QC and geography guards, no fake EN4 observation data."""
from __future__ import annotations
import importlib.util
import io
import zipfile
import unittest
from pathlib import Path

import numpy as np

spec=importlib.util.spec_from_file_location(
    "en4",Path(__file__).resolve().parent/"pilot_EN4_2015_raw_profile_salinity_coverage.py")
en4=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(en4)


class TestOriginalEN4QualityGate(unittest.TestCase):
    def test_source_QC_literal_accepted_vs_rejected(self):
        self.assertEqual(en4.letter(b"1"),"1")
        self.assertEqual(en4.letter(np.bytes_("4")),"4")
        self.assertEqual(en4.letter(np.array([b"1"])),"1")
        self.assertEqual(en4.letter(np.ma.masked),"")
        self.assertNotEqual(en4.letter(b"4"),"1")

    def test_original_sea_surface_depth_not_imputed(self):
        self.assertEqual(en4.QC_SURFACE_M,(10.,20.))
        self.assertEqual(en4.SALINITY_RANGE,(28.,38.))
        self.assertEqual(en4.MONTHS,(8,9,10,11))
        self.assertEqual(en4.YEAR,2015)

    def test_original_southern_nearest_WGS84_colony_and_fixed_radius(self):
        sites=[
            {"site_id":"A","source_region":"Test A","source_250km_block":"a",
             "colony_latitude":"-64.002","colony_longitude":"179.989"},
            {"site_id":"B","source_region":"Test B","source_250km_block":"b",
             "colony_latitude":"-72.5","colony_longitude":"22.6"}
        ]
        found=en4.coordinates_nearest_to_original_colonies(
            sites,
            np.asarray([-64.002,-72.49,-40.0]),
            np.asarray([-179.99,22.61,10.0]))
        self.assertEqual(found[0][0]["site_id"],"A")
        self.assertEqual(found[1][0]["site_id"],"B")
        self.assertNotIn(2,found)
        self.assertLess(found[0][1],100)

    def test_remote_zip_byte_ranges_read_only_selected_members(self):
        source=io.BytesIO()
        with zipfile.ZipFile(source,"w",compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("en4.201508.nc",b"correct raw Aug netCDF test"*15)
            z.writestr("en4.201509.nc",b"correct raw Sep netCDF test"*20)
            z.writestr("en4.201510.nc",b"correct raw Oct netCDF test"*100)
        original=source.getvalue()
        remote=en4.HTTPRangeZipReader(
            "https://example.invalid/official-en4-source.zip",
            len(original),chunk_bytes=37,cache_blocks=4)
        touched=set()
        def source_read_block(index):
            start=index*remote.chunk_bytes
            touched.add(index)
            return original[start:min(len(original),start+remote.chunk_bytes)]
        remote._fetch_block=source_read_block
        with zipfile.ZipFile(remote) as z:
            self.assertEqual(z.read("en4.201509.nc"),b"correct raw Sep netCDF test"*20)
            self.assertEqual(z.getinfo("en4.201508.nc").filename,"en4.201508.nc")
        self.assertTrue(touched)
        self.assertLess(len(touched)*remote.chunk_bytes,5*len(original))

    def test_original_sources_pinned_and_archive_goes_to_summary(self):
        self.assertIn("hadleyserver.metoffice.gov.uk",en4.BASE)
        self.assertTrue(en4.YEAR_ZIP.endswith("2015.zip"))
        self.assertEqual(len(en4.DIRECT_MONTHLY),4)
        self.assertEqual(en4.MAX_COLONY_DIST_KM,(100.,250.))


if __name__=="__main__":
    unittest.main()
