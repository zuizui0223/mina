import csv
import math

from mina.island_partition_overlap import analyze


ISLANDS = ("CHR", "COR", "HUM", "LIT", "TOR")


def _fixture(path):
    state = {
        (island, colony): 300.0 + 30 * colony
        for island in ISLANDS
        for colony in range(4)
    }
    with path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.writer(handle)
        w.writerow(
            ["study_name", "time", "island_name", "colony_code", "num_breeding_pairs"]
        )
        w.writerow(["", "UTC", "", "", "1"])
        for year in range(1991, 2018):
            if year > 1991:
                for ii, island in enumerate(ISLANDS):
                    island_shock = 0.12 * math.sin(0.5 * year + ii)
                    for colony in range(4):
                        idiosyncratic = 0.02 * math.sin(
                            0.9 * year + colony
                        )
                        state[(island, colony)] *= math.exp(
                            island_shock + idiosyncratic
                        )
            for island in ISLANDS:
                for colony in range(4):
                    # Administrative-looking start/stop patterns are retained,
                    # not imputed as zero.
                    if island == "CHR" and colony == 3 and year >= 2007:
                        continue
                    if island == "TOR" and colony == 2 and year == 2014:
                        continue
                    w.writerow(
                        [
                            f"PAL{year}",
                            f"{year}-11-15T00:00:00Z",
                            island,
                            str(colony + 1),
                            round(state[(island, colony)]),
                        ]
                    )
        # Never-positive administrative code: must not enter the analysis.
        for year in range(2007, 2018):
            w.writerow(
                [
                    f"PAL{year}",
                    f"{year}-11-15T00:00:00Z",
                    "CHR",
                    "99",
                    0,
                ]
            )


def test_overlap_partition_handles_code_start_stop(tmp_path):
    p = tmp_path / "c.csv"
    _fixture(p)
    result = analyze(p, n_permutations=500, seed=11)
    assert result["validity_pass"] is True
    assert "99" not in result["included_codes"]["CHR"]
    assert result["decision"]["island_partition_supported"] is True
    assert result["observed"]["partition_contrast_r"] > 0


def test_overlap_estimator_uses_information_weights(tmp_path):
    p = tmp_path / "c.csv"
    _fixture(p)
    result = analyze(p, n_permutations=99, seed=12)
    assert result["observed"]["within_information_weight"] > 0
    assert result["observed"]["between_information_weight"] > 0
    assert result["n_informative_pairs"] > 0
