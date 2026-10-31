"""Matched 3-species nest-count ratios vs lagged original SIC + 1993-2020 GLORYS SST/salinity.

Descriptive source-checked macro correlations and strictly chronological *conditional* hindcast.
Models are fixed here; no model is promoted after seeing one favorable score.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "historical_ocean_species_v1"
SOURCE = ROOT / "outputs"
PINNED = {
    "bio": ("comparison_audit/mapppd_unambiguous_site_seasons.csv", "fc134e364cf38699fa7611d7dee5fbbbcb370c0a"),
    "paired": ("warming_species_breeding_v1/matched_species_breeding_change.csv", "f17b4a21e9e5a045a40f5a4af9019e3bbc011758"),
    "sic": ("climate_penguin/macro_monthly_seaice_1991_2020.csv", "4fcea71c2d8b1069b6ad143f6522061ed434daf5"),
    "timing": ("climate_penguin/historical_count_season_timing.csv", "02b240649e36533445690be9034469251659d0a2"),
    "future": ("warming_species_breeding_v1/future_climate_coobserved_sites.csv", "97ae24e98a0cb5f6b36e275d036cb4b71c953312"),
}
HIST_OCEAN_SHA256 = "28989cb27b06491326fe6fbb827e58fae5b60eab7a73278eb24c56ab41ca2eb8"
FEATURES = {
    "baseline": (),
    "SIC": ("sic_prior_september_pct",),
    "SST_SSS": ("sst_prior_september_c", "sss_prior_september"),
    "SIC_SST_SSS": ("sic_prior_september_pct", "sst_prior_september_c", "sss_prior_september"),
}
MODELS = ("baseline", "SIC", "SST_SSS", "SIC_SST_SSS")
PENALTIES = {"species": 5., "group": 8., "year": 5., "climate": 12.}
MIN_EARLIER = 20
MIN_TRAIN_SITES = 3

def verified_csv(name: str) -> pd.DataFrame:
    relative, expected = PINNED[name]
    content = (SOURCE / relative).read_bytes()
    sha = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
    if sha != expected:
        raise ValueError(f"Original input changed: {name} {sha} != {expected}")
    return pd.read_csv(SOURCE / relative)

def ensure_unique(df: pd.DataFrame, keys: list[str], label: str):
    if df.duplicated(keys).any():
        raise ValueError(f"Duplicate original key {label}: {keys}")

def pear(a: pd.Series | np.ndarray, b: pd.Series | np.ndarray) -> float | None:
    x, y = np.asarray(a, float), np.asarray(b, float)
    if len(x) < 3 or np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return None
    return float(np.corrcoef(x, y)[0, 1])

def within_two_fixed(df: pd.DataFrame, field: str) -> np.ndarray:
    # Explicit dummy regression, not naive demeaning of an unbalanced panel.
    groups = sorted(df["group"].unique())
    years = sorted(df["end_year"].unique())
    x = np.column_stack(
        [np.asarray(df["group"] == g, float) for g in groups] +
        [np.asarray(df["end_year"] == year, float) for year in years[1:]]
    )
    y = df[field].to_numpy(float)
    return y - x @ np.linalg.lstsq(x, y, rcond=None)[0]

def macro_correlations(df: pd.DataFrame) -> list[dict]:
    result = []
    for scope in ("ALL", "GEPE", "CHPE"):
        subset = df if scope == "ALL" else df.loc[df.compared_species == scope]
        for field in ("sic_prior_september_pct", "sst_prior_september_c", "sss_prior_september"):
            a = within_two_fixed(subset, field)
            b = within_two_fixed(subset, "delta_log1p_ratio")
            result.append({
                "compared_species": scope, "variable": field,
                "intervals": len(subset), "unique_sites": subset.site_id.nunique(),
                "unique_site_years": subset[["site_id", "end_year"]].drop_duplicates().shape[0],
                "raw_pearson_r": pear(subset[field], subset.delta_log1p_ratio),
                "site_pair_and_end_year_adjusted_r": pear(a, b),
                "no_independent_effect_claim": True,
            })
    return result

def regression_predict(training: pd.DataFrame, test: pd.DataFrame, name: str, groups: list[str]) -> np.ndarray:
    """Exactly one training-only ridge fit. Site/group levels are fixed identifiers, not response-driven."""
    feats = FEATURES[name]
    def base(frame):
        g = frame.group.astype(str).to_numpy()
        s = frame.compared_species.astype(str).to_numpy()
        parts = [np.ones(len(frame)), (s == "CHPE").astype(float),
                 (frame.end_year.to_numpy(float) - 2000.) / 10.]
        parts.extend((g == key).astype(float) for key in groups)
        return np.column_stack(parts)
    tr, te = base(training), base(test)
    penalties = [0., PENALTIES["species"], PENALTIES["year"]] + [PENALTIES["group"]] * len(groups)
    for column in feats:
        values = training[column].to_numpy(float)
        m, sd = float(np.mean(values)), float(np.std(values))
        sd = max(sd, 1.e-8)  # training-only statistics; no future standardisation leakage
        tr = np.column_stack((tr, (values - m) / sd))
        te = np.column_stack((te, (test[column].to_numpy(float) - m) / sd))
        penalties.append(PENALTIES["climate"])
    y = training.delta_log1p_ratio.to_numpy(float)
    solution = np.linalg.solve(tr.T @ tr + np.diag(penalties), tr.T @ y)
    return te @ solution

def chrono_predictions(df: pd.DataFrame, groups: list[str], exclude_test_site: bool) -> pd.DataFrame:
    predictions = []
    for year in sorted(df.end_year.unique()):
        test = df.loc[df.end_year == year].copy()
        for site in (sorted(test.site_id.unique()) if exclude_test_site else [None]):
            sample = test if site is None else test.loc[test.site_id == site]
            train = df.loc[df.end_year < year]
            if site is not None:
                train = train.loc[train.site_id != site]
            if len(train) < MIN_EARLIER or train.site_id.nunique() < MIN_TRAIN_SITES:
                continue
            if int(train.end_year.max()) >= int(year):
                raise AssertionError("Chronology leaked future outcome year")
            pred = {m: regression_predict(train, sample, m, groups) for m in MODELS}
            prior_mean = train.delta_log1p_ratio.mean()
            for j, (_, observation) in enumerate(sample.iterrows()):
                s = train.loc[train.compared_species == observation.compared_species, "delta_log1p_ratio"]
                predictions.append({
                    "test_year": int(year),
                    "site_id": observation.site_id, "compared_species": observation.compared_species,
                    "group": observation.group,
                    "test_site_excluded": bool(exclude_test_site),
                    "training_intervals": len(train), "training_sites": train.site_id.nunique(),
                    "last_training_end_year": int(train.end_year.max()),
                    "source_start_year": int(observation.start_year),
                    "actual_delta_log1p_ratio": float(observation.delta_log1p_ratio),
                    "predict_zero": 0.,
                    "predict_prior_mean": float(prior_mean),
                    "predict_species_mean": float(s.mean()) if len(s) else float(prior_mean),
                    **{f"predict_{model}": float(pred[model][j]) for model in MODELS},
                })
    return pd.DataFrame(predictions)

def score(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    rows = []
    for species in ("ALL", "GEPE", "CHPE"):
        a = df if species == "ALL" else df.loc[df.compared_species == species]
        for model in ("zero", "prior_mean", "species_mean") + MODELS:
            diff = a["predict_" + model].to_numpy(float) - a.actual_delta_log1p_ratio.to_numpy(float)
            rows.append({
                "species": species, "model": model, "n": len(a),
                "sites": int(a.site_id.nunique()),
                "unique_site_years": a[["site_id", "test_year"]].drop_duplicates().shape[0],
                "mae": float(np.mean(np.abs(diff))),
                "rmse": float(np.sqrt(np.mean(diff ** 2))),
                "mean_bias": float(np.mean(diff)),
            })
    return rows

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ocean_path = OUT / "original_glorys_8sites_1993_2020_monthly.csv"
    if not ocean_path.exists():
        raise ValueError("Source extraction has not been executed: no GLORYS 1993–2020 original")
    sha = hashlib.sha256(ocean_path.read_bytes()).hexdigest()
    if sha != HIST_OCEAN_SHA256:
        raise ValueError("New 1993–2020 ocean source not identical to approved source receipt")
    ocean = pd.read_csv(ocean_path)
    assert len(ocean) == 896 and ocean.site_id.nunique() == 8
    bio, paired, ice, timing, future = (verified_csv(k) for k in ("bio", "paired", "sic", "timing", "future"))
    if len(bio) != 2999 or len(paired) != 13 or len(ice) != 9600:
        raise ValueError("Original historical-count or sea-ice cohort drift")
    if not paired.gate.eq(1).all():
        raise ValueError("Changed original same-year biological eligibility")
    ensure_unique(bio, ["site_id", "species_id", "season", "method"], "original selected site counts")
    ensure_unique(ocean, ["site_id", "year", "month"], "extended ocean")
    ensure_unique(ice, ["site_id", "year", "month", "inner_km"], "satellite ice")
    ensure_unique(timing, ["site_id", "species_id", "season", "method"], "month support")
    ocean9 = ocean.loc[ocean.month == 9].set_index(["site_id", "year"])
    ice9 = ice.loc[(ice.month == 9) & (ice.inner_km == 0) & ice.complete_month.eq(True)].set_index(["site_id", "year"])
    biological = bio.set_index(["site_id", "species_id", "season", "method"])
    timing = timing.set_index(["site_id", "species_id", "season", "method"])
    source_years, intervals = [], []
    for p in paired.itertuples(index=False):
        years = list(map(int, p.common_years.split(";")))
        observations = []
        for year in years:
            a = biological.loc[(p.site_id, "ADPE", year, p.method_reference)]
            b = biological.loc[(p.site_id, p.compared_species, year, p.method_compared)]
            if float(a["count"]) < 0 or float(b["count"]) < 0:
                raise ValueError("Negative original source nests")
            ratio = np.log1p(float(b["count"])) - np.log1p(float(a["count"]))
            row = {
                "site_id": p.site_id, "group": p.site_id + "|" + p.compared_species,
                "compared_species": p.compared_species, "year": year,
                "reference_nests": float(a["count"]), "comparison_nests": float(b["count"]),
                "log1p_ratio": float(ratio),
            }
            observations.append(row)
            source_years.append(row)
        x = pd.DataFrame(observations)
        model_slope = np.polyfit(x.year.to_numpy(), x.log1p_ratio.to_numpy(), 1)[0] * 10
        if abs(model_slope - float(p.common_year_log1p_ratio_slope_decade)) > 1.e-8:
            raise ValueError("Original long-term species ratio endpoint changed")
        for left, right in zip(observations, observations[1:]):
            if right["year"] != left["year"] + 1:
                continue
            key = (left["site_id"], left["year"])
            if key not in ocean9.index or key not in ice9.index:
                continue
            marine = ocean9.loc[key]
            sic = ice9.loc[key]
            fields = {
                "sic_prior_september_pct": float(sic.sic_mean),
                "sst_prior_september_c": float(marine.surface_potential_temperature_c),
                "sss_prior_september": float(marine.surface_salinity),
            }
            if not all(np.isfinite(list(fields.values()))):
                continue
            rawkeys = [(left["site_id"], sp, yr, mt) for yr in (left["year"], right["year"])
                       for sp, mt in (("ADPE", p.method_reference), (p.compared_species, p.method_compared))]
            supported = all(k in timing.index and bool(timing.loc[k, "all_after_september"]) for k in rawkeys)
            known = all(k in timing.index and bool(timing.loc[k, "all_months_known"]) for k in rawkeys)
            intervals.append({
                "site_id": left["site_id"], "region": p.region, "group": left["group"],
                "compared_species": p.compared_species,
                "start_year": left["year"], "end_year": right["year"],
                "start_reference_nests": left["reference_nests"], "end_reference_nests": right["reference_nests"],
                "start_comparison_nests": left["comparison_nests"], "end_comparison_nests": right["comparison_nests"],
                "delta_log1p_ratio": right["log1p_ratio"] - left["log1p_ratio"],
                "start_both_count_months_known": known,
                "both_years_all_counted_after_september": supported,
                "native_marine_grid_y": int(marine.grid_y), "native_marine_grid_x": int(marine.grid_x),
                "marine_grid_distance_km": float(marine.grid_distance_km),
                **fields,
            })
    yearly = pd.DataFrame(source_years)
    df = pd.DataFrame(intervals).sort_values(["end_year", "site_id", "compared_species"]).reset_index(drop=True)
    if len(yearly) != 137 or df.site_id.nunique() != 8 or len(df) < 75:
        raise ValueError("Prior environmental retrieval did not support the matched macro cohort")
    if not df.groupby(["site_id", "start_year", "end_year", "compared_species"]).size().eq(1).all():
        raise ValueError("Duplicate interval observations")
    groups = sorted(df.group.unique())
    if len(groups) != 13:
        raise ValueError("Species-pair representation changed after complete original source join")
    correlations = pd.DataFrame(macro_correlations(df))
    historical = {
        "source_status": "completed_1993_2020_glorys_at_frozen_original_8_sites",
        "temporal_direction": "start_year September environment -> next season's relative nest ratio difference; count month not always known",
        "original_pair_years": len(yearly), "matched_original_intervals": len(df),
        "independent_site_codes": df.site_id.nunique(),
        "native_ocean_grid_cells": df[["native_marine_grid_y", "native_marine_grid_x"]].drop_duplicates().shape[0],
        "unique_source_start_site_years": df[["site_id", "start_year"]].drop_duplicates().shape[0],
        "matched_count_month_known_intervals": int(df.start_both_count_months_known.sum()),
        "matched_count_month_after_september_intervals": int(df.both_years_all_counted_after_september.sum()),
        "year_counts": {
            "first": int(df.end_year.min()), "last": int(df.end_year.max()),
            "test": int(df.end_year.nunique()),
        },
        "numbers_of_intervals": dict(df.compared_species.value_counts().sort_index()),
        "ocean_source_csv_sha256": sha,
    }
    df.to_csv(OUT / "source_1993_2020_breeding_ocean_intervals.csv", index=False)
    correlations.to_csv(OUT / "historical_environment_relationships.csv", index=False)
    allpred = chrono_predictions(df, groups, False)
    strictpred = chrono_predictions(df, groups, True)
    if allpred.empty or strictpred.empty:
        raise ValueError("No chronological or site-out forecast support")
    allpred.to_csv(OUT / "chronological_hindcast_predictions.csv", index=False)
    strictpred.to_csv(OUT / "chronological_site_out_predictions.csv", index=False)
    metrics = pd.DataFrame([
        {"evaluation": "chronological", **x} for x in score(allpred)
    ] + [
        {"evaluation": "chronological_and_heldout_site", **x} for x in score(strictpred)
    ])
    metrics.to_csv(OUT / "hindcast_metrics.csv", index=False)
    climate = future.groupby(["experiment", "period"], as_index=False).agg(
        sites=("site_id", "nunique"),
        mean_temperature_change_c=("tas_C_change_model_mean", "mean"),
        mean_sic_change_pp=("SIC_pp_change_model_mean", "mean"),
        mean_model_salinity_change=("sos_change_model_mean", "mean"),
    )
    climate.to_csv(OUT / "future_physical_context_8sites.csv", index=False)
    def get(eval_name, model):
        r = metrics.loc[(metrics.evaluation == eval_name) & (metrics.species == "ALL") & (metrics.model == model)]
        return {"mae": float(r.mae.iloc[0]), "rmse": float(r.rmse.iloc[0]),
                "n": int(r.n.iloc[0]), "sites": int(r.sites.iloc[0]),
                "unique_site_years": int(r.unique_site_years.iloc[0])}
    chrono = {name: get("chronological", name) for name in ("zero", "prior_mean", "species_mean") + MODELS}
    siteout = {name: get("chronological_and_heldout_site", name) for name in ("zero", "prior_mean", "species_mean") + MODELS}
    # Freeze scientific gate independently of the observed CV outcome. All conditions required.
    gate = {
        "at_least_40_complete_intervals": bool(len(df) >= 40),
        "at_least_5_independent_sites": bool(df.site_id.nunique() >= 5),
        "at_least_20_verified_count_month_intervals": bool(historical["matched_count_month_after_september_intervals"] >= 20),
        "chronology_all_environment_beats_no_environment": bool(chrono["SIC_SST_SSS"]["mae"] < chrono["baseline"]["mae"]),
        "chronology_all_environment_beats_ice_only": bool(chrono["SIC_SST_SSS"]["mae"] < chrono["SIC"]["mae"]),
        "site_out_all_environment_beats_no_environment": bool(siteout["SIC_SST_SSS"]["mae"] < siteout["baseline"]["mae"]),
    }
    prediction_permitted = all(gate.values())
    result = {
        "status": "exploratory_breeding_ocean_associations_not_identified_warming_causal_effect",
        "original_dataset_fingerprint": {k: sha for k, (_, sha) in PINNED.items()},
        "macro_cohort": historical,
        "environment_adjusted_correlations": correlations.to_dict(orient="records"),
        "model_specification": {
            "outcome": "year-to-year log1p(other_nests)-log1p(Adelie_nests) difference",
            "predictors": "fixed native September near SIC and GLORYS potential SST and salinity at START year",
            "penalty": PENALTIES,
            "training_only_standardization": True, "minimum_prior_intervals": MIN_EARLIER,
            "minimum_prior_sites": MIN_TRAIN_SITES, "features": FEATURES,
            "climate_causal_inference": False,
            "interpretation": "conditional hindcast because count month is not fully known, sources assimilate ice/SST, and site/region overlap.",
        },
        "chronological_hindcast": chrono,
        "chronological_plus_heldout_site": siteout,
        "future_physical_context": climate.to_dict(orient="records"),
        "biological_Cmip6_projection_gate": gate,
        "calibrated_future_nesting_projection_permitted": prediction_permitted,
        "conclusion": (
            "Only if every gate passes may a numerical climate-associated future nest-ratio forecast be considered, "
            "and then only after aligning monthly future CMIP6 variables. Missing original count timing prevents "
            "automatic transfer. No future nest abundance is estimated in this script."
        ),
    }
    (OUT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, default=float) + "\n", encoding="utf-8")
    report = f"""# 1993–2020海氷＋表層水温＋塩分 × 同一地点3種繁殖数（source-backed）
    
## 実行状態
原GLORYSの2011–2020との320地点月一致確認済み。1993–2020の元896地点月を利用。
現地営巣数比の長期傾き13比較は別途凍結済み。

- 元種ペア年={len(yearly)}、連続年の9月海氷・海洋環境完全一致={len(df)}、実サイト={df.site_id.nunique()}、海域セル={historical["native_ocean_grid_cells"]}。
- 連続年区間のうち、両種・両年の計数月が9月後と確証={historical["matched_count_month_after_september_intervals"]}。他は0や不在ではなく計数時期不確定。
- モデルは事前固定のtraining-only基準＋SIC＋SST/SSS、同一標本のrolling-origin及び未使用地点との同時ホールドアウトで比較。
- 同じ海氷を同化した海洋再解析である。塩分の独立因果効果は識別できない。

## 時間順MAE（小さいほど良い）
- zero={chrono['zero']['mae']:.5f}、生態基準（種＋場所＋年）={chrono['baseline']['mae']:.5f}。
- 基準＋海氷={chrono['SIC']['mae']:.5f}、基準＋水温・塩分={chrono['SST_SSS']['mae']:.5f}、基準＋全部={chrono['SIC_SST_SSS']['mae']:.5f}。
- 対象={chrono['baseline']['n']}種比較区間、{chrono['baseline']['sites']}実サイト。
- 同時に地点も未使用としたMAE：基準={siteout['baseline']['mae']:.5f}、海氷のみ={siteout['SIC']['mae']:.5f}、全部={siteout['SIC_SST_SSS']['mae']:.5f}、{siteout['baseline']['n']}区間／{siteout['baseline']['sites']}地点。

## 生物予測の判定
\`calibrated_future_nesting_projection_permitted={prediction_permitted}\`。
これらの相関・条件付きhindcastから将来の2050/2100巣数を直接算出しない。
元の計数月、未使用島・地域、予測時点で観測可能な先行海洋値の妥当性が必要。
CI全出力 \`source_1993_2020_breeding_ocean_intervals.csv\`、\`historical_environment_relationships.csv\`、
\`chronological_hindcast_predictions.csv\`、\`chronological_site_out_predictions.csv\`、
\`hindcast_metrics.csv\`、\`future_physical_context_8sites.csv\`、\`result.json\`、\`source_receipt.json\`。
"""
    (OUT / "REPORT_JA.md").write_text(report, encoding="utf-8")
    print("BIOLOGICAL TIME-TRANSFER RESULTS " + json.dumps({
        "cohort": historical,
        "chronological": chrono,
        "chronological_heldout_site": siteout,
        "observed_environment_correlations": result["environment_adjusted_correlations"],
        "forecast_gate": gate,
        "future_nests_projection_permitted": prediction_permitted,
    }, ensure_ascii=False, default=float), flush=True)

if __name__ == "__main__":
    main()
