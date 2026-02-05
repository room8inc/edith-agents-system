#!/usr/bin/env python3
"""
EDITH階層型Agent組織システム（ライブラリ最小版）
YAML形式での構造化通信をJSON代替で実装
"""

import json
from datetime import datetime
from typing import List, Dict, Any
import os

class TaskOrder:
    """タスク指令書"""
    def __init__(self, task_id: str, priority: int, assigned_agent: str, task_type: str,
                 description: str, input_data: Dict[str, Any], deadline: str, dependencies: List[str]):
        self.task_id = task_id
        self.priority = priority
        self.assigned_agent = assigned_agent
        self.task_type = task_type
        self.description = description
        self.input_data = input_data
        self.deadline = deadline
        self.dependencies = dependencies
        self.status = "pending"

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "priority": self.priority,
            "assigned_agent": self.assigned_agent,
            "task_type": self.task_type,
            "description": self.description,
            "input_data": self.input_data,
            "deadline": self.deadline,
            "dependencies": self.dependencies,
            "status": self.status
        }

class StrategyAgent:
    """戦略Agent（家老役）- タスク分解専門"""

    def __init__(self):
        self.agent_id = "strategy_karo"
        print(f"[{self.agent_id}] 戦略Agent初期化完了")

    def decompose_blog_mission(self, mission: Dict[str, Any]) -> List[TaskOrder]:
        """ブログ記事生成ミッションの戦略的分解"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        tasks = [
            TaskOrder(
                task_id=f"{timestamp}_01_structure",
                priority=1,
                assigned_agent="content_structure_ashigaru",
                task_type="structure_design",
                description="記事構成設計（タイトル・見出し・感情導線）",
                input_data={
                    "memo": mission.get("memo", ""),
                    "target_audience": "起業家・経営者",
                    "tone": "成田悠輔風毒舌",
                    "word_count_target": "2000-3000字"
                },
                deadline="30分",
                dependencies=[]
            ),
            TaskOrder(
                task_id=f"{timestamp}_02_writing",
                priority=2,
                assigned_agent="narita_writing_ashigaru",
                task_type="content_writing",
                description="成田悠輔風ライティング実行",
                input_data={
                    "structure_reference": f"{timestamp}_01_structure",
                    "tone_guidelines": "痛烈だが建設的、データ裏付け、読者共感"
                },
                deadline="45分",
                dependencies=[f"{timestamp}_01_structure"]
            ),
            TaskOrder(
                task_id=f"{timestamp}_03_seo",
                priority=3,
                assigned_agent="seo_optimization_ashigaru",
                task_type="seo_optimization",
                description="SEO最適化・メタ情報作成",
                input_data={
                    "content_reference": f"{timestamp}_02_writing",
                    "target_keywords": ["AI導入", "デジタル化", "起業家", "業務効率化"]
                },
                deadline="15分",
                dependencies=[f"{timestamp}_02_writing"]
            ),
            TaskOrder(
                task_id=f"{timestamp}_04_image",
                priority=4,
                assigned_agent="image_concept_ashigaru",
                task_type="image_planning",
                description="記事用画像企画・Gemini API指示生成",
                input_data={
                    "article_theme": "FAXとAIのギャップ",
                    "visual_style": "プロフェッショナル・インフォグラフィック"
                },
                deadline="20分",
                dependencies=[f"{timestamp}_01_structure"]
            ),
            TaskOrder(
                task_id=f"{timestamp}_05_wordpress",
                priority=5,
                assigned_agent="wordpress_publishing_ashigaru",
                task_type="wordpress_draft",
                description="WordPress下書き投稿",
                input_data={
                    "final_content": f"{timestamp}_02_writing",
                    "seo_meta": f"{timestamp}_03_seo",
                    "images": f"{timestamp}_04_image",
                    "publish_mode": "draft_only"
                },
                deadline="10分",
                dependencies=[f"{timestamp}_02_writing", f"{timestamp}_03_seo", f"{timestamp}_04_image"]
            )
        ]

        print(f"[{self.agent_id}] ブログ記事生成を{len(tasks)}個のタスクに戦略分解")
        return tasks

    def save_task_orders(self, tasks: List[TaskOrder], output_dir: str = "orders"):
        """タスク指令書をJSON形式で保存"""
        os.makedirs(output_dir, exist_ok=True)

        for task in tasks:
            with open(f"{output_dir}/{task.task_id}.json", "w", encoding="utf-8") as f:
                json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)

        print(f"[{self.agent_id}] {len(tasks)}件のタスク指令書を生成: {output_dir}/")

class EDITHCommandCenter:
    """EDITH指揮センター（将軍役）- 全体統括"""

    def __init__(self):
        self.agent_id = "EDITH_shogun"
        self.strategy_agent = StrategyAgent()
        self.active_missions = []
        print(f"[{self.agent_id}] EDITH司令部稼働開始")

    def execute_mission(self, mission_request: str, memo_content: str = None):
        """ミッション実行（経営者からの指示受領→完全自動実行）"""

        print(f"\n{'='*60}")
        print(f"[{self.agent_id}] 新規ミッション受領")
        print(f"[{self.agent_id}] 内容: {mission_request}")
        print(f"{'='*60}")

        # 1. ミッション分類・データ整備
        mission = {
            "id": f"mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": self._classify_mission(mission_request),
            "request": mission_request,
            "memo": memo_content,
            "timestamp": datetime.now().isoformat()
        }

        # 2. 戦略Agentにタスク分解指示
        print(f"[{self.agent_id}] 戦略Agent（家老）にタスク分解を指示...")

        if mission["type"] == "blog_article_generation":
            tasks = self.strategy_agent.decompose_blog_mission(mission)
        else:
            print(f"[{self.agent_id}] 未対応ミッション種別: {mission['type']}")
            return None

        # 3. タスク指令書生成・配布
        self.strategy_agent.save_task_orders(tasks)

        # 4. 実行状況報告
        print(f"\n[{self.agent_id}] ミッション分解完了:")
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task.assigned_agent} -> {task.description}")

        print(f"\n[{self.agent_id}] 各専門Agent（足軽）への指令配布完了")
        print(f"[{self.agent_id}] 実行フェーズに移行します...")

        return {
            "mission_id": mission["id"],
            "tasks_count": len(tasks),
            "strategy": "hierarchical_parallel_execution"
        }

    def _classify_mission(self, request: str) -> str:
        """ミッション自動分類"""
        keywords = {
            "blog_article_generation": ["ブログ", "記事", "コンテンツ", "ライティング", "書いて"],
            "strategy_planning": ["戦略", "企画", "計画", "方針"],
            "market_analysis": ["分析", "調査", "リサーチ", "データ"]
        }

        for mission_type, keyword_list in keywords.items():
            if any(keyword in request for keyword in keyword_list):
                return mission_type

        return "general_task"

def test_edith_system():
    """EDITH階層システムのテスト実行"""

    # メモファイル読み込み
    try:
        with open("input/test_memo.txt", "r", encoding="utf-8") as f:
            memo_content = f.read()
    except FileNotFoundError:
        memo_content = "FAXでAI導入を検討している取引先の事例。デジタル化の順序が完全に逆転している現状について。"

    # EDITH司令部初期化・ミッション実行
    edith = EDITHCommandCenter()

    mission_request = "取引先のFAX×AI導入事例についてブログ記事を書いて"
    result = edith.execute_mission(mission_request, memo_content)

    if result:
        print(f"\n{'='*60}")
        print(f"EDITH実行結果:")
        print(f"  ミッションID: {result['mission_id']}")
        print(f"  分解タスク数: {result['tasks_count']}")
        print(f"  実行戦略: {result['strategy']}")
        print(f"{'='*60}")

if __name__ == "__main__":
    test_edith_system()