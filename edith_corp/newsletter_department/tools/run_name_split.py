#!/usr/bin/env python3
"""
姓名分割実行スクリプト（APIキー直接指定版）
"""

import json
import os
import time
import google.generativeai as genai
import requests

# APIキー
BREVO_KEY = os.environ.get("BREVO_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
if not BREVO_KEY or not GEMINI_KEY:
    print("❌ 環境変数 BREVO_API_KEY / GEMINI_API_KEY が設定されていません")
    exit(1)

# Gemini初期化
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Brevo API直接呼び出し
headers = {
    "accept": "application/json",
    "api-key": BREVO_KEY
}

# リスト取得
print("📥 リストID 4 から連絡先を取得中...")
all_contacts = []
offset = 0
limit = 50

while True:
    response = requests.get(
        "https://api.brevo.com/v3/contacts",
        headers=headers,
        params={"limit": limit, "offset": offset}
    )
    data = response.json()
    contacts = data.get("contacts", [])

    # リストID 4のみをフィルタ
    contacts = [c for c in contacts if 4 in c.get("listIds", [])]

    if not contacts:
        break

    all_contacts.extend(contacts)
    offset += limit

    if len(contacts) < limit:
        break

print(f"✅ {len(all_contacts)}件の連絡先を取得")

# 姓名分割処理
success_count = 0
error_count = 0

for i, contact in enumerate(all_contacts, 1):
    email = contact.get("email")
    attributes = contact.get("attributes", {})
    current_name = attributes.get("FIRSTNAME", "")

    if not current_name:
        print(f"⏭️  [{i}/{len(all_contacts)}] {email}: 名前なし、スキップ")
        continue

    print(f"🔍 [{i}/{len(all_contacts)}] {email}: {current_name}")

    try:
        # Geminiで姓名分割
        prompt = f"""以下の名前を姓と名に分割してください。

名前: {current_name}

以下のルールに従ってください：
- 日本語名の場合は姓と名に分割
- ローマ字名の場合は最初の単語を姓、残りを名とする
- 企業名・組織名の場合は姓を空文字、名に全体を入れる

JSON形式で回答してください：
{{"lastname": "姓", "firstname": "名"}}

JSON以外の説明は不要です。"""

        response_ai = model.generate_content(prompt)
        response_text = response_ai.text.strip()

        # JSONブロックから抽出
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        result = json.loads(response_text)
        lastname = result.get("lastname", "").strip()
        firstname = result.get("firstname", "").strip()

        print(f"   → 姓: {lastname}, 名: {firstname}")

        # Brevoを更新
        update_response = requests.put(
            f"https://api.brevo.com/v3/contacts/{email}",
            headers={**headers, "content-type": "application/json"},
            json={
                "attributes": {
                    "LASTNAME": lastname,
                    "FIRSTNAME": firstname
                }
            }
        )

        if update_response.status_code < 300:
            print(f"   ✅ 更新完了")
            success_count += 1
        else:
            print(f"   ⚠️ 更新エラー: {update_response.status_code}")
            error_count += 1

        time.sleep(1)

    except Exception as e:
        print(f"   ❌ エラー: {e}")
        error_count += 1

print(f"\n{'='*60}")
print(f"処理完了")
print(f"{'='*60}")
print(f"成功: {success_count}件")
print(f"エラー: {error_count}件")
