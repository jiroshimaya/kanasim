import csv
from kanasim import WeightedLevenshtein, extend_long_vowel_moras


def load_csv(path: str) -> list[dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_distance_csv(path: str) -> dict[tuple[str, str], float]:
    distance_dict = {}
    distance_list = load_csv(path)
    for row in distance_list:
        kana1 = row["kana1"]
        kana2 = row["kana2"]
        distance = (
            float(row["distance"]) if "." in row["distance"] else int(row["distance"])
        )
        distance_dict[(kana1, kana2)] = distance
    return distance_dict


if __name__ == "__main__":
    import argparse

    def parse_arguments():
        parser = argparse.ArgumentParser(
            description="Calculate weighted edit distance between two words."
        )
        parser.add_argument("word1", type=str, help="The first word")
        parser.add_argument("word2", type=str, help="The second word")
        parser.add_argument(
            "-k",
            "--kana_distance_csv",
            type=str,
            required=False,
            help="Path to the kana distance CSV file",
        )
        return parser.parse_args()

    args = parse_arguments()
    word1 = args.word1
    word2 = args.word2
    kana_distance_csv = args.kana_distance_csv
    distance_dict = load_distance_csv(kana_distance_csv)

    def insert_cost_func(kana: str) -> int:
        return distance_dict[("sp", kana)]

    def delete_cost_func(kana: str) -> int:
        return distance_dict[(kana, "sp")]

    def replace_cost_func(kana1: str, kana2: str) -> int:
        return distance_dict[(kana1, kana2)]

    def preprocess_func(text: str) -> list[str]:
        return extend_long_vowel_moras(text)

    weighted_levenshtein = WeightedLevenshtein(
        insert_cost_func=insert_cost_func,
        delete_cost_func=delete_cost_func,
        replace_cost_func=replace_cost_func,
        preprocess_func=preprocess_func,
    )

    distance = weighted_levenshtein.calculate(word1, word2)
    print(distance)

    # You can now use word1, word2, and kana_distance_csv in your script
