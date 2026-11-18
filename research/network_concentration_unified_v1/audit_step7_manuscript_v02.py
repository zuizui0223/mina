#!/usr/bin/env python3
"""Step7 v0.2 manuscript quality gate against both old frozen source and new TV audit."""
from pathlib import Path
import json,hashlib

BASE=Path(__file__).resolve().parent
OUT=BASE/"outputs"
ARTICLE=BASE/"MANUSCRIPT_FULL_DRAFT_V0_2.md"

def insist(ok,message):
    if not ok:raise ValueError("v0.2 source QA fail: "+message)

def main():
    txt=ARTICLE.read_text(encoding="utf-8")
    original=json.loads((OUT/"STEP6_MANUSCRIPT_SOURCE_QA.json").read_text())
    new=json.loads((OUT/"STEP7_LATE_SHARE_BREAKDOWN.json").read_text())
    hypotheses=json.loads((OUT/"STEP4_FIXED_ASSOCIATIONS.json").read_text())
    insist(original["status"]=="PASS_MANUSCRIPT_SOURCE_FACTS_WITH_DISCLOSED_MEASUREMENT_HOLD","baseline source document not verified")
    insist((original["JNCC"]["positive"],original["JNCC"]["positive_in_declines"])==(436,324),"baseline original outcome changed")
    insist(new["status"]=="POST_RESULT_LATE_ONLY_COMPOSITION_TV_FRAGILITY_NOT_ERROR_CALIBRATION","new source metric status")
    q=new["all_JNCC"]
    insist((q["rows"],q["positive_rows"],q["reached_n"],q["unreachable_n"])==(663,436,429,7),"breakdown source support")
    insist([q["threshold_n"][str(t)] for t in (.01,.025,.05,.1)]==[15,38,94,185],"pre-fixed breakdown thresholds")
    insist(all(not v["prediction_supported"] for v in hypotheses["results"].values()),"fixed H3/H4 support changed")
    required=[
        "Full integrated manuscript draft v0.2",
        "436 (65.8%)",
        "324 (67.6%)",
        "15 of 17",
        "427 of the 651",
        "374/573",
        "94 of the 436",
        "21.6%",
        "429",
        "12.84%",
        "5.59%",
        "24.95%",
        "H3 adjusted p = 0.940",
        "H4D adjusted p = 1.000",
        "H4W adjusted p = 1.000",
        "not externally preregistered",
        "not an estimate of survey error",
        "original unchanged null",
        "Site.ID",
    ]
    missing=[x for x in required if x not in txt]
    insist(not missing,"missing grounded manuscript claims: "+str(missing))
    insist("327 (68.3%)" not in txt,"previous transcription error remained")
    insist("confirmed survey error" not in txt and "causally caused" not in txt,"unsupported effect")
    insist("actual survey error" in txt and "original count-only null offset fixed" in txt,
           "not enough observation-error caveat")
    insist("## Abstract" in txt and "## Results" in txt and "## Discussion" in txt and
           "## Materials and methods" in txt,"missing article sections")
    result={
        "status":"PASS_V02_POST_RESULT_FRAGILITY_WITHOUT_SCIENTIFIC_HYPOTHESIS_REWRITE",
        "manuscript":str(ARTICLE.relative_to(BASE)),
        "manuscript_sha256":hashlib.sha256(ARTICLE.read_bytes()).hexdigest(),
        "source_old_qa_sha256":hashlib.sha256((OUT/"STEP6_MANUSCRIPT_SOURCE_QA.json").read_bytes()).hexdigest(),
        "source_step7_qa_sha256":hashlib.sha256((OUT/"STEP7_LATE_SHARE_BREAKDOWN.json").read_bytes()).hexdigest(),
        "unmodified_step1_positive":436,"unmodified_declining_positive":324,
        "new_post_result_late_only_TV":{"n_positive":436,"reachable":429,"unreachable":7,
                  "n_breakdown_le_1pct":15,"n_le_2p5pct":38,"n_le_5pct":94,"n_le_10pct":185},
        "frozen_H2_status":hypotheses["H2"]["status"],
        "frozen_H3_H4_holm":{k:v["holm_4"] for k,v in hypotheses["results"].items()},
        "source_method_comparable_effort":False,
        "site_polygon_crosswalk_verified":False,
        "submission_ready":False,
    }
    (OUT/"STEP7_MANUSCRIPT_V02_QA.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"old_main":436,"fragility_5pct":94}))

if __name__=="__main__":main()
