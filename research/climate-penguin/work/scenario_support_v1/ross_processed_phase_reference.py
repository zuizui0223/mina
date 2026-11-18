"""Within-trip seasonal contrasts in published Ross Sea processed indices.

Not an independent reconstruction of tracking or transport mechanism.
"""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/ross_phase_reference_v1'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);args=parser.parse_args()
    OUT.mkdir(exist_ok=True);d=pd.read_csv(args.source)
    assert len(d)==5611 and d.birdyear.nunique()==146 and d.bird_fn.nunique()==87
    assert d.groupby('birdyear')[['bird_fn','year.f','colony']].nunique().max().eq(1).all()
    d.to_csv(OUT/'published_processed_table.csv.gz',index=False)
    allpairs=[];summary=[]
    for window,early,late in [('broad',(14,22),(36,43)),('interior',(15,21),(37,42))]:
        groups=[]
        for phase,bounds in [('early',early),('late',late)]:
            a=d[d.yearweek.between(*bounds)]
            q=a.groupby(['birdyear','bird_fn','year.f','colony'],as_index=False).agg(
                support=('support5day','mean'),records=('support5day','count'),sic=('sic5day','mean'))
            groups.append(q.rename(columns={v:f'{phase}_{v}' for v in ['support','records','sic']}))
        pair=groups[0].merge(groups[1],on=['birdyear','bird_fn','year.f','colony'],validate='one_to_one',how='outer')
        pair['window']=window;pair['late_minus_early']=pair.late_support-pair.early_support
        allpairs.append(pair)
        for minimum in [1,3]:
            a=pair[(pair.early_records>=minimum)&(pair.late_records>=minimum)]
            for label,g in [('all',a)]+[(str(k),g) for k,g in a.groupby('colony')]+[(str(k),g) for k,g in a.groupby('year.f')]:
                bybird=g.groupby('bird_fn').late_minus_early.mean()
                summary.append(dict(window=window,minimum_records_per_phase=minimum,group=label,trips=len(g),birds=g.bird_fn.nunique(),
                    mean_early_support=g.early_support.mean(),mean_late_support=g.late_support.mean(),
                    mean_paired_difference=g.late_minus_early.mean(),median_paired_difference=g.late_minus_early.median(),
                    negative_difference_trips=int(g.late_minus_early.lt(0).sum()),
                    bird_equal_mean_difference=bybird.mean(),negative_bird_mean=int(bybird.lt(0).sum())))
    p=pd.concat(allpairs,ignore_index=True);s=pd.DataFrame(summary)
    assert np.allclose(s.mean_late_support-s.mean_early_support,s.mean_paired_difference)
    p.to_csv(OUT/'trip_phase_pairs.csv',index=False);s.to_csv(OUT/'summary.csv',index=False)
    (OUT/'validation.json').write_text(json.dumps(dict(status='published_processed_reference_only',source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),
        source_rows=5611,source_trips=146,source_birds=87,doi='10.5281/zenodo.8374474',
        limits=['Week windows approximate seasons; no exact departure or arrival dates',
                'Support uses observed bird movement; not an independent exposure',
                'Returning recovered tags only; not survival or population-level effect',
                'No significance testing, new mechanism claim or extrapolation outside Ross Sea']),indent=2)+'\n')
    print(s[s.group=='all'].to_string(index=False))


if __name__=='__main__':main()
