"""Derive monophone distance tables from the biphone distance tables.

The bundled biphone tables (e.g. "k+a" vs "k+i") mix the effect of the
neighboring vowel into consonant distances, which sometimes contradicts
intuition (the distance between "k+a" and "k+i" -- the same consonant --
is larger than between "k+a" and "t+a"). This script averages the biphone
distances over every pair that shares the same monophone pair, producing
tables keyed by monophone labels ("k", "t", ..., "a", "a:", "N", ...).

Usage:
    uv run python scripts/create_monophone_distance_csv.py
"""

import argparse
import csv
import os
from collections import defaultdict

DEFAULT_INPUT_DIR = os.path.join(
    os.path.dirname(__file__), "../src/kanasim/data/biphone"
)
DEFAULT_OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), "../src/kanasim/data/monophone"
)


def to_monophone(label: str, separator: str, index: int) -> str:
    return label.split(separator)[index]


def average_distances(
    input_csv: str, separator: str, index: int
) -> list[dict[str, str | float]]:
    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    with open(input_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (
                to_monophone(row["phonome1"], separator, index),
                to_monophone(row["phonome2"], separator, index),
            )
            groups[key].append(float(row["distance"]))
    return [
        {"phonome1": p1, "phonome2": p2, "distance": sum(values) / len(values)}
        for (p1, p2), values in sorted(groups.items())
    ]


def write_csv(rows: list[dict[str, str | float]], output_csv: str) -> None:
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["phonome1", "phonome2", "distance"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--input_dir", default=DEFAULT_INPUT_DIR)
    parser.add_argument("-o", "--output_dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    # consonant biphones are "consonant+vowel" (e.g. "k+a"); "sp" has no "+"
    consonants = average_distances(
        os.path.join(args.input_dir, "distance_consonants_bi.csv"), "+", 0
    )
    write_csv(
        consonants, os.path.join(args.output_dir, "distance_consonants_mono_avg.csv")
    )
    # vowel biphones are "consonant-vowel" (e.g. "b-a"); bare labels such as
    # "a", "N", "q", "sp" have no "-" and are kept as is
    vowels = average_distances(
        os.path.join(args.input_dir, "distance_vowels_bi.csv"), "-", -1
    )
    write_csv(vowels, os.path.join(args.output_dir, "distance_vowels_mono_avg.csv"))
    print(f"wrote {len(consonants)} consonant rows, {len(vowels)} vowel rows")
