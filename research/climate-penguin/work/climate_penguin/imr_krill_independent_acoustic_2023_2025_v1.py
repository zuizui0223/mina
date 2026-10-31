"""Auditable independently surveyed IMR krill acoustic ANNUAL summaries.

Source: IMR official annual overall survey stratum ~60,360 km^2 for South
Orkneys, published annual acoustic density in g m^-2; cruise-level
estimation CV, survey frequency 38 or 120 kHz, years 2011-20, 2023-25.
2021-22 missing, NEVER interpolated. The 2023-25 estimates were NOT in
Freer 2011-20 historical GAM training period but cannot validate its original
spatial model at penguin GPS coordinates or concurrent 2011-19 tracking.
Do not infer a climate→krill causal trend or krill→nest demographics.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics
from pathlib import Path
from scipy.stats import kendalltau,theilslopes

EXPECTED_YEARS=(2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2023,2024,2025)
TRAINED_YEARS=tuple(range(2011,2021))
POSTTRAIN_YEARS=(2023,2024,2025)
SURVEY_AREA_KM2=60360
SOURCE_2024="https://www.hi.no/hi/nettrapporter/toktrapport-en-2024-14"
SOURCE_2025="https://www.hi.no/en/hi/nettrapporter/toktrapport-en-2025-8"
MAX_ROUNDING_MILLION_T=0.016

def source_rows(file):
    data=Path(file).read_bytes()
    rows=list(csv.DictReader(data.decode("utf-8-sig").splitlines()))
    years=tuple(int(r["survey_year"]) for r in rows)
    if years!=EXPECTED_YEARS or len(years)!=len(set(years)):
        raise ValueError("Original published survey year roster drift; 2021-22 must stay missing")
    valid=[]
    for r in rows:
        year=int(r["survey_year"])
        d=float(r["overall_density_g_m2"])
        t=float(r["overall_biomass_million_tonnes"])
        cv=float(r["survey_density_CV"])
        freq=int(r["acoustic_frequency_kHz"])
        if freq not in (38,120) or not(d>0 and t>0 and 0<cv<1):
            raise ValueError("Invalid source acoustic study grain, CV or conversion")
        if r["official_source_url"] not in (SOURCE_2024,SOURCE_2025):
            raise ValueError("Source was not original official IMR survey report")
        if year==2025 and r["official_source_url"]!=SOURCE_2025:
            raise ValueError("2025 source must refer to original 2025 survey results")
        if abs(t-(d*SURVEY_AREA_KM2/1e6))>MAX_ROUNDING_MILLION_T:
            raise ValueError("Original acoustic density and biomass conversion mismatch "+str(year))
        valid.append({"year":year,"density_g_m2":d,"biomass_Mt":t,"cv":cv,
            "frequency_kHz":freq,"source_url":r["official_source_url"],
            "source_support":"Freer_historical_training_period" if year in TRAINED_YEARS
                              else "acoustic_outside_Freer_2011_2020_training_years"})
    for year,density,cv in ((2023,36.7,.51),(2024,80.5,.11),(2025,102.,.75)):
        x=next(z for z in valid if z["year"]==year)
        if (x["density_g_m2"],x["cv"])!=(density,cv):
            raise ValueError("New acoustic out-of-training-year original survey receipt changed")
    return valid,hashlib.sha256(data).hexdigest()

def run(path):
    rows,sha=source_rows(path)
    years=[x["year"] for x in rows]
    density=[x["density_g_m2"] for x in rows]
    tau=kendalltau(years,density)
    sen=theilslopes(density,years,alpha=.95)
    subset=[r for r in rows if r["frequency_kHz"]==120]
    tau120=kendalltau([x["year"] for x in subset],
                      [x["density_g_m2"] for x in subset])
    pre=[x for x in rows if x["year"] in TRAINED_YEARS]
    post=[x for x in rows if x["year"] in POSTTRAIN_YEARS]
    if len(pre)!=10 or len(post)!=3 or len(subset)!=9:
        raise ValueError("Original acoustic survey instrument/time strata changed")
    result={
        "status":"INDEPENDENT_POSTTRAIN_ACOUSTIC_ANNUAL_REGIONAL_SOURCE_VALIDATED_NOT_GPS_PREY",
        "official_IMR_sources":[SOURCE_2024,SOURCE_2025],
        "source_CSV_sha256":sha,"study_area_km2":SURVEY_AREA_KM2,
        "n_annual_survey_estimates":len(rows),
        "Freer_2011_2020_historical_training_overlap_n":len(pre),
        "original_out_of_training_survey_years":list(POSTTRAIN_YEARS),
        "missing_actual_survey_estimates_years":[2021,2022],
        "overall_stratum_density_Kendall_tau":float(tau.statistic),
        "overall_stratum_density_Kendall_p_descriptive":float(tau.pvalue),
        "overall_stratum_density_Theil_Sen_g_m2_per_year":float(sen.slope),
        "overall_stratum_density_Theil_Sen_95pct_CI":[float(sen.low_slope),float(sen.high_slope)],
        "kHz120_only_n":len(subset),
        "kHz120_only_Kendall_tau":float(tau120.statistic),
        "kHz120_only_Kendall_p_descriptive":float(tau120.pvalue),
        "historical_2011_2020_median_density_g_m2":statistics.median(x["density_g_m2"] for x in pre),
        "posttraining_yearly_original_acoustic_estimates":post,
        "posttraining_2025_vs_2023_raw_density_ratio":post[-1]["density_g_m2"]/post[0]["density_g_m2"],
        "acoustic_years_are_regional_cruises_not_prey_measurements_at_penguin_GPS":True,
        "2025_survey_very_high_CV":True,
        "no_attribution_to_ice_or_salinity_or_future_nesting":True,
        "warnings":[
            "Official IMR reports give original region-wide overall-stratum acoustic survey summaries, not georeferenced original transect/NASC per GPS fix.",
            "The 2013 overall stratum density is not a replacement for any separately missing combined acoustic stratum in another study. Keep grain and CV.",
            "2025 official report presents CV 0.75 in results and rounded 0.74 in executive summary; use results/Table/Figure value and retain note of mismatch.",
            "Reported 38 and 120kHz acoustic frequencies vary over 2011-20; separate sensitivity included, but no instrument calibration bridging is inferred.",
            "The annual surveys cover only austral-summer fixed transects; not penguin foraging-distance or local colony marine accessibility.",
            "Post-2020 years 2023-25 were not included in Freer 2011-2020 model training but no model prediction for these new years exists; not an actual GAM out-of-time forecast accuracy test.",
            "Three post-training points and 2025 CV=0.75 do not establish a statistically significant increasing trend.",
            "Regional density cannot explain individual prey capture, chick survival, nest density, breeding patch N_eff, or 2050/2100 vegetation change without independent spatial and stage-specific linkage."
        ]}
    return rows,result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    rows,decision=run(a.source)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"acoustic_annual_source_summary.json").write_text(
        json.dumps(rows,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (a.out/"decision.json").write_text(
        json.dumps(decision,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":decision["status"],
      "acoustic_outside_training":[(x["year"],x["density_g_m2"],x["cv"])
        for x in decision["posttraining_yearly_original_acoustic_estimates"]],
      "tau_all":decision["overall_stratum_density_Kendall_tau"],
      "kendall_p":decision["overall_stratum_density_Kendall_p_descriptive"],
      "instrument_120_kHz_tau":decision["kHz120_only_Kendall_tau"]},ensure_ascii=False))
if __name__=="__main__":main()
