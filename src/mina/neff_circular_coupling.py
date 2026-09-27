"""Mechanical-coupling diagnostic using a serial-structure-preserving topology null."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .colony_network import transition_rows
from .lter import ISLANDS
from .neff_circular_shift import island_sequences
from .neff_coupling import (
    ERROR_MODELS,
    OBSERVED_BETA,
    _draw_counts,
    _effective,
    _fit_beta,
    _state_compositions,
    _summary,
)


def draw_circular_donor_map(
    transitions: list[dict[str, object]],
    rng: np.random.Generator,
) -> tuple[dict[tuple[int, str], int], dict[str, int]]:
    seq=island_sequences(transitions)
    while True:
        lags={
            island:int(rng.integers(0,len(seq[island]["years"])))
            for island in ISLANDS
        }
        if any(lag!=0 for lag in lags.values()):
            break

    donor: dict[tuple[int,str],int]={}
    for island in ISLANDS:
        years=np.asarray(seq[island]["years"],dtype=int)
        lag=lags[island]
        shifted=np.roll(years,lag)
        for target,source in zip(years.tolist(),shifted.tolist()):
            donor[(int(target),island)]=int(source)
    return donor,lags


def simulate(
    census_path: str|Path,
    simulations: int=10000,
    seed: int=20260927,
) -> dict[str,object]:
    transitions=transition_rows(census_path)
    states=_state_compositions(census_path)

    islands=[str(row["island"]) for row in transitions]
    start_year=np.asarray(
        [float(row["start_year"]) for row in transitions],dtype=float
    )
    current_keys=[
        (int(row["start_year"]),str(row["island"])) for row in transitions
    ]
    next_keys=[
        (int(row["end_year"]),str(row["island"])) for row in transitions
    ]

    if len(transitions)!=120:
        raise ValueError(f"frozen transition-row drift: {len(transitions)}")

    seq=island_sequences(transitions)
    lengths={island:len(seq[island]["years"]) for island in ISLANDS}
    if lengths!={"CHR":26,"COR":26,"HUM":26,"LIT":16,"TOR":26}:
        raise ValueError(f"frozen island sequence-length drift: {lengths}")

    rng=np.random.default_rng(seed)
    outputs: dict[str,object]={}

    for model_name,cv in ERROR_MODELS:
        coupled=np.empty(simulations,dtype=float)
        decoupled=np.empty(simulations,dtype=float)
        lag_frequency={
            island:np.zeros(lengths[island],dtype=int) for island in ISLANDS
        }

        for replicate in range(simulations):
            donor_map,lags=draw_circular_donor_map(transitions,rng)
            for island,lag in lags.items():
                lag_frequency[island][lag]+=1

            predictor_counts: dict[tuple[int,str],np.ndarray]={}
            independent_counts: dict[tuple[int,str],np.ndarray]={}

            needed=sorted(set(current_keys)|set(next_keys))
            for year,island in needed:
                target=states[(year,island)]
                if float(target["total"])<=0:
                    predictor_counts[(year,island)]=np.zeros(0,dtype=float)
                    independent_counts[(year,island)]=np.zeros(0,dtype=float)
                    continue

                donor_year=donor_map.get((year,island),year)
                donor=states[(donor_year,island)]
                shares=np.asarray(donor["shares"],dtype=float)
                predictor_counts[(year,island)]=_draw_counts(
                    float(target["total"]),shares,rng,cv
                )
                independent_counts[(year,island)]=_draw_counts(
                    float(target["total"]),shares,rng,cv
                )

            effective=np.asarray(
                [_effective(predictor_counts[key]) for key in current_keys],
                dtype=float,
            )
            current_coupled=np.asarray(
                [float(np.sum(predictor_counts[key])) for key in current_keys],
                dtype=float,
            )
            current_decoupled=np.asarray(
                [float(np.sum(independent_counts[key])) for key in current_keys],
                dtype=float,
            )
            next_independent=np.asarray(
                [float(np.sum(independent_counts[key])) for key in next_keys],
                dtype=float,
            )

            coupled[replicate]=_fit_beta(
                islands,start_year,current_coupled,next_independent,effective
            )
            decoupled[replicate]=_fit_beta(
                islands,start_year,current_decoupled,next_independent,effective
            )

        bias=coupled-decoupled
        exceed_coupled=int(np.sum(coupled>=OBSERVED_BETA))
        exceed_decoupled=int(np.sum(decoupled>=OBSERVED_BETA))
        outputs[model_name]={
            "multiplicative_cv":cv,
            "coupled_beta":{
                **_summary(coupled),
                "exceedances_ge_observed":exceed_coupled,
                "one_sided_probability_ge_observed":(
                    1.0+exceed_coupled
                )/(simulations+1.0),
            },
            "decoupled_beta":{
                **_summary(decoupled),
                "exceedances_ge_observed":exceed_decoupled,
                "one_sided_probability_ge_observed":(
                    1.0+exceed_decoupled
                )/(simulations+1.0),
            },
            "paired_coupling_bias":{
                **_summary(bias),
                "median_fraction_of_observed_beta":float(
                    np.median(bias)/OBSERVED_BETA
                ),
                "mean_fraction_of_observed_beta":float(
                    np.mean(bias)/OBSERVED_BETA
                ),
            },
            "lag_frequency":{
                island:{
                    str(lag):int(count)
                    for lag,count in enumerate(lag_frequency[island].tolist())
                }
                for island in ISLANDS
            },
        }

    survives=all(
        float(outputs[name]["coupled_beta"]["one_sided_probability_ge_observed"])
        <=0.05
        for name,_ in ERROR_MODELS
    )
    return {
        "schema_version":1,
        "analysis_id":"mina-neff-circular-coupling-v1",
        "status":"serial_structure_preserving_same_census_error_diagnostic",
        "simulations_per_error_model":simulations,
        "seed":seed,
        "observed_standardized_beta":OBSERVED_BETA,
        "transition_row_count":len(transitions),
        "sequence_lengths":lengths,
        "error_models":outputs,
        "decision":{
            "observed_beta_unusual_under_all_coupled_circular_nulls":bool(survives)
        },
        "boundary":{
            "stylized_error_not_calibrated_observer_uncertainty":True,
            "latent_topology_null_preserves_island_cyclic_time_structure":True,
            "held_out_predictive_gain_remains_unsupported":True,
            "causal_habitat_claim":False,
        },
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--census",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--simulations",type=int,default=10000)
    p.add_argument("--seed",type=int,default=20260927)
    a=p.parse_args()
    result=simulate(a.census,a.simulations,a.seed)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return 0


if __name__=="__main__":
    raise SystemExit(main())
