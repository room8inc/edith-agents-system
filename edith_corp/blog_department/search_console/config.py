#!/usr/bin/env python3
"""
Search Console API 設定ファイル
"""

import os

# Search Console設定
SEARCH_CONSOLE_CONFIG = {
    # 認証情報ファイル（環境変数優先）
    "credentials_path": os.environ.get(
        'GOOGLE_CREDENTIALS_PATH',
        'credentials/claude-agent-486408-2670454f8c9f.json'
    ),

    # サイトURL（環境変数優先）
    "site_url": os.environ.get(
        'SITE_URL',
        'https://www.room8.co.jp/'  # Room8公式サイト
    ),

    # APIリクエスト設定
    "row_limit": 1000,
    "default_days": 28,
}

# Room8サイト設定
SEARCH_CONSOLE_CONFIG["site_url"] = "https://www.room8.co.jp/"