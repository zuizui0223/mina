import csv
import math
from pathlib import Path

import numpy as np

from mina.colony_network import transition_rows
from mina.neff_circular_shift import (
    _shifted_values,
    independent_shift_matrix,
    island_sequences,
    joint_shift_matrix,
)
from mina.neff_permutation import _fast_permutation_statistics


ISLANDS=("CHR","COR","HUM","LIT","TOR")


def _write_fixture(path: Path):
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow([
            "study_name","time","island_name","colony_code","num_breeding_pairs"
        ])
        w.writerow(["","UTC","","","1"])
        for year in range(2000,2008):
            for i,island in enumerate(ISLANDS):
                if island=="LIT" and year>2005:
                    total=0
                else:
                    total=1000-45*(year-2000)+80*i
                shares=np.asarray([0.5,0.3,0.2],dtype=float)
                # Vary topology smoothly through time without changing the row count.
                tilt=0.025*math.sin((year-2000+i)/2)
                shares=shares+np.asarray([tilt,-tilt/2,-tilt/2])
                counts=np.rint(total*shares).astype(int)
                counts[-1]=max(0,total-int(np.sum(counts[:-1])))
                for j,count in enumerate(counts):
                    w.writerow([
                        f"PAL{year}",
                        f"{year}-11-15T00:00:00Z",
                        island,
                        str(j+1),
                        int(count),
                    ])


def test_shifted_values_preserve_cyclic_structure():
    values=np.asarray([1.0,2.0,4.0,8.0])
    shifts=np.asarray([0,1,2,3])
    out=_shifted_values(values,shifts)
    for j,lag in enumerate(shifts):
        expected=np.roll(values,int(lag))
        assert np.allclose(out[:,j],expected)
        assert np.allclose(
            np.abs(np.fft.rfft(out[:,j])),
            np.abs(np.fft.rfft(values)),
        )


def test_independent_shift_preserves_each_island_multiset(tmp_path):
    census=tmp_path/"census.csv"
    _write_fixture(census)
    rows=transition_rows(census)
    seq=island_sequences(rows)
    matrix,diag=independent_shift_matrix(rows,simulations=200,seed=7)
    assert matrix.shape==(len(rows),200)
    assert diag["global_identity_draws_rejected"]>=0
    for island in seq:
        idx=seq[island]["indices"]
        original=np.sort(seq[island]["values"])
        for j in (0,17,199):
            assert np.allclose(np.sort(matrix[idx,j]),original)


def test_joint_shift_identity_reproduces_statistics(tmp_path):
    # Use a purpose-built 27-year fixture so four islands have 26 transitions
    # and LIT has 16 positive-current transitions, matching the real design.
    census=tmp_path/"census.csv"
    with census.open("w",newline="",encoding="utf-8") as h:
        w=csv.writer(h)
        w.writerow([
            "study_name","time","island_name","colony_code","num_breeding_pairs"
        ])
        w.writerow(["","UTC","","","1"])
        for year in range(1991,2018):
            for i,island in enumerate(ISLANDS):
                active = not (island=="LIT" and year>=2007)
                total=(1600+120*i)-35*(year-1991) if active else 0
                fractions=np.asarray([0.55,0.30,0.15])
                tilt=0.03*math.sin((year-1991+i)/3)
                fractions=fractions+np.asarray([tilt,-tilt/2,-tilt/2])
                counts=np.rint(total*fractions).astype(int) if active else np.zeros(3,dtype=int)
                if active:
                    counts[-1]=max(0,total-int(np.sum(counts[:-1])))
                for j,count in enumerate(counts):
                    w.writerow([
                        f"PAL{year}",
                        f"{year}-11-15T00:00:00Z",
                        island,
                        str(j+1),
                        int(count),
                    ])
    rows=transition_rows(census)
    matrix,combos=joint_shift_matrix(rows)
    identity=next(
        i for i,c in enumerate(combos)
        if c["persistent_lag"]==0 and c["lit_lag"]==0
    )
    gains,betas=_fast_permutation_statistics(rows,matrix)
    direct_matrix=np.asarray([
        [math.log1p(float(r["effective_colony_number"]))] for r in rows
    ])
    direct_gain,direct_beta=_fast_permutation_statistics(rows,direct_matrix)
    assert abs(gains[identity]-direct_gain[0])<1e-12
    assert abs(betas[identity]-direct_beta[0])<1e-12


def test_exact_identity_tail_must_count_identity():
    observed=0.11679896749684507
    # Identity can differ by floating-point roundoff after the FWL
    # re-expression, but it is still the observed transformation.
    beta=np.asarray([observed-5e-14,0.02,-0.01])
    tol=1e-10
    exceed=int(np.sum(beta>=observed-tol))
    assert exceed>=1
    assert exceed/len(beta)>0
