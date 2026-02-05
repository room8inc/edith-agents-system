#!/usr/bin/env python3
"""
戦略Agent（家老） - 企画調整担当
EDITHからのミッションを戦術レベルに分解し、足軽部隊を指揮
"""

import json
from datetime import datetime
from typing import Dict, List, Any

class StrategyKaro:
    """戦略Agent（家老役）"""

    def __init__(self):
        self.rank = "Karo"
        self.specialty = "Strategy & Coordination"
        self.reports_to = "EDITH"

        print(f"[{self.rank}] 戦略Agent初期化")

    def decompose_mission(self, mission_type: str) -> Dict[str, Any]:
        """ミッションの戦術分解"""

        print(f"[{self.rank}] ミッション分解開始: {mission_type}")

        if mission_type == "daily_blog":
            return self._decompose_daily_blog_mission()
        elif mission_type == "room8_strategy":
            return self._decompose_room8_strategy()
        else:
            return self._decompose_general_mission(mission_type)

    def _decompose_daily_blog_mission(self) -> Dict[str, Any]:
        """日刊ブログミッションの分解"""

        mission_id = f"daily_blog_{datetime.now().strftime('%Y%m%d')}"

        orders = [
            {
                "order_id": f"{mission_id}_01",
                "assigned_agent": "research_ashigaru",
                "description": "トレンド・ネタ調査",
                "priority": 1,
                "estimated_time": "15分"
            },
            {
                "order_id": f"{mission_id}_02",
                "assigned_agent": "content_ashigaru",
                "description": "記事構成・ライティング",
                "priority": 2,
                "estimated_time": "45分"
            },
            {
                "order_id": f"{mission_id}_03",
                "assigned_agent": "seo_ashigaru",
                "description": "SEO最適化",
                "priority": 3,
                "estimated_time": "15分"
            },
            {
                "order_id": f"{mission_id}_04",
                "assigned_agent": "image_ashigaru",
                "description": "画像企画・生成",
                "priority": 4,
                "estimated_time": "20分"
            },
            {
                "order_id": f"{mission_id}_05",
                "assigned_agent": "wordpress_ashigaru",
                "description": "WordPress投稿準備",
                "priority": 5,
                "estimated_time": "10分"
            }
        ]

        mission_plan = {
            "mission_id": mission_id,
            "mission_type": "daily_blog",
            "total_agents": len(orders),
            "estimated_total_time": "105分",
            "orders": orders,
            "success_criteria": "WordPress下書き投稿完了",
            "created_at": datetime.now().isoformat()
        }

        print(f"[{self.rank}] ブログミッション分解完了: {len(orders)}個の指令")
        return mission_plan

    def _decompose_room8_strategy(self) -> Dict[str, Any]:
        """Room8戦略ミッションの分解"""

        mission_id = f"room8_strategy_{datetime.now().strftime('%Y%m%d')}"

        orders = [
            {
                "order_id": f"{mission_id}_01",
                "assigned_agent": "research_ashigaru",
                "description": "競合コミュニティ調査",
                "priority": 1,
                "estimated_time": "30分"
            },
            {
                "order_id": f"{mission_id}_02",
                "assigned_agent": "analytics_ashigaru",
                "description": "既存MAU分析",
                "priority": 2,
                "estimated_time": "25分"
            }
        ]

        mission_plan = {
            "mission_id": mission_id,
            "mission_type": "room8_strategy",
            "total_agents": len(orders),
            "orders": orders,
            "created_at": datetime.now().isoformat()
        }

        return mission_plan

    def _decompose_general_mission(self, mission_type: str) -> Dict[str, Any]:
        """汎用ミッション分解"""

        return {
            "mission_id": f"general_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "mission_type": mission_type,
            "status": "analysis_required",
            "message": "未対応ミッション種別です。詳細分析が必要です。"
        }

    def save_mission_plan(self, mission_plan: Dict[str, Any]):
        """作戦計画の保存"""

        mission_file = f"../missions/{mission_plan['mission_id']}.json"

        with open(mission_file, "w", encoding="utf-8") as f:
            json.dump(mission_plan, f, ensure_ascii=False, indent=2)

        print(f"[{self.rank}] 作戦計画保存: {mission_file}")

if __name__ == "__main__":
    karo = StrategyKaro()
    plan = karo.decompose_mission("daily_blog")
    print(json.dumps(plan, indent=2, ensure_ascii=False))