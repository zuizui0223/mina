"""Original same-GPS-day daily SIC at FIXED native 25km ocean pixels.

A retrospective geography standardization: for each island, choose source
GPS-visited pixel footprints (all dates, December-only, January-only), then
hold the ORIGINAL pixel IDs fixed across 14 days and retain only cells
observed as marine with valid satellite SIC on EVERY day. Daily 24h ice
change at those fixed cells is not penguin passage or prey capture.
"""
from __future__ import annotations
import argparse,csv,json,hashlib,math
from collections import defaultdict
from pathlib import Path
import numpy as np
import xarray as xr
import chinstrap_daily_ice_same_day_GPS_2013_v1 as original

PHASES=("all_14_source_GPS_days","Dec_2013_source_GPS_only","Jan_2014_source_GPS_only")
ISLANDS=("SI","PI")
SOURCE_DAY_N=14

def read_csv(file):
    with Path(file).open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def baseline(tag_rows,receipts,root):
    originals={r["date"]:r for r in receipts["source_original_daily_netcdfs"]}
    if len(originals)!=SOURCE_DAY_N:
        raise ValueError("Expected original 14 day source NetCDF files")
    days=sorted(originals)
    if days[0]!="20131229" or days[-1]!="20140111":
        raise ValueError("Source GPS calendar day baseline changed")
    masks={}
    data={}
    coordinate_hash={}
    for day in days:
        src=root/originals[day]["file"]
        f=original.open_day(src,originals[day])
        masks[day]=set(map(int,f["all_ids"].tolist()))
        data[day]=f["values"]
        # Source native 25 km coordinate geometry fixed, not nearest mapped
        # locations that silently change with the ice field.
        with xr.open_dataset(src) as ds:
            lat=np.asarray(ds["lat"].values,dtype="float64")
            lon=np.asarray(ds["lon"].values,dtype="float64")
        coordinate_hash[day]=hashlib.sha256(lat.tobytes()+lon.tobytes()).hexdigest()
    if len(set(coordinate_hash.values()))!=1:
        raise ValueError("Daily original 25-km satellite native grid coordinates changed")
    valid_all=set.intersection(*(masks[d] for d in days))
    tags=defaultdict(set)
    for row in tag_rows:
        if row["max_source_pixel_distance_km"]!="20.0" or row["strict_ice_quality"]!="False":
            continue
        island=row["island"]
        if island not in ISLANDS:continue
        day=row["calendar_date"]
        vals=json.loads(row["original_pixel_values_json"])
        for pix in vals:
            tags[island,"all_14_source_GPS_days"].add(int(pix))
            tagphase="Dec_2013_source_GPS_only" if day.startswith("201312") else "Jan_2014_source_GPS_only"
            tags[island,tagphase].add(int(pix))
    fixed={}
    for island in ISLANDS:
        for phase in PHASES:
            ids=sorted(tags[island,phase]&valid_all)
            if len(ids)<2:
                raise ValueError(f"Insufficient fixed valid satellite native pixels: {island},{phase}")
            fixed[island,phase]=ids
    perday=[]
    for day in days:
        for island in ISLANDS:
            for phase in PHASES:
                pix=fixed[island,phase]
                vals=[float(data[day][i]) for i in pix]
                if any(not math.isfinite(v) or not 0<=v<=100.0001 for v in vals):
                    raise ValueError("Invalid daily ocean SIC at original fixed pixel")
                perday.append({
                    "source_day":day,"island":island,
                    "source_GPS_footprint_definition":phase,
                    "n_distinct_native_ocean_cells_FIXED_all_14days":len(pix),
                    "daily_original_SIC_percent_at_FIXED_pixels":float(np.mean(vals)),
                    "n_original_FIXED_pixels_daily_SIC_ge15":sum(v>=15 for v in vals),
                    "source_native_grid_SHA256":coordinate_hash[day],
                    "same_grid_cells_across_dates":True,
                    "original_SIC_24h_satellite_mean_not_daytime_ice_access":True
                })
    look={(r["source_day"],r["island"],r["source_GPS_footprint_definition"]):r for r in perday}
    pairs=[]
    for day in days:
        for phase in PHASES:
            a=look[day,"SI",phase]
            b=look[day,"PI",phase]
            pairs.append({
                "same_calendar_day":day,"source_fixed_footprint":phase,
                "n_Signy_same_daily_cells":a["n_distinct_native_ocean_cells_FIXED_all_14days"],
                "n_Powell_same_daily_cells":b["n_distinct_native_ocean_cells_FIXED_all_14days"],
                "Signy_fixed_pixel_daily_SIC_percent":a["daily_original_SIC_percent_at_FIXED_pixels"],
                "Powell_fixed_pixel_daily_SIC_percent":b["daily_original_SIC_percent_at_FIXED_pixels"],
                "Signy_minus_Powell_fixed_cell_SIC_pp":a["daily_original_SIC_percent_at_FIXED_pixels"]-b["daily_original_SIC_percent_at_FIXED_pixels"],
                "source_grid_native_pixels_not_independent_temporal_sampling":True
            })
    grouped=[]
    for phase in PHASES:
        for island in ISLANDS:
            for window,prefix in (("2013-12","201312"),("2014-01","201401")):
                matches=[r for r in perday if r["source_GPS_footprint_definition"]==phase
                        and r["island"]==island and r["source_day"].startswith(prefix)]
                grouped.append({
                    "source_fixed_footprint":phase,"island":island,"period":window,
                    "n_actual_shared_GPS_days_in_period":len(matches),
                    "n_distinct_original_ocean_pixels_fixed_across_14_days":
                        len(fixed[island,phase]),
                    "source_daily_ice_mean_on_constant_pixel_set_percent":float(np.mean(
                        [r["daily_original_SIC_percent_at_FIXED_pixels"] for r in matches])),
                    "native_pixels_independent_of_day_by_original_source_grid":True
                })
    summary={}
    for phase in PHASES:
        by={(r["island"],r["period"]):r for r in grouped if r["source_fixed_footprint"]==phase}
        dec=by["SI","2013-12"]["source_daily_ice_mean_on_constant_pixel_set_percent"]-by["PI","2013-12"]["source_daily_ice_mean_on_constant_pixel_set_percent"]
        jan=by["SI","2014-01"]["source_daily_ice_mean_on_constant_pixel_set_percent"]-by["PI","2014-01"]["source_daily_ice_mean_on_constant_pixel_set_percent"]
        summary[phase]={"December_Signy_minus_Powell_pp":dec,
                        "January_Signy_minus_Powell_pp":jan,
                        "change_in_site_ice_contrast_Dec_to_Jan_pp":jan-dec,
                        "Signy_original_fixed_cells":len(fixed["SI",phase]),
                        "Powell_original_fixed_cells":len(fixed["PI",phase])}
    if len(perday)!=14*2*3 or len(pairs)!=14*3 or len(grouped)!=3*2*2:
        raise ValueError("Fixed original source day footprint rows incomplete")
    result={
      "status":"FIXED_ORIGINAL_SATELLITE_OCEAN_CELLS_SHOW_SOURCE_DAILY_SIC_CHANGE_NOT_BIRD_LOCATION_CHANGE",
      "source_original_GPS_DOI":original.GPS_DOI,"source_original_ice_DOI":original.DOI,
      "original_source_day_N":len(days),
      "original_SIC_daily_NetCDF_SHAs":{r["date"]:r["sha256"] for r in originals.values()},
      "original_25km_grid_fixed_latlon_SHA256":list(coordinate_hash.values())[0],
      "original_ocean_pixels_valid_on_all_14_days":len(valid_all),
      "source_footprints_defined_from_GPS_dates_before_daily_SIC_values":True,
      "fixed_footprint_analysis":summary,
      "no_daily_ice_navigability_or_causal_breeding_response_tested":True,
      "warnings":[
        "GPS sets are source-fixed but chosen posthoc 2013 island case; not a novel heldout island-year replicate.",
        "Same valid original satellite ocean pixels are re-used on all 14 days, but spatial autocorrelation and coastline/microwave footprint remain.",
        "A retrospective fixed GPS footprint depends on all GPS dates and valid satellite pixels, not a preregistered foraging opportunity polygon.",
        "Concentration is a 24h average, not impenetrable sea ice at an exact penguin GPS timestamp.",
        "This differentiates bird relocation from source-pixel temporal ice concentration changes but not ice-to-food or breeding causal paths.",
        "No 2050/2100 penguin breeding pairs, patch N_eff or vegetation outcome predictions."
      ]}
    return perday,pairs,grouped,result

def save(path,rows):
    with Path(path).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-tag-day",required=True,type=Path)
    p.add_argument("--receipt",required=True,type=Path)
    p.add_argument("--daily-dir",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    data,paired,summary,decision=baseline(
        read_csv(a.source_tag_day),json.loads(a.receipt.read_text()),a.daily_dir)
    a.out.mkdir(parents=True,exist_ok=True)
    save(a.out/"source_same_native_pixels_daily_SIC.csv",data)
    save(a.out/"source_fixed_pixel_Signy_vs_Powell_by_day.csv",paired)
    save(a.out/"source_fixed_pixel_season_summary.csv",summary)
    (a.out/"decision.json").write_text(json.dumps(decision,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":decision["status"],"main":decision["fixed_footprint_analysis"],
                      "source_day_N":decision["original_source_day_N"]},ensure_ascii=False))

if __name__=="__main__":main()
