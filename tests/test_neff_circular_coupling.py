import csv
import math
from pathlib import Path

import numpy as np

from mina.colony_network import transition_rows
from mina.neff_circular_coupling import draw_circular_donor_map


ISLANDS=("CHR","COR","HUM","LIT","TOR")


def _write_fixture(path: Path):
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow([
            "study_name","time","island_name","colony_code","num_breeding_pairs"
        ])
        w.writerow(["","UTC","","","1"])
        for year in range(1991,2018):
            for i,island in enumerate(ISLANDS):
                active=not (island=="LIT" and year>=2007)
                total=(1500+100*i)-30*(year-1991) if active else 0
                weights=np.asarray([0.55,0.30,0.15],dtype=float)
                tilt=0.025*math.sin((year-1991+i)/2.5)
                weights=weights+np.asarray([tilt,-tilt/2,-tilt/2])
                counts=np.rint(total*weights).astype(int) if active else np.zeros(3,dtype=int)
                if active:
                    counts[-1]=max(0,total-int(np.sum(counts[:-1])))
                for j,count in enumerate(counts):
                    w.writerow([
                        f"PAL{year}",f"{year}-11-15T00:00:00Z",
                        island,str(j+1),int(count)
                    ])


def test_circular_donor_map_is_rotation_within_each_island(tmp_path):
    census=tmp_path/"census.csv"
    _write_fixture(census)
    rows=transition_rows(census)
    rng=np.random.default_rng(42)
    donor,lags=draw_circular_donor_map(rows,rng)
    assert any(v!=0 for v in lags.values())
    for island in ISLANDS:
        years=sorted(
            int(r["start_year"]) for r in rows if r["island"]==island
        )
        donors=[donor[(year,island)] for year in years]
        assert donors==np.roll(np.asarray(years),lags[island]).tolist()
        assert sorted(donors)==years
