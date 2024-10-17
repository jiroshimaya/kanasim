import argparse
import csv

from kanasim import create_kana_distance_list

if __name__ == "__main__":
    import os

    default_kana2phonome_csv = os.path.join(
        os.path.dirname(__file__), "../src/kanasim/data/biphone/kana2phonome_bi.csv"
    )
    default_distance_consonants_csv = os.path.join(
        os.path.dirname(__file__),
        "../src/kanasim/data/biphone/distance_consonants_bi.csv",
    )
    default_distance_vowels_csv = os.path.join(
        os.path.dirname(__file__), "../src/kanasim/data/biphone/distance_vowels_bi.csv"
    )
    default_output_csv = os.path.join(os.path.dirname(__file__), "kana_distance_bi.csv")

    def parse_arguments():
        parser = argparse.ArgumentParser(
            description="Process paths for kana2phonome, distance_consonants, and distance_vowels CSV files."
        )
        parser.add_argument(
            "-k",
            "--kana2phonome",
            type=str,
            required=False,
            default=default_kana2phonome_csv,
            help="Path to the kana2phonome CSV file",
        )
        parser.add_argument(
            "-c",
            "--distance_consonants",
            type=str,
            required=False,
            default=default_distance_consonants_csv,
            help="Path to the distance_consonants CSV file",
        )
        parser.add_argument(
            "-v",
            "--distance_vowels",
            type=str,
            required=False,
            default=default_distance_vowels_csv,
            help="Path to the distance_vowels CSV file",
        )
        parser.add_argument(
            "-o",
            "--output",
            type=str,
            required=False,
            default=default_output_csv,
            help="Path to the output CSV file",
        )
        parser.add_argument(
            "-ip",
            "--insert_penalty",
            type=float,
            required=False,
            default=1.0,
            help="Penalty for insertion",
        )
        parser.add_argument(
            "-dp",
            "--delete_penalty",
            type=float,
            required=False,
            default=1.0,
            help="Penalty for deletion",
        )
        parser.add_argument(
            "-rp",
            "--replace_penalty",
            type=float,
            required=False,
            default=1.0,
            help="Penalty for replacement",
        )
        parser.add_argument(
            "-vr",
            "--vowel_ratio",
            type=float,
            required=False,
            default=0.5,
            help="Ratio for vowels",
        )
        parser.add_argument(
            "-nsp",
            "--non_syllabic_penalty",
            type=float,
            required=False,
            default=1.0,
            help="Penalty for insertion, deletion or replacement of non syllabic phonemes like ン and ッ",
        )
        parser.add_argument(
            "-dspo",
            "--disable_same_phonome_offset",
            action="store_true",
            help="Disable using the same phoneme distance as the offset for consonants and vowels",
        )
        parser.add_argument(
            "-cb",
            "--consonant_binary",
            action="store_true",
            help="Use binary distance for consonants",
        )
        parser.add_argument(
            "-vb",
            "--vowel_binary",
            action="store_true",
            help="Use binary distance for vowels",
        )
        return parser.parse_args()

    args = parse_arguments()
    results = create_kana_distance_list(
        kana2phonome_csv=args.kana2phonome,
        distance_consonants_csv=args.distance_consonants,
        distance_vowels_csv=args.distance_vowels,
        insert_penalty=args.insert_penalty,
        delete_penalty=args.delete_penalty,
        replace_penalty=args.replace_penalty,
        vowel_ratio=args.vowel_ratio,
        non_syllabic_penalty=args.non_syllabic_penalty,
        same_phonome_offset=not args.disable_same_phonome_offset,
        consonant_binary=args.consonant_binary,
        vowel_binary=args.vowel_binary,
    )

    with open(args.output, "w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["kana1", "kana2", "distance"])
        writer.writeheader()
        writer.writerows(results)
