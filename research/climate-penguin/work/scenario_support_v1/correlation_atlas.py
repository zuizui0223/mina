"""Correlation-first atlas: feature-specific support, not prediction selection."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/correlation_atlas_v1';OUT.mkdir(exist_ok=True)
source=ROOT/'outputs/climate_penguin/behavior_ocean_join.csv';raw=pd.read_csv(source)
features={'Air temperature':'tmean_9','Near sea ice':'near_sic_mean_month9','Surface salinity':'ocean_m9_surface_salinity',
 'Water temperature':'ocean_m9_surface_potential_temperature_c','Eastward ice drift':'drift_m9_east_km_day',
 'Northward ice drift':'drift_m9_north_km_day','Ice-edge distance':'edge_distance_km'}
species_order=['Adelie','Chinstrap','Gentoo'];rows=[];points=[];rng=np.random.default_rng(20261030)
for feature,column in features.items():
    r=raw.copy()
    if 'drift' in feature:r=r[r.drift_m9_screen_pass.eq(True)]
    r=r.replace([np.inf,-np.inf],np.nan).dropna(subset=[column,'settlement'])
    for species,g in r.groupby('species'):
        a=g.groupby(['cam','season_start_year'],as_index=False).agg(x=(column,'mean'),y=('settlement','mean'),source_rows=('source_row_1based',lambda s:'|'.join(map(str,sorted(s)))))
        a['feature']=feature;a['species']=species
        a[['within_x','within_y']]=a[['x','y']]-a.groupby('cam')[['x','y']].transform('mean')
        between=a.groupby('cam')[['x','y']].mean()
        z=np.column_stack([np.ones(len(a)),pd.get_dummies(a.cam,drop_first=True,dtype=float),pd.get_dummies(a.season_start_year,drop_first=True,dtype=float)])
        residual=a[['x','y']].to_numpy()-z@np.linalg.lstsq(z,a[['x','y']],rcond=None)[0]
        codes,inv=np.unique(a.cam,return_inverse=True);draws=[]
        xx=a.within_x.to_numpy();yy=a.within_y.to_numpy()
        for _ in range(999):
            weights=np.bincount(rng.integers(len(codes),size=len(codes)),minlength=len(codes))[inv]
            denominator=np.sqrt(np.sum(weights*xx**2)*np.sum(weights*yy**2))
            if denominator>1e-12:draws.append(np.sum(weights*xx*yy)/denominator)
        lo,hi=np.quantile(draws,[.025,.975])
        repeat=a.groupby('cam').size()
        rows.append(dict(feature=feature,species=species,n=len(a),sites=len(codes),years=a.season_start_year.nunique(),
            first_year=int(a.season_start_year.min()),last_year=int(a.season_start_year.max()),
            repeated_sites=int((repeat>=2).sum()),between_r=between.x.corr(between.y),within_r=a.within_x.corr(a.within_y),
            site_year_r=np.corrcoef(residual.T)[0,1],within_site_resample_low=lo,within_site_resample_high=hi,valid_resamples=len(draws)))
        points.append(a)
table=pd.DataFrame(rows);points=pd.concat(points,ignore_index=True)
assert len(table)==21
table.to_csv(OUT/'correlations.csv',index=False);points.to_csv(OUT/'observation_points.csv',index=False)
colors={'between_r':'#a06a29','within_r':'#187b8c','site_year_r':'#7655a3'}
fig,axes=plt.subplots(1,3,figsize=(17,8),layout='constrained')
for ax,species in zip(axes,species_order):
    a=table[table.species.eq(species)].set_index('feature').loc[list(features)]
    positions=np.arange(len(a))
    for col,shift,label in [('between_r',-.2,'Between sites'),('within_r',0,'Within site'),('site_year_r',.2,'Site + year adjusted')]:
        ax.scatter(a[col],positions+shift,color=colors[col],s=35,label=label,zorder=3)
    ax.hlines(positions,a.within_site_resample_low,a.within_site_resample_high,color=colors['within_r'],lw=1.5,alpha=.7)
    ax.axvline(0,color='#999',lw=.8);ax.set_xlim(-1,1);ax.invert_yaxis()
    ax.set_yticks(positions,[f'{f}\nn={int(a.loc[f,"n"])}, sites={int(a.loc[f,"sites"])}' for f in a.index],fontsize=8)
    ax.set_title(species,fontsize=15);ax.set_xlabel('Correlation r');ax.grid(axis='x',alpha=.15)
    ax.spines[['top','right']].set_visible(False)
axes[1].legend(loc='lower center',bbox_to_anchor=(.5,-.2),ncol=3,fontsize=9)
fig.suptitle('September environment and settlement index\nEach feature uses its available observations; lines show site-resampling ranges for within-site r',fontsize=14)
fig.savefig(OUT/'correlation_overview.png',dpi=160);plt.close(fig)
fig,axes=plt.subplots(3,3,figsize=(12,10),layout='constrained')
for i,feature in enumerate(list(features)[:3]):
    for j,species in enumerate(species_order):
        a=points[(points.feature==feature)&(points.species==species)];ax=axes[i,j]
        ax.scatter(a.within_x,a.within_y,s=20,alpha=.65,color=colors['within_r'])
        x=a.within_x.to_numpy();y=a.within_y.to_numpy();slope=x@y/(x@x)
        grid=np.array([x.min(),x.max()]);ax.plot(grid,slope*grid,color='#244b57',lw=1)
        ax.axhline(0,lw=.5,color='#aaa');ax.axvline(0,lw=.5,color='#aaa')
        r=table[(table.feature==feature)&(table.species==species)].iloc[0]
        ax.set_title(f'{species}: r={r.within_r:+.2f}, n={len(a)}')
        ax.set_xlabel(feature+' anomaly');ax.set_ylabel('Settlement index anomaly');ax.spines[['top','right']].set_visible(False)
fig.suptitle('Within-site annual variation (not a causal effect)\nTemperature: C; sea ice: percentage points; salinity: source 0.001 scale',fontsize=13)
fig.savefig(OUT/'within_site_scatter.png',dpi=160);plt.close(fig)
receipt={'status':'correlation_first_exploratory_summary','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'associations':len(table),'bootstrap_repeats':999,'seed':20261030,
 'limitations':['Feature-specific cohorts differ; differences between coefficients are not formal tests',
 'Site-resampling ranges do not include full cross-site year dependence and are not multiple-testing significance labels',
 'Common-year adjustment can absorb shared climate signals; report all three summaries',
 'Index origin unresolved; calendar years follow source season labels',
 'No predictor ranking by forecast-error improvement, no significant-only selection']}
(OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(table[['species','feature','n','sites','between_r','within_r','site_year_r']].to_string(index=False))
