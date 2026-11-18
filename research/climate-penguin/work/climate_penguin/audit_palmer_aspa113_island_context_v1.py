"""Palmer five-island original-source overlap and habitat-identity gate.

No habitat effect model, no sea-ice mechanism, and no causal climate estimate.
The two count sources may share field lineage: not independent replication.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMP = ROOT / "outputs/comparison_audit"
ORIGINAL = ROOT / "inputs/ASPA113_LITCHFIELD_ADELIE_COUNTS_1991_2012.csv"
ID_MAP = {"CHR":"CHIS","COR":"CORM","HUM":"HUMB","LIT":"LITC","TOR":"TORG"}


def csvrows(path):
    with Path(path).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def haversine_km(x, y):
    p1, p2 = math.radians(float(x["latitude"])), math.radians(float(y["latitude"]))
    dp = p2 - p1
    dl = math.radians(float(y["longitude"])-float(x["longitude"]))
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 6371.0088 * 2 * math.asin(min(1.0,math.sqrt(a)))


def audit():
    counts=csvrows(COMP/"palmer_five_island_counts.csv")
    official=csvrows(ORIGINAL)
    sites=csvrows(COMP/"palmer_site_coordinates.csv")
    veg=csvrows(COMP/"vegetation_mapppd_spatial_support.csv")
    assert len(counts)==135 and len(sites)==5
    assert set(ID_MAP)=={r["island_name"] for r in counts}
    assert set(ID_MAP.values())=={r["site_id"] for r in sites}
    coords={r["site_id"]:r for r in sites}
    rowmap={(r["island_name"],int(r["year"])):int(r["count"]) for r in counts}
    assert len(rowmap)==135
    years=sorted({int(r["year"]) for r in counts})
    assert years==list(range(1991,2018))
    for y in years:
        assert all((island,y) in rowmap for island in ID_MAP)
    published={int(r["season_start"]):int(r["breeding_pairs"]) for r in official}
    assert sorted(published)==list(range(1991,2013))
    matches=[y for y in published if published[y]==rowmap["LIT",y]]
    disagreements=[{"year":y,"ASPA113_breeding_pairs":published[y],"Palmer_group_count":rowmap["LIT",y],
                    "difference_palmer_minus_ASPA":rowmap["LIT",y]-published[y]} for y in published if y not in matches]
    assert len(matches)==20 and disagreements==[
        {"year":1998,"ASPA113_breeding_pairs":338,"Palmer_group_count":325,"difference_palmer_minus_ASPA":-13},
        {"year":1999,"ASPA113_breeding_pairs":322,"Palmer_group_count":301,"difference_palmer_minus_ASPA":-21},
    ]
    assert all(rowmap["LIT",y]==0 for y in range(2007,2018))
    assert rowmap["LIT",2006]==4
    assert all(rowmap[island,2017]>0 for island in ("CHR","COR","HUM","TOR"))

    nearest=[]
    ids=sorted(coords)
    for i in range(len(ids)):
        for j in range(i+1,len(ids)):
            a,b=ids[i],ids[j]
            d=haversine_km(coords[a],coords[b])
            nearest.append({"site_a":a,"site_b":b,"distance_km":round(d,6),
                            "overlap_500m_point_buffers":d<1.0,
                            "overlap_2000m_point_buffers":d<4.0})
    assert any(r["site_a"]=="HUMB" and r["site_b"]=="LITC" and r["overlap_500m_point_buffers"] for r in nearest)
    assert any(r["site_a"]=="LITC" and r["site_b"]=="TORG" and r["overlap_500m_point_buffers"] for r in nearest)
    vegmap={(r["site_id"],int(r["radius_m"])):r for r in veg if r["site_id"] in ids}
    assert len(vegmap)==15

    observed=[]
    for y in (1991,2006,2007,2012,2017):
        item={"year":y}
        for col in ID_MAP:
            item[col]=rowmap[col,y]
        item["four_other_islands_sum"]=sum(rowmap[col,y] for col in ("CHR","COR","HUM","TOR"))
        item["other_islands_all_positive"]=all(rowmap[col,y]>0 for col in ("CHR","COR","HUM","TOR"))
        observed.append(item)
    assert [z["four_other_islands_sum"] for z in observed]==[6192,913,847,451,140]
    habitats=[{"source_site_id":site,"palmer_code":next(k for k,v in ID_MAP.items() if v==site),
                "site_name":coords[site]["site_name"],"distance_from_litchfield_km":round(haversine_km(coords["LITC"],coords[site]),6),
                **{f"{radius}m_vegetation_features":int(vegmap[site,radius]["Vegetation_features"]) for radius in (500,2000)},
                **{f"{radius}m_lichen_features":int(vegmap[site,radius]["Lichen_features"]) for radius in (500,2000)}} for site in ids]
    return {
        "schema":1,
        "source_status":"source_overlap_verified_not_independent_causal_test",
        "source_sha256":{"ASPA113":checksum(ORIGINAL),"Palmer":checksum(COMP/"palmer_five_island_counts.csv"),
                         "Palmer_coordinates":checksum(COMP/"palmer_site_coordinates.csv"),
                         "Plantarctica_point_buffer":checksum(COMP/"vegetation_mapppd_spatial_support.csv")},
        "source_lineage_note":"Palmer LTER and ASPA table may reuse Fraser original counts; not independent field replications.",
        "palmer_count_roster_1991_2017":{"sites":5,"years":27,"records":len(counts)},
        "litchfield_official_overlap_1991_2012":{"years":22,"matched":len(matches),"discrepancies":disagreements},
        "litchfield_official_first_recorded_zero":2007,
        "palmer_LIT_explicit_zero_2007_2017":True,
        "palmer_comparison_islands_2017_positive":4,
        "selected_count_years":observed,
        "point_buffer_geometry":{"distance_rows":nearest,"point_buffers_are_not_island_polygons":True,
                                 "500m_overlapping_pairs":sum(z["overlap_500m_point_buffers"] for z in nearest),
                                 "2000m_overlapping_pairs":sum(z["overlap_2000m_point_buffers"] for z in nearest)},
        "static_map_context":habitats,
        "design_stop":{
            "event_count_observed":True,
            "matched_annual_vegetation_area_measured":False,
            "independent_rock_habitat_area_by_actual_island":False,
            "annual_island_snow_census":False,
            "longitudinal_seal_pressure_measured":False,
            "1991_2007_original_nearshore_seaice_verified_complete":False,
            "island_mediator_or_diD_identifiable":False,
        },
        "unsupported":["greening_from_penguin_abandonment","island-level vegetation area from point-buffer features",
                       "four independent temperature exposures for nearby islands",
                       "the baseline size and survey-method effects are controlled"]
    }


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    result=audit()
    (args.output/"PALMER_ASPA113_FIVE_ISLAND_SOURCE_GATE_RESULT.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    print("PALMER_ASPA113_FIVE_ISLAND_RECEIPT="+json.dumps(result,ensure_ascii=False,allow_nan=False),flush=True)


if __name__=="__main__":
    main()
