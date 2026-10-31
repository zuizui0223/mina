"""Source-backed 308 Chinstrap GPS radial-GAM diagnostic × 300 TDR/GPS QA.

Original GPS 308 deployments, source-raster model and 300 original BAS
instrument QA are regenerated in ONE GH Actions source run. No source IDs,
including GPS-only and failed-quality tags, are deleted from the audit.

This is a post-result selection/sampling-bias check of the VISITED published
Freer (2025) GAM relative to a distance-matched circular GAM-valid reference,
NOT independent krill biomass, a measured foraging area, flightless bird
fitness, ocean-accessible geography or a climate-to-breeding causal result.
"""
from __future__ import annotations
import argparse,csv,json,math,statistics
from pathlib import Path
import chinstrap_300tag_observability_v1 as qa

YEAR_PAIRS=((2011,"LI"),(2013,"PI"),(2015,"MI"))
SPECIES="Chinstrap"
ISLAND_YEARS=(("SI",2011),("SI",2013),("SI",2015),("SI",2018),
              ("LI",2011),("PI",2013),("MI",2015))
PERIODS=("preseason","same_summer")
TIERS=("all_GPS","GPS_TDR_source_matched","sensor_QA_primary","sensor_QA_strict")
NUMERIC_PRIMARY={(2011,"LI"):1.6659143365744729,
                 (2013,"PI"):4.499387620290262,
                 (2015,"MI"):3.0160992836021143}
NUMERIC_STRICT={(2011,"LI"):1.6690234798851549,
                (2013,"PI"):6.403454001841444,
                (2015,"MI"):3.20663170547873}
NUMERIC_RAW={(2011,"LI"):1.7299767895093023,
             (2013,"PI"):4.0400136696919375,
             (2015,"MI"):2.9649677228535887}
MIN_TAG_HOURS=10

def load_csv(file):
    with Path(file).open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def modelled_tag_rows(file):
    records=load_csv(file)
    if len(records)!=308 or len({r["deployment"] for r in records})!=308:
        raise ValueError("original 308 unique Chinstrap GPS tag roster changed")
    if {(r["island"],int(r["season_start"])) for r in records}!=set(ISLAND_YEARS):
        raise ValueError("source GPS island×year support changed")
    return records

def attach_QA(gps,qa_rows,require_complete_source=True):
    decisions={x["original_source_id"]:x for x in qa_rows}
    if require_complete_source and len(decisions)!=300:
        raise ValueError("expected complete source 300 TDR/GPS original QA")
    out=[]
    for g in gps:
        pair=decisions.get(g["deployment"])
        r=dict(g)
        r["source_original_BAS_TDR_GPS_pair_exists"]=pair is not None
        r["TDR_source_covered_and_QA_primary"]=(pair["primary_source_observability"] if pair else None)
        r["TDR_source_covered_and_QA_strict"]=(pair["strict_GPS_sensitivity"] if pair else None)
        r["source_not_in_TDR_300_is_not_animal_no_dive"]=pair is None
        r["GPS_source_hourly_ge10"]=(
            g["preseason_qualified_source_hourly"]=="True" and
            g["same_summer_qualified_source_hourly"]=="True" and
            g["preseason_observed_track_mean_GAM_g_m2"] not in ("",None) and
            g["same_summer_observed_track_mean_GAM_g_m2"] not in ("",None))
        out.append(r)
    return out

def eligible(row,tier):
    if not row["GPS_source_hourly_ge10"]:
        return False
    if tier=="all_GPS":return True
    if tier=="GPS_TDR_source_matched":return row["source_original_BAS_TDR_GPS_pair_exists"]
    if tier=="sensor_QA_primary":return row["TDR_source_covered_and_QA_primary"] is True
    if tier=="sensor_QA_strict":return row["TDR_source_covered_and_QA_strict"] is True
    raise ValueError("unknown quality tier")

def get_period(tag,period):
    o=float(tag[period+"_observed_track_mean_GAM_g_m2"])
    a=float(tag[period+"_distance_matched_reference_GAM_g_m2"])
    if not(math.isfinite(o) and math.isfinite(a) and o>=0 and a>0):
        raise ValueError("invalid source modelled krill and distance-matched reference")
    return o,a

def summarize(tags):
    group=[]
    for tier in TIERS:
        for site,year in ISLAND_YEARS:
            eligible_tags=[r for r in tags if r["island"]==site and
                           int(r["season_start"])==year and eligible(r,tier)]
            for period in PERIODS:
                if eligible_tags:
                    obs,radial=zip(*(get_period(tag,period) for tag in eligible_tags))
                    modelled=statistics.mean(obs)
                    ref=statistics.mean(radial)
                    ratio=modelled/ref
                    n_below=sum(x<y for x,y in zip(obs,radial))
                else:
                    modelled=ref=ratio=None
                    n_below=0
                group.append({
                    "source_quality_tier":tier,"island":site,
                    "season_start":year,"period":period,
                    "n_original_available_tags":len(eligible_tags),
                    "n_tags_below_radius_matched_model_background":n_below,
                    "fraction_tags_below_distance_reference":n_below/len(eligible_tags) if eligible_tags else None,
                    "tag_equal_mean_original_GPS_GAM_g_m2":modelled,
                    "tag_equal_mean_radial_matched_GAM_g_m2":ref,
                    "GPS_modelled_krill_div_radius_background":ratio,
                    "no_P_valid_forage_or_independent_krill":True
                })
    pairs=[]
    idx={(x["source_quality_tier"],x["island"],x["season_start"],x["period"]):x for x in group}
    for tier in TIERS:
        for year,other in YEAR_PAIRS:
            for period in PERIODS:
                a=idx[tier,"SI",year,period]
                b=idx[tier,other,year,period]
                if not a["n_original_available_tags"] or not b["n_original_available_tags"]:
                    raise ValueError("matched-year island source spatial support dropped")
                normalized=b["GPS_modelled_krill_div_radius_background"]/a["GPS_modelled_krill_div_radius_background"]
                pairs.append({
                    "source_quality_tier":tier,"season_start":year,
                    "other_island":other,"reference_island":"SI",
                    "krill_model_period":period,
                    "source_tag_n_other":b["n_original_available_tags"],
                    "source_tag_n_Signy":a["n_original_available_tags"],
                    "ratio_other_to_Signy_modelled_GPS_density":(
                      b["tag_equal_mean_original_GPS_GAM_g_m2"]/
                      a["tag_equal_mean_original_GPS_GAM_g_m2"]),
                    "ratio_other_to_Signy_radius_matched_background":(
                      b["tag_equal_mean_radial_matched_GAM_g_m2"]/
                      a["tag_equal_mean_radial_matched_GAM_g_m2"]),
                    "ratio_other_to_Signy_directional_model_output_after_radial_background":normalized,
                    "signy_source_instrument_coverage_not_true_marine_foraging":True,
                    "all_three_pairs_are_different_other_islands_and_years":True
                })
    if len(group)!=4*7*2 or len(pairs)!=4*3*2:
        raise ValueError("all quality×island/year×period source combinations not retained")
    return group,pairs

def verify(tags,group,pairs):
    if len(tags)!=308:
        raise ValueError("source GPS tag count changed")
    n={
      "GPS_hourly_original":sum(r["GPS_source_hourly_ge10"] for r in tags),
      "source_TDR_matched":sum(eligible(r,"GPS_TDR_source_matched") for r in tags),
      "sensor_QA_primary":sum(eligible(r,"sensor_QA_primary") for r in tags),
      "sensor_QA_strict":sum(eligible(r,"sensor_QA_strict") for r in tags)
    }
    if n!={"GPS_hourly_original":253,"source_TDR_matched":247,
           "sensor_QA_primary":175,"sensor_QA_strict":47}:
        raise ValueError("source GPS/TDR selection cardinality changed "+str(n))
    idx={(r["source_quality_tier"],r["island"],r["season_start"],r["period"]):r for r in group}
    # The important new source-derived result: all 103 original eligible
    # Signy tags in all four available years lie below radial model background.
    for year,count in ((2011,4),(2013,19),(2015,26),(2018,54)):
        r=idx["all_GPS","SI",year,"preseason"]
        if (r["n_original_available_tags"],r["n_tags_below_radius_matched_model_background"])!=(count,count):
            raise ValueError("original Signy source low-GAM direction roster changed")
    primary={(2011,3),(2013,8),(2015,23),(2018,42)}
    for year,count in primary:
        r=idx["sensor_QA_primary","SI",year,"preseason"]
        if (r["n_original_available_tags"],r["n_tags_below_radius_matched_model_background"])!=(count,count):
            raise ValueError("source QA primary Signy denominator changed")
    strict=idx["sensor_QA_strict","SI",2018,"preseason"]
    if strict["n_original_available_tags"]!=0 or strict["GPS_modelled_krill_div_radius_background"] is not None:
        raise ValueError("missing Signy 2018 strict source tags must be NA, not ecological zero")
    for year,other in YEAR_PAIRS:
        for tier,expect in (("all_GPS",NUMERIC_RAW),
                            ("sensor_QA_primary",NUMERIC_PRIMARY),
                            ("sensor_QA_strict",NUMERIC_STRICT)):
            row=next(r for r in pairs if
                r["source_quality_tier"]==tier and
                r["season_start"]==year and r["other_island"]==other and
                r["krill_model_period"]=="preseason")
            actual=row["ratio_other_to_Signy_directional_model_output_after_radial_background"]
            if not math.isclose(actual,expect[year,other],rel_tol=1e-11,abs_tol=1e-11):
                raise ValueError("independent original-source radial QA receipt not reproduced")
    return n

def save(path,rows):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-radial-source",required=True,type=Path)
    p.add_argument("--original-300-qa",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--check",action="store_true")
    x=p.parse_args()
    q=qa.evaluate(qa.read(x.original_300_qa))
    qc,islands=qa.summary(q)
    qa.verify(qc,islands)
    observed=attach_QA(modelled_tag_rows(x.original_radial_source),q)
    group,pairs=summarize(observed)
    counts=verify(observed,group,pairs) if x.check else {
       k:sum(eligible(r,tier) for r in observed) for k,tier in (
         ("GPS_hourly_original","all_GPS"),
         ("source_TDR_matched","GPS_TDR_source_matched"),
         ("sensor_QA_primary","sensor_QA_primary"),
         ("sensor_QA_strict","sensor_QA_strict"))
    }
    x.out.mkdir(parents=True,exist_ok=True)
    save(x.out/"all_original_GPS_tags_with_sensor_QA_flags.csv",observed)
    save(x.out/"island_year_radial_selection_QA_56.csv",group)
    save(x.out/"same_species_same_year_island_differences_QA_24.csv",pairs)
    decision={
        "status":"GPS_DIRECTIONS_DIFFER_IN_EXISTING_KRILL_MODEL_AFTER_RADIUS_AND_SENSOR_QA",
        "source_original_radial_GPS_model_CI":
            "https://github.com/zuizui0223/mina/actions/runs/41183123990",
        "original_300_TDR_QA_CI":
            "https://github.com/zuizui0223/mina/actions/runs/41177252296",
        "original_300_QA_CSV_sha256":qa.INPUT_SHA,
        "n_original_GPS_tracks":len(observed),
        "source_GPS_QA_cardinality":counts,
        "n_total_site_years":len(ISLAND_YEARS),
        "n_paired_island_years":len(YEAR_PAIRS),
        "all_24_predefined_correlations_or_ratios_retained":True,
        "all_103_Signy_GPS_tag_radial_GAM_below_reference":True,
        "Signy_2018_strict_QA_is_missing_not_no_foraging":True,
        "matched_preseason_primary_QA":[r for r in pairs if
          r["source_quality_tier"]=="sensor_QA_primary" and
          r["krill_model_period"]=="preseason"],
        "source_qualification_kind":"Post-exposure TDR/GPS instrument time coverage, not verified diving/capture state",
        "model_output_kind":"Freer 2025 published fitted GAM krill, not original acoustic krill at tracked locations",
        "warnings":[
           "All 103 Signy results use the SAME trained Freer GAM, not 103 independent environmental replicates.",
           "Same-year, same-species contrasts do not repeat the same non-Signy island across years.",
           "GPS directional pattern can be due to geography, prey gradients in published GAM, coast accessibility, ice, animal selection, or model bias; none are separately identified.",
           "10km distance-matched all valid GAM cells assumes complete azimuth access, not independently checked.",
           "Post-source sensor selection and small Signy 2011/2013 samples preclude a population-level causal effect.",
           "No new empirical climate→prey or prey→fledgling→breeding space transfer coefficient is estimated.",
           "No 2050/2100 breeding-pair, N_eff or Antarctic greening quantitative prediction is validated."
        ]
    }
    (x.out/"decision.json").write_text(json.dumps(decision,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":decision["status"],
        "total_GPS_original":len(observed),
        "quality_cardinality":counts,
        "Signy_radial_low_by_year":[{k:r[k] for k in ("season_start","n_original_available_tags",
           "n_tags_below_radius_matched_model_background",
           "GPS_modelled_krill_div_radius_background")}
            for r in group if r["island"]=="SI" and r["source_quality_tier"]=="sensor_QA_primary"
             and r["period"]=="preseason"],
        "matched_preseason":decision["matched_preseason_primary_QA"],
        "receipt_checked":bool(x.check)
    },ensure_ascii=False))

if __name__=="__main__":main()
