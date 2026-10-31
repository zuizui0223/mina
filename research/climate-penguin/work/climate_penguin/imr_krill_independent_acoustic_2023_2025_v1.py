"""2026-10-31 correction: prioritize Skaret2023 original Table3 Combined for 2011-20.

IMR2024 historical reprint shifts years 2013-20. The primary 2013
Combined is absent owing sea-ice survey coverage; never impute.
2023-25 official IMR Overall summaries are outside Freer training years.
2026 whole-area estimate is unavailable because pack ice and ship gear
accident prevented representative survey coverage. Missing is NOT zero.
No independent krill GPS prey capture or Freer out-of-time prediction test.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics
from pathlib import Path
from scipy.stats import kendalltau,theilslopes

PRIMARY="https://academic.oup.com/icesjms/article/80/5/1472/7161638"
IMR24="https://www.hi.no/hi/nettrapporter/toktrapport-en-2024-14"
IMR25="https://www.hi.no/en/hi/nettrapporter/toktrapport-en-2025-8"
IMR26="https://www.hi.no/hi/nettrapporter/rapport-fra-havforskningen-en-2026-43"
EXPECTED=(2011,2012,2014,2015,2016,2017,2018,2019,2020,2023,2024,2025)
HISTORICAL=EXPECTED[:9]
POST=(2023,2024,2025)
MISSING=(2013,2021,2022,2026)
EXPECTED_PRIMARY={2011:(62.6,.36,120),2012:(128.8,.35,120),
  2014:(76.5,.30,38),2015:(28.5,.19,38),2016:(49.3,.49,120),
  2017:(23.2,.29,120),2018:(69.4,.25,120),2019:(27.2,.29,120),
  2020:(38.8,.14,38)}
EXPECTED_POST={2023:(36.7,.51,120),2024:(80.5,.11,120),2025:(102.,.75,120)}
AREA=60360

def source_rows(file):
    raw=Path(file).read_bytes()
    lines=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    years=tuple(int(x["survey_year"]) for x in lines)
    if years!=EXPECTED:raise ValueError("Source year priority drift: 2013 primary Combined must be missing")
    out=[]
    for r in lines:
        y=int(r["survey_year"])
        d,cv,frequency=float(r["overall_density_g_m2"]),float(r["survey_density_CV"]),int(r["acoustic_frequency_kHz"])
        expected=(EXPECTED_PRIMARY if y<=2020 else EXPECTED_POST)[y]
        if (d,cv,frequency)!=expected:raise ValueError("Primary author source density/CV/year mismatch "+str(y))
        src=PRIMARY if y<=2020 else IMR24 if y<=2024 else IMR25
        if r["official_source_url"]!=src:raise ValueError("Source precedence mismatch "+str(y))
        biomass=float(r["overall_biomass_million_tonnes"])
        if abs(biomass-d*AREA/1e6)>0.016:raise ValueError("Original Overall study area conversion drift "+str(y))
        out.append({"year":y,"density_g_m2":d,"biomass_Mt":biomass,
                    "cv":cv,"frequency_kHz":frequency,"source_url":src,
                    "source_support":"Skaret2023_original_Combined" if y<=2020 else "post_Freer_training_IMR_overall"})
    return out,hashlib.sha256(raw).hexdigest()

def check_discrepancy(path):
    records=list(csv.DictReader(Path(path).read_text(encoding="utf-8").splitlines()))
    expected={2013:2014,2014:2015,2015:2016,2016:2017,2017:2018,2018:2019,2019:2020,2020:2011}
    if len(records)!=8:raise ValueError("Historical reprint missing 8 conflicting original rows")
    for r in records:
        y=int(r["report_2024_reprint_year"]);primary=int(r["primary_Skaret_2023_year_for_same_density"])
        if primary!=expected[y] or float(r["reported_overall_density_g_m2"])!=EXPECTED_PRIMARY[primary][0]:
            raise ValueError("Source-year-label discrepancy ledger changed "+str(y))
    return {"n_reprint_conflicts":8,"primary_2013_Combined_missing":True,
            "reprint_2020_density_equals_primary_2011_not_2020":True}

def check_2026_gate(path):
    g=json.loads(Path(path).read_text(encoding="utf-8"))
    if g.get("source_report")!=IMR26 or g.get("survey_year")!=2026 or (
       g.get("overall_stratum_density_estimable") is not False) or (
       g.get("region_wide_krill_density_g_m2") is not None) or (
       g.get("region_wide_krill_biomass_Mt") is not None) or (
       g.get("penguin_observatory_installed") is not True) or not (
       g.get("cause_ice") and g.get("cause_operational")):
        raise ValueError("2026 ice/ship-censored whole-area source gate changed")
    return g

def run(path,conflict=None,censored=None):
    root=Path(path).parent
    conflict=conflict or root/"IMR2024_reprint_vs_Skaret2023_year_label_discrepancy.csv"
    censored=censored or root/"IMR_2026_acoustic_nonestimable_and_penguin_observatory.json"
    rows,sha=source_rows(path)
    discrepancies=check_discrepancy(conflict)
    gate=check_2026_gate(censored)
    primary=rows[:9]
    post=rows[9:]
    at120=[r for r in rows if r["frequency_kHz"]==120]
    if len(primary)!=9 or len(post)!=3 or len(at120)!=9:raise ValueError("Corrected year/source grain drift")
    def stats(x):
        y=[r["year"] for r in x];d=[r["density_g_m2"] for r in x]
        t=kendalltau(y,d);s=theilslopes(d,y)
        return {"n":len(x),"Kendall_tau":float(t.statistic),"Kendall_p_descriptive":float(t.pvalue),
                "Theil_Sen_g_m2_per_year":float(s.slope),
                "Theil_Sen_95pct_slope_CI":[float(s.low_slope),float(s.high_slope)]}
    stats_by={"primary_2011_2020":stats(primary),"all_corrected_2011_2025":stats(rows),
              "kHz120_only":stats(at120),"posttraining_2023_2025":stats(post)}
    d={
      "status":"SOURCE_AUTHORITY_CORRECTED_ACOUSTIC_2011_2025_AND_2026_ICE_CENSORED",
      "supersedes":"prior same-path 13-estimate reprint-labelled 2011-2025 analysis; DO NOT CITE prior CI",
      "source_csv_sha256":sha,"original_historical_primary":PRIMARY,
      "source_2023_2024":IMR24,"source_2025":IMR25,"source_2026":IMR26,
      "study_area_km2":AREA,
      "n_actual_estimate_years":len(rows),
      "historical_trained_years":list(HISTORICAL),
      "posttraining_estimate_years":list(POST),
      "missing_or_not_estimable_years":list(MISSING),
      "source_year_reprint_discrepancy":discrepancies,
      "2026_survey_full_area_density_is_not_estimable":gate,
      "descriptive_trends":stats_by,
      "annual_posttraining_CV_and_SE":[{
           "year":x["year"],"density_g_m2":x["density_g_m2"],
           "source_CV":x["cv"],"derived_approx_SE_g_m2":x["density_g_m2"]*x["cv"]}
           for x in post],
      "2025_vs_2023_density_point_ratio":post[2]["density_g_m2"]/post[0]["density_g_m2"],
      "regional_survey_acoustic_is_not_observed_prey_at_penguin_GPS":True,
      "no_2023_2025_Freer_prediction_to_score":True,
      "no_2026_full_region_krill_estimate":True,
      "no_climate_salinity_to_breeding_or_vegetation_prediction":True,
      "limitations":[
         "Skaret2023 original Combined 2013 missing due poor survey coverage; the 2024 report shifts historical year labels.",
         "2026 original report has restricted southern coverage due pack ice plus trawl-propeller incident, not zero krill.",
         "2026 Coronation chinstrap camera/acoustic observatory installed, no nest/chick time-series data in this report.",
         "2023-2025 region-level reports outside historical GAM-training year, but no corresponding Freer model forecast exists.",
         "2025 source CV .75; .74 in report overview; 38/120kHz methodology heterogeneous.",
         "Annual regional estimates do not represent penguin-specific nearby prey/acoustic transects.",
         "Neither true future abundance, effective breeding-space N_eff nor vegetation response is calibrated."
      ]}
    return rows,d

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    rows,d=run(a.source);a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"acoustic_annual_source_summary.json").write_text(json.dumps(rows,indent=2,ensure_ascii=False)+"\n")
    (a.out/"decision.json").write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":d["status"],"n":d["n_actual_estimate_years"],
       "trend":d["descriptive_trends"],"posttraining":d["annual_posttraining_CV_and_SE"],
       "missing":d["missing_or_not_estimable_years"]},ensure_ascii=False))
if __name__=="__main__":main()
