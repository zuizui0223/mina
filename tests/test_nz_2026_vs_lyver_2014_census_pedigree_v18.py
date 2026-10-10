"""Original publication 2012 counts match new compiled NZ 2026 file: provenance only."""
import importlib.util
from pathlib import Path
import pytest

FILE=Path(__file__).resolve().parents[1]/"scripts/audit_nz_2026_vs_lyver_2014_census_pedigree_v18.py"
spec=importlib.util.spec_from_file_location("pedigree_v18",FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def source_fixture():
    return {
      "status":"SOURCE_XLSX_VALIDATED_AND_STRUCTURAL_COVERAGE_REPORTED",
      "verified_md5":m.ORIGINAL_PUBLISHER_MD5,
      "focal_Royds_Crozier_CapeBird_source_counts":{
         "Cape Royds":{"2012":3083},
         "Cape Bird North":{"2012":50701},
         "Cape Bird Middle":{"2012":4912},
         "Cape Bird South":{"2012":20083},
         "Cape Crozier East":{"2012":30147},
         "Cape Crozier West":{"2012":242193}
      }
    }

def test_exact_2012_aggregrate_counts_are_historical_replication_not_new_survey():
    z=m.compare(source_fixture())
    assert z["status"]=="SAME_PUBLISHED_2012_CENSUS_AGGREGATES_REPRODUCED"
    assert z["n_2014_independent_aggregate_colony_counts_compared"]==3
    assert z["original_2026_survey_subsite_components_compared"]==6
    assert z["exact_three_aggregate_match"]
    for name,expected in m.REF_PUBLISHED_2012.items():
        assert z["published_source_overlaps"][name]["NZ_2026_2012_aggregate"]==expected
    assert not z["2026_independent_2012_new_measurement_claim_supported"]
    assert z["independent_archive_not_independent_census_observations"]
    assert not z["not_a_preregistered_biological_hypothesis_test"] is False

def test_one_earlier_publication_aggregate_mismatch_is_rejected():
    z=source_fixture()
    z["focal_Royds_Crozier_CapeBird_source_counts"]["Cape Bird South"]["2012"]=20084
    r=m.compare(z)
    assert not r["exact_three_aggregate_match"]
    assert r["status"].startswith("HOLD_")

def test_not_use_source_without_published_MD5():
    z=source_fixture()
    z["verified_md5"]="0"*32
    with pytest.raises(ValueError,match="MD5"):
        m.compare(z)

def test_missing_previously_printed_2012_record_never_zero_filled():
    z=source_fixture()
    z["focal_Royds_Crozier_CapeBird_source_counts"]["Cape Crozier East"]["2012"]=None
    with pytest.raises(ValueError,match="Missing"):
        m.compare(z)
