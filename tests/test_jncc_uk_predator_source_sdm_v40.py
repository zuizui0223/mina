"""V40 probability maps: invented island records only, no raw ecological outcomes."""
import csv
import json
import math
from pathlib import Path
import sys
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import map_jncc_uk_island_predator_sdm_v40 as v


def invented_domain(n=506):
    """20 geographic block groups, species varying as fixed synthetic patterns."""
    islands={}
    codes={}
    for i in range(n):
        lat=49+(i//26)*.65   # many geographic cells
        lon=-12+(i%26)*.51
        # 10-13 cells each block x variable
        islands[i+1]={
            "low_tide_area_h":20+(i%90)*3,
            "high_tide_area_h":18+(i%90)*2,
            "latitude":lat,
            "longitude":lon,
            "human_population":i%7,
            "ferry":"passenger_ferry" if i%7==0 else " ",
        }
        positive="1" if (i%4==0) else ("2" if i%5==0 else "0")
        codes[i+1]={sp:positive for sp in v.TAXA}
    return islands,codes


def test_original_506_source_domain_and_bounds():
    islands,status=invented_domain()
    rows=v.construct_domain(islands,status)
    assert len(rows)==506
    assert len({r["lowid"] for r in rows})==506
    assert all(r["area_ha"]>10 for r in rows)
    assert all(len(r["features"])==5 for r in rows)
    assert all(isinstance(r["group_1deg"],str) for r in rows)
    assert v.listed_ferry(" ")==0
    assert v.listed_ferry("passenger_ferry")==1
    assert v.listed_ferry(None)==0


def test_code_3_excluded_from_training_but_probability_available():
    islands,status=invented_domain()
    for i in (11,19,29):status[i]["Brown rat"]="3"
    domain=v.construct_domain(islands,status)
    model,rows=v.one_species(domain,"Brown rat",np.random.default_rng(20261027))
    assert model["training_original_source_islands"]==503
    assert model["original_source_status_possible_code3_excluded"]==3
    assert len(rows)==506
    assert sum(r["source_possible_code3_not_used_in_fit"] for r in rows)==3
    assert all(0<=r["p_documented_positive"]<=1 for r in rows)
    assert model["bootstrap"]["bootstrap_valid_refits"]>=100


def test_source_code_0_not_a_verified_negative():
    assert "NOT calibrated true ecological occupancy" in v.PROBABILITY_TARGET
    assert v.MIN_AREA_HA==10.0
    assert v.ESM5_SHA=="3d876a92e68122f8594b320e0794a54c5e8c7306c5a0e6252cbc24776ce1d1c5"


def test_blocks_are_never_mixed_between_outer_train_and_test():
    islands,status=invented_domain()
    domain=v.construct_domain(islands,status)
    used=[r for r in domain if r["source_status"]["American mink"] in {"0","1","2"}]
    y=np.asarray([int(r["source_status"]["American mink"] in {"1","2"}) for r in used])
    result=v.geographic_outer_cv(domain,y,used,"American mink")
    assert result["source_label_status"] in {
        "SOURCE_LABEL_GEOGRAPHICALLY_PORTABLE_ONLY",
        "RESEARCH_ONLY_NOT_GEOGRAPHICALLY_PORTABLE",
        "NOT_VALIDATED",
    }
    if result.get("heldout") is not None:
        assert len(result["heldout_fold_support"])==5
        assert all(x["test_distinct_spatial_blocks"]>=1 for x in result["heldout_fold_support"])
        assert all(x["source_confirmed_or_probable"]>=3 for x in result["heldout_fold_support"])


def test_calibration_bins_and_bootstrap_quantiles_are_valid():
    rng=np.random.default_rng(11)
    y=np.asarray([0,1]*50)
    p=np.linspace(.01,.99,100)
    bins,ece=v.reliability(y,p)
    assert len(bins)==5
    assert sum(b["n"] for b in bins)==100
    assert 0<=ece<=1
    islands,status=invented_domain()
    domain=v.construct_domain(islands,status)
    model,rows=v.one_species(domain,"House mouse",np.random.default_rng(v.BOOT_SEED))
    for r in rows:
        assert 0<=r["p_documented_positive"]<=1
        if r["model_bootstrap_p05"] is not None:
            assert 0<=r["model_bootstrap_p05"]<=r["model_bootstrap_p95"]<=1


def test_GIS_exports_506_points_four_taxa(tmp_path):
    islands,status=invented_domain()
    domain=v.construct_domain(islands,status)
    prob={
        sp:[{
            "lowid":r["lowid"],"species":sp,
            "latitude":r["latitude"],"longitude":r["longitude"],
            "p_documented_positive":.25,
            "model_bootstrap_p05":.1,"model_bootstrap_p95":.5,
            "status":"RESEARCH_ONLY_NOT_GEOGRAPHICALLY_PORTABLE",
            "source_possible_code3_not_used_in_fit":False
        } for r in domain]
        for sp in v.TAXA
    }
    receipt=v.export_products(prob,domain,tmp_path/"sdm")
    assert receipt["CSV_source_island_x_species_rows"]==2024
    assert receipt["GEOJSON_original_island_points"]==506
    with open(receipt["CSV"],encoding="utf-8",newline="") as f:
        data=list(csv.DictReader(f))
    assert len(data)==2024
    with open(receipt["GEOJSON"],encoding="utf-8") as f:
        geo=json.load(f)
    assert len(geo["features"])==506
    assert geo["features"][0]["geometry"]["type"]=="Point"
    assert geo["features"][0]["properties"]["american_mink_p_source_positive"]==.25


def test_insufficient_source_labels_stop_without_promoting_to_occupancy():
    islands,status=invented_domain()
    domain=v.construct_domain(islands,status)
    for r in domain:
        r["source_status"]["Feral cat"]="1" if r["lowid"]<6 else "0"
    model,rows=v.one_species(domain,"Feral cat",np.random.default_rng(1))
    assert model["status"]=="STOP_TOO_FEW_ORIGINAL_SOURCE_LABELS"
    assert rows is None
