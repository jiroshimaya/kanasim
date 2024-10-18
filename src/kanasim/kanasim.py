import csv
import os
from typing import Callable
# from typing import Callable, List, Tuple, Dict, Optional, Iterable, Hashable, Any


def load_csv(path: str) -> list[dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_kana_distance_csv(path: str) -> dict[tuple[str, str], float]:
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


def load_phonome_distance_csv(path: str) -> dict[tuple[str, str], float]:
    distance_dict = {}
    distance_list = load_csv(path)
    for row in distance_list:
        phonome1 = row["phonome1"]
        phonome2 = row["phonome2"]
        distance = float(row["distance"])
        distance_dict[(phonome1, phonome2)] = distance
    return distance_dict


def create_kana_distance_list(
    *,
    kana2phonome_csv: str,
    distance_consonants_csv: str,
    distance_vowels_csv: str,
    vowel_ratio: float,
    non_syllabic_penalty: float,
    insert_penalty: float,
    delete_penalty: float,
    replace_penalty: float,
    same_phonome_offset: bool,
    consonant_binary: bool,
    vowel_binary: bool,
) -> list[dict]:
    if not (0 <= vowel_ratio <= 1):
        raise ValueError("vowel_ratio must be between 0 and 1 inclusive")
    kana2phonome = load_csv(kana2phonome_csv)
    distance_consonants_raw = load_phonome_distance_csv(distance_consonants_csv)
    distance_vowels_raw = load_phonome_distance_csv(distance_vowels_csv)

    if consonant_binary:
        distance_consonants_raw = {
            phoneme: 0 if phoneme[0].split("+")[0] == phoneme[1].split("+")[0] else 1
            for phoneme in distance_consonants_raw
        }
    if vowel_binary:
        distance_vowels_raw = {
            phoneme: 0 if phoneme[0].split("-")[-1] == phoneme[1].split("-")[-1] else 1
            for phoneme in distance_vowels_raw
        }

    distance_consonants = {}
    distance_vowels = {}
    if same_phonome_offset:
        for phoneme1, phoneme2 in distance_consonants_raw.keys():
            offset = distance_consonants_raw[(phoneme1, phoneme1)]
            distance_consonants[(phoneme1, phoneme2)] = max(
                0, distance_consonants_raw[(phoneme1, phoneme2)] - offset
            )
        for phoneme1, phoneme2 in distance_vowels_raw.keys():
            offset = distance_vowels_raw[(phoneme1, phoneme1)]
            distance_vowels[(phoneme1, phoneme2)] = max(
                0, distance_vowels_raw[(phoneme1, phoneme2)] - offset
            )
    else:
        distance_consonants = distance_consonants_raw
        distance_vowels = distance_vowels_raw

    results = []
    for row1 in kana2phonome:
        for row2 in kana2phonome:
            kana1 = row1["kana"]
            kana2 = row2["kana"]
            consonant1 = row1["consonant"]
            consonant2 = row2["consonant"]
            vowel1 = row1["vowel"]
            vowel2 = row2["vowel"]

            distance_consonant = distance_consonants[(consonant1, consonant2)]
            distance_vowel = distance_vowels[(vowel1, vowel2)]

            distance = (
                distance_consonant * (1 - vowel_ratio) + distance_vowel * vowel_ratio
            )

            # non-syllabic insert, delete or replace penalty
            if row1["kana"] == "sp" and row2["kana"] == "sp":
                pass
            elif row1["kana"] in ["ン", "ッ", "sp"] and row2["kana"] in [
                "ン",
                "ッ",
                "sp",
            ]:
                distance *= non_syllabic_penalty
            # other insert penalty
            elif row1["kana"] == "sp" and row2["kana"] != "sp":
                distance *= insert_penalty
            # other delete penalty
            elif row1["kana"] != "sp" and row2["kana"] == "sp":
                distance *= delete_penalty
            # other replace penalty
            else:
                distance *= replace_penalty

            results.append({"kana1": kana1, "kana2": kana2, "distance": distance})

    return results


# Class to calculate weighted Levenshtein distance
class WeightedLevenshtein:
    """
    A class to calculate the weighted Levenshtein distance between two lists of strings.
    The distance is calculated based on the costs of insertion, deletion, and replacement operations.
    Custom cost functions and preprocessing functions can be provided to modify the behavior of the distance calculation.

    Attributes:
        insert_cost (float): The default cost of an insertion operation.
        delete_cost (float): The default cost of a deletion operation.
        replace_cost (float): The default cost of a replacement operation.
        insert_cost_func (Optional[Callable[[str], float]]): A custom function to calculate the cost of an insertion operation.
        delete_cost_func (Optional[Callable[[str], float]]): A custom function to calculate the cost of a deletion operation.
        replace_cost_func (Optional[Callable[[str, str], float]]): A custom function to calculate the cost of a replacement operation.
        preprocess_func (Optional[Callable[[str], List[str]]]): A custom function to preprocess the input lists before calculating the distance.
        memo (Dict[Tuple[Tuple[str, ...], Tuple[str, ...]], float]): A dictionary to store memoized results of distance calculations.
    """

    def __init__(
        self,
        insert_cost: float = 1.0,
        delete_cost: float = 1.0,
        replace_cost: float = 1.0,
        insert_cost_func: Callable[[str], float] | None = None,
        delete_cost_func: Callable[[str], float] | None = None,
        replace_cost_func: Callable[[str, str], float] | None = None,
        preprocess_func: Callable[[str], list[str]] | None = None,
    ):
        """
        Initializes the WeightedLevenshtein class with the given costs and custom functions.

        Args:
            insert_cost (float): The default cost of an insertion operation.
            delete_cost (float): The default cost of a deletion operation.
            replace_cost (float): The default cost of a replacement operation.
            insert_cost_func (Optional[Callable[[str], float]]): A custom function to calculate the cost of an insertion operation.
            delete_cost_func (Optional[Callable[[str], float]]): A custom function to calculate the cost of a deletion operation.
            replace_cost_func (Optional[Callable[[str, str], float]]): A custom function to calculate the cost of a replacement operation.
            preprocess_func (Optional[Callable[[str], List[str]]]): A custom function to preprocess the input lists before calculating the distance.
        """
        self.insert_cost = insert_cost
        self.delete_cost = delete_cost
        self.replace_cost = replace_cost
        self.insert_cost_func = insert_cost_func
        self.delete_cost_func = delete_cost_func
        self.replace_cost_func = replace_cost_func
        self.preprocess_func = preprocess_func
        self.memo: dict[tuple[str, str], float] = {}

    def calculate(self, word1: str, word2: str) -> float:
        if self.preprocess_func:
            word1 = self.preprocess_func(word1)
            word2 = self.preprocess_func(word2)
        return self._calculate(word1, word2)

    def calculate_batch(self, words1: list[str], words2: list[str]) -> list[float]:
        if self.preprocess_func:
            words1 = [self.preprocess_func(word1) for word1 in words1]
            words2 = [self.preprocess_func(word2) for word2 in words2]
        results = []
        for word1 in words1:
            result = []
            for word2 in words2:
                result.append(self._calculate(word1, word2))
            results.append(result)
        return results

    def get_topn(
        self, word: str, wordlist: list[str], n: int = 10
    ) -> list[tuple[str, float]]:
        """
        Get the top n similar lists from the given list.

        Args:
            word (str): The word to compare with.
            wordlist (list[str]): The list of words to compare.
            n (int): The number of similar words to get.

        Returns:
            List[Tuple[Hashable, float]]: The top n similar lists and their distances.
        """
        distances = self.calculate_batch([word], wordlist)[0]
        return sorted(zip(wordlist, distances), key=lambda x: x[1])[:n]

    def _calculate(self, word1: str, word2: str) -> float:
        """
        Calculates the weighted Levenshtein distance between two lists of strings.

        Args:
            word1 (str): The first word.
            word2 (str): The second word.

        Returns:
            float: The calculated weighted Levenshtein distance.
        """
        return self._calculate_helper(word1, word2, len(word1), len(word2))

    def _calculate_helper(self, word1: str, word2: str, m: int, n: int) -> float:
        """
        A helper function to recursively calculate the weighted Levenshtein distance between two lists of strings.

        Args:
            word1 (str): The first word.
            word2 (str): The second word.
            m (int): The length of the first word.
            n (int): The length of the second word.

        Returns:
            float: The calculated weighted Levenshtein distance.
        """
        # Check for memoized result
        if (tuple(word1[:m]), tuple(word2[:n])) in self.memo:
            return self.memo[(tuple(word1[:m]), tuple(word2[:n]))]

        # Base case
        if m == 0:
            cost = 0.0
            for i in range(n):
                cost += (
                    self.insert_cost_func(word2[i])
                    if self.insert_cost_func
                    else self.insert_cost
                )
            self.memo[(tuple(word1[:m]), tuple(word2[:n]))] = cost
            return cost
        if n == 0:
            cost = 0.0
            for i in range(m):
                cost += (
                    self.delete_cost_func(word1[i])
                    if self.delete_cost_func
                    else self.delete_cost
                )
            self.memo[(tuple(word1[:m]), tuple(word2[:n]))] = cost
            return cost

        # Calculate the cost of replace, delete, and insert
        replace_cost = (
            self.replace_cost_func(word1[m - 1], word2[n - 1])
            if self.replace_cost_func
            else self.replace_cost
        )
        delete_cost = (
            self.delete_cost_func(word1[m - 1])
            if self.delete_cost_func
            else self.delete_cost
        )
        insert_cost = (
            self.insert_cost_func(word2[n - 1])
            if self.insert_cost_func
            else self.insert_cost
        )

        replace = replace_cost + self._calculate_helper(word1, word2, m - 1, n - 1)
        delete = delete_cost + self._calculate_helper(word1, word2, m - 1, n)
        insert = insert_cost + self._calculate_helper(word1, word2, m, n - 1)
        cost = min(replace, delete, insert)

        # Memoize the result
        self.memo[(tuple(word1[:m]), tuple(word2[:n]))] = cost
        return cost


# Function to split Katakana into moras. However, it deviates from the original definition of moras by considering long vowels as one mora.


def extend_long_vowel_moras(text: str) -> list[str]:
    try:
        import jamorasep
    except ImportError:
        raise ImportError(
            "The jamorasep module is required but not installed. Please install it using 'pip install jamorasep'."
        )

    parsed_moras = jamorasep.parse(text, output_format="katakana")
    extended_moras = []
    for index, mora in enumerate(parsed_moras):
        if mora == "ー" and index > 0:
            extended_moras[-1] += mora
        else:
            extended_moras.append(mora)
    return extended_moras


# Class to calculate weighted Hamming distance
class WeightedHamming:
    """
    A class to calculate the weighted Hamming distance between two strings.
    The distance is calculated based on the costs of replacement operations.
    Custom cost functions and preprocessing functions can be provided to modify the behavior of the distance calculation.

    Attributes:
        replace_cost (float): The default cost of a replacement operation.
        replace_cost_func (Optional[Callable[[str, str], float]]): A custom function to calculate the cost of a replacement operation.
        preprocess_func (Optional[Callable[[str], List[str]]]): A custom function to preprocess the input strings before calculating the distance.
        memo (Dict[Tuple[Tuple[str, ...], Tuple[str, ...]], float]): A dictionary to store memoized results of distance calculations.
    """

    def __init__(
        self,
        replace_cost: float = 1.0,
        replace_cost_func: Callable[[str, str], float] | None = None,
        preprocess_func: Callable[[str], list[str]] | None = None,
    ):
        """
        Initializes the WeightedHamming class with the given costs and custom functions.

        Args:
            replace_cost (float): The default cost of a replacement operation.
            replace_cost_func (Optional[Callable[[str, str], float]]): A custom function to calculate the cost of a replacement operation.
            preprocess_func (Optional[Callable[[str], List[str]]]): A custom function to preprocess the input strings before calculating the distance.
        """
        self.replace_cost = replace_cost
        self.replace_cost_func = replace_cost_func
        self.preprocess_func = preprocess_func
        self.memo: dict[tuple[str, str], float] = {}

    def calculate(self, word1: str, word2: str) -> float:
        if self.preprocess_func:
            word1 = self.preprocess_func(word1)
            word2 = self.preprocess_func(word2)
        return self._calculate(word1, word2)

    def calculate_batch(self, words1: list[str], words2: list[str]) -> list[float]:
        if self.preprocess_func:
            words1 = [self.preprocess_func(word1) for word1 in words1]
            words2 = [self.preprocess_func(word2) for word2 in words2]
        results = []
        for word1 in words1:
            result = []
            for word2 in words2:
                result.append(self._calculate(word1, word2))
            results.append(result)
        return results

    def get_topn(
        self, word: str, wordlist: list[str], n: int = 10
    ) -> list[tuple[str, float]]:
        """
        Get the top n similar words from the given list based on weighted Hamming distance.

        Args:
            word (str): The word to compare with.
            wordlist (list[str]): The list of words to compare.
            n (int): The number of similar words to get.

        Returns:
            List[Tuple[str, float]]: The top n similar words and their distances.
        """
        distances = self.calculate_batch([word], wordlist)[0]
        return sorted(zip(wordlist, distances), key=lambda x: x[1])[:n]

    def _calculate(self, word1: str, word2: str) -> float:
        """
        Calculates the weighted Hamming distance between two strings.

        Args:
            word1 (str): The first word.
            word2 (str): The second word.

        Returns:
            float: The calculated weighted Hamming distance.
        """
        if len(word1) != len(word2):
            return float("inf")
        return self._calculate_helper(word1, word2, len(word1))

    def _calculate_helper(self, word1: str, word2: str, length: int) -> float:
        """
        A helper function to calculate the weighted Hamming distance between two strings.

        Args:
            word1 (str): The first word.
            word2 (str): The second word.
            length (int): The length of the words.

        Returns:
            float: The calculated weighted Hamming distance.
        """
        # Check for memoized result
        if (tuple(word1), tuple(word2)) in self.memo:
            return self.memo[(tuple(word1), tuple(word2))]

        cost = 0.0
        for i in range(length):
            if self.replace_cost_func:
                cost += self.replace_cost_func(word1[i], word2[i])
            else:
                if word1[i] != word2[i]:
                    cost += self.replace_cost

        # Memoize the result
        self.memo[(tuple(word1), tuple(word2))] = cost
        return cost


def create_kana_distance_calculator(
    *,
    kana2phonome_csv: str = os.path.join(
        os.path.dirname(__file__), "data/biphone/kana2phonome_bi.csv"
    ),
    distance_consonants_csv: str = os.path.join(
        os.path.dirname(__file__), "data/biphone/distance_consonants_bi.csv"
    ),
    distance_vowels_csv: str = os.path.join(
        os.path.dirname(__file__), "data/biphone/distance_vowels_bi.csv"
    ),
    insert_penalty: float = 1.0,
    delete_penalty: float = 1.0,
    replace_penalty: float = 1.0,
    vowel_ratio: float = 0.5,
    non_syllabic_penalty: float = 0.2,
    preprocess_func: Callable[[str], list[str]] | None = extend_long_vowel_moras,
    distance_type: str = "levenshtein",
    same_phonome_offset: bool = True,
    consonant_binary: bool = False,
    vowel_binary: bool = False,
) -> WeightedLevenshtein | WeightedHamming:
    distance_list = create_kana_distance_list(
        kana2phonome_csv=kana2phonome_csv,
        distance_consonants_csv=distance_consonants_csv,
        distance_vowels_csv=distance_vowels_csv,
        insert_penalty=insert_penalty,
        delete_penalty=delete_penalty,
        replace_penalty=replace_penalty,
        vowel_ratio=vowel_ratio,
        non_syllabic_penalty=non_syllabic_penalty,
        same_phonome_offset=same_phonome_offset,
        consonant_binary=consonant_binary,
        vowel_binary=vowel_binary,
    )
    distance_dict = {}
    for row in distance_list:
        kana1 = row["kana1"]
        kana2 = row["kana2"]
        distance = row["distance"]
        distance_dict[(kana1, kana2)] = distance

    def insert_cost_func(kana: str) -> float:
        return distance_dict[("sp", kana)]

    def delete_cost_func(kana: str) -> float:
        return distance_dict[(kana, "sp")]

    def replace_cost_func(kana1: str, kana2: str) -> float:
        return distance_dict[(kana1, kana2)]

    if distance_type == "levenshtein":
        return WeightedLevenshtein(
            insert_cost_func=insert_cost_func,
            delete_cost_func=delete_cost_func,
            replace_cost_func=replace_cost_func,
            preprocess_func=preprocess_func,
        )
    elif distance_type == "hamming":
        return WeightedHamming(
            replace_cost_func=replace_cost_func,
            preprocess_func=preprocess_func,
        )
    else:
        raise ValueError(f"Invalid distance type: {distance_type}")
