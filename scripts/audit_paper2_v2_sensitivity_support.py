#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import pandas as pd, pyreadr
from scripts.simulate_paper2_latent_factor_recovery import build_scale_frame
from scripts.simulate_paper2_observation_recovery import build_frozen_observation_metadata
from scripts.audit_paper2_integrated_sensitivity_support import filter_process_support

SPECIES=("ADPE","CHPE","GEPE")

def load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    return x[expected] if expected in x else next(iter(x.values()))

def run(forcing_result,forcing_units,breeding,metadata):
    frames={sp:build_scale_frame(forcing_result,forcing_units,breeding,sp,"species_wide") for sp in SPECIES}
    expected={"ADPE":41,"CHPE":34,"GEPE":29}
    got={sp:len(x) for sp,x in frames.items()}
    if got!=expected: raise ValueError(f"frame drift {got} != {expected}")
    modes={}
    for mode in ("exclude_unknown","ground_only"):
        modes[mode]={}
        for sp in SPECIES:
            _,summary=filter_process_support(frames[sp],metadata,mode=mode)
            modes[mode][sp]={
                "candidate_units":summary["candidate_units"],
                "supported_units":summary["supported_units"],
                "coverage_fraction":summary["coverage_fraction"],
                "classification":summary["classification"],
                "supported_unit_ids":summary["supported_unit_ids"],
            }
    return {
      "schema_version":2,
      "audit_id":"mina-paper2-v2-sensitivity-support",
      "forcing_scale_by_species":{sp:"species_wide" for sp in SPECIES},
      "frame_units":got,"modes":modes,
      "decision":{
        "exclude_unknown_all_species_testable":all(modes["exclude_unknown"][sp]["classification"]=="testable" for sp in SPECIES),
        "ground_only_testable_species":[sp for sp in SPECIES if modes["ground_only"][sp]["classification"]=="testable"],
        "no_real_count_magnitudes_opened":True
      }
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--forcing-json",type=Path,required=True); p.add_argument("--forcing-csv",type=Path,required=True)
    p.add_argument("--breeding-csv",type=Path,required=True); p.add_argument("--mapppdr-dir",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True); a=p.parse_args()
    fr=json.loads(a.forcing_json.read_text()); fu=pd.read_csv(a.forcing_csv); br=pd.read_csv(a.breeding_csv)
    obs=load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
    meta=build_frozen_observation_metadata(obs)
    out=run(fr,fu,br,meta); a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
