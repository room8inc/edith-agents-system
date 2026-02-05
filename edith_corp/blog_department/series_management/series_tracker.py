#!/usr/bin/env python3
"""
シリーズ記事管理システム - 継続的な記事シリーズの自動追跡
チャットを閉じても次の記事で自動的にシリーズが継続される
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class SeriesTracker:
    """シリーズ記事の自動追跡システム"""

    def __init__(self):
        self.series_db_path = "series_management/series_database.json"
        self.series_db = self._load_series_database()

        # シリーズディレクトリの作成
        os.makedirs("series_management", exist_ok=True)

        print(f"[シリーズ管理] 記事シリーズ追跡システム起動")

    def _load_series_database(self) -> Dict[str, Any]:
        """シリーズデータベース読み込み"""

        if os.path.exists(self.series_db_path):
            with open(self.series_db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {
                "active_series": {},
                "completed_series": {},
                "series_counter": 0,
                "last_updated": None
            }

    def register_next_topic(self, current_article_title: str, next_topic: str, category: str = "AI活用") -> str:
        """次回記事予告の登録"""

        series_id = self._get_or_create_series_id(category)

        next_entry = {
            "series_id": series_id,
            "category": category,
            "next_topic": next_topic,
            "promised_in": current_article_title,
            "promised_at": datetime.now().isoformat(),
            "status": "promised",
            "priority": "high"
        }

        # アクティブシリーズに追加
        if series_id not in self.series_db["active_series"]:
            self.series_db["active_series"][series_id] = {
                "category": category,
                "articles": [],
                "upcoming": [],
                "created_at": datetime.now().isoformat()
            }

        self.series_db["active_series"][series_id]["upcoming"].append(next_entry)

        # データベース保存
        self._save_database()

        print(f"[シリーズ管理] 次回記事予告登録: {next_topic}")
        print(f"[シリーズ管理] シリーズID: {series_id}")

        return series_id

    def get_next_article_suggestion(self) -> Optional[Dict[str, Any]]:
        """次に書くべき記事の提案"""

        # 最優先：約束された記事
        for series_id, series_data in self.series_db["active_series"].items():
            for upcoming in series_data["upcoming"]:
                if upcoming["status"] == "promised":
                    return {
                        "type": "promised",
                        "series_id": series_id,
                        "topic": upcoming["next_topic"],
                        "category": upcoming["category"],
                        "promised_in": upcoming["promised_in"],
                        "urgency": "high"
                    }

        return None

    def mark_article_completed(self, article_title: str, series_id: str = None):
        """記事完成の記録"""

        if series_id and series_id in self.series_db["active_series"]:
            # 約束された記事の完成
            series_data = self.series_db["active_series"][series_id]

            # upcomingから該当記事を削除してarticlesに移動
            for i, upcoming in enumerate(series_data["upcoming"]):
                if upcoming["status"] == "promised":
                    completed_entry = {
                        "title": article_title,
                        "topic": upcoming["next_topic"],
                        "completed_at": datetime.now().isoformat(),
                        "series_position": len(series_data["articles"]) + 1
                    }

                    series_data["articles"].append(completed_entry)
                    series_data["upcoming"].pop(i)
                    break

        self._save_database()
        print(f"[シリーズ管理] 記事完成記録: {article_title}")

    def _get_or_create_series_id(self, category: str) -> str:
        """カテゴリに対応するシリーズIDを取得または新規作成"""

        # 既存のアクティブシリーズを検索
        for series_id, series_data in self.series_db["active_series"].items():
            if series_data["category"] == category:
                return series_id

        # 新規シリーズ作成
        self.series_db["series_counter"] += 1
        new_series_id = f"{category.replace(' ', '_').lower()}_{self.series_db['series_counter']:03d}"

        return new_series_id

    def generate_natural_next_preview(self, next_topic: str, tone: str = "casual") -> str:
        """自然な次回予告文の生成（辛辣表現は使わない）"""

        preview_patterns = [
            f"次回は「{next_topic}」について書こうと思います。",
            f"今度は「{next_topic}」の話をしますね。",
            f"次は「{next_topic}」について詳しく。",
            f"「{next_topic}」についても面白い話があるので、また書きます。",
            f"次回のテーマは「{next_topic}」です。"
        ]

        import random
        return random.choice(preview_patterns)

    def get_series_status(self) -> Dict[str, Any]:
        """現在のシリーズ状況"""

        status = {
            "active_series_count": len(self.series_db["active_series"]),
            "total_promised_articles": 0,
            "urgent_articles": [],
            "series_details": []
        }

        for series_id, series_data in self.series_db["active_series"].items():
            promised_count = len([u for u in series_data["upcoming"] if u["status"] == "promised"])
            status["total_promised_articles"] += promised_count

            # 緊急度の高い約束された記事
            for upcoming in series_data["upcoming"]:
                if upcoming["status"] == "promised":
                    days_since_promise = (datetime.now() - datetime.fromisoformat(upcoming["promised_at"])).days
                    if days_since_promise > 3:  # 3日以上経過
                        status["urgent_articles"].append({
                            "topic": upcoming["next_topic"],
                            "days_waiting": days_since_promise,
                            "promised_in": upcoming["promised_in"]
                        })

            status["series_details"].append({
                "series_id": series_id,
                "category": series_data["category"],
                "completed_articles": len(series_data["articles"]),
                "promised_articles": promised_count
            })

        return status

    def _save_database(self):
        """データベース保存"""

        self.series_db["last_updated"] = datetime.now().isoformat()

        with open(self.series_db_path, "w", encoding="utf-8") as f:
            json.dump(self.series_db, f, ensure_ascii=False, indent=2)

        print(f"[シリーズ管理] データベース更新完了")


class SeriesIntegration:
    """シリーズ管理とライティングシステムの統合"""

    def __init__(self):
        self.tracker = SeriesTracker()

    def process_article_completion(self, article_data: Dict[str, Any]):
        """記事完成時の自動処理"""

        title = article_data.get("title", "")
        content = article_data.get("content", "")

        # 次回予告の自動検出
        next_topic = self._extract_next_topic_from_content(content)

        if next_topic:
            # シリーズに登録
            series_id = self.tracker.register_next_topic(
                current_article_title=title,
                next_topic=next_topic,
                category="AI活用"
            )

            # 自然な予告文に変換
            natural_preview = self.tracker.generate_natural_next_preview(next_topic)

            print(f"[シリーズ統合] 次回予告自動登録: {next_topic}")
            return natural_preview

        return None

    def _extract_next_topic_from_content(self, content: str) -> Optional[str]:
        """記事コンテンツから次回トピックを抽出"""

        # 「次回は」「次は」「今度は」などのパターンを検索
        import re

        patterns = [
            r"次回は[「『](.*?)[」』]",
            r"次は[「『](.*?)[」』]",
            r"今度は[「『](.*?)[」』]"
        ]

        for pattern in patterns:
            matches = re.search(pattern, content)
            if matches:
                return matches.group(1)

        return None

    def get_next_writing_suggestion(self) -> Optional[Dict[str, Any]]:
        """次に書くべき記事の提案"""

        return self.tracker.get_next_article_suggestion()


def test_series_management():
    """シリーズ管理システムのテスト"""

    print("📚 シリーズ管理システムテスト")
    print("=" * 60)

    integration = SeriesIntegration()

    # テスト1: 記事完成処理
    print("\n[テスト1] 記事完成処理")
    test_article = {
        "title": "AI導入失敗の現実分析",
        "content": "...記事本文... 次回は『Excel地獄から脱出する7つの実践的手順』について書こうと思います。"
    }

    preview = integration.process_article_completion(test_article)
    print(f"生成された自然な予告文: {preview}")

    # テスト2: 次の記事提案
    print("\n[テスト2] 次の記事提案")
    suggestion = integration.get_next_writing_suggestion()
    if suggestion:
        print(f"提案記事: {suggestion['topic']}")
        print(f"緊急度: {suggestion['urgency']}")

    # テスト3: シリーズ状況
    print("\n[テスト3] シリーズ状況")
    status = integration.tracker.get_series_status()
    print(f"アクティブシリーズ数: {status['active_series_count']}")
    print(f"約束済み記事数: {status['total_promised_articles']}")


if __name__ == "__main__":
    test_series_management()