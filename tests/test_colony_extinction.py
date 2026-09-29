import csv
from pathlib import Path
import numpy as np
from mina.colony_extinction import risk_rows,sets,contrast
from mina.colony_extinction_zero_boundary import subset_dist

def write_panel(path: Path):
    rows=[]
    series={
        "1":[10,5,0,0,0],
        "2":[40,35,30,25,20],
        "3":[8,4,0,3,2],
    }
    for i,year in enumerate(range(2000,2005)):
        for code,values in series.items():
            rows.append(dict(study_name=f"S{year}",time=f"{year}-11-01T00:00:00Z",
                island_name="CHR",colony_code=code,num_breeding_pairs=values[i]))
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)

def test_durable_zero_excludes_reappearance(tmp_path):
    p=tmp_path/"x.csv";write_panel(p)
    rows=risk_rows(p,islands=("CHR",),later=2)
    events=[r for r in rows if r["event"]]
    assert len(events)==1
    assert events[0]["colony_code"]=="1"
    assert events[0]["end_year"]==2002

def test_event_is_smaller_in_matched_risk_set(tmp_path):
    p=tmp_path/"x.csv";write_panel(p)
    ss=sets(risk_rows(p,islands=("CHR",),later=2),True)
    assert len(ss)==1
    assert contrast(ss[0])<0

def test_zero_null_prefers_small_colonies(tmp_path):
    p=tmp_path/"x.csv";write_panel(p)
    s=sets(risk_rows(p,islands=("CHR",),later=2),True)[0]
    vals,w,_=subset_dist(s,0.0)
    assert np.isclose(w.sum(),1.0)
    assert vals[np.argmax(w)]<0
