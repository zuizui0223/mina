"""Temporal persistence of within-Adelie Palmer island phenotype."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

from .palmer import ISLANDS, ISOTOPES, STRUCTURAL, YEARS, _finite, load_rows


@dataclass(frozen=True)
class ClassificationSummary:
    n_complete: int
    features: tuple[str, ...]
    chance_balanced_accuracy: float
    within_year_folds: tuple[dict[str, object], ...]
    cross_year_folds: tuple[dict[str, object], ...]
    mean_within_year_balanced_accuracy: float
    mean_cross_year_balanced_accuracy: float
    persistence_gap: float

    def as_dict(self) -> dict[str, object]:
        return {
            "n_complete": self.n_complete,
            "features": list(self.features),
            "chance_balanced_accuracy": self.chance_balanced_accuracy,
            "within_year_folds": list(self.within_year_folds),
            "cross_year_folds": list(self.cross_year_folds),
            "mean_within_year_balanced_accuracy": self.mean_within_year_balanced_accuracy,
            "mean_cross_year_balanced_accuracy": self.mean_cross_year_balanced_accuracy,
            "persistence_gap": self.persistence_gap,
        }


def _complete_rows(
    rows: Iterable[dict[str, str]],
    features: tuple[str, ...],
) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("Sex") in {"MALE", "FEMALE"}
        and row.get("Island") in ISLANDS
        and row.get("studyName") in YEARS
        and all(_finite(row.get(feature)) for feature in features)
    ]


def _fit_transform(
    train: list[dict[str, str]],
    test: list[dict[str, str]],
    features: tuple[str, ...],
) -> tuple[np.ndarray, np.ndarray, tuple[str, ...]]:
    if not train or not test:
        raise ValueError("train and test must be non-empty")

    sexes = ("FEMALE", "MALE")
    sex_means: dict[str, np.ndarray] = {}
    for sex in sexes:
        local = [row for row in train if row["Sex"] == sex]
        if not local:
            raise ValueError(f"training fold lacks sex {sex}")
        sex_means[sex] = np.asarray(
            [
                np.mean([float(row[feature]) for row in local])
                for feature in features
            ],
            dtype=float,
        )

    def residual(row: dict[str, str]) -> np.ndarray:
        observed = np.asarray(
            [float(row[feature]) for feature in features],
            dtype=float,
        )
        return observed - sex_means[row["Sex"]]

    train_residual = np.vstack([residual(row) for row in train])
    scale = np.std(train_residual, axis=0, ddof=1)
    if np.any(~np.isfinite(scale)) or np.any(scale <= 0.0):
        raise ValueError("training fold has invalid residual scale")

    train_z = train_residual / scale
    test_z = np.vstack([residual(row) / scale for row in test])
    return train_z, test_z, tuple(row["Island"] for row in train)


def _centroids(
    train_z: np.ndarray,
    train_islands: tuple[str, ...],
) -> dict[str, np.ndarray]:
    result: dict[str, np.ndarray] = {}
    labels = np.asarray(train_islands, dtype=object)
    for island in ISLANDS:
        mask = labels == island
        if not np.any(mask):
            raise ValueError(f"training fold lacks island {island}")
        result[island] = np.mean(train_z[mask], axis=0)
    return result


def _predict(
    test_z: np.ndarray,
    centroids: dict[str, np.ndarray],
) -> list[str]:
    predictions: list[str] = []
    for point in test_z:
        predictions.append(
            min(
                ISLANDS,
                key=lambda island: float(
                    np.sum((point - centroids[island]) ** 2)
                ),
            )
        )
    return predictions


def _balanced_accuracy(
    truth: list[str],
    predictions: list[str],
) -> tuple[float, dict[str, dict[str, float | int]]]:
    recalls: list[float] = []
    detail: dict[str, dict[str, float | int]] = {}
    for island in ISLANDS:
        indices = [index for index, value in enumerate(truth) if value == island]
        if not indices:
            raise ValueError(f"test fold lacks island {island}")
        correct = sum(predictions[index] == island for index in indices)
        recall = correct / len(indices)
        recalls.append(recall)
        detail[island] = {
            "correct": correct,
            "n": len(indices),
            "recall": recall,
        }
    return float(np.mean(recalls)), detail


def within_year_leave_one_out(
    rows: list[dict[str, str]],
    features: tuple[str, ...],
) -> tuple[dict[str, object], ...]:
    complete = _complete_rows(rows, features)
    folds: list[dict[str, object]] = []

    for year in YEARS:
        local = [row for row in complete if row["studyName"] == year]
        truth: list[str] = []
        predictions: list[str] = []

        for heldout_index, heldout in enumerate(local):
            train = [
                row for index, row in enumerate(local)
                if index != heldout_index
            ]
            train_z, test_z, train_islands = _fit_transform(
                train,
                [heldout],
                features,
            )
            centroids = _centroids(train_z, train_islands)
            pred = _predict(test_z, centroids)[0]
            truth.append(heldout["Island"])
            predictions.append(pred)

        balanced, detail = _balanced_accuracy(truth, predictions)
        folds.append(
            {
                "year": year,
                "n": len(local),
                "balanced_accuracy": balanced,
                "per_island": detail,
            }
        )
    return tuple(folds)


def leave_one_year_out(
    rows: list[dict[str, str]],
    features: tuple[str, ...],
) -> tuple[dict[str, object], ...]:
    complete = _complete_rows(rows, features)
    folds: list[dict[str, object]] = []

    for heldout_year in YEARS:
        train = [
            row for row in complete
            if row["studyName"] != heldout_year
        ]
        test = [
            row for row in complete
            if row["studyName"] == heldout_year
        ]
        train_z, test_z, train_islands = _fit_transform(
            train,
            test,
            features,
        )
        centroids = _centroids(train_z, train_islands)
        predictions = _predict(test_z, centroids)
        truth = [row["Island"] for row in test]
        balanced, detail = _balanced_accuracy(truth, predictions)
        folds.append(
            {
                "heldout_year": heldout_year,
                "n": len(test),
                "balanced_accuracy": balanced,
                "per_island": detail,
            }
        )
    return tuple(folds)


def persistence_summary(
    rows: list[dict[str, str]],
    features: tuple[str, ...],
) -> ClassificationSummary:
    complete = _complete_rows(rows, features)
    within = within_year_leave_one_out(complete, features)
    cross = leave_one_year_out(complete, features)
    within_mean = float(
        np.mean([float(row["balanced_accuracy"]) for row in within])
    )
    cross_mean = float(
        np.mean([float(row["balanced_accuracy"]) for row in cross])
    )
    return ClassificationSummary(
        n_complete=len(complete),
        features=features,
        chance_balanced_accuracy=1.0 / len(ISLANDS),
        within_year_folds=within,
        cross_year_folds=cross,
        mean_within_year_balanced_accuracy=within_mean,
        mean_cross_year_balanced_accuracy=cross_mean,
        persistence_gap=within_mean - cross_mean,
    )


def analyze_persistence(raw_csv: str | Path) -> dict[str, object]:
    rows = load_rows(raw_csv)
    return {
        "schema_version": 1,
        "analysis_id": "mina-palmer-phenotype-temporal-persistence-v1",
        "status": "post_outcome_extension",
        "structural_morphology": persistence_summary(
            rows,
            STRUCTURAL,
        ).as_dict(),
        "isotopic_niche": persistence_summary(
            rows,
            ISOTOPES,
        ).as_dict(),
        "interpretation_boundary": {
            "structural_morphology_is_primary": True,
            "isotopic_niche_is_secondary": True,
            "body_mass_excluded_from_primary_transfer_test": True,
            "no_local_adaptation_claim": True,
            "no_individual_plasticity_claim": True,
            "no_causal_island_mechanism_claim": True,
        },
    }
