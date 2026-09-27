import csv
import math

from mina.mechanism import ISLANDS, analyze


def _census(path):
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"])
        w.writerow(["","UTC","","","1"])
        counts={i:1000+100*k for k,i in enumerate(ISLANDS)}
        for year in range(1991,2018):
            if year>1991:
                ice=150+20*math.sin(year)
                for k,i in enumerate(ISLANDS):
                    growth=-0.08+0.0015*(ice-150)+0.003*k
                    counts[i]=max(0,counts[i]*math.exp(growth))
            for i in ISLANDS:
                w.writerow([f"PAL{year}",f"{year}-11-20T00:00:00Z",i,"1.0",round(counts[i])])


def _seaice(path):
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow(["Year","SIAdvance","SIRetreat","SIDuration","IceDays","SIRetrProx","SIExtent","SIArea","OWArea","TotalSIConc"])
        for year in range(1991,2021):
            duration=150+20*math.sin(year)
            w.writerow([year,150,300,duration,duration-10,-65,1,1,1,1])


def test_mechanism_pipeline(tmp_path):
    census=tmp_path/"census.csv"
    sea=tmp_path/"sea.csv"
    _census(census); _seaice(sea)
    x=analyze(census,sea)
    assert x["growth_row_count"]==26*5
    assert x["primary_loyo"]["n_years"]==26
    assert x["full_coefficients"]["regional_beta_M1"]>0
    assert x["primary_loyo"]["primary_mse_gain_M0_minus_M1"]>0
