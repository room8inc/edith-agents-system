# 記事ディレクトリ構造設計

## 新しい記事管理構造

### 📁 記事単位でのディレクトリ管理
```
blog_department/
└── articles/
    ├── 20260204_ai_failure_analysis/
    │   ├── article.md                    # 記事本文
    │   ├── meta.json                     # 記事メタデータ
    │   ├── images/
    │   │   ├── featured.png              # アイキャッチ画像
    │   │   ├── section1_problem.png      # セクション1用画像
    │   │   ├── section2_solution.png     # セクション2用画像
    │   │   └── section3_implementation.png # セクション3用画像
    │   └── wordpress/
    │       ├── publish_data.json         # WordPress投稿データ
    │       └── upload_status.json        # アップロード状況
    │
    ├── 20260205_excel_escape_methods/
    │   ├── article.md
    │   ├── meta.json
    │   ├── images/
    │   │   ├── featured.png
    │   │   ├── section1_excel_hell.png
    │   │   ├── section2_alternatives.png
    │   │   └── section3_migration.png
    │   └── wordpress/
    │       ├── publish_data.json
    │       └── upload_status.json
    │
    └── template/                         # 新規記事用テンプレート
        ├── article_template.md
        ├── meta_template.json
        └── images/.gitkeep
```

### 📋 meta.json の構造
```json
{
  "title": "『AI導入失敗』で大失敗した中小企業の現実分析",
  "slug": "ai-failure-analysis",
  "author": "鶴田（Room8）",
  "created_at": "2026-02-04T10:00:00",
  "category": "AI活用",
  "tags": ["AI導入", "失敗事例", "中小企業", "デジタル化"],
  "seo": {
    "primary_keywords": ["AI導入 失敗", "中小企業 AI"],
    "meta_description": "AI導入で失敗する中小企業の典型的パターンを分析。FAX使用企業が陥る罠と、現実的な解決策を紹介。",
    "expected_traffic": 1200
  },
  "images": {
    "featured": "images/featured.png",
    "sections": [
      {"section": "問題分析", "image": "images/section1_problem.png"},
      {"section": "解決策", "image": "images/section2_solution.png"},
      {"section": "実装手順", "image": "images/section3_implementation.png"}
    ]
  },
  "wordpress": {
    "status": "draft",
    "post_id": null,
    "published_at": null,
    "url": null
  },
  "series": {
    "series_id": "ai活用_001",
    "position": 1,
    "next_article": "Excel地獄から脱出する7つの実践的手順"
  }
}
```

## メリット

### ✅ **管理面**
- 記事と関連ファイルが1箇所に集約
- バージョン管理が容易
- 削除・移動時のファイル漏れなし

### ✅ **開発面**
- 画像パスの相対参照が可能
- WordPressアップロード時のファイル整合性確保
- 記事単位でのバックアップ・復元が簡単

### ✅ **運用面**
- 記事の公開状況が一目でわかる
- SEOデータとコンテンツの一元管理
- シリーズ記事の関連性管理

### ✅ **WordPress連携面**
- 画像のバッチアップロード
- メタデータの自動設定
- 公開ステータスの追跡

## 実装方針

### 1. 記事生成時
```python
# 日付ベースのディレクトリ作成
article_dir = f"articles/{datetime.now().strftime('%Y%m%d')}_{slug}/"

# 必要ディレクトリの自動作成
create_directories([
    f"{article_dir}images/",
    f"{article_dir}wordpress/"
])
```

### 2. 画像生成時
```python
# セクション毎に画像生成
for section in sections:
    image_path = f"{article_dir}images/section_{section.id}.png"
    generate_image(section.prompt, image_path)
```

### 3. WordPress投稿時
```python
# 記事とすべての画像をバッチアップロード
upload_article_with_images(article_dir)
```

この構造にすれば、記事作成から公開まで完全に自動化できます！