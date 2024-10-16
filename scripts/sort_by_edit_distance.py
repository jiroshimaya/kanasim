import editdistance as ed
from kanasim import extend_long_vowel_moras

import jamorasep
def load_wordlist(path: str) -> list[str]:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().splitlines()
def split_consonant_vowel(mora: str) -> tuple[str, str]:
    simpleipa = jamorasep.parse(mora, output_format='simple-ipa')[0]
    consonant, vowel = "".join(simpleipa[:-1]), simpleipa[-1]
    return consonant, vowel
def convert_to_vowels_and_consonants(moras: list[str]) -> tuple[tuple[str, str], tuple[str, str]]:
    vowels, consonants = [], []
    for mora in moras:
        consonant, vowel = split_consonant_vowel(mora)
        consonants.append(consonant)
        vowels.append(vowel)
    return consonants, vowels

if __name__ == "__main__":
    import argparse
    import os
    
    default_wordlist = os.path.join(os.path.dirname(__file__), "../data/sample/pronunciation.txt")

    def parse_arguments():
        parser = argparse.ArgumentParser(description='Calculate weighted edit distance between two words.')
        parser.add_argument('word', type=str, help='Word to be used as a query for similarity search')
        parser.add_argument('-w', '--wordlist', type=str, required=False, default=default_wordlist, help='Path to the word list file')
        parser.add_argument('-n', '--topn', type=int, default=10, help='Number of top similar words to return')
        parser.add_argument('-vr', '--vowel_ratio', type=float, required=False, default=0.5, help='Ratio for vowels')
        return parser.parse_args()

    args = parse_arguments()
    word = args.word
    wordlist_path = args.wordlist

    wordlist = load_wordlist(wordlist_path)
    pronunciations = [extend_long_vowel_moras(pronunciation) for pronunciation in wordlist]
    consonant_pronunciations = []
    vowel_pronunciations = []
    for pronunciation in pronunciations:
        consonants, vowels = convert_to_vowels_and_consonants(pronunciation)
        consonant_pronunciations.append(consonants)
        vowel_pronunciations.append(vowels)
    
    consonant_word, vowel_word = convert_to_vowels_and_consonants(word)
    consonant_distances = [ed.eval(consonant_word, pronunciation) for pronunciation in consonant_pronunciations]
    vowel_distances = [ed.eval(vowel_word, pronunciation) for pronunciation in vowel_pronunciations]
    distances = []
    for consonant_distance, vowel_distance in zip(consonant_distances, vowel_distances):
        distances.append(consonant_distance * (1 - args.vowel_ratio) + vowel_distance * args.vowel_ratio)
    wordlist_with_distance = [(row, distances[i]) for i, row in enumerate(wordlist)]
    sorted_wordlist = sorted(wordlist_with_distance, key=lambda x: x[1])    
    for word, distance in sorted_wordlist[:args.topn]:
        print(word, distance)
    