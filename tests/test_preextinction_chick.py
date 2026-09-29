import csv
import numpy as np
from mina.preextinction_chick import load_chicks, simulate_null

def test_chick_duplicate_cleaning(tmp_path):
    p=tmp_path/"c.csv"
    rows=[
      {"studyName":"A","Date GMT":"2002-01-10","Time GMT":"1000","Island":"CHR","Colony":"1","Adults":"0","Chicks":"5"},
      {"studyName":"A","Date GMT":"2002-01-10","Time GMT":"1000","Island":"CHR","Colony":"1","Adults":"10","Chicks":"5"},
      {"studyName":"B","Date GMT":"2002-01-10","Time GMT":"1000","Island":"CHR","Colony":"2","Adults":"10","Chicks":"3"},
      {"studyName":"C","Date GMT":"2002-01-11","Time GMT":"1000","Island":"CHR","Colony":"2","Adults":"11","Chicks":"4"}
    ]
    with p.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    x,info=load_chicks(p)
    assert x[("CHR","1",2001)]==5
    assert ("CHR","2",2001) not in x
    assert info["identical_duplicate_keys_collapsed"]==1
    assert info["ambiguous_duplicate_keys_excluded"]==1

def test_multinomial_reference():
    e=np.array([1,0,0])
    prior=np.array([10.,10.,10.]); probs=prior/prior.sum()
    y=np.array([0.,15.,15.]); mu=30*probs
    r=(y-mu)/np.sqrt(mu)
    c=float(r[e==1].mean()-r[e==0].mean())
    risk={"island":"CHR","season":2001,"event":e,"prior":prior,"chicks":y,
          "total_chicks":30,"probs":probs,"expected":mu,
          "pearson_residual":r,"observed_contrast":c}
    out=simulate_null([risk],simulations=9999,seed=7,batch_size=500)
    assert out["observed_contrast"]<0
    assert out["one_sided_lower_p"]<=0.05
