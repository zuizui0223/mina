"""Independent numerical audits for penguin niche timescale comparison."""
from __future__ import annotations
import csv
import json
import math
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
OUTS=REPO/"research/climate-penguin/outputs"
SCRIPT=REPO/"research/climate-penguin/work/niche_timescale_divergence_v1/analyze.py"
def table(path):
    with path.open(encoding="utf-8",newline="") as fp:
        return list(csv.DictReader(fp))
def slope(xs,ys):
    mx=sum(xs)/len(xs);my=sum(ys)/len(ys)
    return sum((a-mx)*(b-my) for a,b in zip(xs,ys))/sum((a-mx)**2 for a in xs)
class TestOriginalTimeWindow(unittest.TestCase):
    def test_all_original_source_six_sites(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["python",str(SCRIPT),"--out",tmp],cwd=REPO,check=True,capture_output=True)
            output=Path(tmp)
            summary=json.loads((output/"summary.json").read_text())
            results=table(output/"site_trends.csv")
            yearly=table(output/"site_years.csv")
            interval=table(output/"annual_intervals.csv")
            original=table(OUTS/"comparison_audit/mapppd_unambiguous_site_seasons.csv")
            near=table(OUTS/"climate_penguin/macro_monthly_seaice_1991_2020.csv")
            counts={(r["site_id"],r["species_id"],int(r["season"]),r["method"]):float(r["count"])
                    for r in original if r["count"]!=""}
            ice={(r["site_id"],int(r["year"]),int(r["month"])):float(r["sic_mean"]) for r in near
                 if r["inner_km"]=="0" and r["complete_month"]=="True"}
            pairs=table(OUTS/"warming_species_breeding_v1/matched_species_breeding_change.csv")
            methods={(r["site_id"],r["compared_species"]):r["method_compared"] for r in pairs}
            self.assertEqual((len(results),len(yearly),len(interval)),(6,67,45))
            self.assertEqual([r["site_id"] for r in results],["ARDL","BISC","LION","LLAN","PCHA","PETE"])
            self.assertEqual(summary["n_observation_window_september_ice_rising"],4)
            self.assertEqual(summary["n_observation_window_aug_nov_ice_rising"],2)
            self.assertEqual(summary["n_full_1991_2020_aug_nov_ice_declining"],6)
            self.assertAlmostEqual(summary["corr_one_year_species_growth"],0.20790044100407323,places=10)
            self.assertAlmostEqual(summary["corr_one_year_ratio_change_sic_change"],-0.3243343688480978,places=10)
            for s in results:
                key=s["site_id"]; rows=sorted((r for r in yearly if r["site_id"]==key),key=lambda r:int(r["year"]))
                y=[int(r["year"]) for r in rows]
                method=methods[(key,"GEPE")]
                a=[counts[(key,"ADPE",t,method)] for t in y]
                g=[counts[(key,"GEPE",t,method)] for t in y]
                self.assertTrue(all(q>0 for q in a+g))
                self.assertAlmostEqual(float(s["real_log_gentoo_adelie_ratio_slope_per_decade"]),
                                       10*slope(y,[math.log(gn/an) for an,gn in zip(a,g)]),places=10)
                self.assertAlmostEqual(float(s["observed_years_september_sic_slope_pp_per_decade"]),
                                       10*slope(y,[ice[(key,t,9)] for t in y]),places=10)
                all_year=list(range(1991,2021))
                self.assertAlmostEqual(float(s["full_1991_2020_aug_nov_sic_slope_pp_per_decade"]),
                                       10*slope(all_year,[sum(ice[(key,t,m)] for m in (8,9,10,11))/4 for t in all_year]),places=10)
            self.assertEqual(sum(int(r["same_sign_growth"]) for r in interval),20)
            self.assertEqual(sum(int(r["opposite_sign_growth"]) for r in interval),25)
            self.assertEqual(summary["future_ssp585_2081_2100_physical_only"]["n_three_model_warming"],6)
            self.assertEqual(summary["future_ssp585_2081_2100_physical_only"]["n_three_model_sic_decrease"],6)
if __name__=="__main__":
    unittest.main()
