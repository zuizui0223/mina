#!/usr/bin/env python3
"""Outcome-blind diagnostic of ADPE unknown-vantage temporal dependence."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import pandas as pd, pyreadr
from scripts.simulate_paper2_observation_recovery import build_frozen_observation_metadata
from scripts.simulate_paper2_latent_factor_recovery import build_scale_frame

def load_rda(path,expected):
    x=pyreadr.read_r(str(path)); return x[expected] if expected in x else next(iter(x.values()))

def run(forcing_result,forcing_units,breeding,metadata):
    frame=build_scale_frame(forcing_result,forcing_units,breeding,"ADPE","species_wide")
    out={}
    for unit in frame["unit_id"].astype(str):
        site=unit.split("|",1)[1]
        x=metadata[(metadata.species_id.astype(str)=="ADPE")&(metadata.site_id.astype(str)==site)].copy()
        all_seasons=sorted(set(x.season.astype(int)))
        known=x[x.vantage_family.astype(str)!="unknown"]
        known_seasons=sorted(set(known.season.astype(int)))
        unknown=x[x.vantage_family.astype(str)=="unknown"]
        unknown_seasons=sorted(set(unknown.season.astype(int)))
        unknown_only=sorted(set(unknown_seasons)-set(known_seasons))
        def thirds(ss):
            return {
              "n":len(ss),"span":(max(ss)-min(ss) if ss else 0),
              "first_third":any(1980<=s<=1994 for s in ss),
              "last_third":any(2010<=s<=2025 for s in ss),
              "first":min(ss) if ss else None,"last":max(ss) if ss else None
            }
        out[unit]={
          "records":int(len(x)),"known_records":int(len(known)),"unknown_records":int(len(unknown)),
          "all_seasons":all_seasons,"known_seasons":known_seasons,
          "unknown_seasons":unknown_seasons,"unknown_only_seasons":unknown_only,
          "all_support":thirds(all_seasons),"known_support":thirds(known_seasons),
          "ccamlr_id":str(frame.loc[frame.unit_id.astype(str)==unit,"ccamlr_id"].iloc[0]),
          "region":str(frame.loc[frame.unit_id.astype(str)==unit,"region"].iloc[0])
        }
    dependent=[u for u,v in out.items() if v["all_support"]["n"]>=5 and v["all_support"]["span"]>=10 and v["all_support"]["first_third"] and v["all_support"]["last_third"] and not (v["known_support"]["n"]>=5 and v["known_support"]["span"]>=10 and v["known_support"]["first_third"] and v["known_support"]["last_third"])]
    return {
      "schema_version":1,"audit_id":"mina-paper2-adpe-unknown-dependency",
      "ADPE_specieswide_units":int(len(frame)),
      "units_dependent_on_unknown_for_frozen_support":dependent,
      "dependent_details":{u:out[u] for u in dependent},
      "unknown_records_by_unit":{u:v["unknown_records"] for u,v in out.items() if v["unknown_records"]>0},
      "no_real_count_magnitudes_opened":True
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--forcing-json",type=Path,required=True);p.add_argument("--forcing-csv",type=Path,required=True);p.add_argument("--breeding-csv",type=Path,required=True);p.add_argument("--mapppdr-dir",type=Path,required=True);p.add_argument("--out-json",type=Path,required=True);a=p.parse_args()
    fr=json.loads(a.forcing_json.read_text());fu=pd.read_csv(a.forcing_csv);br=pd.read_csv(a.breeding_csv)
    meta=build_frozen_observation_metadata(load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs"))
    r=run(fr,fu,br,meta);a.out_json.parent.mkdir(parents=True,exist_ok=True);a.out_json.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n");print(json.dumps(r,indent=2,sort_keys=True))
if __name__=="__main__":main()
