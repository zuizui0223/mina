#!/usr/bin/env python3
"""MAPPPD v5 original source-only strict longitudinal nest and NZ overlap audit."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,re,unicodedata
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlparse
import requests
import audit_nz_ross_sea_census_source_v33 as nz

SOURCE={
 "release":"https://www.penguinmap.com/api/v1/release/?format=json",
 "sites":"https://www.penguinmap.com/api/v1/sites/?format=csv",
 "observations":"https://www.penguinmap.com/api/v1/observations/?format=csv"}
VERSION="5.0"
DATE="2026-10-21"
N_SITE=729
N_OBS=5487
NZ_SHA="23a95d9e693dd095e085534f2c215b79880a72fe9cfb5a59337501192dae03e6"
NZ_CITE="manaakiwhenua2021aerial"
SPECIES={"ADPE","CHPE","GEPE"}
SITE_COLUMNS={"site_id","site_name","region","latitude","longitude","mapppd_version"}
OBS_COLUMNS={"id","site_id","site_name","species_id","season","count","type","presence","vantage","citekey","mapppd_version"}
MIN_PAIRS=50;MIN_SITES=20;MIN_REGIONS=4;MIN_SPECIES=2

def fetch(session,url):
    parsed=urlparse(url)
    if parsed.scheme!="https" or parsed.hostname!="www.penguinmap.com":
        raise ValueError("SOURCE_STOP untrusted MAPPPD URL")
    with session.get(url,stream=True,timeout=(20,85),
                     headers={"User-Agent":"mina-MAPPPD5-original-source-only-2026/1.0"}) as res:
        res.raise_for_status()
        end=urlparse(res.url)
        if end.scheme!="https" or end.hostname!="www.penguinmap.com":
            raise ValueError("SOURCE_STOP redirected outside publisher")
        data=bytearray()
        for block in res.iter_content(32768):
            data.extend(block)
            if len(data)>20000000:raise ValueError("SOURCE_STOP oversized original MAPPPD data")
        raw=bytes(data)
        if not raw or raw.lstrip().startswith(b"<"):
            raise ValueError("SOURCE_STOP original API did not supply data")
        return raw,{"original_source_sha256":hashlib.sha256(raw).hexdigest(),
                    "original_source_bytes":len(raw),
                    "MAPPPD_response_version":res.headers.get("X-MAPPPD-Version")}

def csvrows(raw,columns):
    rd=csv.DictReader(io.StringIO(raw.decode("utf-8-sig"),newline=""))
    if not rd.fieldnames or not columns.issubset(set(rd.fieldnames)):
        raise ValueError("SCHEMA_STOP original MAPPPD columns unavailable")
    if len(set(rd.fieldnames))!=len(rd.fieldnames):
        raise ValueError("SCHEMA_STOP duplicate original source CSV columns")
    rows=list(rd)
    if any(None in r for r in rows):
        raise ValueError("SCHEMA_STOP malformed original MAPPPD row")
    return rows

def norm(s):return " ".join(unicodedata.normalize("NFC",str(s or "")).strip().casefold().split())
def valid_year(s):
    if not re.fullmatch(r"(?:18|19|20)\d{2}",str(s).strip()):return None
    y=int(s)
    return y if 1890<=y<=2026 else None

def numeric_present(s):
    s=str(s or "").replace(",","").strip()
    if not re.fullmatch(r"(?:0|[1-9]\d*)(?:\.\d+)?",s):return False
    try:val=float(s)
    except ValueError:return False
    return math.isfinite(val) and 0<=val<1e10

def index_sites(rows,require_n=True):
    if require_n and len(rows)!=N_SITE:raise ValueError("SOURCE_STOP original 729 sites count drift")
    sites={}
    for r in rows:
        ident=r["site_id"].strip()
        if not ident or ident in sites:raise ValueError("SOURCE_STOP site ID duplicated")
        if r["mapppd_version"]!=VERSION or not r["site_name"].strip() or not r["region"].strip():
            raise ValueError("SOURCE_STOP unexpected site identity")
        sites[ident]=r
    return sites

def support(rows,sites,require_n=True):
    if require_n and len(rows)!=N_OBS:raise ValueError("SOURCE_STOP original 5487 observations changed")
    seen=set();groups=defaultdict(list);sources=Counter();stage=Counter();recent=Counter()
    for r in rows:
        oid=str(r["id"]).strip();site=r["site_id"].strip()
        if not oid or oid in seen:raise ValueError("SOURCE_STOP observation ID duplicated")
        seen.add(oid)
        if site not in sites or r["site_name"].strip()!=sites[site]["site_name"]:
            raise ValueError("SOURCE_STOP orphan source observation")
        if r["mapppd_version"]!=VERSION:raise ValueError("SOURCE_STOP observation version drift")
        year=valid_year(r["season"])
        sources[r["citekey"].strip() or "<MISSING_SOURCE_CITATION>"]+=1
        stage[r["type"].strip() or "<MISSING_TYPE>"]+=1
        if year is not None and year>=2022:recent[r["species_id"]]+=1
        if (year is None or r["species_id"] not in SPECIES or
            r["type"]!="nests" or r["presence"]!="1" or
            not numeric_present(r["count"])):
            continue
        groups[(site,r["species_id"],year)].append(r)
    dup={k:v for k,v in groups.items() if len(v)>1}
    good={k:v[0] for k,v in groups.items() if len(v)==1}
    pairs=[];rejected=Counter()
    for (site,species,year),r in good.items():
        nxt=good.get((site,species,year+1))
        if nxt is None:continue
        if not r["citekey"].strip() or r["citekey"]!=nxt["citekey"]:
            rejected["different_or_unknown_original_source"]+=1
            continue
        if not r["vantage"].strip() or r["vantage"]!=nxt["vantage"]:
            rejected["different_or_unknown_original_vantage"]+=1
            continue
        pairs.append((site,species,year,sites[site]["region"]))
    regions=Counter(r for s,sp,y,r in pairs)
    years=sorted({y for s,sp,y,r in pairs})
    sites_supported={s for s,sp,y,r in pairs}
    spp=Counter(sp for s,sp,y,r in pairs)
    strata=defaultdict(set)
    for s,sp,y,reg in pairs:strata[(sp,y,reg)].add(s)
    coverage={
       "source_original_strict_same_site_species_year_method_nest_transitions":len(pairs),
       "distinct_original_siteIDs":len(sites_supported),
       "distinct_publisher_region_labels":len(regions),
       "original_species_pair_opportunities":dict(sorted(spp.items())),
       "original_transitions_by_publisher_region":dict(sorted(regions.items())),
       "distinct_original_year_starts":len(years),
       "original_pair_start_year_roster":years,
       "matched_same_species_year_region_strata_with_ge5_site_IDs":sum(len(v)>=5 for v in strata.values()),
       "duplicate_site_species_season_groups_excluded":len(dup),
       "original_observation_rows_in_duplicate_groups_excluded":sum(len(v) for v in dup.values()),
       "adjacent_source_stage_candidates_excluded":dict(rejected),
       "strict_macro_source_support_pass":(len(pairs)>=MIN_PAIRS and len(sites_supported)>=MIN_SITES
                  and len(regions)>=MIN_REGIONS and len(spp)>=MIN_SPECIES),
       "original_publisher_site_ID_not_independent_landmass_ID":True
    }
    quality={
       "original_observations":len(rows),
       "original_site_count":len(sites),
       "original_type_counts":dict(sorted(stage.items())),
       "original_top_source_citations":dict(sources.most_common(15)),
       "original_NZ_aerial_source_citation_record_count":sources[NZ_CITE],
       "source_original_records_with_season_start_ge2022_by_species":dict(sorted(recent.items())),
       "no_absolute_bird_count_magnitude_exported":True
    }
    return coverage,quality,good

def original_nz_presence(matrix):
    years={c:nz.parse_year(v) for c,v in matrix[0].items() if nz.parse_year(v) is not None}
    if len(years)!=44 or sorted(years.values())!=list(nz.YEARS):
        raise ValueError("SOURCE_STOP original NZ calendar changed")
    output={}
    for rownumber,row in matrix.items():
        if rownumber==0:continue
        name=row.get(0)
        if not isinstance(name,str) or not name.strip():continue
        ident=norm(name)
        if ident in output:raise ValueError("SOURCE_STOP duplicated original NZ colony label")
        output[ident]={year for c,year in years.items() if nz.num_present(row.get(c))}
    if len(output)!=39:raise ValueError("SOURCE_STOP original NZ 39 colony count changed")
    return output

def overlap(good,sites,nzvalid):
    matches=Counter(); pairs=[]
    for (site,sp,yr),obs in good.items():
        if sp!="ADPE" or obs["citekey"]!=NZ_CITE:continue
        name=sites[site]["site_name"]
        if norm(name) in nzvalid and yr in nzvalid[norm(name)]:
            matches[name]+=1
            pairs.append((site,yr))
    return {
       "fixed_upstream_original_source_citation_key":NZ_CITE,
       "exact_site_name_species_ADPE_season_nests_citation_numeric_presence_overlaps":len(pairs),
       "distinct_original_source_siteIDs_with_upstream_overlap":len({site for site,yr in pairs}),
       "source_overlap_by_colony_name":dict(sorted(matches.items())),
       "original_animal_numeric_count_equality_NOT_tested":True,
       "upstream_field_census_not_an_independent_replication":True
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    result={"status":"HOLD_PUBLISHER_ORIGINAL_SOURCE","ecological_effects_fitted":0}
    try:
        with requests.Session() as session:
            downloads={name:fetch(session,url) for name,url in SOURCE.items()}
        release=json.loads(downloads["release"][0])
        if release.get("version")!=VERSION or release.get("release_date")!=DATE:
            raise ValueError("SOURCE_STOP MAPPPD official v5 date/version mismatch")
        if not str(release.get("license","")).startswith("CC BY 4.0"):
            raise ValueError("SOURCE_STOP original licence changed")
        sites=index_sites(csvrows(downloads["sites"][0],SITE_COLUMNS))
        cnt=csvrows(downloads["observations"][0],OBS_COLUMNS)
        coverage,quality,good=support(cnt,sites)
        with requests.Session() as session:
            nzfiles,nzmeta=nz.ckandownloads(session)
        if nzfiles["census"]["receipt"]["sha256"]!=NZ_SHA:
            raise ValueError("SOURCE_STOP original NZ source hash mismatch")
        matrix=nz.workbook_original(nzfiles["census"]["raw"])
        if set(matrix)!={"All data"}:raise ValueError("SOURCE_STOP NZ original sheets drift")
        pedigree=overlap(good,sites,original_nz_presence(matrix["All data"]))
        result={
           "status":"V40_ORIGINAL_MAPPPD5_MACRO_SOURCE_AND_NZ_PEDIGREE_QA",
           "original_release":{"version":VERSION,"date":DATE,"citation":release.get("citation"),"license":release.get("license")},
           "original_download_SHA_receipts":{name:meta for name,(raw,meta) in downloads.items()},
           "frozen_contract":"contracts/MAPPPD_V5_SOURCE_DEDUP_MACRO_PANEL_V40.md",
           "source_quality":quality,"strict_longitudinal_source_sample":coverage,
           "original_NZ_author_census_sha256":NZ_SHA,
           "already_republished_NZ_aerial_source_overlap":pedigree,
           "ecological_models_fitted":0,
           "scientific_decision":("PROCEED_INDEPENDENT_ISLAND_SITE_EVENT_LINEAGE_DESIGN"
                                  if coverage["strict_macro_source_support_pass"]
                                  else "STOP_STRICT_SAME_SOURCE_AND_METHOD_MACRO_SAMPLE")
        }
    except Exception as e:
        result["error_type"]=type(e).__name__;result["error"]=str(e)[:680]
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"]=="HOLD_PUBLISHER_ORIGINAL_SOURCE":raise SystemExit(2)

if __name__=="__main__":main()
