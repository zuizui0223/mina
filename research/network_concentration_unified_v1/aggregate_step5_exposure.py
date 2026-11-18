#!/usr/bin/env python3
"""Step5 source-locked CMIP6 physical exposure of fixed Antarctic MAPPPD cohorts.

No SST-to-breeding prediction or outcome model. Original site counts are transient.
"""
from __future__ import annotations
import csv,hashlib,json,math,subprocess
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent
DATA=BASE/"data"
OUT=BASE/"outputs"
SCENARIO=ROOT/"research/climate-penguin/outputs/cmip6_exposure_atlas_v1/site_scenario_exposure.csv"
MAIN=DATA/"network_species.csv"
LOCK=BASE/"contracts/STEP5_FUTURE_EXPOSURE_LOCK.md"
EXPECTED={"network_species.csv":"e089c4525226c156a1554ce4f480a7611c946ae7",
          "site_scenario_exposure.csv":"9d7badfd2ad077047cb6f20accc74e3738cf4648"}
SCENARIOS=[("ssp245","2041-2060"),("ssp245","2081-2100"),
           ("ssp585","2041-2060"),("ssp585","2081-2100")]
FIELDS=("tas_change_mean_degC","siconc_change_mean_pp","sos_change_mean_native001")

def rows(p):
    with p.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f))

def write(p,records):
    p.parent.mkdir(exist_ok=True,parents=True)
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator="\n")
        w.writeheader();w.writerows(records)

def number(value):
    v=float(value)
    if not math.isfinite(v):raise ValueError("Nonfinite field number")
    return v

def km(lat1,lon1,lat2,lon2):
    p1,p2=map(math.radians,(lat1,lat2))
    dl=math.radians((lon2-lon1+180)%360-180)
    a=math.sin((p2-p1)/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 12742.0176*math.asin(min(1,math.sqrt(a)))

def check_source(path,sha):
    actual=subprocess.run(["git","hash-object",str(path)],cwd=ROOT,
                          check=True,capture_output=True,text=True).stdout.strip()
    if actual!=sha:raise ValueError(f"Prior source pin changed: {path} {actual} vs {sha}")
    return actual

def main():
    if not LOCK.exists():raise ValueError("Missing Step5 pre-computation contract")
    pins={"network_species.csv":check_source(MAIN,EXPECTED["network_species.csv"]),
          "site_scenario_exposure.csv":check_source(SCENARIO,EXPECTED["site_scenario_exposure.csv"])}
    units=DATA/"unit_endpoints.csv"
    if not units.exists():
        raise ValueError("Original Step1 unit_endpoints.csv must be regenerated from byte-pinned originals")
    original=rows(MAIN)
    regions=sorted((r for r in original if r["dataset_id"]=="MAPPPD" and
                    r["analysis_role"]=="macro_primary" and r["null_status"]=="computed"),
                   key=lambda r:r["row_id"])
    uk=[r for r in original if r["dataset_id"]=="JNCC" and
        r["analysis_role"]=="macro_primary" and r["null_status"]=="computed"]
    if len(regions)!=12 or len(uk)!=663:
        raise ValueError("Main Step1 source eligibility changed")
    selected={r["row_id"]:r for r in regions}
    late=defaultdict(dict)
    for s in rows(units):
        if s["analysis_unit"]!="network_species" or s["row_id"] not in selected or s["endpoint"]!="late":
            continue
        if s["dataset_id"]!="MAPPPD" or s["count_unit"]!="nest":
            raise ValueError("A source site has incomparable units")
        sid=s["component_id"]
        if not sid.startswith("MAPPPD::"):
            raise ValueError("Original Mapppd source site id was transformed")
        site=sid[len("MAPPPD::"):]
        if site in late[s["row_id"]]:
            raise ValueError("Repeated physical component in one fixed cohort")
        if s["count_status"] not in ("observed_zero","observed_positive"):
            raise ValueError("Missing is not zero at original late endpoint")
        value=number(s["count_value"])
        if value<0:raise ValueError("Negative original count")
        late[s["row_id"]][site]=(value,number(s["latitude"]),number(s["longitude"]))
    for r in regions:
        pair=late[r["row_id"]]
        if len(pair)!=int(r["K"]):
            raise ValueError(f"Original fixed component count drift: {r['network_id']} {r['species_id']}")
        if abs(sum(p[0] for p in pair.values())-number(r["N1"]))>1e-7:
            raise ValueError("Original late count does not sum to frozen N1")
    scenarios=rows(SCENARIO)
    if len(scenarios)!=424:raise ValueError("Prior 106-coordinate 4-scenario source changed")
    future={}
    for a in scenarios:
        if a["cohort"]!="macro_40":continue
        key=(a["experiment"],a["period"],a["site_id"])
        if key in future:raise ValueError("Duplicate macro40 site/scenario code")
        if (a["experiment"],a["period"]) not in SCENARIOS:
            raise ValueError("Unfrozen scenario")
        future[key]=a
    if len(future)!=160:
        raise ValueError(f"Expected 40 Antarctic fixed source sites x four scenarios, got {len(future)}")
    site_rows=[];summary=Counter();partial={}
    for scenario in SCENARIOS:
        for r in regions:
            sites=late[r["row_id"]]
            match=[];marine=[];missing=Counter()
            for sid,(count,lat,lon) in sorted(sites.items()):
                key=(*scenario,sid)
                geo=future.get(key)
                if geo is None:
                    missing["no_original_macro40_coordinate"]+=1
                    continue
                d=km(lat,lon,number(geo["latitude"]),number(geo["longitude"]))
                if d>0.5:
                    missing["original_coordinate_disagrees_over_500m"]+=1
                    continue
                match.append((count,geo))
                if geo["marine_all_3_models_within_50km"]=="1":
                    marine.append((count,geo))
            n=len(sites);mat=len(match);mn=len(marine)
            N1=number(r["N1"])
            observed_count=sum(a for a,_ in match)
            strict_count=sum(a for a,_ in marine)
            complete=mat==n
            strict=mn==n
            def average(vals,col):
                return sum(number(x[col]) for _,x in vals)/len(vals) if vals else ""
            row={
                "experiment":scenario[0],"period":scenario[1],
                "row_id":r["row_id"],"network_id":r["network_id"],
                "species_id":r["species_id"],
                "year1":r["year1"],"N1":N1,"K":n,
                "matched_site_n":mat,"matched_late_nest_count":observed_count,
                "matched_nest_share":observed_count/N1 if N1>0 else "",
                "strict_marine_site_n":mn,
                "strict_marine_nest_share":strict_count/N1 if N1>0 else "",
                "site_coverage_status":"complete" if complete else ("partial" if mat else "none"),
                "marine_coverage_status":"complete" if strict else ("partial" if mn else "none"),
                "tas_C":"%.12g"%average(match,"tas_change_mean_degC") if complete else "",
                "sic_pp":"%.12g"%average(marine,"siconc_change_mean_pp") if strict else "",
                "sos_native":"%.12g"%average(marine,"sos_change_mean_native001") if strict else "",
                "unmatched_reason_count":json.dumps(dict(missing),sort_keys=True,separators=(",",":")),
            }
            site_rows.append(row)
            summary["total_scenario_network_rows"]+=1
            summary["air_complete_scenario_network_rows"]+=int(complete)
            summary["marine_complete_scenario_network_rows"]+=int(strict)
            if scenario==SCENARIOS[0]:
                summary["total_network_species"]+=1
                summary["air_complete_network_species"]+=int(complete)
                summary["marine_complete_network_species"]+=int(strict)
                summary["matched_sites"]+=mat
                summary["candidate_sites"]+=n
                summary["strict_marine_sites"]+=mn
                summary["total_late_nests"]+=N1
                summary["matched_late_nests"]+=observed_count
                summary["strict_marine_late_nests"]+=strict_count
                partial[r["row_id"]]=dict(r=r,missing=dict(missing),site_n=n,matched_n=mat,
                                           matched_nests=observed_count,strict_marine_n=mn)
    write(DATA/"step5_network_physical_exposure.csv",site_rows)
    species_rows=[]
    for scenario in SCENARIOS:
        for s in sorted({r["species_id"] for r in regions}):
            rr=[r for r in site_rows if r["species_id"]==s and (r["experiment"],r["period"])==scenario]
            denom=sum(r["N1"] for r in rr)
            def aggregate(k,group):
                eligible=[r for r in rr if r[group]=="complete"]
                total=sum(r["N1"] for r in eligible)
                if not eligible or total<=0:return ("",0,0,0)
                v=sum(r["N1"]*float(r[k]) for r in eligible)/total
                return ("%.12g"%v,total,total/denom,len(eligible))
            air,air_count,air_share,air_n=aggregate("tas_C","site_coverage_status")
            sic,sea_count,sea_share,sea_n=aggregate("sic_pp","marine_coverage_status")
            sos,_,_,_=aggregate("sos_native","marine_coverage_status")
            species_rows.append(dict(experiment=scenario[0],period=scenario[1],
                  species_id=s,all_network_count=len(rr),all_late_nests=denom,
                  air_networks=air_n,air_late_nests=air_count,air_late_share=air_share,
                  tas_C=air,marine_networks=sea_n,marine_late_nests=sea_count,
                  marine_late_share=sea_share,sic_pp=sic,sos_native=sos))
    write(DATA/"step5_species_physical_exposure.csv",species_rows)
    # Classify all monitored fixed network units; no ecological future predictions.
    report={
        "status":"PHYSICAL_EXPOSURE_ONLY_NO_BREEDING_FORECAST",
        "source_pins":pins,"n_source_cmip6_sites":40,
        "analysis_network_species":len(regions),
        "n_uncovered_JNCC_macro_species_network_rows":len(uk),
        "scenarios":SCENARIOS,"summary":dict(summary),
        "by_region":[dict(row_id=key,network=x["r"]["network_id"],
           species=x["r"]["species_id"],year1=x["r"]["year1"],source_K=x["site_n"],
           matched_K=x["matched_n"],strict_marine_K=x["strict_marine_n"],
           missing_reasons=x["missing"]) for key,x in partial.items()],
        "limitations":[
          "106 existing CMIP6 atlas positions are NOT 106 independent marine cells.",
          "Only 40 macro_40 original MAPPPD sites are source-compatible with this step.",
          "JNCC 663 UK networks have no matched CMIP6 coast-source cells.",
          "Only complete fixed cohorts produce principal network means; missing climate cells never mean zero change.",
          "Future values are physical exposure under fixed observed population weights, not predicted penguin numbers, occupancy, concentration or competition.",
          "Different source census years mean late weights are a mosaic rather than one synchronized Antarctic breeding census."
        ]}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"STEP5_PHYSICAL_EXPOSURE_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    lines=["# Step 5 — 固定繁殖場所におけるCMIP6物理曝露（将来のペンギン個体数予測ではない）","",
      "主解析675行のうち、既存CMIP6座標とSite.IDの照合可能性を検証したのは南極MAPPPD12行。英国JNCC663行は現状の南極データとは接続しない。",
      f"- MAPPPD 固定ネットワーク×種: {len(regions)}行、元構成単位 {summary['candidate_sites']}地点。",
      f"- CMIP6 macro_40 地点・原座標500m以内で一致: {summary['matched_sites']}地点。",
      f"- 全構成単位が一致したネットワーク×種: {summary['air_complete_network_species']}/{len(regions)}。",
      f"- 3モデルとも50km以内の海域セルですべて一致したネットワーク×種: {summary['marine_complete_network_species']}/{len(regions)}。",
      f"- 原後期巣数でみた座標対応率: {summary['matched_late_nests']/summary['total_late_nests']:.3f}（全12行の年次は揃っていない）。",
      f"- 原後期巣数でみた厳格海域対応率: {summary['strict_marine_late_nests']/summary['total_late_nests']:.3f}。",
      "",
      "## 各種別・全4シナリオ（完全対応ネットワークに限る）","",
      "| 種 | 条件 | 空気温度上昇（℃） | 海氷差（pp） | Air監視巣数対応率 | Marine監視巣数対応率 |",
      "|---|---|---:|---:|---:|---:|"]
    for v in species_rows:
        fmt=lambda x:("NA" if x in ("",None) else f"{float(x):+.3f}")
        lines.append(f"| {v['species_id']} | {v['experiment']}/{v['period']} | {fmt(v['tas_C'])} | {fmt(v['sic_pp'])} | {float(v['air_late_share']):.1%} | {float(v['marine_late_share']):.1%} |")
    lines.extend(["","欠測は真の0変化とみなさない。ネットワーク内は元の固定Site.IDの等重み、種別の完全一致ネットワーク間では後期巣数による固定重み。現行計数は同時年ではない。","",
        "H3/H4には4枠Holm後の支持がなかったため、ここに生物学的な温暖化応答係数を掛けない。将来の集中Yやペア重なりZ、ペンギン巣数の未来予報は出していない。",
        "原データ・結合・完全被覆・欠測の監査情報はSTEP5_PHYSICAL_EXPOSURE_QA.jsonに記録。"])
    (OUT/"STEP5_PHYSICAL_EXPOSURE_JA.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"analysis_rows":len(regions),"summary":dict(summary),
                      "sample_species_rows":species_rows[:3]},ensure_ascii=False))

if __name__=="__main__":main()
