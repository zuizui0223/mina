import pandas as pd

from scripts.audit_adelie_guano_reference_overlap import choose_column


def test_pangaea_colony_id_column():
    df = pd.DataFrame(columns=["ID (of colony)", "Latitude", "Longitude"])
    assert choose_column(df, ["ID (of colony)", "ID"]) == "ID (of colony)"


def test_column_lookup_is_case_insensitive():
    df = pd.DataFrame(columns=["Latitude", "Longitude"])
    assert choose_column(df, ["latitude"]) == "Latitude"
