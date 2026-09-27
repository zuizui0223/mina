"""External spatial triangulation for the Palmer colony-network result."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build(colony_result_path: str | Path, evidence_path: str | Path) -> dict[str, object]:
    colony=_load(colony_result_path)
    evidence=_load(evidence_path)
    if colony["primary"]["decision"]!="supported":
        raise ValueError("frozen colony-network endpoint is no longer supported")

    source=next(
        item for item in evidence["sources"]
        if item["source_id"]=="cimino_2025_landscape_ecology"
    )
    obs=source["observations"]

    historic=float(obs["historic_active_subcolonies_1989"])
    active=float(obs["active_subcolonies_2022"])
    south_hist=float(obs["south_aspect_historic_subcolonies"])
    south_ext=float(obs["south_aspect_extinct_by_2022"])
    north_hist=float(obs["north_aspect_historic_subcolonies"])
    north_ext=float(obs["north_aspect_extinct_by_2022"])

    spatial_contraction=(active/historic) < 0.5
    topographic_attrition=(
        south_ext/south_hist > north_ext/north_hist
        and float(obs["area_extinction_year_correlation_R"]) > 0
    )
    internal_signal=(
        float(colony["primary"]["full_data_coefficient"]) > 0
        and float(colony["primary"]["loyo"]["mse_gain_c0_minus_c1"]) > 0
    )
    crosswalk=(
        evidence["crosswalk_status"]["lter_colony_code_to_published_polygon"]
        == "resolved"
    )
    phenomenon=bool(spatial_contraction and topographic_attrition and internal_signal)

    return {
        "schema_version":1,
        "result_id":"mina-palmer-external-spatial-triangulation-result-v1",
        "decision":{
            "phenomenon_level_spatial_convergence":phenomenon,
            "identifier_level_validation":bool(crosswalk),
            "causal_fragmentation_validated":False,
        },
        "internal_colony_network":{
            "effective_colony_beta":float(colony["primary"]["full_data_coefficient"]),
            "heldout_mse_gain":float(colony["primary"]["loyo"]["mse_gain_c0_minus_c1"]),
        },
        "external_torgersen_spatial":{
            "historic_active_subcolonies":int(historic),
            "active_subcolonies_2022":int(active),
            "active_footprint_fraction":active/historic,
            "south_extinction_fraction":south_ext/south_hist,
            "north_extinction_fraction":north_ext/north_hist,
            "south_minus_north_extinction_fraction":south_ext/south_hist - north_ext/north_hist,
            "active_to_extinct_historic_area_ratio":(
                float(obs["active_historic_area_mean_m2"])
                / float(obs["extinct_historic_area_mean_m2"])
            ),
            "area_extinction_year_correlation_R":float(obs["area_extinction_year_correlation_R"]),
            "area_extinction_year_p":float(obs["area_extinction_year_p"]),
        },
        "crosswalk_status":evidence["crosswalk_status"],
        "interpretation":{
            "supported":"Independent spatial mapping shows real contraction and habitat-structured attrition of Torgersen breeding footprints, converging with the census-derived result that breeder distribution among subcolonies indexes local vulnerability.",
            "boundary":"The external polygons cannot yet be matched one-to-one to Palmer LTER colony_code values, so the convergence is at the process/phenomenon level rather than an identifier-level validation of the exact effective-colony metric.",
        },
    }


def markdown(result: dict[str, object]) -> str:
    x=result["external_torgersen_spatial"]
    d=result["decision"]
    return f"""# Torgersen external spatial triangulation v1

Independent spatial reconstruction provides **phenomenon-level convergence: {d["phenomenon_level_spatial_convergence"]}**.

- Historic active sub-colonies: **{x["historic_active_subcolonies"]}**
- Active mapped footprints in 2022: **{x["active_subcolonies_2022"]}**
- Fraction of historic footprints still active: **{100*x["active_footprint_fraction"]:.1f}%**
- South-aspect extinction fraction: **{100*x["south_extinction_fraction"]:.1f}%**
- North-aspect extinction fraction: **{100*x["north_extinction_fraction"]:.1f}%**
- Historic-area / extinction-year correlation: **R={x["area_extinction_year_correlation_R"]:.2f}**

The frozen mina effective-colony-number result is directionally concordant: a more distributed colony network predicts slightly better next-year island growth.

This is **not** a colony-ID-level validation. The public census `colony_code` identifiers have not been resolved to the independent GIS polygon identifiers, so causal habitat-fragmentation language remains out of scope.
"""


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--colony-result",required=True,type=Path)
    p.add_argument("--evidence",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-md",required=True,type=Path)
    a=p.parse_args()
    x=build(a.colony_result,a.evidence)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_md.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    a.out_md.write_text(markdown(x),encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
