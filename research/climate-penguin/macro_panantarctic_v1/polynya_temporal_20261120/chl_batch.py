"""Exact frozen monthly support, economical necessary-condition screening."""
import argparse, calendar, json, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from pyproj import Geod
from chlorophyll import URL, extract, fixed_mask
from run import HERE, digest, member, save, write

def download(region_id,year,month,g,cache):
    geod=Geod(ellps='WGS84');xs=[];ys=[]
    for r in g.itertuples():
        x,y,_=geod.fwd(np.repeat(r.colony_lon,360),np.repeat(r.colony_lat,360),np.arange(360),np.repeat(101000.,360))
        xs.extend(x);ys.extend(y)
    # These actual study-region rectangles do not cross the dateline.
    assert max(xs)-min(xs)<180,'Explicit dateline split required'
    north=max(0,int(np.floor((89.97916666666667-max(ys))*24)));south=min(4319,int(np.ceil((89.97916666666667-min(ys))*24)))
    lo=max(0,int(np.floor((min(xs)+179.97916666666666)*24)));hi=min(8639,int(np.ceil((max(xs)+179.97916666666666)*24)))
    actualyear=year+int(month<3);last=calendar.monthrange(actualyear,month)[1]
    sel=f'[({actualyear}-{month:02d}-01T00:00:00Z):1:({actualyear}-{month:02d}-{last}T00:00:00Z)][{north}:1:{south}][{lo}:1:{hi}]'
    url=URL+'.nc?'+','.join(v+sel for v in ['chlor_a','chlor_a_log10_rmsd'])
    key=hashlib.sha256(url.encode()).hexdigest()[:12]
    path=cache/f'region{region_id}_{year}_{month:02d}_{key}.nc'
    if not path.exists():
        error=None
        for _ in range(2):
            try:
                r=requests.get(url,timeout=(20,150));r.raise_for_status()
                assert r.content[:3] in [b'CDF',b'\x89HD'],r.content[:200]
                path.write_bytes(r.content);error=None;break
            except Exception as exc:error=str(exc)
        if error:raise RuntimeError(error)
    return path,dict(region_id=region_id,source_region=g.source_region.iloc[0],season=int(year),month=int(month),url=url,bytes=path.stat().st_size,sha256=digest(path))

def main(root):
    assert json.loads((HERE/'verdict.json').read_text())['verdict']=='TIME_SPECIFICITY_SUPPORTED'
    cache=root/'work/polynya_temporal_review/chlorophyll_v6';cache.mkdir(exist_ok=True)
    mask=fixed_mask(root)
    support=pd.read_csv(HERE/'support_before_outcome.csv');support=support[support.eligible].copy()
    geo=pd.read_csv(HERE/'geometry.csv')
    support=support.merge(geo[['site_id','colony_lat','colony_lon']],on='site_id',validate='many_to_one')
    # Physical variables only: the chlorophyll support audit never reads isotope Y.
    phys=member(root/'work/polynya_temporal_review/14328755565.zip','matched_860_original_isotope_ocean_ice_site_seasons.csv',usecols=['site_id','season','author_SIC_150km_NovFeb_center_approx_fraction'])
    support=support.merge(phys,on=['site_id','season'],validate='one_to_one')
    regions={r:i for i,r in enumerate(sorted(support.source_region.unique()))}
    write(regions,'chlorophyll_region_requests.json')
    candidates=support.copy();all_daily=[];monthly=[];receipts=[];errors=[];remaining=True
    for month in [11,12,1,2]:
        groups=list(candidates.groupby(['source_region','season']))
        current=[]
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures={pool.submit(download,regions[region],int(year),month,g,cache):(region,year,g) for (region,year),g in groups}
            for j,f in enumerate(as_completed(futures),1):
                region,year,g=futures[f]
                try:
                    path,rec=f.result();receipts.append(rec)
                    for r in g.itertuples():
                        d,_=extract([path],r.site_id,int(year),r.colony_lat,r.colony_lon,mask)
                        d['date']=pd.to_datetime(d.date);actualyear=int(year)+int(month<3)
                        expected=pd.date_range(f'{actualyear}-{month:02d}-01',periods=calendar.monthrange(actualyear,month)[1])
                        assert len(d)==len(expected) and set(d.date)==set(expected)
                        d['month']=month;d['half']=np.where(d.date.dt.day<=15,1,2);all_daily.append(d)
                        v=d[d.passes_daily];ok=len(v)>=5 and v.half.nunique()==2
                        current.append(dict(site_id=r.site_id,season=int(year),month=month,n_days=len(v),halves=v.half.nunique(),passes=ok,chlor_a=v.chlor_a.mean() if ok else np.nan,mean_coverage=d.coverage.mean(),max_coverage=d.coverage.max()))
                except Exception as exc:
                    errors.append(dict(region=region,season=int(year),month=month,error=str(exc)))
                print('OC-CCI month',month,'region-season',j,'/',len(groups),'errors',len(errors),flush=True)
                write(receipts,'chlorophyll_batch_receipts.json');write(errors,'chlorophyll_batch_errors.json')
        monthly.extend(current)
        save(pd.DataFrame(monthly),'chlorophyll_screen_monthly.csv')
        if all_daily:save(pd.concat(all_daily,ignore_index=True),'chlorophyll_screen_daily.csv')
        if errors:
            write(dict(status='INCOMPLETE_DOWNLOAD',errors=errors),'chlorophyll_screen_audit.json');return
        passed=pd.DataFrame(current);passed=passed[passed.passes][['site_id','season']]
        candidates=candidates.merge(passed,on=['site_id','season'],validate='one_to_one')
        counts=dict(rows=len(candidates),sites=candidates.site_id.nunique(),regions=candidates.source_region.nunique(),seasons=candidates.season.nunique())
        print('remaining upper bound after month',month,counts,flush=True)
        if counts['sites']<30 or counts['regions']<6 or counts['seasons']<4:
            remaining=False;break
    m=pd.DataFrame(monthly)
    rows=[]
    for r in support.itertuples():
        g=m[m.site_id.eq(r.site_id)&m.season.eq(r.season)]
        failed=not g.passes.all();complete=len(g)==4
        rows.append(dict(site_id=r.site_id,season=int(r.season),months_retrieved=len(g),failed_months=';'.join(g.loc[~g.passes,'month'].astype(str)),status='INELIGIBLE_MONTHLY_COVERAGE' if failed else ('ELIGIBLE' if complete else 'UNRESOLVED_UPPER_BOUND'),C=float(np.log10(g.chlor_a.mean())) if complete and not failed else np.nan))
    s=support.merge(pd.DataFrame(rows),on=['site_id','season'],validate='one_to_one');save(s,'chlorophyll_screen_support.csv')
    summary=s.groupby(['source_region','season','status']).agg(rows=('site_id','size'),mean_P0=('P0','mean'),mean_SIC=('author_SIC_150km_NovFeb_center_approx_fraction','mean')).reset_index();save(summary,'chlorophyll_selection_comparison.csv')
    audit=dict(status='PASS_CHL_SUPPORT' if remaining else 'NO_GO_CHL_SUPPORT_UPPER_BOUND',candidate_rows=len(support),completed_months=[int(v) for v in m.month.unique()],download_errors=len(errors),confirmed_eligible_rows=int(s.status.eq('ELIGIBLE').sum()),confirmed_ineligible_rows=int(s.status.eq('INELIGIBLE_MONTHLY_COVERAGE').sum()),unresolved_rows=int(s.status.eq('UNRESOLVED_UPPER_BOUND').sum()),upper_bound=counts,passes_support=remaining)
    write(audit,'chlorophyll_screen_audit.json');print(json.dumps(audit,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();main(a.root)
