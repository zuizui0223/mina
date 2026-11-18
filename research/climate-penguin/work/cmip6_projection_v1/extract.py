"""CMIP6 conditional environmental projections at fixed penguin study coordinates.

Selection is fixed before values are read. This is neither a species forecast nor
observational detection/attribution. Remote zarr reads are spatially indexed and
limited to the requested seasonal months; only two mask frames are read in full.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import traceback
import warnings

import cftime
import dask
import fsspec
import numpy as np
import pandas as pd
from pyproj import Geod
import requests
import xarray as xr

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
OUT = ROOT / 'outputs/cmip6_projection_v1'
CATALOG_URL = 'https://storage.googleapis.com/cmip6/cmip6-zarr-consolidated-stores.csv'
EXPERIMENTS = ('historical', 'ssp245', 'ssp585')
TABLES = {'tas': 'Amon', 'sos': 'Omon', 'siconc': 'SImon'}
MONTHS = (8, 9, 10, 11)
PERIODS = {'historical': [(1995, 2014)], 'ssp245': [(2041, 2060), (2081, 2100)], 'ssp585': [(2041, 2060), (2081, 2100)]}


def seasonal_means(values, times, start, end, months=MONTHS):
    """Return annual day-weighted means, rejecting absent/duplicate months.

    A nonfinite observation makes that cell-year missing. No partial-month or
    partial-year imputation is performed. Calendars are retained as CFTime.
    """
    values = np.asarray(values, dtype=float)
    times = list(times)
    if values.shape[0] != len(times):
        raise ValueError('time/value lengths differ')
    years = np.arange(start, end + 1)
    output = []
    for year in years:
        index = [i for i, t in enumerate(times) if t.year == year and t.month in months]
        if sorted(times[i].month for i in index) != sorted(months):
            raise ValueError(f'incomplete or duplicate season {year}')
        weights = np.array([times[i].daysinmonth for i in index], dtype=float)
        output.append(np.sum(values[index] * weights.reshape((-1,) + (1,) * (values.ndim - 1)), axis=0) / weights.sum())
    return years, np.asarray(output)


def normalize_values(values, variable, units):
    values = np.asarray(values, dtype=float)
    normalized_units = str(units).strip()
    if variable == 'tas':
        if normalized_units in ('K', 'kelvin'):
            return values - 273.15, 'degC'
        if normalized_units in ('degC', 'degree_Celsius', 'degrees_Celsius'):
            return values, 'degC'
        raise ValueError(f'unrecognized tas units {units!r}')
    if variable == 'sos':
        if normalized_units not in ('0.001', 'psu', '1e-3', '1.e-3', 'g kg-1', 'g/kg'):
            raise ValueError(f'unrecognized sos units {units!r}')
        valid = values[np.isfinite(values)]
        if valid.size and (valid.min() < 0 or valid.max() > 50):
            raise ValueError('sos outside physical range')
        return values, '0.001'
    if variable == 'siconc':
        if normalized_units in ('1', 'fraction'):
            values = values * 100
        elif normalized_units not in ('%', 'percent', 'percentage'):
            raise ValueError(f'unrecognized siconc units {units!r}')
        valid = values[np.isfinite(values)]
        if valid.size and (valid.min() < -0.001 or valid.max() > 100.001):
            raise ValueError('siconc outside 0..100 percent range')
        return values, 'percent'
    raise ValueError(variable)


def nearest_cells(lat, lon, valid, sites):
    """Geodesic closest valid model cell, including dateline wrap."""
    lat, lon = np.asarray(lat), np.asarray(lon)
    yy, xx = np.where(np.asarray(valid) & np.isfinite(lat) & np.isfinite(lon))
    if len(yy) == 0:
        raise ValueError('no valid cells')
    geod = Geod(ellps='WGS84')
    rows = []
    for site in sites.to_dict('records'):
        distances = geod.inv(np.full(len(xx), site['longitude']), np.full(len(xx), site['latitude']), lon[yy, xx], lat[yy, xx])[2] / 1000
        k = int(np.argmin(distances))
        rows.append(dict(site, grid_y=int(yy[k]), grid_x=int(xx[k]), grid_lat=float(lat[yy[k], xx[k]]),
                         grid_lon=float(lon[yy[k], xx[k]]), distance_km=float(distances[k])))
    return rows


def select_stores(catalog, n_models=3):
    """ASCII source order, natural member order, gn before other shared grids."""
    d = catalog[catalog.experiment_id.isin(EXPERIMENTS)].copy()
    d = d[d.apply(lambda r: TABLES.get(r.variable_id) == r.table_id, axis=1)]
    available = []
    for (source, member), group in d.groupby(['source_id', 'member_id']):
        chosen = []
        for variable in TABLES:
            v = group[group.variable_id == variable]
            grids = [grid for grid, g in v.groupby('grid_label') if set(g.experiment_id) == set(EXPERIMENTS)]
            if not grids:
                break
            grid = sorted(grids, key=lambda x: (x != 'gn', x))[0]
            chosen.append(v[v.grid_label == grid].sort_values(['version', 'zstore']).drop_duplicates('experiment_id', keep='last'))
        if len(chosen) == len(TABLES):
            available.append((source, tuple(int(n) for n in re.findall(r'\d+', member)), pd.concat(chosen)))
    selected, sources = [], set()
    for source, _, frame in sorted(available, key=lambda x: (x[0], x[1])):
        if source not in sources and len(sources) < n_models:
            selected.append(frame)
            sources.add(source)
    if not selected:
        raise ValueError('no complete model/member combination')
    return pd.concat(selected).sort_values(['source_id', 'variable_id', 'experiment_id']).reset_index(drop=True)


def open_store(row):
    url = row.zstore.replace('gs://', 'https://storage.googleapis.com/')
    mapper = fsspec.get_mapper(url, client_kwargs={'trust_env': True})
    return xr.open_zarr(mapper, consolidated=True, decode_times=xr.coders.CFDatetimeCoder(use_cftime=True)), url


def coordinates(dataset, variable):
    da = dataset[variable]
    spatial = tuple(d for d in da.dims if d != 'time')
    if len(spatial) != 2:
        raise ValueError(f'expected two spatial dimensions, got {da.dims}')
    latitude = next((n for n in ('latitude', 'lat', 'nav_lat') if n in dataset), None)
    longitude = next((n for n in ('longitude', 'lon', 'nav_lon') if n in dataset), None)
    if latitude is None or longitude is None:
        raise ValueError('unrecognized coordinate names')
    lat, lon = xr.broadcast(dataset[latitude], dataset[longitude])
    lat = lat.transpose(*spatial).values
    lon = lon.transpose(*spatial).values
    return lat, (lon + 180) % 360 - 180, spatial


def read_cached_artifact(path, expected_identity):
    """Reuse an artifact only with an exactly matching provenance sidecar."""
    path = Path(path)
    sidecar = path.with_suffix('.json')
    if not path.exists() or not sidecar.exists():
        return None
    metadata = json.loads(sidecar.read_text())
    if metadata.get('cache_identity') != expected_identity:
        raise ValueError(f'cache identity mismatch: {path.name}')
    if path.suffix == '.npz':
        with np.load(path) as cached:
            values = cached['values'].copy()
    elif path.suffix == '.csv':
        values = pd.read_csv(path)
    else:
        raise ValueError(f'unsupported cache extension: {path.suffix}')
    return values, metadata


def cache_identity(row, lat, lon, dataset, sites):
    """Fingerprint all inputs that determine grid support and monthly values."""
    grid = hashlib.sha256()
    grid.update(json.dumps(list(lat.shape)).encode())
    grid.update(np.asarray(lat, dtype='<f8').tobytes())
    grid.update(np.asarray(lon, dtype='<f8').tobytes())
    return dict(
        zstore=row.zstore, variable_id=row.variable_id, experiment_id=row.experiment_id,
        member_id=row.member_id, grid_label=row.grid_label,
        grid_sha256=grid.hexdigest(),
        sites_sha256=hashlib.sha256(sites.to_csv(index=False).encode()).hexdigest(),
        site_file_sha256=hashlib.sha256((ROOT/'outputs/climate_penguin/daily_ice_locations.csv').read_bytes()).hexdigest(),
        periods=[list(x) for x in PERIODS[row.experiment_id]], months=list(MONTHS),
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        time_sha256=hashlib.sha256('|'.join(str(t) for t in dataset.time.values).encode()).hexdigest(),
        metadata_sha256=hashlib.sha256(json.dumps(dict(
            units=dataset[row.variable_id].attrs.get('units'),
            calendar=dataset.time.encoding.get('calendar'),
            tracking_id=dataset.attrs.get('tracking_id'),
            parent_variant_label=dataset.attrs.get('parent_variant_label'),
            spatial_dimensions=list(dataset[row.variable_id].dims)),sort_keys=True,default=str).encode()).hexdigest(),
        mask_policy='historical_1995_Aug_Nov_finite_ocean_or_all_surface_atmosphere_v1')


def bind_support_identity(identity, grid_rows, historical_identity):
    """Future values also depend on the historical mask and selected cell order."""
    support = grid_rows[['location_id','grid_y','grid_x']].astype(
        {'location_id':str,'grid_y':'int64','grid_x':'int64'})
    return dict(identity,
        support_sha256=hashlib.sha256(support.to_csv(index=False).encode()).hexdigest(),
        historical_identity_sha256=hashlib.sha256(
            json.dumps(historical_identity,sort_keys=True).encode()).hexdigest())


def read_variable(source, variable, selected, sites):
    """One model variable, with historical grid reused for both scenarios."""
    stores = selected[(selected.source_id == source) & (selected.variable_id == variable)]
    hist = stores[stores.experiment_id == 'historical'].iloc[0]
    cache = WORK / 'cache'
    cache.mkdir(exist_ok=True)
    prefix = f'{source}_{hist.member_id}_{variable}'
    support_path = OUT / f'support_{prefix}.csv'
    records, metadata = [], []
    hist_lat = hist_lon = None
    grid_rows = None
    historical_identity = None
    for experiment in EXPERIMENTS:
        row = stores[stores.experiment_id == experiment].iloc[0]
        print(f'OPEN {source} {variable} {experiment}', flush=True)
        dataset, url = open_store(row)
        lat, lon, dims = coordinates(dataset, variable)
        identity = cache_identity(row, lat, lon, dataset, sites)
        identity_sha = hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
        if experiment == 'historical':
            historical_identity = identity
            hist_lat, hist_lon = lat, lon
            support_cache = cache / f'{prefix}_support_{identity_sha}.csv'
            cached_support = read_cached_artifact(support_cache, identity)
            if cached_support is not None:
                grid_rows, _ = cached_support
            else:
                if variable == 'tas':
                    valid = np.isfinite(lat) & (lat < -45)
                    mask_kind = 'atmosphere_all_surfaces_no_land_fraction_filter'
                else:
                    ts = list(dataset.time.values)
                    mask_times = [i for i,t in enumerate(ts) if t.year == 1995 and t.month in (8,11)]
                    if len(mask_times) != 2:
                        raise ValueError('historical ocean mask months unavailable')
                    mask_data = dataset[variable].isel(time=mask_times).compute().values
                    valid = np.all(np.isfinite(mask_data), axis=0) & (lat < -45)
                    mask_kind = 'finite_historical_1995_Aug_and_Nov_ocean_cells'
                grid_rows = pd.DataFrame(nearest_cells(lat, lon, valid, sites))
                grid_rows['source_id'] = source
                grid_rows['member_id'] = hist.member_id
                grid_rows['variable_id'] = variable
                grid_rows['grid_label'] = row.grid_label
                grid_rows['mask_strategy'] = mask_kind
                grid_rows['grid_cell_id'] = [f'{source}:{variable}:{a}:{b}' for a,b in zip(grid_rows.grid_y, grid_rows.grid_x)]
                grid_rows['locations_sharing_cell'] = grid_rows.groupby('grid_cell_id').location_id.transform('size')
                grid_rows['distance_gt_50km'] = grid_rows.distance_km > 50
                grid_rows.to_csv(support_cache, index=False)
                support_cache.with_suffix('.json').write_text(json.dumps({'cache_identity':identity},indent=2))
            grid_rows.to_csv(support_path,index=False)
        elif not (lat.shape == hist_lat.shape and np.allclose(lat, hist_lat, equal_nan=True, rtol=0, atol=1e-6) and np.allclose(lon, hist_lon, equal_nan=True, rtol=0, atol=1e-6)):
            raise ValueError(f'{source} {variable} {experiment}: grid differs from historical')
        if experiment != 'historical':
            parent = dataset.attrs.get('parent_variant_label')
            if parent and parent != hist.member_id:
                raise ValueError(f'parent member mismatch: {parent} != {hist.member_id}')
        identity = bind_support_identity(identity, grid_rows, historical_identity)
        identity_sha = hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
        dest = cache / f'{prefix}_{experiment}_{identity_sha}.npz'
        meta_path = dest.with_suffix('.json')
        times = list(dataset.time.values)
        wanted = [i for i,t in enumerate(times) if t.month in MONTHS and any(start<=t.year<=end for start,end in PERIODS[experiment])]
        selected_times = [times[i] for i in wanted]
        cached_values = read_cached_artifact(dest, identity)
        if cached_values is not None:
            values, meta = cached_values
        else:
            subset = dataset[variable].isel(time=wanted, **{
                dims[0]: xr.DataArray(grid_rows.grid_y.to_numpy(dtype=int), dims='location'),
                dims[1]: xr.DataArray(grid_rows.grid_x.to_numpy(dtype=int), dims='location')})
            raw = subset.transpose('time','location').compute().values
            values, unit = normalize_values(raw, variable, dataset[variable].attrs.get('units',''))
            if not np.isfinite(values).all():
                raise ValueError(f'nonfinite selected monthly values: {np.sum(~np.isfinite(values))}')
            meta = dict(source_id=source, member_id=hist.member_id, variable_id=variable,
                experiment_id=experiment, grid_label=row.grid_label, zstore=row.zstore, http_url=url,
                source_units=dataset[variable].attrs.get('units'), output_units=unit,
                calendar=dataset.time.encoding.get('calendar',getattr(times[0],'calendar','unknown')),
                first_date=str(times[0]), last_date=str(times[-1]), requested_months=len(wanted),
                sites=len(sites), monthly_values=int(values.size), actual_min=float(values.min()),
                actual_max=float(values.max()), grid_shape=list(lat.shape), spatial_dimensions=list(dims),
                grid_unchanged_vs_historical=True,
                parent_source_id=dataset.attrs.get('parent_source_id'),
                parent_experiment_id=dataset.attrs.get('parent_experiment_id'),
                parent_variant_label=dataset.attrs.get('parent_variant_label'),
                tracking_id=dataset.attrs.get('tracking_id'), license=dataset.attrs.get('license'),
                source=dataset.attrs.get('source'), institution=dataset.attrs.get('institution'),
                read_utc=datetime.now(timezone.utc).isoformat())
            meta['cache_identity'] = identity
            np.savez_compressed(dest, values=values)
            meta_path.write_text(json.dumps(meta, indent=2))
        metadata.append(meta)
        monthly = pd.DataFrame({'source_id': source, 'member_id': hist.member_id, 'variable_id': variable,
            'experiment_id': experiment, 'year':np.repeat([t.year for t in selected_times],len(sites)),
            'month':np.repeat([t.month for t in selected_times],len(sites)),
            'location_id':np.tile(grid_rows.location_id.to_numpy(),len(wanted)), 'value':values.ravel(),
            'units':meta['output_units']})
        monthly.to_csv(OUT / f'monthly_{prefix}_{experiment}.csv.gz',index=False)
        for start,end in PERIODS[experiment]:
            years, annual = seasonal_means(values, selected_times, start,end)
            for i,site in enumerate(grid_rows.to_dict('records')):
                records.append(dict(source_id=source,member_id=hist.member_id,variable_id=variable,
                    experiment_id=experiment,period=f'{start}-{end}', location_id=site['location_id'],
                    site_id=site['site_id'],cohort=site['cohort'],latitude=site['latitude'],longitude=site['longitude'],
                    seasonal_mean=float(annual[:,i].mean()), annual_sd=float(annual[:,i].std(ddof=1)),
                    complete_years=int(np.isfinite(annual[:,i]).sum()),units=meta['output_units'],
                    grid_cell_id=site['grid_cell_id'],distance_km=site['distance_km']))
        dataset.close()
        print(f'DONE {source} {variable} {experiment}: {values.shape}',flush=True)
    return records, metadata


def summarize(records, metadata, failures, selected, catalog_path):
    raw = pd.DataFrame(records)
    raw.to_csv(OUT/'seasonal_climatologies.csv',index=False)
    base = raw[raw.experiment_id=='historical'][['source_id','member_id','variable_id','location_id','seasonal_mean']].rename(columns={'seasonal_mean':'baseline_1995_2014'})
    delta = raw[raw.experiment_id!='historical'].merge(base,on=['source_id','member_id','variable_id','location_id'],validate='many_to_one')
    delta['change'] = delta.seasonal_mean-delta.baseline_1995_2014
    delta['change_units'] = delta.variable_id.map({'tas':'degC','sos':'0.001','siconc':'percentage_points'})
    delta.to_csv(OUT/'site_model_changes.csv',index=False)
    keys = ['variable_id','experiment_id','period','location_id','site_id','cohort','latitude','longitude','change_units']
    ensemble = delta.groupby(keys,dropna=False).agg(n_models=('source_id','nunique'),change_mean=('change','mean'),change_median=('change','median'),change_min=('change','min'),change_max=('change','max')).reset_index()
    ensemble.to_csv(OUT/'site_model_ensemble.csv',index=False)
    # Summary across DISTINCT model cells, not 106 pseudo-independent sites.
    unique = delta.drop_duplicates(['source_id','variable_id','experiment_id','period','grid_cell_id'])
    cell_summary = unique.groupby(['source_id','variable_id','experiment_id','period','change_units']).agg(n_unique_cells=('grid_cell_id','nunique'),change_cell_mean=('change','mean'),change_cell_median=('change','median'),change_cell_min=('change','min'),change_cell_max=('change','max')).reset_index()
    cell_summary.to_csv(OUT/'model_unique_cell_summary.csv',index=False)
    # Palmer vicinity is a declared coordinate box, not selected by response.
    palmer_all = delta[delta.latitude.between(-65.0,-64.5)&delta.longitude.between(-64.5,-63.5)]
    palmer_locations = palmer_all.groupby(['source_id','variable_id','experiment_id','period','change_units']).location_id.nunique().rename('n_locations').reset_index()
    palmer = palmer_all.drop_duplicates(['source_id','variable_id','experiment_id','period','grid_cell_id'])
    palmer_summary = palmer.groupby(['source_id','variable_id','experiment_id','period','change_units']).agg(n_unique_cells=('grid_cell_id','nunique'),change=('change','mean'),baseline=('baseline_1995_2014','mean'),future=('seasonal_mean','mean')).reset_index()
    palmer_summary = palmer_summary.merge(palmer_locations,on=['source_id','variable_id','experiment_id','period','change_units'],validate='one_to_one')
    palmer_summary.to_csv(OUT/'palmer_box_unique_cell_summary.csv',index=False)
    palmer_ensemble = palmer_summary.groupby(['variable_id','experiment_id','period','change_units']).agg(n_models=('source_id','nunique'),mean_change=('change','mean'),min_change=('change','min'),max_change=('change','max')).reset_index()
    palmer_ensemble.to_csv(OUT/'palmer_box_three_model_summary.csv',index=False)
    (OUT/'source_metadata.json').write_text(json.dumps(metadata,indent=2))
    supports = pd.concat([pd.read_csv(p) for p in OUT.glob('support_*.csv')],ignore_index=True)
    supports.to_csv(OUT/'coastal_grid_support.csv',index=False)
    support_summary = supports.groupby(['source_id','variable_id','mask_strategy']).agg(locations=('location_id','size'),unique_cells=('grid_cell_id','nunique'),distance_median_km=('distance_km','median'),distance_max_km=('distance_km','max'),locations_gt_50km=('distance_gt_50km','sum')).reset_index()
    support_summary.to_csv(OUT/'grid_support_summary.csv',index=False)
    manifest = dict(status='complete' if not failures else 'partial',created_utc=datetime.now(timezone.utc).isoformat(),
        purpose='conditional_environmental_model_projection_not_biological_forecast_or_observational_attribution',
        source_catalog_url=CATALOG_URL,catalog_sha256=hashlib.sha256(catalog_path.read_bytes()).hexdigest(),
        site_input='outputs/climate_penguin/daily_ice_locations.csv',
        site_input_sha256=hashlib.sha256((ROOT/'outputs/climate_penguin/daily_ice_locations.csv').read_bytes()).hexdigest(),
        selection='First 3 complete models by ASCII source_id; smallest numeric r/i/p/f member per model; native gn preferred among experiment-common grids; newest catalog version; selection before values',
        selected_models=selected[['source_id','member_id']].drop_duplicates().to_dict('records'),
        baseline='1995-2014',future_periods=['2041-2060','2081-2100'],months=list(MONTHS),
        averaging='calendar-day-weighted monthly average per complete year, then equal weight over 20 complete years; equal weight per model for site ensemble',
        model_spread='min/max across selected models; not a confidence or probability interval',
        extraction_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        cache_policy='Content identity from source/version URL, grid, input sites, dates, units, periods/months, historical support cells/mask, mask policy and extraction code; hash-key plus exact JSON sidecar match',
        n_stores_read=len(metadata),n_monthly_values=sum(m['monthly_values'] for m in metadata),
        n_model_site_period_rows=len(raw),n_site_changes=len(delta),failures=failures,
        limitations=['3 availability-selected models are not a representative or probabilistic CMIP6 ensemble',
          'one member per model does not characterize internal variability',
          'nearest coarse cells are not local downscaling or bias correction',
          'distance is site-to-model-cell geodesic displacement, not measured coastline distance',
          'tas is nearest atmospheric grid cell with no land fraction filter; small islands may be unresolved',
          'ocean validity from two finite historical mask frames; no observed coastline mask used',
          'sites sharing a grid cell are not independent environmental replicates',
          'salinity is model sea-surface salinity, not measured colony coastal salinity',
          'vegetation, sea ice drift, reproductive response and population forecasts are outside this extraction'])
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps({k:manifest[k] for k in ('status','n_stores_read','n_monthly_values','n_site_changes','failures')},indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--workers',type=int,default=3)
    parser.add_argument('--select-only',action='store_true')
    args=parser.parse_args()
    OUT.mkdir(exist_ok=True,parents=True)
    catalog_path=WORK/'catalog.csv'
    if not catalog_path.exists():
        response=requests.get(CATALOG_URL,timeout=120);response.raise_for_status();catalog_path.write_bytes(response.content)
    catalog=pd.read_csv(catalog_path)
    eligible=select_stores(catalog,n_models=catalog.source_id.nunique())
    eligible[['source_id','member_id']].drop_duplicates().to_csv(OUT/'eligible_model_first_members.csv',index=False)
    selected=eligible[eligible.source_id.isin(eligible.source_id.unique()[:3])].copy()
    selected.to_csv(OUT/'selected_stores.csv',index=False)
    print(selected[['source_id','member_id','variable_id','experiment_id','grid_label']].to_string(index=False),flush=True)
    if args.select_only:
        return
    sites=pd.read_csv(ROOT/'outputs/climate_penguin/daily_ice_locations.csv')
    if sites.location_id.duplicated().any():
        raise ValueError('duplicate fixed location_id')
    tasks=[(s,v) for s in selected.source_id.unique() for v in TABLES]
    records,metadata,failures=[],[],[]
    with dask.config.set(scheduler='threads',num_workers=6):
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures={pool.submit(read_variable,s,v,selected,sites):(s,v) for s,v in tasks}
            for future in as_completed(futures):
                s,v=futures[future]
                try:
                    r,m=future.result();records.extend(r);metadata.extend(m)
                except Exception as exc:
                    failures.append(dict(source_id=s,variable_id=v,error=repr(exc)))
                    traceback.print_exc()
                (OUT/'progress.json').write_text(json.dumps(dict(completed_stores=len(metadata),failures=failures),indent=2))
    if records:
        summarize(records,metadata,failures,selected,catalog_path)
    else:
        (OUT/'manifest.json').write_text(json.dumps(dict(status='failed',failures=failures),indent=2))
        raise SystemExit(1)

if __name__=='__main__':
    main()
