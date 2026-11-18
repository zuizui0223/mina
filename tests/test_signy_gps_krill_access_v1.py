"""Source data, geometry, GPS spikes, repeated-pixel and native-year tests."""
from __future__ import annotations
import datetime as dt,importlib.util,json,math,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"research/climate-penguin/work/climate_penguin/signy_gps_krill_access_v1.py"
spec=importlib.util.spec_from_file_location("signy_gps_access",P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class GPSKrillAccessTests(unittest.TestCase):
    def test_distance_and_one_hour_actual_location(self):
        self.assertAlmostEqual(float(m.geodesic([-60.704025],[-45.6275835])[0]),0,places=9)
        base=dt.datetime(2013,12,2,11,0)
        fixes=[(base+dt.timedelta(minutes=i*15),float(i),1.0,i) for i in range(4)]
        out=m.selected_hourly(fixes)
        self.assertEqual(len(out),1)
        self.assertEqual(out[0][1],1.0)
    def test_remove_isolated_extreme_jump(self):
        base=dt.datetime(2013,12,2,11,0)
        pts=[(base+dt.timedelta(minutes=i),-60.7,-45.7 if i!=1 else -40.0,i) for i in range(3)]
        mask=m.singleton_spike_mask(pts)
        self.assertEqual(mask.tolist(),[False,True,False])
    def test_geo_raster_lookup(self):
        from affine import Affine
        arr=np.array([[10.0,20.0],[30.0,40.0]])
        tr=Affine(1,0,0,0,-1,2)
        vals,rr,cc=m.sampled_cells(arr,tr,np.array([1.5,0.5]),np.array([0.5,1.5]))
        self.assertEqual(vals.tolist(),[10.0,40.0])
    def test_source_pins(self):
        self.assertEqual(m.TRACK_SHA,"e65a884341346a95ebb4a25de492d350716fde5f5cb77a669d66846811f6800a")
        self.assertEqual(sum(z[2] for z in m.TRACK_FILES.values()),173)
        pins=json.loads(m.TIFF_PINS.read_text(encoding="utf-8"))
        self.assertEqual(len(pins),10)
    def test_original_archive_and_2013_source_receipt(self):
        gps=ROOT/"build/signy_gps_source"
        krill=ROOT/"build/freer_krill/bas_published_source.zip"
        stage=ROOT/"build/signy_stage_derived/species_annual_stage_summary.csv"
        if not(gps.exists() and krill.exists() and stage.exists()):
            self.skipTest("original BAS GPS/raster/breeding source downloads only in dedicated Actions workflow")
        tracks,audit=m.read_tracks(gps)
        models=m.source_models(krill)
        stg=m.annual_stage(stage)
        rows=m.tracking_vs_models(tracks,models)
        geo=m.geographic_index(models)
        annual=m.by_species_year(rows,stg,geo)
        prim=[r for r in annual if r["minimum_distance_km"]==10 and r["isolated_spike_filter"]]
        out={"original_unique_deployments":len(tracks),
             "source_positions":sum(r["raw_count"] for r in tracks),
             "qualifying_deployments_primary":sum(r["n_qualified_deployments"] for r in prim),
             "common_3species_seasons":sorted(set.intersection(*[
                {r["season_start"] for r in prim if r["species"]==sp} for sp in m.TRACK_FILES
             ])), "primary_species_years":prim}
        self.assertTrue(m.verify(rows,out))
        loo=m.leave_one_deployment_out(rows)
        self.assertTrue(m.verify_2013_loo(loo))
        self.assertEqual(len(loo),9)
        self.assertEqual(audit["species"]["Chinstrap"]["empty_gps_source_file"],4)
        self.assertEqual(audit["species"]["Chinstrap"]["identical_duplicate_source_file"],1)
        self.assertEqual(sum(int(z["qualifies"]) for z in rows if z["minimum_distance_km"]==10 and z["isolated_spike_filter"]),152)
if __name__=="__main__":
    unittest.main()
