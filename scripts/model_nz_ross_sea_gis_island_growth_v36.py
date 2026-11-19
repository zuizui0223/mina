#!/usr/bin/env python3
"""V36: publisher-source Adélie nested colony growth across four SCAR land polygons.

Frozen islands/annual window/same-colony rosters from V35. No new island or
year selection from original nesting outcome magnitude; no causal inference.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
import math
from pathlib import Path
import random
import statistics
from itertools import combinations
import requests
import audit_nz_ross_sea_census_source_v33 as v33
import audit_nz_ross_sea_island_groups_v34 as v34

V35_RESULTS=Path(__file__).resolve().parents[1]/"results"/"NZ_ROSS_SEA_SCAR_ISLAND_GEO_V35.json"
SOURCE_CENSUS_SHA="23a95d9e693dd095e085534f2c215b79880a72fe9cfb5a59337501192dae03e6"
SOURCE_GEO_SHA="d744e7493f85564f1b634f390a5e4a976b2d5359a6f93cdd9ef345639661b6a6"
SOURCE_GIS_SHA="b0172d698436f871f49339cea5c7155e3d98648360521cc4bbc44a026c0edc38"
POLYGONS={"Ross Island":59,"Beaufort Island":50,"Coulman Island":37,"Inexpressible Island":43}
V35_GROUPS={**POLYGONS,"Possession Island":29}
SOURCE_WINDOWS=tuple(list(range(1983,1993))+[2001,2004,2005])
ISLANDS=tuple(sorted(POLYGONS))
MIN_ISLANDS_WITH_FIVE=3
MIN_COMMON_YEARS=8
MIN_NONZERO_YEAR_WINDOWS=8
MIN_PAIR_R_YEARS=5
PERMUTATIONS=2000
SEED=20261024

def frozen_v35(receipt):
    if receipt.get("status")!="V35_ORIGINAL_NZ_ROSS_SEA_COASTLINE_ISLAND_PANEL_GEOMETRY_QA":
        raise ValueError("SOURCE_STOP V35 original status changed")
    if receipt.get("original_SCAR_ADD_medium_ZIP_SHA256")!=SOURCE_GIS_SHA:
        raise ValueError("SOURCE_STOP V35 independent GIS source changed")
    if (receipt.get("publisher_census_sha256")!=SOURCE_CENSUS_SHA or
        receipt.get("publisher_location_sha256")!=SOURCE_GEO_SHA):
        raise ValueError("SOURCE_STOP V35 public source SHA changed")
    if receipt.get("original_group_to_GIS_landpolygonID")!=V35_GROUPS:
        raise ValueError("SOURCE_STOP V35 fixed unique landpolygon grouping changed")
    support=receipt.get("prespecified_original_GIS_locus_year_support",{})
    if not support.get("source_geography_and_calendar_gate_pass"):
        raise ValueError("SOURCE_STOP original physical named-island support failed")
    if support.get("source_years_with_ge2_named_GIS_island_units")!=list(SOURCE_WINDOWS):
        raise ValueError("SOURCE_STOP original 13 full original year roster changed")
    panel=support.get("source_named_GIS_island_temporal_support",{})
    if set(panel)!=set(V35_GROUPS):
        raise ValueError("SOURCE_STOP original named-island coverage record changed")
    for island in ISLANDS:
        if panel[island]["original_same_colony_adjacent_year_window_count"]<5:
            raise ValueError("SOURCE_STOP one fixed V36 source island below 5 windows")
    return panel,receipt["original_colony_geo_link_records"]

def original_numeric(value):
    """Only source literal numeric values; unknown, bool and negative never zero."""
    if not v33.num_present(value):
        return None
    if isinstance(value,bool) or value is None:
        return None
    try:
        v=float(str(value).strip().replace(",",""))
    except (ValueError,TypeError):
        return None
    return v if math.isfinite(v) and 0<=v<1e10 else None

def source_colony_year_counts(matrix):
    if 0 not in matrix:
        raise ValueError("SCHEMA_STOP publisher census header absent")
    header=matrix[0]
    years={col:v33.parse_year(x) for col,x in header.items()
           if v33.parse_year(x) is not None}
    if len(years)!=44 or sorted(years.values())!=list(v33.YEARS):
        raise ValueError("SOURCE_STOP original 44 year census schema drift")
    if len(years)!=len(set(years.values())):
        raise ValueError("SOURCE_STOP duplicate calendar source year columns")
    items=defaultdict(list)
    for rowi,row in matrix.items():
        if rowi==0:continue
        name=v34.source_record_label(row.get(0))
        if not name:continue
        counts={year:original_numeric(row.get(col)) for col,year in years.items()
                if original_numeric(row.get(col)) is not None}
        items[name].append(counts)
    duplicate={name for name,values in items.items() if len(values)>1}
    good={name:values[0] for name,values in items.items() if len(values)==1}
    return good,{"source_rows_with_colony_name":len(items),
                 "duplicate_source_colony_ids_dropped":sorted(duplicate),
                 "source_colony_source_years":len(years),
                 "original_2020_count_values_present":sum(2020 in counts for counts in good.values()),
                 "2020_missing_survey_not_zero":True}

def exact_source_rosters(panel,counts,geolinks,status_only=False):
    by_island={}
    missing=[]
    for island in ISLANDS:
        by_year={}
        source=panel[island]["original_fixed_source_colonies_by_annual_window"]
        for start,roster in source.items():
            year=int(start)
            for site in roster:
                if (site not in counts or year not in counts[site]
                    or year+1 not in counts[site]):
                    missing.append((island,site,year))
            by_year[year]=tuple(roster)
        by_island[island]=by_year
    if missing:
        raise ValueError("SOURCE_STOP immutable original same-colony census support drift: "+str(len(missing)))
    allowed={}
    for item in geolinks:
        if (item.get("source_named_landmass") in ISLANDS and
            item.get("land_polygon_feature_id")==POLYGONS[item["source_named_landmass"]]
            and item.get("provisional_land_class")=="SEPARATE_LAND_POLYGON_PROXY"):
            allowed[item["original_colony"]]=item
    for island,windows in by_island.items():
        for sites in windows.values():
            for site in sites:
                if site not in allowed or allowed[site]["source_named_landmass"]!=island:
                    raise ValueError("SOURCE_STOP immutable original point-to-landmass join drift")
    source_windows={year:sum(year in m for m in by_island.values()) for year in SOURCE_WINDOWS}
    if any(n<2 for n in source_windows.values()):
        raise ValueError("SOURCE_STOP V35 13 paired-year support changed")
    return by_island,allowed,source_windows

def growth_by_island(annual,counts,exact_only=False):
    output=defaultdict(dict)
    component_counts=defaultdict(dict)
    for island,windows in annual.items():
        for year,roster in windows.items():
            vals=[]
            for site in roster:
                if exact_only and not site[1]:
                    continue
                name=site[0] if isinstance(site,tuple) else site
                before=counts[name][year]
                after=counts[name][year+1]
                vals.append(math.log1p(after)-math.log1p(before))
            if vals:
                output[island][year]=float(statistics.mean(vals))
                component_counts[island][year]=len(vals)
    return dict(output),{k:dict(x) for k,x in component_counts.items()}

def year_balanced_concordance(growth,years=SOURCE_WINDOWS):
    scores={}
    comparable_pairs=0
    same_pairs=0
    for year in years:
        available={isl:series[year] for isl,series in growth.items()
                   if year in series and series[year]!=0}
        if len(available)<2:
            continue
        pairs=list(combinations(sorted(available),2))
        agrees=sum(available[a]*available[b]>0 for a,b in pairs)
        comparable_pairs+=len(pairs)
        same_pairs+=agrees
        scores[year]={"number_islands_with_nonzero_change":len(available),
                      "between_island_pairs":len(pairs),
                      "same_direction_island_pairs":agrees,
                      "year_pair_concordance":agrees/len(pairs)}
    values=[v["year_pair_concordance"] for v in scores.values()]
    return {
        "years_with_two_nonzero_island_changes":len(values),
        "per_year_sign_pairings":{str(y):v for y,v in sorted(scores.items())},
        "observed_year_balanced_agreement":float(statistics.mean(values)) if values else None,
        "original_pair_comparisons":comparable_pairs,
        "original_pair_comparisons_same_sign":same_pairs,
        "pair_weighted_same_direction_fraction":same_pairs/comparable_pairs if comparable_pairs else None,
    }

def null_year_shuffles(growth,years=SOURCE_WINDOWS,iterations=PERMUTATIONS,seed=SEED):
    rng=random.Random(seed)
    source={island:sorted((year,math.copysign(1.,v) if v!=0 else 0.)
                   for year,v in values.items() if year in years)
            for island,values in growth.items()}
    actual=year_balanced_concordance({
        isl:{year:sign for year,sign in vals} for isl,vals in source.items()},years)
    draws=[]
    for _ in range(iterations):
        sim={}
        for isl,vals in source.items():
            ys=[z[0] for z in vals]
            signs=[z[1] for z in vals]
            rng.shuffle(signs)
            sim[isl]={yr:sign for yr,sign in zip(ys,signs)}
        outcome=year_balanced_concordance(sim,years)["observed_year_balanced_agreement"]
        if outcome is not None:draws.append(outcome)
    draws.sort()
    def q(p):
        if not draws:return None
        return draws[max(0,min(len(draws)-1,round((len(draws)-1)*p)))]
    return {
        "source_sign_shuffles":iterations,
        "source_sign_shuffle_seed":seed,
        "null_diagnostic_preserves_island_year_coverage":True,
        "null_not_temporal_autocorrelation_robust_or_an_inferential_p_value":True,
        "valid_shuffles":len(draws),
        "null_year_balanced_agreement_quantiles_05_50_95":[q(.05),q(.5),q(.95)],
        "observed_minus_null_median":(
            actual["observed_year_balanced_agreement"]-q(.5)
            if actual["observed_year_balanced_agreement"] is not None and q(.5) is not None else None),
    }

def pearson(x,y):
    if len(x)<MIN_PAIR_R_YEARS or len(y)!=len(x):
        return None
    xa=statistics.mean(x);ya=statistics.mean(y)
    xx=[v-xa for v in x];yy=[v-ya for v in y]
    den=math.sqrt(sum(v*v for v in xx)*sum(v*v for v in yy))
    if den<=1e-12:return None
    return sum(a*b for a,b in zip(xx,yy))/den

def pair_diagnostics(growth):
    records=[]
    for a,b in combinations(ISLANDS,2):
        years=sorted(set(growth[a])&set(growth[b])&set(SOURCE_WINDOWS))
        rec={"islands":[a,b],"matched_annual_start_years":years,
             "n_source_common_years":len(years),"r_estimated":False}
        if len(years)>=MIN_PAIR_R_YEARS:
            x=[growth[a][yr] for yr in years]
            y=[growth[b][yr] for yr in years]
            r=pearson(x,y)
            loo=[pearson(x[:i]+x[i+1:],y[:i]+y[i+1:]) for i in range(len(x))]
            loo=[v for v in loo if v is not None]
            rec.update({"r_estimated":r is not None,"source_pairwise_growth_pearson_r":r,
                        "leave_one_annual_start_year_out_r_min_max":
                            [min(loo),max(loo)] if loo else None})
        records.append(rec)
    return records

def source_analysis(source_counts,original_v35):
    panel,geolinks=frozen_v35(original_v35)
    roster,geo_sites,_=exact_source_rosters(panel,source_counts,geolinks)
    # Convert source site names to (name, exact_polygon_hit), one per source.
    component_roster={}
    for island,by_year in roster.items():
        component_roster[island]={year:tuple(
            (site,geo_sites[site]["status"]=="EXACT_ONE_LAND_POLYGON")
            for site in names) for year,names in by_year.items()}
    growth,components=growth_by_island(component_roster,source_counts)
    observed=year_balanced_concordance(growth)
    accepted_islands=sum(len(x)>=5 for x in growth.values())
    if (accepted_islands<MIN_ISLANDS_WITH_FIVE or
        observed["years_with_two_nonzero_island_changes"]<MIN_NONZERO_YEAR_WINDOWS or
        sorted(observed["per_year_sign_pairings"],key=int)!=[str(y) for y in SOURCE_WINDOWS]):
        return {"status":"STOP_REAL_NUMERIC_ISLAND_YEAR_SUPPORT",
                "ecological_effect_computed":False,
                "number_islands_with_at_least_five_original_year_change_windows":accepted_islands,
                "source_year_balanced_concordance_coverage":observed}
    shuffled=null_year_shuffles(growth)
    pairwise=pair_diagnostics(growth)
    loo=[year_balanced_concordance(growth,tuple(y for y in SOURCE_WINDOWS if y!=remove))
         ["observed_year_balanced_agreement"] for remove in SOURCE_WINDOWS]
    # Strongly SOURCE-verified point-in-polygon only. This may fail support.
    exact,exact_component=growth_by_island(component_roster,source_counts,exact_only=True)
    exact_eval=year_balanced_concordance(exact)
    exact_good=sum(len(row)>=5 for row in exact.values())
    exact_pass=exact_good>=MIN_ISLANDS_WITH_FIVE and exact_eval["years_with_two_nonzero_island_changes"]>=MIN_COMMON_YEARS
    omit={}
    for drop in ISLANDS:
        other={island:row for island,row in growth.items() if island!=drop}
        support=year_balanced_concordance(other)
        enough=support["years_with_two_nonzero_island_changes"]>=MIN_COMMON_YEARS
        omit[drop]={
            "remaining_source_years_with_two_nonzero_islands":support["years_with_two_nonzero_island_changes"],
            "year_balanced_sign_agreement_if_gate_passes":
                support["observed_year_balanced_agreement"] if enough else None,
            "support_pass_for_leverage_contrast":enough,
        }
    result={
        "status":"V36_ROSS_SEA_GIS_SOURCE_NAMED_ISLAND_GROWTH_CONCORDANCE",
        "ecological_effect_computed":True,
        "source_fixed_independent_land_polygon_groups":POLYGONS,
        "island_group_original_annual_windows_with_one_or_more_matched_colonies":{
            island:len(rows) for island,rows in growth.items()},
        "per_island_matched_colony_count_by_year":{
            island:{str(y):n for y,n in values.items()} for island,values in components.items()},
        "frozen_original_source_two_island_year_starts":list(SOURCE_WINDOWS),
        "primary_cross_island_year_balanced_directional_coherence":observed,
        "independent_island_source_sign_null_diagnostic":shuffled,
        "six_a_priori_fixed_island_pair_growth_correlations":pairwise,
        "leave_one_year_out_primary_directional_agreement_range":[min(loo),max(loo)],
        "GIS_exact_polygon_only_coverage":{
            "n_exact_polygon_only_islands_with_at_least_five_year_windows":exact_good,
            "n_exact_polygon_only_same_year_island_comparisons":
                exact_eval["years_with_two_nonzero_island_changes"],
            "passes_frozen_3island_and_8year_robustness_gate":exact_pass,
            "exact_only_island_year_components":{i:{str(y):v for y,v in x.items()}
                                                   for i,x in exact_component.items()},
            "exact_only_ecological_conclusion":"HOLD" if not exact_pass else "SUPPORTIVE_SENSITIVITY_AVAILABLE"
        },
        "leave_one_island_out_year_balance":omit,
        "sample_era": {
            "primary_early_block_start_years":list(range(1983,1993)),
            "other_observation_start_years":[2001,2004,2005],
            "no_change_point_test_fitted":True,
        },
        "field_method_after_2017_not_assumed_unchanged":True,
        "four_islands_in_one_Ross_Sea_sector_not_four_independent_antarctic_regions":True,
        "source_NZ_colonies_may_overlap_APBP_MAPPPD_population_records":True,
        "water_isolation_or_marine_climate_causal_effect_identified":False,
        "original_absolute_penguin_census_count_values_not_reprinted":True,
        "statistical_p_value_computed":False,
        "scientific_decision":"DESCRIPTIVE_ROSS_SEA_ISLAND_CONCORDANCE_WITH_GEO_AND_EFFORT_LIMITS"
    }
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--json",type=Path,required=True)
    args=ap.parse_args()
    receipt={"status":"HOLD_ORIGINAL_SOURCE","ecological_effect_computed":False}
    try:
        reference=json.loads(V35_RESULTS.read_text(encoding="utf-8"))
        with requests.Session() as session:
            found,meta=v33.ckandownloads(session)
        if (found["census"]["receipt"]["sha256"]!=SOURCE_CENSUS_SHA or
            found["locations"]["receipt"]["sha256"]!=SOURCE_GEO_SHA):
            raise ValueError("SOURCE_STOP original 2026 NZ source material changed")
        workbook=v33.workbook_original(found["census"]["raw"])
        if set(workbook)!={"All data"}:
            raise ValueError("SOURCE_STOP original author workbook sheets changed")
        raw,source_qa=source_colony_year_counts(workbook["All data"])
        if source_qa["original_2020_count_values_present"]!=0:
            raise ValueError("SOURCE_STOP official no-survey 2020 now contains counts")
        effect=source_analysis(raw,reference)
        receipt={
            "status":"V36_ORIGINAL_ROSS_SEA_GIS_GROWTH_AUDIT_EXECUTED",
            "source_DOI":v33.DOI,
            "original_census_sha256":SOURCE_CENSUS_SHA,
            "original_colony_location_sha256":SOURCE_GEO_SHA,
            "V35_original_independent_SCAR_ADD_coast_sha256":SOURCE_GIS_SHA,
            "source_2026_CKAN_coverage_QA":source_qa,
            "outcome_method":"same-colony log1p reported nest/breeding-pair change; per-island equal colony mean",
            "frozen_design":"contracts/NZ_ROSS_SEA_GIS_ISLAND_GROWTH_V36.md",
            "original_GIS_island_ecology":effect,
            "ecological_effect_computed":effect["ecological_effect_computed"],
            "scientific_decision":effect.get("scientific_decision",effect["status"]),
        }
    except Exception as exc:
        receipt["error_type"]=type(exc).__name__
        receipt["error"]=str(exc)[:650]
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))
    if receipt["status"]=="HOLD_ORIGINAL_SOURCE":
        raise SystemExit(2)

if __name__=="__main__":
    main()
