"""Same-sensor, original QA-only eligibility for historical Palmer points on physical islands.

Never fits an NDVI response, climate effect, or island-colony greening mechanism.
Uses frozen source QA and exact first-party SCAR coastline polygon IDs.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,math,sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import Point

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
source=HERE.parent/"climate_penguin/audit_palmer_original_island_rock_v1.py"
spec=importlib.util.spec_from_file_location("palmer_original_land",source)
land=importlib.util.module_from_spec(spec);spec.loader.exec_module(land)

SITES=("LITC","HUMB","TORG")
SOURCE_LAND_FIDS={"LITC":5475,"HUMB":5496,"TORG":5504}
OFFSETS=(-80,-40,0,40,80)
PRE=tuple(range(2003,2008))
POST=tuple(range(2009,2014))
SENSOR="LE07"
MIN_YEARS=3
MIN_SAME_POINTS=5

def read_csv(path):
    with Path(path).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))

def checksum(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def matches_site(item, site, polys):
    cls=land.classify(item,polys)
    if cls["category"]!="EXACT_ONE_ORIGINAL_MAPPED_LAND_POLYGON":raise ValueError("source geometry not exact")
    if cls["original_land_fid"]!=SOURCE_LAND_FIDS[site]:
        raise ValueError("official mapped-land FID identity drift")
    return cls

def nonleap_day(d):
    dt=date.fromisoformat(d)
    mm,dd=dt.month,dt.day
    if (mm,dd)==(2,29):return 60
    return (date(2001,mm,dd)-date(2001,1,1)).days+1

def choose(rows,mask):
    eligible=[]
    for r in rows:
        if r.get("status")!="ok" or not r["item_id"].startswith(SENSOR+"_"):continue
        year=int(r["image_year"])
        if year not in PRE+POST:continue
        if not r["clear_25_bit_mask"]:continue
        good=int(r["clear_25_bit_mask"])&mask
        n=good.bit_count()
        if n<1:continue
        day=nonleap_day(r["date"])
        if day<32 or day>90:continue
        eligible.append({**r,"selected_island_clear_mask":good,
                         "selected_island_clear_points":n,
                         "march1_day_gap":abs(day-60)})
    # Stable selection within a *single* biological site/year independent of
    # red/NIR reflectance. A source duplicate item ID is not an independent scene.
    by_year=defaultdict(list)
    for x in eligible:by_year[int(x["image_year"])].append(x)
    output=[]
    for year,items in sorted(by_year.items()):
        ids=[z["item_id"] for z in items]
        if len(ids)!=len(set(ids)):raise ValueError("duplicated original QA scene ID")
        item=sorted(items,key=lambda z:(-z["selected_island_clear_points"],z["march1_day_gap"],z["item_id"]))[0]
        output.append(item)
    return output

def physical_land_masks(site_rows):
    proj=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    points={}
    for r in site_rows:
        x,y=proj.transform(float(r["longitude"]),float(r["latitude"]))
        points[r["site_id"]]=Point(x,y)
    blob=land.original_publisher_zip()
    import tempfile
    with tempfile.TemporaryDirectory(prefix="palmer-le07-coast-") as temp:
        shp=land.unpack(blob,Path(temp))
        polygons,geo=land.geometry_source_candidates(shp,points)
    by_fid=dict(polygons)
    masks={}
    for r in site_rows:
        sid=r["site_id"]
        matches_site(points[sid],sid,polygons)
        geom=by_fid[SOURCE_LAND_FIDS[sid]]
        x,y=points[sid].x,points[sid].y
        masks[sid]=sum((1<<i) for i,(dy,dx) in enumerate(
            (a,b) for a in OFFSETS for b in OFFSETS)
            if geom.covers(Point(x+dx,y+dy)))
    return masks,checksum(SITE_SOURCE),hashlib.sha256(blob).hexdigest()

SITE_SOURCE=ROOT/"outputs/comparison_audit/palmer_site_coordinates.csv"

def support(selected,mask):
    periods={}
    for label,years in (("pre",PRE),("post",POST)):
        part=[r for r in selected if int(r["image_year"]) in years]
        flags=[sum(bool(r["selected_island_clear_mask"]&(1<<i)) for r in part) for i in range(25)]
        periods[label]={"years":len(part),"available_calendar_years":[int(r["image_year"]) for r in part],
                        "fixed_position_observed_years":flags}
    fixed=[i for i in range(25)
           if bool(mask&(1<<i)) and
           periods["pre"]["fixed_position_observed_years"][i]>=MIN_YEARS and
           periods["post"]["fixed_position_observed_years"][i]>=MIN_YEARS]
    passes=(len(fixed)>=MIN_SAME_POINTS and
            periods["pre"]["years"]>=MIN_YEARS and periods["post"]["years"]>=MIN_YEARS)
    return {"pre":periods["pre"],"post":periods["post"],
            "source_fixed_points_inside_original_land":mask.bit_count(),
            "same_fixed_points_3pre_3post":fixed,
            "same_fixed_point_count":len(fixed),
            "passes_site_source_gate":passes}

def execute(annual):
    site_rows=[r for r in read_csv(SITE_SOURCE) if r["site_id"] in SITES]
    assert len(site_rows)==len(SITES)
    masks,coordinates_sha,source_sha=physical_land_masks(site_rows)
    rows=read_csv(annual/"local_qa_scenes.csv")
    years=read_csv(annual/"local_qa_years.csv")
    checks=json.loads((annual/"checks.json").read_text())
    assert checks["sites"]==list(SITES)
    assert checks["grid_offsets_m"]==list(OFFSETS)
    assert checks["first_calendar_image_year"]<=2003 and checks["last_calendar_image_year"]>=2013
    assert checks["source_qa_errors"]==0
    assert len({(r["site_id"],r["image_year"]) for r in years})==len(years)
    assert all(s in SITES for s in {r["site_id"] for r in rows})
    selected=[]
    summary={}
    for site in SITES:
        ss=choose([r for r in rows if r["site_id"]==site],masks[site])
        result=support(ss,masks[site])
        summary[site]=result
        for r in ss:
            selected.append({"site_id":site,
                             "image_year":r["image_year"],
                             "breeding_season_start_year":r["breeding_season_start_year"],
                             "item_id":r["item_id"],"date":r["date"],
                             "clear_25_bit_mask_original":r["clear_25_bit_mask"],
                             "strict_island_clear_mask":r["selected_island_clear_mask"],
                             "strict_island_clear_points":r["selected_island_clear_points"],
                             "qa_only_selection":True})
    ready=summary["LITC"]["passes_site_source_gate"] and any(
        summary[s]["passes_site_source_gate"] for s in ("HUMB","TORG"))
    return selected,{"schema":1,
       "status":"source_temporal_spatial_L7_eligibility_only",
       "original_annual_QA_sha256":checksum(annual/"local_qa_scenes.csv"),
       "original_annual_check_sha256":checksum(annual/"checks.json"),
       "original_site_coords_sha256":coordinates_sha,
       "SCAR_original_coast_sha256":source_sha,
       "annual_qa_run":40863960933,
       "source_sensor":SENSOR,"source_months":[2,3],
       "source_pre_image_years":list(PRE),"source_post_image_years":list(POST),
       "source_month_alignment":"Feb-Mar image Y follows breeding season Y-1",
       "original_land_fid":SOURCE_LAND_FIDS,
       "support":summary,
       "LITC_and_any_control_pass":ready,
       "spectral_change_measured":False,
       "nest_polygon_measured":False,
       "no_threshold_rescue":True,
       "next":"If pass, read exactly these pre-QA-selected reflectance scenes at physical-land-contained fixed positions, without changing the roster. If fail, STOP."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--annual-QA-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    rows,receipt=execute(args.annual_QA_dir)
    with (args.out/"selected_L7_QA_island_years.csv").open("w",newline="",encoding="utf-8") as f:
        fields=["site_id","image_year","breeding_season_start_year","item_id","date",
                "clear_25_bit_mask_original","strict_island_clear_mask",
                "strict_island_clear_points","qa_only_selection"]
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    (args.out/"source_only_gate.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print("PALMER_L7_ANNUAL_SOURCE_GATE="+json.dumps(receipt,ensure_ascii=False),flush=True)
    return 0

if __name__=="__main__":raise SystemExit(main())
