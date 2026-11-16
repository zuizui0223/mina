#!/usr/bin/env python3
"""Validate official CCAMLR 2022 v0.9 MPA polygon source *readiness*, not overlap.

The CCAMLR dataset has EPSG:6932 coordinates, NOT WGS84 longitude/latitude.
Never apply geographic-degree foraging buffers directly to this GeoJSON;
no reported nest protection without an adopted-zone legal rule and a
scientifically verified ocean/land mask.
"""
import argparse,hashlib,json
from pathlib import Path
EXPECTED_CODES={"GPZi","GPZii","GPZiii","KRZ","SRZ","SOSS"}
EXPECTED_REPO_COMMIT="8f17ec7e1e37d139ead6ea277821d5983beabd6a"
EXPECTED_GIT_BLOB_SHA="17fdf0d2ef6388c02d1b1a45d7e7c7d4e9a6cd0a"
def git_blob_sha(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\x00"+raw).hexdigest()
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--official-geojson",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    raw=args.official_geojson.read_bytes()
    assert git_blob_sha(raw)==EXPECTED_GIT_BLOB_SHA,"Unpinned MPA polygon source version"
    data=json.loads(raw)
    assert data["type"]=="FeatureCollection"
    assert data.get("crs",{}).get("properties",{}).get("name")=="urn:ogc:def:crs:EPSG::6932","Do not interpret source projected XY as longitude and latitude"
    assert len(data["features"])==6
    entries=[]
    for feature in data["features"]:
        prop=feature["properties"]
        assert feature["geometry"]["type"] in ("Polygon","MultiPolygon")
        assert {"GAR_ID","GAR_Name","GAR_Short_Label","GAR_Reference","GAR_Start_Date","GAR_Size"}<=set(prop)
        assert prop["GAR_End_Date"] is None
        assert prop["GAR_Size"]>0
        entries.append(dict(zone_code=prop["GAR_Short_Label"],original_name=prop["GAR_Name"],
            original_legal_reference=prop["GAR_Reference"],source_start_date=prop["GAR_Start_Date"],
            original_dataset_size_field=prop["GAR_Size"],
            legal_management_rule_not_derived_from_name=True))
    assert set(x["zone_code"] for x in entries)==EXPECTED_CODES
    assert sum(z["original_legal_reference"].startswith("Conservation Measure 91-05") for z in entries)==5
    assert len([z for z in entries if "91-03" in z["original_legal_reference"]])==1
    summary={
        "status":"OFFICIAL_CCAMLR_2022_V0_9_GEOMETRY_VERIFIED_BUT_NO_MARINE_ACCESS_OVERLAP",
        "publisher":"CCAMLR",
        "dataset":"Geographical data layer: CCAMLR Marine Protected Areas",
        "version":"v0.9",
        "dataset_version_date":"2022-08-04",
        "official_repo":"https://github.com/ccamlr/data/tree/main/geographical_data/mpa",
        "pinned_source_commit":EXPECTED_REPO_COMMIT,
        "pinned_MPA_json_git_blob_sha":EXPECTED_GIT_BLOB_SHA,
        "local_raw_sha256":hashlib.sha256(raw).hexdigest(),
        "source_geometry_CRS":"EPSG:6932 (projected equal-area, NOT lon/lat)",
        "source_features":len(entries),
        "source_zone_metadata":entries,
        "current_conservation_measures_to_recheck":["91-03","91-05"],
        "does_not_prove_RossSea_effective_2017_date_from_GAR_Start_Date":True,
        "does_not_imply_all_five_RossSea_zones_have_identical_fishing_restrictions":True,
        "required_next_sources":["official marine ocean/land coastline mask",
            "current adopted CCAMLR 91-03 and 91-05 zone-wise permitted activities",
            "modelled 50/100/200 km marine-access circles, not observed GPS foraging",
            "original nest-weight denominator with exact 595-source WGS84 coordinates"],
        "biological_271_source_colony_coverage_not_yet_overlaid":True,
        "no_actual_penguin_foraging_or_protection_fraction_claimed":True,
        "status_for_population_protected_fraction":"NO_GO_PROTECTION_COVERAGE"
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":summary["status"],"features":len(entries),
       "CRS":summary["source_geometry_CRS"],"blob_sha":summary["pinned_MPA_json_git_blob_sha"]},ensure_ascii=False))
if __name__=="__main__":main()
