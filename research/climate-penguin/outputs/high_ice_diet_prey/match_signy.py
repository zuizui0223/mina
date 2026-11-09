"""Sensitivity of the two consecutive Signy seasons to gear and spatial matching."""
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Geod
from scipy.optimize import linear_sum_assignment

out = Path(__file__).resolve().parent
table = pd.read_csv(out / 'matching_hauls.csv')
h = table.query("region == 'Signy' and km <= 100 and NET_TYPE == 'Isaac Kidd'")
high = h[h.year == 2007].reset_index(drop=True)
low = h[h.year == 2008].reset_index(drop=True)
lon1, lon2 = np.meshgrid(high.LONGITUDE, low.LONGITUDE, indexing='ij')
lat1, lat2 = np.meshgrid(high.LATITUDE, low.LATITUDE, indexing='ij')
distance = Geod(ellps='WGS84').inv(lon1, lat1, lon2, lat2)[2] / 1000
records = []
for cutoff in [10, 25, 50]:
    # A prohibitive cost maximizes valid pair count before minimizing distance.
    rows, cols = linear_sum_assignment(np.where(distance <= cutoff, distance, 1e5))
    for i, j in zip(rows, cols):
        if distance[i, j] <= cutoff:
            records.append(dict(cutoff_km=cutoff, distance_km=distance[i,j],
                high_station=high.STATION[i], low_station=low.STATION[j],
                high_day=high.DATE[i], low_day=low.DATE[j],
                high_krill=high.STANDARDISED_KRILL_UNDER_1M2[i],
                low_krill=low.STANDARDISED_KRILL_UNDER_1M2[j]))
pd.DataFrame(records).to_csv(out / 'gear_spatial_pairs.csv',index=False)
