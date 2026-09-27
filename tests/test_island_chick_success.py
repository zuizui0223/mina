import csv
import math

from mina.island_chick_success import analyze


ISLANDS=("CHR","COR","HUM","LIT","TOR")


def _write_chicks(path):
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow([
            "study_name","time","island_name","colony_code",
            "num_breeding_pairs","num_chicks","census_time"
        ])
        w.writerow(["","UTC","","","","",""])
        for season in range(1991,2018):
            census_year=season+1
            regional=0.05*math.sin(0.3*season)
            for k,island in enumerate(ISLANDS):
                island_signal=0.20*math.sin(0.71*season+1.2*k)
                for code in range(4):
                    adult=150+20*code+5*k
                    success=1.1+regional+island_signal+0.02*math.sin(
                        1.3*season+0.5*code
                    )
                    chicks=max(0,round(adult*success))
                    w.writerow([
                        f"PAL{season}",
                        f"{census_year}-01-20T00:00:00Z",
                        island,
                        str(code+1),
                        adult,
                        chicks,
                        "12:00",
                    ])


def _write_adults(path):
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow([
            "study_name","time","island_name","colony_code",
            "num_breeding_pairs"
        ])
        w.writerow(["","UTC","","","1"])
        for year in range(1991,2018):
            for k,island in enumerate(ISLANDS):
                for code in range(4):
                    adult=150+20*code+5*k
                    w.writerow([
                        f"PAL{year}",
                        f"{year}-11-20T00:00:00Z",
                        island,
                        str(code+1),
                        adult,
                    ])


def test_chick_success_detects_independent_island_signal(tmp_path):
    chicks=tmp_path/"chicks.csv"
    adults=tmp_path/"adults.csv"
    _write_chicks(chicks)
    _write_adults(adults)
    x=analyze(chicks,adults,n_permutations=500,seed=23)
    assert x["five_island_primary"]["observed"]["island_success_covariance_contrast"]>0
    assert x["five_island_primary"]["null"]["two_sided_p"]<=0.05
    assert x["four_island_no_litchfield"]["null"]["two_sided_p"]<=0.05
    assert x["decision"]["strong_independent_validation"] is True
    assert x["adult_denominator_overlap"]["exact_fraction"]==1.0


def test_minimum_season_rule_excludes_short_code(tmp_path):
    chicks=tmp_path/"chicks.csv"
    adults=tmp_path/"adults.csv"
    _write_chicks(chicks)
    _write_adults(adults)
    with chicks.open("a",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        for season in range(1991,1995):
            w.writerow([
                f"PAL{season}",
                f"{season+1}-01-20T00:00:00Z",
                "CHR","99",50,50+season%2,"12:00"
            ])
    x=analyze(chicks,adults,n_permutations=99,seed=24)
    records=x["five_island_primary"]["eligibility"]["colonies"]
    assert not any(r["island"]=="CHR" and r["colony_code"]=="99" for r in records)
