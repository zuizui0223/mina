#!/usr/bin/env python3
"""Original Plantarctica mapped-class point overlay on fixed USGS Landsat8 source.

This checks the 2024-era publisher's 87391 EPSG:3031 polygons, and counts
their point-in-polygon matches at unchanged source-fixed Landsat coordinates.
No new spectral scene/date selection. Mapped plant or lichen in a 2024 composite
does NOT prove botanical vegetation in 2017-2020 or any greening trajectory.
"""
from __future__ import annotations
from collections import Counter,defaultdict
import argparse,csv,json,math,sys,tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
WORK=ROOT/"work/climate_penguin"
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(WORK))
import acquire_original_landsat8_seasonal_spectra as l8
import audit_palmer_plants_original_land_clip_v1 as plantarctica
from pyproj import Transformer
import shapefile
from shapely.geometry import Point,shape
from shapely.prepared import prep

FOCAL=("CRZW","INEX")
CLASSES=("Vegetation","Lichen","Snow Algae")
EXPECTED={"Vegetation":58740,"Lichen":24876,"Snow Algae":3775}

def csvread(p):
    with p.open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))

def csvwrite(path,rr,fields):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader();w.writerows(rr)

def source_fixed_scored_points(samples):
    """Reproduce exact broad and strict month-matched eligibility without images."""
    by=defaultdict(dict)
    for r in samples:
        site=r["site_id"]
        if site not in FOCAL or r["qa_status"]!="qa_clear_land_non_snow":
            continue
        key=(site,int(r["survey_season"]),int(r["point_id"]))
        date=r["original_scene_date"]
        if date in by[key]:
            raise ValueError("Original 150-scene cohort has duplicate date per fixed source position")
        by[key][date]=float(r["ndvi"])
    out={}
    for site,a,b in (("CRZW",2017,2018),("CRZW",2018,2019),("INEX",2018,2019)):
        summer=set();dec=set()
        for pt in range(77):
            x=by.get((site,a,pt),{})
            y=by.get((site,b,pt),{})
            if len(x)>=2 and len(y)>=2:
                summer.add(pt)
            xa=[v for date,v in x.items() if date[:7]==f"{a}-12"]
            yb=[v for date,v in y.items() if date[:7]==f"{b}-12"]
            if len(xa)>=2 and len(yb)>=2:
                dec.add(pt)
        out[(site,a,b)]={"summer":summer,"december":dec}
    if {k:len(v["summer"]) for k,v in out.items()}!={("CRZW",2017,2018):6,
        ("CRZW",2018,2019):6,("INEX",2018,2019):30}:
        raise ValueError("Original selected pair and source fixed point IDs changed")
    if len(out["INEX",2018,2019]["december"])!=13 or any(
         v["december"] for k,v in out.items() if k!=("INEX",2018,2019)):
        raise ValueError("Original strict December 13-point cohort changed")
    return out

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-folder",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    original=args.source_folder/"landsat_original_outputs"/"original_geo_point_scene_NDVI_quality.csv"
    samples=csvread(original)
    if len(samples)!=11550 or Counter(z["qa_status"] for z in samples).get("qa_clear_land_non_snow")!=983:
        raise ValueError("Source original 150-scene pixel QA cohort changed")
    for r in samples:
        pt=int(r["point_id"])
        if not 0<=pt<77 or (int(r["dx_EPSG3031_m"]),int(r["dy_EPSG3031_m"]))!=l8.GRID[pt]:
            raise ValueError("Source EPSG3031 grid shape/point_id drift")
    pairs=source_fixed_scored_points(samples)
    modern=csvread(HERE/"outputs"/"contemporary_vegetation_site_species_197.csv")
    centers={}
    for site in FOCAL:
        src={(round(float(z["latitude"]),8),round(float(z["longitude"]),8))
            for z in modern if z["site_id"]==site}
        if len(src)!=1:raise ValueError("Site coordinate mismatch between source species records")
        centers[site]=next(iter(src))
    convert=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    points={}
    for site in FOCAL:
        lat,lon=centers[site]
        cx,cy=convert.transform(lon,lat)
        points[site]=[Point(cx+dx,cy+dy) for dx,dy in l8.GRID]
    bounds={site:(
       min(p.x for p in points[site]), min(p.y for p in points[site]),
       max(p.x for p in points[site]), max(p.y for p in points[site]))
       for site in FOCAL}
    mapped={site:[set() for _ in l8.GRID] for site in FOCAL}
    hit_polygons=Counter()
    source_counts=Counter()
    raw,receipt=plantarctica.official_vegetation_zip()
    with tempfile.TemporaryDirectory(prefix="original_plantarctica_overlay-") as td:
        path=plantarctica.unpack(raw,Path(td))
        rd=shapefile.Reader(str(path))
        fields=[z[0] for z in rd.fields[1:]]
        if "Vegetation" not in fields:
            raise ValueError("Original publisher vegetation classification field not found")
        for n,sr in enumerate(rd.iterShapeRecords()):
            values=dict(zip(fields,sr.record))
            kind=str(values["Vegetation"])
            source_counts[kind]+=1
            if kind not in CLASSES:
                raise ValueError("Unknown botanical map class "+kind)
            bb=sr.shape.bbox
            if not any(not(bb[2]<b[0] or bb[0]>b[2] or bb[3]<b[1] or bb[1]>b[3])
                       for b in bounds.values()):
                continue
            geom=shape(sr.shape.__geo_interface__)
            if geom.is_empty or not geom.is_valid:
                raise ValueError("Selected original mapped vegetation geometry invalid")
            accepted=prep(geom)
            for site in FOCAL:
                b=bounds[site]
                if bb[2]<b[0] or bb[0]>b[2] or bb[3]<b[1] or bb[1]>b[3]:
                    continue
                found=False
                for i,p in enumerate(points[site]):
                    if accepted.covers(p):
                        mapped[site][i].add(kind)
                        found=True
                if found:hit_polygons[site,kind]+=1
    if dict(source_counts)!=EXPECTED or sum(source_counts.values())!=87391:
        raise ValueError("First-party original mapped feature counts/vegetation classes changed")

    point_rows=[]
    for site in FOCAL:
        for i,(dx,dy) in enumerate(l8.GRID):
            classes=mapped[site][i]
            point_rows.append({
              "site_id":site,"original_fixed_EPSG3031_point_id":i,
              "dx_EPSG3031_m":dx,"dy_EPSG3031_m":dy,
              "mapped_Plant_arctica_2024_classes":";".join(sorted(classes)),
              "is_2024_mapped_vegetation_or_lichen":bool(classes & {"Vegetation","Lichen"}),
              "is_2024_mapped_snow_algae":bool("Snow Algae" in classes),
              "is_2017to2020_biological_vegetation_confirmed":False})
    counts=[]
    for (site,ya,yb),kinds in pairs.items():
        for period in ("summer","december"):
            idx=kinds[period]
            botanical={i for i in idx if mapped[site][i] & {"Vegetation","Lichen"}}
            algae={i for i in idx if "Snow Algae" in mapped[site][i]}
            counts.append({
              "site_id":site,"first_census_season":ya,"second_census_season":yb,
              "fixed_month_qa":period,
              "n_original_same_point_two_date_each_year":len(idx),
              "n_fixed_points_in_original_Plant_arctica_2024_vegetation_or_lichen":len(botanical),
              "n_fixed_points_in_original_Plant_arctica_2024_snow_algae":len(algae),
              "static_map_is_future_to_2017_2020_censuses":True,
              "actual_plant_growth_or_greening_proven":False})
    strict=next(z for z in counts if z["site_id"]=="INEX" and
                z["first_census_season"]==2018 and z["fixed_month_qa"]=="december")
    support=strict["n_fixed_points_in_original_Plant_arctica_2024_vegetation_or_lichen"]
    status=("STATIC_PLANTARCTICA_CLASS_SUPPORT_ONLY" if support>=6 else
            "BOTANICAL_SOURCE_SUPPORT_TOO_WEAK")
    result={
      "status":status,
      "source":"Original published Plantarctica 2024-era composite, NOT 2017–2020 annual botanical field observations",
      "published_original_map_doi":receipt["doi"],
      "published_original_map_sha256":receipt["download_original_sha256"],
      "original_map_epsg":"EPSG:3031",
      "original_map_feature_counts":dict(source_counts),
      "n_source_map_polygons_hitting_any_fixed_point_by_site_class":{
        site:{kind:hit_polygons[site,kind] for kind in CLASSES} for site in FOCAL},
      "n_fixed_original_Landsat8_points_by_site":77,
      "n_sites_overlaid":len(FOCAL),
      "n_2017to2020_original_summer_NDVI_yearpairs":3,
      "n_strict_same_month_inexpressible_island_source_points":13,
      "n_strict_same_month_points_mapped_as_plant_or_lichen_in_2024":support,
      "n_strict_same_month_points_mapped_as_snow_algae_in_2024":strict["n_fixed_points_in_original_Plant_arctica_2024_snow_algae"],
      "n_all_77_points_with_2024_botanical_map_at_Crozier":sum(bool(z & {"Vegetation","Lichen"}) for z in mapped["CRZW"]),
      "n_all_77_points_with_2024_botanical_map_at_Inexpressible":sum(bool(z & {"Vegetation","Lichen"}) for z in mapped["INEX"]),
      "interpretation":"Even mapped 2024 vegetation/lichen does not prove 2017–2020 live plant-cover change. Unmapped at 400m sampled point does not demonstrate true absence of vegetation.",
      "no_new_annual_warming_vegetation_penguin_effect":True
    }
    csvwrite(args.out/"original_fixed_154point_Plant_arctica_mapped_class.csv",point_rows,list(point_rows[0]))
    csvwrite(args.out/"summer_vs_December_original_mapped_botanical_QA.csv",counts,list(counts[0]))
    (args.out/"original_Plant_arctica_polygon_overlap.json").write_text(
         json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("ORIGINAL_BOTANICAL_SOURCE_POINT_GATE="+json.dumps(result,ensure_ascii=False),flush=True)
if __name__=="__main__":
    main()
