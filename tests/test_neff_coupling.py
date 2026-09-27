import csv

from mina.neff_coupling import simulate


ISLANDS=("CHR","COR","HUM","LIT","TOR")


def _fixture(path):
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"])
        w.writerow(["","UTC","","","1"])
        for year in range(1991,2018):
            for k,island in enumerate(ISLANDS):
                total=max(20,1200-25*(year-1991)+50*k)
                shares=(0.55,0.30,0.15)
                for j,share in enumerate(shares,1):
                    w.writerow([
                        f"PAL{year}",f"{year}-11-15T00:00:00Z",
                        island,str(j),round(total*share)
                    ])


def test_mechanical_coupling_simulation_is_reproducible(tmp_path,monkeypatch):
    path=tmp_path/"census.csv"
    _fixture(path)
    import mina.neff_coupling as mod
    monkeypatch.setattr(mod,"OBSERVED_BETA",0.1)
    a=simulate(path,simulations=20,seed=77)
    b=simulate(path,simulations=20,seed=77)
    assert a["error_models"]==b["error_models"]
    assert set(a["error_models"])=={
        "poisson","gamma_poisson_cv10","gamma_poisson_cv20"
    }
    for result in a["error_models"].values():
        assert result["coupled_beta"]["sd"]>=0
        assert result["decoupled_beta"]["sd"]>=0
        assert "median_fraction_of_observed_beta" in result["paired_coupling_bias"]
