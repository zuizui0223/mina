"""Independent checks of source parsing, HC3 arithmetic and chronological holdout."""
from pathlib import Path
import argparse,json,re
import numpy as np
import pandas as pd
from scipy.stats import t

def run(out):
    d=pd.read_csv(out/'signy_17_seasons.csv')
    # Separate lxml table reader: the legacy page's malformed table is represented
    # as column multi-level tuples, each level being one original annual row.
    table=pd.read_html(out/'source/Orcadas.All.temperature.html')[0]
    alternate={int(y):float(re.match(r'-?\d+\.\d+',str(v))[0])
               for y,v in zip(table.columns[0],table.columns[10]) if re.match(r'-?\d+\.\d+',str(v))}
    assert all(alternate[int(row.year)]==row.temp_oct for row in d.itertuples())
    x=np.column_stack([np.ones(len(d)),d.temp_oct,d.ice10]);y=d.gap.to_numpy()
    inv=np.linalg.inv(x.T@x);b=inv@x.T@y;res=y-x@b
    h=np.sum((x@inv)*x,axis=1)
    cov=inv@(x.T@np.diag((res/(1-h))**2)@x)@inv
    se=np.sqrt(np.diag(cov));lo=b-t.ppf(.975,len(d)-3)*se
    hi=b+t.ppf(.975,len(d)-3)*se
    r=pd.read_csv(out/'model_coefficients.csv')
    r=r[(r.response=='gap')&(r.model=='joint_primary')].set_index('term').loc[['temp_oct','ice10']]
    assert np.allclose(r.estimate,b[1:]) and np.allclose(r.ci_low,lo[1:]) and np.allclose(r.ci_high,hi[1:])
    pred=pd.read_csv(out/'forward_predictions.csv')
    for row in pred.itertuples():
        train=d[d.year<row.year]
        assert len(train)==row.n_train and row.year>=2006
        if row.model=='historical_mean':assert np.isclose(train[row.response].mean(),row.predicted)
    pairs=pd.read_csv(out/'noaa_same_site_year_pairs.csv')
    assert pairs.site.nunique()==4 and pairs.year.nunique()==1
    report={'independent_temperature_values_checked':len(d),'independent_HC3_terms_checked':2,
            'forward_rows_checked':len(pred),'noaa_distinct_paired_sites':4,
            'status':'pass','scope':'source temperature parser, matrix HC3, no future training rows, paired support; not global CI'}
    (out/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps(report))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);run(p.parse_args().out)
