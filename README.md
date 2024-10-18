# kanasim

This repository provides phonetic similarity data for kana, calculated using a Japanese acoustic model, along with sample programs that utilize this data to compute word similarity. This similarity data is used in the lyric creation support app "Soramimic" (https://soramimic.com). It is expected to be useful in applications where quantitatively evaluating phonetic similarity is important, such as in the automatic generation of puns or rap lyrics, not just for misheard lyrics.

#### English | [日本語](https://github.com/jiroshimaya/kanasim/blob/main/README.ja.md)

## Phonetic Similarity Data
This data represents the distances between consonants and between vowels, calculated using the acoustic model from the open source speech recognition software [julius](https://github.com/julius-speech/julius). It is stored in the following file:

- [Kana-Phoneme-Similarity Correspondence Table](src/kanasim/data/biphone/kana_to_phonome_distance.csv)

The column names in CSV format are as follows:

- kana1: The first kana (mora)
- kana2: The second kana (mora)
- consonant1: The consonant corresponding to kana1
- consonant2: The consonant corresponding to kana2
- vowel1: The vowel corresponding to kana1
- vowel2: The vowel corresponding to kana2
- distance_consonant: The distance between consonant1 and consonant2
- distance_vowel: The distance between vowel1 and vowel2

By managing the distances between consonants and vowels separately, it is possible to adjust the weighting according to the application. The following example outputs the similarity of kana when consonants and vowels are added together in a 1:1 ratio.

```sh
git clone https://github.com/jiroshimaya/kanasim.git
cd kanasim
```

```Python
import pandas as pd
# Load the Kana-Phoneme-Similarity Correspondence Table
kana_df = pd.read_csv("src/kanasim/data/biphone/kana_to_phonome_distance.csv")
# Convert the Kana-Phoneme-Similarity Correspondence Table to a dictionary
kana_dict = {}
for _, row in kana_df.iterrows():
    kana_dict[(row["kana1"], row["kana2"])] = row["distance_consonant"] + row["distance_vowel"]

# Print the distance between kana
kana1, kana2 = "カ", "ナ"
print(f"distance between {kana1} and {kana2}: {kana_dict[(kana1, kana2)]}")

kana1, kana2 = "カ", "サ"
print(f"distance between {kana1} and {kana2}: {kana_dict[(kana1, kana2)]}")

kana1, kana2 = "バ", "マ"
print(f"distance between {kana1} and {kana2}: {kana_dict[(kana1, kana2)]}")    
```

```
distance between カ and ナ: 134.181978
distance between カ and サ: 130.812428
distance between バ and マ: 123.74445
```

## Sample code
This sample code demonstrates how to calculate the weighted edit distance and Hamming distance between katakana words using phonetic similarity data.
In the sample code, the similarity of the same phoneme is used as an offset by default and subtracted from the actual value. This means that the replacement cost for the same phoneme is set to 0. This is to prevent the insertion cost from being overestimated and to ensure that the calculation of the edit distance aligns with intuition when the replacement cost for the same phoneme is greater than 0.
### Installation

- Install from source (Recommend)

```sh
git clone https://github.com/jiroshimaya/kanasim.git
cd kanasim
pip install .
```

- Install from PyPI

```
pip install kanasim
```

### Using in terminal

```sh
# Edit distance
python scripts/calculate_weighted_edit_distance.py カナダ バハマ

# Hamming distance
python scripts/calculate_weighted_edit_distance.py カナダ バハマ -dt

# Sort word list based on distance
python scripts/sort_by_weighted_edit_distance.py シマウマ -w data/sample/pro
nunciation.txt 
```
### Using in Python code

#### Distance Calculation
```Python
from kanasim import create_kana_distance_calculator

calculator = create_kana_distance_calculator()
distance = calculator.calculate("カナダ", "バハマ")
print(distance)
```

```
22.74598650000001
```

#### Batch Processing

```python
from kanasim import create_kana_distance_calculator

calculator = create_kana_distance_calculator()

words = ["カナダ", "タハラ"]
wordlist = ["カナダ", "バハマ", "タバタ", "サワラ", "カナタ", "カラダ", "カドマ"]
distances = calculator.calculate_batch(words, wordlist)
for i, target_word in enumerate(words):
    print(f"distance between {target_word} and ...")
    for source_word, distance in zip(wordlist, distances[i]):
        print(source_word, distance)
    print()
```

```
distance between カナダ and ...
カナダ 0.0
バハマ 22.74598650000001
タバタ 14.328020000000006
サワラ 16.4028395
カナタ 4.468167000000005
カラダ 3.967136
カドマ 16.998950500000007

distance between タハラ and ...
カナダ 16.56518150000001
バハマ 11.308950499999998
タバタ 14.952468
サワラ 12.972008500000001
カナタ 19.041203000000007
カラダ 14.90169000000001
カドマ 20.102040000000006
```
#### Ranking

```Python
from kanasim import create_kana_distance_calculator

calculator = create_kana_distance_calculator()

word = "カナダ"
wordlist = ["カナダ", "バハマ", "タバタ", "サワラ", "カナタ", "カラダ", "カドマ"]
ranking = calculator.get_topn(word, wordlist, n=10)
for i, (w, d) in enumerate(ranking, 1):
    print(f"{i}: {w} ({d})")
```

```
1: カナダ (0.0)
2: カラダ (3.967136)
3: カナタ (4.468167000000005)
4: タバタ (14.328020000000006)
5: サワラ (16.4028395)
6: カドマ (16.998950500000007)
7: バハマ (22.74598650000001)
```

#### Weight Adjustment

```Python
from kanasim import create_kana_distance_calculator

# The vowel_ratio parameter determines the weight of vowels when calculating the distance between kana.
# By default, it is set to 0.5, meaning vowels and consonants are weighted equally (1:1).
calculator = create_kana_distance_calculator(vowel_ratio=0.2)

word = "カナダ"
wordlist = ["カナデ", "サラダ"]

topn = calculator.get_topn(word, wordlist, n=10)
print("vowel_ratio=0.2")
for i, (w, d) in enumerate(topn, 1):
    print(f"{i}: {w} ({d})")

calculator = create_kana_distance_calculator(vowel_ratio=0.8)

topn = calculator.get_topn(word, wordlist, n=10)
print("vowel_ratio=0.8")
for i, (w, d) in enumerate(topn, 1):
    print(f"{i}: {w} ({d})")
```

```
vowel_ratio=0.2
1: カナデ (8.397902000000006)
2: サラダ (11.487954600000004)
vowel_ratio=0.8
1: サラダ (7.347296400000003)
2: カナデ (15.578681000000007)
```


## Other Phonetic Similarity Related Files
In addition to the [Kana-Phoneme-Similarity Correspondence Table](src/kanasim/biphone/kana_to_phonome_distance.csv), there are three other files. These files are integrated into the Kana-Phoneme-Similarity Correspondence Table, so you usually do not need to refer to them directly.

- [Consonant Distance](src/kanasim/data/biphone/distance_consonants_bi.csv)
- [Vowel Distance](src/kanasim/data/biphone/distance_vowels_bi.csv)
- [Kana-Phoneme Correspondence Table](src/kanasim/data/biphone/kana2phonome_bi.csv)

### Consonant and Vowel Distances
The CSV format includes the following column names:

- phonome1: The first phoneme
- phonome2: The second phoneme
- distance: The distance between phonome1 and phonome2

Phonons are described in a biphone format with adjacent phonemes, excluding silence (sp), geminate consonants (q), and nasal sounds (N) ([reference](https://ftp.jaist.ac.jp/pub/osdn.net/julius/47534/Juliusbook-4.1.5-ja.pdf#page=37)).
For consonants, it is a biphone with the following vowel. The following vowel is separated by `+`.
For example, `b+a` means a consonant b immediately before a vowel a.
For vowels, it is a biphone with the preceding consonant. The preceding consonant is separated by `-`.
For example, `b-a` means a vowel a immediately after a consonant b.

A smaller distance indicates a higher similarity. Although referred to as "distance," swapping phonome1 and phonome2 results in different values, so it does not meet the strict definition of distance. Also, the "distance" of the same phoneme is not zero.

### Kana-Phoneme Correspondence Table
The CSV format includes the following column names:
- kana: Kana (mora) written in katakana. Long vowels are treated as a single element combined with the preceding kana.
- consonant: The phoneme representing the consonant of the kana in biphone format. If the kana is a single vowel, geminate consonant, or nasal sound, it is represented as "sp".
- vowel: The phoneme representing the vowel of the kana in biphone format. If the kana is a geminate consonant (q), nasal sound (N), or silence (sp), it corresponds to the respective phoneme.
- constant_mono: Optional. The phoneme representing the consonant of the kana in monophone format.
- vowel_mono: Optional. The phoneme representing the vowel of the kana in monophone format.

## Data Creation Method
This was derived based on the GMM-HMM model of the Julius speech recognition model. The following method was referenced:

- [音響モデルから音素間の距離を求める | 見返すかもしれないメモ](https://yaamaa-memo.hatenablog.com/entry/2017/12/17/062435)

In simple terms, Julius has an acoustic model (HMM) for each phoneme, and the "distance" between the HMMs of two phonemes is used as a measure of similarity. The "distance" between HMMs is calculated as the probability that the output of one phoneme's HMM is produced by another phoneme's HMM.

To reduce computation time, the calculation targets for phonemes and kana are limited. For phonemes, only biphones consisting of a consonant followed by a vowel and a vowel preceded by a consonant are calculated. Although triphone formats are considered more accurate, they are not used due to the vast number of combinations. Additionally, in Japanese, consecutive consonants or vowels can occur but are not frequest, thus, they are not targeted for calculation. Regarding "distance," only the distances between consonants and between vowels are calculated, and the distance between consonants and vowels is not calculated. From the perspective of kana similarity, it is generally sufficient to match consonants and vowels separately.

## Evaluation
### Visualization
The positional relationships of phonemes calculated using the above method are shown in a diagram mapped by multidimensional scaling. Since there are too many elements in biphones, the diagram is based on monophone calculations. It can be seen that phonemes belonging to the same category, such as palatal sounds, voiced sounds, voiceless sounds, and vowels, are somewhat close to each other.

![Phoneme Positional Relationships](docs/pictures/phonome_distance_2d.png)


### Comparison with Baseline
We compare the results of the commonly used unweighted Hamming distance, a measure of phonetic similarity between words, with the proposed weighted Hamming distance. Edit distance and Hamming distance are often used to measure phonetic similarity between words. In this case, considering the application to parody lyrics, we limit the search to words with the same number of morae and obtain those with a close Hamming distance. The unweighted Hamming distance is calculated separately for vowels and consonants and then summed.

Weighted Hamming Distance (Proposed)
```
% python scripts/sort_by_weighted_edit_distance.py シマウマ -dt hamming
シラウオ 17.72447499999999
シマフグ 19.3677925
シロウオ 21.458600499999996
シマアジ 24.4898105
シマドジョー 25.773904000000005
シマハギ 25.934866999999997
ピライーバ 26.07182999999999
チゴダラ 26.469384999999992
シマダイ 27.469623499999994
ツマグロ 28.451683499999998
```

Unweighted Hamming Distance (Baseline)

```
% python scripts/sort_by_hamming_distance.py シマウマ
シマアジ 1.5
シマフグ 1.5
シラウオ 1.5
カマツカ 2.0
シマソイ 2.0
シマダイ 2.0
シマドジョー 2.0
シマハギ 2.0
シロウオ 2.0
ピライーバ 2.0
```
In the case of unweighted calculations, "シマアジ" (Shimaaji), "シマフグ" (Shimafugu), and "シラウオ" (Shirauo) have the same score. However, with weighting, the scores differ in the order of "シラウオ" (Shirauo), "シマフグ" (Shimafugu), and "シマアジ" (Shimaaji). This is likely because, in the distance data, "m" and "r" are relatively close, giving "シラウオ" (Shirauo) priority. Whether this aligns with actual perception depends on the application and requires consideration.

### Subtle Influence of vowel or consonant weights
In the sample program, vowel or consonant weights can be set when calculating distances, but because phonemes are distinguished by biphones, the influence is less apparent compared to using simple edit distance.

```Python
from kanasim import create_kana_distance_calculator

# The vowel_ratio parameter determines the weight of vowels when calculating the distance between kana.
# By default, it is set to 0.5, meaning vowels and consonants are weighted equally (1:1).
calculator = create_kana_distance_calculator(vowel_ratio=0.0)

word = "カナダ"
wordlist = ["サラダ", "コノデ"]

topn = calculator.get_topn(word, wordlist, n=10)
print("vowel_ratio=0.0")
for i, (w, d) in enumerate(topn, 1):
    print(f"{i}: {w} ({d})")
```

```
vowel_ratio=0.0
1: サラダ (12.868174000000003)
2: コノデ (16.23794400000002)
```

In the above example, because the vowel_ratio is set to 0, "コノデ" (Konode), which matches the consonants of "カナダ" (Kanada), should ideally be ranked first, but it ends up in second place. If you want to strictly prioritize specific elements like vowel matching, you might need to use unweighted edit distance.
In the manual tests conducted, the influence of vowels was found to be greater than that of consonants, and even when the vowel_ratio was set to 0, consonant matching was not prioritized. This is likely because, in Japanese, vowels often characterize the phonetics of kana, and a similar tendency is observed in this data based on Japanese acoustic models. If you want to emphasize consonant matching, using unweighted edit distance might be more appropriate.


## Citation

If you wish to cite this library or similarity data, please include the following:

```
@software{kanasim,  
  author={Jiro Shimaya},  
  title={Kanasim: Japanese Kana Distance Data and Sample Code for Similarity Calculation},  
  url={https://github.com/jiroshimaya/kanasim},  
  year={2024},  
  month={10},  
}
```

## References

- A. Lee and T. Kawahara: Julius v4.5 (2019) https://doi.org/10.5281/zenodo.2530395
- [音響モデルから音素間の距離を求める | 見返すかもしれないメモ](https://yaamaa-memo.hatenablog.com/entry/2017/12/17/062435)

# For Developers

- This project uses [uv](https://github.com/astral-sh/uv) for package management.
- This project uses [taskipy](https://github.com/taskipy/taskipy) for command management.

```
uv run task test
uv run task lint
uv run task format
```