# コンテンツマーケ部門 標準仕様書

**Last Updated:** 2026-02-04
**Version:** 1.0
**管理責任者:** コンテンツマーケ部門Agent

## 1. ディレクトリ構造仕様

### 基本構造
```
./ (プロジェクトルート: blog_department/)
├── articles/                    # 完成記事保管（公開用）
│   └── YYYYMMDD_slug/          # 記事専用ディレクトリ
│       ├── article.md          # メイン記事ファイル
│       ├── meta.json          # SEO・投稿メタデータ
│       ├── images/            # 記事専用画像
│       └── wordpress/         # WordPress投稿データ
├── research/                   # 調査・リサーチ資料
├── search_console/            # SEO・検索コンソール設定
├── seo_specialist_ashigaru/   # SEO専門システム
├── keyword_strategy/          # キーワード戦略
├── image_generation/          # 画像生成システム（Gemini 3 Pro + 並列処理）
├── series_management/         # シリーズ記事管理
└── memory_system/            # ナレッジベース・記憶システム
```

### 重要な設定ファイル場所
- **戦略設定:** `memory_system/knowledge_base/strategies/current_strategy.json`
- **シリーズ管理:** `series_management/series_management/series_database.json`
- **検索コンソール:** `search_console/config/search_console_config.json`

## 2. ファイル命名規則・ディレクトリ構造

### ⚠️ 重要な仕様変更履歴（2026-02-04）

**旧仕様（廃止）:**
```
generated_articles/
└── [記事名].md  # mdファイルのみ、画像生成なし
```

**現行仕様（必須遵守）:**
```
articles/YYYYMMDD_slug/
├── article.md    # メイン記事
├── meta.json     # SEO・投稿データ
├── images/       # 画像ディレクトリ（必須）
└── wordpress/    # WordPress投稿データ
```

**変更理由:**
- 日付ディレクトリで記事管理の改善
- 画像生成機能の追加
- WordPress投稿との完全統合

### 記事ディレクトリ命名
```
YYYYMMDD_slug-format
例: 20260204_failure-small-business-chatgpt
```

### 記事ファイル構成（必須）
```
articles/YYYYMMDD_slug/
├── article.md                 # メイン記事（必須）
├── meta.json                  # SEO・投稿データ（必須）
├── images/                    # 画像ディレクトリ（必須）
│   ├── featured.png          # アイキャッチ画像
│   ├── section[N]_[title].png # セクション画像
│   └── ...
└── wordpress/                 # WordPress投稿データ（自動生成）
    └── publish_data.json      # 投稿ID・URL等
```

### 画像ファイル命名（2026-02-04更新）

**最新仕様（コンテンツベース命名 - プレフィックスなし）:**
```
[keyword1]_[keyword2]_[keyword3].png

例:
ai_failure_analysis.png              # アイキャッチ（AI・失敗・分析）
ai_fax_sme.png                      # セクション1（AI・FAX・中小企業）
chatgpt_excel_digitization.png       # セクション2（ChatGPT・Excel・デジタル化）
tools_roi_effect.png                # セクション3（ツール・ROI・効果）
```

**キーワード抽出ロジック:**
- 日本語ビジネス用語 → 英語短縮形（AI→ai, 中小企業→sme, ROI→roi）
- 数値 → num[数字]（300万→num300）
- 英単語 → そのまま使用（Excel→excel）
- 最大3キーワード（プレフィックスなしで短縮）

**旧仕様（廃止）:**
```
hero_ai_chatgpt_sme.png        # 廃止（プレフィックスあり版）
section1_ai_chatgpt_fax.png    # 廃止（プレフィックスあり版）
featured.png                   # 廃止（旧旧仕様）
section[N]_[title].png         # 廃止（旧旧仕様）
```

## 3. 記事作成標準フロー

### Step 1: 企画・調査
1. **キーワード調査** (`keyword_strategy/`で管理)
2. **競合分析** (`research/`に保存)
3. **シリーズ確認** (`series_management/series_database.json`更新)

### Step 2: 記事作成（必須フロー）
1. **ディレクトリ作成:** `articles/YYYYMMDD_slug/` （**generated_articles/は使用禁止**）
2. **記事執筆:** `article.md`作成
3. **メタデータ作成:** `meta.json`作成
4. **画像生成:** `images/`配下に保存（**画像生成は必須**）

**⚠️ 絶対禁止:** `generated_articles/`への保存（旧仕様）

### Step 3: 品質管理
1. **SEOチェック** (seo_specialist_ashigaru使用)
2. **内容確認** (EDITH承認)
3. **画像確認** (全画像正常表示確認)

### Step 4: 公開準備
1. **WordPress下書き投稿** (自動)
2. **publish_data.json生成** (自動)
3. **最終承認待ち** (EDITH判断)

## 4. 画像生成システム仕様

### ⚠️ 重要な制限事項（2026-02-04判明）
**Gemini APIは画像生成機能を持たない** - テキスト生成のみ対応

### 詳細仕様
**完全仕様書を参照**: `/Users/tsuruta/Documents/000AGENTS/edith_corp/blog_department/IMAGE_GENERATION_SPECIFICATIONS.md`

### 現在の対処法
```bash
# プレースホルダー画像生成（動作保証）
cd /Users/tsuruta/Documents/000AGENTS/edith_corp/blog_department/image_generation/
python3 simple_image_generator.py
```

### 保存先統一（2026-02-04変更）
**変更前（分離）:**
```
記事: /blog_department/articles/YYYYMMDD_slug/article.md
画像: /image_generation/articles/YYYYMMDD_slug/images/
```

**変更後（統一）:**
```
/blog_department/articles/YYYYMMDD_slug/
├── article.md
├── meta.json
├── images/
│   ├── ai_failure_analysis.png
│   └── ...
└── wordpress/
```

### 生成枚数別の処理時間
| 画像数 | 並列処理時間 | 従来処理時間 | 負荷分散例 |
|--------|-------------|-------------|------------|
| 4枚 | ~30秒 | ~20分 | [1,1,1,1] |
| 6枚 | ~40秒 | ~30分 | [2,2,1,1] |
| 8枚 | ~50秒 | ~40分 | [2,2,2,2] |
| 10枚 | ~70秒 | ~50分 | [3,3,2,2] |

## 5. 品質管理基準

### 記事品質チェックリスト
- [ ] タイトル: キーワード含有・魅力的
- [ ] 導入: 問題提起・共感獲得
- [ ] 構成: 論理的・読みやすい
- [ ] 具体例: 数値・事例含有
- [ ] 結論: 実行可能なアクション
- [ ] SEO: メタデータ完備

### 画像品質基準
- [ ] アイキャッチ: 1200x630px推奨
- [ ] セクション画像: コンテンツと関連性
- [ ] ファイルサイズ: 1MB以下
- [ ] alt text: 適切な説明文

### メタデータ必須項目
```json
{
  "title": "記事タイトル",
  "slug": "url-slug",
  "meta_description": "120文字以内説明",
  "keywords": ["キーワード1", "キーワード2"],
  "category": "カテゴリ",
  "tags": ["タグ1", "タグ2"],
  "featured_image": "images/featured.png",
  "created_at": "2026-02-04T19:13:00",
  "seo_score": 85
}
```

## 5. 緊急時対応手順

### セッション切断時の復旧方法
1. **記事場所確認:**
   ```bash
   find /Users/tsuruta/Documents/000AGENTS/edith_corp/blog_department/articles -name "*keyword*"
   ```

2. **最新記事確認:**
   ```bash
   ls -la /Users/tsuruta/Documents/000AGENTS/edith_corp/blog_department/articles/
   ```

3. **仕様書確認:** 本ファイルを参照

### 実働部隊への緊急指示
- **記事作成Agent:** この仕様書の「記事作成標準フロー」に従う
- **画像生成Agent:** ファイル命名規則を厳守
- **SEOAgent:** メタデータ必須項目を確認
- **WordPress投稿Agent:** publish_data.json生成を確認

## 6. 部門間連携仕様

### EDITH（統括管理）への報告形式
```
Status: [完了/進行中/要確認]
What was done: [具体的作業内容]
Weakness detected: [問題点・改善点]
Improvement proposal: [改善案]
Need approval? [Yes/No]
```

### 他部門との連携
- **戦略企画部門:** キーワード戦略・市場分析
- **技術開発部門:** WordPress API・自動化システム
- **分析部門:** パフォーマンス測定・改善提案

## 7. 自動保存・バックアップ仕様

### 重要データの自動保存
- **記事作成中:** 30分毎の自動保存
- **設定変更時:** 即座にJSON更新
- **シリーズ管理:** 記事公開時に自動更新

### バックアップ対象
- `articles/` 全ディレクトリ
- `memory_system/knowledge_base/`
- `series_management/series_database.json`
- 本仕様書

---

## 🚨 仕様変更時の絶対更新義務

### 仕様変更を認識した瞬間→即座更新（例外なし）

#### 即座更新が必要なケース
- ディレクトリ構造の変更
- ファイル命名規則の変更
- 記事作成フローの変更
- 品質基準の変更
- WordPress投稿方法の変更

#### 更新手順（30秒以内実行）
1. **本仕様書の即座更新**
2. **EDITH_MASTER_SPECIFICATIONS.mdへの反映**
3. **関連Agentへの変更通知**

#### 絶対禁止事項
- 「後で更新」の判断 ❌
- 「次回更新」の判断 ❌
- 口頭・記憶による仕様管理 ❌

---

**重要:** この仕様書は、セッション切断やエラー発生時の復旧基準として機能する。
すべての実働部隊は、作業前に本仕様書を確認すること。
**仕様変更時は他のすべての作業を停止し、即座に更新すること。**

**緊急連絡先:** EDITH（統括管理・戦略判断）