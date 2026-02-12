#!/usr/bin/env python3
"""
CSVをBrevoにインポートする統合スクリプト
"""

import sys
from pathlib import Path
from brevo_api import BrevoAPI
from list_manager import ListManager


def main():
    import argparse

    parser = argparse.ArgumentParser(description='CSVをBrevoにインポート')
    parser.add_argument('csv_path', help='インポートするCSVファイル')
    parser.add_argument('--list-name', default='Room8 Newsletter', help='リスト名（新規作成する場合）')
    parser.add_argument('--list-id', type=int, help='既存のリストID（指定時は新規作成しない）')

    args = parser.parse_args()

    api = BrevoAPI()
    manager = ListManager()

    # リストIDが指定されていない場合は新規作成
    if not args.list_id:
        # フォルダを取得または作成
        print("📁 フォルダを確認中...")
        folders = api.get_folders()

        # "Room8"フォルダを探す
        room8_folder = None
        for folder in folders:
            if folder['name'] == 'Room8':
                room8_folder = folder
                break

        # なければ作成
        if not room8_folder:
            print("📁 'Room8' フォルダを作成中...")
            room8_folder = api.create_folder('Room8')
            print(f"✅ フォルダ作成完了: ID {room8_folder['id']}")
        else:
            print(f"✅ 既存フォルダを使用: ID {room8_folder['id']}")

        # リスト作成
        print(f"📝 新しいリスト '{args.list_name}' を作成中...")
        list_info = api.create_list(args.list_name, folder_id=room8_folder['id'])
        list_id = list_info['id']
        print(f"✅ リスト作成完了: ID {list_id}")
    else:
        list_id = args.list_id
        print(f"📋 既存リスト ID {list_id} を使用")

    # CSVからインポート
    print(f"\n📥 CSVをインポート中: {args.csv_path}")
    result = manager.import_from_csv(Path(args.csv_path), list_ids=[list_id])

    print(f"\n✅ インポート完了!")
    print(f"   成功: {result['success_count']}件")
    print(f"   エラー: {result['error_count']}件")

    if result['errors']:
        print("\n⚠️ エラー詳細:")
        for error in result['errors'][:10]:
            print(f"  - {error['email']}: {error['error']}")

        if len(result['errors']) > 10:
            print(f"  ... 他 {len(result['errors']) - 10}件")

    # 最終確認
    print(f"\n📊 最終確認中...")
    contacts = manager.get_all_contacts(list_id=list_id)
    print(f"✅ リストID {list_id} には現在 {len(contacts)} 件の連絡先があります")


if __name__ == '__main__':
    main()
