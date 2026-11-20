#!/usr/bin/env python3
"""Original 88 Antarctic sites × external 2009–21 VHR verified guano-area ground observations.

SOURCE-ONLY: no 2013+ L8 δ15N, no new image reflectance, no penguin diet or
polynya association. Independently pins Strang et al 2025 VHR published data
and checks exact colony IDs vs original frozen 88. CROZ/BIRD are aggregate colony
groups, NOT exact CRZW/CRZE or multiple BRD site IDs and must never be assigned.
An external VHR *area* is NOT a pixel-level mask, so it cannot validate Landsat
guano-vs-rock classifier sensitivity or specificity.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path
import pandas as pd
import numpy as np

ORIGINAL88_SOURCE_ZIP_SHA256="702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96"
STRANG_GITHUB_TREE_COMMIT="759935d0a16f731af44d568ec47f686f6fb050e4"
STRANG_GIT_BLOB_SHA="d279d3f0d1cbcce6c027d0457ce685d0d8bf378d"
EXTERNAL_VHR="https://github.com/AlexandraStrang/ADPE_Remote_Sensing/blob/"+STRANG_GITHUB_TREE_COMMIT+"/Data/ADPE_guano_area_trends.csv"
SOURCE_NAME="source_original_88_site_polynya_25km_100km_native_grid_geography.csv"
CVPR2019_GITHUB_SOURCE_COMMIT="b2b5a61a32137c250d1f26fd6bdb6c8ea03babef"

def get_original88(path):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=ORIGINAL88_SOURCE_ZIP_SHA256:
        raise ValueError("Original native site-only geography ZIP source checksum changed")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        if z.testzip():raise ValueError("Original 88 source geography archive CRC failure")
        names=[n for n in z.namelist() if n==SOURCE_NAME or n.endswith("/"+SOURCE_NAME)]
        if len(names)!=1:raise ValueError("Missing true colony source geography")
        t=pd.read_csv(io.BytesIO(z.read(names[0])),low_memory=False)
    orig=t.loc[t.radius_km.eq(100)].copy()
    orig.site_id=orig.site_id.astype(str)
    if (len(orig),orig.site_id.nunique(),orig.source_region.nunique())!=(88,88,13):
        raise ValueError("Original 88/13 source geography population drift")
    return orig

def git_blob_sha(b):
    h=hashlib.sha1()
    h.update(f"blob {len(b)}\0".encode())
    h.update(b)
    return h.hexdigest()

def get_external_vhr(path):
    raw=Path(path).read_bytes()
    if git_blob_sha(raw)!=STRANG_GIT_BLOB_SHA:
        raise ValueError(f"External independently published Strang VHR CSV Git object SHA mismatch: {git_blob_sha(raw)}")
    d=pd.read_csv(io.BytesIO(raw),encoding="utf-8-sig",low_memory=False)
    cols={"Colony","Colony_code","Season","Date","Guano_area"}
    if not cols.issubset(d.columns):raise ValueError("External VHR schema changed")
    d.Colony_code=d.Colony_code.astype(str)
    d.Season=pd.to_numeric(d.Season,errors="raise").astype(int)
    d.Guano_area=pd.to_numeric(d.Guano_area,errors="raise")
    if (d.Guano_area<=0).any() or not np.isfinite(d.Guano_area).all():
        raise ValueError("External VHR true documented observed guano area invalid")
    if d.duplicated(["Colony_code","Season"]).any():
        raise ValueError("External site×source season duplicated; no silent averaging")
    if not d.Season.between(2009,2021).all():
        raise ValueError("External VHR actual observation year outside publication")
    if set(d.Colony_code)!={"CROZ","BIRD","ROYD","INEX"}:
        raise ValueError("External VHR site codes diverged from 4 known source sites")
    return d

def main(a):
    orig=get_original88(a.original88_geography_zip)
    d=get_external_vhr(a.external_strang_vhr_csv)
    common=set(orig.site_id)&set(d.Colony_code)
    geo=orig[["site_id","source_region","colony_lon","colony_lat"]].rename(columns={"site_id":"Colony_code"})
    matched=d.merge(geo,on="Colony_code",how="inner",validate="many_to_one")
    if set(matched.Colony_code)!=common:
        raise ValueError("Exact site ID support matching changed")
    holdout=matched.loc[matched.Season.between(2013,2021)].copy()
    if holdout.empty: raise ValueError("No independently published 2013–2021 matched source VHR coverage")
    group=holdout.groupby(["Colony_code","source_region"],as_index=False).agg(
       n_actual_VHR_seasons=("Season","nunique"),
       first_year=("Season","min"),last_year=("Season","max"),
       min_measured_guano_area_m2=("Guano_area","min"),
       max_measured_guano_area_m2=("Guano_area","max"),
       median_measured_guano_area_m2=("Guano_area","median"),
       sample_area_CV=("Guano_area",lambda x:float(x.std(ddof=1)/x.mean()) if len(x)>1 else np.nan),
    )
    group["ratio_max_to_min_VHR_guano_area"]=group.max_measured_guano_area_m2/group.min_measured_guano_area_m2
    notjoined=sorted(set(d.Colony_code)-common)
    observed_years=sorted(holdout.Season.astype(int).unique())
    # 2019 weakly annotated high-res dataset published 31 hand-labels,
    # but its public GitHub source tree is only 61 source files, no exposed
    # georeferenced masks or high-res image ground truth.
    rep={
      "status":"EXTERNAL_VHR_AREA_SOURCE_OVERLAP_VALIDATED_NOT_GUANO_PIXEL_LABELS",
      "original_sites":88,"original_regions":13,
      "same_original_site_code_independent_VHR":sorted(common),
      "same_original_site_code_n":len(common),
      "strict_independent_regions_with_actual_VHR_area":int(holdout.source_region.nunique()),
      "strict_source_years_with_actual_VHR_area":observed_years,
      "strict_source_2013_2021_site_season_area_rows":len(holdout),
      "four_source_colony_groups_not_directly_joinable":notjoined,
      "why_CROZ_BIRD_not_exact":["CROZ is aggregate Cape Crozier, not original CRZW/CRZE code",
         "BIRD is aggregate Cape Bird not individual BRDN/BRDS/BRDM code"],
      "external_VHR_source_ref":EXTERNAL_VHR,"external_VHR_git_blob_sha":STRANG_GIT_BLOB_SHA,
      "external_VHR_independent_area_observations_all4_colonies":len(d),
      "external_VHR_exact_site_source_area_ranges":group.to_dict("records"),
      "external_VHR_area_is_not_pixel_level_true_guano_label":True,
      "published_2019_penguin_colony_hand_mask_dataset_article":"https://arxiv.org/abs/1905.03313",
      "published_2019_source_repo":"https://github.com/lynch-lab/CVPR19-CV4GC-WeaklyLabeling",
      "published_2019_source_repository_pinned_commit":CVPR2019_GITHUB_SOURCE_COMMIT,
      "published_2019_31_masks_not_present_as_pixel_ground_truth_in_source_repository":True,
      "2019_pretrained_model_based_on_1_to_2_4m_commercial_imagery_not_L8_30m":True,
      "2026_Cape_Hallett_UAV_guano_manual_reference_source":"https://doi.org/10.1002/jgo2.70027",
      "2026_Cape_Hallett_UAV_reference_polygon_public_machine_download":"NOT_VERIFIED_OR_PROVIDED_IN_ORIGINAL_PAPER",
      "2026_Cape_Hallett_L8_reference_commission_error":0.59,
      "2026_Cape_Hallett_L8_reference_omission_error":0.21,
      "no_2013_2021_L8_reflectance_opened":True,
      "no_2013_2021_L8_optical_isotope_proxy_constructed":True,
      "no_2013_2021_polynya_isotope_association_tested":True,
      "source_gate_for_pixel_classifier_external_multiregion_truth":"NO_GO_TRUE_POSITIVE_AND_NEGATIVE_GUANO_PIXEL_LABELS_NOT_OPENLY_VERIFIED",
      "no_false_transfer_from_only_one_original_geographic_region":True,
    }
    a.out.mkdir(parents=True,exist_ok=True)
    matched.to_csv(a.out/"independent_original_VHR_only_exact_original_site_id_full_records.csv",index=False)
    holdout.to_csv(a.out/"independent_2013_2021_VHR_only_strict_original_site_years.csv",index=False)
    group.to_csv(a.out/"independent_2013_2021_VHR_exact_original_site_temporal_support.csv",index=False)
    (a.out/"EXTERNAL_GUANO_VHR_SITE_AREA_NOT_PIXEL_CLASSIFIER_GATE.json").write_text(
       json.dumps(rep,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(rep,indent=2,ensure_ascii=False),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original88-geography-zip",type=Path,required=True)
    p.add_argument("--external-strang-vhr-csv",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
