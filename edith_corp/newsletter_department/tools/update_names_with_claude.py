#!/usr/bin/env python3
"""
BrevoのリストからNAMEを取得し、Gemini AIで姓名に分割してBrevoを更新

Gemini API（有料枠 GEMINI_IMAGE_API_KEY）を使って日本語名を精度高く姓名分割する。
"""

import os
import json
import time
from typing import Dict, Optional
from brevo_api import BrevoAPI
from list_manager import ListManager
import google.generativeai as genai


def split_name_with_gemini(full_name: str, model) -> Dict[str, str]:
    """
    Gemini AIで姓名を分割

    Args:
        full_name: フルネーム
        model: Gemini model

    Returns:
        {"lastname": "姓", "firstname": "名"}
    """
    prompt = f"""以下の名前を姓と名に分割してください。

名前: {full_name}

以下のルールに従ってください：
- 日本語名の場合は姓と名に分割
- ローマ字名の場合は最初の単語を姓、残りを名とする
- 企業名・組織名の場合は姓を空文字、名に全体を入れる
- 名前が不明な場合は姓を空文字、名に全体を入れる

JSON形式で回答してください：
{{"lastname": "姓", "firstname": "名"}}

JSON以外の説明は不要です。"""

    response = model.generate_content(prompt)
    response_text = response.text.strip()

    # JSONブロックから抽出（```json ... ``` がある場合）
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()

    try:
        result = json.loads(response_text)
        return {
            "lastname": result.get("lastname", "").strip(),
            "firstname": result.get("firstname", "").strip()
        }
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON解析エラー: {full_name} - {response_text}")
        return {"lastname": "", "firstname": full_name}


def update_brevo_contacts_with_names(list_id: int, dry_run: bool = True):
    """
    Brevoのリストから連絡先を取得し、姓名を分割してBrevoを更新

    Args:
        list_id: リストID
        dry_run: True の場合は実際には更新せず、結果のみ表示
    """
    # API初期化
    brevo_api_key = os.environ.get("BREVO_API_KEY")
    gemini_api_key = os.environ.get("GEMINI_IMAGE_API_KEY")

    if not gemini_api_key:
        raise ValueError("GEMINI_IMAGE_API_KEY が設定されていません")

    brevo_api = BrevoAPI(brevo_api_key)
    manager = ListManager(brevo_api_key)

    # Gemini API初期化（有料枠 Tier1）
    genai.configure(api_key=gemini_api_key)
    gemini_model = genai.GenerativeModel('gemini-2.5-flash')

    # リストから連絡先を取得
    print(f"📥 リストID {list_id} から連絡先を取得中...")
    contacts = manager.get_all_contacts(list_id=list_id)
    print(f"✅ {len(contacts)}件の連絡先を取得")

    # 姓名分割処理
    results = []
    success_count = 0
    error_count = 0

    for i, contact in enumerate(contacts, 1):
        email = contact.get("email")
        attributes = contact.get("attributes", {})
        current_name = attributes.get("FIRSTNAME", "")

        if not current_name:
            print(f"⏭️  [{i}/{len(contacts)}] {email}: 名前なし、スキップ")
            continue

        print(f"🔍 [{i}/{len(contacts)}] {email}: {current_name}")

        try:
            # Geminiで姓名分割
            split_result = split_name_with_gemini(current_name, gemini_model)
            lastname = split_result["lastname"]
            firstname = split_result["firstname"]

            print(f"   → 姓: {lastname}, 名: {firstname}")

            # 結果を記録
            results.append({
                "email": email,
                "original_name": current_name,
                "lastname": lastname,
                "firstname": firstname
            })

            # Brevoを更新
            if not dry_run:
                brevo_api.update_contact(email, {
                    "LASTNAME": lastname,
                    "FIRSTNAME": firstname
                })
                print(f"   ✅ 更新完了")

            success_count += 1

            # レート制限対策（有料枠なので短めに）
            time.sleep(1)

        except Exception as e:
            print(f"   ❌ エラー: {e}")
            error_count += 1

    # 結果サマリ
    print(f"\n{'='*60}")
    print(f"処理完了")
    print(f"{'='*60}")
    print(f"成功: {success_count}件")
    print(f"エラー: {error_count}件")

    if dry_run:
        print(f"\n⚠️  DRY RUNモード: Brevoは更新されていません")
        print(f"実際に更新する場合は --apply を指定してください")

    # 結果をJSONで保存
    output_file = f"name_split_results_{list_id}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n📄 結果を保存: {output_file}")

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description='BrevoリストのNAMEをGemini AIで姓名分割')
    parser.add_argument('--list-id', type=int, default=4, help='リストID（デフォルト: 4）')
    parser.add_argument('--apply', action='store_true', help='実際にBrevoを更新する（指定しない場合はDRY RUN）')

    args = parser.parse_args()

    update_brevo_contacts_with_names(
        list_id=args.list_id,
        dry_run=not args.apply
    )


if __name__ == '__main__':
    main()
