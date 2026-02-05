# 画像生成システム 完全仕様書

**Last Updated:** 2026-02-04 22:30
**Version:** 2.0
**Status:** 🔴 CRITICAL - 厳密遵守

## 🚨 絶対原則
1. **この仕様書は絶対**である
2. **変更時は即座に更新**する
3. **実装はこの仕様書に100%準拠**する
4. **仕様書と異なる動作は全てバグ**である

## 1. システム構成

### 1.1 ディレクトリ構造（2026-02-05 更新 - 相対パス化）
```
./image_generation/
├── simple_image_generator.py        # メイン：Pillowプレースホルダー版
└── generate_*_images.py            # 実行：記事別生成スクリプト

./deprecated_gemini_image_gen/
├── parallel_image_generator.py      # 廃止：Gemini API（動作不可）
├── image_generator.py               # 廃止：Gemini API（動作不可）
└── README.md                       # 廃止理由の説明
```

### 1.2 環境変数ファイル（相対パス）
```
../../.env.local  (プロジェクトルート)
```

### 1.3 必須環境変数
```bash
GEMINI_IMAGE_API_KEY_1=AIzaSy...  # 必須
GEMINI_IMAGE_API_KEY_2=AIzaSy...  # 必須
GEMINI_IMAGE_API_KEY_3=AIzaSy...  # 必須
GEMINI_IMAGE_API_KEY_4=AIzaSy...  # 必須
```

## 2. API仕様

### 2.1 使用API
- **プロバイダー**: Google Gemini
- **モデル**: `gemini-1.5-flash` または `gemini-1.5-pro`
- **エンドポイント**: `https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent`

### 2.2 動作確認済みモデル（2026-02-04時点）
| モデル名 | ステータス | 備考 |
|---------|----------|------|
| gemini-1.5-flash | ✅ 動作可能 | テキスト生成のみ |
| gemini-1.5-pro | ✅ 動作可能 | テキスト生成のみ |
| gemini-2.0-flash-exp | ❌ 404エラー | 存在しない |
| gemini-3-pro-image-preview | ❌ 404エラー | 存在しない |

### 2.3 重要な制限事項
**⚠️ Gemini APIは画像を直接生成しない**
- Geminiはテキスト生成AIである
- 画像生成には別のサービス（Imagen, DALL-E等）が必要
- 現在の実装は動作しない

## 3. 実装仕様

### 3.1 parallel_image_generator.py
```python
class ParallelImageGenerator:
    def __init__(self):
        # 環境変数パス（絶対指定）
        env_path = '/Users/tsuruta/Documents/000AGENTS/.env.local'

        # 4つのAPIキー取得
        for i in range(1, 5):
            key = os.getenv(f'GEMINI_IMAGE_API_KEY_{i}')

        # エンドポイント
        self.image_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    def generate_article_images_parallel(self, article_data):
        # 並列処理で画像生成
        # 保存先: /blog_department/articles/YYYYMMDD_slug/images/
```

### 3.2 ファイル命名規則
```
# プレフィックスなし、キーワードベース
[keyword1]_[keyword2]_[keyword3].png

例:
chatgpt_excel_vba.png
ai_failure_analysis.png
automation_efficiency_improvement.png
```

### 3.3 画像保存先（統一仕様）
```
/Users/tsuruta/Documents/000AGENTS/edith_corp/blog_department/articles/YYYYMMDD_slug/
├── article.md           # 記事本文
├── meta.json           # メタデータ
└── images/             # 画像ディレクトリ
    ├── keyword1_keyword2_keyword3.png
    └── ...
```

## 4. 実行手順

### 4.1 標準実行フロー（現在の唯一の方法）
```bash
cd ./image_generation/
python3 generate_[記事名]_images.py
# または
python3 simple_image_generator.py
```

## 5. 現在の仕様と制限事項

### 5.1 APIの制限
**Gemini APIは画像生成機能を持たない**
- Geminiはテキスト生成専用AI
- 画像生成には別のAPIが必要

### 5.2 暫定対策
1. **simple_image_generator.py**を使用
   - Pillowライブラリでプレースホルダー画像生成
   - テキストとグラデーション背景
   - 即座に動作可能

### 5.3 恒久対策（要実装）
1. **Imagen API**の導入
2. **DALL-E API**の導入
3. **Stable Diffusion API**の導入

## 6. 依存関係と前提条件

### 必須ライブラリ
- python-dotenv
- Pillow
- requests

### 環境変数
- GEMINI_IMAGE_API_KEY_1〜4が.env.localに必要

### エラーが発生した場合
- ERROR_LOG.mdに記録
- 仕様に影響する場合のみ本書を更新

## 7. チェックリスト

### 7.1 実装前確認
- [ ] この仕様書を熟読した
- [ ] .env.localが正しい場所にある
- [ ] 4つのAPIキーが設定されている
- [ ] 必要なライブラリがインストール済み

### 7.2 実装時確認
- [ ] ファイルパスは絶対パスを使用
- [ ] エラーハンドリングを実装
- [ ] ファイル名はプレフィックスなし
- [ ] 保存先は統一仕様に準拠

### 7.3 実装後確認
- [ ] 画像が生成された（またはプレースホルダーが生成された）
- [ ] ファイル名が正しい
- [ ] 保存場所が正しい
- [ ] この仕様書を更新した（変更があった場合）

## 8. 更新履歴

| 日時 | バージョン | 変更内容 |
|------|-----------|----------|
| 2026-02-04 22:30 | 2.0 | 完全仕様書作成、問題点明確化 |
| 2026-02-04 19:00 | 1.0 | 初版作成 |

## 9. 責任と義務

### 9.1 開発者の絶対義務
1. **この仕様書を死守する**
2. **仕様書と異なる実装をしない**
3. **変更時は必ず仕様書を更新する**
4. **仕様書の更新を怠らない**
5. **SPECIFICATION_ENFORCEMENT_RULES.mdに従う**

### 9.2 仕様書更新トリガー（必須）
以下の瞬間に即座に仕様書更新：
- エラー発生 → 原因と対処を追記
- 新しいAPIモデル試行 → 結果を追記
- パス変更 → 絶対パスを更新
- 動作確認 → 結果を追記
- 問題発見 → 詳細と対策を追記

### 9.3 仕様書の優先順位
```
0. SPECIFICATION_ENFORCEMENT_RULES.md ← 絶対最優先
1. IMAGE_GENERATION_SPECIFICATIONS.md（本書）
2. CONTENT_MARKETING_SPECIFICATIONS.md
3. コード内のコメント
4. 口頭での指示
```

## 10. 緊急連絡

**現在の状態: 🔴 画像生成API未対応**

**推奨アクション:**
1. simple_image_generator.pyでプレースホルダー生成
2. 画像生成APIの契約・導入を検討
3. この仕様書を基に正しい実装を行う

---

**⚠️ 警告: この仕様書に従わない実装は全て無効とする**

**最終更新者:** Claude
**次回レビュー:** 実装変更時即座