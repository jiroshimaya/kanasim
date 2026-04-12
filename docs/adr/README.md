# ADR

このディレクトリでは、テンプレートの重要な設計判断を Architecture Decision Record (ADR) として管理します。

説明文を README や instructions に散在させるのではなく、判断の背景・結論・見直し履歴をエージェントと人の両方が追える形で残すことを目的とします。

## 命名規則

- ファイル名は `NNNNN-short-kebab-case.md` 形式にします
- `NNNNN` は 5 桁の連番です
- `short-kebab-case` は判断内容を短く表す英語の kebab-case にします
- 採番は時系列順に増やし、欠番は再利用しません

例:

- `00001-replace-pyright-with-ty.md`
- `00002-store-agent-policy-as-adr.md`

## ステータス

各 ADR の先頭には少なくとも次のメタデータを置きます。

```md
# ADR 00001: Title

- Status: accepted
- Date: 2026-03-21
- Supersedes: none
- Superseded by: none
```

利用するステータスは次の 3 つに限定します。

- `proposed`: 提案中で、まだ標準方針としては採用していない
- `accepted`: 現在有効な方針
- `superseded`: 後続の ADR に置き換えられ、現行方針ではない

## superseded の扱い

- 既存 ADR を置き換えるときは、新しい ADR を追加し、古い ADR は削除しません
- 置き換えられた ADR は `Status: superseded` に更新します
- 古い ADR の `Superseded by` には後続 ADR の番号とファイル名を記載します
- 新しい ADR の `Supersedes` には置き換え元 ADR の番号とファイル名を記載します
- 置き換え関係がない場合は `none` を明記します

## テンプレート

新しい ADR は次のテンプレートから始めます。

```md
# ADR NNNNN: Title

- Status: proposed
- Date: YYYY-MM-DD
- Supersedes: none
- Superseded by: none

## Context

この判断が必要になった背景を書く。

## Decision

採用する判断を簡潔に書く。

## Consequences

得られる利点、受け入れるトレードオフ、次に必要な作業を書く。
```
