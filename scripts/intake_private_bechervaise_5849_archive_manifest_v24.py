#!/usr/bin/env python3
"""PRIVATE/OFFLINE intake for publisher-obtained AADC Béchervaise ZIP.

Not executed on original penguin data in GitHub Actions. The user must
first obtain the official AAS_4086 download from its documented link
https://data.aad.gov.au/eds/5849/download via normal publisher access.
No network, no extraction, no individual RFID or nest data read, no names
of constituent files disclosed: only ZIP central-directory metadata.

Never commit original AADC raw files, human download emails, S3 creds or
per-bird data to the public git repository.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from zipfile import ZipFile, BadZipFile

MAX_ARCHIVE_BYTES=25*1024**3
MAX_FILES=100_000
MAX_UNCOMPRESSED_BYTES=100*1024**3
VALID_EXTENSIONS={".txt",".csv",".xls",".xlsx",".dat",".pdf",".doc",".docx",
                  ".zip",".raw",".db",".tsv",".bin",".json",".xml",".log",".r"}
EXPECTED_DOI="10.26179/1205-2s58"
SOURCE_URL="https://data.aad.gov.au/eds/5849/download"

def sha256_file(path:Path):
    digest=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            digest.update(chunk)
    return digest.hexdigest()

def suffix_type(name:str):
    suffix=PurePosixPath(name).suffix.lower()
    return suffix if suffix in VALID_EXTENSIONS else "OTHER_OR_NO_EXTENSION"

def archive_summary(path:Path):
    if not path.is_file():
        raise ValueError("The official downloaded archive path must be a local file")
    if path.is_symlink():
        raise ValueError("Do not scan a symbolic link for a private source")
    n=path.stat().st_size
    if n<=0 or n>MAX_ARCHIVE_BYTES:
        raise ValueError("Empty or oversized original binary")
    # Hashing all input bytes is permitted; parsing original animal/tag ROWS
    # is not. This is a deterministic source receipt, not biology.
    sha=sha256_file(path)
    manifest={
        "status":"LOCAL_SOURCE_ARCHIVE_METADATA_ONLY",
        "original_source_publisher_url":SOURCE_URL,
        "source_DOI":EXPECTED_DOI,
        "local_file_size_bytes":n,
        "source_binary_sha256_computed_locally":sha,
        "publisher_MD5_not_independently_verified":True,
        "local_archive_source_authenticity_requires_publisher_receipt":True,
        "no_archive_contents_extracted":True,
        "no_original_penguin_tag_records_read":True,
        "no_original_penguin_individual_identifiers_output":True,
        "no_original_member_filenames_output":True,
        "no_private_source_bytes_committed":True,
        "no_same_tag_to_egg_join_performed":True,
        "no_causal_antarctic_island_ecology_result":True
    }
    try:
        with ZipFile(path,"r") as z:
            infos=z.infolist()
            if len(infos)>MAX_FILES:
                raise ValueError("Implausibly many ZIP source members")
            types=Counter()
            year_counts=Counter()
            total=0
            zip_invalid_traversal=0
            encrypted_members=0
            for item in infos:
                if item.is_dir():continue
                filename=item.filename.replace("\\","/")
                basename=PurePosixPath(filename)
                if filename.startswith("/") or ".." in basename.parts:
                    zip_invalid_traversal+=1
                    continue
                total+=item.file_size
                if total>MAX_UNCOMPRESSED_BYTES:
                    raise ValueError("Uncompressed source manifest exceeds safety cap")
                types[suffix_type(filename)]+=1
                encrypted_members+=bool(item.flag_bits&0x1)
                for year in set(re.findall(r"(?<!\d)(?:19\d\d|20\d\d)(?!\d)",filename)):
                    if 1991<=int(year)<=2021:year_counts[year]+=1
            manifest.update({
                "source_container":"ZIP_FILE_CENTRAL_DIRECTORY_ONLY",
                "zip_source_member_count":len(infos),
                "zip_source_member_file_suffix_groups":dict(sorted(types.items())),
                "year_tokens_from_member_names_only":dict(sorted(year_counts.items())),
                "zip_member_path_traversal_count":zip_invalid_traversal,
                "zip_encrypted_members":encrypted_members,
                "zip_manifest_not_proof_of_valid_RFID_data":True
            })
    except BadZipFile:
        # Do not run OCR, unzip or decode unknown user-managed originals.
        with path.open("rb") as f:
            head=f.read(12)
        if head.startswith(b"%PDF-"):fmt="PDF_DOCUMENT_NOT_RFID_DATA"
        elif head.startswith(b"\xd0\xcf\x11\xe0"):fmt="LEGACY_EXCEL_BINARY_UNREAD"
        elif head.startswith(b"Rar!"):fmt="RAR_BINARY_UNREAD"
        elif head.lower().startswith(b"<!doctype") or head.lower().startswith(b"<html"):
            fmt="HOLD_HTML_NOT_ORIGINAL_DATA"
        else:fmt="UNKNOWN_BINARY_NEEDS_CODEBOOK"
        manifest["source_container"]=fmt
        manifest["source_rows_schema_opened"]=0
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--publisher-download",type=Path,required=True,
                   help="Absolute path to a privately and legitimately acquired 5849 publisher original download")
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    z=archive_summary(a.publisher_download)
    a.out.write_text(json.dumps(z,indent=2)+"\n",encoding="utf8")
    print("AADC_PRIVATE_SOURCE_METADATA_ONLY",z["source_container"])
    print("FILE_SHA256",z["source_binary_sha256_computed_locally"])
    print("TAG_ROWS_PARSED",0)
    print("SOURCE_EGG_LINK_AND_CAUSAL_MODEL",False)
if __name__=="__main__":main()
