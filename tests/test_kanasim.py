import random
import time

import pytest

from kanasim import (
    WeightedLevenshtein,
    create_kana_distance_calculator,
    extend_long_vowel_moras,
)


def test_extend_long_vowel_moras():
    assert extend_long_vowel_moras("カーンシャッ") == ["カー", "ン", "シャ", "ッ"]


def test_extend_long_vowel_moras_ignores_whitespace():
    assert extend_long_vowel_moras("ウェンザ ナイ ハズ カム") == [
        "ウェ",
        "ン",
        "ザ",
        "ナ",
        "イ",
        "ハ",
        "ズ",
        "カ",
        "ム",
    ]
    # full-width space, tab and newline
    assert extend_long_vowel_moras("カー　ンシャ\tッ\n") == ["カー", "ン", "シャ", "ッ"]
    # long vowel mark right after a removed space extends the previous mora
    assert extend_long_vowel_moras("カ ーン") == ["カー", "ン"]


def test_calculate_with_whitespace():
    calculator = create_kana_distance_calculator()
    assert calculator.calculate("ウェンザ ナイ", "ウェンザナイ") == 0
    assert calculator.calculate("カナダ ", "バハマ") == calculator.calculate(
        "カナダ", "バハマ"
    )


def test_calculate_with_unsupported_character_raises_value_error():
    calculator = create_kana_distance_calculator()
    with pytest.raises(ValueError, match="distance table"):
        calculator.calculate("ａｂｃ", "カナダ")


def test_create_kana_edit_distance_calculator():
    calculator = create_kana_distance_calculator()

    assert int(calculator.calculate("カナダ", "バハマ")) == 22

    word = "カナダ"
    wordlist = ["カナダ", "バハマ", "タバタ", "サワラ", "カナタ", "カラダ", "カドマ"]
    ranking = calculator.get_topn(word, wordlist, n=10)
    top3_words = [w for w, _ in ranking[:3]]
    assert top3_words == ["カナダ", "カラダ", "カナタ"]


def test_create_kana_hamming_distance_calculator():
    calculator = create_kana_distance_calculator(distance_type="hamming")

    assert int(calculator.calculate("カナダ", "バハマ")) == 22

    word = "カナダ"
    wordlist = ["カナダ", "バハマ", "タバタ", "サワラ", "カナタ", "カラダ", "カドマ"]
    ranking = calculator.get_topn(word, wordlist, n=10)
    top3_words = [w for w, _ in ranking[:3]]
    assert top3_words == ["カナダ", "カラダ", "カナタ"]


def test_normalize_bounds_distances():
    calculator = create_kana_distance_calculator(normalize=True)
    # with all penalties at 1.0, a normalized single-mora distance is at most 1
    assert 0 < calculator.calculate("カ", "サ") <= 1
    assert calculator.calculate("カ", "カ") == 0


def test_normalize_with_vowel_binary_prioritizes_vowel_match():
    # For rhyming, a vowel mismatch should outweigh a consonant mismatch.
    # Without normalize, vowel_binary=True has the opposite effect because the
    # binary vowel distance (0/1) is negligible next to raw consonant
    # distances.
    calculator = create_kana_distance_calculator(vowel_binary=True, normalize=True)
    vowel_mismatch = calculator.calculate("カ", "コ")
    consonant_mismatch = calculator.calculate("カ", "サ")
    assert vowel_mismatch > consonant_mismatch


def test_normalize_keeps_ranking_of_default_weights():
    calculator = create_kana_distance_calculator(normalize=True)
    word = "カナダ"
    wordlist = ["バハマ", "タバタ", "サワラ", "カナタ", "カラダ", "カドマ"]
    ranking = calculator.get_topn(word, wordlist, n=10)
    assert ranking[0][0] in ("カラダ", "カナタ")


def test_phoneme_unit_mono_removes_vowel_contamination():
    # In the biphone tables the consonant labels carry the following vowel
    # ("k+a" vs "k+i"), so with consonants only (vowel_ratio=0) the same
    # consonant カ/キ ends up farther apart than the different consonants カ/タ.
    biphone = create_kana_distance_calculator(vowel_ratio=0)
    assert biphone.calculate("カ", "キ") > biphone.calculate("カ", "タ")
    # With monophone tables the contamination is gone.
    mono = create_kana_distance_calculator(vowel_ratio=0, phoneme_unit="mono")
    assert mono.calculate("カ", "キ") == 0
    assert mono.calculate("カ", "タ") > 0


def test_phoneme_unit_mono_basic():
    calculator = create_kana_distance_calculator(phoneme_unit="mono")
    assert calculator.calculate("カナダ", "カナダ") == 0
    word = "カナダ"
    wordlist = ["カナダ", "バハマ", "タバタ", "サワラ", "カナタ", "カラダ", "カドマ"]
    ranking = calculator.get_topn(word, wordlist, n=10)
    assert ranking[0][0] == "カナダ"
    # combined with the rhyme-oriented options
    rhyme = create_kana_distance_calculator(
        phoneme_unit="mono", vowel_binary=True, normalize=True
    )
    assert rhyme.calculate("カ", "コ") > rhyme.calculate("カ", "サ")


def test_consonant_distance_features():
    calculator = create_kana_distance_calculator(
        phoneme_unit="mono", consonant_distance="features", vowel_ratio=0
    )
    # voicing pair < place mismatch < almost everything differs
    voicing = calculator.calculate("カ", "ガ")
    place = calculator.calculate("カ", "サ")
    unrelated = calculator.calculate("マ", "サ")
    assert 0 < voicing < place < unrelated


def test_consonant_distance_features_requires_mono():
    with pytest.raises(ValueError, match="features"):
        create_kana_distance_calculator(consonant_distance="features")


def test_mono_hmm_tables_usable():
    import os

    import kanasim

    data_dir = os.path.join(os.path.dirname(kanasim.__file__), "data/monophone")
    calculator = create_kana_distance_calculator(
        phoneme_unit="mono",
        vowel_ratio=0,
        distance_consonants_csv=os.path.join(
            data_dir, "distance_consonants_mono_hmm.csv"
        ),
        distance_vowels_csv=os.path.join(data_dir, "distance_vowels_mono_hmm.csv"),
    )
    assert calculator.calculate("カナダ", "カナダ") == 0
    # consonants only: s/sh are acoustically close, s/m far apart
    assert calculator.calculate("サ", "シャ") < calculator.calculate("サ", "マ")


def test_symmetric_option():
    asym = create_kana_distance_calculator()
    assert asym.calculate("カナダ", "バハマ") != asym.calculate("バハマ", "カナダ")
    sym = create_kana_distance_calculator(symmetric=True)
    pairs = [("カナダ", "バハマ"), ("ウェンザ", "ウェザー"), ("カ", "キー")]
    for word1, word2 in pairs:
        assert sym.calculate(word1, word2) == pytest.approx(sym.calculate(word2, word1))
    # the symmetric distance is the average of the two directions at the
    # single-mora level
    expected = (asym.calculate("カ", "サ") + asym.calculate("サ", "カ")) / 2
    assert sym.calculate("カ", "サ") == pytest.approx(expected)


def _reference_levenshtein(word1, word2, insert_cost, delete_cost, replace_cost):
    """Naive recursive implementation used as a test oracle."""
    if not word1:
        return sum(insert_cost(c) for c in word2)
    if not word2:
        return sum(delete_cost(c) for c in word1)
    return min(
        replace_cost(word1[-1], word2[-1])
        + _reference_levenshtein(
            word1[:-1], word2[:-1], insert_cost, delete_cost, replace_cost
        ),
        delete_cost(word1[-1])
        + _reference_levenshtein(
            word1[:-1], word2, insert_cost, delete_cost, replace_cost
        ),
        insert_cost(word2[-1])
        + _reference_levenshtein(
            word1, word2[:-1], insert_cost, delete_cost, replace_cost
        ),
    )


def test_calculate_matches_reference_implementation():
    calculator = create_kana_distance_calculator()
    assert isinstance(calculator, WeightedLevenshtein)
    assert calculator.insert_cost_func is not None
    assert calculator.delete_cost_func is not None
    assert calculator.replace_cost_func is not None
    rng = random.Random(0)
    katakana = (
        "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホヤユヨランー"
    )
    for _ in range(30):
        # a word starting with "ー" has no preceding mora to extend and is
        # not in the distance table, so it is not a valid input
        word1 = "".join(rng.choices(katakana, k=rng.randint(0, 5))).lstrip("ー")
        word2 = "".join(rng.choices(katakana, k=rng.randint(0, 5))).lstrip("ー")
        expected = _reference_levenshtein(
            extend_long_vowel_moras(word1),
            extend_long_vowel_moras(word2),
            calculator.insert_cost_func,
            calculator.delete_cost_func,
            calculator.replace_cost_func,
        )
        assert calculator.calculate(word1, word2) == pytest.approx(expected)


def test_calculate_long_input():
    # The previous recursive implementation hit Python's recursion limit
    # around 1000 moras in total.
    calculator = create_kana_distance_calculator()
    assert calculator.calculate("カ" * 600, "サ" * 600) > 0


def test_calculate_batch_speed():
    calculator = create_kana_distance_calculator()
    katakana = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワンガギグゲゴザジズゼゾダジヅデドバビブベボパピプペポ"
    wordlist1 = ["".join(random.choices(katakana, k=5)) for _ in range(10)]
    wordlist2 = ["".join(random.choices(katakana, k=5)) for _ in range(10)]
    start = time.time()
    calculator.calculate_batch(wordlist1, wordlist2)
    total_time = time.time() - start
    # Guards against a memoization regression (without memoization this takes
    # seconds). Loose enough not to flake on slow CI runners.
    assert total_time < 0.5
