"""Numerical contracts: missingness, true season matching and geographic adjustment."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

SCRIPT = Path(__file__).resolve().parents[1] / 'research/climate-penguin/work/vegetation_response_v1/analyze_vegetation_relationships.py'
spec = importlib.util.spec_from_file_location('vegetation_response_v1', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def panel(rows):
    return pd.DataFrame(rows, columns=['site_id','species_id','season','count']).assign(
        region='R', site_name=lambda x:x.site_id, latitude=-64., longitude=-63., method='ground')


def areas(rows):
    return pd.DataFrame(rows, columns=['site_id','mapped_terrestrial_union_area_2km_m2'])


class VegetationResponseTests(unittest.TestCase):
    def test_collapsing_repeats_keeps_observed_zero_and_unknown_change(self):
        # Break caught: repeat weighting, imputed absent seasons, or map-absence=biological-zero.
        self.assertTrue(callable(getattr(mod, 'build_site_cohort', None)), 'site cohort function missing')
        counts=panel([('A','ADPE',2017,0),('A','ADPE',2019,8),('B','ADPE',2018,4),
                      ('C','ADPE',2018,np.nan),('D','ADPE',2016,500)])
        got=mod.build_site_cohort(counts,areas([('A',100),('B',0),('C',900),('D',50)]))
        self.assertEqual(len(got),2)
        a=got.set_index('site_id').loc['A']; b=got.set_index('site_id').loc['B']
        self.assertEqual(a['observed_seasons'],2)
        self.assertEqual(a['count_median'],4)
        self.assertAlmostEqual(a['observed_log_count_slope_per_year'],1.0986122886681098)
        self.assertEqual(a['observed_zero_seasons'],1)
        self.assertFalse(bool(b['positive_mapped_detection']))
        self.assertTrue(np.isnan(b['observed_log_count_slope_per_year']))
        self.assertEqual(b['count_median'],4)

    def test_duplicate_counts_or_map_rows_cannot_silently_multiply_units(self):
        self.assertTrue(callable(getattr(mod, 'build_site_cohort', None)), 'site cohort function missing')
        counts=panel([('A','ADPE',2017,1),('A','ADPE',2017,2)])
        with self.assertRaises(ValueError):
            mod.build_site_cohort(counts,areas([('A',100)]))
        with self.assertRaises(ValueError):
            mod.build_site_cohort(counts.iloc[:1],areas([('A',100),('A',100)]))

    def test_common_species_comparison_matches_same_observed_season(self):
        # Break caught: species with disjoint survey years treated as paired observations.
        self.assertTrue(callable(getattr(mod, 'build_matched_species', None)), 'matched comparison function missing')
        counts=panel([('A','ADPE',2017,3),('A','ADPE',2018,99),('A','GEPE',2017,7),
                      ('B','ADPE',2017,10),('B','GEPE',2018,20)])
        matched=mod.build_matched_species(counts,areas([('A',100),('B',200)]),'ADPE','GEPE')
        self.assertEqual(len(matched),1)
        self.assertEqual(matched.iloc[0]['site_id'],'A')
        self.assertEqual(matched.iloc[0]['common_seasons'],1)
        self.assertAlmostEqual(matched.iloc[0]['mean_log_count_difference_second_minus_first'],0.6931471805599453)

    def test_region_adjustment_uses_within_region_variation(self):
        # Hand-checked slope=2 within each region; between-region offsets must disappear.
        self.assertTrue(callable(getattr(mod, 'association', None)), 'association function missing')
        got=mod.association(np.array([1.,2.,11.,12.]),np.array([2.,4.,2.,4.]),np.array(['A','A','B','B']),True)
        self.assertAlmostEqual(got['slope'],2.)
        self.assertAlmostEqual(got['pearson_r'],1.)
        self.assertEqual(got['n'],4)
        empty=mod.association(np.array([1.,2.]),np.array([3.,4.]),np.array(['A','B']),True)
        self.assertTrue(np.isnan(empty['slope']))

    def test_missing_values_cannot_create_common_case_disagreement(self):
        self.assertTrue(callable(getattr(mod, 'association', None)), 'association function missing')
        got=mod.association(np.array([1.,2.,np.nan,4.]),np.array([2.,4.,9.,8.]),np.array(['A','A','A','A']),False)
        self.assertEqual(got['n'],3)
        self.assertAlmostEqual(got['slope'],2.)

    def test_spatial_block_transitive_links_keep_nearby_sites_together(self):
        self.assertTrue(callable(getattr(mod, 'spatial_blocks', None)), 'spatial block function missing')
        data=pd.DataFrame({'site_id':['A','B','C','D'],'latitude':[0.,0.,0.,20.],'longitude':[0.,.06,.12,0.]})
        got=mod.spatial_blocks(data,10.)
        self.assertEqual(got['A'],got['B'])
        self.assertEqual(got['A'],got['C'])
        self.assertNotEqual(got['A'],got['D'])


if __name__ == '__main__':
    unittest.main()
