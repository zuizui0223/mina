#!/usr/bin/env python3
"""V33. CKAN-publisher original 2026 Ross Sea 39-colony census SOURCE coverage.

Standard-library XLSX ZIP reader deliberately never exports bird count values.
Outputs raw SHA/checksum, true source sheet names, colony IDs and year presence.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import hashlib
import io
import json
import math
from pathlib import Path
import posixpath
import re
import requests
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
from zipfile import ZipFile

HOST="datastore.landcareresearch.co.nz"
PACKAGE="fb407798-f399-4875-81a0-51976b4c759c"
API="https://"+HOST+"/api/3/action/package_show?id=adelie-penguin-census-data"
DOI="https://doi.org/10.7931/kf06-x745"
RESOURCES={
 "census":("5fd490e5-92c4-4f2c-a82e-c66db2320eb1",12578,"195a9027a0d18012812b09fb345ac60e"),
 "locations":("f82c5e1d-f04d-446d-9338-e9d0603360f8",8025,""),
 "methods_pdf":("e081bd92-4e27-44eb-8d5b-065906e97cc2",29666,""),
}
NS={"main":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkg":"http://schemas.openxmlformats.org/package/2006/relationships"}
MAX_RAW=250000
MAX_SHEETS=15
MAX_SOURCE_CELLS=90000
MIN_COLONIES_WITH_5YEARS=20
MIN_YEARS_WITH_5COLONIES=10
YEARS=range(1981,2025)

def get(session,url,cap,expect_json=False):
    p=urlparse(url)
    if p.scheme!="https" or p.hostname!=HOST:
        raise ValueError("SOURCE_STOP untrusted CKAN source URL")
    with session.get(url,stream=True,timeout=(18,75),headers={
        "User-Agent":"mina-ross-sea-original-39-colonies-research/1.0"
    }) as response:
        response.raise_for_status()
        end=urlparse(response.url)
        if end.scheme!="https" or not (end.hostname==HOST or
              end.hostname.endswith(".landcareresearch.co.nz")):
            raise ValueError("SOURCE_STOP original download redirected outside publisher")
        buf=bytearray()
        for block in response.iter_content(16384):
            if not block:continue
            buf.extend(block)
            if len(buf)>cap:raise ValueError("SOURCE_STOP original payload oversized")
        data=bytes(buf)
        if not data:raise ValueError("SOURCE_STOP original source empty")
        if expect_json and not data[:1]==b"{":
            raise ValueError("SOURCE_STOP CKAN API did not return JSON")
        return data,{"byte_length":len(data),
                     "sha256":hashlib.sha256(data).hexdigest(),
                     "md5":hashlib.md5(data).hexdigest(),
                     "final_publisher_host":end.hostname}

def ckandownloads(session):
    data,api_source=get(session,API,MAX_RAW,True)
    packet=json.loads(data)
    if not packet.get("success") or not isinstance(packet.get("result"),dict):
        raise ValueError("SOURCE_STOP original CKAN metadata invalid")
    item=packet["result"]
    if str(item.get("id",""))!=PACKAGE or str(item.get("doi",""))!=DOI:
        raise ValueError("SOURCE_STOP original Ross Sea dataset version/DOI drift")
    if item.get("private") is True:
        raise ValueError("SOURCE_STOP source data marked private")
    if item.get("license_id")!="CC-BY-NC-4.0":
        raise ValueError("SOURCE_STOP licence changed; inspect before downloading")
    resource_index={r.get("id"):r for r in item.get("resources",[])}
    found={}
    for label,(uuid,size,md5) in RESOURCES.items():
        r=resource_index.get(uuid)
        if not r or r.get("size")!=size:
            raise ValueError("SOURCE_STOP publisher resource missing or size changed: "+label)
        if md5 and r.get("hash")!=md5:
            raise ValueError("SOURCE_STOP publisher original checksum metadata changed")
        url=str(r.get("url",""))
        source,metadata=get(session,url,MAX_RAW)
        if len(source)!=size:
            raise ValueError("SOURCE_STOP source advertised byte size not equal delivered bytes")
        if md5 and metadata["md5"]!=md5:
            raise ValueError("SOURCE_STOP original source MD5 mismatch")
        found[label]={"raw":source,
                      "receipt":{**metadata,"resource_uuid":uuid,
                                 "publisher_filename":url.rsplit("/",1)[-1],
                                 "publisher_resource_metadata_modified":r.get("metadata_modified")}}
    return found,{"source_dataset_DOI":DOI,"publisher_CKAN_dataset_uuid":PACKAGE,
                  "publisher_source_license_id":item.get("license_id"),
                  "publisher_start_year":item.get("start_date"),
                  "publisher_end_year":item.get("end_date"),
                  "publisher_data_last_modified":item.get("metadata_modified"),
                  "publisher_original_CKAN_manifest_sha256":api_source["sha256"]}

def local(tag):return tag.rsplit("}",1)[-1]

def parse_year(v):
    if isinstance(v,bool) or v is None:return None
    if isinstance(v,(int,float)):
        if int(v)==v and v in YEARS:return int(v)
        return None
    text=str(v).strip()
    if re.fullmatch(r"(?:19|20)\d{2}",text):
        y=int(text)
        return y if y in YEARS else None
    match=re.fullmatch(r"((?:19|20)\d{2})[-/](\d{2}|\d{4})",text)
    if not match:return None
    y=int(match.group(1));end=int(match.group(2))
    return y if y in YEARS and (end==(y+1)%100 or end==y+1) else None

def num_present(v):
    """Validate original numeric token but never expose any count magnitude."""
    if v is None or isinstance(v,bool):return False
    if isinstance(v,(int,float)):
        return math.isfinite(v) and 0<=v<1e10
    s=str(v).strip().replace(",","")
    if not re.fullmatch(r"(?:0|[1-9]\d*)(?:\.\d+)?",s):
        return False
    try:
        value=float(s)
        return math.isfinite(value) and 0<=value<1e10
    except ValueError:return False

def colnum(cell):
    m=re.match(r"([A-Z]+)",cell or "")
    if not m:raise ValueError("SCHEMA_STOP invalid Excel cell A1 reference")
    c=0
    for ch in m.group(1):
        c=c*26+ord(ch)-64
    return c-1

def workbook_original(raw):
    if not raw.startswith(b"PK"):
        raise ValueError("SOURCE_STOP original advertised XLSX not ZIP")
    out={}
    with ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None or "xl/workbook.xml" not in z.namelist():
            raise ValueError("SCHEMA_STOP invalid XLSX archive")
        names=z.namelist()
        if len(names)>150:raise ValueError("SCHEMA_STOP too many XLSX members")
        shared=[]
        if "xl/sharedStrings.xml" in names:
            sr=ET.fromstring(z.read("xl/sharedStrings.xml"))
            for entry in sr.findall("main:si",NS):
                shared.append("".join(t.text or "" for t in entry.iter() if local(t.tag)=="t"))
        workbook=ET.fromstring(z.read("xl/workbook.xml"))
        rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        relmap={r.get("Id"):r.get("Target") for r in rels if local(r.tag)=="Relationship"}
        sheets=workbook.findall("main:sheets/main:sheet",NS)
        if len(sheets)>MAX_SHEETS:raise ValueError("SCHEMA_STOP too many original source sheets")
        for entry in sheets:
            sheetname=entry.get("name")
            rid=entry.get("{"+NS["rel"]+"}id")
            target=relmap.get(rid)
            if not target:raise ValueError("SCHEMA_STOP original Excel sheet relationship missing")
            member=(target.lstrip("/") if target.startswith("/") else
                    posixpath.normpath(posixpath.join("xl",target)))
            if member not in names:
                raise ValueError("SCHEMA_STOP original worksheet source missing "+member)
            root=ET.fromstring(z.read(member))
            matrix={}
            count=0
            for row in root.findall(".//main:sheetData/main:row",NS):
                num=int(row.get("r","0"))
                if num<=0 or num>6000:raise ValueError("SCHEMA_STOP invalid sheet row")
                cells={}
                for node in row.findall("main:c",NS):
                    col=colnum(node.get("r"))
                    t=node.get("t","n")
                    val=node.find("main:v",NS)
                    inline=node.find("main:is",NS)
                    if t=="s" and val is not None:
                        key=int(val.text)
                        content=shared[key]
                    elif t=="inlineStr" and inline is not None:
                        content="".join(x.text or "" for x in inline.iter() if local(x.tag)=="t")
                    elif t=="b" and val is not None:
                        content=val.text=="1"
                    elif val is not None and val.text is not None:
                        if t in ("n",""):
                            try:content=float(val.text)
                            except ValueError:content=None
                        else:content=val.text
                    else:content=None
                    if content is not None:cells[col]=content
                    count+=1
                    if count>MAX_SOURCE_CELLS:
                        raise ValueError("SOURCE_STOP original workbook too many source cells")
                matrix[num-1]=cells
            out[sheetname]=matrix
    return out

def nice_label(v):
    if not isinstance(v,str):return None
    val=v.strip()
    if not val or len(val)>130 or re.fullmatch(r"[+\-]?(?:\d+(?:\.\d+)?)",val):
        return None
    return val

def aggregate_name(s):
    return bool(re.search(r"\b(total|subtotal|all colonies|sum|aggregate|overall)\b",s,re.I))

def summarize_matrix(matrix):
    """Structural presence only; NO count magnitude returned."""
    rows=sorted(matrix)
    years_by_col=defaultdict(set)
    for index in rows:
        for col in range(4):
            year=parse_year(matrix[index].get(col))
            if year is not None:years_by_col[col].add(year)
    candidate_year_col=max(years_by_col,key=lambda i:len(years_by_col[i])) if years_by_col else None
    year_col_score=len(years_by_col.get(candidate_year_col,set()))
    header_candidates=[]
    for row in rows[:12]:
        values=matrix[row]
        ys={col:parse_year(val) for col,val in values.items() if parse_year(val) is not None}
        if len(ys)>=8:
            header_candidates.append((len(ys),row,ys))
    wide=max(header_candidates,key=lambda r:r[0]) if header_candidates else None
    horizontal_score=wide[0] if wide else 0
    if horizontal_score<8 and year_col_score<8:
        return {"status":"HOLD_UNRESOLVED_PUBLISHER_MATRIX_ORIENTATION",
                "years_found_in_header":horizontal_score,
                "years_found_in_first_four_columns":year_col_score,
                "source_count_values_opened":0}
    # In header-with-year-column format, original named colonies are in rows.
    if horizontal_score>year_col_score:
        orientation="ROWS_COLONY_COLUMNS_YEAR"
        header_row=wide[1]
        yearcols={c:y for c,y in wide[2].items()}
        bysite={}
        dup=Counter()
        for row in rows:
            if row<=header_row:continue
            rec=matrix[row]
            labels=[nice_label(rec.get(c)) for c in range(4)]
            labels=[s for s in labels if s and parse_year(s) is None]
            if not labels:continue
            name=labels[0]
            if aggregate_name(name):continue
            if name in bysite:
                dup[name]+=1
                continue
            bysite[name]={year for col,year in yearcols.items() if num_present(rec.get(col))}
        for name in dup:bysite.pop(name,None)
        headinfo={"original_year_header_row":header_row+1,
                  "original_source_calendar_year_column_count":len(yearcols)}
    else:
        orientation="ROWS_YEAR_COLUMNS_COLONY"
        if candidate_year_col is None:
            raise ValueError("SCHEMA_STOP original calendar year column not selected")
        years_rows={r:parse_year(matrix[r].get(candidate_year_col))
                    for r in rows if parse_year(matrix[r].get(candidate_year_col)) is not None}
        dupyears=Counter(years_rows.values())
        stable={r:y for r,y in years_rows.items() if dupyears[y]==1}
        firstyear=min(stable) if stable else None
        first_data_row=min(stable) if stable else None
        header_rows=[r for r in rows if r<first_data_row] if first_data_row is not None else []
        # Last declared textual header row before original observations.
        header_row=max(header_rows) if header_rows else 0
        header=matrix.get(header_row,{})
        names={c:nice_label(v) for c,v in header.items() if c!=candidate_year_col and nice_label(v)}
        names={c:n for c,n in names.items() if not aggregate_name(n) and parse_year(n) is None}
        dupnames=Counter(names.values())
        names={c:n for c,n in names.items() if dupnames[n]==1}
        bysite={name:{y for row,y in stable.items() if num_present(matrix[row].get(c))}
                for c,name in names.items()}
        headinfo={"original_source_colony_header_row":header_row+1,
                  "original_year_data_column_1_based":candidate_year_col+1,
                  "original_distinct_calendar_year_keys":len(stable),
                  "duplicate_original_year_keys_excluded":sorted(y for y,num in dupyears.items() if num>1)}
    byyear=Counter(y for yrs in bysite.values() for y in yrs)
    sites=[{"colony":name,"original_numeric_present_years":len(ys),
            "original_first_last_numeric_years":[min(ys),max(ys)] if ys else None}
           for name,ys in sorted(bysite.items())]
    fiveyears=sum(len(v)>=5 for v in bysite.values())
    adjacents=sum(sum(y+1 in ys for y in ys) for ys in bysite.values())
    comparable_years={str(y):int(byyear[y]) for y in YEARS}
    output={
        "status":"SOURCE_COLONY_YEAR_PRESENCE_ONLY",
        "source_year_colony_orientation":orientation,
        **headinfo,
        "n_distinct_colony_labels":len(bysite),
        "n_colonies_with_ge5_measured_years":fiveyears,
        "n_source_years_with_ge5_measured_colonies":sum(n>=5 for n in byyear.values()),
        "n_source_years_with_ge10_measured_colonies":sum(n>=10 for n in byyear.values()),
        "original_source_2020_number_of_explicit_numeric_cells":int(byyear[2020]),
        "original_numeric_present_colonies_by_year":comparable_years,
        "within_colony_consecutive_year_opportunities":int(adjacents),
        "source_colony_coverage":sites,
        "source_records_are_not_confirmed_independent_physical_islands":True,
        "source_missing_or_unobserved_is_never_biological_zero":True,
        "count_or_population_magnitudes_used":0,
        "predeclared_source_colony_and_year_support_pass":(
            fiveyears>=MIN_COLONIES_WITH_5YEARS and sum(n>=5 for n in byyear.values())>=MIN_YEARS_WITH_5COLONIES),
        "island_level_effect_gate":"HOLD_GEOGRAPHIC_ISLAND_BOUNDARY_AND_SURVEY_PROTOCOL",
    }
    return output

def location_structure(book):
    reports=[]
    for name,matrix in book.items():
        if not matrix:continue
        first=[]
        for idx in sorted(matrix)[:5]:
            fields=[nice_label(v) for c,v in sorted(matrix[idx].items()) if c<40]
            if any(fields):first.append({"row":idx+1,"text_headers":[s for s in fields if s][:20]})
        reports.append({"sheet":name,"source_excel_rows":max(matrix)+1,
                        "first_5_text_rows":first,"numeric_location_values_opened":0})
    return reports

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--json",type=Path,required=True)
    args=p.parse_args()
    out={"status":"HOLD_ORIGINAL_2026_ROSS_SEA_SOURCE","ecological_effects_fitted":0}
    try:
        with requests.Session() as session:
            found,source=ckandownloads(session)
        for label in ("census","locations"):
            if not found[label]["raw"].startswith(b"PK"):
                raise ValueError("SOURCE_STOP original XLSX payload not spreadsheet for "+label)
        if not found["methods_pdf"]["raw"].startswith(b"%PDF"):
            raise ValueError("SOURCE_STOP original publisher field metadata PDF invalid")
        count_book=workbook_original(found["census"]["raw"])
        loc_book=workbook_original(found["locations"]["raw"])
        census_struct={
            name:{"sheet_declared_rows":max(mat)+1 if mat else 0,
                  "source_declared_nonempty_cells":sum(len(row) for row in mat.values()),
                  "source_support":summarize_matrix(mat)}
            for name,mat in count_book.items()
        }
        source_pass=any(
            v["source_support"].get("predeclared_source_colony_and_year_support_pass",False)
            for v in census_struct.values())
        out={
            "status":"V33_ORIGINAL_NEW_ZEALAND_ROSS_SEA_SOURCE_PANEL_AUDITED",
            "original_CKAN_metadata":source,
            "actual_original_resource_receipts":{
                label:resource["receipt"] for label,resource in found.items()
            },
            "2026_original_census_sheet_support":census_struct,
            "original_colony_geography_workbook_structure":location_structure(loc_book),
            "source_colony_coverage_gate_pass":bool(source_pass),
            "survey_effort_comparability_verified":False,
            "site_to_true_physical_island_crosswalk_verified":False,
            "independent_geographical_island_count":None,
            "2020_source_no_surveys_not_zero_penguins":True,
            "original_bird_count_values_reprinted":0,
            "ecological_effects_fitted":0,
            "scientific_decision":(
                "PROCEED_ORIGINAL_SITE_ISLAND_CROSSWALK_WITHOUT_OUTCOME_INSPECTION"
                if source_pass else "HOLD_INSUFFICIENT_OR_UNRESOLVED_ORIGINAL_SITE_YEAR_STRUCTURE"
            )
        }
    except Exception as exc:
        out["error_type"]=type(exc).__name__
        out["error"]=str(exc)[:750]
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False))
    if out["status"]=="HOLD_ORIGINAL_2026_ROSS_SEA_SOURCE":
        raise SystemExit(2)

if __name__=="__main__":
    main()
