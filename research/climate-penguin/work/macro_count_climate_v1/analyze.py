#!/usr/bin/env python3
"""Exploratory three-species MAPPPD nest-count × observed September SIC macro-analysis.

Frozen external source: CCheCastaldo/mapppdr commit 88c73a507e...
Different from colony-code N_eff, arrival index, and future abundance prediction.
No absent observation is treated as a zero or an extinction.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pyreadr

SPECIES = ("ADPE", "CHPE", "GEPE")
SIC_BANDS = ((0, "near_0_100km"), (100, "offshore_100_500km"))
MIN_YEAR, MAX_YEAR = 1991, 2020
PINNED_COMMIT = "88c73a507e0921b2541c218c71eaf16721bc6502"


def load_rda(path, expected):
    items = pyreadr.read_r(str(path))
    return items[expected] if expected in items else next(iter(items.values()))


def finite_float(s):
    return pd.to_numeric(s, errors="coerce")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def fe_partial_r(frame, y, x, controls):
    if len(frame) < 8:
        return None, "too_few_rows", None
    dummies = [pd.get_dummies(frame[k].astype(str), drop_first=True).astype(float) for k in controls]
    mat = np.column_stack([np.ones(len(frame))] + [x.to_numpy() for x in dummies])
    yy = frame[y].to_numpy(float)
    xx = frame[x].to_numpy(float)
    rank = np.linalg.matrix_rank(mat)
    if len(frame) <= rank + 2:
        return None, "no_residual_df", int(rank)
    ry = yy - mat @ np.linalg.lstsq(mat, yy, rcond=None)[0]
    rx = xx - mat @ np.linalg.lstsq(mat, xx, rcond=None)[0]
    if np.linalg.norm(rx) < 1e-9 or np.linalg.norm(ry) < 1e-9:
        return None, "no_residual_variation", int(rank)
    return float(np.corrcoef(rx, ry)[0, 1]), "estimated", int(rank)


def pear(a, b):
    if len(a) < 5 or np.std(a) < 1e-10 or np.std(b) < 1e-10:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mapppdr", type=Path, required=True)
    p.add_argument("--ice-csv", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    sites = load_rda(a.mapppdr / "data" / "sites.rda", "sites")
    obs = load_rda(a.mapppdr / "data" / "penguin_obs.rda", "penguin_obs")
    ice = pd.read_csv(a.ice_csv)
    assert len(sites) == 729, f"MAPPPD site version drift: {len(sites)}"
    assert len(obs) == 5487, f"MAPPPD obs version drift: {len(obs)}"
    assert len(ice) == 9600, f"satellite product row drift: {len(ice)}"
    assert not sites.site_id.duplicated().any()
    assert not ice.duplicated(["site_id", "year", "month", "inner_km"]).any()

    nest = obs[obs.species_id.isin(SPECIES) & obs.type.eq("nests")].copy()
    nest["count"] = finite_float(nest["count"])
    nest["season"] = finite_float(nest["season"])
    nest = nest[nest["count"].notna() & nest["season"].between(MIN_YEAR, MAX_YEAR)].copy()
    assert (nest["count"] >= 0).all()
    assert (nest["season"] % 1 == 0).all()
    nest["season"] = nest["season"].astype(int)
    nest["site_id"] = nest["site_id"].astype(str)
    nest["species_id"] = nest["species_id"].astype(str)
    nest["method"] = (nest["vantage"].fillna("").astype(str)
                      .str.strip().str.lower().str.replace("_", " ", regex=False))
    nest = nest[~nest["method"].isin(("", "na", "nan", "unknown", "missing"))].copy()

    # Collapse repeated same-method records within a breeding season; never pool
    # different vantage methods, and never turn missing seasons into 0.
    base = (nest.groupby(["site_id", "species_id", "season", "method"], as_index=False)
             .agg(nests=("count", "median"), n_source_records=("count", "size")))
    meta = sites[["site_id", "region", "latitude", "longitude"]].copy()
    meta["site_id"] = meta["site_id"].astype(str)
    base = base.merge(meta, on="site_id", validate="many_to_one", how="left")
    assert base["region"].notna().all(), "Missing site region in MAPPPD"

    # Keep exactly one pre-specified method per site×species: most seasons,
    # then alphabetic method name as a deterministic tie-breaker.
    method_support = (base.groupby(["site_id", "species_id", "method"], as_index=False)
                      .agg(n_seasons=("season", "nunique")))
    method_support = method_support.sort_values(
        ["site_id", "species_id", "n_seasons", "method"],
        ascending=[True, True, False, True])
    chosen = method_support.drop_duplicates(["site_id", "species_id"])
    panel = base.merge(chosen[["site_id", "species_id", "method"]],
                       on=["site_id", "species_id", "method"],
                       validate="many_to_one")
    climate = ice[(ice.month == 9) & ice.complete_month.eq(True)].copy()
    assert len(climate) == 2400, f"September coverage unexpectedly {len(climate)}"
    climate = climate[["site_id", "year", "inner_km", "sic_mean"]]

    joined = None
    for inner, name in SIC_BANDS:
        subset = climate[climate.inner_km.eq(inner)][["site_id", "year", "sic_mean"]]
        subset = subset.rename(columns={"year": "season", "sic_mean": name})
        if joined is None:
            joined = panel.merge(subset, on=["site_id", "season"], validate="many_to_one", how="inner")
        else:
            joined = joined.merge(subset, on=["site_id", "season"], validate="one_to_one", how="left")
    if joined.empty:
        raise RuntimeError("All source site-year intersection missing")
    assert joined[["near_0_100km", "offshore_100_500km"]].notna().all().all()
    assert not joined.duplicated(["site_id", "species_id", "season"]).any()
    joined.sort_values(["species_id", "site_id", "season"]).to_csv(a.out / "site_species_season.csv", index=False)

    # Positive-to-positive consecutive observed seasons; no interpolation.
    new = joined.rename(columns={"season": "end_year", "nests": "n_end",
                                "near_0_100km": "near_end", "offshore_100_500km": "off_end"})
    older = joined.rename(columns={"nests": "n_start",
                                    "near_0_100km": "near_start", "offshore_100_500km": "off_start"})
    older["end_year"] = older["season"] + 1
    intervals = new.merge(
        older[["site_id", "species_id", "end_year", "n_start", "near_start", "off_start"]],
        on=["site_id", "species_id", "end_year"], validate="one_to_one", how="inner")
    intervals = intervals[(intervals.n_start > 0) & (intervals.n_end > 0)].copy()
    intervals["log_growth"] = np.log(intervals.n_end / intervals.n_start)
    intervals["near_change10"] = (intervals.near_end - intervals.near_start) / 10
    intervals["off_change10"] = (intervals.off_end - intervals.off_start) / 10
    intervals.sort_values(["species_id", "site_id", "end_year"]).to_csv(
        a.out / "annual_intervals.csv", index=False)

    summaries = []
    all_species = []
    for species in SPECIES:
        sf = joined[joined.species_id.eq(species)]
        si = intervals[intervals.species_id.eq(species)]
        site_rows = []
        for site, d in sf.groupby("site_id"):
            d = d.sort_values("season")
            x = d.season.to_numpy(float)
            y = np.log1p(d.nests.to_numpy(float))
            # Count trend is descriptive; not a vital rate.
            log_slope = (float(np.polyfit(x, y, 1)[0])
                         if len(d) >= 3 and x.max()-x.min() >= 5 else np.nan)
            near_slope = (float(np.polyfit(x, d.near_0_100km, 1)[0])
                          if len(d) >= 3 and x.max()-x.min() >= 5 else np.nan)
            off_slope = (float(np.polyfit(x, d.offshore_100_500km, 1)[0])
                         if len(d) >= 3 and x.max()-x.min() >= 5 else np.nan)
            site_rows.append(dict(species_id=species, site_id=site,
                region=d.region.iloc[0], method=d.method.iloc[0],
                seasons=len(d), first_season=int(x.min()), last_season=int(x.max()),
                count_trend_log1p_per_year=log_slope,
                near_ice_trend_pp_per_year=near_slope,
                offshore_ice_trend_pp_per_year=off_slope))
        frame = pd.DataFrame(site_rows)
        if not frame.empty:
            all_species.append(frame)
        # Spatial correlations use equal-weight eligible source sites, and
        # regional fixed-effects are explicitly distinct from pooled.
        good = frame.dropna(subset=["count_trend_log1p_per_year"]).copy()
        for variable in ["near_ice_trend_pp_per_year", "offshore_ice_trend_pp_per_year"]:
            pooled = pear(good[variable].to_numpy(), good.count_trend_log1p_per_year.to_numpy())
            within, status, rank = fe_partial_r(good, "count_trend_log1p_per_year", variable, ["region"])
            summaries.append(dict(species_id=species, unit="site_trend", predictor=variable,
                scope="count-season-matched_climate_trend", n_obs=len(good),
                n_sites=good.site_id.nunique(), n_years=good.last_season.nunique(),
                n_regions=good.region.nunique(), r=pooled, r_site_adjusted=None,
                r_site_year_adjusted=within, identification=status, controls_rank=rank))
        for variable in ["near_change10", "off_change10"]:
            within, status, rank = fe_partial_r(si, "log_growth", variable, ["site_id"])
            both, status2, rank2 = fe_partial_r(si, "log_growth", variable, ["site_id","end_year"])
            pooled = pear(si[variable].to_numpy(), si.log_growth.to_numpy())
            summaries.append(dict(species_id=species, unit="observed_positive_to_positive_annual_interval",
                predictor=variable, scope="same_exact_breeding_season_source_method", n_obs=len(si),
                n_sites=si.site_id.nunique(), n_years=si.end_year.nunique(),
                n_regions=si.region.nunique(), r=pooled, r_site_adjusted=within,
                r_site_year_adjusted=both, identification=status2, controls_rank=rank2))
    per_site = pd.concat(all_species, ignore_index=True)
    per_site.to_csv(a.out / "site_species_trends.csv", index=False)
    results = pd.DataFrame(summaries)
    results.to_csv(a.out / "association_atlas.csv", index=False)
    info = dict(status="observed_exploratory_mapped_MACRO_counts_not_future_breeding_predictor",
        source=dict(mapppdr_commit=PINNED_COMMIT,
          penguin_obs_rda_sha256=sha256(a.mapppdr/"data"/"penguin_obs.rda"),
          sites_rda_sha256=sha256(a.mapppdr/"data"/"sites.rda"),
          historical_sic_csv_sha256=sha256(a.ice_csv)),
        raw=dict(mapppdr_sites=len(sites), mapppdr_observations=len(obs),
          nest_records_three_species_known_method_1991_2020=len(nest),
          same_method_site_species_season_records=len(panel),
          climate_joined_site_species_season_records=len(joined),
          climate_joined_units=len(per_site), positive_annual_intervals=len(intervals)),
        by_species={sp:dict(site_units=int((per_site.species_id==sp).sum()),
          with_count_trends=int(per_site[per_site.species_id==sp].count_trend_log1p_per_year.notna().sum()),
          positive_annual_intervals=int((intervals.species_id==sp).sum()))
            for sp in SPECIES},
        explicit_cautions=[
          "40 macro climate sites are a non-random subset of 729 MAPPPD sites.",
          "Vantage labels are only compared within exactly matching raw method; mixed source calibration not assumed.",
          "Months within austral seasons and record precision are not verified from input here; season alignment is an assumption.",
          "Missing years and unobserved absences remain missing; observed zeros are used only for count trends.",
          "Association atlas is descriptive; source-site and common-year dependence are not significance-calibrated.",
          "No breeding-site occupancy transition inferred without comparable surveys and absences.",
          "No biological climate coefficient is transferred to CMIP6, and no future count is predicted."])
    (a.out/"summary.json").write_text(json.dumps(info,indent=2,allow_nan=False)+"\n")
    (a.out/"REPORT_JA.md").write_text(
      "# 3種MAPPPD繁殖数×過去海氷の広域相関 — 実測結果\n\n"
      "固定MAPPPD原データの全種3組から、方法を混合せず、実測の繁殖季ごとの記録を生成。"
      "同じ場所の翌年と前年を両方確認できる正の巣数計数だけ年差を作った。"
      "海氷は9月、0–100kmと100–500kmを別々に比較。"
      "解釈は相関であり、未来巣数の較正ではない。\n\n"
      "## サンプル\n\n"
      +json.dumps(info["raw"],ensure_ascii=False,indent=2)
      +"\n\n## 種別\n\n"
      +json.dumps(info["by_species"],ensure_ascii=False,indent=2)
      +"\n\n## 主要相関\n\n"
      +results.to_markdown(index=False)
      +"\n\n## 不確実性\n\n"
      +"\n".join("- "+z for z in info["explicit_cautions"])
      +"\n",encoding="utf-8")
    print(json.dumps(info,indent=2))
    print(results.to_string(index=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
