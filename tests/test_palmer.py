import csv

from mina.palmer import analyze


HEADER = [
    "studyName",
    "Species",
    "Island",
    "Clutch Completion",
    "Date Egg",
    "Culmen Length (mm)",
    "Culmen Depth (mm)",
    "Flipper Length (mm)",
    "Body Mass (g)",
    "Sex",
    "Delta 15 N (o/oo)",
    "Delta 13 C (o/oo)",
]


def test_synthetic_palmer_analysis_runs(tmp_path):
    path = tmp_path / "raw.csv"
    years = [("PAL0708", 2007), ("PAL0809", 2008), ("PAL0910", 2009)]
    islands = ["Biscoe", "Dream", "Torgersen"]
    rows = []
    for yi, (study, year) in enumerate(years):
        for ii, island in enumerate(islands):
            for sexi, sex in enumerate(["FEMALE", "MALE"]):
                for rep in range(3):
                    # Interaction and replicate terms prevent a perfect linear fit.
                    shift = (ii - 1) * (yi - 1) * 0.7 + rep * 0.11
                    rows.append(
                        [
                            study,
                            "Adelie Penguin (Pygoscelis adeliae)",
                            island,
                            "Yes" if rep != 2 else "No",
                            f"{year}-11-{10 + rep + ii:02d}",
                            38 + sexi * 3 + yi * 0.2 + ii * 0.1 + shift,
                            18 + sexi * 1.2 - yi * 0.1 + ii * 0.05 + shift * 0.3,
                            188 + sexi * 5 + yi + ii * 0.4 + shift,
                            3500 + sexi * 700 + yi * 40 + ii * 20 + shift * 50,
                            sex,
                            8.5 + yi * 0.2 + ii * 0.05 + shift * 0.08,
                            -26 + yi * 0.15 - ii * 0.04 + shift * 0.05,
                        ]
                    )
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        writer.writerows(rows)

    result = analyze(path)
    assert result["scope"]["adelie_rows_raw"] == 54
    assert set(result["outcome_models"]) == {
        "Culmen Length (mm)",
        "Culmen Depth (mm)",
        "Flipper Length (mm)",
        "Body Mass (g)",
        "Delta 15 N (o/oo)",
        "Delta 13 C (o/oo)",
    }
    assert len(result["cross_year_transfer"]["structural_morphology"]["folds"]) == 3
