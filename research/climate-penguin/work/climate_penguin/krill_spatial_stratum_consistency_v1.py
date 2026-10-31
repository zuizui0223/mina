"""Consistency audit: published Signy krill GAM spatial pattern vs published acoustic stratum contrasts.

Inputs are not independent survey sources: Freer et al 2025 GAM learned from
IMR acoustic observations, and the Skaret et al 2023 acoustic stratum table
reports overlapping underlying surveys. The diagnostic is purely
internal/observational; North/South survey STRATA DO NOT correspond to local
near/offshore spatial bands or biologically verified penguin foraging ranges.
No ecological causal claim or forecast is estimated here.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import statistics
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/"research/climate-penguin/inputs/skaret_2023_krill_stratum_table3_reconciled_v2.csv"
BANDS=("0-50","50-100","100-150")
SPECIES=("Adelie","Chinstrap","Gentoo")
YEARS=(2011,2012,2014,2015,2016,2017,2018,2019,2020)


def read(path):
    with Path(path).open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))


def acoustic(path):
    records=read(path)
    items={}
    for row in records:
        yr=int(row["survey_calendar_year"])
        st=row["stratum"]
        key=(yr,st)
        if key in items:
            raise ValueError("duplicate observed acoustic stratum-year")
        if row["source_paper"]!="Skaret_2023_ICES" or row["source_table"]!="Table_3":
            raise ValueError("wrong paper/stratum source")
        items[key]=float(row["density_g_m2"])
    if (2013,"Combined") in items or (2013,"South") in items:
        raise ValueError("2013 original combined/south acoustic is MISSING, not zero")
    if {y for y,s in items if s=="Combined"}!=set(YEARS):
        raise ValueError("original combined acoustic year roster changed")
    if {y for y,s in items if s=="South"}!=set(YEARS):
        raise ValueError("original southern acoustic year roster changed")
    if {y for y,s in items if s=="North"}!=set(range(2011,2021)):
        raise ValueError("original northern acoustic year roster changed")
    return items


def model_bands(path):
    records=read(path)
    vals={}
    for row in records:
        key=(int(row["survey_year"]),row["product"],row["distance_band_km"])
        if key in vals:
            raise ValueError("duplicate modelled krill band-year")
        vals[key]=float(row["predicted_area_weighted_mean"])
        if int(row["n_valid_model_cells"])<20:
            raise ValueError("model valid raster cell support drift")
    expected={(y,p,b) for y in range(2011,2021)
              for p in ("combined","occurrence","positive_density") for b in BANDS}
    if set(vals)!=expected:
        raise ValueError("raster band source expected 90 distinct product-year-band units")
    return vals


def correlation(a,b):
    if len(a)!=len(b) or len(a)<4:
        raise ValueError("requires at least four paired calendar years")
    ma=statistics.mean(a)
    mb=statistics.mean(b)
    x=[z-ma for z in a]
    y=[z-mb for z in b]
    d=math.sqrt(sum(z*z for z in x)*sum(z*z for z in y))
    return sum(z*w for z,w in zip(x,y))/d if d>1e-12 else None


def compute(observed,predicted,stage_annual):
    rows=[]
    for year in YEARS:
        north=observed[year,"North"]
        south=observed[year,"South"]
        combined=observed[year,"Combined"]
        near=predicted[year,"combined","0-50"]
        middle=predicted[year,"combined","50-100"]
        far=predicted[year,"combined","100-150"]
        if min(north,south,combined,near,middle,far)<=0:
            raise ValueError("nonpositive matched source not log-compatible")
        rows.append(dict(
            acoustic_year=year,
            original_north_density_g_m2=north,
            original_south_density_g_m2=south,
            original_combined_density_g_m2=combined,
            original_south_div_north=south/north,
            original_south_minus_north=south-north,
            published_gam_0_50km_mean=near,
            published_gam_50_100km_mean=middle,
            published_gam_100_150km_mean=far,
            published_gam_near_div_far=near/far,
            published_gam_near_minus_far=near-far,
            original_2015_south_survey_ice_limited=(year==2015),
            original_2011_2012_design_differs=(year<=2012)
        ))
    if len(rows)!=9:
        raise ValueError("9 original observed acoustic contrasts required")
    stage={(r["species"],int(r["season_start"])):float(r["median_recorded_fledglings_per_pair"]) 
            for r in read(stage_annual)
            if r["species"] in SPECIES and int(r["season_start"]) in range(2011,2020)}
    if len(stage)!=27:
        raise ValueError("source-native BAS stage n=3 species × 9 seasons drift")
    checks=[]
    for scope in ("all_years","omit_2015_partial_south","omit_2012_influential","omit_both_2012_2015"):
        allowed=[
            r for r in rows if
            (scope not in ("omit_2015_partial_south","omit_both_2012_2015") or r["acoustic_year"]!=2015)
            and (scope not in ("omit_2012_influential","omit_both_2012_2015") or r["acoustic_year"]!=2012)
        ]
        for model_var,obs_var in (
            ("published_gam_near_div_far","original_south_div_north"),
            ("published_gam_near_minus_far","original_south_minus_north"),
            ("published_gam_0_50km_mean","original_north_density_g_m2"),
            ("published_gam_0_50km_mean","original_south_density_g_m2")
        ):
            xx=[r[model_var] for r in allowed]
            yy=[r[obs_var] for r in allowed]
            checks.append(dict(
                scope=scope,n_distinct_calendar_survey_years=len(allowed),
                paired_years=";".join(str(z["acoustic_year"]) for z in allowed),
                modelled_krill_exposure=model_var,
                original_acoustic_stratum_measure=obs_var,
                pearson_r=correlation(xx,yy),
                shared_IMR_training_data_not_independent_test=True,
                geographic_strata_not_equivalent=True
            ))
    stage_checks=[]
    for sp in SPECIES:
        subset=[r for r in rows if r["acoustic_year"]<=2019]
        years=[r["acoustic_year"] for r in subset]
        if len(years)!=8:
            raise ValueError("2013 missing means only 8 Signy stage-opportunity years")
        y=[stage[sp,year] for year in years]
        for feature in ("original_north_density_g_m2",
                        "original_south_density_g_m2",
                        "original_south_div_north",
                        "published_gam_0_50km_mean",
                        "published_gam_near_div_far"):
            stage_checks.append(dict(
                species=sp,years=";".join(map(str,years)),n_calendar_years=8,
                feature=feature,
                pearson_r=correlation([r[feature] for r in subset],y),
                status="DESCRIPTIVE_DIFFERENT_GRAIN_NOT_CAUSAL_OR_FORECAST"
            ))
    return rows,checks,stage_checks


def verify(rows,checks,stage_checks):
    get=lambda a,b:next(z["pearson_r"] for z in checks if
                        z["scope"]=="all_years" and z["modelled_krill_exposure"]==a and
                        z["original_acoustic_stratum_measure"]==b)
    receipt=[
        ("published_gam_near_div_far","original_south_div_north",0.0706),
        ("published_gam_near_minus_far","original_south_minus_north",-0.3388),
        ("published_gam_0_50km_mean","original_north_density_g_m2",0.8198),
        ("published_gam_0_50km_mean","original_south_density_g_m2",0.4003)
    ]
    for a,b,v in receipt:
        if not math.isclose(get(a,b),v,abs_tol=0.00012):
            raise ValueError("earlier independent source calculation disagreed "+a+" "+b)
    if len(rows)!=9 or len(checks)!=16 or len(stage_checks)!=15:
        raise ValueError("source cohort/specification count changed")
    if any(x["acoustic_year"]==2013 for x in rows):
        raise ValueError("2013 partial North improperly substituted")
    return True


def write(path,rows):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--band-csv",required=True,type=Path)
    p.add_argument("--stage-annual",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    annual,contrasts,stage=compute(acoustic(SOURCE),model_bands(a.band_csv),a.stage_annual)
    if a.check:
        verify(annual,contrasts,stage)
    a.out.mkdir(parents=True,exist_ok=True)
    write(a.out/"source_modelled_krill_years.csv",annual)
    write(a.out/"stratum_spatial_consistency.csv",contrasts)
    write(a.out/"native_fledgling_stage_overlap.csv",stage)
    result={
        "status":"MODEL_STRATUM_GEOGRAPHY_NOT_EQUIVALENT_INTERNAL_9YEAR_DIAGNOSTIC",
        "original_acoustic_source":"Skaret 2023 Table3; source corrected 2013 combined and South missing",
        "model_source":"Freer 2025 same underlying IMR 2011-2020 acoustic sample, hurdle GAM with ice/salinity",
        "annual_comparable_acoustic_years":[r["acoustic_year"] for r in annual],
        "observed_acoustic_and_model_years":9,
        "pre_fledgling_stage_seasons":8,
        "n_fixed_stratum_model_comparisons":len(contrasts),
        "n_stage_comparisons":len(stage),
        "primary_modelled_near_far_vs_observed_south_north_ratio_r":
            next(z["pearson_r"] for z in contrasts if z["scope"]=="all_years"
                and z["modelled_krill_exposure"]=="published_gam_near_div_far"
                and z["original_acoustic_stratum_measure"]=="original_south_div_north"),
        "limitations":[
            "North/South acoustic survey strata DO NOT correspond to modelled 0–50 and 100–150 km bands.",
            "Signy centroid/colony points do not identify actual foraging tracks or accessible krill.",
            "Both measures have overlapping original IMR acoustic source; do not call this independent validation.",
            "All spatial krill rasters were fitted with ice, salinity and acoustic data using the full 2011–2020 era.",
            "2013 has only North acoustic data; original Combined and South unavailable, never substituted.",
            "2015 South sampling was limited by ice; 2011/12 survey lines differ, so year comparison is descriptive.",
            "Only eight complete acoustic-year×stage opportunities; response years do not provide independent geographic replication.",
            "A weak near-offshore versus North-South proxy concordance does NOT prove inadequate GAM accuracy: estimands differ.",
            "No predictive climate→krill, krill→fledgling, nests, N_eff or vegetation coefficients validated."
        ],
        "source_receipt_checked":bool(a.check)
    }
    (a.out/"decision.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__":
    main()
