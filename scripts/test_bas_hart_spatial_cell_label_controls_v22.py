#!/usr/bin/env python3
"""V22 post-V21 within-geographic-cell label null for original SSI nests.

Preserves observed nest coordinates and species counts in 25/100/500m grids.
Identifies whether original near-zero heterospecific NN rate is mostly
inter-patch rather than within-patch species segregation. NOT competition.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from validate_bas_hart_original_multiisland_nest_points_v20 import (
    LOCALITIES, SITE_GAZETTEER_PARENT
)

FROZEN_SCALING=[(25.,(0.,0.)),(100.,(0.,0.)),
               (100.,(50.,0.)),(100.,(0.,50.)),(100.,(50.,50.)),
               (500.,(0.,0.))]
NUM_SHUFFLES=99
V21_EXPECTED_STATUS="BAS_HART_ORIGINAL_MULTIISLAND_INDIVIDUAL_NEST_SPATIAL_GEOMETRY_V21"
DUPLICATE_FAILURE_FRAC=.1
PRIMARY_MAX_NEIGHBOR_M=10.
MIXED_GRID_MIN_ELIGIBLE_FRAC=.05
SOURCE_SEED=20261026


def recover_primary_point_neighbors(xy,labels):
    if xy.ndim!=2 or xy.shape[1]!=2 or labels.ndim!=1 or len(xy)!=len(labels):
        raise ValueError("SCHEMA_STOP original UTM nest dimensions differ")
    if not np.isfinite(xy).all():raise ValueError("GEOMETRY_STOP nonfinite source")
    _,reverse,count=np.unique(xy,axis=0,return_inverse=True,return_counts=True)
    keep=count[reverse]==1
    if np.mean(~keep)>=DUPLICATE_FAILURE_FRAC:
        raise ValueError("GEOMETRY_STOP excess original exact nest coordinate ties")
    xy=xy[keep]
    labels=labels[keep]
    order=np.lexsort((xy[:,1],xy[:,0]))
    xy,labels=xy[order],labels[order]
    dist,nn=cKDTree(xy).query(xy,k=2)
    if not np.all(np.isfinite(dist)) or not np.all(dist[:,1]>0):
        raise ValueError("GEOMETRY_STOP duplicate original nest positions survive exclusion")
    active=dist[:,1]<=PRIMARY_MAX_NEIGHBOR_M
    return xy,labels,nn[:,1],active


def per_source_geo_null(xy,labels,nearest,eligible,cell_width,shift,seed,nsim=NUM_SHUFFLES):
    if cell_width not in (25.,100.,500.):
        raise ValueError("SOURCE_STOP not a frozen post-V21 geographical grid width")
    if len(xy)!=len(labels) or len(xy)!=len(nearest) or len(xy)!=len(eligible):
        raise ValueError("SCHEMA_STOP original V21 site point arrays mismatch")
    offsets=np.asarray(shift,dtype=float)
    cells=np.floor((xy-offsets)/cell_width).astype(np.int64)
    # Unique shape 2: use inverse cell id, avoiding risky 64-bit hash mixing.
    unique,cell_id,cell_n=np.unique(cells,axis=0,return_inverse=True,return_counts=True)
    cell_sorted=np.argsort(cell_id,kind="stable")
    cuts=np.r_[0,np.cumsum(cell_n)]
    multi_groups=[]
    species_mixed=np.zeros(len(cell_n),dtype=bool)
    for j in range(len(cell_n)):
        if cell_n[j]<=1:continue
        indices=cell_sorted[cuts[j]:cuts[j+1]]
        if np.unique(labels[indices]).size>=2:
            multi_groups.append(indices)
            species_mixed[j]=True
    mixed=species_mixed[cell_id]
    mixed_eligible=int(np.count_nonzero(mixed&eligible))
    original_eligible=int(np.count_nonzero(eligible))
    if not original_eligible:
        raise ValueError("SAMPLE_STOP no original local within-10m nearest neighbors")
    effective_fraction=mixed_eligible/original_eligible
    observed=float(np.mean(labels[eligible]!=labels[nearest[eligible]]))
    rng=np.random.default_rng(seed)
    controls=np.empty(nsim,dtype=float)
    changed_permutation=np.empty(nsim,dtype=float)
    for j in range(nsim):
        permuted=labels.copy()
        for indices in multi_groups:
            permuted[indices]=rng.permutation(labels[indices])
        controls[j]=float(np.mean(permuted[eligible]!=permuted[nearest[eligible]]))
        changed_permutation[j]=float(np.mean(permuted[eligible]!=labels[eligible]))
    q=np.percentile(controls,[10,50,90])
    return {
        "status":"CELL_CONDITIONAL_LABEL_NULL_REPORTABLE" if effective_fraction>=MIXED_GRID_MIN_ELIGIBLE_FRAC
                 else "GEOGRAPHIC_MIXED_PATCH_SUPPORT_HOLD",
        "frozen_cell_width_m":cell_width,
        "frozen_cell_phase_shift_m":list(map(float,shift)),
        "original_geographic_grid_cell_n":len(cell_n),
        "mixed_species_source_grid_cell_n":len(multi_groups),
        "original_nests_in_mixed_species_grid_cells":int(np.sum(mixed)),
        "original_eligible_NN_source_nests_in_mixed_source_cells":mixed_eligible,
        "fraction_original_NN_eligible_source_nests_in_mixed_species_grid_cells":effective_fraction,
        "original_observed_heterospecific_NN_fraction":observed,
        "within_cell_exchangeable_species_label_null":{
           "n_permutations":nsim,
           "seed":seed,
           "median":float(q[1]),"p10":float(q[0]),"p90":float(q[2]),
           "mean":float(np.mean(controls)),
           "null_runs_with_heterospecific_fraction_le_observed":int(np.sum(controls<=observed)),
           "median_source_nearest_nests_with_labels_actually_changed":float(np.median(changed_permutation)),
        },
        "source_within_cell_local_segregation_delta_nullminusobserved":float(q[1]-observed),
        "underpowered_source_cell_mixing_not_proof_no_competition":effective_fraction<MIXED_GRID_MIN_ELIGIBLE_FRAC,
        "source_spatial_habitat_classes_kept_constant":False,
        "source_original_nests_are_independent_island_replicates":False
    }


def analyze_original_groups(v20,originalv21,arrays):
    if v20["status"]!="BAS_HART_ORIGINAL_10_SPECIES_NEST_CSV_SOURCE_V20":
        raise ValueError("SOURCE_STOP V20 actual original nested per-species CSV sources missing")
    if originalv21["status"]!=V21_EXPECTED_STATUS:
        raise ValueError("SOURCE_STOP V21 fixed 10m original location outcome receipt missing")
    groups={}
    for i,site in enumerate(LOCALITIES):
        xy=np.asarray(arrays[site+"_xy"],dtype=np.float64)
        labels=np.asarray(arrays[site+"_label"],dtype=np.uint8)
        points,lab,nearest,eligible=recover_primary_point_neighbors(xy,labels)
        v21=originalv21["source_observed_nearest_nest_10m_by_locality"][site]
        obs=float(np.mean(lab[eligible]!=lab[nearest[eligible]]))
        if abs(obs-v21["observed_heterospecific_nearest_nest_fraction_10m"])>1e-10:
            raise ValueError("REPLAY_STOP 10m spatial nearest-neighbor V21 source value changed")
        if np.count_nonzero(eligible)!=v21["primary_local_10m_nests_with_nearest_neighbor_n"]:
            raise ValueError("REPLAY_STOP source nearest-neighbor denominator changed")
        modes={}
        for scale_index,(width,phase) in enumerate(FROZEN_SCALING):
            key=f"{int(width)}m_shift_{int(phase[0])}_{int(phase[1])}"
            modes[key]=per_source_geo_null(
                points,lab,nearest,eligible,width,phase,
                SOURCE_SEED+(i+1)*10000+(scale_index+1)*100+(scale_index%4))
        groups[site]={
          "candidate_parent_named_island":SITE_GAZETTEER_PARENT[site],
          "original_source_geo_nest_rows":len(xy),
          "original_nests_after_exact_coordinate_duplicate_exclusions":len(points),
          "original_primary_10m_observed_heterospecific_fraction_replayed":obs,
          "grid_conditional_null_by_scale_and_shift":modes
        }
    primary=[groups[k]["grid_conditional_null_by_scale_and_shift"]["100m_shift_0_0"]
             for k in LOCALITIES]
    supported=[z for z in primary if z["status"]=="CELL_CONDITIONAL_LABEL_NULL_REPORTABLE"]
    return {
      "status":"BAS_HART_MULTIISLAND_NEST_SPECIES_PATCH_PARTITION_V22_POST_RESULT",
      "original_observation_localities_n":len(LOCALITIES),
      "original_candidate_physical_islands_n":len(set(SITE_GAZETTEER_PARENT.values())),
      "source_original_P_A_or_nonreported_recoded_to_absence":False,
      "source_primary_spatial_null_100m_sufficient_mixed_patch_support_localities":len(supported),
      "source_primary_spatial_null_100m_insufficient_mixed_patch_support_localities":{
        k:groups[k]["grid_conditional_null_by_scale_and_shift"]["100m_shift_0_0"]["fraction_original_NN_eligible_source_nests_in_mixed_species_grid_cells"]
        for k in LOCALITIES
        if groups[k]["grid_conditional_null_by_scale_and_shift"]["100m_shift_0_0"]["status"]!="CELL_CONDITIONAL_LABEL_NULL_REPORTABLE"
      },
      "source_locality_spatial_patch_tests":groups,
      "post_V21_label_geometry_interaction_inference_is_causal":False,
      "source_all_fully_separate_single_species_patch_can_be_used_to_test_direct_competition":False,
      "original_flightless_penguin_colony_point_cloud_not_4_independent_geographical_islands":True,
      "source_survey_footprint_continuity_and_independently_suitable_substrate_verified":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--v20",type=Path,required=True)
    p.add_argument("--v21",type=Path,required=True)
    p.add_argument("--original-points",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report={"status":"HOLD_BAS_HART_SPATIAL_PATCH_V22"}
    try:
        v20=json.loads(a.v20.read_text(encoding="utf-8"))
        v21=json.loads(a.v21.read_text(encoding="utf-8"))
        if hashlib.sha256(a.original_points.read_bytes()).hexdigest()!=v20["derived_source_geography_NPZ_SHA256"]:
            raise ValueError("SOURCE_STOP V20 source original coordinate point cache SHA drift")
        with np.load(a.original_points,allow_pickle=False) as obj:
            original={k:obj[k] for k in obj.files}
        report=analyze_original_groups(v20,v21,original)
        report["original_V20_source_georeferenced_point_cache_SHA256"]=v20["derived_source_geography_NPZ_SHA256"]
        report["original_V21_original_individual_nest_NN_artifact"]=v21.get("execution",{}).get("github_actions_run")
    except Exception as e:
        report["error_type"]=type(e).__name__
        report["error"]=str(e)[:1200]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    if report["status"].startswith("HOLD"):raise SystemExit(2)


if __name__=="__main__":
    main()
