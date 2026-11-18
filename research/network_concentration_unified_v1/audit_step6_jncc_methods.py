#!/usr/bin/env python3
"""JNCC source measurement comparability audit against FIXED Step1 663 responses.

This is an after-result, noninferential method-support audit. It never modifies
the original Step1 network species outcomes, Step3 contract, or Step4 coefficients.
Raw original publisher-level site counts are NOT written to the repository.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
OUT = BASE / "outputs"
DATA = BASE / "data"
ORIGINAL = ROOT / "build/step1_inputs/jncc.xlsx"
PARSERS = ROOT / "build/step1_inputs/jncc_code"
ORIGINAL_SHA = "9edf05b8af0a44c3ca770f390120c4b99bcaae3ae35fd844a82982d6ad8116d4"
SOURCE_BLOB_SHA = "e089c4525226c156a1554ce4f480a7611c946ae7"
ORIGINAL_PANEL_N = 1483
MAIN_JNCC_N = 663


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def positive(row):
    return float(row["concentration_excess_decade"]) > 0


def stats(rows):
    n = len(rows)
    by_species = defaultdict(list)
    by_network = set()
    for r in rows:
        by_species[r["species_id"]].append(float(r["concentration_excess_decade"]))
        by_network.add(r["network_id"])
    means = [statistics.mean(vals) for vals in by_species.values()]
    values = [float(r["concentration_excess_decade"]) for r in rows]
    return {
        "n_rows": n,
        "n_networks": len(by_network),
        "n_species": len(by_species),
        "positive": sum(positive(r) for r in rows),
        "negative": sum(float(r["concentration_excess_decade"]) < 0 for r in rows),
        "fraction_positive": sum(positive(r) for r in rows) / n if n else None,
        "species_with_positive_mean": sum(m > 0 for m in means),
        "species_equal_mean_excess_decade": statistics.mean(means) if means else None,
        "median_excess_decade": statistics.median(values) if values else None,
        "declining_rows": sum(float(r["N1"]) < float(r["N0"]) for r in rows),
    }


def main():
    if not ORIGINAL.exists() or not PARSERS.exists():
        raise FileNotFoundError("Fixed original JNCC XLSX and pinned parsers must be recovered by Actions")
    raw = ORIGINAL.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("Publisher JNCC original file byte identity changed")
    sys.path.insert(0, str(PARSERS))
    import audit_jncc_comparable_site_panels_v29 as v29
    import model_jncc_component_concentration_v30 as v30
    source = list(v29.original_rows(raw))
    original_cover = v29.coverage(source)
    if (original_cover["unique_original_two_census_site_species_rows_after_literal_QA"] != 14112
        or original_cover["qualified_species_country_master_unit_panels_with_ge3_sites"] != 1485):
        raise ValueError("Pinned V29 source gate changed")
    safe, original_structural = v30.extract_structural(source)
    if len(safe) != ORIGINAL_PANEL_N:
        raise ValueError("Guarded original JNCC panels changed")
    headers = {}
    for sheet, i, record in source:
        if i == 4 and sheet not in headers:
            headers[sheet] = {col: val for col, val in record.items() if val.strip()}
    if len(headers) != 2:
        raise ValueError("Original comparison sheets changed")
    for sheet, head in headers.items():
        for col, expected in v29.REQUIRED.items():
            if head.get(col, "").strip() != expected.strip():
                raise ValueError(f"Original count/survey schema drift {sheet}, {col}")
    # Inspect real original worksheet headers; do not infer effort from count units or
    # author percent-change Q/R columns.
    method_labels = sorted({
        f"{sheet}:{col}:{name}" for sheet, hdr in headers.items()
        for col, name in hdr.items()
        if any(word in name.casefold() for word in
               ("observer", "effort", "detect", "method", "survey duration",
                "plot boundary", "polygon", "survey area", "coverage"))
    })
    raw_main = read_csv(DATA / "network_species.csv")
    main = [r for r in raw_main if r["dataset_id"] == "JNCC"
            and r["analysis_role"] == "macro_primary"
            and r["null_status"] == "computed"]
    if len(raw_main) != 1529 or len(main) != MAIN_JNCC_N:
        raise ValueError("Fixed Step1 main sample changed")
    import subprocess
    blob = subprocess.run(["git", "hash-object", str(DATA / "network_species.csv")],
                          cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    if blob != SOURCE_BLOB_SHA:
        raise ValueError("Original outcome file was modified")
    seen=set()
    source_qa=[]
    duplicate_source_point_panels=0
    duplicated_point_child_rows=0
    duplicate_label_panels=0
    matched_child_count=0
    for r in sorted(main, key=lambda x: x["row_id"]):
        pieces=r["network_id"].split("::", 2)
        if len(pieces)!=3 or pieces[0]!="JNCC":
            raise ValueError("Network identity changed")
        country,master=pieces[1],pieces[2]
        key=(r["species_id"],country,master,r["count_unit"])
        if key in seen:
            raise ValueError("Duplicated parent network species unit")
        seen.add(key)
        if key not in safe:
            raise ValueError(f"Original publisher parent cannot be recovered {key}")
        group=safe[key]
        y0={i["year_2000"] for i,_ in group}
        y1={i["year_recent"] for i,_ in group}
        if len(y0)!=1 or len(y1)!=1 or \
           int(r["year0"])!=next(iter(y0)) or int(r["year1"])!=next(iter(y1)):
            raise ValueError(f"Survey year/source parent inconsistency {key}")
        if len(group)!=int(r["K"]):
            raise ValueError(f"Original child source count does not match K {key}")
        x0=[v30.exact_count(sr.get("L")) for _,sr in group]
        x1=[v30.exact_count(sr.get("O")) for _,sr in group]
        if any(x is None for x in x0+x1):
            raise ValueError("Supposed exact-count main cohort contains noninteger source value")
        if sum(x0)!=float(r["N0"]) or sum(x1)!=float(r["N1"]):
            raise ValueError("Original source totals do not match saved Step1 response")
        coords=[(round(i["lat"],6),round(i["lon"],6)) for i,_ in group]
        names=[v30.normalize_name(i["original_site_name"]) for i,_ in group]
        collocated=len(coords)-len(set(coords))
        repeated_labels=len(names)-len(set(names))
        if collocated:
            duplicate_source_point_panels+=1
            duplicated_point_child_rows+=collocated
        if repeated_labels:
            duplicate_label_panels+=1
        matched_child_count+=len(group)
        source_qa.append(dict(
            row_id=r["row_id"],species=r["species_id"],country=country,
            count_unit=r["count_unit"],source_K=len(group),
            year0=r["year0"],year1=r["year1"],
            original_startpoints_with_duplicate_coordinates=bool(collocated),
            original_repeated_child_site_labels=bool(repeated_labels),
            source_years_uniform=True,
            original_adjusted_counts_integer=True,
            source_effort_per_epoch_available=False,
            independently_verified_historic_polygon_crosswalk=False,
            null_status=r["null_status"],
        ))
    if len(seen)!=MAIN_JNCC_N:
        raise ValueError("Main parent to original worksheet join not one-to-one")

    collided_ids={q["row_id"] for q in source_qa if q["original_startpoints_with_duplicate_coordinates"]}
    repeated_label_ids={q["row_id"] for q in source_qa if q["original_repeated_child_site_labels"]}
    suspect_ids=collided_ids | repeated_label_ids
    clean=[r for r in main if r["row_id"] not in suspect_ids]
    if len(main)-len(clean)!=len(suspect_ids):
        raise ValueError("Original source quality flags do not join 1:1")

    # Public JNCC population-trend warning (not learned from these outcomes):
    # lower comparability for these gulls due to method or survey coverage.
    publisher_warning={"Herring Gull","Lesser Black-backed Gull"}
    no_warning=[r for r in main if r["species_id"] not in publisher_warning]
    if len(main)-len(no_warning)!=90:
        raise ValueError("Expected JNCC publisher warning cohort shifted")

    groupings={
      "by_country": {k:stats([r for r in main if r["network_id"].split("::",2)[1]==k])
                     for k in sorted({r["network_id"].split("::",2)[1] for r in main})},
      "by_original_count_unit": {k:stats([r for r in main if r["count_unit"]==k])
                     for k in sorted({r["count_unit"] for r in main})},
      "by_species": {k:stats([r for r in main if r["species_id"]==k])
                     for k in sorted({r["species_id"] for r in main})},
    }
    profiles=[]
    for q in source_qa:
        found=next(r for r in main if r["row_id"]==q["row_id"])
        if q["original_startpoints_with_duplicate_coordinates"]:
            profiles.append(found)
    sizes=[float(r["extent_km"]) for r in main]
    non_scot=[r for r in main if not r["network_id"].startswith("JNCC::Scotland::")]
    obs=stats(main)
    if obs["positive"]!=436 or sum(float(r["N1"])<float(r["N0"]) for r in main)!=479:
        raise ValueError("Original 436/663 and 479 decline main results drift")
    report={
       "audit_status":"SOURCE_VERIFIED_JNCC_METADATA_AND_DESCRIPTIVE_STRATA_ONLY",
       "original_source_sha256":ORIGINAL_SHA,
       "unchanged_step1_git_blob":blob,
       "n_original_matched_JNCC_parent_source_panels":len(safe),
       "n_main_exact_year_count_panels":len(main),
       "source_matched_child_sites_across_panels":matched_child_count,
       "original_comparable_sheet_columns":headers,
       "method_or_effort_word_header_columns":method_labels,
       "count_unit_is_not_survey_effort_or_detection_parameter":True,
       "year_uniform_counts_have_already_been_filtered_in_Step1":True,
       "publisher_adjusted_counts_are_not_independent_calibrated_observation_errors":True,
       "source_Site_ID_does_not_certify_historical_polygon_stability":True,
       "original_source_start_coordinate_duplicates_panel_n":duplicate_source_point_panels,
       "source_additional_child_IDs_sharing_a_start_point_n":duplicated_point_child_rows,
       "original_repeated_child_site_names_panel_n":duplicate_label_panels,
       "duplicated_coordinate_panels_descriptive_only":stats(profiles),
       "source_metadata_ambiguity_eligible_n":len(suspect_ids),
       "unique_coordinate_and_label_descriptive_subset":stats(clean),
       "this_subset_is_post_result_descriptive_not_independent_confirmation":True,
       "publisher_population_trend_method_warning":{
           "publisher_url":"https://jncc.gov.uk/our-work/seabirds-count/",
           "risk":"JNCC states lower confidence in Herring Gull and Lesser Black-backed Gull population trends due to methodology and/or coverage; this is a population-trend warning and not proof that each source Site.ID record is invalid",
           "species":["Herring Gull","Lesser Black-backed Gull"],
           "excluded_panel_n":len(main)-len(no_warning),
           "descriptive_remaining":stats(no_warning),
           "after_result_exploratory":True
       },
       "complete_main":obs,
       "without_scotland":stats(non_scot),
       "source_extent_km":{"min":min(sizes),"median":statistics.median(sizes),
                           "max":max(sizes)},
       "stratified_original_outcome_descriptives":groupings,
       "unknown_without_independent_record":[
         "epoch-specific independent observer effort / visit number",
         "site polygon boundary identity between 1998–2005 and 2015–2021",
         "source per-site detection probability and adjusted-count error distribution",
         "physical-island versus mainland verified crosswalk",
         "survey season/month within a year",
       ],
       "not_performed":[
         "new null simulation or biological association test",
         "H3/H4 re-estimation or post hoc rescue models",
         "changing prior Step1 or Step4 inferences",
         "attributing survey artifacts or true polygon loss",
       ],
    }
    OUT.mkdir(exist_ok=True)
    (OUT/"STEP6_JNCC_METHOD_QA.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    headings=next(iter(headers.values()))
    lines=[
        "# Step6 — JNCC元原本の計数・調査境界監査（2026-11-07）",
        "",
        "**観測済み結果の後に実施した品質監査。H3/H4の4枠Holm主検定は変更しない。**",
        "",
        f"- JNCC公式2024年改訂原XLSXのSHA256照合成功。{MAIN_JNCC_N}主解析行の種・国・Master site・計数単位・二時点・子Site.ID数・集計計数の全件が原表と一致。",
        f"- 原子地点のレコードは延べ{matched_child_count}件（同じ地点が別種等で再利用されるため独立地点数ではない）。",
        f"- 固定した原Site.IDの開始点座標が同じものを含むネットワーク×種は{duplicate_source_point_panels}行、重複した追加子Site.IDは{duplicated_point_child_rows}件。地点の同一物理パッチや重複計数を証明するものではない。",
        f"- 同じMaster site内部で元Site名が重複するネットワーク×種は{duplicate_label_panels}行。単なる文字列一致で除外・地理的重複認定しない。",
        f"- 開始点座標・地点名の重複がある{len(suspect_ids)}行を**記述のみ**別枠にした場合、残る{len(clean)}行の正は{stats(clean)['positive']}行、種平均が正は{stats(clean)['species_with_positive_mean']}/{stats(clean)['n_species']}種。これは主対象の変更や新しい事前登録検定ではない。",
        f"- JNCCが国全体のトレンド比較に方法・被覆率上の留保を付けたHerring Gull/Lesser Black-backed Gull（計90行）を別枠にすると、残る{len(no_warning)}行の正は{stats(no_warning)['positive']}行、種平均正は{stats(no_warning)['species_with_positive_mean']}/{stats(no_warning)['n_species']}種。出版社の全国傾向への注意は、各原Site.IDが不適格と証明したものではない。",
        "- 二時点の年次とAON/AOS/AOT/AOB/IND単位は元原本で一致する行だけを採用済み。一方、調査努力・観測誤差・物理区画の歴史的同一性はこの二時点の比較表だけでは較正できない。",
        "",
        "## 元Excelに存在する列名（main比較表）",
        "",
    ]
    for key in sorted(headings):
        lines.append(f"- {key}: {headings[key].replace(chr(10),' / ')}")
    lines.extend(["","## 記述的な計数単位別の集中正方向","",
                  "| 原計数単位 | 行数 | 集中が正 | 種数 | 種均等重み平均Y（10年） |",
                  "|---|---:|---:|---:|---:|"])
    for unit,x in sorted(groupings["by_original_count_unit"].items()):
        lines.append(f"| {unit} | {x['n_rows']} | {x['positive']}（{x['fraction_positive']:.1%}） | {x['n_species']} | {x['species_equal_mean_excess_decade']:+.4f} |")
    lines.extend(["","## 国別の集中の支持と地理的制約","",
                  "| 原Country | 行数 | 集中正 | 種数 | 種均等重み平均Y |",
                  "|---|---:|---:|---:|---:|"])
    for country,x in sorted(groupings["by_country"].items()):
        lines.append(f"| {country} | {x['n_rows']} | {x['positive']}（{x['fraction_positive']:.1%}） | {x['n_species']} | {x['species_equal_mean_excess_decade']:+.4f} |")
    lines.extend(["",
      "## 解釈の上限",
      "",
      "- 同じ原本内の計数単位ごとには正方向の例が存在する。ただし種×単位の交絡が強く、各計数単位で独立に再現した現象とは読まない。",
      "- 原Excelの“調整された計数”があることと、独立した努力・観測誤差のデータがあることは別。今回の多項帰無は定義上、二時点の観測誤差を較正しない。",
      "- 同じSite.IDが対応していても、独立した過去・現在の営巣ポリゴン照合なしに境界変化がないとは言えない。開始点の重なりや地理幅は疑義の検出にとどめる。",
      "- カモメの一部は自然営巣地のみ、Atlantic Puffinは比較可能な専用シートのみ、非同期原調査は外したという既存出版社の制約を引き継ぐ。",
      "- この監査は未観測の努力の差による見かけの集中を数値的に排除するものではない。旧Step1の結果の規模と観測範囲を精密化する記述であり、仮説検定の成功結果には数えない。",
      "",
      "元Excelと子Site.ID別の原計数は再配布しない。機械可読版：STEP6_JNCC_METHOD_QA.json。",
    ])
    (OUT/"STEP6_JNCC_METHOD_QA_JA.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["audit_status"],
                      "main":len(main),"matched_child_rows":matched_child_count,
                      "duplicate_point_parents":duplicate_source_point_panels,
                      "duplicate_site_names":duplicate_label_panels,
                      "count_units":{k:x["positive"] for k,x in groupings["by_original_count_unit"].items()},
                      "original_columns":headings},ensure_ascii=False))


if __name__ == "__main__":
    main()
