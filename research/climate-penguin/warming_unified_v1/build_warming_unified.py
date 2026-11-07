#!/usr/bin/env python3
"""Warming-unified v1: join fixed six monitored breeding sites and nine Signy shared seasons.

The ecological units are DIFFERENT: six sites/2 regions, versus one island/9 seasons.
No new causal tests, no fitted climate response transferred into the future.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
OUTPUT=ROOT/"research/climate-penguin/outputs"
OUT=BASE/"outputs"
DATA=BASE/"data"
PLAN=BASE/"ANALYSIS_CONTRACT_20261107.md"
PINS={
    "warming_species_breeding_v1/matched_species_breeding_change.csv":"f17b4a21e9e5a045a40f5a4af9019e3bbc011758",
    "warming_species_breeding_v1/historical_species_site_trends.csv":"2b6c0793ea9f9ea9acf0771052cf7a2ad9ab335b",
    "warming_species_breeding_v1/future_climate_coobserved_sites.csv":"97ae24e98a0cb5f6b36e275d036cb4b71c953312",
    "signy_diet_components_v1/species_season_components.csv":"715364538b0542cf1198e9a2ab0ae2133495ba9a",
    "hatching_gap_climate_v1/signy_17_seasons.csv":"f12581366ce908bafec1bd1b450efe8f41eeb605",
    "cmip6_exposure_atlas_v1/site_scenario_exposure.csv":"9d7badfd2ad077047cb6f20accc74e3738cf4648",
}
SIX=("ARDL","BISC","LION","LLAN","PCHA","PETE")
SEASONS=tuple(range(2001,2010))
SCENARIOS=(("ssp245","2041-2060"),("ssp245","2081-2100"),
           ("ssp585","2041-2060"),("ssp585","2081-2100"))
SPS=("Adelie","Chinstrap","Gentoo")

def rows(path):
    with path.open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))

def save(path,records):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator="\n")
        w.writeheader();w.writerows(records)

def ensure(x,why):
    if not x:raise ValueError("WARMING_UNIFIED_SOURCE_GATE: "+why)

def val(x):
    y=float(x)
    if not math.isfinite(y):raise ValueError("Nonfinite source numeric value")
    return y

def corr(a,b):
    aa=[val(q) for q in a];bb=[val(q) for q in b]
    ma=statistics.mean(aa);mb=statistics.mean(bb)
    den=math.sqrt(sum((v-ma)**2 for v in aa)*sum((v-mb)**2 for v in bb))
    if den<=0:raise ValueError("Undefined Pearson r for repeated climate years")
    return sum((x-ma)*(y-mb) for x,y in zip(aa,bb))/den

def loo_corr(a,b):
    return [corr(a[:i]+a[i+1:],b[:i]+b[i+1:]) for i in range(len(a))]

def source_check():
    ensure(PLAN.exists(),"pre-saved warming contract missing")
    pins={}
    for name,sha in PINS.items():
        path=OUTPUT/name
        actual=subprocess.run(["git","hash-object",str(path)],cwd=ROOT,
                     capture_output=True,text=True,check=True).stdout.strip()
        ensure(actual==sha,"Source binary changed: "+name+" got="+actual)
        pins[name]={"git_blob":actual,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
    return pins

def source_report_six():
    source=(OUTPUT/"niche_timescale_divergence_v1/REPORT_JA.md").read_text(encoding="utf-8")
    data=[]
    for line in source.splitlines():
        if not line.startswith("| "):continue
        parts=[p.strip() for p in line.split("|")[1:-1]]
        if len(parts)!=5 or parts[0] not in SIX:continue
        data.append(dict(site_id=parts[0],
           source_log_ratio_slope=val(parts[1]),
           observed_september_sic_slope=val(parts[2]),
           observed_aug_nov_sic_slope=val(parts[3]),
           full_30yr_aug_nov_sic_slope=val(parts[4])))
    ensure(len(data)==6 and set(x["site_id"] for x in data)==set(SIX),
           "Six original source-report table rows missing")
    ensure(sum(x["source_log_ratio_slope"]>0 for x in data)==6,
           "Existing six positive true breeding ratio slopes changed")
    ensure(sum(x["observed_september_sic_slope"]>0 for x in data)==4,
           "Published 4/6 observed-year Sep SIC directions changed")
    ensure(sum(x["full_30yr_aug_nov_sic_slope"]<0 for x in data)==6,
           "Published 6/6 full-year SIC negative trends changed")
    return {r["site_id"]:r for r in data}

def main():
    pins=source_check()
    summaries=rows(OUTPUT/"warming_species_breeding_v1/matched_species_breeding_change.csv")
    trends=rows(OUTPUT/"warming_species_breeding_v1/historical_species_site_trends.csv")
    future=rows(OUTPUT/"warming_species_breeding_v1/future_climate_coobserved_sites.csv")
    cmip=rows(OUTPUT/"cmip6_exposure_atlas_v1/site_scenario_exposure.csv")
    phys={(r["site_id"],r["experiment"],r["period"]):r for r in future}
    ensure(len(phys)==len(future),"duplicated physical-site-scenario")
    trend={(r["site_id"],r["species_id"]):r for r in trends}
    reported=source_report_six()
    strict=[]
    for site in SIX:
        q=[r for r in summaries if r["site_id"]==site and r["reference_species"]=="ADPE"
             and r["compared_species"]=="GEPE" and r["gate"]=="1"]
        ensure(len(q)==1,"Original same-year strict source pair missing: "+site)
        r=q[0]
        ensure(min(val(r[k]) for k in ("first_ADPE_n","last_ADPE_n","first_other_n","last_other_n"))>0,
               "Strict original ratio has nonpositive endpoint at "+site)
        ensure(val(r["last_ADPE_n"])<val(r["first_ADPE_n"]) and
               val(r["last_other_n"])>val(r["first_other_n"]),
               "Opposite absolute source endpoints do not hold at "+site)
        ensure((site,"ADPE") in trend and (site,"GEPE") in trend,"Original trend absent")
        x=reported[site]
        strict.append(dict(site_id=site,region=r["region"],year0=r["first_year"],year1=r["last_year"],
              common_years_n=r["n_shared_years"],count_span=r["shared_span_years"],
              first_Adelie=r["first_ADPE_n"],last_Adelie=r["last_ADPE_n"],
              first_Gentoo=r["first_other_n"],last_Gentoo=r["last_other_n"],
              log_ratio_slope_decade=f"{x['source_log_ratio_slope']:.6g}",
              sep_SIC_observed_years_pp_decade=x["observed_september_sic_slope"],
              aug_nov_SIC_observed_years_pp_decade=x["observed_aug_nov_sic_slope"],
              aug_nov_SIC_full_1991_2020_pp_decade=x["full_30yr_aug_nov_sic_slope"]))
    ensure(len({r["region"] for r in strict})==2,"Six sites no longer from two regions")
    atlas={r["site_id"]:r for r in cmip if r["cohort"]=="macro_40" and
           r["experiment"]=="ssp245" and r["period"]=="2041-2060"}
    future_rows=[];climate=[]
    for condition in SCENARIOS:
        these=[]
        for site in SIX:
            ensure((*[site],*condition) in phys,"Missing source future site "+site)
            p=phys[(site,*condition)]
            ensure(p["all3_tas_increase"]=="1" and p["all3_sic_decrease"]=="1",
                   "Source consensus climate sign changed")
            ensure(p["all3_marine_cell_within50km"]=="1","Marine physical support changed")
            h=reported[site]
            ensure(abs(val(p["historical_obs_SIC_trend_pp_decade"])-h["full_30yr_aug_nov_sic_slope"])<.001,
                   "Source 1991–2020 SIC slope does not match prior strict-site report")
            fingerprint=atlas[site]["marine_fingerprint"] if site in atlas else ""
            these.append(dict(site_id=site,region=next(r["region"] for r in strict if r["site_id"]==site),
                 experiment=condition[0],period=condition[1],
                 tas_C_change_mean=val(p["tas_C_change_model_mean"]),
                 tas_C_change_min=val(p["tas_C_change_min"]),tas_C_change_max=val(p["tas_C_change_max"]),
                 SIC_pp_change_mean=val(p["SIC_pp_change_model_mean"]),
                 SIC_pp_change_min=val(p["SIC_pp_change_min"]),SIC_pp_change_max=val(p["SIC_pp_change_max"]),
                 sos_change_native=val(p["sos_change_model_mean"]),
                 observed_SIC_full30yr_trend_pp_decade=h["full_30yr_aug_nov_sic_slope"],
                 three_models_tas_increase=p["all3_tas_increase"],
                 three_models_sic_decrease=p["all3_sic_decrease"],
                 marine_fingerprint=fingerprint))
        future_rows+=these
        climate.append(dict(experiment=condition[0],period=condition[1],
           n_site=6,n_geographic_regions=2,
           n_unique_marine_fingerprints=len({x["marine_fingerprint"] for x in these if x["marine_fingerprint"]}),
           mean_tas_C=statistics.mean(x["tas_C_change_mean"] for x in these),
           mean_SIC_pp=statistics.mean(x["SIC_pp_change_mean"] for x in these),
           mean_sos_native=statistics.mean(x["sos_change_native"] for x in these),
           tas_site_range=[min(x["tas_C_change_mean"] for x in these),max(x["tas_C_change_mean"] for x in these)],
           sic_site_range=[min(x["SIC_pp_change_mean"] for x in these),max(x["SIC_pp_change_mean"] for x in these)],
           n_all3_tas_warming=sum(x["three_models_tas_increase"]=="1" for x in these),
           n_all3_sic_decreasing=sum(x["three_models_sic_decrease"]=="1" for x in these)))
    save(DATA/"six_site_original_breeding_ice.csv",strict)
    save(DATA/"six_site_future_physical.csv",future_rows)

    diet=rows(OUTPUT/"signy_diet_components_v1/species_season_components.csv")
    hatching=rows(OUTPUT/"hatching_gap_climate_v1/signy_17_seasons.csv")
    hatch={int(r["year"]):r for r in hatching}
    ensure(len(hatch)==17 and len(hatching)==17,"Published 17-season hatching source changed")
    digest={(int(r["year"]),r["species"]):r for r in diet}
    ensure(len(diet)==27 and len(digest)==27,"Original three species x nine diet years changed")
    nine=[]
    for y in SEASONS:
        ensure(y in hatch and all((y,sp) in digest for sp in SPS),
               "Exact common calendar year lacks both axes "+str(y))
        a,g,c=[digest[(y,sp)] for sp in ("Adelie","Gentoo","Chinstrap")]
        h=hatch[y]
        sic=val(g["sic_aug_nov"])
        ensure(all(abs(val(x["sic_aug_nov"])-sic)<1e-10 for x in (a,c)),
               "Species stomachs were joined to different GOPT SIC")
        ensure(abs(sic-10*val(h["ice10"]))<.00001,
               "Two original annual SIC proxies do not refer to same climate series")
        fish=val(g["mean_fish_fraction"])-.5*(val(a["mean_fish_fraction"])+val(c["mean_fish_fraction"]))
        gap=val(h["gap"])
        ensure(abs(gap-(val(h["Chinstrap"])-val(h["Adelie"])))<1e-10,
               "Original hatching gap not species difference")
        nine.append(dict(year=y,site_id="SIGNY::GOPT",sic_aug_nov_pct=sic,
             diet_gentoo_fish_fraction=val(g["mean_fish_fraction"]),
             diet_adelie_fish_fraction=val(a["mean_fish_fraction"]),
             diet_chinstrap_fish_fraction=val(c["mean_fish_fraction"]),
             diet_gap_fish_fraction=fish,
             hatching_adelie_day=val(h["Adelie"]),
             hatching_chinstrap_day=val(h["Chinstrap"]),
             hatching_gap_days=gap,
             n_stomachs_adelie=a["n_stomachs"],
             n_stomachs_chinstrap=c["n_stomachs"],
             n_stomachs_gentoo=g["n_stomachs"],
             adelie_hatching_source_colony=h["Adelie_colony"]))
    ensure(sum(int(r["n_stomachs_"+sp]) for r in nine for sp in ("adelie","chinstrap","gentoo"))==772,
           "BAS source sample total changed; stomachs not climate-year replicates")
    save(DATA/"signy_same_year_diet_phenology.csv",nine)
    def series(k):return [r[k] for r in nine]
    sic=series("sic_aug_nov_pct")
    fish=series("diet_gap_fish_fraction")
    gap=series("hatching_gap_days")
    r_fish=corr(sic,fish)
    r_gap=corr(sic,gap)
    r_cog=corr(fish,gap)
    r_adelie=corr(sic,series("hatching_adelie_day"))
    r_chin=corr(sic,series("hatching_chinstrap_day"))
    loo_fish=loo_corr(sic,fish)
    loo_gap=loo_corr(sic,gap)
    report=dict(
       status="WARMING_SINGLE_PAPER_CROSS_AXIS_OBSERVATIONAL_JOIN_NO_CAUSAL_FORECAST",
       prior_outcomes_viewed=True,
       input_git_blob_and_sha256=pins,
       contract_sha256=hashlib.sha256(PLAN.read_bytes()).hexdigest(),
       same_location_community=dict(
          strict_shared_breeding_sites=6,regions=2,
          all_six_true_ratio_slope_positive=True,
          six_adelie_absolute_endpoints_declining=True,
          six_gentoo_absolute_endpoints_increasing=True,
          observed_year_september_sic_positive_sites=sum(float(r["sep_SIC_observed_years_pp_decade"])>0 for r in strict),
          long_period_aug_nov_sic_negative_sites=sum(float(r["aug_nov_SIC_full_1991_2020_pp_decade"])<0 for r in strict),
          site_codes=list(SIX),all_site_values= "data/six_site_original_breeding_ice.csv"),
       same_year_Signy=dict(
          island="Signy",n_climate_years=9,years=list(SEASONS),
          n_original_stomachs_across_9_years=772,
          r_sic_vs_fish_gap=r_fish,r_sic_vs_hatching_gap=r_gap,
          r_fish_gap_vs_hatching_gap=r_cog,
          r_sic_vs_absolute_adelie_hatch_day=r_adelie,
          r_sic_vs_absolute_chinstrap_hatch_day=r_chin,
          mean_fish_gap=statistics.mean(fish),mean_hatch_gap_days=statistics.mean(gap),
          r_fish_sic_leave_one_year_range=[min(loo_fish),max(loo_fish)],
          r_hatch_gap_sic_leave_one_year_range=[min(loo_gap),max(loo_gap)],
          descriptive_abs_correlation_contrast=abs(r_fish)-abs(r_gap),
          hatching_adelie_colony_changed_in_2003=True,
          no_new_formal_hypothesis_p_values=True),
       future_six_sites=dict(
          scenario_conditions=4,locations_per_condition=6,
          physical_exposure_only=True,
          scenario_site_equal_means=climate),
       land_vegetation=dict(status="UNVALIDATED_NEST_POLYGON_ANNUAL_VEGETATION_RESPONSE",
               no_greenup_or_future_nest_access_forecast=True),
       limitations=[
         "Six community sites share two regions and reused ocean-grid values; repeated sites are not independent geographic experiments.",
         "Signy 9 shared years are one island, and 772 stomachs are not independent climate replicates.",
         "Absolute hatching timing and allochrony findings were already reported by Clewlow et al. (2019).",
         "Existing diet/ice relationships and population trajectories were inspected before cross-axis audit.",
         "Sea-ice and temperatures are observations, not random treatments; no climate caused species replacement inference.",
         "Marine, phenology and community observations were obtained in different localities, temporal grains and methods.",
         "Published static vegetation map / unvalidated NDVI is not a nest-level vegetation trajectory.",
         "CMIP6 future physical changes do not constitute future nest counts, diet, or hatching-day predictions."
       ])
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"WARMING_UNIFIED_EVIDENCE.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    lines=[
      "# 温暖化×ペンギン：一本化統合・原行監査（2026-11-07）","",
      "**主題は温暖化が繁殖群集・海のニッチ・時間ニッチにどう違って現れるか。** 集中JNNCCの論文ではない。元結果を見た後の観測的統合であり、因果や予報を確証したものではない。",
      "","## 1. 長期の繁殖群集変化と観測海氷の時間尺度","",
      "- 同所・同年・同一計数法で全共通年に2種が繁殖したアデリー対ジェンツー6地点（2地域）：元実巣数比の増加6/6、アデリー絶対減6/6、ジェンツー絶対増6/6。",
      f"- 元1991–2020年の8–11月SIC長期低下6/6。一方、元繁殖数を観測した年だけの9月SIC増加は{report['same_location_community']['observed_year_september_sic_positive_sites']}/6。これは逆転ではなく環境窓の違い。",
      "","## 2. 同じSigny繁殖季を使った海・時間ニッチの新しい同年照合","",
      "- 2001–2009の共通9繁殖季、3種元胃772個、原平均孵化日を別原資料で接続。元SICの10倍単位差まで相互に点検した。",
      f"- 海の3種魚類比率差 D と8–11月SIC: r={r_fish:+.4f}（9季、留一季 r={min(loo_fish):+.4f}〜{max(loo_fish):+.4f}）。",
      f"- 時間ニッチ（Chinstrap−Adélie孵化日の差）と同じSIC: r={r_gap:+.4f}（同9季、留一季 r={min(loo_gap):+.4f}〜{max(loo_gap):+.4f}）。",
      f"- 海・時間の2軸の同年相関: r={r_cog:+.4f}、絶対孵化日とSICはAdélie r={r_adelie:+.4f}／Chinstrap r={r_chin:+.4f}。個体胃772を気候反復772と数えない。",
      f"- 海と時間のSIC相関の絶対値差 |r海|−|r時間|={abs(r_fish)-abs(r_gap):+.4f}。これは差の有意性や気候因果を検定した結果ではない。",
      "- Signy時期差はClewlow et al. (2019)がすでに報告。今回の追加は9年同一海氷系列と元胃差の独立原行の同年監査。",
      "","## 3. 同一6繁殖地点への4条件の将来物理曝露（生物予測ではない）","",
      "| SSP / 期間 | 空気温度tas平均Δ℃ | 海氷SIC平均Δpp | 塩分sos元単位Δ | 全3モデル昇温/海氷減 | 実海洋格子指紋数 |",
      "|---|---:|---:|---:|---|---:|"]
    for z in climate:
        lines.append(f"| {z['experiment']} / {z['period']} | {z['mean_tas_C']:+.2f} | {z['mean_SIC_pp']:+.2f} | {z['mean_sos_native']:+.3f} | {z['n_all3_tas_warming']}/6、{z['n_all3_sic_decreasing']}/6 | {z['n_unique_marine_fingerprints']} |")
    lines.extend([
      "","## 4. 陸・植生、塩分/水温、空間集中の使い方","",
      "- 陸上繁殖数の種組成変化は主観測の繁殖応答だが、**緑化・無氷地・巣ポリゴンの時系列は較正不足**。植生の同年・同地点因果効果を入れない。",
      "- 塩分・SST・気温は既存の探索的な物理環境。独立地域の予測性能は弱く、既存将来条件の生物応答係数はモデル仕様で符号が逆転する。物理曝露から未来の種比や巣数は計算しない。",
      "- Palmer/Signyの繁殖区画集中は人口構造の下位空間軸として補足に置く。UK JNCCの集中マクロ論文は温暖化主論文に加算しない。既存の肯定結果は保持。",
      "- この統合表の9年は前解析を見た後の同年照合であり、外部事前登録ではない。平均孵化日とGentoo胃の試料同一個体性はない。",
      "","## 明確に区別すべきこと","",
      "肯定：6地点での反対方向の絶対巣数、全30年のSIC低下、Signy元胃の海氷関連、時間差の継続、将来の物理環境変化。",
      "未同定：温暖化が巣数交代の原因か／種間競争が変わったか／植生が巣を増減させたか／2050-2100の種別繁殖数・定着日は何か。",
      "新しく実行：一つの9季節で海と時間ニッチを同じSICへ対応させた出典固定の数値表と、同じ6繁殖地点だけでの4将来気候条件の縮約。"
    ])
    (OUT/"WARMING_UNIFIED_EVIDENCE_JA.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"status":report["status"],"six":len(strict),"signy_years":len(nine),
       "r_diet":r_fish,"r_gap":r_gap,"r_diet_gap":r_cog,
       "future":climate},ensure_ascii=False))

if __name__=="__main__":
    main()
