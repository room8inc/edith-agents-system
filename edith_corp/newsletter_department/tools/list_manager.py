#!/usr/bin/env python3
"""
購読者リスト管理

Brevo APIを使った購読者リストのCRUD操作。
CSVインポート・エクスポート機能も提供。
"""

import csv
from typing import List, Dict, Optional
from pathlib import Path

from brevo_api import BrevoAPI


class ListManager:
    """購読者リスト管理"""

    LISTS_DIR = Path(__file__).parent.parent / "lists"

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: Brevo APIキー
        """
        self.api = BrevoAPI(api_key)
        self.LISTS_DIR.mkdir(parents=True, exist_ok=True)

    def get_all_contacts(self, list_id: Optional[int] = None) -> List[Dict]:
        """
        全連絡先を取得

        Args:
            list_id: リストID（指定時はそのリストのみ）

        Returns:
            連絡先リスト
        """
        all_contacts = []
        offset = 0
        limit = 50

        while True:
            response = self.api.get_contacts(list_id=list_id, limit=limit, offset=offset)
            contacts = response.get("contacts", [])

            if not contacts:
                break

            all_contacts.extend(contacts)
            offset += limit

            # 全件取得済みならループを抜ける
            if len(contacts) < limit:
                break

        return all_contacts

    def add_contacts_batch(
        self,
        contacts: List[Dict[str, str]],
        list_ids: Optional[List[int]] = None
    ) -> Dict:
        """
        複数の連絡先を一括追加

        Args:
            contacts: 連絡先リスト [{"email": "...", "name": "..."}]
            list_ids: 追加先リストID

        Returns:
            追加結果
        """
        success_count = 0
        error_count = 0
        errors = []

        for contact in contacts:
            try:
                self.api.add_contact(
                    email=contact["email"],
                    attributes={"FIRSTNAME": contact.get("name", "")},
                    list_ids=list_ids
                )
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append({"email": contact["email"], "error": str(e)})

        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors
        }

    def export_to_csv(self, list_id: Optional[int] = None, output_path: Optional[Path] = None) -> Path:
        """
        連絡先をCSVエクスポート

        Args:
            list_id: リストID
            output_path: 出力先パス（省略時は自動生成）

        Returns:
            出力ファイルパス
        """
        contacts = self.get_all_contacts(list_id)

        if not output_path:
            list_name = f"list_{list_id}" if list_id else "all_contacts"
            output_path = self.LISTS_DIR / f"{list_name}.csv"

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            if not contacts:
                return output_path

            # カラム名を取得（最初の連絡先から）
            fieldnames = ["email"]
            if contacts[0].get("attributes"):
                fieldnames.extend(contacts[0]["attributes"].keys())

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for contact in contacts:
                row = {"email": contact["email"]}
                if contact.get("attributes"):
                    row.update(contact["attributes"])
                writer.writerow(row)

        return output_path

    def import_from_csv(self, csv_path: Path, list_ids: Optional[List[int]] = None) -> Dict:
        """
        CSVから連絡先をインポート

        Args:
            csv_path: CSVファイルパス
            list_ids: インポート先リストID

        Returns:
            インポート結果
        """
        contacts = []

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # カラム名を大文字小文字両対応
                email = row.get("email") or row.get("EMAIL", "")
                name = row.get("name") or row.get("NAME") or row.get("FIRSTNAME", "")

                contacts.append({
                    "email": email.strip(),
                    "name": name.strip()
                })

        return self.add_contacts_batch(contacts, list_ids)

    def remove_bounced_contacts(self, list_id: Optional[int] = None) -> Dict:
        """
        バウンスした連絡先を削除

        Args:
            list_id: リストID

        Returns:
            削除結果
        """
        # Brevo APIでバウンスした連絡先を取得（実装は省略、実際にはAPI仕様に応じて実装）
        # ここでは簡易的にハードバウンスのみを削除する想定

        # TODO: 実際のバウンスリスト取得処理を実装
        bounced_emails = []

        deleted_count = 0
        for email in bounced_emails:
            try:
                self.api.delete_contact(email)
                deleted_count += 1
            except Exception as e:
                print(f"⚠️ 削除失敗: {email} - {e}")

        return {
            "deleted_count": deleted_count,
            "bounced_emails": bounced_emails
        }


def main():
    """CLI テスト用"""
    import argparse

    parser = argparse.ArgumentParser(description="リスト管理 CLI")
    parser.add_argument("action", choices=["export", "import", "count"], help="実行するアクション")
    parser.add_argument("--list-id", type=int, help="リストID")
    parser.add_argument("--csv", help="CSVファイルパス")

    args = parser.parse_args()

    manager = ListManager()

    if args.action == "export":
        # CSVエクスポート
        output_path = manager.export_to_csv(list_id=args.list_id)
        print(f"✅ エクスポート完了: {output_path}")

    elif args.action == "import":
        # CSVインポート
        if not args.csv:
            print("❌ --csv を指定してください")
            return

        csv_path = Path(args.csv)
        result = manager.import_from_csv(csv_path, list_ids=[args.list_id] if args.list_id else None)
        print(f"✅ インポート完了: 成功 {result['success_count']}件, エラー {result['error_count']}件")

        if result['errors']:
            print("\n⚠️ エラー詳細:")
            for error in result['errors']:
                print(f"  - {error['email']}: {error['error']}")

    elif args.action == "count":
        # 連絡先数を確認
        contacts = manager.get_all_contacts(list_id=args.list_id)
        print(f"📊 連絡先数: {len(contacts)}")


if __name__ == "__main__":
    main()
