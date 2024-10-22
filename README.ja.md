# kanasim

このリポジトリは、日本語音響モデルを用いて計算されたカナの音韻類似度データと、そのデータを活用して単語間の類似度を算出するサンプルプログラムを提供します。
この類似度データは、空耳歌詞の作詞支援アプリ「[Soramimic](https://soramimic.com)」で利用されています。
空耳に限らず、ダジャレやラップの自動生成など、音韻の類似度を定量的に評価することが重要なアプリケーションでの利用が期待されます。

#### [English](https://github.com/jiroshimaya/kanasim/blob/main/README.md) | 日本語

## 音韻類似度データ
オープンソースの音声認識ソフトウェア[julius](https://github.com/julius-speech/julius)の音響モデルを使用して計算された、子音間および母音間の距離データです。以下に保存されています。

- [カナ-音素-類似度対応表](src/kanasim/data/biphone/kana_to_phonome_distance.csv)

csv形式で列名は以下です。

- kana1: 1つめのカナ（モーラ）
- kana2: 2つめのカナ（モーラ）
- consonant1: kana1に対応する子音
- consonant2: kana2に対応する子音
- vowel1: kana1に対応する母音
- vowel2: kana2に対応する母音
- distance_consonant: consonant1とconsonant2の間の距離
- distance_vowel: vowel1とvowel2の間の距離

子音と母音の距離を個別に管理することで、アプリケーションに応じた重み付けの調整が可能です。
以下の例では、子音と母音を1:1で足し合わせたときのカナの類似度を出力しています。

```sh
git clone https://github.com/jiroshimaya/kanasim.git
cd kanasim
```

```Python
import pandas as pd
# カナ-音素-類似度対応表を読み込む
kana_df = pd.read_csv("src/kanasim/data/biphone/kana_to_phonome_distance.csv")
# カナ-音素-類似度対応表を辞書に変換する
kana_dict = {}
for _, row in kana_df.iterrows():
    kana_dict[(row["kana1"], row["kana2"])] = row["distance_consonant"] + row["distance_vowel"]

# カナ-カナ間の距離をprint
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

## サンプルプログラム
音韻類似度データを使用して、カナ表記の単語間の重み付き編集距離とハミング距離を計算するためのサンプルプログラムです。
サンプルプログラムでは、デフォルトで同じ音素の類似度をオフセットとして使用し、実際の値から引いています。つまり、同じ音素の置換コストが0になるようにしています。これは、同じ音素の置換コストが0より大きい場合に、挿入コストが過大に見積もられ、編集距離の計算が直感に反することを防ぐためです。

### インストール
- ソースからインストール (推奨)

```sh
git clone https://github.com/jiroshimaya/kanasim.git
cd kanasim
pip install .
```

- PyPIからインストール

```
pip install kanasim
```
### スクリプト実行

```sh
#編集距離
python scripts/calculate_weighted_edit_distance.py カナダ バハマ

#ハミング距離
python scripts/calculate_weighted_edit_distance.py カナダ バハマ -dt

# 距離に基づく単語リストのソート
python scripts/sort_by_weighted_edit_distance.py シマウマ -w data/sample/pro
nunciation.txt 
```
### pythonからの呼び出し

#### 距離計算
```Python
from kanasim import create_kana_distance_calculator

calculator = create_kana_distance_calculator()
distance = calculator.calculate("カナダ", "バハマ")
print(distance)
```

```
22.74598650000001
```

#### バッチ処理

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
#### ランキング

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

#### 重み調整

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


## その他の音韻類似度関連ファイル
[カナ-音素-類似度対応表](src/kanasim/biphone/kana_to_phonome_distance.csv)以外に、3つのファイルがあります。これらのファイルは、カナ-音素-類似度対応表に統合されているため、通常はこれらを直接参照する必要はありません。

- [子音距離](src/kanasim/data/biphone/distance_consonants_bi.csv)
- [母音距離](src/kanasim/data/biphone/distance_vowels_bi.csv)
- [カナ-音素対応表](src/kanasim/data/biphone/kana2phonome_bi.csv)

### 子音・母音距離
CSV形式で、以下の列名があります。

- phonome1: 1つ目の音素
- phonome2: 2つ目の音素
- distance: phonome1とphonome2の距離

phonomeは無音（sp）、促音（q）、撥音（N）を除き、隣接音素とのバイフォン（biphone）形式で記述されています（[参考](https://ftp.jaist.ac.jp/pub/osdn.net/julius/47534/Juliusbook-4.1.5-ja.pdf#page=37)）。
子音の場合、直後の母音とのバイフォンです。直後の母音は`+`で区切られます。
例えば、`b+a`は、aという母音の直前のbという子音を意味します。
母音の場合、直前の子音とのバイフォンです。直前の子音は`-`で区切られます。
例えば、`b-a`はbの直後のaという母音を意味します。

distanceが小さいほど、類似度が高いことを示します。「距離」と呼んでいますが、phonome1と2を入れ替えると値が異なるため、厳密な距離の定義は満たしません。また、同じ音素の「距離」が0にはなりません。

### カナ-音素対応表
CSV形式で、以下の列名があります。
- kana: カナ（モーラ）。長音は直前のカナと合わせて1要素として扱います。
- consonant: カナの子音を表すバイフォン形式の音素。カナが単母音や促音、撥音の場合は「sp」となります。
- vowel: カナの母音または表すバイフォン形式の音素。カナが促音（q）、撥音（N）、無音（sp）の場合は対応する音素となります。
- constant_mono: オプション。カナの子音を表すモノフォン形式の音素。
- vowel_mono: オプション。カナの母音を表すモノフォン形式の音素。

## データ作成方法
音声認識モデル Julius の GMM-HMM モデルに基づいて求められました。
以下の方法を参考にしました。

- [音響モデルから音素間の距離を求める | 見返すかもしれないメモ](https://yaamaa-memo.hatenablog.com/entry/2017/12/17/062435)

簡単に説明すると、Julius では音素ごとの音響モデル（HMM）が存在し、2つの音素のHMM同士の「距離」を類似度の指標とします。
HMM同士の「距離」は、ある音素のHMMの出力が別の音素のHMMから出力される確率として算出します。

計算時間を短縮するため、音素やカナについて、計算対象を限定しています。
音素については、子音は直後の母音とのバイフォン、母音は直前の子音とのバイフォンのみを計算しています。トライフォン形式はより精度が高いと考えられますが、組み合わせが膨大になるため採用していません。また、日本語では子音や母音が連続することもありますが、頻度が低いため計算対象にしていません。
「距離」については、子音同士、母音同士の距離のみを主に計算しており、子音と母音の距離は計算していません。カナの類似度という観点では、子音と母音をそれぞれ対応付ければ基本的には十分と判断したためです。

## 評価
### 視覚化
上記の方法で算出した音素の位置関係を、2次元尺度法によりマッピングした図を示します。バイフォンだと要素が多すぎるため、モノフォンで計算したものに基づいています。口蓋音、有声音、無声音、母音など、同じジャンルに属する音素がなんとなく近くに存在していることがわかります。

![音素の位置関係](docs/pictures/phonome_distance_2d.png)


### ベースラインとの比較
単語の音韻類似度の指標として一般的に使用される重みなしのハミング距離と、今回提案する重み付きハミング距離の結果を比較します。
単語の音韻類似度を測る方法として、編集距離やハミング距離がよく用いられますが、今回は替え歌への応用を考慮し、モーラ数が同じ単語に限定して検索し、ハミング距離が近いものを取得します。重みなしのハミング距離は、母音と子音のハミング距離を別々に計算し、それらを合計する方法を採用しています。

重み付きハミング距離（提案）
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

重みなしハミング距離（ベースライン）

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
重みなしの場合、「シマアジ」「シマフグ」「シラウオ」は同じスコアですが、重みありでは「シラウオ」「シマフグ」「シマアジ」の順にスコアが異なります。これは距離データ上、mとrが比較的近いため「シラウオ」が優先されたと考えられます。実際の感覚と一致するかはアプリケーション次第で、検討が必要です。

### 母音や子音重みの影響の現れにくさ
サンプルプログラムでは、距離を計算する際に母音や子音の重みを設定できますが、音素がバイフォンで区別されるため、影響はシンプルな編集距離を使用する場合に比べて、現れにくいです。

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

上記ではvowel_ratioを0に設定したため、「カナダ」と子音が一致する「コノデ」が1位になることを期待しましたが、実際には2位になっています。
手動で試した範囲では、母音が子音に与える影響がそのの影響が子音よりも大きく、vowel_ratio=0に設定しても、子音の一致が優先されない傾向が見られました。これは、日本語では母音がカナの音韻を特徴づけることが多いため、日本語の音響モデルに基づくこのデータでも同様の傾向が見られると考えられます。子音の一致を重視したい場合は、重みなしの編集距離を使用することが適しているかもしれません。

## 引用

このライブラリや類似度データを引用する場合は、以下を記載ください。

```
@software{kanasim,  
  author={Jiro Shimaya},  
  title={Kanasim: Japanese Kana Distance Data and Sample Code for Similarity Calculation},  
  url={https://github.com/jiroshimaya/kanasim},  
  year={2024},  
  month={10},  
}
```

## 参考資料

- A. Lee and T. Kawahara: Julius v4.5 (2019) https://doi.org/10.5281/zenodo.2530395
- [音響モデルから音素間の距離を求める | 見返すかもしれないメモ](https://yaamaa-memo.hatenablog.com/entry/2017/12/17/062435)

# 開発者向け

- パッケージ管理に[uv](https://github.com/astral-sh/uv)を使用しています。
- コマンド管理に[taskipy](https://github.com/taskipy/taskipy)を使用しています。

```
uv run task test
uv run task lint
uv run task format
```
