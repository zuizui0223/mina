from pathlib import Path
import importlib.util
import numpy as np
import pytest
P=Path(__file__).resolve().parents[1]/'research/climate-penguin/work/abandonment/litchfield_map_alignment.py'
def load():
    assert P.exists(), 'map alignment implementation missing'
    s=importlib.util.spec_from_file_location('map_align',P)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def test_affine_recovers_known_metric_coordinates():
    m=load(); p=np.array([[0,0],[3,0],[0,4],[3,4]],float)
    truth=np.array([[2,0],[0,-2],[10,20]],float)
    q=np.column_stack([p,np.ones(4)])@truth
    a,r=m.fit_affine(p,q)
    assert np.allclose(a,truth) and max(r)<1e-10

def test_affine_rejects_collinear_control_points():
    m=load()
    with pytest.raises(ValueError):m.fit_affine([[0,0],[1,1],[2,2]],[[0,0],[2,2],[4,4]])

def test_open_hatch_not_polygon_and_chain_preserved():
    m=load()
    edges=[('l',(0,0),(1,0)),('l',(1,0),(1,1)),('l',(1,1),(0,0))]
    assert len(m.closed_outline(edges))==4
    with pytest.raises(ValueError):m.closed_outline(edges[:-1])
    with pytest.raises(ValueError):m.closed_outline([edges[0],('l',(2,0),(1,1)),edges[2]])

def test_source_hash_is_binding(tmp_path):
    m=load(); f=tmp_path/'wrong.pdf';f.write_bytes(b'%PDF-1.4 wrong')
    with pytest.raises(ValueError):m.verify_source(f)

def test_map_outlines_not_census_units():
    m=load()
    assert len(m.OUTLINE_IDS)==10
    assert m.GEOMETRY_STATUS=='map_derived_historical_candidate_not_survey_verified'
