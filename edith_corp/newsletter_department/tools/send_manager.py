#!/usr/bin/env python3
"""
分割送信マネージャー

1日300通制限を考慮した分割送信を管理する。
- 送信済み/未送信の管理
- 送信ログ記録
- リトライ処理
"""

import os
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from brevo_api import BrevoAPI


class SendManager:
    """分割送信マネージャー"""

    DAILY_LIMIT = 300  # 1日の送信上限
    LOG_DIR = Path(__file__).parent.parent / "logs"

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: Brevo APIキー
        """
        self.api = BrevoAPI(api_key)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)

    def _get_today_utc(self) -> str:
        """今日の日付（UTC）を取得"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _get_log_path(self, date: Optional[str] = None) -> Path:
        """
        送信ログのパスを取得

        Args:
            date: 日付（YYYY-MM-DD、省略時は今日）

        Returns:
            ログファイルパス
        """
        date = date or self._get_today_utc()
        return self.LOG_DIR / f"send_log_{date}.json"

    def _load_log(self, date: Optional[str] = None) -> Dict:
        """
        送信ログ読み込み

        Args:
            date: 日付

        Returns:
            ログデータ
        """
        log_path = self._get_log_path(date)
        if log_path.exists():
            with open(log_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {
                "date": date or self._get_today_utc(),
                "sent_count": 0,
                "sent_emails": [],
                "campaigns": []
            }

    def _save_log(self, log_data: Dict, date: Optional[str] = None) -> None:
        """
        送信ログ保存

        Args:
            log_data: ログデータ
            date: 日付
        """
        log_path = self._get_log_path(date)
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

    def get_remaining_quota(self, date: Optional[str] = None) -> int:
        """
        本日の残り送信可能数を取得

        Args:
            date: 日付（省略時は今日）

        Returns:
            残り送信可能数
        """
        log = self._load_log(date)
        return max(0, self.DAILY_LIMIT - log["sent_count"])

    def send_campaign_batch(
        self,
        campaign_name: str,
        subject: str,
        html_content: str,
        recipients: List[Dict[str, str]],
        sender: Dict[str, str],
        max_send: Optional[int] = None
    ) -> Dict:
        """
        分割送信実行

        Args:
            campaign_name: キャンペーン名
            subject: 件名
            html_content: HTML本文
            recipients: 宛先リスト [{"email": "...", "name": "..."}]
            sender: 送信者情報 {"email": "...", "name": "..."}
            max_send: 最大送信数（省略時は残り枠すべて使う）

        Returns:
            送信結果
        """
        # 残り枠を確認
        remaining = self.get_remaining_quota()
        if remaining == 0:
            next_reset = self._get_next_reset_time()
            return {
                "status": "quota_exceeded",
                "message": f"本日の送信枠を使い切りました。次回リセット: {next_reset}",
                "sent_count": 0,
                "remaining_count": len(recipients),
                "next_reset_time": next_reset
            }

        # 送信数を決定
        send_count = min(remaining, len(recipients))
        if max_send:
            send_count = min(send_count, max_send)

        # 送信対象を抽出
        batch = recipients[:send_count]
        remaining_recipients = recipients[send_count:]

        # 送信実行
        sent_emails = []
        failed_emails = []

        for recipient in batch:
            try:
                self.api.send_email(
                    to=[recipient],
                    subject=subject,
                    html_content=html_content,
                    sender=sender
                )
                sent_emails.append(recipient["email"])
            except Exception as e:
                print(f"⚠️ 送信失敗: {recipient['email']} - {e}")
                failed_emails.append({"email": recipient["email"], "error": str(e)})

        # ログ記録
        log = self._load_log()
        log["sent_count"] += len(sent_emails)
        log["sent_emails"].extend(sent_emails)
        log["campaigns"].append({
            "name": campaign_name,
            "subject": subject,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "sent_count": len(sent_emails),
            "failed_count": len(failed_emails),
            "failed_emails": failed_emails
        })
        self._save_log(log)

        return {
            "status": "success",
            "sent_count": len(sent_emails),
            "failed_count": len(failed_emails),
            "remaining_count": len(remaining_recipients),
            "quota_remaining": self.get_remaining_quota(),
            "next_reset_time": self._get_next_reset_time() if len(remaining_recipients) > 0 else None,
            "failed_emails": failed_emails
        }

    def _get_next_reset_time(self) -> str:
        """
        次のリセット時刻を取得（UTC 00:00 = JST 09:00）

        Returns:
            次回リセット時刻（ISO8601形式）
        """
        now_utc = datetime.now(timezone.utc)
        next_reset_utc = (now_utc + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        # JST表記に変換して返す
        jst = timezone(timedelta(hours=9))
        next_reset_jst = next_reset_utc.astimezone(jst)

        return next_reset_jst.strftime("%Y-%m-%d %H:%M JST")

    def get_unsent_contacts(self, all_contacts: List[Dict[str, str]], campaign_name: str) -> List[Dict[str, str]]:
        """
        未送信の連絡先を取得

        Args:
            all_contacts: 全連絡先リスト
            campaign_name: キャンペーン名

        Returns:
            未送信の連絡先リスト
        """
        # 過去のログから送信済みメールアドレスを収集
        sent_emails = set()

        for log_file in self.LOG_DIR.glob("send_log_*.json"):
            with open(log_file, "r", encoding="utf-8") as f:
                log = json.load(f)
                for campaign in log.get("campaigns", []):
                    if campaign["name"] == campaign_name:
                        sent_emails.update(log["sent_emails"])

        # 未送信の連絡先を抽出
        unsent = [c for c in all_contacts if c["email"] not in sent_emails]

        return unsent


def main():
    """CLI テスト用"""
    import argparse

    parser = argparse.ArgumentParser(description="分割送信マネージャー CLI")
    parser.add_argument("action", choices=["quota", "send_test"], help="実行するアクション")
    parser.add_argument("--email", help="テスト送信先メールアドレス")

    args = parser.parse_args()

    manager = SendManager()

    if args.action == "quota":
        # 残り枠確認
        remaining = manager.get_remaining_quota()
        print(f"📊 本日の残り送信枠: {remaining}/{manager.DAILY_LIMIT}")

        if remaining < manager.DAILY_LIMIT:
            log = manager._load_log()
            print(f"✅ 送信済み: {log['sent_count']}通")
            print(f"📅 次回リセット: {manager._get_next_reset_time()}")

    elif args.action == "send_test":
        # テスト送信
        if not args.email:
            print("❌ --email を指定してください")
            return

        result = manager.send_campaign_batch(
            campaign_name="test_campaign",
            subject="分割送信テスト",
            html_content="<h1>テスト</h1><p>分割送信のテストです。</p>",
            recipients=[{"email": args.email, "name": "Test User"}],
            sender={"email": "noreply@room8.co.jp", "name": "Room8"}
        )

        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
