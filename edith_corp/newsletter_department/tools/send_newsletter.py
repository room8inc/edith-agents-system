#!/usr/bin/env python3
"""
メルマガ配信スクリプト
使い方: python3 send_newsletter.py "件名" "本文HTMLファイルパス"
"""

import os
import sys
import json
from pathlib import Path
from brevo_api import BrevoAPI
from send_manager import SendManager

BREVO_KEY = os.environ.get("BREVO_API_KEY")
LIST_ID = 4  # Room8 Newsletter

def main():
    if len(sys.argv) < 3:
        print("使い方: python3 send_newsletter.py '件名' 'HTMLファイルパス'")
        print("\n例:")
        print("  python3 send_newsletter.py '2月のAI LAB開催' './templates/ailab_event.html'")
        sys.exit(1)

    subject = sys.argv[1]
    html_file = sys.argv[2]

    # HTMLファイル読み込み
    if not Path(html_file).exists():
        print(f"❌ HTMLファイルが見つかりません: {html_file}")
        sys.exit(1)

    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Brevo API初期化
    brevo = BrevoAPI(BREVO_KEY)
    send_mgr = SendManager(BREVO_KEY)

    # リストから受信者取得
    print(f"📋 リストID {LIST_ID} から受信者を取得中...")
    contacts = brevo.get_contacts(list_id=LIST_ID, limit=500)

    recipients = [
        {
            'email': c['email'],
            'name': f"{c.get('attributes', {}).get('LASTNAME', '')} {c.get('attributes', {}).get('FIRSTNAME', '')}".strip()
        }
        for c in contacts
    ]

    print(f"✅ {len(recipients)}名の受信者を取得")

    # 送信者設定
    sender = {
        'name': 'Room8',
        'email': 'k_tsuruta@room8.co.jp'
    }

    # 配信実行
    print(f"\n📧 メルマガ配信開始...")
    print(f"   件名: {subject}")
    print(f"   受信者数: {len(recipients)}名")
    print(f"   送信者: {sender['name']} <{sender['email']}>")

    result = send_mgr.send_campaign_batch(
        campaign_name=f"Newsletter_{subject}",
        subject=subject,
        html_content=html_content,
        recipients=recipients,
        sender=sender
    )

    # 結果表示
    print("\n" + "=" * 80)
    print("📊 配信結果")
    print("=" * 80)
    print(f"✅ 送信成功: {result['sent_count']}件")
    print(f"📬 残り配信可能数: {result['remaining_quota']}件")

    if result.get('unsent_recipients'):
        print(f"⏳ 未送信: {len(result['unsent_recipients'])}件（明日送信されます）")
        print(f"   次回送信可能時刻: {result.get('next_reset_time', 'N/A')}")

    if result.get('failed'):
        print(f"❌ 失敗: {len(result['failed'])}件")
        for fail in result['failed'][:5]:  # 最初の5件だけ表示
            print(f"   - {fail['email']}: {fail['error']}")

if __name__ == '__main__':
    main()
