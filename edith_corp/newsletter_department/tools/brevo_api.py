#!/usr/bin/env python3
"""
Brevo API連携ツール

Brevo（旧Sendinblue）のREST APIを使った操作を提供する。
- メール送信
- リスト管理
- テンプレート管理
- キャンペーン統計取得
"""

import os
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime


class BrevoAPI:
    """Brevo API クライアント"""

    BASE_URL = "https://api.brevo.com/v3"

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: Brevo APIキー（省略時は環境変数 BREVO_API_KEY から取得）
        """
        self.api_key = api_key or os.environ.get("BREVO_API_KEY")
        if not self.api_key:
            raise ValueError("BREVO_API_KEY が設定されていません")

        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": self.api_key
        }

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        API リクエスト実行

        Args:
            method: HTTPメソッド (GET, POST, PUT, DELETE)
            endpoint: エンドポイント (/contacts 等)
            data: リクエストボディ

        Returns:
            レスポンスJSON
        """
        url = f"{self.BASE_URL}{endpoint}"

        if method == "GET":
            response = requests.get(url, headers=self.headers, params=data)
        elif method == "POST":
            response = requests.post(url, headers=self.headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=self.headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=self.headers, json=data)
        else:
            raise ValueError(f"未対応のメソッド: {method}")

        if response.status_code >= 400:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

        return response.json() if response.text else {}

    # ==================== メール送信 ====================

    def send_email(
        self,
        to: List[Dict[str, str]],
        subject: str,
        html_content: str,
        sender: Optional[Dict[str, str]] = None,
        reply_to: Optional[Dict[str, str]] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        メール送信

        Args:
            to: 宛先リスト [{"email": "test@example.com", "name": "Test User"}]
            subject: 件名
            html_content: HTML本文
            sender: 送信者情報 {"email": "from@example.com", "name": "Sender"}
            reply_to: 返信先
            params: テンプレート変数

        Returns:
            送信結果
        """
        data = {
            "to": to,
            "subject": subject,
            "htmlContent": html_content
        }

        if sender:
            data["sender"] = sender
        if reply_to:
            data["replyTo"] = reply_to
        if params:
            data["params"] = params

        return self._request("POST", "/smtp/email", data)

    def send_campaign(
        self,
        list_ids: List[int],
        subject: str,
        html_content: str,
        sender: Dict[str, str],
        name: str,
        scheduled_at: Optional[str] = None
    ) -> Dict:
        """
        キャンペーン送信（リスト全体に配信）

        Args:
            list_ids: 配信先リストID
            subject: 件名
            html_content: HTML本文
            sender: 送信者情報
            name: キャンペーン名
            scheduled_at: 配信予定日時（ISO8601形式、省略時は即時送信）

        Returns:
            キャンペーンID
        """
        # キャンペーン作成
        campaign_data = {
            "name": name,
            "subject": subject,
            "sender": sender,
            "type": "classic",
            "htmlContent": html_content,
            "recipients": {
                "listIds": list_ids
            }
        }

        campaign = self._request("POST", "/emailCampaigns", campaign_data)
        campaign_id = campaign["id"]

        # 送信スケジュール設定
        if scheduled_at:
            schedule_data = {"scheduledAt": scheduled_at}
            self._request("POST", f"/emailCampaigns/{campaign_id}/sendSchedule", schedule_data)
        else:
            # 即時送信
            self._request("POST", f"/emailCampaigns/{campaign_id}/sendNow", {})

        return campaign

    # ==================== リスト管理 ====================

    def get_folders(self) -> List[Dict]:
        """全フォルダを取得"""
        response = self._request("GET", "/contacts/folders")
        return response.get("folders", [])

    def create_folder(self, name: str) -> Dict:
        """
        フォルダ作成

        Args:
            name: フォルダ名

        Returns:
            フォルダ情報
        """
        data = {"name": name}
        return self._request("POST", "/contacts/folders", data)

    def get_lists(self) -> List[Dict]:
        """全リストを取得"""
        response = self._request("GET", "/contacts/lists")
        return response.get("lists", [])

    def create_list(self, name: str, folder_id: Optional[int] = None) -> Dict:
        """
        リスト作成

        Args:
            name: リスト名
            folder_id: フォルダID

        Returns:
            リスト情報
        """
        data = {"name": name}
        if folder_id:
            data["folderId"] = folder_id

        return self._request("POST", "/contacts/lists", data)

    def get_contacts(self, list_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> Dict:
        """
        連絡先取得

        Args:
            list_id: リストID（指定時はそのリストの連絡先のみ）
            limit: 取得件数
            offset: オフセット

        Returns:
            連絡先リスト
        """
        params = {"limit": limit, "offset": offset}
        if list_id:
            params["listIds"] = list_id

        return self._request("GET", "/contacts", params)

    def add_contact(
        self,
        email: str,
        attributes: Optional[Dict] = None,
        list_ids: Optional[List[int]] = None,
        update_enabled: bool = True
    ) -> Dict:
        """
        連絡先追加

        Args:
            email: メールアドレス
            attributes: 属性（名前等）
            list_ids: 追加先リストID
            update_enabled: 既存連絡先の場合は更新

        Returns:
            追加結果
        """
        data = {
            "email": email,
            "updateEnabled": update_enabled
        }

        if attributes:
            data["attributes"] = attributes
        if list_ids:
            data["listIds"] = list_ids

        return self._request("POST", "/contacts", data)

    def update_contact(self, email: str, attributes: Dict) -> None:
        """
        連絡先更新

        Args:
            email: メールアドレス
            attributes: 更新する属性
        """
        data = {"attributes": attributes}
        self._request("PUT", f"/contacts/{email}", data)

    def delete_contact(self, email: str) -> None:
        """
        連絡先削除

        Args:
            email: メールアドレス
        """
        self._request("DELETE", f"/contacts/{email}")

    def import_contacts_csv(self, file_url: str, list_ids: List[int]) -> Dict:
        """
        CSVインポート

        Args:
            file_url: CSVファイルのURL
            list_ids: インポート先リストID

        Returns:
            インポート結果
        """
        data = {
            "fileUrl": file_url,
            "listIds": list_ids,
            "emailBlacklist": False,
            "smsBlacklist": False,
            "updateExistingContacts": True
        }

        return self._request("POST", "/contacts/import", data)

    # ==================== 統計・分析 ====================

    def get_campaign_stats(self, campaign_id: int) -> Dict:
        """
        キャンペーン統計取得

        Args:
            campaign_id: キャンペーンID

        Returns:
            統計情報（開封率、クリック率等）
        """
        return self._request("GET", f"/emailCampaigns/{campaign_id}")

    def get_all_campaigns(self, status: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        全キャンペーン取得

        Args:
            status: ステータスフィルタ (sent, draft, scheduled)
            limit: 取得件数

        Returns:
            キャンペーンリスト
        """
        params = {"limit": limit}
        if status:
            params["status"] = status

        response = self._request("GET", "/emailCampaigns", params)
        return response.get("campaigns", [])


def main():
    """CLI テスト用"""
    import argparse

    parser = argparse.ArgumentParser(description="Brevo API CLI")
    parser.add_argument("action", choices=["test", "lists", "contacts", "send_test"], help="実行するアクション")
    parser.add_argument("--list-id", type=int, help="リストID")
    parser.add_argument("--email", help="メールアドレス")

    args = parser.parse_args()

    api = BrevoAPI()

    if args.action == "test":
        # API接続テスト
        print("🔗 Brevo API接続テスト...")
        lists = api.get_lists()
        print(f"✅ 接続成功！ リスト数: {len(lists)}")
        for lst in lists:
            print(f"  - {lst['name']} (ID: {lst['id']}, 件数: {lst.get('totalSubscribers', 0)})")

    elif args.action == "lists":
        # リスト一覧
        lists = api.get_lists()
        print(json.dumps(lists, indent=2, ensure_ascii=False))

    elif args.action == "contacts":
        # 連絡先一覧
        contacts = api.get_contacts(list_id=args.list_id)
        print(json.dumps(contacts, indent=2, ensure_ascii=False))

    elif args.action == "send_test":
        # テストメール送信
        if not args.email:
            print("❌ --email を指定してください")
            return

        result = api.send_email(
            to=[{"email": args.email}],
            subject="Brevo API テストメール",
            html_content="<h1>テストメール</h1><p>Brevo APIからの送信テストです。</p>",
            sender={"email": "noreply@room8.co.jp", "name": "Room8"}
        )
        print(f"✅ テストメール送信完了: {result}")


if __name__ == "__main__":
    main()
