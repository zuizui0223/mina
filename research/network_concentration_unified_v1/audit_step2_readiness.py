#!/usr/bin/env python3
"""Step 2 covariate availability and strict join gates for mina unified macroecology.

Reads fixed Step 1 CSVs; NEVER estimates H2/H3/H4 or substitutes trait/SST values.
Creates empty source-intake templates once; subsequently preserves manually curated data.
Only source-verified numerical values can enter the pre-model readiness ledger.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
OUT = BASE / "outputs"

TRAIT_COLUMNS = (
    "species_id", "annual_breeding_site_fidelity", "source_identifier",
    "source_url", "original_definition", "breeding_unit", "denominator",
    "study_region", "study_interval", "verification_status",
)
CLIMATE_COLUMNS = (
    "analysis_unit", "row_id", "dataset_id", "network_id", "cohort_id",
    "year0", "year1", "oisst_v21_temporal_candidate",
    "delta_sst_C_per_decade", "source_id", "spatial_status",
    "temporal_status", "verification_status",
)
READY_COLUMNS = (
    "analysis_unit", "row_id", "dataset_id", "network_id", "species_id",
    "species_a", "species_b", "year0", "year1",
    "fidelity_status", "sst_status", "oisst_v21_temporal_candidate",
    "H2_ready", "H3_ready", "H4D_ready", "H4W_ready",
)


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            raise ValueError(f"No CSV header: {path}")
        return list(reader)


def write_csv(path: Path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def intake(path: Path, columns, default_records, idfunc):
    expected_keys = [idfunc(x) for x in default_records]
    if len(expected_keys) != len(set(expected_keys)):
        raise ValueError(f"Duplicate expected source-intake keys {path}")
    if not path.exists():
        write_csv(path, columns, default_records)
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if tuple(reader.fieldnames or ()) != tuple(columns):
            raise ValueError(f"Intake schema mismatch {path}")
        actual = list(reader)
    observed_keys = [idfunc(x) for x in actual]
    if set(observed_keys) != set(expected_keys) or len(observed_keys) != len(set(observed_keys)):
        raise ValueError(f"Intake keys changed or duplicated: {path}")
    return {idfunc(x): x for x in actual}


def numeric(s):
    if s is None or str(s).strip() == "":
        return None
    try:
        v = float(s)
    except ValueError as exc:
        raise ValueError(f"Non-numeric curated value {s!r}") from exc
    if not math.isfinite(v):
        raise ValueError(f"Non-finite curated value {s!r}")
    return v


def trait_gate(record):
    value = numeric(record["annual_breeding_site_fidelity"])
    if value is not None and not 0 <= value <= 1:
        raise ValueError(f"Site fidelity must be a 0..1 probability: {record['species_id']}")
    required = ("source_identifier", "original_definition", "breeding_unit",
                "denominator", "study_region", "study_interval")
    valid = (
        record["verification_status"] == "verified_comparable_breeding_site_fidelity"
        and value is not None
        and all(record[k].strip() for k in required)
    )
    return "verified" if valid else "not_verified"


def climate_gate(record):
    value = numeric(record["delta_sst_C_per_decade"])
    valid = (
        record["verification_status"] == "verified_same_definition_sst"
        and record["spatial_status"] == "verified_source_ocean_cell"
        and record["temporal_status"] == "source_endpoint_months_verified"
        and bool(record["source_id"].strip())
        and value is not None
    )
    return "verified" if valid else "not_verified"


def temporal_candidate(y0, y1):
    # NOAA OISST v2.1 begins 1981-09. Year-only screen, not evidence of an SST join.
    # Actual month selection, wet-cell distance and source vintage remain unverified.
    return "yes" if int(y0) >= 1981 and int(y1) <= 2026 else "no"


def main():
    main_path = DATA / "network_species.csv"
    pair_path = DATA / "network_species_pairs.csv"
    main_raw = load_csv(main_path)
    pair_raw = load_csv(pair_path)
    main_rows = sorted(
        (r for r in main_raw if r["analysis_role"] == "macro_primary"
         and r["null_status"] == "computed"), key=lambda r: r["row_id"]
    )
    pair_rows = sorted(
        (r for r in pair_raw if r["analysis_role"] == "macro_primary"
         and r["null_status"] == "computed"), key=lambda r: r["pair_row_id"]
    )
    if len(main_rows) != 675 or len(pair_rows) != 378:
        raise ValueError("Step1 fixed-row count drift; do not silently rebuild covariate cohorts")
    for r in main_rows:
        if numeric(r["concentration_excess_decade"]) is None or \
           numeric(r["abundance_log_change_decade"]) is None or \
           (numeric(r["extent_km"]) or 0) <= 0:
            raise ValueError(f"Main modeling support invalid: {r['row_id']}")
    for r in pair_rows:
        if numeric(r["overlap_excess_decade"]) is None or \
           numeric(r["pair_decline_decade"]) is None or \
           (numeric(r["extent_km"]) or 0) <= 0:
            raise ValueError(f"Pair modeling support invalid: {r['pair_row_id']}")

    species = sorted({r["species_id"] for r in main_rows})
    if len(species) != 20:
        raise ValueError("Unexpected number of primary species")
    traits_default = [dict(zip(TRAIT_COLUMNS, (
        s, "", "", "", "", "", "", "", "", "not_extracted"
    ))) for s in species]
    traits = intake(DATA / "species_traits_intake.csv", TRAIT_COLUMNS, traits_default,
                    lambda r: r["species_id"])

    entries = []
    for kind, records, keycol, cohortcol in (
        ("network_species", main_rows, "row_id", "cohort_id"),
        ("network_species_pairs", pair_rows, "pair_row_id", "pair_cohort_id"),
    ):
        for r in records:
            entries.append(dict(zip(CLIMATE_COLUMNS, (
                kind, r[keycol], r["dataset_id"], r["network_id"],
                r[cohortcol], r["year0"], r["year1"],
                temporal_candidate(r["year0"], r["year1"]),
                "", "", "not_matched", "not_checked", "not_extracted",
            ))))
    climate = intake(DATA / "network_climate_intake.csv", CLIMATE_COLUMNS, entries,
                     lambda r: (r["analysis_unit"], r["row_id"]))

    ledger = []
    for kind, records, keycol in (
        ("network_species", main_rows, "row_id"),
        ("network_species_pairs", pair_rows, "pair_row_id"),
    ):
        for r in records:
            t = ("not_applicable" if kind != "network_species"
                 else trait_gate(traits[r["species_id"]]))
            c = climate_gate(climate[kind, r[keycol]])
            is_main = kind == "network_species"
            status = dict(zip(READY_COLUMNS, (
                kind, r[keycol], r["dataset_id"], r["network_id"],
                r.get("species_id", ""), r.get("species_a", ""),
                r.get("species_b", ""), r["year0"], r["year1"],
                t, c, temporal_candidate(r["year0"], r["year1"]),
                str(is_main and t == "verified").lower(),
                str(is_main and c == "verified").lower(),
                str(not is_main and c == "verified").lower(),
                str(not is_main and c == "verified").lower(),
            )))
            ledger.append(status)
    write_csv(DATA / "step2_join_readiness.csv", READY_COLUMNS, ledger)

    main_uk = [r for r in main_rows if r["dataset_id"] == "JNCC"]
    pair_uk = [r for r in pair_rows if r["dataset_id"] == "JNCC"]
    summary = {
        "status": "SOURCE_READINESS_ONLY_NO_HYPOTHESIS_TESTS",
        "step1_n_main": len(main_rows),
        "step1_n_pair": len(pair_rows),
        "main_networks": len({r["network_id"] for r in main_rows}),
        "pair_networks": len({r["network_id"] for r in pair_rows}),
        "independent_species_ids_main": len(species),
        "main_jncc": len(main_uk),
        "main_mapppd": len(main_rows) - len(main_uk),
        "pair_jncc": len(pair_uk),
        "pair_mapppd": len(pair_rows) - len(pair_uk),
        "main_temporal_oisst_candidate": sum(x["oisst_v21_temporal_candidate"] == "yes" for x in ledger if x["analysis_unit"] == "network_species"),
        "pair_temporal_oisst_candidate": sum(x["oisst_v21_temporal_candidate"] == "yes" for x in ledger if x["analysis_unit"] == "network_species_pairs"),
        "species_fidelity_verified": sum(trait_gate(r) == "verified" for r in traits.values()),
        "observed_sst_verified_rows": sum(climate_gate(r) == "verified" for r in climate.values()),
        "H2_ready_rows": sum(x["H2_ready"] == "true" for x in ledger),
        "H3_ready_rows": sum(x["H3_ready"] == "true" for x in ledger),
        "H4D_ready_rows": sum(x["H4D_ready"] == "true" for x in ledger),
        "H4W_ready_rows": sum(x["H4W_ready"] == "true" for x in ledger),
        "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (main_path, pair_path)},
        "not_done": ["H2/H3/H4D/H4W coefficients", "multiple-testing correction",
                     "SST site matching", "site-fidelity numeric synthesis"],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "STEP2_SOURCE_READINESS.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    def missing(records):
        return [r for r in records if temporal_candidate(r["year0"], r["year1"]) == "no"]
    ms, ps = missing(main_rows), missing(pair_rows)
    lines = [
        "# Step 2: 共変量の結合可能性（結果ではなくデータ入力監査）",
        "",
        "Step 1 の計数帰無を再実行せず、確定済みの共通表から検定候補のキーを作成した。",
        "対象はマクロ主解析のみ。島内行、皇帝モデル平均は加算していない。",
        "",
        f"- 主表 {len(main_rows)} 行／{summary['main_networks']} ネットワーク／{len(species)} 種（JNCC {len(main_uk)}、MAPPPD {len(main_rows)-len(main_uk)}）。",
        f"- 種ペア {len(pair_rows)} 行／{summary['pair_networks']} ネットワーク（JNCC {len(pair_uk)}、MAPPPD {len(pair_rows)-len(pair_uk)}）。",
        f"- OISST v2.1 の **年月範囲だけ**を満たす候補: 主表 {summary['main_temporal_oisst_candidate']}/{len(main_rows)}、種ペア {summary['pair_temporal_oisst_candidate']}/{len(pair_rows)}。",
        f"- 同じ定義の数値固執率を原資料で検証した種: {summary['species_fidelity_verified']}/{len(species)}。",
        f"- 同じSSTを位置・年月・格子・出典まで検証して結合した行: {summary['observed_sst_verified_rows']}/{len(ledger)}。",
        f"- 入力条件を満たす行: H2 {summary['H2_ready_rows']}、H3 {summary['H3_ready_rows']}、H4D {summary['H4D_ready_rows']}、H4W {summary['H4W_ready_rows']}。",
        "",
        "## OISST時系列範囲に入らない行（欠測で保持）",
        "",
    ]
    for r in ms:
        lines.append(f"- 主表 {r['network_id']} / {r['species_id']} ({r['year0']}–{r['year1']})")
    for r in ps:
        lines.append(f"- 種ペア {r['network_id']} / {r['species_a']}×{r['species_b']} ({r['year0']}–{r['year1']})")
    lines.extend([
        "",
        "## 重要な判定境界",
        "",
        "- 時間範囲の一致はSSTの結合成功を意味しない。元のSite.ID／MAPPPD地点の座標を原出典から再取得し、海洋セル・沿岸マスク・季節・端点年の一致を別途検証する。",
        "- 英国JNCCの水温入力は既存の南極GLORYS thetao（約0.494m深）または南極に限定されたCMIP6 tosから代用しない。両者の物理定義・期間・空間支持が違う。",
        "- NOAA OISST v2.1 (月次0.25°、1981年9月以降) は今後の取得候補。公式案内: https://www.ncei.noaa.gov/products/optimum-interpolation-sst 。同一変数の採用と月別・空間規則はモデルを当てる前に固定する。",
        "- H2は成鳥の翌繁殖機会の同じ繁殖地への条件付き固執率が必要。帰還率、個体の生存率、出生地への帰還、定性評価を代用しない。種が20あってもネットワーク675行を独立20種以上の形質反復と誤認しない。",
        "- H4Dの予定モデルにもWが必要なので、W欠測行をSSTなしモデルへすり替えて検定しない。378ペアは90ネットワークに由来し、同じ種・元計数を共有する。",
        "- ここでのreadyは **データ入力条件のみ**。対象数、解析エンジン、共有計数による依存と不確実性はStep 3の凍結が必要。H2～H4の推定値、p値、支持判定は出していない。",
        "",
        "自動生成: audit_step2_readiness.py／入力共通表のSHA256はSTEP2_SOURCE_READINESS.json。",
        "入力用テンプレートは既存の場合上書きしない。出典と原定義の検証が済むまで数値は埋めず、欠測として保存する。",
        "",
    ])
    (OUT / "STEP2_SOURCE_READINESS_JA.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
