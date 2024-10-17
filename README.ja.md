# kanasim

このリポジトリは、日本語のカナの音韻類似度データ、および、そのデータを使用して単語同士の類似度を求めるサンプルプログラムを提供します。  
このデータは、空耳歌詞の作詞支援アプリ「Soramimic」で使用されているものです。空耳以外にもダジャレやラップの自動生成など、音韻の類似度を定量的に見積もることが重要になってくる取り組みにおいて、活用できる可能性があると考えています。

## 使い方

### インストール
```
pip install .
pip install jamorasep
```

### 距離計算
```Python
from kanasim import create_kana_distance_calculator

calculator = create_kana_distance_calculator()
distance = calculator.calculate("カナダ", "バハマ")
print(distance)
```

```
200.886091
```

### バッチ処理

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
カナダ 178.1401045
バハマ 200.886091
タバタ 192.4681245
サワラ 194.542944
カナタ 182.6082715
カラダ 182.1072405
カドマ 195.139055

distance between タハラ and ...
カナダ 193.4058865
バハマ 188.1496555
タバタ 191.793173
サワラ 189.8127135
カナタ 195.881908
カラダ 191.74239500000004
カドマ 196.94274500000003
```
### ランキング

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
1: カナダ (178.1401045)
2: カラダ (182.1072405)
3: カナタ (182.6082715)
4: タバタ (192.4681245)
5: サワラ (194.542944)
6: カドマ (195.139055)
7: バハマ (200.886091)
```

### 重み調整
#### 母音を重視する

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
1: カナデ (188.8045896)
2: サラダ (191.89464220000002)
vowel_ratio=0.8
1: サラダ (183.22081780000002)
2: カナデ (191.4522024)
```

注意点として、音素がbiphononで区別されるため、重みの影響はシンプルな編集距離を使う場合などに比べて、現れにくいです。

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
1: サラダ (194.78591699999998)
2: コノデ (198.155687)
```

上記ではvowel_ratioを0にしたため、「カナダ」と子音が一致する「コノデ」が1位になってほしいですが、2位になってしまっています。
母音の一致など特定の要素を厳密に重視したい場合は、編集距離などを用いる必要があるかもしれません。


## 音韻類似度データ
以下に格納されています。

- [子音距離](src/kanasim/data/biphone/distance_consonants_bi.csv)
- [母音距離](src/kanasim/data/biphone/distance_vowels_bi.csv)
- [カナ-音素対応表](src/kanasim/data/biphone/kana2phonon_bi.csv)

### 子音・母音距離
csv形式で列名は以下です。

- phonon1: 1つめの音素
- phonon2: 2つめの音素
- distance: phonon1とphonon2の距離

phononは無音（sp）、促音（q）、撥音（N）を除いて、隣接音素とのバイフォン（biphone）形式で書かれています（[参考](https://ftp.jaist.ac.jp/pub/osdn.net/julius/47534/Juliusbook-4.1.5-ja.pdf#page=37)）。
子音の場合は直後の母音とのバイフォンです。直後の母音は`+`を挟んで後ろに記述されます。
例えば`b+a`であれば、aという母音の直前のbという子音であることを意味します。
母音の場合は直前の子音とのbiphoneです。直前の子音は`-`を挟んで前に記述されます。
例えば`b-a`はbの直後のaという母音であることを意味します。

distanceは小さいほど、類似度が高いことを意味します。便宜的に「距離」と呼称していますが、phonon1と2を入れ替えると値が異なるため、厳密な距離の定義は満たしません。また同じ音素の「距離」が0にはなりません。

### カナ-音素対応表
csv形式で列名は以下です。
- kana: カナ（モーラ）。ただし長音は直前のカナと合わせて1要素として扱う。
- consonant: カナの子音を表すバイフォン形式の音素。カナが単母音や促音、撥音の場合は「sp」となる。
- vowel: カナの母音または表すバイフォン形式の音素。カナが促音（q）、撥音（N）、無音（sp）の場合は対応する音素となる。
- constant_mono: オプショナル。カナの子音を表すモノフォン形式の音素。
- vowel_mono: オプショナル。カナの母音を表すモノフォン形式の音素。

### カナ類似度の計算
子音距離、母音距離、カナ-音素対応表を用いて、カナ同士の類似度を算出することができます。
例えば、カナを音素で表した後、子音同士、母音同士の距離を足し合わせればよいです。
無音との距離も計算できるため、それらを挿入や削除のコストとみなすことも可能です。

## データ作成方法
音声認識モデル Julius の DNNHMM モデルに基づいて求められました。
以下のやり方を参考にしました。

- [音響モデルから音素間の距離を求める | 見返すかもしれないメモ](https://yaamaa-memo.hatenablog.com/entry/2017/12/17/062435)

簡単に概要だけ述べると、Julius では音素ごとの音響モデル（HMM）が存在するため、2つの音素のHMM同士の「距離」を類似度の指標とします。
HMM同士の「距離」はある音素のHMMの出力が別の音素のHMMから出力される確率として算出します。

計算時間を短くするため、音素やカナについて、計算する対象を限定しています。
音素については、子音は直後の母音との、母音は直前の子音とのバイフォンのみ求めています。カナの類似度であれば、その2種類が重要だと考えたためです。理想的にはトライフォン形式がよかったのですが、計算するペアが多くなりすぎるため、実施していません。また子音の連続や母音の連続もありえるのですが、頻度が少ないと考えられるため、計算していません。
「距離」については、子音同士、母音同士の距離だけを主に計算していません。子音と母音の距離は計算していません。カナの類似度という観点では、子音と母音をそれぞれ対応付ければ基本的には事足りると判断したためです。

## 評価
### 視覚化
上記の方法で算出した音素の位置関係を、2次元尺度法によりマッピングした図を示します。バイフォンだと要素が多すぎるため、モノフォンで計算したものに基づいています。口蓋音、有声音、無声音、母音など、同じジャンルに属する音素がなんとなく近くに存在していることがわかります。

![音素の位置関係](docs/pictures/phonon_distance_2d.png)


### ベースラインとの比較
単語の音韻類似度の指標としてよく用いられる、重みなしのハミング距離と今回の重みを用いたハミング距離の出力を比較します。
単語の音韻類似度の指標として、編集距離やハミング距離がよく用いられますが、今回は替え歌への応用を想定して、検索対象をモーラ数が同じ単語に限定し、ハミング距離が近いものを取得します。重みなしハミング距離は、カナの異同だけだと条件として不利すぎるので、母音および子音のハミング距離を別に計算して足し合わせるようにしています。


重みつきハミング距離（提案）
```
% python scripts/sort_by_weighted_edit_distance.py シマウマ -dt hamming
シラウオ 245.4491025
シマフグ 247.09242
シロウオ 249.183228
シマアジ 252.214438
シマドジョー 253.49853149999998
シマハギ 253.6594945
ピライーバ 253.79645749999997
チゴダラ 254.19401249999999
シマダイ 255.194251
ツマグロ 256.176311
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
重みなしの場合は、「シマアジ」「シマフグ」「シラウオ」が同一のスコアですが、重みありでは「シラウオ」「シマフグ」「シマアジ」の順にスコアの大小が計算されています。おそらく距離データ上、mとrが比較的近いために「シラウオ」が優先されたのだと思います。実際の感覚がこれとあうかはアプリケーションにもよりますし、要検討だと思います。

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
