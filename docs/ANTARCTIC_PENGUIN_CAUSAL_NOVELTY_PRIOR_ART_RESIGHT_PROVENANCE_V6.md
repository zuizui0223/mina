# V6 — Prior art rules out easy penguin-colony causal novelty; public resight copy identity gate

Date: 2026-10-08. Evidence and provenance audit, not a new ecological discovery. Ecology PR189 and frozen individual-choice PR142 untouched.

## Existing results we must not claim as new

- **Penney 1968** (doi:10.1029/AR012p0083): Two small Adélie nesting groups attracted many new breeders and grew quickly while retaining relatively low breeding success. Adult territory fidelity, individual recognition and edge effects already described. Thus attraction without high local fitness is very old prior art.
- **Penney 1970** (doi:10.1016/0003-3472(70)90048-5): Young first breeders wander and are less nest-site faithful; 40% first breed in natal contiguous colony group, 66% within natal area (~200 m). Age-dependent pioneering not new.
- **Cox et al. 2024** (doi:10.1007/s00300-024-03246-9): The original solitary-nest dataset already reports four nascent subcolonies around formerly solitary sites, including two without active solitary breeding the prior year. Our 2022 adjacent-neighbor sites are a spatial-unit audit, not a discovery of such founder-independent group emergence.
- **Dugger et al. 2026** (doi:10.3389/fevo.2026.1868960): Twenty-five years of known-age Ross Island mark–resights (Royds/Bird/Crozier) already quantify age-specific survival, recruitment, breeding propensity and between-colony movement. Some 5–7-year-old Royds pre-breeders prospect at Bird with probabilities 8–12%, whereas established breeders move between colonies under 0.20%. The paper also discusses complete reproductive failure in three of five Cape Royds iceberg years leaving some birth cohorts absent and multiyear population recovery. Generic pre-breeder dispersal versus breeder fidelity and delayed cohort debt are not novel mechanisms.

## A source identity check that may unblock the frozen PR142 access route

USAP-DC 601444 (doi:10.15784/601444) officially lists a 25.1MB file named band_resighting_1997-2021.csv, with public MD5 **aaae6ddad6d12081b5a68466794438a2**. The direct official portal requires reCAPTCHA, and PR142's official API schema gate has been blocked on an authentication requirement.

The 2023 publicly released original-author GitHub repository pointblue/solo_nests contains data/allresight_reference_copy.csv at frozen commit **04517cedac18950408abd4d0b510f4aae3447f05**. GitHub reports **25,121,923 bytes**, blob SHA **7dd043fb276ff8687a53f04f73719243c23268ec**. Filename similarity alone is not source identity.

The new source-only probe has:
- contracts/ROSS_PUBLIC_RESIGHT_MIRROR_MD5_SOURCE_IDENTITY_V1.json
- scripts/verify_ross_public_resight_mirror_md5_v1.py
- .github/workflows/ross-public-resight-byte-identity-v1.yml

It processes bytes as opaque input only, calculating byte count, MD5, SHA256 and Git blob SHA; it **does not read even the first CSV row or header, individual tag, or behavioral outcome**. A MATCH is a proposed exact-binary-source identity requiring independent review; it does NOT automatically unlock PR142 or modify any pre-registered model. A MISMATCH means stop. The 2026 demographic findings remain prior art even if source access is resolved.

## Scientific decision

No current source demonstrates novel causal island colonization, chick protection or recruitment debt. Simple social aggregation, young-penguin wandering and shock-driven missing cohorts are already reported. To claim a new mechanism would require independently timed exogenous habitat/social-cue/predation perturbations, tracked individual origins, first settlements and outcomes under appropriate controls. No inference is licensed from a source checksum. Frozen Ecology PR189 remains unchanged.

## Verified 2026-10-08 source integrity outcome

[Actual source-only GitHub Actions run #37794660804](https://github.com/zuizui0223/mina/actions/runs/37794660804) **completed successfully as a source validation workflow**, with scientifically negative identity result:

- Public pointblue 2023 author-candidate: **25,121,923 bytes** and **Git blob SHA matches** the author repository pin.
- Compared to USAP-DC 601444 documented official MD5 `aaae6ddad6d12081b5a68466794438a2`: **MD5 DOES NOT MATCH**.
- Source verdict: **HOLD_PUBLIC_COPY_NOT_BYTE_IDENTICAL_TO_OFFICIAL**.
- The code opened **no CSV header, no bird ID, no behavioral data rows**. PR142 remains **locked**; **do not silently use this author mirror as the official USAP-DC source**.
- The mismatch establishes binary nonidentity, not why the datasets differ. They might be different versions, filters, encodings or even distinct data exports; none is demonstrated from hashes alone. An account-specific USAP-DC download/API request remains the necessary path to the exact official file.

This source check closes the public mirror shortcut. It does not unfreeze preregistered hypotheses or create a new island ecological result.

