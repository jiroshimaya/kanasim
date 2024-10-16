import csv
import os
from typing import Callable, List, Tuple, Dict, Optional, Iterable, Hashable, Any


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


def load_phonon_distance_csv(path: str) -> dict[tuple[str, str], float]:
    distance_dict = {}
    distance_list = load_csv(path)
    for row in distance_list:
        phonon1 = row["phonon1"]
        phonon2 = row["phonon2"]
        distance = float(row["distance"])
        distance_dict[(phonon1, phonon2)] = distance
    return distance_dict


def create_kana_distance_list(
    *,
    kana2phonon_csv: str,
    distance_consonants_csv: str,
    distance_vowels_csv: str,
    vowel_ratio: float,
    non_syllabic_penalty: float,
    insert_penalty: float,
    delete_penalty: float,
    replace_penalty: float,
) -> list[dict]:
    kana2phonon = load_csv(kana2phonon_csv)
    distance_consonants = load_phonon_distance_csv(distance_consonants_csv)
    distance_vowels = load_phonon_distance_csv(distance_vowels_csv)

    results = []
    for row1 in kana2phonon:
        for row2 in kana2phonon:
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
        insert_cost_func: Optional[Callable[[Hashable], float]] = None,
        delete_cost_func: Optional[Callable[[Hashable], float]] = None,
        replace_cost_func: Optional[Callable[[Hashable, Hashable], float]] = None,
        preprocess_func: Optional[Callable[[Any], Iterable[Hashable]]] = None,
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
        self.memo: Dict[Tuple[Tuple[Hashable, ...], Tuple[Hashable, ...]], float] = {}

    def calculate(self, list1: List[Hashable], list2: List[Hashable]) -> float:
        if self.preprocess_func:
            list1 = self.preprocess_func(list1)
            list2 = self.preprocess_func(list2)
        return self._calculate(list1, list2)

    def calculate_batch(
        self, lists1: List[List[Hashable]], lists2: List[List[Hashable]]
    ) -> List[float]:
        processed_lists1 = [self.preprocess_func(list1) for list1 in lists1]
        processed_lists2 = [self.preprocess_func(list2) for list2 in lists2]
        results = []
        for processed_list1 in processed_lists1:
            result = []
            for processed_list2 in processed_lists2:
                result.append(self._calculate(processed_list1, processed_list2))
            results.append(result)
        return results

    def _calculate(self, list1: List[Hashable], list2: List[Hashable]) -> float:
        """
        Calculates the weighted Levenshtein distance between two lists of strings.

        Args:
            list1 (List[str]): The first list of strings.
            list2 (List[str]): The second list of strings.

        Returns:
            float: The calculated weighted Levenshtein distance.
        """
        return self._calculate_helper(list1, list2, len(list1), len(list2))

    def _calculate_helper(
        self, list1: List[str], list2: List[str], m: int, n: int
    ) -> float:
        """
        A helper function to recursively calculate the weighted Levenshtein distance between two lists of strings.

        Args:
            list1 (List[str]): The first list of strings.
            list2 (List[str]): The second list of strings.
            m (int): The length of the first list.
            n (int): The length of the second list.

        Returns:
            float: The calculated weighted Levenshtein distance.
        """
        # Check for memoized result
        if (tuple(list1[:m]), tuple(list2[:n])) in self.memo:
            return self.memo[(tuple(list1[:m]), tuple(list2[:n]))]

        # Base case
        if m == 0:
            cost = 0.0
            for i in range(n):
                cost += (
                    self.insert_cost_func(list2[i])
                    if self.insert_cost_func
                    else self.insert_cost
                )
            self.memo[(tuple(list1[:m]), tuple(list2[:n]))] = cost
            return cost
        if n == 0:
            cost = 0.0
            for i in range(m):
                cost += (
                    self.delete_cost_func(list1[i])
                    if self.delete_cost_func
                    else self.delete_cost
                )
            self.memo[(tuple(list1[:m]), tuple(list2[:n]))] = cost
            return cost

        # Calculate the cost of replace, delete, and insert
        replace_cost = (
            self.replace_cost_func(list1[m - 1], list2[n - 1])
            if self.replace_cost_func
            else self.replace_cost
        )
        delete_cost = (
            self.delete_cost_func(list1[m - 1])
            if self.delete_cost_func
            else self.delete_cost
        )
        insert_cost = (
            self.insert_cost_func(list2[n - 1])
            if self.insert_cost_func
            else self.insert_cost
        )

        replace = replace_cost + self._calculate_helper(list1, list2, m - 1, n - 1)
        delete = delete_cost + self._calculate_helper(list1, list2, m - 1, n)
        insert = insert_cost + self._calculate_helper(list1, list2, m, n - 1)
        cost = min(replace, delete, insert)

        # Memoize the result
        self.memo[(tuple(list1[:m]), tuple(list2[:n]))] = cost
        return cost


# Function to split Katakana into moras. However, it deviates from the original definition of moras by considering long vowels as one mora.


def extend_long_vowel_moras(text: str) -> List[str]:
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


def create_kana_distance_calculator(
    *,
    kana2phonon_csv: str = os.path.join(
        os.path.dirname(__file__), "data/biphone/kana2phonon_bi.csv"
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
    preprocess_func: Callable[[Any], Iterable[Hashable]] = extend_long_vowel_moras,
) -> WeightedLevenshtein:
    distance_list = create_kana_distance_list(
        kana2phonon_csv=kana2phonon_csv,
        distance_consonants_csv=distance_consonants_csv,
        distance_vowels_csv=distance_vowels_csv,
        insert_penalty=insert_penalty,
        delete_penalty=delete_penalty,
        replace_penalty=replace_penalty,
        vowel_ratio=vowel_ratio,
        non_syllabic_penalty=non_syllabic_penalty,
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

    return WeightedLevenshtein(
        insert_cost_func=insert_cost_func,
        delete_cost_func=delete_cost_func,
        replace_cost_func=replace_cost_func,
        preprocess_func=preprocess_func,
    )
