"""V49 source-only colony coordinate fidelity on fabricated FIG bird records."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_paper2_falkland_original_colony_georef_v49 as m


def fixture(duplicate_centroids=False):
    headers=["Other"]*26
    for c,txt in {0:"Location Name",7:"English name",16:"Breeding status",
                  17:"Colony code",18:"Colony longitude",19:"Colony latitude"}.items():
        headers[c]=txt
    birds=[tuple(headers)]
    places={}
    years=set()
    days=set()
    for k in range(4):
        n="fictional location "+str(k)
        lat=-51.5+k*.01;lon=-60.0
        places[n]={"lat":lat,"lon":lon,"category":"island",
                   "area_ha":200+k,"wider_area":"region a" if k%2==0 else "region b"}
        years.add((n,2009))
        days.add((n,"2009-02-12"))
        for penguin in (True,False):
            source=[""]*26
            source[0]=n
            source[7]="Gentoo penguin" if penguin else "Dolphin gull"
            source[9]=12;source[10]=2;source[11]=2009
            source[16]="Confirmed breeding"
            source[17]="testcolonycode"
            source[2]=lat;source[3]=lon
            source[18]=lon if duplicate_centroids else lon+(.002 if penguin else -.002)
            source[19]=lat
            birds.append(tuple(source))
    return birds,places,years,days


def test_original_colony_coordinates_valid_geographically_without_nest_claim():
    state,coord=m.coordinate_state(-51.1,-60.4)
    assert state=="VALID_BOTH_SOURCE_FIELDS" and coord==(-51.1,-60.4)
    assert m.coordinate_state("",0)[0]=="ONE_FIELD_MISSING"
    assert m.coordinate_state(0,0)[0]=="OUTSIDE_FIXED_FALKLAND_WGS84_OR_SENTINEL"
    assert m.distance_m((-51.5,-60.),(-51.5,-60.))==0
    assert m.distance_m((-51.5,-60.),(-51.5,-59.998))>100


def test_independent_original_colony_georefs_can_be_compared_as_SOURCE_gates():
    birds,places,year,days=fixture(False)
    q=m.source_bird_colony_geo(birds,places,year,days)
    assert q["V47_original_same_island_year_confirmed_source_pairs"]==4
    assert q["same_year_both_guild_valid_colony_latlon_pairs"]==4
    assert q["same_year_both_guild_noncentroid_gt100m_colony_source_pairs"]==4
    assert q["same_day_both_guild_noncentroid_gt100m_colony_source_pairs"]==4
    assert q["G4_two_guild_noncentroid_original_colony_georef_support_pass"] is False
    assert q["source_original_candidate_location_categories"]=={"island":4}
    assert q["physical_shore_to_nest_route_estimated"] is False


def test_colony_coordinates_copied_from_island_centroid_are_NOT_nest_gps():
    birds,places,year,days=fixture(True)
    q=m.source_bird_colony_geo(birds,places,year,days)
    assert q["same_year_both_guild_valid_colony_latlon_pairs"]==4
    assert q["same_year_both_guild_noncentroid_gt100m_colony_source_pairs"]==0
    assert q["source_original_colony_distance_to_island_reference_m_V47_matched"]["n_distance_le20m"]==8
    assert q["G4_two_guild_noncentroid_original_colony_georef_support_pass"] is False


def test_missing_or_single_colony_coordinate_is_unresolved():
    birds,places,year,days=fixture()
    arr=list(birds[1]);arr[18]="";birds[1]=tuple(arr)
    q=m.source_bird_colony_geo(birds,places,year,days)
    assert q["source_rows_at_definite_matched_island_year"]["colony_ONE_FIELD_MISSING"]==1
    assert q["source_original_colony_distance_to_island_reference_m_V47_matched"]["n"]==7
