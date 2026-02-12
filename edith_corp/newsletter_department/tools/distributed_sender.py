#!/usr/bin/env python3
"""
分散送信マネージャー
受信者を複数グループに分けて、時間帯をずらして送信する
A/Bテスト・開封率分析用
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
from brevo_api import BrevoAPI

class DistributedSender:
    def __init__(self, api_key: str):
        self.api = BrevoAPI(api_key)
        self.schedule_dir = Path(__file__).parent / "schedules"
        self.schedule_dir.mkdir(exist_ok=True)

    def create_schedule(
        self,
        campaign_name: str,
        recipients: List[Dict],
        time_slots: List[str],
        shuffle: bool = True
    ) -> Dict:
        """
        分散送信スケジュールを作成

        Args:
            campaign_name: キャンペーン名
            recipients: 受信者リスト [{'email': '...', 'name': '...'}]
            time_slots: 送信時間帯 ['09:00', '12:00', '15:00', '18:00', '21:00']
            shuffle: 受信者をシャッフルするか（時間帯の偏りを防ぐ）

        Returns:
            スケジュール情報
        """
        # 受信者をシャッフル（同じ人が毎回同じ時間にならないように）
        if shuffle:
            recipients_copy = recipients.copy()
            random.shuffle(recipients_copy)
        else:
            recipients_copy = recipients

        # 各時間帯にほぼ均等に分配
        total = len(recipients_copy)
        slot_count = len(time_slots)
        per_slot = total // slot_count
        remainder = total % slot_count

        schedule = {
            'campaign_name': campaign_name,
            'created_at': datetime.now().isoformat(),
            'total_recipients': total,
            'time_slots': []
        }

        start_idx = 0
        for i, time_slot in enumerate(time_slots):
            # 余りを前半の時間帯に分配
            count = per_slot + (1 if i < remainder else 0)
            end_idx = start_idx + count

            slot_recipients = recipients_copy[start_idx:end_idx]

            schedule['time_slots'].append({
                'time': time_slot,
                'recipient_count': count,
                'recipients': slot_recipients,
                'sent': False,
                'sent_at': None,
                'message_ids': []
            })

            start_idx = end_idx

        # スケジュールを保存
        schedule_file = self.schedule_dir / f"{campaign_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(schedule_file, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)

        print(f"✅ スケジュール作成完了: {schedule_file}")
        print(f"\n📊 配信計画:")
        for slot in schedule['time_slots']:
            print(f"   {slot['time']}: {slot['recipient_count']}名")

        return schedule

    def send_slot(
        self,
        schedule_file: Path,
        slot_index: int,
        subject: str,
        html_content: str,
        sender: Dict[str, str]
    ) -> Dict:
        """
        指定された時間帯のグループに送信

        Args:
            schedule_file: スケジュールファイルパス
            slot_index: 時間帯インデックス（0始まり）
            subject: メール件名
            html_content: HTML本文
            sender: 送信者 {'name': '...', 'email': '...'}

        Returns:
            送信結果
        """
        # スケジュール読み込み
        with open(schedule_file, 'r', encoding='utf-8') as f:
            schedule = json.load(f)

        if slot_index >= len(schedule['time_slots']):
            raise ValueError(f"Invalid slot_index: {slot_index}")

        slot = schedule['time_slots'][slot_index]

        if slot['sent']:
            print(f"⚠️ この時間帯は既に送信済みです: {slot['time']}")
            return {'status': 'already_sent', 'slot': slot}

        # 送信実行
        recipients = slot['recipients']
        print(f"📧 送信中... [{slot['time']}] {len(recipients)}名")

        # Brevo API で送信（一括送信ではなく個別送信でトラッキング）
        message_ids = []
        failed = []

        for recipient in recipients:
            try:
                response = self.api.send_email(
                    to=[{'email': recipient['email'], 'name': recipient.get('name', '')}],
                    subject=subject,
                    html_content=html_content,
                    sender=sender,
                    tags=[schedule['campaign_name'], f"slot_{slot['time']}"]
                )
                message_ids.append(response.get('messageId'))
            except Exception as e:
                failed.append({'email': recipient['email'], 'error': str(e)})

        # スケジュール更新
        slot['sent'] = True
        slot['sent_at'] = datetime.now().isoformat()
        slot['message_ids'] = message_ids
        slot['failed_count'] = len(failed)

        with open(schedule_file, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)

        result = {
            'status': 'success',
            'slot_time': slot['time'],
            'sent_count': len(message_ids),
            'failed_count': len(failed),
            'failed': failed
        }

        print(f"✅ 送信完了: {len(message_ids)}件")
        if failed:
            print(f"❌ 失敗: {len(failed)}件")

        return result

    def get_schedule_status(self, schedule_file: Path) -> Dict:
        """スケジュールの進捗状況を取得"""
        with open(schedule_file, 'r', encoding='utf-8') as f:
            schedule = json.load(f)

        total = schedule['total_recipients']
        sent = sum(slot['recipient_count'] for slot in schedule['time_slots'] if slot['sent'])
        pending = total - sent

        return {
            'campaign_name': schedule['campaign_name'],
            'total': total,
            'sent': sent,
            'pending': pending,
            'progress': f"{sent}/{total} ({sent*100//total}%)",
            'time_slots': [
                {
                    'time': slot['time'],
                    'count': slot['recipient_count'],
                    'status': '✅ 送信済み' if slot['sent'] else '⏳ 未送信',
                    'sent_at': slot.get('sent_at')
                }
                for slot in schedule['time_slots']
            ]
        }


def main():
    """テスト用メイン関数"""
    import sys

    if len(sys.argv) < 2:
        print("使い方:")
        print("  1. スケジュール作成: python3 distributed_sender.py create <campaign_name>")
        print("  2. 時間帯送信: python3 distributed_sender.py send <schedule_file> <slot_index>")
        print("  3. 状況確認: python3 distributed_sender.py status <schedule_file>")
        sys.exit(1)

    command = sys.argv[1]
    BREVO_KEY = os.environ.get("BREVO_API_KEY")
    if not BREVO_KEY:
        print("❌ 環境変数 BREVO_API_KEY が設定されていません")
        sys.exit(1)
    sender_instance = DistributedSender(BREVO_KEY)

    if command == "create":
        campaign_name = sys.argv[2] if len(sys.argv) > 2 else "test_campaign"

        # テスト用: リストから受信者取得
        api = BrevoAPI()
        contacts = api.get_contacts(list_id=4, limit=500)
        recipients = [
            {'email': c['email'], 'name': f"{c.get('attributes', {}).get('LASTNAME', '')} {c.get('attributes', {}).get('FIRSTNAME', '')}".strip()}
            for c in contacts
        ]

        # 5つの時間帯に分散
        time_slots = ['09:00', '12:00', '15:00', '18:00', '21:00']
        schedule = sender_instance.create_schedule(campaign_name, recipients, time_slots, shuffle=True)

    elif command == "status":
        schedule_file = Path(sys.argv[2])
        status = sender_instance.get_schedule_status(schedule_file)
        print(f"\n📊 {status['campaign_name']}")
        print(f"進捗: {status['progress']}")
        print("\n時間帯別:")
        for slot in status['time_slots']:
            print(f"  {slot['time']}: {slot['count']}名 - {slot['status']}")

if __name__ == '__main__':
    main()
