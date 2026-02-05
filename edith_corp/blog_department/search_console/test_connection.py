#!/usr/bin/env python3
"""
Search Console API 接続テスト
Room8サイトへの接続を確認
"""

import sys
import os
from datetime import datetime, timedelta

# 設定読み込み
from config import SEARCH_CONSOLE_CONFIG

# API モジュール
from search_console_api import SearchConsoleIntegration

def test_connection():
    """Search Console接続テスト"""

    print("=" * 60)
    print("Search Console API 接続テスト")
    print("=" * 60)

    # 設定確認
    print("\n📋 設定内容:")
    print(f"  サイトURL: {SEARCH_CONSOLE_CONFIG['site_url']}")
    print(f"  認証ファイル: {SEARCH_CONSOLE_CONFIG['credentials_path']}")

    # ファイル存在確認
    if not os.path.exists(SEARCH_CONSOLE_CONFIG['credentials_path']):
        print(f"❌ 認証ファイルが見つかりません: {SEARCH_CONSOLE_CONFIG['credentials_path']}")
        return False

    print("  ✅ 認証ファイル存在確認OK")

    # 統合マネージャー初期化
    print("\n🔌 接続開始...")
    integration = SearchConsoleIntegration()

    # 接続実行
    success = integration.setup(
        site_url=SEARCH_CONSOLE_CONFIG['site_url'],
        credentials_path=SEARCH_CONSOLE_CONFIG['credentials_path']
    )

    if not success:
        print("\n❌ 接続失敗")
        print("考えられる原因:")
        print("1. サービスアカウントがSearch Consoleに追加されていない")
        print("2. Search Console APIが有効化されていない")
        print("3. 認証ファイルが正しくない")
        return False

    print("\n✅ 接続成功！")

    # データ取得テスト
    print("\n📊 データ取得テスト...")

    try:
        # 過去7日間のデータを試験取得
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        data = integration.api.get_search_analytics(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            dimensions=['query'],
            row_limit=10
        )

        if data and 'summary' in data:
            print(f"\n✅ データ取得成功！")
            print(f"\n📈 過去7日間のサマリー:")
            print(f"  総クリック数: {data['summary']['total_clicks']:,}")
            print(f"  総インプレッション数: {data['summary']['total_impressions']:,}")
            print(f"  平均CTR: {data['summary']['avg_ctr']:.2%}")

            if data['queries']:
                print(f"\n🔍 上位検索クエリ (TOP 5):")
                for i, query in enumerate(data['queries'][:5], 1):
                    print(f"  {i}. {query['query']}")
                    print(f"     クリック: {query['clicks']}, "
                          f"表示回数: {query['impressions']}, "
                          f"CTR: {query['ctr']:.2%}")

            return True
        else:
            print("⚠️ データが取得できませんでした")
            print("Search Consoleにデータが蓄積されているか確認してください（最低3日必要）")
            return False

    except Exception as e:
        print(f"\n❌ データ取得エラー: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()

    if success:
        print("\n" + "=" * 60)
        print("🎉 Room8 Search Console連携成功！")
        print("SEO足軽が実データを活用できるようになりました")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠️ 接続に問題があります")
        print("上記のエラーメッセージを確認してください")
        print("=" * 60)