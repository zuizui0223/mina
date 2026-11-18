"""Five Palmer islands: independent original ERA5 1991–2020 grid separability audit.

A common 0.25-degree nearest ERA5 cell cannot identify a local island-specific
warming effect. This source audit uses NO biological outcome-dependent request.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics,sys
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"outputs/comparison_audit/palmer_site_coordinates.csv"
sys.path.insert(0,str(Path(__file__).resolve().parent))
import acquire_era5_warming_macro_v1 as era5

def rows():
    with SOURCE.open(newline="",encoding="utf-8") as f:
        a=list(csv.DictReader(f))
    assert len(a)==5
    assert {r["site_id"] for r in a}=={"CHIS","CORM","HUMB","LITC","TORG"}
    return sorted(a,key=lambda z:z["site_id"])

def valid_daily(p,years):
    d=p["daily"]
    vals=d[era5.VAR]
    dates=d["time"]
    assert len(dates)==len(vals) and dates[0]=="1991-01-01" and dates[-1]=="2020-12-31"
    assert len(dates)==10958
    assert all(v is not None and -100<float(v)<50 for v in vals)
    return dates,vals

def summarize(batch,items):
    assert len(batch)==len(items)==5
    all_rows={}
    grid_lookup={}
    for site,item in zip(batch,items):
        assert item.get("daily_units",{}).get(era5.VAR) in {"°C","C"}
        assert item.get("utc_offset_seconds")==0
        lat,lon=float(item["latitude"]),float(item["longitude"])
        assert math.isfinite(lat) and math.isfinite(lon)
        grid=(round(lat,6),round(lon,6))
        dates,values=valid_daily(item,range(1991,2021))
        grid_lookup[site["site_id"]]=grid
        all_rows[site["site_id"]]=values
    grids=set(grid_lookup.values())
    same_grid=len(grids)==1
    n=len(next(iter(all_rows.values())))
    maximum=max(max(all_rows[s][i] for s in all_rows)-min(all_rows[s][i] for s in all_rows)
                for i in range(n))
    if same_grid:
        assert maximum==0.0, "Same original ERA5 nearest cell had different daily values"
    climatology={}
    for site,p in zip(batch,items):
        dates,values=valid_daily(p,range(1991,2021))
        obs={d:float(v) for d,v in zip(dates,values)}
        monthly={str(y):statistics.mean(obs[d] for d in obs if d.startswith(f"{y}-09-"))
                 for y in (2005,2006,2007,2008)}
        climatology[site["site_id"]]={
            "source_returned_era5_grid":list(grid_lookup[site["site_id"]]),
            "september_source_years_c":monthly}
    return {
      "n_original_island_site_locations":5,
      "n_actual_era5_nearest_grids":len(grids),
      "grid_per_site":{k:list(v) for k,v in grid_lookup.items()},
      "all_five_share_identical_original_era5_source_grid":same_grid,
      "max_absolute_same_day_temperature_between_island_sites_c":maximum,
      "daily_source_day_count":n,
      "2005_2008_september_era5_source_context":climatology,
      "biological_event": "Litchfield observed nesting zero from 2007; other four monitored groups remain positive in 2017 (from separate original source)",
      "comparison_scope":"Same coarse atmospheric reanalysis exposure does not guarantee identical island microclimate/ice/prey, and its common signal cannot identify different local colony fate",
      "causal_warming_effect_fitted":False,
      "distinct_island_microclimate_exposures_measured":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    a=rows()
    url,raw,items=era5.fetch_batch(a,attempts=3)
    result={"schema":1,
        "status":"original_ERA5_grid_separability_only",
        "source_request_sha256":hashlib.sha256(raw).hexdigest(),
        "source_query_url":url,
        "source_site_coordinates_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "dataset":"Open-Meteo Historical Weather API explicit ERA5 2m mean daily grid, 1991-2020; no elevation downscaling; nearest grid",
        **summarize(a,items)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
    print("PALMER_FIVE_ISLAND_ERA5_GRID_RECEIPT="+json.dumps(result,ensure_ascii=False,allow_nan=False),flush=True)

if __name__=="__main__":main()
