"""Crosswalk *independently sourced satellite physical ice* with pretrained krill GAM.

Source inputs are two small SHA-pinned derived receipts from first-party
publisher-original GitHub Actions, no raw penguin locations. This joins
matching island-year labels for inspection only. It does NOT regress one
against the other, infer ice→prey causality, or fit climate→breeding forecasts.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path

EXPECTED_ICE_NORMALIZED_SHA="bcaa350b5e1b5c3729bf1c7941e225dbc233cd178b6447582d2f55f309faa366"
EXPECTED_GAM_NORMALIZED_SHA="5efa3e418794691d43e186368f93e335da2809b92ce286e9bca67e2ecddf8b63"
SOURCE_ICE_RUN="https://github.com/zuizui0223/mina/actions/runs/41190087752"
SOURCE_KRILL_RUN="https://github.com/zuizui0223/mina/actions/runs/41184743053"
EXPECTED_PAIRS=((2011,"LI"),(2013,"PI"),(2015,"MI"))
EXPECTED_DAYS={(2011,"LI"):(1,5),(2013,"PI"):(3,11),(2015,"MI"):(5,20)}
EXPECTED_ICE={(2011,"LI"):(0.0,0.0),
              (2013,"PI"):(10.977869005847952,2.6582947368421057),
              (2015,"MI"):(0.5218378378378379,0.0)}

def original_receipt(path,sha):
    raw=Path(path).read_bytes().replace(b"\r\n",b"\n")
    if hashlib.sha256(raw).hexdigest()!=sha:
        raise ValueError("Immutable original source receipt digest drift: "+Path(path).name)
    rows=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    return rows

def join(ice,gam):
    byice={}
    for row in ice:
        key=(int(row["season_start"]),row["other_island"],row["fixed_GPS_footprint"],row["month"])
        if key in byice:raise ValueError("duplicate source SIC fixed-pixel month receipt")
        byice[key]=row
    bygam={}
    for row in gam:
        key=(int(row["season_start"]),row["other_island"],row["model_period"])
        if key in bygam:raise ValueError("duplicate original Freer krill GAM output receipt")
        bygam[key]=row
    if len(ice)!=18 or len(gam)!=6:
        raise ValueError("published fixed source sensitivity support incomplete")
    out=[]
    for year,other in EXPECTED_PAIRS:
        dec=byice[year,other,"all_GPS_days","Dec"]
        jan=byice[year,other,"all_GPS_days","Jan"]
        pre=bygam[year,other,"preseason"]
        post=bygam[year,other,"same_summer"]
        obs_days=int(dec["n_valid_fixed_pixel_daily_contrasts"]),int(jan["n_valid_fixed_pixel_daily_contrasts"])
        source_days=int(dec["n_original_shared_source_GPS_days"]),int(jan["n_original_shared_source_GPS_days"])
        if obs_days!=EXPECTED_DAYS[year,other] or obs_days!=source_days:
            raise ValueError("GPS native actual observation-day support changed")
        deltas=float(dec["mean_Signy_minus_other_fixed_25km_cell_SIC_pp"]),float(
            jan["mean_Signy_minus_other_fixed_25km_cell_SIC_pp"])
        if any(not math.isclose(a,b,abs_tol=1e-12) for a,b in zip(deltas,EXPECTED_ICE[year,other])):
            raise ValueError("Original satellite SIC fixed-pixel outcome drift")
        original_ratio=float(pre["combined_radial_adjusted_ratio"])
        summer_ratio=float(post["combined_radial_adjusted_ratio"])
        if original_ratio<=0 or summer_ratio<=0:raise ValueError("pretrained krill GAM denominator invalid")
        n=(int(pre["n_native_pixels_Signy"]),int(pre["n_native_pixels_other"]))
        if n!=(int(post["n_native_pixels_Signy"]),int(post["n_native_pixels_other"])):
            raise ValueError("original krill GAM source pixels differ by retrospective model year")
        out.append({
            "season_start":year,"other_island":other,"reference_island":"SI",
            "GPS_shared_Dec_dates":obs_days[0],"GPS_shared_Jan_dates":obs_days[1],
            "native_daily_SIC_Signy_minus_other_Dec_pp":deltas[0],
            "native_daily_SIC_Signy_minus_other_Jan_pp":deltas[1],
            "SIC_Signy_minus_other_Dec_to_Jan_change_pp":deltas[1]-deltas[0],
            "preseason_T_Freer_GAM_other_div_Signy_krill_model_ratio":original_ratio,
            "retrospective_Tplus1_Freer_GAM_other_div_Signy_krill_model_ratio":summer_ratio,
            "retrospective_Tplus1_vs_T_modelled_ratio_attenuation":summer_ratio/original_ratio,
            "GAM_native_model_pixels_Signy":n[0],
            "GAM_native_model_pixels_other":n[1],
            "satellite_daily_SIC_and_GAM_are_not_same_measurement_dates":True,
            "pretrained_Freer_GAM_already_uses_seaice_salinity_acoustic":True,
            "no_pretraining_out_of_time_or_independent_prey_causality":True,
            "no_2050_2100_breeding_or_vegetation_forecast":True
        })
    return out

def output(root,icepath,gampath):
    pairs=join(original_receipt(icepath,EXPECTED_ICE_NORMALIZED_SHA),
               original_receipt(gampath,EXPECTED_GAM_NORMALIZED_SHA))
    root.mkdir(parents=True,exist_ok=True)
    with (root/"satellite_SIC_vs_published_krill_GAM_source_crosswalk.csv").open("w",
             newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(pairs[0]))
        writer.writeheader();writer.writerows(pairs)
    result={
        "status":"INDEPENDENT_SATELLITE_ICE_VS_PRETRAINED_KRILL_GAM_CROSSWALK_ONLY",
        "source_ice_CI":SOURCE_ICE_RUN,"source_GAM_CI":SOURCE_KRILL_RUN,
        "source_ice_original_derived_receipt_sha256":EXPECTED_ICE_NORMALIZED_SHA,
        "source_GAM_original_derived_receipt_sha256":EXPECTED_GAM_NORMALIZED_SHA,
        "n_island_year_pairs":len(pairs),"n_original_shared_daily_SIC_dates":sum(
            r["GPS_shared_Dec_dates"]+r["GPS_shared_Jan_dates"] for r in pairs),
        "joined_source_metrics":pairs,
        "limitations":[
            "Satellite SIC = observed 25km 24h average on GPS-selected fixed pixels; not daily ocean passability.",
            "Preseason krill T = modelled Jan-Feb of preceding model year; retrospective T+1 = modelled Jan-Feb of breeding season, not same GPS days.",
            "Freer GAM fit with original acoustic, sea ice and salinity: combining these sources does not independently identify ice impact on krill.",
            "One other island per year (island and year confounded) and only one 2011 shared December day.",
            "No causal temperature/ice/salinity→prey→fledgling→breeding space N_eff, vegetation or 2050/2100 projection."
        ]}
    (root/"decision.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"n":len(pairs),
       "data":[{k:v for k,v in r.items() if k in
            ("season_start","other_island","native_daily_SIC_Signy_minus_other_Dec_pp",
             "native_daily_SIC_Signy_minus_other_Jan_pp",
             "retrospective_Tplus1_Freer_GAM_other_div_Signy_krill_model_ratio")} for r in pairs]},
         ensure_ascii=False))
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-ice",required=True,type=Path)
    p.add_argument("--source-gam",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args();output(a.out,a.source_ice,a.source_gam)
if __name__=="__main__":main()
