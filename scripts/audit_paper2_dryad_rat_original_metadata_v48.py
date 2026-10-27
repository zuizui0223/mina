#!/usr/bin/env python3
"""V48 source-only Dryad original 230-island rat-status predictor metadata check.

No FIBD bird observations used, no original passerine outcome analyzed and no
true rat-absence artificially assigned. Public Dryad official API only.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse
import requests

API="https://datadryad.org/api/v2"
HOST="datadryad.org"
DOI="doi:10.5061/dryad.dj524"
ENCODED_DOI="doi%3A10.5061%2Fdryad.dj524"
MAX_JSON=1200000
MAX_FILES_LISTED=100
MAX_RESOURCE_BYTES=10_000_000
MAX_TOTAL_SOURCE_BYTES=20_000_000

def first_party_public_get(session,path):
    """No credentials, no private/embargo endpoints, no external redirect."""
    if not path.startswith("/api/v2/") or "//" in path:
        raise ValueError("SOURCE_OUTSIDE_PREDECLARED_DRYAD_API")
    url="https://"+HOST+path
    with session.get(url,timeout=(12,45),stream=True,
                     headers={"User-Agent":"mina-Paper2-Falkland-original-rat-source-V48/1.0","Accept":"application/json"},
                     allow_redirects=True) as r:
        r.raise_for_status()
        dest=urlparse(r.url)
        if dest.hostname!=HOST or dest.scheme!="https":
            raise ValueError("DRYAD_NOT_OFFICIAL_FIRST_PARTY_REDIRECT")
        pieces=[];size=0
        for piece in r.iter_content(chunk_size=16384):
            size+=len(piece)
            if size>MAX_JSON:
                raise ValueError("DRYAD_PUBLIC_JSON_TOO_LARGE")
            pieces.append(piece)
        try:doc=json.loads(b"".join(pieces).decode("utf-8"))
        except Exception as exc:raise ValueError("DRYAD_PUBLIC_RESPONSE_NOT_JSON") from exc
        if not isinstance(doc,dict):
            raise ValueError("DRYAD_PUBLIC_RESPONSE_NOT_OBJECT")
        return doc


def extract_versions_metadata(dataset, session):
    # Explicit exact source DOI lineage required. A related article DOI is not enough.
    identity=str(dataset.get("identifier",dataset.get("doi",""))).strip().lower()
    if identity!=DOI.lower():
        raise ValueError("DRYAD_DATASET_DOI_NOT_THE_PUBLISHED_TABAK_DEPOSIT")
    if str(dataset.get("curationStatus", "")).lower() not in ("published", ""):
        raise ValueError("DRYAD_SOURCE_NOT_PUBLIC_PUBLISHED")
    license_val=dataset.get("license") or dataset.get("licenseUri") or ""
    # Dryad dataset default CC0, but confirm from response instead of assuming.
    if not license_val:
        # Dataset API may serve public licence via version API: continue as
        # metadata, BUT do not download raw content without proven terms.
        license_state="UNVERIFIED_NEED_VERSION"
    else:
        license_state=str(license_val)[:250]
    direct=dataset.get("_links",{}).get("stash:version",{})
    href=direct.get("href") if isinstance(direct,dict) else None
    if href:
        pp=urlparse(href)
        if pp.scheme and (pp.scheme!="https" or pp.hostname!=HOST):
            raise ValueError("DRYAD_CROSS_DOMAIN_VERSION_LINK")
        path=pp.path if pp.scheme else href
        if not path.startswith("/api/v2/versions/"):
            raise ValueError("DRYAD_VERSION_LINK_NOT_API")
        version=first_party_public_get(session,path)
    else:
        version_list=first_party_public_get(
            session,"/api/v2/datasets/"+ENCODED_DOI+"/versions")
        versions=version_list.get("_embedded",{}).get("stash:versions")
        if not isinstance(versions,list):
            versions=version_list.get("versions")
        if not isinstance(versions,list) or not versions:
            raise ValueError("DRYAD_NO_VERIFIED_PUBLISHED_VERSION_LINK")
        candidates=[x for x in versions
                    if str(x.get("curationStatus","")).lower()=="published"]
        if not candidates:raise ValueError("DRYAD_NO_PUBLIC_PUBLISHED_VERSION")
        ids=[int(x.get("id",-1)) for x in candidates]
        version=first_party_public_get(session,"/api/v2/versions/"+str(max(ids)))
    if str(version.get("curationStatus","")).lower() not in ("published",):
        raise ValueError("DRYAD_LATEST_VERSION_NOT_PUBLISHED")
    version_id=version.get("id")
    if not isinstance(version_id,int) or version_id<=0:
        raise ValueError("DRYAD_PUBLIC_VERSION_ID_INVALID")
    return version_id,license_state,version


def original_file_listing(session,version_id):
    obj=first_party_public_get(session,f"/api/v2/versions/{version_id}/files")
    embedded=obj.get("_embedded",{})
    files=(embedded.get("stash:files") if isinstance(embedded,dict) else None)
    if files is None:files=obj.get("files")
    if not isinstance(files,list):
        raise ValueError("DRYAD_FILE_LISTING_SHAPE_UNKNOWN")
    total=obj.get("total")
    if isinstance(total,int) and total>len(files):
        raise ValueError("DRYAD_PUBLIC_FILE_LISTING_PAGINATED_UNEXHAUSTED")
    if len(files)>MAX_FILES_LISTED:
        raise ValueError("DRYAD_UNEXPECTEDLY_LARGE_FILE_LISTING")
    processed=[]
    for f in files:
        name=str(f.get("path") or f.get("filename") or "").strip()
        f_id=f.get("id")
        size=f.get("size")
        if not name or not isinstance(f_id,int) or not isinstance(size,int) or size<0:
            raise ValueError("DRYAD_NATIVE_FILE_METADATA_INCOMPLETE")
        processed.append({
           "filename":name[:180],"official_file_id":f_id,
           "published_mime_type":str(f.get("mimeType") or "")[:100],
           "published_file_bytes":size,
           "published_digest":str(f.get("digest") or "")[:180],
           "published_digest_type":str(f.get("digestType") or "")[:30],
           "tabular_source_candidate":bool(re.search(r"\.(csv|tsv|xls|xlsx|txt|zip)$",name,re.I)),
           "bounded_download_allowed_by_size":size<=MAX_RESOURCE_BYTES,
        })
    return processed


def inspect_open_published_source():
    report={
      "source_doi":DOI,
      "published_source_api":"https://datadryad.org/api/v2/datasets/"+ENCODED_DOI,
      "original_published_2015_passerine_study":"doi:10.1111/1365-2656.12312",
      "original_source_prior_published_rat_status_islands":{"rat_present":85,"historically_rat_free":108,"rat_eradicated":37,"total":230},
      "no_original_FIBD_Paper2_bird_outcomes_read":True,
      "no_TabAK_passserine_bird_outcome_reanalysis":True,
      "original_dryad_bird_species_file_records_not_republished":True,
      "rat_absences_not_assumed_from_mammal_record_missing":True,
      "status":"V48_DRYAD_PUBLIC_SOURCE_METADATA_HOLD",
    }
    try:
        with requests.Session() as session:
            dataset=first_party_public_get(session,"/api/v2/datasets/"+ENCODED_DOI)
            v,lic,version=extract_versions_metadata(dataset,session)
            files=original_file_listing(session,v)
            report["official_first_party_dataset_metadata"]={
                "source_title":str(dataset.get("title") or "")[:300],
                "original_doi":dataset.get("identifier"),
                "original_source_publication_year":dataset.get("publicationDate"),
                "confirmed_public_version_id":v,
                "source_version_status":version.get("curationStatus"),
                "original_source_reuse_licence":lic,
                "original_source_files_n":len(files),
                "files_total_declared_bytes":sum(f["published_file_bytes"] for f in files),
            }
            report["original_public_data_files"]=files
            report["original_source_file_downloaded"]=False
            report["original_island_level_rat_status_schema_verified"]=False
            report["can_authenticate_island_key_to_FIBD"]=False
            report["status"]="V48_PUBLISHED_DRYAD_SOURCE_AND_FILE_METADATA_AUDITED"
    except Exception as e:
        report["error"]=type(e).__name__+": "+str(e)[:500]
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    r=inspect_open_published_source()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(r,ensure_ascii=False))
    if r["status"]!="V48_PUBLISHED_DRYAD_SOURCE_AND_FILE_METADATA_AUDITED":
        raise SystemExit(2)

if __name__=="__main__":
    main()
