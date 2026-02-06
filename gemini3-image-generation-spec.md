# Gemini 3 画像生成 API 仕様書

## 概要

Gemini 3で画像生成を行うには **Nano Banana Pro**（`gemini-3-pro-image-preview`）を使用する。
通常のgenerateContent APIで、テキストと画像を同時に返せるネイティブマルチモーダルモデル。

---

## モデルID

| 用途 | モデルID | 備考 |
|------|---------|------|
| 高品質画像生成（推奨） | `gemini-3-pro-image-preview` | Nano Banana Pro。4K対応、テキストレンダリング最良 |
| 高速・低コスト画像生成 | `gemini-2.5-flash-image` | Nano Banana。速度重視 |

---

## エンドポイント

```
POST https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent
```

ヘッダー:
```
x-goog-api-key: {API_KEY}
Content-Type: application/json
```

---

## 基本リクエスト構造

### テキストから画像生成

```json
{
  "contents": [{
    "parts": [
      {"text": "プロンプトテキスト"}
    ]
  }],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"],
    "imageConfig": {
      "aspectRatio": "16:9",
      "imageSize": "2K"
    }
  }
}
```

### 画像＋テキストから画像編集

```json
{
  "contents": [{
    "parts": [
      {"text": "この画像の背景を夕焼けにして"},
      {
        "inline_data": {
          "mime_type": "image/jpeg",
          "data": "<BASE64エンコードされた画像データ>"
        }
      }
    ]
  }],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"],
    "imageConfig": {
      "aspectRatio": "16:9",
      "imageSize": "2K"
    }
  }
}
```

---

## imageConfig パラメータ

### aspectRatio（アスペクト比）

指定可能な値:
- `"1:1"` — 正方形
- `"2:3"`, `"3:2"`
- `"3:4"`, `"4:3"`
- `"4:5"`, `"5:4"`
- `"9:16"`, `"16:9"` — 縦長/横長ワイド
- `"21:9"` — ウルトラワイド

### imageSize（解像度）

指定可能な値:
- `"1K"` — 標準
- `"2K"` — 高解像度
- `"4K"` — 最高解像度（Nano Banana Proのみ）

---

## レスポンス構造

レスポンスの `candidates[0].content.parts` に、テキストパートと画像パートが混在して返る。

```json
{
  "candidates": [{
    "content": {
      "parts": [
        {
          "text": "画像を生成しました。..."
        },
        {
          "inlineData": {
            "mimeType": "image/png",
            "data": "<BASE64エンコードされた画像データ>"
          }
        }
      ]
    }
  }]
}
```

### レスポンスの処理方法

```javascript
// parts をループして type を判定
for (const part of response.candidates[0].content.parts) {
  if (part.text) {
    console.log(part.text);
  } else if (part.inlineData) {
    // Base64デコードして画像ファイルに保存
    const buffer = Buffer.from(part.inlineData.data, "base64");
    fs.writeFileSync("output.png", buffer);
  }
}
```

---

## Google検索グラウンディング（リアルタイムデータ連携）

`tools` に `google_search` を追加すると、モデルがリアルタイム情報を取得してから画像を生成できる。

```json
{
  "contents": [{
    "parts": [
      {"text": "東京の現在の天気をインフォグラフィックで生成して"}
    ]
  }],
  "tools": [{"googleSearch": {}}],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"],
    "imageConfig": {
      "aspectRatio": "16:9",
      "imageSize": "4K"
    }
  }
}
```

---

## マルチターン（会話型）画像編集

マルチターンで画像を編集する場合、会話履歴を `contents` 配列に含める。
**重要: 思考シグネチャ（thoughtSignature）を必ず保持・返送すること。**

### リクエスト例（2ターン目: 編集）

```json
{
  "contents": [
    {
      "role": "user",
      "parts": [{"text": "サイバーパンクな都市を生成して"}]
    },
    {
      "role": "model",
      "parts": [
        {
          "text": "サイバーパンクな都市を生成しました...",
          "thoughtSignature": "<Signature_D>"
        },
        {
          "inlineData": {"mimeType": "image/png", "data": "<BASE64>"},
          "thoughtSignature": "<Signature_E>"
        }
      ]
    },
    {
      "role": "user",
      "parts": [{"text": "昼間のシーンに変更して"}]
    }
  ],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"]
  }
}
```

### 思考シグネチャのルール（画像生成/編集）

1. モデルのレスポンスの**最初のパート**（テキストでも画像でも）に `thoughtSignature` が付く
2. **すべての `inlineData`（画像）パート**にも `thoughtSignature` が付く
3. 次のターンで編集をリクエストする際、これらの署名を**すべてそのまま返送**する必要がある
4. 署名が欠けると **400エラー** になる

SDKのchat機能を使う場合は自動で処理されるが、REST APIを直接使う場合は手動管理が必要。

---

## Python SDK での使用例

### テキストから画像生成

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="東京の現在の天気をインフォグラフィックで生成して",
    config=types.GenerateContentConfig(
        tools=[{"google_search": {}}],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="4K"
        )
    )
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("output.png")
```

### マルチターン編集（Chat API）

```python
from google import genai
from google.genai import types

client = genai.Client()

chat = client.chats.create(
    model="gemini-3-pro-image-preview",
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        tools=[{"google_search": {}}]
    )
)

# 1ターン目: 生成
response = chat.send_message("光合成のインフォグラフィックを作って")

# 2ターン目: 編集（thoughtSignatureはSDKが自動管理）
response = chat.send_message(
    "スペイン語に翻訳して",
    config=types.GenerateContentConfig(
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="2K"
        )
    )
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif image := part.as_image():
        image.save("edited.png")
```

---

## JavaScript (Node.js) SDK での使用例

```javascript
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

const ai = new GoogleGenAI({});

const response = await ai.models.generateContent({
  model: "gemini-3-pro-image-preview",
  contents: "東京タワーの水彩画を生成して",
  config: {
    tools: [{ googleSearch: {} }],
    imageConfig: {
      aspectRatio: "16:9",
      imageSize: "2K"
    }
  }
});

for (const part of response.candidates[0].content.parts) {
  if (part.text) {
    console.log(part.text);
  } else if (part.inlineData) {
    const buffer = Buffer.from(part.inlineData.data, "base64");
    fs.writeFileSync("output.png", buffer);
  }
}
```

---

## 参照画像の使用（最大14枚）

Nano Banana Pro は最大14枚の参照画像を入力できる:
- オブジェクト画像: 最大6枚（高忠実度で最終画像に含める）
- 人物画像: 最大5枚（キャラクター一貫性の維持）

```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        "これらの人物のオフィス集合写真を作って",
        Image.open("person1.png"),
        Image.open("person2.png"),
        Image.open("person3.png"),
    ],
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio="5:4",
            image_size="2K"
        )
    )
)
```

---

## Interactions API（新API・ベータ）

より簡潔なインターフェース。状態管理が簡素化される。

```python
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3-pro-image-preview",
    input="未来都市の画像を生成して",
    generation_config={
        "image_config": {
            "aspect_ratio": "9:16",
            "image_size": "2k"
        }
    }
)

for output in interaction.outputs:
    if output.type == "image":
        import base64
        with open("output.png", "wb") as f:
            f.write(base64.b64decode(output.data))
```

---

## 料金

| 項目 | 料金 |
|------|------|
| テキスト入力 | $2 / 100万トークン |
| 画像出力 | $0.134 / 画像（解像度により変動） |

---

## 注意事項

- 全生成画像にSynthIDウォーターマークが含まれる
- `responseModalities` に `"IMAGE"` を含めないと画像は返されない
- 温度パラメータはデフォルト `1.0` を推奨（変更するとループや品質低下のリスク）
- マルチターン編集時は `thoughtSignature` の保持が必須（REST API直接使用時）
- SDKのChat機能を使えば `thoughtSignature` は自動管理される
