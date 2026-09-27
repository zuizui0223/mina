import csv
import math

from mina.timescale import analyze


ISLANDS=("CHR","COR","HUM","LIT","TOR")


def _write_census(path):
    sea={year:180+40*math.sin((year-1991)*0.9)+2*(year-1991) for year in range(1992,2018)}
    counts={island:1000+100*i for i,island in enumerate(ISLANDS)}
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"])
        w.writerow(["","UTC","","","1"])
        for year in range(1991,2018):
            if year>1991:
                g=-0.09+0.00035*sea[year]
                for island in ISLANDS:
                    counts[island]*=math.exp(g)
            for island in ISLANDS:
                w.writerow([f"PAL{year}",f"{year}-11-15T00:00:00Z",island,"1",round(counts[island])])
    return sea


def _write_sea(path,sea):
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["Year","SIDuration","IceDays","SIRetreat"])
        for year in range(1992,2018):
            w.writerow([year,sea[year],sea[year]-10,320])


def test_timescale_pipeline(tmp_path):
    census=tmp_path/"census.csv"; ice=tmp_path/"ice.csv"
    sea=_write_census(census); _write_sea(ice,sea)
    x=analyze(census,ice)
    assert x["primary"]["K"]==5
    assert x["primary"]["n_windows"]==22
    assert x["primary"]["validation"]["min_train_windows"]>=5
    assert x["primary"]["full_fit"]["seaice_beta_T1"]>0
