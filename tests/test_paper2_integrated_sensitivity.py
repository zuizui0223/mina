import unittest

try:
    import pandas as pd
except ModuleNotFoundError as exc:
    raise unittest.SkipTest("integrated sensitivity tests require pandas") from exc

from scripts.simulate_paper2_integrated_sensitivity import (
    filter_process_support,
)
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata,
)


class RawVantageMetadataTests(unittest.TestCase):
    def test_frozen_metadata_retains_raw_vantage_without_count(self):
        rows=[]
        gate0={"ADPE":57,"CHPE":46,"GEPE":49}
        bridged={"ADPE":44,"CHPE":34,"GEPE":29}
        index=0
        for sp in ("ADPE","CHPE","GEPE"):
            for j in range(gate0[sp]):
                site=f"S{index:03d}"
                years=[1980,1985,1990,1995,2000]
                seasons=(
                    [1980,1990,2000,2010,2020]
                    if j<bridged[sp]
                    else [1995,2000,2005,2010,2015]
                )
                raws=["ground","aerial","ground photo","ground","ground"]
                for year,season,vantage in zip(years,seasons,raws):
                    rows.append({
                        "site_id":site,"species_id":sp,"type":"nests",
                        "count":1000+index,"year":year,"season":season,
                        "vantage":vantage,"accuracy":1,
                    })
                index+=1
        out=build_frozen_observation_metadata(pd.DataFrame(rows))
        self.assertIn("vantage_raw",out.columns)
        self.assertNotIn("count",out.columns)
        self.assertIn("ground",set(out["vantage_raw"]))
        self.assertIn("aerial",set(out["vantage_raw"]))


class ProcessSupportTests(unittest.TestCase):
    def test_ground_only_support_uses_raw_ground_not_direct_family(self):
        frame=pd.DataFrame([
            {"unit_id":"ADPE|A","site_id":"A","species_id":"ADPE"},
            {"unit_id":"ADPE|B","site_id":"B","species_id":"ADPE"},
        ])
        rows=[]
        for season in (1980,1990,2000,2010,2020):
            rows.append({
                "unit_id":"ADPE|A","site_id":"A","species_id":"ADPE",
                "season":season,"vantage_family":"direct","vantage_raw":"ground",
            })
            rows.append({
                "unit_id":"ADPE|B","site_id":"B","species_id":"ADPE",
                "season":season,"vantage_family":"direct","vantage_raw":"aerial",
            })
        supported,meta=filter_process_support(
            frame,pd.DataFrame(rows),mode="ground_only"
        )
        self.assertEqual(set(supported["unit_id"]),{"ADPE|A"})
        self.assertEqual(meta["supported_units"],1)

    def test_exclude_unknown_keeps_known_bridged_unit(self):
        frame=pd.DataFrame([
            {"unit_id":"GEPE|A","site_id":"A","species_id":"GEPE"},
        ])
        rows=[
            {
                "unit_id":"GEPE|A","site_id":"A","species_id":"GEPE",
                "season":season,
                "vantage_family":"direct" if season!=2000 else "unknown",
                "vantage_raw":"ground" if season!=2000 else "missing",
            }
            for season in (1980,1990,2000,2010,2020,2025)
        ]
        supported,meta=filter_process_support(
            frame,pd.DataFrame(rows),mode="exclude_unknown"
        )
        self.assertEqual(len(supported),1)
        self.assertEqual(meta["supported_units"],1)


if __name__=="__main__":
    unittest.main()
