#!/usr/bin/env python3
"""Original QA-only common-location gate for January 2007/2008 at Palmer.

Samples both years at EXACTLY the same EPSG:3031 fixed 25 locations.
Source scene choice depends solely on QA-valid land pixels, not NDVI or
inferred greening. It does not trace historical nesting polygon boundaries.
"""
from __future__ import annotations
import argparse
import csv
import importlib.util
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("original_local_qa", HERE / "palmer_landsat_local_qa_pilot.py")
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)
YEARS = (2007, 2008)
OFFSETS_M = [(dx,dy) for dx in qa.GRID_M for dy in qa.GRID_M]


def sample_grid(ds, loc):
    from pyproj import Transformer
    from_4326 = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
    to_native = Transformer.from_crs("EPSG:3031", ds.crs, always_xy=True)
    x0, y0 = from_4326.transform(loc["longitude"], loc["latitude"])
    coords = [to_native.transform(x0 + dx, y0 + dy) for dx,dy in OFFSETS_M]
    out = []
    for idx, (pt, value) in enumerate(zip(coords, ds.sample(coords, masked=True))):
        mask = getattr(value, "mask", False)
        masked = bool(mask.any()) if hasattr(mask, "any") else bool(mask)
        row,col = ds.index(*pt)
        if masked or not (0 <= row < ds.height and 0 <= col < ds.width):
            out.append({"i":idx,"r":row,"c":col,"qa":None,"clear":False,"status":"masked"})
        else:
            bits = int(value[0])
            out.append({"i":idx,"r":row,"c":col,"qa":bits,
                        "clear":qa.clear_land_qa(bits),"status":"valid"})
    return out


def choose_best_pair(images_2007, images_2008):
    """Full pair catalogue; choose largest common QA-set, then nearest month-day."""
    pairs = []
    for a in images_2007:
        for b in images_2008:
            if a["status"] != "ok" or b["status"] != "ok":
                continue
            common = sorted(set(a["clear_points"]) & set(b["clear_points"]))
            day_a = datetime.strptime("2000-" + a["date"][5:10], "%Y-%m-%d").timetuple().tm_yday
            day_b = datetime.strptime("2000-" + b["date"][5:10], "%Y-%m-%d").timetuple().tm_yday
            pairs.append({
                "before_id":a["item_id"],"after_id":b["item_id"],
                "before_date":a["date"],"after_date":b["date"],
                "before_clear_points":len(a["clear_points"]),
                "after_clear_points":len(b["clear_points"]),
                "same_grid_clear_points":len(common),
                "indices":common,"calendar_day_gap":abs(day_b-day_a),
            })
    pairs.sort(key=lambda x:(-x["same_grid_clear_points"],x["calendar_day_gap"],x["before_date"],x["after_date"],x["before_id"],x["after_id"]))
    return pairs


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,default=Path("palmer_january_common_points"))
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    import rasterio
    import planetary_computer
    samples, scenes=[],[]
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",GDAL_HTTP_MAX_RETRY="2",GDAL_HTTP_RETRY_DELAY="1"):
        for year in YEARS:
            for feature in qa.fetch_all(year,month=1):
                aid=feature["id"]
                date=feature["properties"]["datetime"][:10]
                cloud=feature["properties"].get("eo:cloud_cover")
                href=feature.get("assets",{}).get("qa_pixel",{}).get("href")
                for site,loc in qa.mod.SITES.items():
                    base={"site_id":site,"year":year,"item_id":aid,"date":date,
                          "scene_cloud":cloud,"status":"error","error":"","clear_points":[]}
                    try:
                        if not href:raise ValueError("missing qa_pixel")
                        with rasterio.open(planetary_computer.sign(href)) as ds:
                            arr=sample_grid(ds,loc)
                        base["status"]="ok"
                        base["clear_points"]=[p["i"] for p in arr if p["clear"]]
                        for p in arr:
                            samples.append({"site_id":site,"year":year,"item_id":aid,"date":date,
                                            "point_index":p["i"],"offset_x_m":OFFSETS_M[p["i"]][0],
                                            "offset_y_m":OFFSETS_M[p["i"]][1],
                                            "native_row":p["r"],"native_col":p["c"],
                                            "qa_value":p["qa"] if p["qa"] is not None else "",
                                            "clear_land":p["clear"],"pixel_status":p["status"]})
                    except Exception as e:base["error"]=f"{type(e).__name__}: {str(e)[:220]}"
                    scenes.append(base)
    pairs_all=[]; summary={}
    for site in qa.mod.SITES:
        earlier=[x for x in scenes if x["site_id"]==site and x["year"]==2007]
        later=[x for x in scenes if x["site_id"]==site and x["year"]==2008]
        pairs=choose_best_pair(earlier,later)
        best=pairs[0] if pairs else None
        for j,p in enumerate(pairs):
            pairs_all.append({**{k:v for k,v in p.items() if k!="indices"},
                              "site_id":site,"rank":j+1,"selected":j==0,"common_indices_json":json.dumps(p["indices"])})
        summary[site]={
            "before_scenes":len(earlier),"after_scenes":len(later),
            "successful_before":sum(x["status"]=="ok" for x in earlier),
            "successful_after":sum(x["status"]=="ok" for x in later),
            "qa_pair_count":len(pairs),
            "selected_by_qa_only":best,
            "at_least_one_common_clear_point":bool(best and best["same_grid_clear_points"]>0),
        }
    def writer(name,records,fields):
        with (args.out/name).open("w",encoding="utf-8",newline="") as fh:
            wr=csv.DictWriter(fh,fieldnames=fields); wr.writeheader();wr.writerows(records)
    writer("source_scene_site.csv",[
        {k:(json.dumps(v) if k=="clear_points" else v) for k,v in s.items()} for s in scenes],
        ["site_id","year","item_id","date","scene_cloud","status","error","clear_points"])
    writer("fixed_sample_qa.csv",samples,["site_id","year","item_id","date","point_index",
        "offset_x_m","offset_y_m","native_row","native_col","qa_value","clear_land","pixel_status"])
    writer("all_qa_scene_pairs.csv",pairs_all,["site_id","rank","selected","before_id",
        "after_id","before_date","after_date","before_clear_points","after_clear_points",
        "same_grid_clear_points","calendar_day_gap","common_indices_json"])
    checks={
        "source":"original Planetary Computer Landsat C2 Level 2, original QA_PIXEL",
        "time_window":"January 2007 and January 2008 (post-hoc observation-support only)",
        "grid_definition":"EPSG:3031 exactly 25 centers at ±80,±40,0 metres around three MAPPPD centroids",
        "source_assets_read":Counter(x["status"] for x in scenes),
        "total_qa_fixed_point_records":len(samples),
        "selection_rule":"all 2007x2008 scene combinations; maximum common QA-clear fixed points; tie nearest Julian calendar day then lexicographic scene/date",
        "outcomes_not_accessed":["NDVI","surface reflectance","vegetation class","historic colony polygons"],
        "summary":summary,
        "limitations":[
          "Same coordinate point does NOT prove the two native 30m pixel footprints are identical",
          "Nearby site-coordinate grid is NOT a mapped historic breeding colony",
          "Only 25 QA probes per registered island coordinate; no evidence for island-wide vegetation",
          "The January support window was added after the original February-March window failed",
          "QA-clear land does not imply any vegetation is present",
        ],
    }
    (args.out/"checks.json").write_text(json.dumps(checks,indent=2,default=dict)+"\n")
    print(json.dumps(summary,indent=2,default=dict),flush=True)
    return 2 if any(x["status"]!="ok" for x in scenes) else 0


if __name__=="__main__":raise SystemExit(main())
