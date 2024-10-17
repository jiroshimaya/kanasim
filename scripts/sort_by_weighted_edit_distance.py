from kanasim import create_kana_distance_calculator


def load_wordlist(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines()


if __name__ == "__main__":
    import argparse
    import os

    default_kana2phonome_csv = os.path.join(
        os.path.dirname(__file__), "../src/kanasim/data/biphone/kana2phonome_bi.csv"
    )
    default_distance_vowels_csv = os.path.join(
        os.path.dirname(__file__), "../src/kanasim/data/biphone/distance_vowels_bi.csv"
    )
    default_distance_consonants_csv = os.path.join(
        os.path.dirname(__file__),
        "../src/kanasim/data/biphone/distance_consonants_bi.csv",
    )
    default_wordlist = os.path.join(
        os.path.dirname(__file__), "../data/sample/pronunciation.txt"
    )

    def parse_arguments():
        parser = argparse.ArgumentParser(
            description="Calculate weighted edit distance between two words."
        )
        parser.add_argument(
            "word", type=str, help="Word to be used as a query for similarity search"
        )
        parser.add_argument(
            "-w",
            "--wordlist",
            type=str,
            required=False,
            default=default_wordlist,
            help="Path to the word list file",
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
            "-v",
            "--distance_vowels",
            type=str,
            required=False,
            default=default_distance_vowels_csv,
            help="Path to the distance_vowels CSV file",
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
            help="Penalty for insertion, deletion or replacement of non-syllabic moras like ン and ッ",
        )
        parser.add_argument(
            "-n",
            "--topn",
            type=int,
            default=10,
            help="Number of top similar words to return",
        )
        parser.add_argument(
            "-dt",
            "--distance_type",
            type=str,
            default="levenshtein",
            help="Distance type (levenshtein or hamming)",
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
            help="Disable using the same phoneme distance as the offset for consonants and vowels",
        )
        parser.add_argument(
            "-vb",
            "--vowel_binary",
            action="store_true",
            help="Disable using the same phoneme distance as the offset for consonants and vowels",
        )
        return parser.parse_args()

    args = parse_arguments()
    word = args.word
    wordlist_path = args.wordlist
    kana2phonome_csv = args.kana2phonome
    distance_vowels_csv = args.distance_vowels
    distance_consonants_csv = args.distance_consonants

    weighted_levenshtein = create_kana_distance_calculator(
        kana2phonome_csv=kana2phonome_csv,
        distance_vowels_csv=distance_vowels_csv,
        distance_consonants_csv=distance_consonants_csv,
        insert_penalty=args.insert_penalty,
        delete_penalty=args.delete_penalty,
        replace_penalty=args.replace_penalty,
        vowel_ratio=args.vowel_ratio,
        non_syllabic_penalty=args.non_syllabic_penalty,
        distance_type=args.distance_type,
        consonant_binary=args.consonant_binary,
        vowel_binary=args.vowel_binary,
        same_phonome_offset=not args.disable_same_phonome_offset,
    )

    wordlist = load_wordlist(wordlist_path)
    distances = weighted_levenshtein.calculate_batch([word], wordlist)[0]
    wordlist_with_distance = [(row, distances[i]) for i, row in enumerate(wordlist)]
    sorted_wordlist = sorted(wordlist_with_distance, key=lambda x: x[1])
    for word, distance in sorted_wordlist[: args.topn]:
        print(word, distance)
