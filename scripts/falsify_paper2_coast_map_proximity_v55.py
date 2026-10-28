#!/usr/bin/env python3
"""V55 after V54 observation: strict original land and 30m cell density falsifications.

All 2019–20 source birds in this source are penguins. A GIS-independent-of-
taxon coastline-map proximity source variable improved 3/3 source-island
Adelie/Chinstrap classification, but original Hewison coastline includes
99.8% Adelie versus 73.6% Chinstrap (source artefact risk). Refit both B1
and B2 on land-only source and on land-only equal-occupied-30m-cell weights.
This post-result sensitivity is NOT a flight/mammal/island causality finding.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
from shapely import contains_xy
from sklearn.linear_model import LogisticRegression

import analyze_paper2_three_island_penguin_coast_access_v51 as v51
import analyze_paper2_penguin_official_coast_map_proximity_v54 as v54

EXPECTED_V54_GAIN=0.051613243579301644
GRID=30.
MIN_CELLS_CLASS_SITE=20
MIN_SOURCE_NESTS_CLASS_SITE=100
MIN_POSITIVE_SOURCE_ISLANDS=2
MIN_EQUAL_ISLAND_GAIN=.005


def original_land_and_source_coast(source,coast,full_measures):
    seen={}
    counts={}
    for site in v51.ORIGINAL_LOCALITIES:
        raw=source[site]
        poly=coast[v51.PARENT[site]]
        inside=contains_xy(poly,raw["xy"][:,0],raw["xy"][:,1])
        # Original V52 all-source category denominators must not change.
        n,inside_n=v54.SOURCE_SAMPLE_COUNTS[site]
        if len(inside)!=n or inside.sum()!=inside_n:
            raise ValueError("V55_ORIGINAL_V52_SOURCE_MAPPED_COAST_ONSHORE_COUNT_CHANGED:"+site)
        keep=full_measures[site]["keep"] & inside
        original_counts=Counter(raw["label"][keep].tolist())
        if any(original_counts[code]<MIN_SOURCE_NESTS_CLASS_SITE for code in (0,1)):
            raise ValueError("V55_ORIGINAL_SOURCE_LAND_ONLY_TAXON_SAMPLE_LT100:"+site)
        seen[site]={
          "D_coast":full_measures[site]["D_coast"],
          "keep":keep,
          "original_source_inside":inside,
        }
        counts[site]={
          "original_land_only_nest_coordinates_total":int(keep.sum()),
          "original_all_taxa_source_2020_land_inside":int(inside.sum()),
          "original_Adelie_source_inside_and_DEM_qualified":int(original_counts[0]),
          "original_Chinstrap_source_inside_and_DEM_qualified":int(original_counts[1]),
          "2020_original_offpolygon_points_never_snap_to_land":True,
        }
    return seen,counts


def source_taxon_cell_inverse(utm_xy,source_y):
    """One sampled nest = 1 / same species x same fixed original 30m cell size."""
    xy=np.asarray(utm_xy)
    y=np.asarray(source_y)
    if xy.ndim!=2 or xy.shape[1]!=2 or len(xy)!=len(y):
        raise ValueError("V55_ORIGINAL_UTM_SOURCE_CELL_ARRAY_MISSHAPED")
    tile=np.floor(xy/GRID).astype(np.int64)
    # The key contains source taxon and fixed origin-aligned 30m cell coordinates.
    key=np.column_stack([y.astype(np.int64),tile])
    cell,reverse,frequencies=np.unique(key,axis=0,return_inverse=True,return_counts=True)
    if len(cell)==0 or np.any(frequencies<=0):
        raise ValueError("V55_ORIGINAL_TAXON_CELL_EMPTY")
    inv=1.0/frequencies[reverse]
    sizes={int(code):int(np.sum(cell[:,0]==code)) for code in (0,1)}
    return inv,sizes


def spatial_cell_guild_balanced_brier(y,p,inv):
    y=np.asarray(y)
    p=np.asarray(p,dtype=float)
    inv=np.asarray(inv,dtype=float)
    result=0.
    for code in (0,1):
        sel=(y==code)
        if np.sum(sel)<MIN_SOURCE_NESTS_CLASS_SITE or not np.isfinite(inv[sel]).all():
            raise ValueError("V55_HELDOUT_ORIGINAL_TAXON_CELL_SAMPLE_FAILED")
        sq=(p[sel]-code)**2
        result+=.5*float(np.sum(sq*inv[sel])/np.sum(inv[sel]))
    return result


def prep_land_only_cell_source(source,access):
    info={}
    for site in v51.ORIGINAL_LOCALITIES:
        data=source[site]
        eligible=access[site]["keep"] & np.isin(data["label"],[0,1])
        X=np.column_stack((
            data["elev"][eligible],
            data["slope"][eligible],
            np.log1p(access[site]["D_coast"][eligible])
        ))
        yy=data["label"][eligible]
        if len(yy)<2*MIN_SOURCE_NESTS_CLASS_SITE or not np.isfinite(X).all():
            raise ValueError("V55_SOURCE_LAND_ONLY_GEOGRAPHY_OR_DEM_INVALID")
        inv,cells=source_taxon_cell_inverse(data["xy"][eligible],yy)
        if any(cells[code]<MIN_CELLS_CLASS_SITE for code in (0,1)):
            raise ValueError("V55_SOURCE_LAND_ONLY_30M_CELL_TAXON_SUPPORT_LT20:"+site)
        info[site]={
           "X":X,"y":yy,"inv":inv,"original_taxon_cell_n":cells,
           "original_true_source_island":v51.PARENT[site]
        }
    return info


def original_three_island_cell_equal_holdout(source):
    if set(source)!=set(v51.ORIGINAL_LOCALITIES):
        raise ValueError("V55_ORIGINAL_LOCALITIES_CHANGED")
    held={}
    islands=sorted(set(v51.PARENT.values()))
    for hold in islands:
        train_sites=[k for k in v51.ORIGINAL_LOCALITIES if v51.PARENT[k]!=hold]
        test_sites=[k for k in v51.ORIGINAL_LOCALITIES if v51.PARENT[k]==hold]
        train=np.vstack([source[k]["X"] for k in train_sites])
        labels=np.concatenate([source[k]["y"] for k in train_sites])
        weights=[]
        for site in train_sites:
            yy=source[site]["y"]
            inv=source[site]["inv"]
            nsites=sum(v51.PARENT[k]==v51.PARENT[site] for k in train_sites)
            w=np.zeros(len(yy))
            for code in (0,1):
                mask=(yy==code)
                w[mask]=(.5/nsites/source[site]["original_taxon_cell_n"][code])*inv[mask]
            weights.append(w)
        weights=np.concatenate(weights)
        if np.any(weights<=0) or not np.isclose(
                np.sum(weights),len({v51.PARENT[s] for s in train_sites})):
            raise ValueError("V55_SOURCE_ISLAND_SITE_TAXON_30M_CELL_TRAIN_WEIGHTS_BAD")
        w=weights/np.mean(weights)
        bysite={}
        for n,prefix in ((2,"B1_elevation_slope"),(3,"B2_plus_map_coast_proximity")):
            X_train=train[:,:n]
            mid=np.median(X_train,axis=0)
            q=np.percentile(X_train,[25,75],axis=0)
            scale=np.where(q[1]-q[0]>1e-7,q[1]-q[0],1.)
            Xscaled=(X_train-mid)/scale
            classifier=LogisticRegression(C=v51.FIXED_C,solver="lbfgs",max_iter=500)
            classifier.fit(Xscaled,labels,sample_weight=w)
            for site in test_sites:
                test=source[site]
                y=test["y"]
                Xtest=(test["X"][:,:n]-mid)/scale
                pred=classifier.predict_proba(Xtest)[:,1]
                score=spatial_cell_guild_balanced_brier(y,pred,test["inv"])
                bysite.setdefault(site,{})[prefix]=score
                bysite[site]["original_land_only_occupied_cell_n_by_taxon"]={
                    "Adelie":test["original_taxon_cell_n"][0],
                    "Chinstrap":test["original_taxon_cell_n"][1]
                }
        b1=float(np.mean([q["B1_elevation_slope"] for q in bysite.values()]))
        b2=float(np.mean([q["B2_plus_map_coast_proximity"] for q in bysite.values()]))
        held[hold]={
          "original_heldout_island_name":hold,
          "original_sites_heldout_together":test_sites,
          "original_train_other_physical_islands":sorted({v51.PARENT[s] for s in train_sites}),
          "original_cell_balanced_B1":b1,
          "original_cell_balanced_B2":b2,
          "original_incremental_map_coast_proximity_gain":b1-b2,
          "original_heldout_site_cell_balanced_Brier":bysite
        }
    gains=[v["original_incremental_map_coast_proximity_gain"] for v in held.values()]
    return {
      "original_heldout_independent_physical_islands":3,
      "original_source_land_only_30m_taxon_cells":{
          site:info["original_taxon_cell_n"] for site,info in source.items()
      },
      "original_island_holdout_results":held,
      "original_equal_island_Brier_gain":float(np.mean(gains)),
      "source_islands_with_positive_increment":int(sum(v>0 for v in gains)),
      "V55_30m_cell_balanced_incremental_map_source_gate_pass":bool(
          sum(v>0 for v in gains)>=MIN_POSITIVE_SOURCE_ISLANDS and
          np.mean(gains)>=MIN_EQUAL_ISLAND_GAIN
      ),
      "individual_penguin_nests_not_independent_source_island_replicates":True,
      "original_cells_are_not_verified_vacant_habitat":True,
    }


def model_after_original_source_checks(npz_path:Path):
    data,orig=v51.read_original_npz(npz_path)
    coast,source=v54.original_exact_coastal_geography(data)
    measures,geography=v54.island_coast_map_only(data,coast)
    original=v51.source_heldout_predictive_qa(data,measures)
    if abs(original["island_equal_mean_B1_minus_B2_gain"]-EXPECTED_V54_GAIN)>1e-8:
        raise ValueError("V55_ORIGINAL_V54_OBSERVED_FULL_FRAME_RESULT_DRIFT")
    inside,counts=original_land_and_source_coast(data,coast,measures)
    strictonly=v51.source_heldout_predictive_qa(data,inside)
    cell_input=prep_land_only_cell_source(data,inside)
    spatial=original_three_island_cell_equal_holdout(cell_input)
    original_criterion=strictonly["fixed_coast_increment_at_least_two_islands_and_gain_ge_0p005_pass"]
    cell_criterion=spatial["V55_30m_cell_balanced_incremental_map_source_gate_pass"]
    return {
       "status":"V55_ORIGINAL_THREE_ISLAND_STRICT_LAND_AND_CELL_FALSIFICATION_COMPLETED",
       "original_V54_full_frame_source_equal_island_Brier_gain_unchanged":EXPECTED_V54_GAIN,
       "original_V54_three_source_island_gain_replicated":original["heldout_island_Brier"],
       "actual_original_source_sample_censored_to_strict_2020_land":counts,
       "strict_original_land_only_same_B1_v_B2_heldout_island":strictonly,
       "strict_original_land_only_plus_equal_30m_occupied_species_cells":spatial,
       "V55_both_source_geography_and_original_30m_cell_robustness_PASS":bool(
          original_criterion and cell_criterion),
       "V51_original_strict_95percent_all_original_nests_SOURCE_GATE_still_FAILED":True,
       "original_2019_20_nests_to_2020_map_not_actual_breeder_walking_route":True,
       "no_mammalian_predator_or_flying_seabird_interaction_estimated":True,
       "exploratory_post_V54_geographic_and_sampling_bias_falsification":True,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v26-npz",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    a=ap.parse_args()
    report={
      "status":"V55_SOURCE_OR_MODEL_FALSIFICATION_HOLD",
      "date":"2026-10-28",
      "contract":"contracts/PAPER2_V55_COAST_MAP_STRICT_LAND_AND_30M_CELL_FALSIFICATION.md",
      "original_official_BAS_2020_coast_SHA256":v54.SHA,
      "no_mammal_or_flying_bird_biological_outcome_fitted":True,
    }
    try:
        report.update(model_after_original_source_checks(a.v26_npz))
    except Exception as e:
        report["status"]="V55_SOURCE_OR_MODEL_FALSIFICATION_HOLD"
        report["error"]=type(e).__name__+": "+str(e)[:900]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    atlas=report.get("strict_original_land_only_same_B1_v_B2_heldout_island",{})
    grid=report.get("strict_original_land_only_plus_equal_30m_occupied_species_cells",{})
    print(json.dumps({
      "status":report["status"],
      "V54_original_source_gain":report.get("original_V54_full_frame_source_equal_island_Brier_gain_unchanged"),
      "V55_A_source_land_only_equal_island_gain":atlas.get("island_equal_mean_B1_minus_B2_gain"),
      "V55_A_source_land_only_islands_improved":atlas.get("original_3_island_groups_with_positive_access_gain"),
      "V55_A_source_land_only_folds":atlas.get("heldout_island_Brier"),
      "V55_B_strict_land_30m_species_cells_island_equal_gain":grid.get("original_equal_island_Brier_gain"),
      "V55_B_strict_land_cell_species_gains":grid.get("original_island_holdout_results"),
      "V55_B_source_cells_by_site":grid.get("original_source_land_only_30m_taxon_cells"),
      "both_robust":report.get("V55_both_source_geography_and_original_30m_cell_robustness_PASS"),
      "error":report.get("error"),
    },ensure_ascii=False))
    if report["status"]=="V55_SOURCE_OR_MODEL_FALSIFICATION_HOLD":
        raise SystemExit(2)


if __name__=="__main__":
    main()
