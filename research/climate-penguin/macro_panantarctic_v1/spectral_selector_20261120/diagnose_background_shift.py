"""Same-coordinate class-stable candidate backgrounds; observational contrast only."""
import gzip
import json
from pathlib import Path
import numpy as np
import pandas as pd
from diagnose_fixed_failure import block_mean_intervals

ROOT=Path(__file__).parent

def main():
    f=json.loads((ROOT/'matched_center_frozen_model.json').read_text());bands=f['bands'];slope=np.array(f['coef'])/f['scale']
    tr=pd.read_csv(ROOT/'matched_training_samples.csv');tr=tr[tr.label.eq(0)].copy();tr['period']='train'
    te=pd.read_csv(ROOT/'matched_holdout_scores.csv.gz');te=te[te.label.eq(0)].copy();te['period']='test'
    all_bg=pd.concat([tr,te],ignore_index=True);keys=['site_id','easting','northing']
    stable=all_bg.groupby(keys).background_class.nunique().eq(1)
    eligible=stable[stable].reset_index()[keys]
    all_bg=all_bg.merge(eligible,on=keys,validate='many_to_one')
    grouping=keys+['background_class']
    a=all_bg[all_bg.period.eq('train')].groupby(grouping)[bands].mean()
    b=all_bg[all_bg.period.eq('test')].groupby(grouping)[bands].mean()
    pair=a.join(b,how='inner',lsuffix='_train',rsuffix='_test').reset_index()
    pos=pd.read_csv(ROOT/'failure_coordinate_pairs.csv.gz')
    names=[band+'_change' for band in bands]
    for band in bands:
        pos[band+'_change']=pos[band+'_test']-pos[band+'_train']
        pair[band+'_change']=pair[band+'_test']-pair[band+'_train']
    positive=pos.groupby(['site_id','region','block'])[names].mean().reset_index()
    positive['positive_logit_change']=positive[names].to_numpy()@slope
    summary=[];site_tables=[];support=[]
    for category in ['other','snow','water']:
        p=pair[pair.background_class.eq(category)]
        background=p.groupby('site_id')[names].mean().reset_index()
        bg_counts=p.groupby('site_id').size().rename('paired_background_coordinates')
        both=positive.merge(background,on='site_id',suffixes=('_positive','_background'),validate='one_to_one').merge(bg_counts,on='site_id')
        support.append(dict(background_class=category,common_sites=len(both),regions=both.region.nunique(),blocks=both.block.nunique(),
          common_background_coordinates=int(both.paired_background_coordinates.sum()),
          common_positive_coordinates=int(pos.site_id.isin(both.site_id).sum())))
        if both.empty:continue
        differences=[]
        for band in bands:
            name=band+'_difference_of_changes'
            both[name]=both[band+'_change_positive']-both[band+'_change_background'];differences.append(name)
        both['background_logit_change']=both[[n+'_background' for n in names]].to_numpy()@slope
        both['logit_difference_of_changes']=both.positive_logit_change-both.background_logit_change
        if not np.allclose(both[differences].to_numpy()@slope,both.logit_difference_of_changes):raise ValueError('Contrast decomposition mismatch')
        cols=[n+'_positive' for n in names]+[n+'_background' for n in names]+differences+['positive_logit_change','background_logit_change','logit_difference_of_changes']
        result=block_mean_intervals(both,cols);result['background_class']=category;summary.append(result)
        both['background_class']=category;site_tables.append(both)
    pd.DataFrame(support).to_csv(ROOT/'failure_background_support.csv',index=False,lineterminator='\n')
    if summary:pd.concat(summary).to_csv(ROOT/'failure_background_contrasts.csv',index=False,lineterminator='\n')
    if site_tables:pd.concat(site_tables).to_csv(ROOT/'failure_background_site_contrasts.csv',index=False,lineterminator='\n')
    (ROOT/'failure_background_coordinate_pairs.csv.gz').write_bytes(gzip.compress(pair.to_csv(index=False,lineterminator='\n').encode(),mtime=0))
    print(pd.DataFrame(support).to_string(index=False))
    if summary:
        s=pd.concat(summary);print(s[s.variable.isin(['swir16_change_positive','swir16_change_background','swir16_difference_of_changes','positive_logit_change','background_logit_change','logit_difference_of_changes'])].to_string(index=False))

if __name__=='__main__':main()
