import csv
from mina.preextinction_chick_repair import load_coherent_chick_candidates

def test_cleaner(tmp_path):
    p=tmp_path/'x.csv'
    fields=['studyName','Date GMT','Time GMT','Island','Colony','Adults','Chicks']
    rows=[['A','2002-01-10','1000','CHR','1','0','5'],['A','2002-01-10','1000','CHR','1','10','5']]
    with p.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(fields);w.writerows(rows)
    x,a=load_coherent_chick_candidates(p)
    assert x[('CHR','1',2001)]['chick_adults']==10
    assert a['identical_duplicates_resolved']==1
