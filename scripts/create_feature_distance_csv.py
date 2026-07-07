"""Derive a consonant distance table from distinctive phonological features.

Following the approach used in rap-rhyme analyses (e.g. Kawahara 2007,
"Half rhymes in Japanese rap lyrics and knowledge of similarity"), the
similarity between two consonants is measured by how many distinctive
features they share. The distance is the fraction of mismatched features
(0 = identical feature set, 1 = all features differ), so the table is
symmetric and already normalized to [0, 1].

The feature matrix lives in src/kanasim/data/features/consonant_features.csv
and can be edited (features added/removed/weighted) before regenerating.

"sp" (no consonant) is not describable by features; its distance to every
consonant is set to 1.0 (the maximum) and to itself 0.0.

Usage:
    uv run python scripts/create_feature_distance_csv.py
"""

import argparse
import csv
import os

DEFAULT_FEATURES_CSV = os.path.join(
    os.path.dirname(__file__), "../src/kanasim/data/features/consonant_features.csv"
)
DEFAULT_OUTPUT_CSV = os.path.join(
    os.path.dirname(__file__),
    "../src/kanasim/data/features/distance_consonants_mono_features.csv",
)


def load_features(path: str) -> dict[str, dict[str, str]]:
    features = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            consonant = row.pop("consonant")
            features[consonant] = row
    return features


def feature_distance(features1: dict[str, str], features2: dict[str, str]) -> float:
    mismatches = sum(features1[name] != features2[name] for name in features1)
    return mismatches / len(features1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-f", "--features_csv", default=DEFAULT_FEATURES_CSV)
    parser.add_argument("-o", "--output_csv", default=DEFAULT_OUTPUT_CSV)
    args = parser.parse_args()

    features = load_features(args.features_csv)
    consonants = [*features.keys(), "sp"]

    rows = []
    for c1 in consonants:
        for c2 in consonants:
            if c1 == c2:
                distance = 0.0
            elif c1 == "sp" or c2 == "sp":
                distance = 1.0
            else:
                distance = feature_distance(features[c1], features[c2])
            rows.append({"phonome1": c1, "phonome2": c2, "distance": distance})

    with open(args.output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["phonome1", "phonome2", "distance"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.output_csv}")
