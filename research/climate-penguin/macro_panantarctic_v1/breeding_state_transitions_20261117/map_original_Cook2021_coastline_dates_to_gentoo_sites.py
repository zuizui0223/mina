#!/usr/bin/env python3
"""Actual Cook/Fox/Thomson (2021) original Antarctic Peninsula coastline LINE
feature census within 2/5km of MAPPPD Gentoo source appearance clusters.

Uses 13,436 original coastal line segments (ESRI shapefile EPSG:3031), each
with 'coast_type', 'year', 'reliabilit', and 'source_inf'. Official ADD coast
codes 22010=definite ice coast, 22011=definite rock coast, etc.
A coast line (even rock coastline) does NOT map interior bare-rock area,
glacier ice volume, or exact biological colony founding. Changes in number of
mapped lines often reflect survey effort and source footprints, not ecology.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,io,json,zipfile
from pathlib import Path

SITES={
 "BISC":{"lon":-63.7775,"lat":-64.8114,"zero":1984,"positive":1994},
 "ORNE":{"lon":-62.673,"lat":-64.662,"zero":1998,"positive":1999},
 "GALINDEZ":{"lon":-64.2399,"lat":-65.2476,"zero":1999,"positive":2007}
}
RADII=(2,5)
COAST_CLASSES={
"22010":"definite_ice_coast",
"22011":"definite_rock_coast",
"22012":"definite_grounding_line",
"22013":"rock_against_ice_shelf",
"22020":"approx_ice_wall",
"22021":"approx_rock_coast",
"22022":"approx_grounding_line",
"22023":"approx_rock_against_ice_shelf",
"22030":"iceberg_tongue",
"22040":"floating_glacier_tongue",
"22050":"ice_shelf_front",
}
def run(source_zip,out):
    import shapefile
    from pyproj import Transformer
    from shapely.geometry import shape,Point
    out.mkdir(parents=True,exist_ok=True)
    data=source_zip.read_bytes()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        assert z.testzip() is None
        base="Coastal_Change_line"
        # Archive member basename case is fixed by genuine publisher retrieval.
        names={n.lower():n for n in z.namelist()}
        get=lambda ext:z.read(names[(base+ext).lower()])
        r=shapefile.Reader(
            shp=io.BytesIO(get(".shp")),
            shx=io.BytesIO(get(".shx")),
            dbf=io.BytesIO(get(".dbf")),
            encoding="latin1")
        wkt=get(".prj").decode(errors="replace")
        assert len(r)==13436
        # EPSG3031 source archive field is titled EPSG and its source WKT
        # MUST be Antarctic polar stereographic. Avoid silent crs guessing.
        assert "antarctic" in wkt.lower() or "polar" in wkt.lower(),wkt[:180]
        fields=[f[0] for f in r.fields[1:]]
        assert set(("gid","coast_type","year","reliabilit","source_inf")).issubset(fields)
        t=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
        centers={k:Point(*t.transform(v["lon"],v["lat"])) for k,v in SITES.items()}
        maxB={k:c.buffer(5000,resolution=64) for k,c in centers.items()}
        rows=[]
        # Build geometry ONLY for lines whose original EPSG3031 bbox touches
        # one of three local target 5km source windows.
        scanned_bbox=0
        for i in range(len(r)):
            s=r.shape(i)
            bbox=s.bbox
            locs=[k for k,b in maxB.items()
                  if not (bbox[2]<b.bounds[0] or bbox[0]>b.bounds[2]
                      or bbox[3]<b.bounds[1] or bbox[1]>b.bounds[3])]
            if not locs:continue
            scanned_bbox+=1
            geom=shape(s.__geo_interface__)
            row=dict(zip(fields,r.record(i)))
            for k in locs:
                distance=float(geom.distance(centers[k])/1000)
                if distance>5+1e-6:continue
                year=int(row["year"])
                coastcode=str(row["coast_type"])
                rows.append({
                    "site_cluster":k,"source_feature_ID":str(row["gid"]),
                    "source_year":year,"revision_date_field":str(row.get("revdate","")),
                    "source_coast_type":coastcode,
                    "source_coast_category":COAST_CLASSES.get(coastcode,"unrecognized_code"),
                    "source_reliability_class":str(row["reliabilit"]),
                    "nearest_coastline_distance_to_source_site_km":distance,
                    "source_editor":str(row.get("editor","")),
                    "source_reference":str(row.get("reference","")),
                    "source_original_information":str(row.get("source_inf",""))[:250],
                    "before_or_on_last_zero_census":year<=SITES[k]["zero"],
                    "between_source_census_zero_and_first_positive":SITES[k]["zero"]<year<SITES[k]["positive"],
                    "on_or_after_first_source_positive":year>=SITES[k]["positive"],
                    "no_true_rock_area_or_colony_occupation_estimated":True
                })
        r.close()
    outrows=sorted(rows,key=lambda x:(x["site_cluster"],x["source_year"],
                                      x["nearest_coastline_distance_to_source_site_km"]))
    with (out/"Cook2021_original_coast_features_within5km.csv").open("w",newline="") as f:
        fields=list(outrows[0]) if outrows else ["site_cluster"]
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(outrows)
    summary=[]
    for k in SITES:
        for radius in RADII:
            selected=[x for x in outrows if x["site_cluster"]==k
                      and x["nearest_coastline_distance_to_source_site_km"]<=radius]
            years=collections.Counter(x["source_year"] for x in selected)
            types=collections.Counter(x["source_coast_category"] for x in selected)
            before=sum(x["before_or_on_last_zero_census"] for x in selected)
            middle=sum(x["between_source_census_zero_and_first_positive"] for x in selected)
            after=sum(x["on_or_after_first_source_positive"] for x in selected)
            summary.append({
             "site_cluster":k,"radius_km":radius,
             "source_last_recorded_zero_year":SITES[k]["zero"],
             "source_first_positive_year":SITES[k]["positive"],
             "n_original_coastline_features":len(selected),
             "n_distinct_source_years":len(years),
             "all_source_years":sorted(years),
             "n_segments_before_or_on_last_zero":before,
             "n_segments_strictly_within_census_interval":middle,
             "n_segments_on_or_after_first_positive":after,
             "year_segment_counts":dict(sorted(years.items())),
             "coast_type_counts":dict(sorted(types.items())),
             "has_any_definite_rock_coast":any(x["source_coast_category"]=="definite_rock_coast" for x in selected),
             "has_any_definite_ice_coast":any(x["source_coast_category"]=="definite_ice_coast" for x in selected),
             "not_a_real_colony_foundation_year":True,
             "coastal_front_line_not_annual_terrestrial_available_habitat":True})
    assert len(summary)==6
    rec={
      "status":"PASS_AUTHENTIC_COOK_2021_GLACIER_COASTLINE_SITEYEAR_SOURCE_GRAIN",
      "source_archive_sha256":hashlib.sha256(data).hexdigest(),
      "n_publisher_original_feature_rows":13436,
      "n_original_features_screened_by_local_bbox":scanned_bbox,
      "n_original_site_proximal_feature_joins_within5km":len(outrows),
      "original_source_crs":"EPSG:3031 Antarctic polar stereographic from ZIP WKT",
      "n_original_site_clusters":len(SITES),
      "results":summary,
      "no_annual_rock_opportunity_estimate":True,
      "never_impute_unsurveyed_glacier_years":True,
      "coast_type_official_dictionary":"BAS ADD User Guide / SCAR coast codes",
      "not_a_counterfactual_true_unoccupied_breeding_patch_design":True,
      "not_causal_ice_retreat_or_colony_colonization_rate":True}
    (out/"Cook2021_official_coastline_local_year_support_receipt.json").write_text(
        json.dumps(rec,ensure_ascii=False,indent=2)+"\n")
    print("COOK2021_COASTLINE_SITE_SUPPORT="+json.dumps(
     {"status":rec["status"],"n_local_segments":len(outrows),
      "results":summary},ensure_ascii=False),flush=True)

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--original-source-zip",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    v=a.parse_args();run(v.original_source_zip,v.out)
