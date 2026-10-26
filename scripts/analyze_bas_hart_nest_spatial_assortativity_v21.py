#!/usr/bin/env python3
"""V21 fixed 10m original Hart individual nest label-assortativity descriptor.

Actual first-party BAS source nest coordinates in validated V20 NPZ; 4
localities nested in only 3 provisional named islands. 199 within-locality
exchangeable-label controls, NOT evidence of direct interspecific competition.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from validate_bas_hart_original_multiisland_nest_points_v20 import (
    LOCALITIES,SPECIES,SITE_GAZETTEER_PARENT,SOURCE_SPECIES_TO_CODE
)

FROZEN_SEED=20261026
N_RANDOM_LABELS=199
PRIMARY_NN_RADIUS_M=10.
SECONDARY_RADII_M=(5.,20.)
MIN_PER_SPECIES=100
MIN_PRIMARY_NN=1000
DUPLICATE_FAILURE_FRACTION=.1


def locality_nearest_species_assortativity(xy,labels,seed,replicates=N_RANDOM_LABELS):
    n=len(xy)
    if n!=len(labels) or n<MIN_PRIMARY_NN:
        return {"status":"STOP_ORIGINAL_NEST_POINT_SAMPLE_TOO_SMALL","source_nest_point_n":n}
    if not np.isfinite(xy).all() or xy.shape!=(n,2) or len(labels.shape)!=1:
        raise ValueError("GEOMETRY_STOP invalid source-projected UTM nest point array")
    labels=np.asarray(labels,dtype=np.uint8)
    if not np.isin(labels,range(len(SPECIES))).all():
        raise ValueError("SCHEMA_STOP unexpected original source species label")
    unique,reverse,count=np.unique(xy,axis=0,return_inverse=True,return_counts=True)
    usable=count[reverse]==1
    discarded=int(np.count_nonzero(~usable))
    if discarded/n>=DUPLICATE_FAILURE_FRACTION:
        return {"status":"STOP_EXCESSIVE_EXACT_COORDINATE_COLLISIONS",
                "original_source_point_n":n,
                "exact_coordinate_collision_records":discarded,
                "fraction_excluded_duplicate_coordinates":discarded/n,
                "ecological_effect_fitted":False}
    xy=xy[usable]
    labels=labels[usable]
    # Canonical spatial order to avoid source file/species order affecting
    # numerical nearest-neighbor tie selection.
    spatial_order=np.lexsort((xy[:,1],xy[:,0]))
    xy,labels=xy[spatial_order],labels[spatial_order]
    n_unique=len(xy)
    source_count={SPECIES[i]:int(np.count_nonzero(labels==i)) for i in range(len(SPECIES))}
    available={name:v for name,v in source_count.items() if v>=MIN_PER_SPECIES}
    if len(available)<2:
        return {"status":"STOP_FEWER_THAN_TWO_SAMPLED_SPECIES","source_points_after_duplicate_exclusion":n_unique,
                "source_species_point_counts":source_count,"ecological_effect_fitted":False}
    # V20 source cohort is frozen at two or four original species. Do not
    # selectively drop rare confirmed species to enhance association.
    if any(0<v<MIN_PER_SPECIES for v in source_count.values()):
        return {"status":"STOP_ANY_SOURCE_TAXON_TOO_SMALL_FOR_FROZEN_COHORT",
                "source_species_point_counts":source_count,"ecological_effect_fitted":False}
    kdt=cKDTree(xy)
    d,nearest=kdt.query(xy,k=2)
    neighbour_distance=d[:,1]
    neighbour_index=nearest[:,1]
    if not np.isfinite(neighbour_distance).all() or np.any(neighbour_distance<=0):
        raise ValueError("GEOMETRY_STOP duplicate nest centres survived source collision exclusion")
    eligible=neighbour_distance<=PRIMARY_NN_RADIUS_M
    n_eligible=int(np.sum(eligible))
    if n_eligible<MIN_PRIMARY_NN:
        return {"status":"STOP_FEWER_THAN_1000_LOCAL_10M_NN_PAIRS",
                "n_eligible_nearest_neighbor_nests":n_eligible,
                "source_species_point_counts":source_count,"ecological_effect_fitted":False}
    source_het=(labels[eligible]!=labels[neighbour_index[eligible]])
    observed=float(np.mean(source_het))
    # Analytical combinatorial expected heterospecific pair rate when all
    # original labels are freely exchangeable over the source point cloud.
    freq=np.bincount(labels,minlength=len(SPECIES))
    analytic_null=1-float(np.dot(freq,freq-1))/(n_unique*(n_unique-1))
    rng=np.random.default_rng(seed)
    controls=np.empty(replicates,dtype=float)
    for it in range(replicates):
        shuffle=rng.permutation(labels)
        controls[it]=np.mean(shuffle[eligible]!=shuffle[neighbour_index[eligible]])
    q=np.percentile(controls,[10,50,90])
    secondary={}
    for r in SECONDARY_RADII_M:
        mask=neighbour_distance<=r
        secondary[f"heterospecific_nearest_neighbor_fraction_within_{int(r)}m"]={
            "eligible_original_nest_coordinates":int(np.sum(mask)),
            "observed_heterospecific_fraction":float(
                np.mean(labels[mask]!=labels[neighbour_index[mask]])) if np.any(mask) else None
        }
    return {
        "status":"BAS_NEST_NN_10M_FIXED_NULL_GEOMETRY_EXPLORATORY",
        "source_original_nest_records":n,
        "source_nests_excluded_due_exact_coordinate_tie":discarded,
        "source_nests_fraction_excluded_due_coordinate_tie":discarded/n,
        "source_nests_with_distinct_UTM_positions":n_unique,
        "source_species_point_count_after_duplicate_exclusion":source_count,
        "source_taxon_richness_observed":len(available),
        "nearest_neighbor_distance_m":{"median":float(np.median(neighbour_distance)),
                                        "p10":float(np.percentile(neighbour_distance,10)),
                                        "p90":float(np.percentile(neighbour_distance,90))},
        "primary_local_10m_nests_with_nearest_neighbor_n":n_eligible,
        "primary_local_10m_fraction_of_unique_nests":n_eligible/n_unique,
        "observed_heterospecific_nearest_nest_fraction_10m":observed,
        "permutation_199_heterospecific_nearest_nest_fraction_null":{
            "n_randomizations":replicates,"seed":seed,
            "mean":float(np.mean(controls)),
            "median":float(q[1]),
            "p10":float(q[0]),
            "p90":float(q[2]),
            "original_observed_percentile_among_random_labels":float(np.mean(controls<=observed)),
            "random_label_controls_with_heterospecific_fraction_le_observed":int(np.sum(controls<=observed)),
        },
        "simple_analytical_exchangeable_species_label_expected_heterospecific_fraction":analytic_null,
        "positive_conspecific_enrichment_delta_nullminusobserved":float(q[1]-observed),
        "secondary_fixed_radius_descriptors":secondary,
        "taxon_label_randomization_preserves_local_habitat_selection":False,
        "ecological_island_movement_or_interspecific_competition_causally_identified":False,
        "statistical_independent_observation_units_are_original_individual_nests":False,
        "calibrated_common_UAV_coverage_area_verified":False,
    }


def analyze_all_point_sources(v20:dict,arrays:dict):
    if v20["status"]!="BAS_HART_ORIGINAL_10_SPECIES_NEST_CSV_SOURCE_V20":
        raise ValueError("SOURCE_STOP original 10-file V20 data not successfully audited")
    sample={}
    for i,locality in enumerate(LOCALITIES):
        xy=np.asarray(arrays[f"{locality}_xy"],dtype=np.float64)
        lbl=np.asarray(arrays[f"{locality}_label"],dtype=np.uint8)
        if len(xy)!=sum(x["original_row_count"] for x in v20["source_species_original_file_validation"]
                        if x["source_original_locality"]==locality):
            raise ValueError("SOURCE_STOP original source sample and V20 point-set row totals differ")
        m=locality_nearest_species_assortativity(xy,lbl,FROZEN_SEED+i+1)
        sample[locality]={"candidate_physical_island":SITE_GAZETTEER_PARENT[locality],**m}
    effects={k:v["positive_conspecific_enrichment_delta_nullminusobserved"]
             for k,v in sample.items()
             if v["status"]=="BAS_NEST_NN_10M_FIXED_NULL_GEOMETRY_EXPLORATORY"}
    island_effect={}
    for place in sorted(set(SITE_GAZETTEER_PARENT.values())):
        values=[effects[k] for k in effects
                if SITE_GAZETTEER_PARENT[k]==place]
        if values:island_effect[place]=float(np.mean(values))
    return {
       "status":"BAS_HART_ORIGINAL_MULTIISLAND_INDIVIDUAL_NEST_SPATIAL_GEOMETRY_V21",
       "original_source_locality_cohort":list(LOCALITIES),
       "original_source_locality_count":len(LOCALITIES),
       "original_source_CSV_frozen_n":10,
       "source_locality_to_gazetteer_candidate_island":SITE_GAZETTEER_PARENT,
       "original_successful_localities":len(effects),
       "original_failed_source_locality_gates":{
           k:v["status"] for k,v in sample.items()
           if v["status"]!="BAS_NEST_NN_10M_FIXED_NULL_GEOMETRY_EXPLORATORY"},
       "source_observed_nearest_nest_10m_by_locality":sample,
       "source_locality_equal_weight_mean_conspecific_enrichment_delta":
           float(np.mean(list(effects.values()))) if effects else None,
       "candidate_island_equal_weight_mean_conspecific_enrichment_delta":{
           "n_provisional_independent_named_islands":len(island_effect),
           "island_site_mean_values":island_effect,
           "mean":float(np.mean(list(island_effect.values()))) if island_effect else None},
       "original_locality_count_not_number_of_independent_islands":True,
       "original_2019_2020_campaign_not_verified_same_acquisition_day":True,
       "same_source_image_species_COOBSERVATION_METHOD_COMPARABLE":False,
       "species_habitat_partition_or_interspecific_competition_demonstrated":False,
       "source_species_imputed_unknown_or_ZAVO_2022_points_opened":False,
       "survey_geometry_coverage_footprints_independently_verified":False,
       "general_Antarctic_island_biogeography_law_confirmed":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v20",type=Path,required=True)
    ap.add_argument("--points",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    report={"status":"HOLD_BAS_HART_POINT_CLOUD_SPATIAL_V21"}
    try:
        source=json.loads(args.v20.read_text(encoding="utf-8"))
        digest=hashlib.sha256(args.points.read_bytes()).hexdigest()
        if digest!=source["derived_source_geography_NPZ_SHA256"]:
            raise ValueError("SOURCE_STOP original V20 source-calibrated nest NPZ SHA drift")
        with np.load(args.points,allow_pickle=False) as archive:
            orig={key:archive[key] for key in archive.files}
        if sorted(orig)!=sorted(source["derived_nest_points_NPZ_array_keys"]):
            raise ValueError("SOURCE_STOP V20 expected four original site species coordinate arrays changed")
        report=analyze_all_point_sources(source,orig)
        report["original_V20_nest_point_artifact_SHA256"]=digest
        report["original_V20_source_nest_CSV_SHA_receipts"]={
            x["source_original_file_path"]:x["source_original_raw_CSV_sha256"]
            for x in source["source_species_original_file_validation"]}
    except Exception as e:
        report["error_type"]=type(e).__name__
        report["error"]=str(e)[:1400]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
    if report["status"].startswith("HOLD"):raise SystemExit(2)


if __name__=="__main__":
    main()
