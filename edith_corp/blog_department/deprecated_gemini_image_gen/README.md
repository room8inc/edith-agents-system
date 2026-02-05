# Deprecated - Gemini画像生成

**廃止日:** 2026-02-05
**理由:** Gemini APIは画像生成機能を持たない（テキスト生成専用）

## 保管ファイル

- `parallel_image_generator.py` - 4つのAPIキーで並列処理を試みた実装
- `image_generator.py` - 単一APIキーでの実装

## 重要な知見

これらのファイルは以下の理由で動作しません：

1. **Gemini APIの制限**
   - Geminiはテキスト生成AI
   - 画像生成機能なし
   - `generateContent`エンドポイントはテキストのみ返す

2. **試行したモデル**
   - gemini-2.0-flash-thinking-exp-1219 → 404
   - gemini-2.0-flash-exp → 404
   - gemini-1.5-flash → 200 OK（ただし画像生成不可）
   - gemini-1.5-pro → 200 OK（ただし画像生成不可）

## 今後の方針

画像生成が必要な場合は以下を検討：

1. **Imagen API** - Google Cloud Platform
2. **DALL-E API** - OpenAI
3. **Stable Diffusion API** - 各種サービス
4. **Pillow** - プレースホルダー画像（現在使用中）

## 注意

これらのファイルは参考のために保管していますが、使用しないでください。