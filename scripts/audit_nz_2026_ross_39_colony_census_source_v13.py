#!/usr/bin/env python3
"""Reproducible source / sampling-support audit, not a new penguin mechanism.

Official NZ Landcare CKAN resource metadata -> published XLSX file. This
does not infer penguin migration or breeding success from colony pairs.
Missing annual colony counts remain missing, not zeros. No copyrighted XLSX
bytes are committed or republished. Source licence CC BY-NC 4.0.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, re
from collections import Counter
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse, urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler, HTTPSHandler
from zipfile import ZipFile, is_zipfile
import xml.etree.ElementTree as ET

HOST="datastore.landcareresearch.co.nz"
RESOURCE_ID="5fd490e5-92c4-4f2c-a82e-c66db2320eb1"
API="https://datastore.landcareresearch.co.nz/api/3/action/resource_show"
SOURCE_MD5="195a9027a0d18012812b09fb345ac60e"
MAX_FILE=1024*1024
MAX_SOURCE_METADATA=200000
M="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
P="{http://schemas.openxmlformats.org/package/2006/relationships}"
R="{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

def approved(url):
    p=urlparse(url)
    return p.scheme=="https" and p.hostname==HOST

class ApprovedRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,url):
        if not approved(url):
            raise ValueError("Unverified host or protocol redirect; blocked")
        return super().redirect_request(req,fp,code,msg,headers,url)

def fetch_bounded(url,max_size=MAX_FILE):
    if not approved(url): raise ValueError("Source must be official repository HTTPS")
    op=build_opener(HTTPSHandler(),ApprovedRedirect())
    with op.open(Request(url,headers={"User-Agent":"penguin-census-provenance-audit/1.0",
                 "Accept":"application/json,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*"}),timeout=25) as res:
        if not approved(res.geturl()):raise ValueError("Untrusted final resource URL")
        cl=res.headers.get("Content-Length")
        if cl and cl.isdigit() and int(cl)>max_size:
            raise ValueError("Source over size cap")
        data=res.read(max_size+1)
        if len(data)>max_size:raise ValueError("Source over size cap")
        if res.headers.get("Content-Type","").lower().find("html")>=0 or data[:150].lower().lstrip().startswith((b"<!doctype",b"<html")):
            raise ValueError("HTML application shell instead of data")
        return data

def official_metadata(raw):
    z=json.loads(raw)
    if not z.get("success") or not isinstance(z.get("result"),dict):
        raise ValueError("CKAN official response did not return resource metadata")
    r=z["result"]
    if str(r.get("id"))!=RESOURCE_ID:
        raise ValueError("Wrong CKAN source resource ID")
    if str(r.get("hash","")).lower()!=SOURCE_MD5:
        raise ValueError("Published official MD5 changed")
    if str(r.get("format","")).upper()!="XLSX":
        raise ValueError("Published file no longer XLSX")
    url=r.get("url","")
    if not approved(url):
        raise ValueError("CKAN official resource file URL redirects/offsite unverified")
    return {"url":url,"size":r.get("size"),"hash":r.get("hash"),
            "format":r.get("format"),"name":r.get("name")}

def excel_col(address):
    letters=re.match(r"^[A-Z]+",address)
    if not letters:return None
    ix=0
    for s in letters.group():
        ix=ix*26+ord(s)-64
    return ix-1

def workbook_first_table(raw):
    if not is_zipfile(BytesIO(raw)):
        raise ValueError("Author file not valid XLSX ZIP")
    with ZipFile(BytesIO(raw)) as z:
        members=set(z.namelist())
        if "xl/workbook.xml" not in members:
            raise ValueError("Missing workbook root")
        book=ET.fromstring(z.read("xl/workbook.xml"))
        rel={}
        if "xl/_rels/workbook.xml.rels" in members:
            rel={x.attrib.get("Id"):x.attrib.get("Target") for x in
                  ET.fromstring(z.read("xl/_rels/workbook.xml.rels")).findall(P+"Relationship")}
        sheets=book.find(M+"sheets")
        if sheets is None:raise ValueError("No Excel sheets")
        sh=next(iter(sheets),None)
        if sh is None:raise ValueError("No first Excel sheet")
        target=rel.get(sh.attrib.get(R+"id"),"")
        if not target: raise ValueError("No first-sheet file mapping")
        target=(target.lstrip("/") if target.startswith("/xl/") else
                target if target.startswith("xl/") else "xl/"+target.lstrip("/"))
        if target not in members:raise ValueError("Referenced XLSX sheet missing")
        if z.getinfo(target).file_size>MAX_FILE:raise ValueError("Sheet uncompressed too large")
        shared=[]
        if "xl/sharedStrings.xml" in members:
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(M+"si"):
                shared.append("".join(x.text or "" for x in si.iter(M+"t")))
        doc=ET.fromstring(z.read(target))
        values=[]
        for row in doc.findall(".//"+M+"sheetData/"+M+"row"):
            cells={}
            for c in row.findall(M+"c"):
                i=excel_col(c.get("r",""))
                if i is None:continue
                v=c.find(M+"v")
                if c.get("t")=="s" and v is not None and v.text:
                    val=shared[int(v.text)]
                elif c.get("t")=="inlineStr":
                    val="".join(n.text or "" for n in c.iter(M+"t"))
                else:
                    val=v.text if v is not None and v.text is not None else ""
                cells[i]=val
            if cells:values.append(cells)
        return {"sheet_name":sh.attrib.get("name",""),"rows":values}

def evaluate_xlsx(raw):
    if hashlib.md5(raw).hexdigest()!=SOURCE_MD5:
        raise ValueError("Actual original XLSX MD5 mismatched published resource")
    obj=workbook_first_table(raw)
    allrows=obj["rows"]
    hdr_index=None
    years=None
    for i,row in enumerate(allrows[:18]):
        cells=[str(v).strip() for k,v in sorted(row.items())]
        if any(v.lower()=="colony" for v in cells) and sum(bool(re.fullmatch(r"(19|20)\d{2}",v)) for v in cells)>=25:
            hdr_index=i;break
    if hdr_index is None:
        raise ValueError("Source header row containing colony + calendar years not identified")
    hdr=allrows[hdr_index]
    col_key=next(k for k,v in hdr.items() if str(v).strip().lower()=="colony")
    years={k:int(str(v).strip()) for k,v in hdr.items()
           if re.fullmatch(r"(19|20)\d{2}",str(v).strip())}
    if min(years.values())>1981 or max(years.values())<2024:
        raise ValueError("Official year range 1981..2024 unavailable")
    names=[]
    value_types=Counter()
    byyear={v:Counter() for v in years.values()}
    for row in allrows[hdr_index+1:]:
        name=str(row.get(col_key,"")).strip()
        if not name:continue
        normalized=name.lower()
        # Total or summary is not one of the 39 independent colonies.
        if normalized.startswith(("total","sum of","grand total","all colony","all sites")):
            value_types["aggregate_summary_rows_excluded"]+=1
            continue
        names.append(name)
        for col,year in years.items():
            v=str(row.get(col,"")).strip()
            if not v:
                byyear[year]["MISSING_BLANK"]+=1
                value_types["MISSING_BLANK"]+=1
            else:
                try:
                    n=float(v.replace(",",""))
                except ValueError:
                    byyear[year]["TEXT_UNRESOLVED"]+=1
                    value_types["TEXT_UNRESOLVED"]+=1
                else:
                    if not math.isfinite(n) or n<0 or n!=int(n):
                        byyear[year]["OTHER_NONNEG_INTEGER_REVIEW"]+=1
                    elif n==0:
                        byyear[year]["EXPLICIT_ZERO_SOURCE"]+=1
                    else:
                        byyear[year]["POSITIVE_NUMERIC_COUNT"]+=1
    if len(set(names))!=len(names):
        raise ValueError("Colony source names are not unique")
    # No hard-coded assumption that full table includes only 39 rows;
    # report actual sample roster faithfully.
    report={
        "source_status":"OFFICIAL_2026_39_COLONY_CENSUS_COUNTS_STRUCTURALLY_AUDITED",
        "original_bytes":len(raw),
        "verified_md5":hashlib.md5(raw).hexdigest(),
        "official_metadata_sha256":hashlib.sha256(raw).hexdigest(),
        "sheet_name":obj["sheet_name"],
        "n_named_nonaggregate_source_rows":len(names),
        "expected_publication_colonies":39,
        "contains_cape_barne_literal":any("barne" in s.lower() for s in names),
        "contains_cape_royds_literal":any("royds" in s.lower() for s in names),
        "contains_cape_crozier_literal":any("crozier" in s.lower() for s in names),
        "colony_name_roster":names,
        "source_years":sorted(years.values()),
        "value_classes":dict(value_types),
        "surveyed_positive_zero_missing_by_year":{
            str(yr):dict(byyear[yr]) for yr in sorted(byyear)},
        "source_count_zeros_not_conflated_with_missing":True,
        "source_count_not_individual_survival_or_dispersion":True,
        "Cape_Barne_missing_from_roster_if_absent_not_proof_of_2024_extinction":True,
        "source_2020_text_field_retained_as_numeric_only_when_parseable":True,
        "no_new_ecological_model_fitted":True,
        "author_license":"CC-BY-NC 4.0",
        "PR189_science_unmodified":True
    }
    return report

def run():
    report={"status":"HOLD_NZ_CENSUS_OFFICIAL_SOURCE_ACCESS",
            "source_metadata_endpoint":API,
            "resource_id":RESOURCE_ID,
            "actual_penguin_colony_rows_parsed":0,
            "new_causal_immigration_effect":False,
            "PR189_science_unmodified":True}
    try:
        req=API+"?"+urlencode({"id":RESOURCE_ID})
        meta=official_metadata(fetch_bounded(req,MAX_SOURCE_METADATA))
        report["official_source_metadata"]=meta
        data=fetch_bounded(meta["url"])
        result=evaluate_xlsx(data)
        report.update(result)
        report["status"]="SOURCE_XLSX_VALIDATED_AND_STRUCTURAL_COVERAGE_REPORTED"
        report["actual_penguin_colony_rows_parsed"]=result["n_named_nonaggregate_source_rows"]
    except Exception as e:
        report["status"]="HOLD_OFFICIAL_SOURCE_SCHEMA_OR_ACCESS"
        report["error_type"]=type(e).__name__
        report["error_message"]=str(e)[:250]
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    opts=p.parse_args()
    z=run()
    opts.out.write_text(json.dumps(z,indent=2)+"\n",encoding="utf-8")
    print("ROSS_NZ_39_COLONY_SOURCE",z["status"])
    print("SOURCE_FILE_MD5",z.get("verified_md5","UNKNOWN"))
    print("COLONY_ROWS",z.get("n_named_nonaggregate_source_rows","UNKNOWN"))
    print("CAPE_BARNE_PRESENT",z.get("contains_cape_barne_literal","UNKNOWN"))
    print("YEAR_COUNT",len(z.get("source_years",[])))
    print("SOURCE_CLASSES",json.dumps(z.get("value_classes",{}),sort_keys=True))
    print("ERROR_IF_HELD",z.get("error_type",""),z.get("error_message",""))
    print("NO_PENGUIN_DEMOGRAPHIC_CAUSAL_EFFECT_FITTED")
if __name__=="__main__":main()
