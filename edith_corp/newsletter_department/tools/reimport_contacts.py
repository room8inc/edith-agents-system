#!/usr/bin/env python3
"""
Brevoリストを全削除して新しいCSVを再インポート
"""

import csv
import os
import requests
import time

# APIキー
BREVO_KEY = os.environ.get("BREVO_API_KEY")
if not BREVO_KEY:
    print("❌ 環境変数 BREVO_API_KEY が設定されていません")
    exit(1)

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "api-key": BREVO_KEY
}

LIST_ID = 4  # Room8 Newsletter

print("🗑️  既存の連絡先を削除中...")

# リストID 4の全連絡先を取得
all_contacts = []
offset = 0
limit = 50

while True:
    response = requests.get(
        "https://api.brevo.com/v3/contacts",
        headers={"accept": "application/json", "api-key": BREVO_KEY},
        params={"limit": limit, "offset": offset}
    )
    data = response.json()
    contacts = data.get("contacts", [])

    # リストID 4のみをフィルタ
    contacts = [c for c in contacts if LIST_ID in c.get("listIds", [])]

    if not contacts:
        break

    all_contacts.extend(contacts)
    offset += limit

    if len(contacts) < limit:
        break

print(f"📋 {len(all_contacts)}件の連絡先を削除します...")

# 全連絡先を削除
deleted_count = 0
for i, contact in enumerate(all_contacts, 1):
    email = contact.get("email")
    try:
        response = requests.delete(
            f"https://api.brevo.com/v3/contacts/{email}",
            headers=headers
        )
        if response.status_code < 300:
            deleted_count += 1
            if i % 50 == 0:
                print(f"  削除中... {i}/{len(all_contacts)}")
    except Exception as e:
        print(f"  ⚠️ {email} 削除失敗: {e}")

print(f"✅ {deleted_count}件削除完了")

# 新しいCSVをインポート
print("\n📥 新しいCSVをインポート中...")

csv_path = "/Users/tsuruta/Downloads/brevo_import_v2.csv"
success_count = 0
error_count = 0

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)

    for i, row in enumerate(reader, 1):
        email = row.get('EMAIL', '').strip()
        lastname = row.get('LASTNAME', '').strip()
        firstname = row.get('FIRSTNAME', '').strip()
        name_original = row.get('NAME_ORIGINAL', '').strip()

        if not email or '@' not in email:
            continue

        # FIRSTNAMEが空の場合はNAME_ORIGINALを使う
        if not firstname and name_original:
            firstname = name_original

        try:
            # 連絡先を追加
            contact_data = {
                "email": email,
                "listIds": [LIST_ID],
                "updateEnabled": True,
                "attributes": {
                    "LASTNAME": lastname,
                    "FIRSTNAME": firstname
                }
            }

            response = requests.post(
                "https://api.brevo.com/v3/contacts",
                headers=headers,
                json=contact_data
            )

            if response.status_code < 300:
                success_count += 1
                if i % 50 == 0:
                    print(f"  インポート中... {i}件")
            else:
                error_count += 1
                print(f"  ⚠️ {email}: {response.status_code}")

            time.sleep(0.1)  # レート制限対策

        except Exception as e:
            error_count += 1
            print(f"  ❌ {email}: {e}")

print(f"\n{'='*60}")
print(f"インポート完了")
print(f"{'='*60}")
print(f"成功: {success_count}件")
print(f"エラー: {error_count}件")
