# ファイル構成仕様書

**最終更新:** 2026-02-05
**管理者:** EDITH Corp Blog Department

## 1. 現在のディレクトリ構造

```
./ (blog_department/)
├── 📁 articles/                    # 完成記事保管
├── 📁 image_generation/            # 画像生成システム
├── 📁 generated_articles/          # ⚠️ 旧仕様・使用禁止
├── 📁 memory_system/               # ナレッジベース
├── 📁 search_console/              # SEO設定
├── 📁 seo_specialist_ashigaru/    # SEO専門システム
├── 📁 series_management/           # シリーズ記事管理
├── 📁 wordpress_posting/           # WordPress投稿
├── 📁 writing/                     # 執筆支援
└── 📄 仕様書・ドキュメント類
```

## 2. 画像生成システム（/image_generation/）

### 現在のファイル構成（2026-02-05 クリーンアップ済み）
```
image_generation/
├── simple_image_generator.py        # ✅ メイン画像生成（Pillowプレースホルダー）
└── generate_*_images.py            # ✅ 記事別生成スクリプト
```

### 各ファイルの役割と状態

| ファイル名 | 状態 | 用途 |
|-----------|------|------|
| simple_image_generator.py | ✅ 動作可能 | Pillowでプレースホルダー生成 |
| generate_*_images.py | ✅ 動作可能 | 記事別実行スクリプト |

### 廃止・移動済みファイル（/deprecated_gemini_image_gen/）
- parallel_image_generator.py - Gemini APIでの画像生成試行（動作不可）
- image_generator.py - Gemini APIでの画像生成試行（動作不可）

## 3. 仕様書・ドキュメント

### 必須仕様書（優先順）
```
1. SPECIFICATION_ENFORCEMENT_RULES.md  # 仕様書管理ルール
2. SPECIFICATIONS_INDEX.md            # 仕様書インデックス
3. FILE_STRUCTURE_SPECIFICATION.md    # 本書（ファイル構成）
4. IMAGE_GENERATION_SPECIFICATIONS.md # 画像生成仕様
5. CONTENT_MARKETING_SPECIFICATIONS.md # 部門統括仕様
```

### その他ドキュメント
```
- ERROR_LOG.md                        # エラーログ
- writing_guidelines.md               # 執筆ガイドライン
- seo_strategy.md                    # SEO戦略
- article_structure_design.md        # 記事構成設計
```

## 4. クリーンアップ実施済み（2026-02-05）

### 削除済み
- `generated_articles/` - 旧仕様ディレクトリ

### 移動済み（→ deprecated_gemini_image_gen/）
- `parallel_image_generator.py` - Gemini API画像生成（動作不可）
- `image_generator.py` - Gemini API画像生成（動作不可）

### 今後の方針
- 画像生成APIを導入時に新規実装
- 当面はsimple_image_generator.pyを使用

## 5. 記事ディレクトリ構造（/articles/）

### 標準構成
```
articles/YYYYMMDD_slug/
├── article.md           # 記事本文（必須）
├── meta.json           # メタデータ（必須）
├── images/             # 画像ディレクトリ（必須）
│   ├── keyword1_keyword2.png
│   └── ...
└── wordpress/          # WordPress投稿データ（自動生成）
    └── publish_data.json
```

## 6. 環境変数・設定ファイル

### 重要な設定ファイル
```
../../.env.local (プロジェクトルート)    # 環境変数
```

### 必要な環境変数
```bash
GEMINI_IMAGE_API_KEY_1=AIza...  # 現在は画像生成に使用不可
GEMINI_IMAGE_API_KEY_2=AIza...  # 同上
GEMINI_IMAGE_API_KEY_3=AIza...  # 同上
GEMINI_IMAGE_API_KEY_4=AIza...  # 同上
```

## 7. クリーンアップ推奨事項

### 即座に実行可能
1. `generated_articles/` ディレクトリの内容を確認し、必要なら`articles/`に移動

### 将来的に実行
1. 画像生成APIが決定したら、不要なスクリプトを`deprecated/`に移動
2. 使用しないAPIキーを.env.localから削除

## 8. ファイル命名規則

### スクリプト
- 汎用: `[機能]_generator.py`
- 記事別: `generate_[記事名]_images.py`

### 仕様書
- 大文字スネークケース: `SPECIFICATION_NAME.md`
- 通常ドキュメント: `lowercase_name.md`

### 記事関連
- ディレクトリ: `YYYYMMDD_slug/`
- 画像: `keyword1_keyword2_keyword3.png`（プレフィックスなし）

---

**重要:** このファイル構成に変更があった場合は、即座に本書を更新すること