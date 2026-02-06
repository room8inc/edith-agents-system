#!/usr/bin/env python3
"""
Google Analytics 4 Data API 連携モジュール
GA4プロパティからアクセスデータを取得する。

Search Consoleと同じサービスアカウント認証方式を使用。
事前準備:
  1. Google Cloud Console で Analytics Data API を有効化
  2. GA4 プロパティの管理画面でサービスアカウントのメールアドレスを閲覧者として追加
  3. config/ga4_config.json に property_id を設定
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

_THIS_DIR = Path(__file__).resolve().parent


class GA4API:
    """Google Analytics 4 Data API ラッパー"""

    SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]

    def __init__(self, credentials_path: str, property_id: str):
        self.credentials_path = credentials_path
        self.property_id = property_id
        self.service = None

    def authenticate(self) -> bool:
        """API認証"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.SCOPES,
            )
            self.service = build(
                "analyticsdata", "v1beta", credentials=credentials
            )
            return True
        except Exception as e:
            print(f"[GA4 API] 認証失敗: {e}", flush=True)
            return False

    def _run_report(self, date_range: dict, dimensions: list, metrics: list, limit: int = 10) -> dict:
        """GA4 Data API の runReport を実行"""
        body = {
            "dateRanges": [date_range],
            "dimensions": [{"name": d} for d in dimensions],
            "metrics": [{"name": m} for m in metrics],
            "limit": limit,
        }
        response = (
            self.service.properties()
            .runReport(property=f"properties/{self.property_id}", body=body)
            .execute()
        )
        return response

    def get_overview(self, days: int = 28) -> dict:
        """サイト全体のアクセス概況を取得"""
        end = datetime.now()
        start = end - timedelta(days=days)
        date_range = {
            "startDate": start.strftime("%Y-%m-%d"),
            "endDate": end.strftime("%Y-%m-%d"),
        }

        # 全体メトリクス（ディメンションなし）
        body = {
            "dateRanges": [date_range],
            "metrics": [
                {"name": "activeUsers"},
                {"name": "sessions"},
                {"name": "screenPageViews"},
                {"name": "bounceRate"},
                {"name": "averageSessionDuration"},
                {"name": "newUsers"},
            ],
        }
        overview = (
            self.service.properties()
            .runReport(property=f"properties/{self.property_id}", body=body)
            .execute()
        )

        row = overview.get("rows", [{}])[0] if overview.get("rows") else {}
        values = [v.get("value", "0") for v in row.get("metricValues", [])]

        return {
            "period_days": days,
            "active_users": int(values[0]) if len(values) > 0 else 0,
            "sessions": int(values[1]) if len(values) > 1 else 0,
            "page_views": int(values[2]) if len(values) > 2 else 0,
            "bounce_rate": round(float(values[3]) * 100, 1) if len(values) > 3 else 0,
            "avg_session_duration_sec": round(float(values[4]), 1) if len(values) > 4 else 0,
            "new_users": int(values[5]) if len(values) > 5 else 0,
        }

    def get_top_pages(self, days: int = 28, limit: int = 10) -> list:
        """ページ別アクセスランキング"""
        end = datetime.now()
        start = end - timedelta(days=days)
        date_range = {
            "startDate": start.strftime("%Y-%m-%d"),
            "endDate": end.strftime("%Y-%m-%d"),
        }

        response = self._run_report(
            date_range=date_range,
            dimensions=["pagePath"],
            metrics=["screenPageViews", "activeUsers", "averageSessionDuration"],
            limit=limit,
        )

        pages = []
        for row in response.get("rows", []):
            dims = [d.get("value", "") for d in row.get("dimensionValues", [])]
            vals = [v.get("value", "0") for v in row.get("metricValues", [])]
            pages.append({
                "path": dims[0] if dims else "",
                "page_views": int(vals[0]) if len(vals) > 0 else 0,
                "active_users": int(vals[1]) if len(vals) > 1 else 0,
                "avg_duration_sec": round(float(vals[2]), 1) if len(vals) > 2 else 0,
            })
        return pages

    def get_traffic_sources(self, days: int = 28) -> list:
        """流入元の内訳"""
        end = datetime.now()
        start = end - timedelta(days=days)
        date_range = {
            "startDate": start.strftime("%Y-%m-%d"),
            "endDate": end.strftime("%Y-%m-%d"),
        }

        response = self._run_report(
            date_range=date_range,
            dimensions=["sessionDefaultChannelGroup"],
            metrics=["sessions", "activeUsers"],
            limit=10,
        )

        sources = []
        for row in response.get("rows", []):
            dims = [d.get("value", "") for d in row.get("dimensionValues", [])]
            vals = [v.get("value", "0") for v in row.get("metricValues", [])]
            sources.append({
                "channel": dims[0] if dims else "",
                "sessions": int(vals[0]) if len(vals) > 0 else 0,
                "active_users": int(vals[1]) if len(vals) > 1 else 0,
            })
        return sources

    def get_full_report(self, days: int = 28) -> dict:
        """リサーチ用の全データ取得"""
        return {
            "overview": self.get_overview(days),
            "top_pages": self.get_top_pages(days),
            "traffic_sources": self.get_traffic_sources(days),
        }
