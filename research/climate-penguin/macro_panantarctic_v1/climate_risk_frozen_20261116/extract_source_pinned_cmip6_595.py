#!/usr/bin/env python3
"""Expand original 2026-10 source-pinned CMIP6 projection from 106 to 595 sites.

Reuses existing validated remote Zarr extraction *without editing its source*.
Original three model/member/store choices are pinned to the already published
selected_stores.csv, original model code SHA is preserved. Runs in a temporary
output namespace instead of overwriting the historical 106-site source archive.

Model future delta != forecast change in actual nesting or habitat suitability.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,shutil,sys
from pathlib import Path
import pandas as pd
from pyproj import Geod

HERE=Path(__file__).resolve()
REPO=HERE.parents[3] # research/climate-penguin? inspect below
# Use exact source-internal filenames resolved from this source's location.
CLIMATE=HERE.parents[2] # research/climate-penguin
EXTRACT=CLIMATE/"work/cmip6_projection_v1/extract.py"
SELECTED=CLIMATE/"outputs/cmip6_projection_v1/selected_stores.csv"
EXPECTED_MODEL_MAP={"ACCESS-CM2":"r1i1p1f1","BCC-CSM2-MR":"r1i1p1f1","CESM2":"r4i1p1f1"}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-site-inventory",required=True,type=Path)
    parser.add_argument("--output-root",required=True,type=Path)
    parser.add_argument("--workers",default=3,type=int)
    parser.add_argument("--select-only",action="store_true")
    a=parser.parse_args()
    assert EXTRACT.is_file() and SELECTED.is_file(),(EXTRACT,SELECTED)
    assert a.workers in (1,2,3,4), "Bounded remote GCS pressure"
    original=pd.read_csv(a.source_site_inventory)
    expected={"site_id","source_region","latitude","longitude"}
    if len(original)!=595 or original.site_id.nunique()!=595 or not expected.issubset(original):
        raise ValueError("Must use frozen 595 unique original known-colony catalogue")
    if not (original.latitude.between(-90,-55).all() and original.longitude.between(-180,180).all()):
        raise ValueError("Invalid original Antarctic colony coordinates")
    if original.source_region.nunique()!=18:
        raise ValueError("Original reporting region membership drift")
    model=pd.read_csv(SELECTED)
    if len(model)!=27 or model.source_id.nunique()!=3 or model.variable_id.nunique()!=3:
        raise ValueError("Published 27 source-store selection changed")
    for name,member in EXPECTED_MODEL_MAP.items():
        if set(model.loc[model.source_id.eq(name),"member_id"])!={member}:
            raise ValueError("Published model/member changed unexpectedly")
    if not model.groupby(["source_id","variable_id"]).experiment_id.nunique().eq(3).all():
        raise ValueError("Source historical/SSP manifest incomplete")

    out=a.output_root.resolve()
    work=out/"work"
    root=out/"source_root"
    target=root/"outputs/climate_penguin/daily_ice_locations.csv"
    result=root/"outputs/cmip6_projection_v1"
    for d in (work,target.parent,result):
        d.mkdir(parents=True,exist_ok=True)
    site=original[["site_id","latitude","longitude"]].copy()
    site.insert(0,"location_id",site.site_id)
    site["cohort"]="original_595_known_source_sites"
    assert site.location_id.is_unique
    site=site.sort_values("location_id")
    site.to_csv(target,index=False)
    # Historical version-fixed catalog only; no new models may enter silently.
    shutil.copyfile(SELECTED,work/"catalog.csv")
    source_receipt={
        "status":"SOURCE_PINNED_595_CMIP6_REMOTE_ZARR_WORKFLOW",
        "scope":"595 known catalogued original penguin colony points, not equally surveyed biological samples",
        "historical_source_model_selection_sha256":sha(SELECTED),
        "original_106_site_extractor_code_sha256":sha(EXTRACT),
        "original_595_site_inventory_sha256":sha(a.source_site_inventory),
        "generated_595_model_sites_sha256":sha(target),
        "selected_original_source_models":EXPECTED_MODEL_MAP,
        "original_source_106_site_results_unchanged":True,
        "original_cmip6_1995_2014_reference_to_2041_2060_and_2081_2100":True,
        "three_physical_variables":["tas","siconc","sos"],
        "no_nest_abundance_change_prediction":True
    }
    (out/"595_model_source_receipt.json").write_text(json.dumps(source_receipt,indent=2)+"\n")
    spec=importlib.util.spec_from_file_location("frozen_original_cmip6_extractor",str(EXTRACT))
    module=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    module.ROOT=root
    module.WORK=work
    module.OUT=result
    sys.argv=[str(EXTRACT),"--workers",str(a.workers)] + (["--select-only"] if a.select_only else [])
    module.main()
    if a.select_only:
        selected=pd.read_csv(result/"selected_stores.csv")
        assert len(selected)==27 and set(selected.zstore)==set(model.zstore)
        print("SOURCE_PINNED 27 original CMIP6 stores selected, 595 sites cohort frozen")
        return
    manifest=json.loads((result/"manifest.json").read_text())
    if manifest.get("status")!="complete" or manifest["n_stores_read"]!=27 or manifest["failures"]:
        raise RuntimeError("Remote physical data source incomplete")
    expected_future=595*3*3*2*2 # 595 locations x 3 models x 3 variables x 2 future SSP x 2 periods
    delta=pd.read_csv(result/"site_model_changes.csv")
    ensemble=pd.read_csv(result/"site_model_ensemble.csv")
    assert len(delta)==expected_future, (len(delta),expected_future)
    assert len(ensemble)==595*3*2*2
    assert delta.groupby(["source_id","variable_id","experiment_id","period"]).site_id.nunique().eq(595).all()
    assert ensemble.n_models.eq(3).all()
    assert delta.complete_years.eq(20).all()
    assert not delta.duplicated(["source_id","variable_id","experiment_id","period","site_id"]).any()
    assert manifest["n_site_changes"]==len(delta)
    report={"status":"PASS_PHYSICAL_ONLY_595_SELECTED_SOURCE",
        "n_original_colonies":595,"n_original_regions":18,
        "n_model_future_rows":len(delta),
        "n_model_ensemble_rows":len(ensemble),
        "n_archive_site_ids":delta.site_id.nunique(),
        "input_source_sha256":source_receipt,
        "n_original_source_models":3,
        "no_breeding_response_prediction":True,
        "full_595_site_source_coverage_does_not_imply_595_true_censused_past_or_future":True,
        "do_not_interpret_sos_model_scenarios_as_verified_glorys_or_EN4":True}
    (out/"595_physical_extraction_validation.json").write_text(json.dumps(report,indent=2)+"\n")
    print("PASS_SOURCE_PINNED_595_CMIP6_PHYSICAL_ONLY="+json.dumps(report))
if __name__=="__main__":main()
