#!/usr/bin/env python3
"""Falsification-grade source-matched PCA geographic cohort and time window
sensitivity of observed Antarctic Pygoscelis two-species nest ratios.

No independent causal warming test. Exact original physical and biological
co-census source panels, with PCA calibrated BEFORE species association.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from test_joint_marine_regime_axis import pca,pearson
from analyze_original_18region_marine_regime_1993_2020 import (
    COLUMNS, OLD_PCA_PC1
)

SOURCE_OLD_ADPE_R=(-0.5079500862836571,0.5231858620924323)
SOURCE_NEW_ADPE_R=(-0.10135101337668344,-0.00836584140622839)
PAIRS=("ADPE__GEPE","CHPE__GEPE","ADPE__CHPE")


def marine_PC1_transformed(df,fit):
    a=df[list(COLUMNS)].to_numpy(dtype=float)
    return (((a-fit["means"])/fit["stds"])@fit["loadings"][:,0])


def source_co_census_correlation(rows):
    if len(rows)<3:return {
        "n_true_same_colony_species_year_pairs":len(rows),
        "n_original_colony_ids":rows.site_id.nunique(),
        "n_original_reporting_regions":rows.source_region.nunique(),
        "n_original_250km_blocks":rows.source_250km_block.nunique(),
        "raw_r":None,"within_site_r":None
    }
    raw=pearson(rows.frozen_projected_PC1,rows.log1p_B_minus_A_observed_nests)
    site_counts=rows.groupby("site_id").size()
    recurring=rows.loc[rows.site_id.isin(site_counts.index[site_counts>=2])].copy()
    if recurring.site_id.nunique()>=3 and len(recurring)>=5:
        xx=recurring.frozen_projected_PC1-recurring.groupby("site_id").frozen_projected_PC1.transform("mean")
        yy=recurring.log1p_B_minus_A_observed_nests-recurring.groupby("site_id").log1p_B_minus_A_observed_nests.transform("mean")
        within=pearson(xx,yy)
    else:within=None
    return {
        "n_true_same_colony_species_year_pairs":len(rows),
        "n_original_colony_ids":rows.site_id.nunique(),
        "n_original_reporting_regions":rows.source_region.nunique(),
        "n_original_250km_blocks":rows.source_250km_block.nunique(),
        "n_original_sites_with_two_or_more_same_species_cocensus_years":recurring.site_id.nunique(),
        "n_true_cocensus_years_contributing_to_within_site_r":len(recurring),
        "raw_r":raw,"within_site_r":within
    }


def diagnostic(args):
    siteyear=pd.read_csv(args.marine_siteyear)
    pairs=pd.read_csv(args.cocensus)
    source=pd.read_csv(args.original40_grid)
    if (len(siteyear)!=588*28 or siteyear.site_id.nunique()!=588 or
        siteyear.source_region.nunique()!=18):
        raise ValueError("The actual complete 588 site×28year continental marine source no longer matches")
    valid=source.loc[(source.cohort=="macro_40")&source.grid_within_25km]
    if len(valid)!=34:raise ValueError("The original 34 source marine sites changed")
    oldsite=set(valid.site_id)
    sub=siteyear.loc[siteyear.site_id.isin(oldsite)&siteyear.year.between(2011,2020)]
    if len(sub)!=340:raise ValueError("The actual original 34×10 sea climate siteyears are not present")
    old=pca(sub[list(COLUMNS)].to_numpy(dtype=float))
    old_error=abs(float(old["explained"][0])-OLD_PCA_PC1)
    if old_error>1e-9:
        raise ValueError("Previous exact original 34site PCA no longer reproduced")
    ry=siteyear.groupby(["source_region","year"],as_index=False)[list(COLUMNS)].mean()
    if len(ry)!=18*28:raise ValueError("Original 18×28 source region climate grid changed")
    new=pca(ry[list(COLUMNS)].to_numpy(dtype=float))
    fits={
        "previous_34sites_2011_2020":old,
        "expanded_equal18regions_1993_2020":new
    }
    for k,fit in fits.items():
        siteyear["score_"+k]=marine_PC1_transformed(siteyear,fit)
    if pairs.duplicated(["site_id","season","species_pair"]).any():
        raise ValueError("Duplicate original same-colony same-year species ratio")
    m=pairs.merge(siteyear[["site_id","year","source_region","source_250km_block",
                            "score_previous_34sites_2011_2020",
                            "score_expanded_equal18regions_1993_2020"]],
                  left_on=["site_id","season"],right_on=["site_id","year"],
                  how="inner",suffixes=("_old_source",""),validate="many_to_one")
    if len(m)!=len(pairs):
        raise ValueError("Not all original two-species source co-census pairs carry physical source")
    if any(m.source_region_old_source!=m.source_region):
        raise ValueError("Original source region co-census and physical source inconsistent")
    if any(m.source_250km_block_old_source!=m.source_250km_block):
        raise ValueError("Original penguin pair polar-block source differs")
    records=[]
    for sp in PAIRS:
        physical=m.loc[m.species_pair==sp]
        for physical_fit,fit in fits.items():
            for group in (
                "previous_34_siteIDs_and_2011_2020_cocensus",
                "all_original_588_siteIDs_2011_2020_cocensus",
                "all_original_588_siteIDs_1993_2020_cocensus"
            ):
                subset=physical.copy()
                if group.startswith("previous_34"):
                    subset=subset.loc[subset.site_id.isin(oldsite)&subset.year.between(2011,2020)]
                elif group.endswith("2011_2020_cocensus"):
                    subset=subset.loc[subset.year.between(2011,2020)]
                subset["frozen_projected_PC1"]=subset["score_"+physical_fit]
                record=source_co_census_correlation(subset)
                record.update({
                    "species_pair":sp,"physical_PC1_calibration":physical_fit,
                    "original_co_census_geographic_period":group,
                    "original_census_absence_never_recoded_as_zero":True,
                    "physical_PCA_refit_to_biological_response":False
                })
                records.append(record)
    df=pd.DataFrame(records)
    keys=[
        ("ADPE__GEPE","previous_34sites_2011_2020",
         "previous_34_siteIDs_and_2011_2020_cocensus",SOURCE_OLD_ADPE_R),
        ("ADPE__GEPE","expanded_equal18regions_1993_2020",
         "all_original_588_siteIDs_1993_2020_cocensus",SOURCE_NEW_ADPE_R)
    ]
    verified={}
    for sp,fit,cohort,ref in keys:
        record=df.loc[(df.species_pair==sp)&
            (df.physical_PC1_calibration==fit)&
            (df.original_co_census_geographic_period==cohort)]
        if len(record)!=1:raise ValueError("Original anchor original biological sample identity missing")
        got=record.iloc[0]
        if abs(float(got.raw_r)-ref[0])>1e-8 or abs(float(got.within_site_r)-ref[1])>1e-8:
            raise ValueError(f"Published original biology marine PCA anchor changed: {sp} {fit} {cohort} "
                             f"{got.raw_r}, {got.within_site_r} != {ref}")
        verified[cohort]={
           "raw_original_r":float(got.raw_r),
           "within_original_site_r":float(got.within_site_r),
           "original_CDR_source_reproduced":True
        }
    result={
        "status":"ORIGINAL_34_VS_588_MARINE_PC1_AND_2011_VS_1993_SPECIES_COCENSUS_FACTORIAL_COMPLETE",
        "original_34site_source_PC1_explained_verified":float(old["explained"][0]),
        "source_34_PC1_max_absolute_deviation_from_original":old_error,
        "original_34_source_first_loading":[float(z) for z in old["loadings"][:,0]],
        "new_equal18_region_28year_PC1_explained":float(new["explained"][0]),
        "new_equal18_region_PC1_first_loading":[float(z) for z in new["loadings"][:,0]],
        "n_real_site_years":len(siteyear),
        "n_original_two_species_real_co_census_record_pairs":len(pairs),
        "original_baseline_34_and_588_biological_r_reproduction":verified,
        "source_factorial_species_by_marine_axis_population_and_time":records,
        "limits":[
            "Changing two simultaneous dimensions (geographic support and physical axis loading) is not independent evidence of a warming effect; this fixed factorial separates source definitions.",
            "Within-site Pearson correlations reuse actual original counted years, not independent ecological block experiments.",
            "Previous 34-site climate axis extrapolated to other Antarctic regions is out-of-domain and only an observational sensitivity.",
            "GLORYS salinity/thetao assimilative reanalysis and OSI SAF source ocean buffers are physical proxies, not penguin foraging niche.",
            "This does not create true regional gentoo population turnover fractions, plant greening timeseries, or future breeding response."
        ]
    }
    args.out.mkdir(parents=True,exist_ok=True)
    df.to_csv(args.out/"frozen_original_species_cocensus_PCA_axis_by_cohort_year_factorial.csv",index=False)
    (args.out/"original34_vs_588_PCA_species_cocensus_2axis_3cohort_verdict.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("SOURCE_34_VS_588_COCENSUS_AXES="+json.dumps(records,ensure_ascii=False),flush=True)
    print("SOURCE_34_VS_588_COCENSUS_PUBLISHED_BENCHMARK="+json.dumps(verified,ensure_ascii=False),flush=True)
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--marine-siteyear",required=True,type=Path)
    ap.add_argument("--cocensus",required=True,type=Path)
    ap.add_argument("--original40-grid",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    diagnostic(ap.parse_args())


if __name__=="__main__":
    main()
