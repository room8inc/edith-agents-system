#!/usr/bin/env python3
"""
自律的記憶システム - 重要な発見・戦略を自動保存
「保存して」と言われなくても、価値ある情報は自動的に蓄積される
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

class InsightType(Enum):
    """洞察タイプの分類"""
    SUCCESS_PATTERN = "success_pattern"        # 成功パターン
    KEYWORD_DISCOVERY = "keyword_discovery"    # キーワード発見
    STRATEGY_UPDATE = "strategy_update"        # 戦略更新
    PERFORMANCE_MILESTONE = "milestone"        # 実績達成
    FAILURE_LESSON = "failure_lesson"          # 失敗からの学び
    USER_PREFERENCE = "user_preference"        # ユーザーの好み
    COMPETITIVE_INTEL = "competitive_intel"    # 競合情報

class AutonomousMemory:
    """自律的記憶管理システム"""

    def __init__(self):
        self.memory_base = "knowledge_base"
        self.importance_threshold = 0.7  # 重要度閾値
        self._ensure_memory_structure()

        print(f"[自律記憶] システム起動 - 自動学習モード")

    def _ensure_memory_structure(self):
        """記憶構造の初期化"""

        directories = [
            f"{self.memory_base}/strategies",      # 戦略記憶
            f"{self.memory_base}/successes",       # 成功事例
            f"{self.memory_base}/keywords",        # キーワードDB
            f"{self.memory_base}/preferences",     # 好み・スタイル
            f"{self.memory_base}/lessons",         # 学習記録
            f"{self.memory_base}/daily_insights"   # 日次洞察
        ]

        for dir_path in directories:
            os.makedirs(dir_path, exist_ok=True)

    def observe_and_remember(self, context: str, data: Any) -> Optional[Dict]:
        """観察して重要なものを自動記憶"""

        # 重要度を自動判定
        importance = self._calculate_importance(context, data)

        if importance < self.importance_threshold:
            return None  # 重要でないものはスルー

        # コンテキストから洞察タイプを推定
        insight_type = self._infer_insight_type(context, data)

        # 自動的に適切な場所に保存
        memory_record = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "insight_type": insight_type.value,
            "importance": importance,
            "data": data,
            "auto_saved": True
        }

        # タイプに応じて保存
        self._save_by_type(insight_type, memory_record)

        print(f"[自律記憶] 💾 自動保存: {insight_type.value} (重要度: {importance:.2f})")

        return memory_record

    def _calculate_importance(self, context: str, data: Any) -> float:
        """重要度の自動計算"""

        importance = 0.5  # ベースライン

        # キーワードベースの重要度判定
        high_value_keywords = [
            'CTR', '50%', '成功', 'パターン', '戦略',
            'ロングテール', '発見', 'Room8', 'Gemini',
            '増加', '改善', '効果的', 'MAU'
        ]

        context_str = str(context).lower()
        data_str = str(data).lower()

        for keyword in high_value_keywords:
            if keyword.lower() in context_str or keyword.lower() in data_str:
                importance += 0.1

        # 数値データがある場合
        if isinstance(data, dict):
            if any(key in data for key in ['ctr', 'clicks', 'impressions', 'growth']):
                importance += 0.2

            # 特に高い数値
            for value in data.values():
                if isinstance(value, (int, float)):
                    if value > 30:  # 30%以上の値
                        importance += 0.2

        # ユーザーからの明示的な評価
        positive_signals = ['いいね', 'その通り', 'OK', '素晴らしい', 'よき']
        if any(signal in context_str for signal in positive_signals):
            importance += 0.3

        return min(importance, 1.0)

    def _infer_insight_type(self, context: str, data: Any) -> InsightType:
        """コンテキストから洞察タイプを推定"""

        context_lower = context.lower()

        if 'キーワード' in context or 'keyword' in context_lower:
            return InsightType.KEYWORD_DISCOVERY
        elif '成功' in context or 'success' in context_lower or 'ctr' in context_lower:
            return InsightType.SUCCESS_PATTERN
        elif '戦略' in context or 'strategy' in context_lower:
            return InsightType.STRATEGY_UPDATE
        elif '失敗' in context or 'failure' in context_lower:
            return InsightType.FAILURE_LESSON
        elif 'ユーザー' in context or '好み' in context:
            return InsightType.USER_PREFERENCE
        elif '競合' in context or 'competitive' in context_lower:
            return InsightType.COMPETITIVE_INTEL
        else:
            return InsightType.SUCCESS_PATTERN  # デフォルト

    def _save_by_type(self, insight_type: InsightType, record: Dict):
        """タイプ別に適切な場所に保存"""

        if insight_type == InsightType.SUCCESS_PATTERN:
            self._save_success_pattern(record)

        elif insight_type == InsightType.KEYWORD_DISCOVERY:
            self._save_keyword_discovery(record)

        elif insight_type == InsightType.STRATEGY_UPDATE:
            self._update_strategy(record)

        elif insight_type == InsightType.USER_PREFERENCE:
            self._save_preference(record)

        # 全ての洞察を日次ログにも保存
        self._save_daily_insight(record)

    def _save_success_pattern(self, record: Dict):
        """成功パターンの保存"""

        filepath = f"{self.memory_base}/successes/patterns_{datetime.now().strftime('%Y%m')}.json"

        patterns = []
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                patterns = json.load(f)

        patterns.append(record)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, ensure_ascii=False, indent=2)

    def _save_keyword_discovery(self, record: Dict):
        """キーワード発見の保存"""

        filepath = f"{self.memory_base}/keywords/discoveries.json"

        keywords = {}
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                keywords = json.load(f)

        # キーワードデータを抽出して追加
        if 'data' in record and isinstance(record['data'], dict):
            for key, value in record['data'].items():
                if 'keyword' in key.lower() or 'query' in key.lower():
                    keywords[value] = {
                        'discovered_at': record['timestamp'],
                        'context': record['context'],
                        'performance': record['data']
                    }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(keywords, f, ensure_ascii=False, indent=2)

    def _update_strategy(self, record: Dict):
        """戦略の更新"""

        filepath = f"{self.memory_base}/strategies/current_strategy.json"

        strategy = {}
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                strategy = json.load(f)

        # 戦略を更新
        strategy['last_updated'] = record['timestamp']
        strategy['updates'] = strategy.get('updates', [])
        strategy['updates'].append(record)

        # 最新の戦略要素を抽出
        if 'data' in record:
            strategy['current'] = record['data']

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(strategy, f, ensure_ascii=False, indent=2)

    def _save_preference(self, record: Dict):
        """ユーザー好みの保存"""

        filepath = f"{self.memory_base}/preferences/user_preferences.json"

        preferences = {}
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                preferences = json.load(f)

        # 好みを記録
        preference_key = record['context'][:50]  # キーとして最初の50文字
        preferences[preference_key] = {
            'preference': record['data'],
            'recorded_at': record['timestamp']
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(preferences, f, ensure_ascii=False, indent=2)

    def _save_daily_insight(self, record: Dict):
        """日次洞察の保存"""

        date_str = datetime.now().strftime('%Y%m%d')
        filepath = f"{self.memory_base}/daily_insights/{date_str}.json"

        insights = []
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                insights = json.load(f)

        insights.append(record)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(insights, f, ensure_ascii=False, indent=2)

    def recall(self, query: str, limit: int = 5) -> List[Dict]:
        """関連する記憶を想起"""

        print(f"[自律記憶] 🔍 想起: '{query}'")

        relevant_memories = []

        # キーワードDBを検索
        keyword_file = f"{self.memory_base}/keywords/discoveries.json"
        if os.path.exists(keyword_file):
            with open(keyword_file, 'r', encoding='utf-8') as f:
                keywords = json.load(f)
                for kw, data in keywords.items():
                    if query.lower() in kw.lower():
                        relevant_memories.append({
                            'type': 'keyword',
                            'content': kw,
                            'data': data
                        })

        # 戦略を検索
        strategy_file = f"{self.memory_base}/strategies/current_strategy.json"
        if os.path.exists(strategy_file):
            with open(strategy_file, 'r', encoding='utf-8') as f:
                strategy = json.load(f)
                if 'current' in strategy:
                    relevant_memories.append({
                        'type': 'strategy',
                        'content': strategy['current']
                    })

        return relevant_memories[:limit]

    def get_daily_summary(self) -> Dict[str, Any]:
        """本日の学習サマリー"""

        date_str = datetime.now().strftime('%Y%m%d')
        filepath = f"{self.memory_base}/daily_insights/{date_str}.json"

        if not os.path.exists(filepath):
            return {"message": "本日の学習記録はまだありません"}

        with open(filepath, 'r', encoding='utf-8') as f:
            insights = json.load(f)

        summary = {
            "date": date_str,
            "total_insights": len(insights),
            "by_type": {},
            "high_importance": []
        }

        for insight in insights:
            insight_type = insight.get('insight_type', 'unknown')
            summary['by_type'][insight_type] = summary['by_type'].get(insight_type, 0) + 1

            if insight.get('importance', 0) > 0.8:
                summary['high_importance'].append({
                    'context': insight['context'][:100],
                    'type': insight_type,
                    'importance': insight['importance']
                })

        return summary


class MemoryIntegration:
    """他システムとの統合"""

    def __init__(self):
        self.memory = AutonomousMemory()

    def observe_search_console_data(self, data: Dict):
        """Search Consoleデータを観察して自動記憶"""

        # 高CTRキーワードを自動保存
        if 'queries' in data:
            for query in data['queries']:
                if query.get('ctr', 0) > 0.2:  # CTR 20%以上
                    self.memory.observe_and_remember(
                        f"高CTRキーワード発見: {query['query']}",
                        query
                    )

        # 成功パターンを自動保存
        if 'performance_summary' in data:
            if data['performance_summary'].get('avg_ctr', 0) > 0.15:
                self.memory.observe_and_remember(
                    "高パフォーマンス期間",
                    data['performance_summary']
                )

    def observe_user_feedback(self, message: str):
        """ユーザーフィードバックを観察"""

        positive_keywords = ['いいね', 'その通り', 'OK', 'よき', '素晴らしい']

        if any(kw in message for kw in positive_keywords):
            # 直前のコンテキストと共に保存
            self.memory.observe_and_remember(
                f"ユーザー肯定的フィードバック: {message}",
                {"feedback": message, "sentiment": "positive"}
            )


def test_autonomous_memory():
    """自律記憶システムのテスト"""

    print("🧠 自律記憶システムテスト")
    print("=" * 60)

    memory = AutonomousMemory()

    # テストケース1: 成功パターンの自動記憶
    memory.observe_and_remember(
        "Geminiキーワードで高CTR達成",
        {"keyword": "google workspace gemini pro", "ctr": 0.50, "clicks": 26}
    )

    # テストケース2: 戦略の自動記憶
    memory.observe_and_remember(
        "ロングテール戦略が効果的",
        {"strategy": "3-4語キーワード重視", "growth": "+36%"}
    )

    # テストケース3: 重要度が低いものは記憶されない
    memory.observe_and_remember(
        "今日は晴れ",
        {"weather": "sunny"}
    )

    # 日次サマリー確認
    summary = memory.get_daily_summary()
    print(f"\n📊 本日の自動学習:")
    print(f"  総洞察数: {summary.get('total_insights', 0)}")
    print(f"  タイプ別: {summary.get('by_type', {})}")

    # 記憶の想起テスト
    recalled = memory.recall("Gemini")
    print(f"\n🔍 'Gemini'関連の記憶:")
    for mem in recalled:
        print(f"  - {mem['type']}: {mem.get('content', 'N/A')}")


if __name__ == "__main__":
    test_autonomous_memory()