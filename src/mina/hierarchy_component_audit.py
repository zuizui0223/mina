"""Post-hoc component-count audit for the Palmer hierarchy result."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .hierarchical_variability import (
    EXPECTED_YEARS,
    STABLE_ROSTER_ISLANDS,
    _annual_log1p_growth,
    _linear_detrended_log1p,
    colony_roster_audit,
    island_series,
    subcolony_series,
    wang_loreau_raw,
)
from .lter import load_colony_rows


def _pairwise_summary(series: dict[str, np.ndarray]) -> dict[str, object]:
    labels=sorted(series)
    matrix=np.vstack([np.asarray(series[label],dtype=float) for label in labels])
    corr=np.corrcoef(matrix)
    values=corr[np.triu_indices(len(labels),1)]
    values=values[np.isfinite(values)]
    if values.size==0:
        raise ValueError("no finite pairwise correlations")
    return {
        "n_units":len(labels),
        "n_pairs":int(values.size),
        "mean_pairwise_correlation":float(np.mean(values)),
        "median_pairwise_correlation":float(np.median(values)),
        "min_pairwise_correlation":float(np.min(values)),
        "max_pairwise_correlation":float(np.max(values)),
    }


def _transform(
    series: dict[str,np.ndarray],
    kind: str,
) -> dict[str,np.ndarray]:
    if kind=="raw_abundance":
        return {key:np.asarray(value,dtype=float) for key,value in series.items()}
    if kind=="linear_detrended_log1p":
        return {key:_linear_detrended_log1p(value) for key,value in series.items()}
    if kind=="annual_log1p_growth":
        return {key:_annual_log1p_growth(value) for key,value in series.items()}
    raise ValueError(kind)


def _normalized_excess(beta: float,n_units: int) -> float:
    if n_units<2:
        raise ValueError("normalized beta requires at least two units")
    return (beta-1.0)/(n_units-1.0)


def analyze(path: str|Path) -> dict[str,object]:
    rows=load_colony_rows(path)
    audit=colony_roster_audit(rows)
    stable=tuple(
        island for island in STABLE_ROSTER_ISLANDS
        if bool(audit[island]["roster_stable"])
    )
    if stable!=STABLE_ROSTER_ISLANDS:
        raise ValueError(f"stable-roster drift: {stable}")

    islands_raw=island_series(rows,STABLE_ROSTER_ISLANDS,EXPECTED_YEARS)
    sub_raw=subcolony_series(
        rows,STABLE_ROSTER_ISLANDS,EXPECTED_YEARS,audit
    )

    among_raw=wang_loreau_raw(islands_raw)
    among_norm=_normalized_excess(
        float(among_raw["beta_spatial"]),
        int(among_raw["n_units"]),
    )
    raw_normalized={"among_islands":{
        "n_units":int(among_raw["n_units"]),
        "beta_spatial":float(among_raw["beta_spatial"]),
        "normalized_excess_beta":among_norm,
    }}
    all_norm=True
    for island in STABLE_ROSTER_ISLANDS:
        prefix=f"{island}:"
        local={k:v for k,v in sub_raw.items() if k.startswith(prefix)}
        stat=wang_loreau_raw(local)
        norm=_normalized_excess(
            float(stat["beta_spatial"]),int(stat["n_units"])
        )
        raw_normalized[island]={
            "n_units":int(stat["n_units"]),
            "beta_spatial":float(stat["beta_spatial"]),
            "normalized_excess_beta":norm,
        }
        all_norm=all_norm and norm>among_norm

    pairwise={}
    all_pairwise=True
    for kind in (
        "raw_abundance",
        "linear_detrended_log1p",
        "annual_log1p_growth",
    ):
        among=_pairwise_summary(_transform(islands_raw,kind))
        within={}
        for island in STABLE_ROSTER_ISLANDS:
            prefix=f"{island}:"
            local={k:v for k,v in sub_raw.items() if k.startswith(prefix)}
            within[island]=_pairwise_summary(_transform(local,kind))
        all_lower=all(
            float(within[island]["mean_pairwise_correlation"])
            < float(among["mean_pairwise_correlation"])
            for island in STABLE_ROSTER_ISLANDS
        )
        all_pairwise=all_pairwise and all_lower
        pairwise[kind]={
            "among_islands":among,
            "within_islands":within,
            "all_within_mean_correlations_below_among_mean":bool(all_lower),
        }

    return {
        "schema_version":1,
        "analysis_id":"mina-palmer-hierarchy-component-count-audit-v1",
        "status":"post_hoc_component_count_robustness_diagnostic",
        "eligible_islands":list(STABLE_ROSTER_ISLANDS),
        "raw_normalized_excess_beta":raw_normalized,
        "pairwise_correlation_audit":pairwise,
        "decision":{
            "all_within_normalized_excess_beta_above_among":bool(all_norm),
            "all_signals_all_within_mean_pairwise_correlations_below_among":bool(
                all_pairwise
            ),
            "hierarchy_not_explained_only_by_more_within_island_units":bool(
                all_norm and all_pairwise
            ),
        },
        "interpretation_boundary":{
            "post_hoc_diagnostic":True,
            "confirmatory_endpoint":False,
            "causal_inference":False,
            "pairwise_correlation_replaces_wang_loreau_partition":False,
        },
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--census",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=analyze(a.census)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return 0


if __name__=="__main__":
    raise SystemExit(main())
