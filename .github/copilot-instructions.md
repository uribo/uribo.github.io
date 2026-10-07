# Copilot への指示（uribo.github.io）

瓜生真也の研究者個人サイト（Quarto、GitHub Pages）。内容は QMD のヘッダ（front matter）と YAML で持ち、スキーマは `docs/content-model.md` が正本。主なディレクトリは `publications/items/`（論文）、`research/<slug>/`（研究プロジェクト）、`data-software/items/`（データ・R パッケージ）、`about/`、`scripts/`（点検と書誌の同期）。全体の規則は `AGENTS.md` にあり、ここでは繰り返さない。

**指摘は日本語で書く。**

CI（`check.yml`）が PR ごとに `uv run scripts/validate.py` と `quarto render` を走らせる。スキーマ違反、論文ヘッダと Crossref の食い違い、R パッケージのバッジ行の食い違いは CI が止めるので、同じことを指摘しなくてよい。点検スクリプトが判定できない次の点を優先して見てほしい。

## この repo で優先して見てほしいこと

- **ページ間で同じ事実が食い違っていないか。** トップの数値の帯（論文数、研究軸の数、進行中のプロジェクト数、研究費の件数、言語版の数、種数）と、`publications/items/`・`research/` の実際の件数や本文の数値が一致しているか。研究ページ・トップ・About に書き写した数値（例: 種数、正答率、取引件数）が、その論文ファイルの本文と一致しているか。
- **本文の主張が、引用している論文やデータの中身を越えていないか。** 規模や効果を、論文に無い言い方で強めていないか（例: 落札済みの取引を「出品」と書く）。
- **公開してよい情報だけか。** Funding 節には採択済み・保有中の研究費だけを書く（申請中・不採択・内部の配分は書かない）。About の Talks & Outreach では、公開募集の催しだけ主催者名を出し、非公開の研修や業務依頼は聞き手の種類だけを書く。個人名・未公表の事業名・未発表の数値が入っていないか。
- **日付の過ぎた記述や撤回された記述が残っていないか。** 予定として書いた講演・講座が中止になっていないか、"forthcoming" や "in press" のまま刊行済みになっていないか、`status: active` のプロジェクトに TODO の節が残っていないか。
- **機械が持つ欄を手で直していないか。** DOI のある論文の `title`・`author`・`year`・`venue`・`locator` と、本文の "Published in" 行は `scripts/sync_refs.py` が書く。出版社側の誤りは `publications/overrides.yml` に理由つきで記録する。`overrides.yml` の新しい項目は、`reason` が実際の出版社の誤りを説明しているか（好みの書き換えでないか）を見る。
- **`scripts/` の変更で照合が弱くなっていないか。** 比較を緩める（大文字小文字・句読点を無視する、例外を黙って増やす）、エラーを警告に下げる、`validate.py` がネットワークに依存する、といった変更。

## 指摘しなくてよいこと

- **Markdown・QMD 散文のハードラップ**。段落・リスト項目は 1 行で書いて soft-wrap させる規約なので、行が長いことを問題にしない。
- **Crossref 由来の表記**。論文名の大文字小文字、曲線のアポストロフィ（’）、著者名の形（"Takehiko I Hayashi" など）は Crossref の記録に従っている。論文ごとに表記が揃っていなくても指摘しない。
- 英文の文体の好み、日本語の語尾の統一。
- 生成物と資産: `publications/references.json`（Crossref の取得結果）、`_freeze/`、`assets/illustrations/*.svg` のパスデータ。
- About の書籍・講演、ヒーロー、`join/` にある日本語（`AGENTS.md` で許可済み）。

## 記法の規約

- コミットメッセージは Conventional Commits。scope は `about`, `content`, `data-software`, `home`, `illustrations`, `publications`, `research`, `github`, `ci`。
- DOI は URL を付けない形（`10.xxxx/...`）で書く。雑誌名の欄は `venue`（`journal` は Quarto の予約語なので使わない）。
- 論文へのリンク文字列は `Title (YEAR, Venue)` か `Surname et al. YEAR, Venue` の形にする（`validate.py` が照合する）。
- R パッケージは `cran: available | archived` を持ち、公開中は CRAN の DOI、取り下げ済みは DOI なしで GitHub へリンクする。本文に版番号を書かない。

## 触れない方が良いもの

- `publications/references.json` の値を直す提案はしない。直すなら `overrides.yml` に理由つきで足す。
- `_freeze/` を消す、計算を再実行させる提案はしない（計算を伴う文書は人が手元で実行して凍結する運用）。
- Talks & Outreach の非公開の催しに主催者名を足す提案はしない。
