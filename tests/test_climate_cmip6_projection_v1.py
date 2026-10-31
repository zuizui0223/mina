"""Core scientific contracts: calendars, complete seasons, units and selection."""
import importlib.util
from pathlib import Path
import cftime
import numpy as np
import pandas as pd
import pytest

PATH = Path(__file__).resolve().parents[1] / 'research/climate-penguin/work/cmip6_projection_v1/extract.py'
spec = importlib.util.spec_from_file_location('cmip6_projection_v1', PATH)
m = importlib.util.module_from_spec(spec)
if PATH.exists():
    spec.loader.exec_module(m)


def test_gregorian_season_uses_calendar_day_weights():
    times = [cftime.DatetimeGregorian(2000, n, 16) for n in (8, 9, 10, 11)]
    years, values = m.seasonal_means(np.array([[0.], [10.], [20.], [30.]]), times, 2000, 2000)
    assert years.tolist() == [2000]
    assert values[0, 0] == pytest.approx(1820 / 122)


def test_360_day_calendar_does_not_use_pandas_datetime():
    times = [cftime.Datetime360Day(2050, n, 30) for n in (8, 9, 10, 11)]
    _, values = m.seasonal_means(np.array([[0.], [10.], [20.], [30.]]), times, 2050, 2050)
    assert values[0, 0] == 15


def test_missing_month_is_rejected_instead_of_short_season():
    times = [cftime.DatetimeNoLeap(2000, n, 16) for n in (8, 9, 11)]
    with pytest.raises(ValueError, match='complete'):
        m.seasonal_means(np.ones((3, 1)), times, 2000, 2000)


def test_missing_site_value_does_not_silently_shorten_season():
    times = [cftime.DatetimeNoLeap(2000, n, 16) for n in (8, 9, 10, 11)]
    _, values = m.seasonal_means(np.array([[1.], [np.nan], [1.], [1.]]), times, 2000, 2000)
    assert np.isnan(values[0, 0])


def test_siconc_fraction_conversion_and_percentage_point_change():
    values, unit = m.normalize_values(np.array([0.2, 0.8]), 'siconc', '1')
    assert values.tolist() == [20., 80.]
    assert unit == 'percent'
    assert (values[1] - values[0]) == 60.


def test_siconc_percent_values_below_one_are_not_misread_as_fractions():
    values, _ = m.normalize_values(np.array([0.2, 0.8]), 'siconc', '%')
    assert values.tolist() == [0.2, 0.8]


def test_siconc_out_of_range_is_rejected():
    with pytest.raises(ValueError, match='range'):
        m.normalize_values(np.array([100.1]), 'siconc', '%')


def test_temperature_celsius_and_salinity_scale():
    values, unit = m.normalize_values(np.array([273.15, 275.15]), 'tas', 'K')
    assert values.tolist() == pytest.approx([0, 2])
    assert unit == 'degC'
    values, unit = m.normalize_values(np.array([34.]), 'sos', '0.001')
    assert values.tolist() == [34.]
    assert unit == '0.001'


def test_ocean_mask_and_dateline_nearest_cell():
    lat = np.array([[-70., -70., -70.]])
    lon = np.array([[179., -179., -170.]])
    sites = pd.DataFrame({'location_id':['x'], 'latitude':[-70.], 'longitude':[-180.]})
    rows = m.nearest_cells(lat, lon, np.array([[False, True, True]]), sites)
    assert rows[0]['grid_y'] == 0
    assert rows[0]['grid_x'] == 1
    assert 30 < rows[0]['distance_km'] < 45


def test_selection_requires_same_member_all_three_experiments_and_variables():
    rows = []
    for source, member in [('B','r1i1p1f1'), ('A','r10i1p1f1'), ('A','r2i1p1f1')]:
        for variable, table in [('tas','Amon'),('sos','Omon'),('siconc','SImon')]:
            for experiment in ['historical','ssp245','ssp585']:
                rows.append(dict(source_id=source, member_id=member, variable_id=variable,
                    table_id=table, experiment_id=experiment, grid_label='gn', version=1,
                    zstore=f'gs://example/{source}/{member}/{variable}/{experiment}'))
    # A/r2 is incomplete; selection must use complete A/r10, not mix members.
    rows = [r for r in rows if not (r['source_id']=='A' and r['member_id']=='r2i1p1f1' and r['variable_id']=='sos')]
    selected = m.select_stores(pd.DataFrame(rows), n_models=2)
    assert set(zip(selected.source_id, selected.member_id)) == {('A','r10i1p1f1'),('B','r1i1p1f1')}
    assert len(selected) == 18


@pytest.mark.parametrize('changed', ['zstore','grid_sha256','sites_sha256','periods','months','code_sha256'])
def test_changed_input_identity_never_reuses_stale_monthly_values(tmp_path, changed):
    import json
    path=tmp_path/'values.npz'
    original=dict(zstore='gs://source/v1/',grid_sha256='grid1',sites_sha256='sites1',
                  periods=[[1995,2014]],months=[8,9,10,11],code_sha256='code1')
    np.savez_compressed(path,values=np.array([[42.]]))
    path.with_suffix('.json').write_text(json.dumps({'cache_identity':original}))
    current=dict(original)
    current[changed]='changed-input'
    with pytest.raises(ValueError,match='cache identity'):
        m.read_cached_artifact(path,current)


def test_matching_input_identity_reuses_actual_cached_values(tmp_path):
    import json
    path=tmp_path/'values.npz'
    identity={'zstore':'gs://source/v1/','sites_sha256':'sites1'}
    np.savez_compressed(path,values=np.array([[42.]]))
    path.with_suffix('.json').write_text(json.dumps({'cache_identity':identity}))
    values,metadata=m.read_cached_artifact(path,identity)
    assert values.tolist()==[[42.]]
    assert metadata['cache_identity']==identity


def test_changed_input_identity_never_reuses_stale_support_csv(tmp_path):
    import json
    path=tmp_path/'support.csv'
    pd.DataFrame({'location_id':['x'],'grid_y':[2],'grid_x':[4]}).to_csv(path,index=False)
    path.with_suffix('.json').write_text(json.dumps({'cache_identity':{'sites_sha256':'old'}}))
    with pytest.raises(ValueError,match='cache identity'):
        m.read_cached_artifact(path,{'sites_sha256':'new'})


def test_future_identity_changes_when_historical_support_cell_changes():
    future={'zstore':'gs://future/unchanged/'}
    first=pd.DataFrame({'location_id':['x'],'grid_y':[2],'grid_x':[4]})
    second=pd.DataFrame({'location_id':['x'],'grid_y':[3],'grid_x':[4]})
    assert m.bind_support_identity(future,first,{'zstore':'gs://hist/v1/'}) != m.bind_support_identity(future,second,{'zstore':'gs://hist/v1/'})


def test_future_identity_changes_when_historical_version_changes():
    future={'zstore':'gs://future/unchanged/'}
    support=pd.DataFrame({'location_id':['x'],'grid_y':[2],'grid_x':[4]})
    assert m.bind_support_identity(future,support,{'zstore':'gs://hist/v1/'}) != m.bind_support_identity(future,support,{'zstore':'gs://hist/v2/'})
