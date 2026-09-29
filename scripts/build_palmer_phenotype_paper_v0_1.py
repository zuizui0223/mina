#!/usr/bin/env python3
"""Build Palmer phenotype-reassembly manuscript v0.1 and figure-data tables."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results" / "PALMER_PHENOTYPE_REASSEMBLY_RESULT_V1.json"


def _read_result() -> dict[str, object]:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    if value.get("result_id") != "mina-palmer-phenotype-reassembly-result-v1":
        raise ValueError("unexpected Palmer phenotype result")
    return value


def _words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def figure_rows(result: dict[str, object]) -> dict[str, list[dict[str, object]]]:
    assemblage = result["assemblage_scale"]
    existing = result["within_adelie_existing"]
    structural = result["structural_morphology_persistence"]
    isotopes = result["isotopic_niche_sensitivity"]

    fig1 = [
        {
            "contrast": "morphology_vs_pooled",
            "gain": assemblage["naive_pooled_morphology_gain"],
            "ecological_role": "apparent assemblage island phenotype",
        },
        {
            "contrast": "species_vs_pooled",
            "gain": assemblage["species_layer_gain"],
            "ecological_role": "species sorting component",
        },
        {
            "contrast": "morphology_beyond_species",
            "gain": assemblage["species_conditioned_morphology_gain"],
            "ecological_role": "within-species morphology beyond composition",
        },
    ]

    labels = {
        "bill_length": "Bill length",
        "bill_depth": "Bill depth",
        "flipper_length": "Flipper length",
    }
    fig2 = []
    for trait in ("bill_length", "bill_depth", "flipper_length"):
        reversed_text = existing["pairwise_island_sign_reversals"][trait]
        reversed_count, pair_count = (int(value) for value in reversed_text.split("/"))
        fig2.append(
            {
                "trait": labels[trait],
                "fixed_island_partial_r2": existing["fixed_island_partial_r2"][trait],
                "island_by_year_partial_r2": existing[
                    "island_by_year_partial_r2_given_main"
                ][trait],
                "reversed_pair_count": reversed_count,
                "pair_count": pair_count,
                "reversed_pair_fraction": reversed_count / pair_count,
            }
        )

    fig3: list[dict[str, object]] = []
    for domain, payload in (
        ("structural_morphology", structural),
        ("isotopic_niche", isotopes),
    ):
        for year, value in payload["within_year_balanced_accuracy"].items():
            fig3.append(
                {
                    "domain": domain,
                    "validation": "within_year_leave_one_out",
                    "year": year,
                    "balanced_accuracy": value,
                    "chance_reference": payload["chance_balanced_accuracy"],
                }
            )
        for year, value in payload["cross_year_balanced_accuracy"].items():
            fig3.append(
                {
                    "domain": domain,
                    "validation": "leave_one_year_out",
                    "year": year,
                    "balanced_accuracy": value,
                    "chance_reference": payload["chance_balanced_accuracy"],
                }
            )

    return {
        "figure1_assemblage_decomposition.csv": fig1,
        "figure2_within_adelie_reassembly.csv": fig2,
        "figure3_temporal_persistence.csv": fig3,
    }


def manuscript_text(result: dict[str, object]) -> str:
    assemblage = result["assemblage_scale"]
    existing = result["within_adelie_existing"]
    structural = result["structural_morphology_persistence"]
    isotopes = result["isotopic_niche_sensitivity"]

    text = f"""# Species sorting creates transient island phenotypes in Palmer penguins

**Draft:** ecological short paper v0.1  
**Repository lane:** Palmer phenotype reassembly

## Abstract

Functional differences among island communities can arise through species sorting or through persistent phenotypic differentiation within species, but snapshot data often confound these processes. We used the Palmer Penguins data set from three neighboring West Antarctic Peninsula breeding sites to separate assemblage composition from within-species temporal persistence. Across the full Pygoscelis assemblage, morphology predicted breeding-site identity relative to a pooled site distribution (held-out log-score gain {assemblage['naive_pooled_morphology_gain']:+.3f}), but species identity carried a larger gain ({assemblage['species_layer_gain']:+.3f}) and morphology contributed negatively after species identity was already known ({assemblage['species_conditioned_morphology_gain']:+.3f}). Restricting the analysis to Adélie penguins weakened fixed island effects: structural-trait partial R² values were {existing['fixed_island_partial_r2']['bill_length']:.3f}–{existing['fixed_island_partial_r2']['flipper_length']:.3f}, and pairwise island contrasts reversed among years for 3/3 bill-length pairs, 3/3 bill-depth pairs and 2/3 flipper-length pairs. Structural morphology still contained modest island information within individual breeding seasons (mean balanced accuracy {structural['mean_within_year_balanced_accuracy']:.3f}), but leave-one-year-out transfer fell to {structural['mean_cross_year_balanced_accuracy']:.3f}, close to the three-island chance reference of {structural['chance_balanced_accuracy']:.3f}. Isotopic niche space showed little persistence contrast ({isotopes['mean_within_year_balanced_accuracy']:.3f} within-year versus {isotopes['mean_cross_year_balanced_accuracy']:.3f} across years). These results indicate that the conspicuous Palmer island phenotype is mainly compositional, while the residual within-Adélie spatial signal is temporally reassembled rather than a stable island-specific phenotype.

**Keywords:** Adélie penguin; community assembly; functional differentiation; island ecology; species sorting; temporal turnover

## 1. Introduction

Functional differentiation among islands is often interpreted as evidence that local environments generate distinct resident phenotypes. That interpretation is not unique. Island communities can also differ because species with different traits occupy different sites, and within-species differences observed in a single season may be temporary products of cohort composition, condition, breeding phenology or nonrandom site use. Distinguishing persistent within-species differentiation from species sorting and temporal reassembly is therefore central to interpreting trait variation in island assemblages.

The Palmer Archipelago penguin system is useful for this problem because three neighboring breeding sites contain different mixtures of Pygoscelis species while Adélie penguins occur across all three sites in the Palmer Penguins data set [@gorman2014]. Penguins are highly mobile marine foragers but breed on discrete terrestrial sites, so breeding-site identity can structure community assembly without isolating individuals from a shared regional marine environment. A strong breeding-site phenotype at the assemblage level may therefore reflect which species breed at a site rather than persistent morphological differentiation within one species.

An initial held-out audit showed exactly this ambiguity. Morphology strongly predicted breeding-site identity relative to a pooled site distribution, yet species identity carried still more predictive information, and the incremental morphology signal became negative once species identity was known. Here we treat that result as ecological provenance rather than a methodological endpoint. We ask whether a persistent island phenotype remains after restricting the analysis to Adélie penguins.

A persistent within-species island phenotype should satisfy two expectations. First, island identity should explain a nontrivial and relatively stable fraction of structural-trait variation after sex and annual covariates are controlled. Second, an island phenotype learned in one or two breeding seasons should transfer to a different year. A temporally reassembled phenotype instead predicts weak fixed island effects, frequent reversals in island trait contrasts, and a gap between same-year spatial discrimination and cross-year transfer. We tested these alternatives with a frozen post-outcome extension using structural morphology as the primary trait set and blood stable isotopes as a secondary sensitivity.

## 2. Methods

### 2.1 Data and ecological hierarchy

We used the pinned Palmer Penguins raw table underlying the public Palmer Penguins data set [@gorman2014]. The assemblage-scale context included Adélie, chinstrap and gentoo penguins. The within-species analysis retained Adélie penguins from Biscoe, Dream and Torgersen over three breeding seasons (PAL0708, PAL0809 and PAL0910).

The ecological hierarchy was fixed before the persistence extension was executed: assemblage-scale site differentiation, fixed within-Adélie island effects, island-by-year reassembly and temporal transfer. Body mass was treated separately because it is strongly condition-sensitive. Blood δ15N and δ13C were retained only as a secondary niche-space sensitivity because blood isotope values integrate pre-breeding foraging rather than strictly local summer island use.

### 2.2 Assemblage-scale compositional context

The frozen assemblage audit compared held-out breeding-site log predictive probability under three information contrasts. Morphology relative to a pooled breeding-site distribution quantified the apparent island phenotype. Species identity relative to the same pooled distribution quantified compositional information. Morphology beyond a species-conditioned breeding-site distribution quantified whether morphology added site information after species identity was already known.

These contrasts are used here only to locate the ecological source of assemblage-scale site differentiation. No methods novelty is claimed.

### 2.3 Fixed and time-varying within-Adélie island effects

For each trait, linear models controlled sex, breeding season, egg date and clutch completion. We compared the baseline model with a fixed-island model and then with an island-by-year interaction model. Effect sizes are reported as partial R² and AICc contrasts. Our primary interpretation emphasizes effect magnitude and temporal consistency rather than null-hypothesis significance.

We separately calculated equal-sex island means within each breeding season and recorded whether pairwise island contrasts changed sign among the three years. Repeated sign reversal is inconsistent with a simple fixed ranking of island phenotypes over the observed interval.

### 2.4 Same-year versus cross-year island classification

The persistence extension was frozen before execution. Structural morphology comprised bill length, bill depth and flipper length. For every training set, traits were centered by training-set sex means and scaled using training-set residual standard deviations. Island centroids were then calculated in standardized trait space and individuals were assigned to the nearest centroid.

Same-year spatial information was measured by leave-one-individual-out classification separately within each breeding season. Cross-year persistence used leave-one-year-out classification: centering, scaling and island centroids were estimated only from the two training years, and the held-out year was not used in preprocessing. Balanced accuracy across the three islands was the common metric; the equal-class reference is 1/3.

The secondary isotope analysis repeated the same procedure with δ15N and δ13C. No alternate classifier, distance metric, trait subset or year grouping was allowed after the result was opened.

## 3. Results

### 3.1 Assemblage-level island differentiation was dominated by species composition

Morphology predicted breeding-site identity relative to a pooled site marginal, with a mean held-out log-score gain of {assemblage['naive_pooled_morphology_gain']:+.5f}. Species identity alone carried a larger gain ({assemblage['species_layer_gain']:+.5f}). Once species identity was included in the reference, the morphology increment was negative ({assemblage['species_conditioned_morphology_gain']:+.5f}).

The conspicuous assemblage-level island phenotype was therefore primarily compositional: who occupied the breeding site carried more information than morphology beyond species identity.

### 3.2 Fixed within-Adélie island effects were small and contrasts were unstable

After sex, year, egg date and clutch completion were controlled, fixed island identity explained {existing['fixed_island_partial_r2']['bill_length']:.3f} of residual bill-length variance, {existing['fixed_island_partial_r2']['bill_depth']:.3f} of bill-depth variance and {existing['fixed_island_partial_r2']['flipper_length']:.3f} of flipper-length variance.

Island-by-year structure was at least as large as the fixed island component for bill length and bill depth and was similar in magnitude for flipper length. More importantly, pairwise island rankings were not stable: all three island pairs reversed sign for bill length and bill depth, and two of three pairs reversed for flipper length.

### 3.3 Structural morphology distinguished islands within years but not across years

Same-year leave-one-individual-out balanced accuracy averaged {structural['mean_within_year_balanced_accuracy']:.3f}. Year-specific values were {structural['within_year_balanced_accuracy']['PAL0708']:.3f}, {structural['within_year_balanced_accuracy']['PAL0809']:.3f} and {structural['within_year_balanced_accuracy']['PAL0910']:.3f}.

When an entire breeding season was held out, mean balanced accuracy fell to {structural['mean_cross_year_balanced_accuracy']:.3f}, only {structural['mean_cross_year_balanced_accuracy'] - structural['chance_balanced_accuracy']:+.3f} above the three-island chance reference. The persistence gap between same-year and cross-year classification was {structural['persistence_gap']:.3f} balanced-accuracy units.

Thus, structural morphology contained modest spatial information within a breeding season, but almost none of that spatial signature persisted when transferred to another year.

### 3.4 Isotopic niche space showed little evidence of persistent island identity

The isotope sensitivity was weak at both temporal scales. Same-year balanced accuracy averaged {isotopes['mean_within_year_balanced_accuracy']:.3f}, while leave-one-year-out accuracy averaged {isotopes['mean_cross_year_balanced_accuracy']:.3f}. The persistence gap was only {isotopes['persistence_gap']:.3f}.

Because these blood isotope measurements integrate pre-breeding foraging, we do not interpret this result as a test of local summer island foraging. It provides only a secondary indication that a stable island signature is not rescued in isotope space.

## 4. Discussion

The Palmer breeding-site phenotype is hierarchical rather than fixed. At the full-assemblage scale, breeding sites differ strongly because different penguin species with different morphologies occupy them. After species turnover is removed by restricting the analysis to Adélie penguins, fixed island effects are small and the remaining spatial structure is temporally unstable. Morphology distinguishes islands better within a single breeding season than across seasons, and pairwise trait rankings repeatedly reverse through time.

This combination supports a species-sorting and temporal-reassembly interpretation. The largest functional differences among breeding sites arise from community composition. Within Adélie penguins, the island signal appears to be rebuilt among years rather than expressed as a persistent site-specific phenotype over the sampled period. A single-season snapshot could therefore overstate the stability of functional differentiation among islands.

The result does not imply that breeding-site environments are biologically unimportant. Same-year classification remained above the equal-class reference, demonstrating real spatial structure within seasons. Annual differences in age composition, breeder condition, timing, nonrandom settlement or unmeasured environmental state could all generate such structure. The present data cannot distinguish these mechanisms because the same individuals were not followed across years and no causal habitat manipulation was available.

Nor does the result reject local adaptation in general. Three breeding seasons are too short to evaluate evolutionary differentiation, and weak cross-year transfer over this interval does not preclude longer-term genetic or developmental structure. Our inference is narrower: the available Palmer phenotype does not behave like a stable island-specific trait signature over the observed three-year window.

The broader island-ecology implication concerns functional biogeography of mobile consumers. Functional differences among islands can be generated by species sorting even when within-species differentiation is weak, and transient within-species structure can further exaggerate snapshot contrasts. For marine central-place foragers, asking which species breed on a terrestrial patch may therefore be more informative for island functional differentiation than assuming that persistent phenotypic divergence has evolved among neighboring breeding sites.

Temporal replication changes the ecological conclusion. The same data that suggest detectable island phenotype within a season show almost no temporal transfer of that phenotype. Repeated sampling is therefore necessary to distinguish persistent island differentiation from annually reassembled population structure.

## 5. Boundaries

This study does not identify local adaptation, individual plasticity, or a causal snow, habitat, competition or foraging mechanism. Body mass is not used as a primary persistence trait. Blood isotope results are secondary because they integrate pre-breeding foraging. The three-island, three-year result is not presented as a general law of island biogeography.

The long-term Palmer colony-network paper and Antarctic-wide macroecology programme remain separate mina products.
"""
    return text


def build(out_dir: Path) -> dict[str, object]:
    result = _read_result()
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = figure_rows(result)
    for name, table in rows.items():
        _write_csv(out_dir / name, table)

    manuscript = manuscript_text(result)
    manuscript_path = out_dir / "PALMER_PHENOTYPE_REASSEMBLY_MANUSCRIPT_V0_1.md"
    manuscript_path.write_text(manuscript, encoding="utf-8")

    abstract = manuscript.split("## Abstract", 1)[1].split("**Keywords:**", 1)[0]
    manifest = {
        "schema_version": 1,
        "build_id": "palmer-phenotype-reassembly-paper-v0-1",
        "source_result": RESULT.name,
        "source_result_id": result["result_id"],
        "manuscript_word_count": _words(manuscript),
        "abstract_word_count": _words(abstract),
        "figure_data_files": sorted(rows),
        "paper1_ecosphere_modified": False,
        "paper2_macroecology_modified": False,
        "method_paper_positioning": False,
    }
    (out_dir / "PALMER_PHENOTYPE_REASSEMBLY_BUILD_MANIFEST_V0_1.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    manifest = build(args.out_dir)
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
