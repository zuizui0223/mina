"""Reconstruct verified MAPPPD v5 same-source same-vantage 3-taxon site-year panel.

Original Oceanites 2026-10-21 API SHA pinned against previously independently
audited PR199 V40. No nest count magnitudes, ecological effects or climate data.
Survey season start year is not a verified precise census date or physical island.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,re
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlparse

import requests

BASE="https://www.penguinmap.com"
SOURCE={
  "release":f"{BASE}/api/v1/release/?format=json",
  "sites":f"{BASE}/api/v1/sites/?format=csv",
  "observations_p1":f"{BASE}/api/v1/observations/?format=csv&page_size=5000&page=1",
  "observations_p2":f"{BASE}/api/v1/observations/?format=csv&page_size=5000&page=2",
}
PINS={
"release":"8f676f6498b1bc79708a67fb05d4ac8ee73249444e85402af87f6a3c64280a65",
"sites":"36059537701069c934227148d32296368943b978b988fb415e07873e48c5ae34",
"observations_p1":"cd751e43ab61d57a6e7d3c7e918d673cf699392ac4bfccd546d29b99ea62f075",
"observations_p2":"c2b054fb687d13eb93e67d48a2b492cd47c94ccdef75b562680b770ad6be18f3",
}
SPECIES={"ADPE","CHPE","GEPE"}
EXPECTED={"ADPE":414,"CHPE":152,"GEPE":205}
EXPECTED_REGIONS={
"Adelie Land":27,"Central-west Antarctic Peninsula":180,"Elephant Island":14,
"Mac. Robertson Land":11,"Northeast Antarctic Peninsula":3,"Queen Maud Land":2,
"South Orkney Islands":5,"South Shetland Islands":250,
"Southwest Antarctic Peninsula":1,"Victoria Land":277,"Wilkes Land":1
}
SITE_FIELDS={"site_id","site_name","region","latitude","longitude","mapppd_version"}
OBS_FIELDS={"id","site_id","site_name","species_id","season","count","type",
            "presence","vantage","citekey","mapppd_version"}

def sha(data):return hashlib.sha256(data).hexdigest()

def source_data(session,name):
    url=SOURCE[name]
    if urlparse(url).hostname!="www.penguinmap.com":raise ValueError("SOURCE_STOP wrong publisher")
    with session.get(url,timeout=(25,85),stream=True) as res:
        res.raise_for_status()
        if urlparse(res.url).hostname!="www.penguinmap.com":raise ValueError("SOURCE_STOP redirected")
        data=bytearray()
        for part in res.iter_content(chunk_size=32768):
            data.extend(part)
            if len(data)>20000000:raise ValueError("SOURCE_STOP publisher payload too large")
    payload=bytes(data)
    if sha(payload)!=PINS[name]:raise ValueError(f"SOURCE_STOP publisher {name} SHA mismatch")
    if payload[:100].lstrip().startswith(b"<"):raise ValueError("SOURCE_STOP unexpected HTML")
    return payload

def tabular(data,required):
    text=data.decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(text,newline=""))
    if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
        raise ValueError("SCHEMA_STOP required original table fields missing")
    if len(reader.fieldnames)!=len(set(reader.fieldnames)):
        raise ValueError("SCHEMA_STOP duplicate original columns")
    rows=list(reader)
    if any(None in z for z in rows):raise ValueError("SCHEMA_STOP malformed original CSV")
    return rows

def numeric(s):
    s=str(s or "").strip().replace(",","")
    if not re.fullmatch(r"(?:0|[1-9]\d*)(?:\.\d+)?",s):return False
    x=float(s)
    return math.isfinite(x) and 0<=x<1e10

def strict_pairs(site_rows,observations):
    if len(site_rows)!=729 or len(observations)!=5487:
        raise ValueError("SOURCE_STOP original 729×5487 base changed")
    sites={}
    for s in site_rows:
        sid=s["site_id"].strip()
        if not sid or sid in sites or s["mapppd_version"]!="5.0":
            raise ValueError("SOURCE_STOP site identity duplicated/version changed")
        if not s["region"].strip() or not s["site_name"].strip():
            raise ValueError("SOURCE_STOP no source physical site name/region")
        sites[sid]=s
    all_ids=set()
    bykey=defaultdict(list)
    for row in observations:
        ident=row["id"]
        if ident in all_ids:raise ValueError("SOURCE_STOP duplicate observation ID")
        all_ids.add(ident)
        if row["mapppd_version"]!="5.0" or row["site_id"] not in sites:
            raise ValueError("SOURCE_STOP observation source ID/version drift")
        if row["site_name"]!=sites[row["site_id"]]["site_name"]:
            raise ValueError("SOURCE_STOP site name conflicted")
        try:year=int(row["season"])
        except (ValueError,TypeError):continue
        if not (1890<=year<=2026 and str(year)==row["season"]):continue
        if row["species_id"] not in SPECIES or row["type"]!="nests" or row["presence"]!="1" or not numeric(row["count"]):
            continue
        bykey[row["site_id"],row["species_id"],year].append(row)
    valid={k:a[0] for k,a in bykey.items() if len(a)==1}
    output=[]
    excluded=Counter()
    for (site,sp,yr),obs in valid.items():
        later=valid.get((site,sp,yr+1))
        if later is None:continue
        c0,c1=obs["citekey"].strip(),later["citekey"].strip()
        v0,v1=obs["vantage"].strip(),later["vantage"].strip()
        if not c0 or c0!=c1:
            excluded["different_or_unknown_original_source"]+=1
            continue
        if not v0 or v0!=v1:
            excluded["different_or_unknown_original_vantage"]+=1
            continue
        s=sites[site]
        lat,lon=float(s["latitude"]),float(s["longitude"])
        if not (-90<=lat<=-40 and -180<=lon<=180):
            raise ValueError("SOURCE_STOP unsupported original source point")
        output.append({
            "site_id":site,"species_id":sp,"start":yr,"end":yr+1,
            "source_region":s["region"],"original_site_name":s["site_name"],
            "source_point_latitude":lat,"source_point_longitude":lon,
            "original_citekey":c0,"original_vantage":v0,
            "source_early_observation_id":obs["id"],
            "source_late_observation_id":later["id"],
            "same_source_and_vantage":True,
            "source_recorded_count_magnitudes_exported":False,
            "actual_survey_month_known":False,
            "verified_physical_island":False
        })
    output.sort(key=lambda x:(x["species_id"],x["source_region"],x["site_id"],x["start"]))
    return output,{"duplicate_original_site_species_year_keys_excluded":sum(len(z)>1 for z in bykey.values()),
                   "source_rejection_summary":dict(excluded)}

def summarize(rows):
    s=Counter(r["species_id"] for r in rows)
    regions=Counter(r["source_region"] for r in rows)
    if len(rows)!=771 or dict(s)!=EXPECTED or dict(regions)!=EXPECTED_REGIONS:
        raise ValueError(f"SOURCE_STOP strict source 771 registry changed {len(rows)} {dict(s)} {dict(regions)}")
    if len({r["site_id"] for r in rows})!=95:raise ValueError("SOURCE_STOP source site support changed")
    strata=defaultdict(set)
    for r in rows:strata[(r["species_id"],r["start"],r["source_region"])].add(r["site_id"])
    if sum(len(v)>=5 for v in strata.values())!=54:
        raise ValueError("SOURCE_STOP region-year support changed")
    return {
       "original_strict_site_species_adjacent_year_pairs":len(rows),
       "distinct_original_site_ids":95,
       "distinct_publisher_region_labels":len(regions),
       "species_pair_counts":dict(sorted(s.items())),
       "source_region_pair_counts":dict(sorted(regions.items())),
       "species_region_year_strata_ge5_source_site_ids":54,
       "source_coordinate_not_nest_GPS":True,
       "survey_season_label_not_actual_census_date":True,
       "source_site_id_not_independent_physical_island":True,
       "original_nest_counts_not_written":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    report={"schema":1,"status":"ORIGINAL_SOURCE_NOT_VERIFIED","source_release":"MAPPPD v5.0 2026-10-21",
            "no_biological_effect_fitted":True,"ecological_warming_effect_fitted":False}
    try:
        with requests.Session() as session:
            session.headers.update({"User-Agent":"mina-climate-macro-three-taxa-source-support-v1/1.0"})
            raw={k:source_data(session,k) for k in SOURCE}
        release=json.loads(raw["release"])
        if release.get("version")!="5.0" or release.get("release_date")!="2026-10-21":
            raise ValueError("SOURCE_STOP release version mismatch")
        sites=tabular(raw["sites"],SITE_FIELDS)
        p1=tabular(raw["observations_p1"],OBS_FIELDS)
        p2=tabular(raw["observations_p2"],OBS_FIELDS)
        if len(p1)!=5000 or len(p2)!=487 or int(p1[-1]["id"])+1!=int(p2[0]["id"]):
            raise ValueError("SOURCE_STOP original two-page pagination changed")
        rows,metadata=strict_pairs(sites,p1+p2)
        summary=summarize(rows)
        filename=args.out/"original_MAPPPD5_strict_three_taxa_macro_pair_support.csv"
        with filename.open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        report.update({"status":"SOURCE_VERIFIED_PAIRED_SAMPLE_NO_EFFECTS",
            "original_publisher_sha256":{k:sha(v) for k,v in raw.items()},
            "source_quality":metadata,"source_summary":summary,
            "pair_support_csv_sha256":hashlib.sha256(filename.read_bytes()).hexdigest(),
            "time_alignment_note":"Only season start year, not actual census month; no unqualified pre-census climate claim.",
            "physical_island_geography_note":"Original site coordinate may be mainland, unnamed or uncertain; strict island IDs remain unverified.",
            "next_identification_gate":"Compare climate availability and source chronologies with frozen 771 pair roster before ecological effect fitting."})
    except Exception as e:
        report.update({"status":"SOURCE_ACCESS_OR_SCHEMA_HOLD",
                       "error":type(e).__name__+": "+str(e)[:600]})
    finally:
        (args.out/"original_MAPPPD5_strict_three_taxa_macro_support.json").write_text(
            json.dumps(report,indent=2,ensure_ascii=False)+"\n")
        print("MAPPPD5_STRICT_THREE_TAXA_MACRO_RECEIPT="+json.dumps(report,ensure_ascii=False),flush=True)
    return 0 if report["status"]=="SOURCE_VERIFIED_PAIRED_SAMPLE_NO_EFFECTS" else 2

if __name__=="__main__":raise SystemExit(main())
