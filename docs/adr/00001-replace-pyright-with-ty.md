# ADR 00001: Replace pyright with ty

- Status: accepted
- Date: 2026-03-21
- Supersedes: none
- Superseded by: none

## Context

このテンプレートは AI アシスタント、とくに Copilot CLI との協働を前提にしています。

型チェック系の実行経路としては、`pyproject.toml` の `check` タスク、`.pre-commit-config.yaml` のローカル hook、CI の `uv run pre-commit run --all-files` が使われています。

`pyright` を使い続ける案もありましたが、このテンプレートでは AI エージェントがローカルで何度もチェックを回す前提があるため、実行時間の短さをより重視しました。主な判断理由は、型チェックをより高速に回せる構成へ寄せることです。

2026-03-21 の `pyright` から `ty` への移行では、実際に次のような段階的な調整が発生しました。

- `a7c5bb8`: `pyproject.toml`、`taskipy`、pre-commit hook を `pyright` から `ty` に置き換えた
- `e1bb0b9`: lockfile にまだ `pyright` が残っていたため、CI で一時的に `ty` を追加インストールする対応を入れた
- `ba0114d`: 利用可能な版に合わせて `ty==0.0.24` に固定し、CI の依存解決を安定させた
- `45c08f2`: 実行コマンドを `uv run ty check src` にそろえ、`pass_filenames: false` を加え、暫定 CI 対応を外した

## Decision

このテンプレートでは、型チェック系の標準ツールを `pyright` ではなく `ty` とします。

主な理由は速度です。AI エージェントと人が反復的に型チェックを実行するテンプレートでは、1 回ごとの差が小さくても累積の待ち時間が効いてきます。そのため、このテンプレートでは型チェックの実行速度を優先し、`ty` を標準に採用します。

採用する実行経路は次のとおりです。

- 依存関係は `pyproject.toml` の `dev` グループで `ty==0.0.24` を利用する
- ローカルの標準コマンドは `uv run ty check src` とする
- pre-commit hook も `uv run ty check src` を使い、`pass_filenames: false` を設定して明示的に `src` を対象にする
- CI は追加の暫定インストールを行わず、`uv sync --all-extras` と pre-commit 実行だけで再現できる状態を維持する
- 今後この判断を見直す場合は、新しい ADR を追加し、この ADR を supersede する

## Consequences
型チェックをより短い待ち時間で回しやすくなるため、開発者とエージェントの双方が反復を進めやすくなります。
