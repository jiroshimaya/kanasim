from kanasim import extend_long_vowel_moras

import jamorasep
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_wordlist(path: str) -> list[str]:
    logging.debug(f"Loading wordlist from {path}")
    with open(path, "r", encoding="utf-8") as f:
        wordlist = f.read().splitlines()
    logging.debug(f"Loaded {len(wordlist)} words")
    return wordlist


def split_consonant_vowel(mora: str) -> tuple[str, str]:
    logging.debug(f"Splitting mora: {mora}")
    simpleipa = jamorasep.parse(mora, output_format="simple-ipa")[0]
    consonant, vowel = "".join(simpleipa[:-1]), simpleipa[-1]
    logging.debug(f"Consonant: {consonant}, Vowel: {vowel}")
    return consonant, vowel


def convert_to_vowels_and_consonants(
    moras: list[str],
) -> tuple[tuple[str, str], tuple[str, str]]:
    logging.debug(f"Converting moras to vowels and consonants: {moras}")
    vowels, consonants = [], []
    for mora in moras:
        consonant, vowel = split_consonant_vowel(mora)
        consonants.append(consonant)
        vowels.append(vowel)
    logging.debug(f"Consonants: {consonants}, Vowels: {vowels}")
    return consonants, vowels


def hamming_distance(str1: str, str2: str) -> int:
    logging.debug(f"Calculating Hamming distance between '{str1}' and '{str2}'")
    if len(str1) != len(str2):
        logging.debug("Strings have different lengths, returning infinity")
        return float("inf")
    distance = sum(el1 != el2 for el1, el2 in zip(str1, str2))
    logging.debug(f"Hamming distance: {distance}")
    return distance


if __name__ == "__main__":
    import argparse
    import os

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
            "-n",
            "--topn",
            type=int,
            default=10,
            help="Number of top similar words to return",
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
            "-cr",
            "--consonant_ratio",
            type=float,
            required=False,
            default=0.5,
            help="Ratio for consonants",
        )
        parser.add_argument(
            "-sr",
            "--surface_ratio",
            type=float,
            required=False,
            default=0.0,
            help="Ratio for surface",
        )
        return parser.parse_args()

    args = parse_arguments()
    logging.debug(f"Arguments: {args}")
    word = args.word
    wordlist_path = args.wordlist

    wordlist = load_wordlist(wordlist_path)
    surface_pronunciations = [
        extend_long_vowel_moras(pronunciation) for pronunciation in wordlist
    ]
    surface_word = extend_long_vowel_moras(word)
    logging.debug(f"Surface word: {surface_word}")
    filtered_wordlist = []
    filtered_surface_pronunciations = []
    for word, pronunciation in zip(wordlist, surface_pronunciations):
        if len(surface_word) == len(pronunciation):
            filtered_wordlist.append(word)
            filtered_surface_pronunciations.append(pronunciation)
    logging.debug(f"Filtered wordlist: {filtered_wordlist}")
    logging.debug(f"Filtered surface pronunciations: {filtered_surface_pronunciations}")

    consonant_pronunciations = []
    vowel_pronunciations = []
    for surface_pronunciation in filtered_surface_pronunciations:
        consonants, vowels = convert_to_vowels_and_consonants(surface_pronunciation)
        consonant_pronunciations.append(consonants)
        vowel_pronunciations.append(vowels)
    logging.debug(f"Consonant pronunciations: {consonant_pronunciations}")
    logging.debug(f"Vowel pronunciations: {vowel_pronunciations}")

    surface_distances = [
        hamming_distance(surface_word, pronunciation)
        for pronunciation in filtered_surface_pronunciations
    ]
    logging.debug(f"Surface distances: {surface_distances}")
    consonant_word, vowel_word = convert_to_vowels_and_consonants(surface_word)
    consonant_distances = [
        hamming_distance(consonant_word, pronunciation)
        for pronunciation in consonant_pronunciations
    ]
    logging.debug(f"Consonant distances: {consonant_distances}")
    vowel_distances = [
        hamming_distance(vowel_word, pronunciation)
        for pronunciation in vowel_pronunciations
    ]
    logging.debug(f"Vowel distances: {vowel_distances}")
    distances = []
    for surface_distance, consonant_distance, vowel_distance in zip(
        surface_distances, consonant_distances, vowel_distances
    ):
        distance = (
            surface_distance * args.surface_ratio
            + consonant_distance * args.consonant_ratio
            + vowel_distance * args.vowel_ratio
        )
        distances.append(distance)
    logging.debug(f"Combined distances: {distances}")
    wordlist_with_distance = [
        (row, distances[i]) for i, row in enumerate(filtered_wordlist)
    ]
    sorted_wordlist = sorted(wordlist_with_distance, key=lambda x: x[1])
    logging.debug(f"Sorted wordlist: {sorted_wordlist}")
    for word, distance in sorted_wordlist[: args.topn]:
        print(word, distance)
