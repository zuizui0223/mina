#!/usr/bin/env python3
"""Source byte identity only. NO csv parsing, headings, animal rows or movement modeling.

Compare a public pointblue 2023 released file candidate to the explicitly
published USAP-DC 601444 MD5. Do not promote a merely similarly named file
into the official identity if any invariant is false.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

OFFICIAL_MD5="aaae6ddad6d12081b5a68466794438a2"
AUTHOR_GIT_BLOB="7dd043fb276ff8687a53f04f73719243c23268ec"
BYTES=25121923
PUBLIC="https://raw.githubusercontent.com/pointblue/solo_nests/04517cedac18950408abd4d0b510f4aae3447f05/data/allresight_reference_copy.csv"
OFFICIAL="https://www.usap-dc.org/view/dataset/601444"

def checksum_candidate(path,expected_official_md5=OFFICIAL_MD5,
                       expected_source_blob=AUTHOR_GIT_BLOB,expected_length=BYTES):
    path=Path(path)
    n=path.stat().st_size
    md5=hashlib.md5(usedforsecurity=False)
    sha256=hashlib.sha256()
    gb=hashlib.sha1(usedforsecurity=False)
    gb.update(f"blob {n}\0".encode())
    with path.open("rb") as handle:
        while True:
            block=handle.read(1024*1024)
            if not block: break
            md5.update(block)
            sha256.update(block)
            gb.update(block)
    digest=md5.hexdigest()
    blob=gb.hexdigest()
    same_author=n==expected_length and blob==expected_source_blob
    exact=same_author and digest==expected_official_md5
    return {
        "status":("POTENTIAL_OFFICIAL_IDENTICAL_MD5_AUTHOR_COPY_SOURCE_ONLY"
                  if exact else "HOLD_PUBLIC_COPY_NOT_BYTE_IDENTICAL_TO_OFFICIAL"),
        "size_bytes":n,
        "source_blob_matches_pin":same_author,
        "source_md5":digest,
        "source_sha256":sha256.hexdigest(),
        "source_git_blob_sha":blob,
        "official_md5_from_USAP_metadata":expected_official_md5,
        "official_md5_matches":digest==expected_official_md5,
        "identity_eligible_exact_digest_and_size":exact,
        "source_candidate_url":PUBLIC,
        "canonical_dataset_url":OFFICIAL,
        "headers_read":0,
        "behavioral_rows_read":0,
        "individual_ID_values_extracted":0,
        "state_decoding_or_source_processing_unlocked":False,
        "PR142_original_frozen_gate_modified":False,
        "PR189_frozen_science_modified":False
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    x=checksum_candidate(args.source)
    args.out.write_text(json.dumps(x,indent=2)+"\n",encoding="utf-8")
    print("PUBLIC_RESIGHT_SOURCE_IDENTITY",x["status"])
    print("OFFICIAL_MD5_MATCH",x["official_md5_matches"],
          "GIT_BLOB_MATCH",x["source_blob_matches_pin"],
          "BYTES",x["size_bytes"])
    print("BEHAVIORAL_SOURCE_HEADER_NOT_OPENED")
    print("PR142_REMAINS_LOCKED")
if __name__=="__main__":
    main()
