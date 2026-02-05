#!/usr/bin/env python3
"""
EDITH階層型Agent組織システム
参考: https://zenn.dev/shio_shoppaize/articles/5fee11d03a11a1
"""

import yaml
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any
import os

@dataclass
class TaskOrder:
    """タスク指令書（YAML形式）"""
    task_id: str
    priority: int
    assigned_agent: str
    task_type: str
    description: str
    input_data: Dict[str, Any]
    deadline: str
    dependencies: List[str]
    status: str = "pending"

@dataclass
class AgentReport:
    """エージェント報告書（YAML形式）"""
    agent_id: str
    task_id: str
    status: str
    output_data: Dict[str, Any]
    quality_score: float
    execution_time: float
    next_recommendations: List[str]
    timestamp: str

class StrategyAgent:
    """戦略Agent（家老役）"""

    def __init__(self):
        self.agent_id = "strategy_karo"
        self.specialized_skills = [
            "task_decomposition",
            "priority_assignment",
            "resource_allocation",
            "quality_coordination"
        ]

    def decompose_mission(self, mission: Dict[str, Any]) -> List[TaskOrder]:
        """ミッションをタスクに分解"""

        # 例：ブログ記事生成ミッションの分解
        if mission["type"] == "blog_article_generation":
            tasks = [
                TaskOrder(
                    task_id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_01",
                    priority=1,
                    assigned_agent="content_structure_agent",
                    task_type="structure_design",
                    description="記事構成設計",
                    input_data={"memo": mission["memo"], "target_audience": "entrepreneurs"},
                    deadline="30min",
                    dependencies=[]
                ),
                TaskOrder(
                    task_id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_02",
                    priority=2,
                    assigned_agent="narita_writing_agent",
                    task_type="content_writing",
                    description="成田悠輔風ライティング",
                    input_data={"structure": "from_task_01"},
                    deadline="45min",
                    dependencies=["task_01"]
                ),
                TaskOrder(
                    task_id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_03",
                    priority=3,
                    assigned_agent="seo_agent",
                    task_type="seo_optimization",
                    description="SEO最適化",
                    input_data={"content": "from_task_02"},
                    deadline="15min",
                    dependencies=["task_02"]
                )
            ]
            return tasks

        return []

    def save_task_orders(self, tasks: List[TaskOrder], output_dir: str = "orders"):
        """タスク指令書をYAMLで保存"""
        os.makedirs(output_dir, exist_ok=True)

        for task in tasks:
            task_data = {
                "task_id": task.task_id,
                "priority": task.priority,
                "assigned_agent": task.assigned_agent,
                "task_type": task.task_type,
                "description": task.description,
                "input_data": task.input_data,
                "deadline": task.deadline,
                "dependencies": task.dependencies,
                "status": task.status
            }

            with open(f"{output_dir}/{task.task_id}.yaml", "w", encoding="utf-8") as f:
                yaml.dump(task_data, f, default_flow_style=False, allow_unicode=True)

class EDITHCommandCenter:
    """EDITH指揮センター（将軍役）"""

    def __init__(self):
        self.strategy_agent = StrategyAgent()
        self.active_missions = []
        self.completed_missions = []

    def receive_mission(self, mission_request: str, context: Dict[str, Any] = None):
        """経営者からのミッション受領"""

        mission = {
            "id": f"mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": self._classify_mission(mission_request),
            "request": mission_request,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }

        print(f"[EDITH] ミッション受領: {mission['type']}")
        print(f"[EDITH] 戦略Agentにタスク分解を指示...")

        # 戦略Agentにタスク分解指示
        tasks = self.strategy_agent.decompose_mission(mission)

        # タスク指令書生成
        self.strategy_agent.save_task_orders(tasks)

        print(f"[EDITH] {len(tasks)}個のタスクに分解完了")
        print(f"[EDITH] 各専門Agentに指令送信中...")

        return {
            "mission_id": mission["id"],
            "tasks_generated": len(tasks),
            "execution_status": "initiated"
        }

    def _classify_mission(self, request: str) -> str:
        """ミッション種別の自動判定"""
        if "ブログ" in request or "記事" in request:
            return "blog_article_generation"
        elif "戦略" in request or "企画" in request:
            return "strategy_planning"
        elif "分析" in request:
            return "data_analysis"
        else:
            return "general_task"

def test_hierarchy_system():
    """階層システムのテスト実行"""

    print("=" * 50)
    print("EDITH階層型Agent組織システム テスト開始")
    print("=" * 50)

    # EDITH司令部初期化
    edith = EDITHCommandCenter()

    # 経営者からのミッション例
    mission_request = "FAXでAI導入を検討している取引先についてブログ記事を書いて"
    context = {
        "memo_file": "input/test_memo.txt",
        "target_tone": "成田悠輔風",
        "output_destination": "WordPress下書き"
    }

    # ミッション実行
    result = edith.receive_mission(mission_request, context)

    print(f"\n[結果] ミッションID: {result['mission_id']}")
    print(f"[結果] 生成タスク数: {result['tasks_generated']}")
    print(f"[結果] 実行状態: {result['execution_status']}")

    print("\n" + "=" * 50)
    print("生成されたタスク指令書を確認してください: ./orders/")
    print("=" * 50)

if __name__ == "__main__":
    test_hierarchy_system()