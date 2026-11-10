"""Source-backed residual scatter panels; rows are different estimands."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[2]/'outputs';out=root/'evidence_figure_v1';out.mkdir(exist_ok=True)
paths=[root/'relationship_response_v1/cohort.csv',root/'vegetation_response_v1/site_species_cohort.csv',root/'ross_movement_pairs_v1/joined_exposure_movement.csv.gz']
salt=pd.read_csv(paths[0]);veg=pd.read_csv(paths[1]);flow=pd.read_csv(paths[2])
salt=salt[salt.scope=='all_source_labels']
flow=flow[(flow.product_class=='satellite')&(flow.support_fraction>=.5)&(flow.nominal_overlap_fraction>=.5)&(flow.month==9)&(flow.target!='CRZW')]
fig,axes=plt.subplots(3,3,figsize=(13,12));fig.subplots_adjust(left=.10,right=.98,bottom=.14,top=.88,hspace=.75,wspace=.30)
plt.rcParams.update({'font.size':10})
colors=['#2563a6','#bb7022','#26805d'];points=[];checks=[]
def plot(ax,data,x,y,z,panel,title,color,expected,ids):
    values=np.column_stack([x,y]);r=values-z@np.linalg.lstsq(z,values,rcond=None)[0]
    coefficient=np.corrcoef(r.T)[0,1]
    assert np.isclose(coefficient,expected,atol=1e-8)
    ax.scatter(r[:,0],r[:,1],s=19 if len(data)<100 else 10,alpha=.7 if len(data)<100 else .35,c=color,linewidths=0)
    ax.axhline(0,color='#aaa',lw=.6);ax.axvline(0,color='#aaa',lw=.6)
    beta=r[:,0]@r[:,1]/(r[:,0]@r[:,0]);xx=np.array([r[:,0].min(),r[:,0].max()]);ax.plot(xx,beta*xx,color=color,lw=1.5)
    ax.set_title(f'{panel}  {title}\nn = {len(data)}; r = {coefficient:+.3f}',loc='left',fontsize=10)
    ax.spines[['top','right']].set_visible(False)
    for identity,(vx,vy) in zip(ids,r):points.append(dict(panel=panel,identity=str(identity),x=float(vx),y=float(vy)))
    checks.append(dict(panel=panel,n=len(data),r=coefficient,slope=beta))
for j,(species,expected) in enumerate(zip(['Adelie','Chinstrap','Gentoo'],[.212534,.006837,-.158760])):
    a=salt[salt.species==species];z=np.column_stack([pd.get_dummies(a.cam,dtype=float),pd.get_dummies(a.year,drop_first=True,dtype=float),a[['airC','ice10','waterC']]])
    frozen=pd.read_csv(root/'salinity_sensitivity_v1/specifications.csv')
    er=frozen[(frozen.scope=='all_source_labels')&(frozen.species==species)&(frozen['mode']=='site_year')&(frozen.controls=='ice_water_air')].partial_r.item()
    plot(axes[0,j],a,a.salt01,a.y,z,'ABC'[j],species,colors[j],er,a.cam+' / '+a.year.astype(str))
    axes[0,j].set_xlabel('Residual salinity (0.1 product units)')
    a=veg[(veg.species_id==['ADPE','CHPE','GEPE'][j])&veg.positive_mapped_detection&veg.observed_log_count_slope_per_year.notna()]
    z=pd.get_dummies(a.region,dtype=float).to_numpy()
    er=[-.08281102727072627,-.10739369094424324,.18765007224023697][j]
    plot(axes[1,j],a,a.log1p_mapped_area_m2,a.observed_log_count_slope_per_year,z,'DEF'[j],species,colors[j],er,a.site_id)
    axes[1,j].set_xlabel('Residual log(1 + mapped area [m²])')
for j,(mode,label,er) in enumerate([('pooled','Unadjusted',-.002569339452039617),('trip','Individual-year adjusted',-.06143348161455372),('trip_date','Individual-year + date adjusted',-.013487677204149985)]):
    z=np.ones((len(flow),1)) if mode=='pooled' else pd.get_dummies(flow.trip,dtype=float).to_numpy()
    if mode=='trip_date':z=np.column_stack([z,pd.get_dummies(flow.date,drop_first=True,dtype=float)])
    plot(axes[2,j],flow,flow.projected_km_day,flow.mean_radial_km_day,z,'GHI'[j],label,'#6b50a1',er,flow.trip+' / '+flow.time1)
    axes[2,j].set_xlabel('Centered / residual toward-colony ice flow (km/day)',fontsize=9)
for row in range(3):
    xlim=(min(ax.get_xlim()[0] for ax in axes[row]),max(ax.get_xlim()[1] for ax in axes[row]))
    ylim=(min(ax.get_ylim()[0] for ax in axes[row]),max(ax.get_ylim()[1] for ax in axes[row]))
    for ax in axes[row]:ax.set_xlim(xlim);ax.set_ylim(ylim)
axes[0,0].set_ylabel('Residual settlement index (day scale)')
axes[1,0].set_ylabel('Residual log-count slope (per year)')
axes[2,0].set_ylabel('Centered / residual model movement\ntoward colony (km/day)')
fig.suptitle('Penguin environmental associations: observations, adjustments and limits',fontsize=15,y=.975)
fig.text(.10,.925,'A–C  Salinity: site-year observations; site, year, air, ice and water-temperature adjusted.',fontsize=10)
fig.text(.10,.650,'D–F  Vegetation: sites with mapped vegetation; region adjusted; static 2017–2023 map.',fontsize=10)
fig.text(.10,.365,'G–I  Ross tracking: same 515 intervals / 169 individual-years; September, satellite-supported.',fontsize=10)
fig.text(.10,.035,'Lines are descriptive fits, not confidence bands. Points are not independent biological replicates.\nDifferent rows measure different relationships. GLS movement is model-derived; static vegetation is not annual greening.\nSources and all plotted point identities: evidence_figure_v1. Ice data: Copyright EUMETSAT (OSI-455).',fontsize=9)
fig.savefig(out/'environment_associations.png',dpi=180,facecolor='white')
pd.DataFrame(points).to_csv(out/'plotted_points.csv',index=False)
pd.DataFrame(checks).to_csv(out/'panel_checks.csv',index=False)
(out/'validation.json').write_text(json.dumps(dict(passed=True,panels=9,point_rows=len(points),
    inputs={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    scope='All panel correlations reproduced from source rows; visual inspection separately required'),indent=2)+'\n')
print(pd.DataFrame(checks).to_string(index=False))
