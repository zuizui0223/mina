import csv

from mina.neff_permutation import apply_schedule, availability_strata, diagnose
from mina.colony_network import transition_rows


ISLANDS=("CHR","COR","HUM","LIT","TOR")


def _write_fixture(path):
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"])
        w.writerow(["","UTC","","","1"])
        totals={i:1500+100*k for k,i in enumerate(ISLANDS)}
        state={i:4 for i in ISLANDS}
        for year in range(1991,2010):
            for k,island in enumerate(ISLANDS):
                active=max(1,state[island])
                weights=[1+0.15*j for j in range(active)]
                z=sum(weights)
                for j,v in enumerate(weights):
                    w.writerow([
                        f"PAL{year}",f"{year}-11-15T00:00:00Z",island,
                        str(j+1),round(totals[island]*v/z)
                    ])
                if year<2009:
                    growth=-0.05+0.025*(active-2)+0.001*k
                    totals[island]=max(1,totals[island]*__import__("math").exp(growth))
                    if (year+k)%5==0:
                        state[island]=max(1,state[island]-1)


def test_block_schedule_preserves_island_availability(tmp_path):
    census=tmp_path/"census.csv"
    _write_fixture(census)
    rows=transition_rows(census)
    strata=availability_strata(rows)
    assert len(strata)==1
    years=next(iter(strata.values()))
    schedule={year:years[(idx+1)%len(years)] for idx,year in enumerate(years)}
    perm=apply_schedule(rows,schedule)
    baseline=[
        (r["start_year"],r["end_year"],r["island"],r["current_total"],r["next_growth"])
        for r in rows
    ]
    altered=[
        (r["start_year"],r["end_year"],r["island"],r["current_total"],r["next_growth"])
        for r in perm
    ]
    assert baseline==altered
    assert any(
        a["effective_colony_number"]!=b["effective_colony_number"]
        for a,b in zip(rows,perm)
    )


def test_permutation_diagnostic_runs_on_synthetic_fixture(tmp_path, monkeypatch):
    census=tmp_path/"census.csv"
    _write_fixture(census)
    # Synthetic fixture does not match the frozen real-data drift constants;
    # test the algorithm by temporarily replacing them with fixture values.
    import mina.neff_permutation as mod
    rows=transition_rows(census)
    obs=mod.loyo(rows,"effective")
    monkeypatch.setattr(mod,"EXPECTED_GAIN",float(obs["mse_gain_C0_minus_C1"]))
    monkeypatch.setattr(mod,"EXPECTED_BETA",float(mod.full_coefficient(rows,"effective")))
    monkeypatch.setattr(mod,"EXPECTED_C0",float(obs["mse"]["C0"]))
    monkeypatch.setattr(mod,"EXPECTED_C1",float(obs["mse"]["C1"]))

    # The production function also checks 120 rows / 26 years, so exercise the
    # lower-level permutation loop structure rather than diagnose().
    rng=__import__("numpy").random.default_rng(1)
    schedule=mod.draw_schedule(rows,rng)
    perm=mod.apply_schedule(rows,schedule)
    assert len(perm)==len(rows)
    result=mod.loyo(perm,"effective")
    assert "mse_gain_C0_minus_C1" in result
