import unittest
from scripts.audit_postglacial_support import audit


def exp(site='S1', **kwargs):
    out=dict(site_id=site,species_id='GEPE',patch_id=site+'-p',landmass_id='I1',
             exposure_first_year='2018',exposure_last_year='2020',
             prior_ice_verified='yes',icefree_verified='yes',spatial_match='exact',source_id='publisherA')
    out.update(kwargs)
    return out


def obs(site='S1',season='2021',state='A',**kwargs):
    out=dict(site_id=site,species_id='GEPE',season=season,state=state,
             visited='yes',effort_verified='yes',source_id='publisherB')
    out.update(kwargs)
    return out


class TestSourceSupport(unittest.TestCase):
    def test_verified_consecutive_A_P(self):
        result=audit([exp()],[obs(),obs(season='2022',state='P')])
        self.assertEqual(len(result['verified_A_to_P_events']),1)
        self.assertEqual(result['A_risk_pairs'],1)
        self.assertEqual(result['sample_support'],'HOLD')

    def test_no_missing_to_absence(self):
        result=audit([exp()],[obs(),obs(season='2022',state='NR'),obs(season='2023',state='P')])
        self.assertEqual(len(result['verified_A_to_P_events']),0)
        self.assertEqual(result['A_risk_pairs'],0)

    def test_no_preexposure_no_unverified_visit(self):
        result=audit([exp()],[obs(season='2019'),obs(season='2020',state='P',effort_verified='no')])
        self.assertEqual(len(result['verified_A_to_P_events']),0)
        self.assertEqual(result['exclusion_counts']['before_confirmed_exposure'],1)
        self.assertEqual(result['exclusion_counts']['unverified_visit_or_effort'],1)

    def test_uncertain_spatial_match_excluded(self):
        result=audit([exp(spatial_match='provisional')],[obs(),obs(season='2022',state='P')])
        self.assertEqual(result['verified_exposure_site_species'],0)
        self.assertEqual(len(result['verified_A_to_P_events']),0)

    def test_first_present_is_not_colonization(self):
        result=audit([exp()],[obs(state='P'),obs(season='2022',state='P')])
        self.assertEqual(len(result['verified_A_to_P_events']),0)
        self.assertEqual(result['consecutive_pairs']['P_to_P'],1)

    def test_conflicting_survey_errors(self):
        with self.assertRaises(ValueError):
            audit([exp()],[obs(),obs(state='P')])

    def test_many_subsites_same_island_not_replication(self):
        ex=[exp(site=f'S{i}') for i in range(30)]
        sv=[o for i in range(30) for o in [obs(site=f'S{i}'),obs(site=f'S{i}',season='2022',state='P')]]
        result=audit(ex,sv)
        self.assertEqual(len(result['verified_A_to_P_events']),30)
        self.assertEqual(result['independent_landmass_labels_with_repeated_visits'],1)
        self.assertEqual(result['sample_support'],'HOLD')


if __name__ == '__main__':
    unittest.main()
