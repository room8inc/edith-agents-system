# メルマガ配信システム 仕様書

## システム概要

Brevo（旧Sendinblue）APIを使ったメルマガ自動配信システム。
EDITHのメルマガ事業部として、コンテンツ作成から配信・効果測定までを自動化する。

### 基本スペック

| 項目 | 内容 |
|---|---|
| 配信基盤 | Brevo 無料プラン |
| 購読者数 | 約315名 |
| 1日の送信上限 | 300通（UTC 0:00 = JST 9:00 リセット） |
| 送信者 | Room8 `<k_tsuruta@room8.co.jp>` |
| 配信リストID | 4（Room8 Newsletter） |
| パーソナライズ | `{{ contact.LASTNAME }}` `{{ contact.FIRSTNAME }}` で姓名挿入 |

### 制約事項

- 315名に対して1日300通制限 → **2日に分けて全員に配信**
- トランザクションメールも300通の枠に含まれる
- 上限超過時は翌日JST 9:00以降に自動リトライ

---

## 配信方式

### 分散送信（通常運用）

1日の300通枠内で、5つの時間帯に分けて送信する。
受信者は毎回ランダムにシャッフルされ、特定の人が特定時間帯に偏らない。

| 時間帯 | 想定ターゲット |
|---|---|
| 09:00 | 朝型・通勤時間 |
| 12:00 | 昼休み |
| 15:00 | 午後の休憩 |
| 18:00 | 帰宅時間 |
| 21:00 | 夜・リラックスタイム |

各グループ約56名（278名 / 5グループ）。残り37名は翌日に配信。

**目的**: スパム判定リスク低減 + 時間帯別の開封率A/Bテスト

### 即時送信

300通以内であれば一括即時送信も可能（`send_newsletter.py` 使用）。

---

## ファイル構成

```
newsletter_department/
├── README.md                  # この仕様書
├── DEPARTMENT_PROMPT.md       # EDITH部門プロンプト（エージェント用）
├── NEWSLETTER_WORKFLOW.md     # 運用ワークフロー詳細
├── requirements.md            # 元の要件定義
├── requirements.txt           # Python依存関係
│
├── tools/                     # 実行ツール群
│   ├── brevo_api.py           # Brevo REST API ラッパー（全API操作の基盤）
│   ├── distributed_sender.py  # 分散送信マネージャー（スケジュール作成→グループ別送信）
│   ├── send_newsletter.py     # 即時送信スクリプト（CLI用）
│   ├── send_manager.py        # 送信ログ管理・重複防止・枠管理
│   ├── content_generator.py   # コンテンツ生成（ブログ通知・イベント告知・ダイジェスト）
│   ├── list_manager.py        # 購読者リスト管理（追加・削除・CSV入出力）
│   ├── import_to_brevo.py     # CSVからBrevoへの一括インポート
│   ├── convert_csv.py         # CSV変換ユーティリティ
│   ├── split_japanese_names.py       # 日本語姓名分割
│   ├── update_names_with_claude.py   # Claude APIで姓名を推定・更新
│   └── schedules/             # 分散送信スケジュールJSON保存先
│
├── templates/
│   └── sample_newsletter.html # HTMLメールテンプレート（Room8デザイン）
│
├── lists/                     # 購読者CSVデータ
│   ├── brevo_ready.csv        # Brevoインポート用CSV
│   └── brevo_with_names.csv   # 姓名付きCSV
│
├── campaigns/                 # 配信キャンペーン記録（JSON）
└── logs/                      # 送信ログ
```

---

## 主要ツールの役割

### brevo_api.py — API基盤

Brevo REST API (`https://api.brevo.com/v3`) のラッパークラス。
他の全ツールがこれを通じてBrevoと通信する。

**提供機能**: メール送信 / キャンペーン作成・送信 / リスト管理 / 連絡先CRUD / CSV インポート / 統計取得

### distributed_sender.py — 分散送信

受信者を時間帯グループに分割し、スケジュールJSONを生成・管理する。

```bash
# スケジュール作成（リストID 4 から受信者取得→5グループに分割）
python3 distributed_sender.py create "キャンペーン名"

# 指定グループに送信（slot_index: 0=09:00, 1=12:00, ...）
python3 distributed_sender.py send schedules/xxx.json 0

# 進捗確認
python3 distributed_sender.py status schedules/xxx.json
```

### send_newsletter.py — 即時送信

HTMLファイルと件名を指定して一括送信。300通超えた分は翌日に自動繰り越し。

```bash
python3 send_newsletter.py "件名" "./templates/sample_newsletter.html"
```

### content_generator.py — コンテンツ生成

テーマに応じたメルマガ本文を自動生成。

```bash
python3 content_generator.py blog    # ブログ更新通知
python3 content_generator.py event   # イベント告知
python3 content_generator.py digest  # 月次ダイジェスト
```

---

## 運用フロー

```
鶴田さん「メルマガ送って」
    ↓
EDITH: コンテンツ案を複数提示
    ↓
鶴田さん: 選ぶ or 修正指示
    ↓
EDITH: HTMLテンプレート適用 → 分散送信スケジュール作成
    ↓
自動配信: 09:00 / 12:00 / 15:00 / 18:00 / 21:00
    ↓
翌日: 残り分を配信 + 効果測定レポート
```

---

## セットアップ

### 依存関係

```bash
pip install -r requirements.txt
```

### APIキー

環境変数 `BREVO_API_KEY` を設定、または `.env` ファイルに記載。

```bash
export BREVO_API_KEY="your-api-key"
```

### 接続テスト

```bash
python3 tools/brevo_api.py test
```

---

## 実装状況

### 完了

- Brevo API連携（送信・リスト管理・統計取得）
- 分散送信マネージャー（5時間帯分割・シャッフル・進捗管理）
- 即時送信スクリプト（300通枠管理・繰り越し）
- 購読者リスト管理（CSV入出力・姓名分割・Brevoインポート）
- HTMLテンプレート（Room8デザイン・パーソナライズ対応）
- コンテンツ生成（ブログ通知・イベント告知・ダイジェスト）

### 未実装

- テンプレートのバリエーション拡充（イベント用・月報用等）
- 開封率・クリック率の詳細分析レポート
- 時間帯別パフォーマンス自動最適化
- cron連携による完全自動配信
- A/Bテスト自動化（件名・CTA）
