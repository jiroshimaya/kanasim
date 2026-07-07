import random
import time

import pytest

from kanasim import create_kana_distance_calculator, extend_long_vowel_moras


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
