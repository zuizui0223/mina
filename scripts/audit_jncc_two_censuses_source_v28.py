#!/usr/bin/env python3
"""JNCC 2024 revision xlsx original publisher source-only structural/headers audit.

No Excel cell numeric magnitude is exposed or used in this inventory. Only
ZIP+OOXML integrity, original text heading candidates and sheet dimensions.
"""
import argparse,hashlib,json,posixpath,re,zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
import requests

URL="https://data.jncc.gov.uk/data/63f0ea40-485d-46dd-b967-150df90a7b2b/comparative-seabirds-count-dataset-revised-20240708.xlsx"
MAX_SOURCE=12*1024*1024
MAX_UNPACKED=140*1024*1024
MAIN="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG="http://schemas.openxmlformats.org/package/2006/relationships"

def download_original(url=URL,session=None):
    if urlparse(url).hostname!="data.jncc.gov.uk" or urlparse(url).scheme!="https":
        raise ValueError("SOURCE_STOP non-publisher original URL")
    s=session or requests.Session()
    try:
        r=s.get(url,stream=True,timeout=55,allow_redirects=True,
                headers={"User-Agent":"mina-jncc-source-structure-v28/1.0"})
        p=urlparse(r.url)
        if p.scheme!="https" or p.hostname!="data.jncc.gov.uk":
            raise ValueError("SOURCE_STOP non-JNCC redirected source")
        r.raise_for_status()
        bufs=[];size=0
        for c in r.iter_content(chunk_size=65536):
            size+=len(c)
            if size>MAX_SOURCE:
                raise ValueError("SOURCE_STOP original xlsx exceeds bound")
            bufs.append(c)
        original=b"".join(bufs)
        if not original.startswith(b"PK"):
            raise ValueError("SOURCE_STOP unexpected non-XLSX body")
        return original,{"publisher_url":url,"final_url":r.url,
                         "publisher_content_type":r.headers.get("Content-Type"),
                         "original_bytes":len(original),
                         "original_sha256":hashlib.sha256(original).hexdigest()}
    finally:
        if session is None:s.close()

def text_cell(c,strings):
    typ=c.attrib.get("t","")
    if typ=="s":
        val=c.find("{%s}v"%MAIN)
        if val is None or val.text is None:return ""
        i=int(val.text)
        if i<0 or i>=len(strings):raise ValueError("SCHEMA_STOP broken original shared string ID")
        return strings[i]
    if typ=="inlineStr":
        return "".join(t.text or "" for t in c.findall(".//{%s}is//{%s}t"%(MAIN,MAIN)))
    if typ in ("str","e"):
        val=c.find("{%s}v"%MAIN)
        return (val.text or "") if val is not None else ""
    return ""

def inspect_source(raw):
    import io
    if not raw.startswith(b"PK"):
        raise ValueError("SOURCE_STOP no original Office ZIP magic")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=z.namelist()
        if len(names)>800 or z.testzip() is not None:
            raise ValueError("SOURCE_STOP invalid/corrupted/oversized ZIP member index")
        total=0
        for info in z.infolist():
            path=PurePosixPath(info.filename)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("SOURCE_STOP malicious XLSX member name")
            total+=info.file_size
        if total>MAX_UNPACKED:
            raise ValueError("SOURCE_STOP decompress size too large")
        if "xl/workbook.xml" not in names or "xl/_rels/workbook.xml.rels" not in names:
            raise ValueError("SCHEMA_STOP XLSX workbook relationships missing")
        strings=[]
        if "xl/sharedStrings.xml" in names:
            root=ET.fromstring(z.read("xl/sharedStrings.xml"))
            for item in root.findall("{%s}si"%MAIN):
                strings.append("".join(t.text or "" for t in item.findall(".//{%s}t"%MAIN)))
        book=ET.fromstring(z.read("xl/workbook.xml"))
        rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        target={r.attrib["Id"]:r.attrib["Target"] for r in rels.findall("{%s}Relationship"%PKG)}
        sheets=[]
        for s in book.findall(".//{%s}sheet"%MAIN):
            name=s.attrib.get("name","")
            rid=s.attrib.get("{%s}id"%REL)
            if not rid or rid not in target:
                raise ValueError("SCHEMA_STOP invalid workbook relationship")
            raw_path=target[rid]
            path=posixpath.normpath(raw_path.lstrip("/") if raw_path.startswith("/xl/") else
                                  ("xl/"+raw_path if not raw_path.startswith("/") else raw_path.lstrip("/")))
            if path not in names or not path.startswith("xl/worksheets/"):
                raise ValueError("SCHEMA_STOP missing original worksheet XML")
            data=z.read(path)
            root=ET.fromstring(data)
            dim=root.find("{%s}dimension"%MAIN)
            dval=dim.attrib.get("ref") if dim is not None else None
            head=[];rows=0;nonempty=Counter();numbers=Counter();toprows=[]
            for row in root.findall(".//{%s}sheetData/{%s}row"%(MAIN,MAIN)):
                cells=row.findall("{%s}c"%MAIN)
                if not cells:continue
                rows+=1
                if rows>300000:
                    raise ValueError("SCHEMA_STOP unexpectedly large original worksheet")
                texts=[]
                for cell in cells:
                    addr=cell.attrib.get("r","")
                    cm=re.match(r"([A-Z]+)\d+",addr)
                    if not cm:raise ValueError("SCHEMA_STOP invalid cell address")
                    col=cm.group(1)
                    val=cell.find("{%s}v"%MAIN)
                    txt=text_cell(cell,strings)
                    if txt.strip() or val is not None and val.text not in (None,""):
                        nonempty[col]+=1
                    if cell.attrib.get("t","") not in ("s","inlineStr","str","e","b") and val is not None and val.text not in (None,""):
                        numbers[col]+=1
                    if rows<=12 and txt.strip():
                        texts.append({"column":col,"source_text":txt[:3000] if name=="Coversheet" else txt[:160]})
                if rows<=12:
                    toprows.append({"original_row_number":row.attrib.get("r"),
                                    "source_text_cells":texts[:35]})
            sheets.append({"original_name":name,"original_xml_path":path,
                           "original_declared_dimension":dval,
                           "original_nonempty_xml_rows":rows,
                           "original_nonempty_cell_counts_by_column":dict(nonempty),
                           "original_numeric_cell_presence_by_column":dict(numbers),
                           "first_12_source_text_rows":toprows,
                           "source_animal_count_magnitudes_accessed":0})
        return {"original_sheet_count":len(sheets),
                "original_shared_strings_count":len(strings),
                "sheets":sheets,"archive_uncompressed_bytes":total,
                "biological_effect_models_fit":0}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    result={"status":"HOLD_PUBLISHER_OR_SCHEMA","effect_fitted":False}
    try:
        source,receipt=download_original()
        structural=inspect_source(source)
        result={"status":"JNCC_2024_REVISED_ORIGINAL_STRUCTURE_AUDITED",
                "original_publisher":receipt,
                "structure":structural,
                "ecological_effect_fitted":False,
                "scientific_decision":"STRUCTURAL_SOURCE_READY_HEADER_AND_ID_GATE_PENDING"}
    except Exception as exc:
        result["error_type"]=type(exc).__name__
        result["error"]=str(exc)[:700]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"]=="HOLD_PUBLISHER_OR_SCHEMA":
        raise SystemExit(2)
if __name__=="__main__":main()
