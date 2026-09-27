import csv
import math

from mina.island_partition_loio import analyze

ISLANDS = ("CHR", "COR", "HUM", "LIT", "TOR")


def _fixture(path):
    state = {
        (island, colony): 300.0 + 20.0 * colony
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
                    shock = 0.10 * math.sin(0.45 * year + ii)
                    for colony in range(4):
                        noise = 0.015 * math.sin(0.8 * year + colony)
                        state[(island, colony)] *= math.exp(shock + noise)
            for island in ISLANDS:
                for colony in range(4):
                    w.writerow(
                        [
                            f"PAL{year}",
                            f"{year}-11-15T00:00:00Z",
                            island,
                            str(colony + 1),
                            round(state[(island, colony)]),
                        ]
                    )


def test_loio_preserves_distributed_synthetic_partition(tmp_path):
    p = tmp_path / "c.csv"
    _fixture(p)
    result = analyze(p, n_permutations=300, base_seed=21)
    assert result["decision"]["directional_robustness"] is True
    assert all(
        result["results"][island]["observed"]["partition_contrast_r"] > 0
        for island in ISLANDS
    )
