#!/usr/bin/env python3
"""V29 original source matched-site comparative cohort, no source abundance magnitudes."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,posixpath,re,zipfile
from collections import Counter,defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET
import audit_jncc_two_censuses_source_v28 as source

ORIGINAL_SHA="9edf05b8af0a44c3ca770f390120c4b99bcaae3ae35fd844a82982d6ad8116d4"
COLS=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R"]
UNITS={"AON","AOS","AOT","AOB","IND"}
MIN_PANELS=20;MIN_SPECIES=8;MIN_MASTERS=15;MIN_UNITS=3
REQUIRED={
 "A":"Species","B":"Country","C":"Admin Area/\nCounty","D":"Master site",
 "E":"Site","F":"Site.ID","I":"Start.Lat","J":"Start.Long",
 "K":"S. 2000 Year","L":"S.2000 adjusted count","M":"Count Unit (S.2000)",
 "N":"Seabirds Count Year","O":"Seabirds Count adjusted count",
 "P":"Count Unit (Seabirds Count)"
}
MAIN="1_SC_S2K_dataset"
PUFFIN="3_Atlantic_Puffin_comparable"

def typed_strings(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if "xl/sharedStrings.xml" not in z.namelist():return []
        root=ET.fromstring(z.read("xl/sharedStrings.xml"))
        return ["".join(t.text or "" for t in s.findall(".//{%s}t"%source.MAIN))
                for s in root.findall("{%s}si"%source.MAIN)]

def original_rows(raw, sheet_names=(MAIN,PUFFIN)):
    """Read sheet only; data count CELL VALUES are later used lexically, not numerically."""
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        shared=typed_strings(raw)
        book=ET.fromstring(z.read("xl/workbook.xml"))
        rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        paths={x.attrib["Id"]:x.attrib["Target"]
               for x in rel.findall("{%s}Relationship"%source.PKG)}
        sheet_paths={}
        for child in book.findall(".//{%s}sheet"%source.MAIN):
            rid=child.attrib.get("{%s}id"%source.REL)
            if rid not in paths:raise ValueError("SOURCE_STOP broken Excel sheet ref")
            dest=paths[rid]
            name=posixpath.normpath(dest.lstrip("/") if dest.startswith("/xl/")
                                   else "xl/"+dest)
            sheet_paths[child.attrib.get("name")]=name
        if not set(sheet_names).issubset(sheet_paths):
            raise ValueError("SOURCE_STOP original JNCC survey sheets changed")
        for sheet in sheet_names:
            root=ET.fromstring(z.read(sheet_paths[sheet]))
            for row in root.findall(".//{%s}sheetData/{%s}row"%(source.MAIN,source.MAIN)):
                index=int(row.attrib.get("r",0))
                if index<4:continue
                out={}
                for cell in row.findall("{%s}c"%source.MAIN):
                    addr=cell.attrib.get("r","")
                    pattern=re.match(r"([A-Z]+)\d+",addr)
                    if pattern is None:raise ValueError("SCHEMA_STOP invalid Excel address")
                    col=pattern.group(1)
                    if col not in COLS:continue
                    txt=source.text_cell(cell,shared)
                    if txt!="":
                        out[col]=txt.strip()
                    else:
                        val=cell.find("{%s}v"%source.MAIN)
                        out[col]=str(val.text).strip() if val is not None and val.text is not None else ""
                yield sheet,index,out

def original_int(val):
    s=str(val or "").strip()
    if not re.fullmatch(r"\d+(?:\.0+)?",s):return None
    n=int(float(s))
    return n

def numeric_presence(val):
    """Never convert COUNT magnitude, check only lexical non-negative finite candidate."""
    s=str(val or "").strip()
    return bool(re.fullmatch(r"(?:0|[1-9]\d*)(?:\.\d+)?",s))

def eligible_metadata(sheet,idx,rec):
    if idx==4:return None,"header"
    if not (rec.get("A") and rec.get("B") and rec.get("D") and rec.get("F")):
        return None,"missing_species_country_master_or_ID"
    species=rec["A"].strip()
    if sheet==MAIN and "Atlantic Puffin" in species:
        return None,"puffin_removed_from_general_sheet"
    if sheet==PUFFIN:
        if species!="Comparable - Atlantic Puffin":
            return None,"puffin_not_explicitly_comparable"
        species="Atlantic Puffin"
    n=original_int(rec["F"])
    if n is None or n<=0:return None,"noninteger_source_site_ID"
    try:
        lat=float(rec.get("I",""));lon=float(rec.get("J",""))
        if not (math.isfinite(lat) and math.isfinite(lon) and
                48<=lat<=62.5 and -13<=lon<=3):return None,"geographic_out_of_scope"
    except (ValueError,TypeError):
        return None,"invalid_source_coordinates"
    earlier=original_int(rec.get("K"))
    later=original_int(rec.get("N"))
    if earlier is None or not 1998<=earlier<=2005 or later is None or not 2015<=later<=2021:
        return None,"missing_or_out_of_study_original_survey_year"
    u0=rec.get("M","").strip().upper()
    u1=rec.get("P","").strip().upper()
    if u0 not in UNITS or u0!=u1:
        return None,"unit_incompatible_unknown_or_changed"
    if not numeric_presence(rec.get("L")) or not numeric_presence(rec.get("O")):
        return None,"NA_missing_or_non_numeric_two_census_measurement"
    return {
       "species":species,"country":rec["B"].strip(),
       "master":rec["D"].strip(),"site_id":str(n),"unit":u0,
       "source_sheet":sheet,"source_row":idx,"lat":lat,"lon":lon,
       "year_2000":earlier,"year_recent":later,
       # deliberately no original L/O numeric magnitudes retained or emitted
    },None

def coverage(rows):
    if not rows:raise ValueError("SOURCE_STOP no comparison rows")
    attempts=Counter();unique=defaultdict(list);sheet_count=Counter()
    for sheet,idx,rec in rows:
        sheet_count[sheet]+=1
        if idx==4:
            for col,label in REQUIRED.items():
                if rec.get(col,"").strip()!=label.strip():
                    raise ValueError("SCHEMA_STOP publisher comparable header changed "+col)
            continue
        item,why=eligible_metadata(sheet,idx,rec)
        if why is not None:
            attempts[why]+=1;continue
        key=(item["species"],item["country"],item["master"],item["site_id"])
        unique[key].append(item)
    dup={key:items for key,items in unique.items() if len(items)>1}
    valid=[items[0] for key,items in unique.items() if len(items)==1]
    panels=defaultdict(list)
    for item in valid:
        panels[(item["species"],item["country"],item["master"],item["unit"])].append(item)
    qualified={key:rows for key,rows in panels.items() if len(rows)>=3}
    sites={z["site_id"] for group in qualified.values() for z in group}
    masters={(k[1],k[2]) for k in qualified}
    species={k[0] for k in qualified}
    units={k[3] for k in qualified}
    gate=(len(qualified)>=MIN_PANELS and len(species)>=MIN_SPECIES
          and len(masters)>=MIN_MASTERS and len(units)>=MIN_UNITS)
    mainqual=dict(Counter(k[0] for k in qualified))
    counts_per_panel=Counter(str(min(15,len(v))) for v in qualified.values())
    return {
      "original_source_row_records_by_worksheet":dict(sheet_count),
      "original_source_exclusion_reasons":dict(attempts),
      "entire_duplicate_species_master_site_ID_keys_excluded":len(dup),
      "source_rows_dropped_for_duplicate_key_groups":sum(map(len,dup.values())),
      "unique_original_two_census_site_species_rows_after_literal_QA":len(valid),
      "qualified_species_country_master_unit_panels_with_ge3_sites":len(qualified),
      "qualified_distinct_seabird_species":len(species),
      "qualified_distinct_country_master_site_networks":len(masters),
      "qualified_distinct_source_site_IDs":len(sites),
      "qualified_distinct_biological_count_units":len(units),
      "qualified_panels_by_species":dict(sorted(mainqual.items())),
      "qualified_panels_by_unit":dict(Counter(k[3] for k in qualified)),
      "qualified_panel_size_at_most_15_counts":dict(counts_per_panel),
      "frozen_eligibility_gate_pass":bool(gate),
      "source_row_identity_is_not_verified_historical_polygon_crosswalk":True,
      "source_site_IDs_not_physical_island_IDs":True,
      "source_original_animal_magnitudes_accessed":0,
      "source_two_epoch_comparison_not_annual_synchrony":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result={"status":"HOLD_ORIGINAL_JNCC_SOURCE","effect_fitted":False}
    try:
        raw,rec=source.download_original()
        if rec["original_sha256"]!=ORIGINAL_SHA:
            raise ValueError("SOURCE_STOP original JNCC XLSX SHA256 changed")
        qa=coverage(original_rows(raw))
        result={"status":"V29_JNCC_SOURCE_PAIR_IDENTITY_PANEL_GATE",
                "original_publisher_sha256":ORIGINAL_SHA,
                "source_DOI_or_resource":"https://jncc.gov.uk/resources/63f0ea40-485d-46dd-b967-150df90a7b2b",
                "original_panel_support":qa,"ecological_effect_fitted":False,
                "scientific_decision":("READY_FOR_INDEPENDENT_GIS_SITE_IDENTITY_AND_OUTCOME_CONTRACT"
                    if qa["frozen_eligibility_gate_pass"] else
                    "STOP_INSUFFICIENT_TAXONOMIC_OR_SITE_PANEL_COVERAGE")}
    except Exception as exc:
        result["error_type"]=type(exc).__name__
        result["error"]=str(exc)[:800]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"]=="HOLD_ORIGINAL_JNCC_SOURCE":raise SystemExit(2)
if __name__=="__main__":main()
