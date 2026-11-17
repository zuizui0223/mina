#!/usr/bin/env python3
"""Source-vintage duplication test of the 1989 and 1998 mapped ice/rock
coastline around original penguin site Biscoe Point.

The Cook/Fox/Thomson 2021 archive contains line fragments from different
publication/source dates. Equal minimal site-to-coast distances across
1989 and 1998 could be genuine fixed shoreline or repeated digitized
geometry. This script tests exact identical WKB-normalized local line
features, geometry overlay, and class-matched common line length.
It does NOT estimate a glacier front velocity or created nesting area.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,zipfile
from pathlib import Path
from collections import defaultdict

SOURCE_SHA256="cd17b91692d2f110acbe84553b950161f03f3e4c01c0d622ffaca1682af972d4"
ORIGINAL_SITE=(-63.7775,-64.8114)
YEARS=(1989,1998)
COAST_CLASSES={"22010":"ice_coast","22011":"rock_coast"}
RADIUS_KM=2

def compute(sourcezip):
    import shapefile
    from shapely.geometry import Point,shape
    from shapely.ops import unary_union
    from pyproj import Transformer
    data=sourcezip.read_bytes()
    assert hashlib.sha256(data).hexdigest()==SOURCE_SHA256
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names={n.lower():n for n in z.namelist()}
        get=lambda x:z.read(names[("coastal_change_line"+x).lower()])
        r=shapefile.Reader(shp=io.BytesIO(get(".shp")),shx=io.BytesIO(get(".shx")),
                           dbf=io.BytesIO(get(".dbf")),encoding="latin1")
        assert len(r)==13436
        fields=[x[0] for x in r.fields[1:]]
        cx,cy=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True).transform(*ORIGINAL_SITE)
        center=Point(cx,cy)
        area=center.buffer(RADIUS_KM*1000,resolution=96)
        base=[]
        for i in range(len(r)):
            obj=r.shape(i)
            bounds=obj.bbox
            bounds2=area.bounds
            if bounds[2]<bounds2[0] or bounds[0]>bounds2[2] or bounds[3]<bounds2[1] or bounds[1]>bounds2[3]:
                continue
            row=dict(zip(fields,r.record(i)))
            yr=int(row["year"]);coast=str(row["coast_type"])
            if yr not in YEARS or coast not in COAST_CLASSES:continue
            geom=shape(obj.__geo_interface__)
            local=geom.intersection(area)
            if local.is_empty or local.length==0:continue
            base.append({
                "year":yr,"class":COAST_CLASSES[coast],
                "gid":str(row["gid"]),
                "near_km":float(geom.distance(center)/1000.),
                "geometric_length_in2km_km":float(local.length/1000.),
                "normalized_shape_hash":hashlib.sha256(local.normalize().wkb).hexdigest(),
                "geometry":local,
            })
        r.close()
    by=defaultdict(list)
    for x in base:by[x["class"],x["year"]].append(x)
    out=[];features=[]
    for cls in ("ice_coast","rock_coast"):
        old=by[cls,YEARS[0]];new=by[cls,YEARS[1]]
        union_old=unary_union([v["geometry"] for v in old])
        union_new=unary_union([v["geometry"] for v in new])
        exacts=[]
        for a in old:
            for b in new:
                if a["geometry"].equals(b["geometry"]):
                    exacts.append({"class":cls,"gid_1989":a["gid"],"gid_1998":b["gid"],
                                   "exactly_same_local_geometry":True,
                                   "same_source_feature_ID":a["gid"]==b["gid"],
                                   "duplicated_line_km":a["geometric_length_in2km_km"]})
        shared=union_old.intersection(union_new)
        common=float(shared.length/1000.)
        a0=float(union_old.length/1000.)
        a1=float(union_new.length/1000.)
        out.append({
            "coast_class":cls,
            "n_original_1989_features":len(old),
            "n_original_1998_features":len(new),
            "n_exact_identical_cross_year_feature_pairs":len(exacts),
            "n_old_features_identical_to_any_1998":len({d["gid_1989"] for d in exacts}),
            "n_new_features_identical_to_any_1989":len({d["gid_1998"] for d in exacts}),
            "total_mapped_line_length_1989_km":a0,
            "total_mapped_line_length_1998_km":a1,
            "exact_shared_line_length_km":common,
            "fraction_1989_line_matching_1998_exactly":common/a0 if a0 else None,
            "fraction_1998_line_matching_1989_exactly":common/a1 if a1 else None,
            "mapped_line_not_true_land_change":True,
        })
        features.extend(exacts)
    assert len(base)==17,(len(base),by.keys())
    return {"status":"PASS_COOK2021_BISCOE_1989_1998_GIS_LINEAGE_EQUALITY_CHECK",
            "source_original_archive_sha256":SOURCE_SHA256,
            "original_13436_features_read":13436,
            "source_sites":"BISC original MAPPPD -64.8114,-63.7775",
            "source_calendar_years":list(YEARS),
            "local_radius_km":RADIUS_KM,
            "n_original_local_source_features":len(base),
            "by_type":out,"exact_duplicate_line_feature_pairs":features,
            "same_year_coastline_missing_segments_dont_imply_change":True,
            "no_direct_ice_ramp_break_or_new_bare_rock_area":True,
            "not_a_demographic_response_estimate":True
            }
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-source-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    r=compute(a.original_source_zip)
    (a.out/"Cook2021_Biscoe_1989_1998_rock_ice_lineage_receipt.json").write_text(
      json.dumps(r,ensure_ascii=False,indent=2)+"\n")
    print("COOK_BISCOE_COASTLINE_DUPLICATION="+json.dumps(
        {"status":r["status"],"by_type":r["by_type"],
         "identical_examples":r["exact_duplicate_line_feature_pairs"][:10]},
        ensure_ascii=False),flush=True)
if __name__=="__main__":main()
