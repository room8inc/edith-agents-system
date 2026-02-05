#!/usr/bin/env python3
"""
戦略的記憶システム - 自律的な学習・記録・改善
重要な発見や戦略を自動的に保存・活用
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class StrategicMemory:
    """戦略的記憶の自律管理システム"""

    def __init__(self):
        self.memory_root = Path("/Users/tsuruta/Documents/000AGENTS/edith_corp/strategic_memory")
        self.memory_root.mkdir(exist_ok=True)

        # 記憶カテゴリ別のディレクトリ
        self.dirs = {
            "strategies": self.memory_root / "strategies",
            "discoveries": self.memory_root / "discoveries",
            "performance": self.memory_root / "performance",
            "patterns": self.memory_root / "patterns",
            "failures": self.memory_root / "failures"
        }

        # ディレクトリ作成
        for dir_path in self.dirs.values():
            dir_path.mkdir(exist_ok=True)

        # メモリバンク初期化
        self.memory_bank = self._load_memory_bank()

        print(f"[戦略記憶] 自律記憶システム起動")
        print(f"[戦略記憶] 記憶カテゴリ: {len(self.dirs)}種類")

    def _load_memory_bank(self) -> Dict[str, Any]:
        """既存の記憶バンクを読み込み"""

        bank_file = self.memory_root / "memory_bank.json"

        if bank_file.exists():
            with open(bank_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {
                "total_memories": 0,
                "categories": {
                    "strategies": [],
                    "discoveries": [],
                    "performance": [],
                    "patterns": [],
                    "failures": []
                },
                "last_updated": None
            }

    def auto_save_insight(self, insight_type: str, data: Dict[str, Any], context: str = None) -> bool:
        """重要な発見を自動保存"""

        print(f"[戦略記憶] 💾 自動保存開始: {insight_type}")

        # インサイトの分類と処理
        if insight_type == "success_pattern":
            return self._save_success_pattern(data, context)

        elif insight_type == "keyword_discovery":
            return self._save_keyword_discovery(data, context)

        elif insight_type == "performance_milestone":
            return self._save_performance_milestone(data, context)

        elif insight_type == "failure_learning":
            return self._save_failure_learning(data, context)

        elif insight_type == "strategic_decision":
            return self._save_strategic_decision(data, context)

        else:
            # 未分類のインサイトも保存
            return self._save_general_insight(insight_type, data, context)

    def _save_success_pattern(self, data: Dict[str, Any], context: str) -> bool:
        """成功パターンの保存"""

        pattern = {
            "pattern_id": f"success_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "pattern_type": data.get("type", "unknown"),
            "description": data.get("description", ""),
            "metrics": data.get("metrics", {}),
            "reproducibility": data.get("reproducibility", "unknown"),
            "context": context,
            "applied_count": 0,
            "success_rate": 0.0
        }

        # ファイル保存
        pattern_file = self.dirs["patterns"] / f"{pattern['pattern_id']}.json"
        with open(pattern_file, "w", encoding="utf-8") as f:
            json.dump(pattern, f, ensure_ascii=False, indent=2)

        # メモリバンクに追加
        self.memory_bank["categories"]["patterns"].append({
            "id": pattern["pattern_id"],
            "type": pattern["pattern_type"],
            "metrics": pattern["metrics"],
            "file": str(pattern_file)
        })

        # 戦略ドキュメント自動更新
        self._update_strategy_document(pattern)

        print(f"[戦略記憶] ✅ 成功パターン保存: {pattern['pattern_id']}")
        return True

    def _save_keyword_discovery(self, data: Dict[str, Any], context: str) -> bool:
        """キーワード発見の保存"""

        discovery = {
            "discovery_id": f"keyword_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "keyword": data.get("keyword", ""),
            "search_volume": data.get("search_volume", 0),
            "competition": data.get("competition", "unknown"),
            "ctr": data.get("ctr", 0),
            "position": data.get("position", 0),
            "potential_traffic": data.get("potential_traffic", 0),
            "context": context,
            "status": "discovered",
            "action_taken": None
        }

        # ファイル保存
        discovery_file = self.dirs["discoveries"] / f"{discovery['discovery_id']}.json"
        with open(discovery_file, "w", encoding="utf-8") as f:
            json.dump(discovery, f, ensure_ascii=False, indent=2)

        # キーワードバンクに追加
        self._append_to_keyword_bank(discovery)

        print(f"[戦略記憶] ✅ キーワード発見保存: {discovery['keyword']}")
        return True

    def _save_performance_milestone(self, data: Dict[str, Any], context: str) -> bool:
        """パフォーマンスマイルストーンの保存"""

        milestone = {
            "milestone_id": f"perf_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "metric_name": data.get("metric", ""),
            "value": data.get("value", 0),
            "previous_value": data.get("previous_value", 0),
            "change_percentage": data.get("change_percentage", 0),
            "target_value": data.get("target_value", 0),
            "achievement_rate": data.get("achievement_rate", 0),
            "context": context
        }

        # ファイル保存
        perf_file = self.dirs["performance"] / f"{milestone['milestone_id']}.json"
        with open(perf_file, "w", encoding="utf-8") as f:
            json.dump(milestone, f, ensure_ascii=False, indent=2)

        # パフォーマンストレンド更新
        self._update_performance_trends(milestone)

        print(f"[戦略記憶] ✅ パフォーマンス記録: {milestone['metric_name']} = {milestone['value']}")
        return True

    def _save_failure_learning(self, data: Dict[str, Any], context: str) -> bool:
        """失敗からの学習を保存"""

        learning = {
            "learning_id": f"failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "failure_type": data.get("type", "unknown"),
            "description": data.get("description", ""),
            "root_cause": data.get("root_cause", "unknown"),
            "impact": data.get("impact", {}),
            "lesson_learned": data.get("lesson", ""),
            "prevention_measure": data.get("prevention", ""),
            "context": context,
            "prevented_count": 0
        }

        # ファイル保存
        failure_file = self.dirs["failures"] / f"{learning['learning_id']}.json"
        with open(failure_file, "w", encoding="utf-8") as f:
            json.dump(learning, f, ensure_ascii=False, indent=2)

        print(f"[戦略記憶] ✅ 失敗学習保存: {learning['failure_type']}")
        return True

    def _save_strategic_decision(self, data: Dict[str, Any], context: str) -> bool:
        """戦略的決定の保存"""

        decision = {
            "decision_id": f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "decision_type": data.get("type", "unknown"),
            "title": data.get("title", ""),
            "rationale": data.get("rationale", ""),
            "expected_outcome": data.get("expected_outcome", {}),
            "actual_outcome": None,
            "status": "active",
            "context": context
        }

        # ファイル保存
        strategy_file = self.dirs["strategies"] / f"{decision['decision_id']}.json"
        with open(strategy_file, "w", encoding="utf-8") as f:
            json.dump(decision, f, ensure_ascii=False, indent=2)

        print(f"[戦略記憶] ✅ 戦略決定保存: {decision['title']}")
        return True

    def _save_general_insight(self, insight_type: str, data: Dict[str, Any], context: str) -> bool:
        """汎用インサイトの保存"""

        insight = {
            "insight_id": f"general_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "type": insight_type,
            "data": data,
            "context": context
        }

        # 適切なディレクトリに保存
        general_file = self.memory_root / f"general_{insight['insight_id']}.json"
        with open(general_file, "w", encoding="utf-8") as f:
            json.dump(insight, f, ensure_ascii=False, indent=2)

        print(f"[戦略記憶] ✅ インサイト保存: {insight_type}")
        return True

    def _update_strategy_document(self, pattern: Dict[str, Any]):
        """戦略ドキュメントの自動更新"""

        strategy_doc = self.memory_root.parent / "blog_department" / "seo_strategy.md"

        if not strategy_doc.exists():
            return

        # 既存内容読み込み
        with open(strategy_doc, "r", encoding="utf-8") as f:
            content = f.read()

        # 新しいパターンを追加
        new_section = f"\n\n### 自動発見パターン ({pattern['pattern_id']})\n"
        new_section += f"- **発見日時**: {pattern['timestamp']}\n"
        new_section += f"- **パターン**: {pattern['description']}\n"
        new_section += f"- **メトリクス**: {json.dumps(pattern['metrics'], ensure_ascii=False)}\n"

        # 適切な位置に挿入（実装簡略化のため末尾に追加）
        content += new_section

        with open(strategy_doc, "w", encoding="utf-8") as f:
            f.write(content)

    def _append_to_keyword_bank(self, discovery: Dict[str, Any]):
        """キーワードバンクへの追加"""

        keyword_bank_file = self.memory_root / "keyword_bank.json"

        if keyword_bank_file.exists():
            with open(keyword_bank_file, "r", encoding="utf-8") as f:
                keyword_bank = json.load(f)
        else:
            keyword_bank = {"keywords": [], "last_updated": None}

        keyword_bank["keywords"].append({
            "keyword": discovery["keyword"],
            "discovered_at": discovery["timestamp"],
            "metrics": {
                "ctr": discovery["ctr"],
                "position": discovery["position"],
                "potential": discovery["potential_traffic"]
            }
        })
        keyword_bank["last_updated"] = datetime.now().isoformat()

        with open(keyword_bank_file, "w", encoding="utf-8") as f:
            json.dump(keyword_bank, f, ensure_ascii=False, indent=2)

    def _update_performance_trends(self, milestone: Dict[str, Any]):
        """パフォーマンストレンドの更新"""

        trends_file = self.memory_root / "performance_trends.json"

        if trends_file.exists():
            with open(trends_file, "r", encoding="utf-8") as f:
                trends = json.load(f)
        else:
            trends = {"metrics": {}, "last_updated": None}

        metric = milestone["metric_name"]
        if metric not in trends["metrics"]:
            trends["metrics"][metric] = []

        trends["metrics"][metric].append({
            "timestamp": milestone["timestamp"],
            "value": milestone["value"],
            "change": milestone["change_percentage"]
        })
        trends["last_updated"] = datetime.now().isoformat()

        with open(trends_file, "w", encoding="utf-8") as f:
            json.dump(trends, f, ensure_ascii=False, indent=2)

    def recall_relevant_memories(self, context: str) -> List[Dict[str, Any]]:
        """関連する記憶の想起"""

        relevant_memories = []

        # コンテキストに基づいて関連記憶を検索
        for category, items in self.memory_bank["categories"].items():
            for item in items:
                # 簡易的な関連性判定（実際はより高度な実装が必要）
                if context.lower() in str(item).lower():
                    relevant_memories.append({
                        "category": category,
                        "memory": item
                    })

        print(f"[戦略記憶] 🔍 関連記憶 {len(relevant_memories)}件を想起")
        return relevant_memories

    def save_memory_bank(self):
        """メモリバンクの保存"""

        self.memory_bank["total_memories"] = sum(
            len(items) for items in self.memory_bank["categories"].values()
        )
        self.memory_bank["last_updated"] = datetime.now().isoformat()

        bank_file = self.memory_root / "memory_bank.json"
        with open(bank_file, "w", encoding="utf-8") as f:
            json.dump(self.memory_bank, f, ensure_ascii=False, indent=2)

        print(f"[戦略記憶] 💾 メモリバンク保存: {self.memory_bank['total_memories']}件")

    def get_memory_stats(self) -> Dict[str, Any]:
        """記憶統計の取得"""

        stats = {
            "total_memories": self.memory_bank["total_memories"],
            "by_category": {
                category: len(items)
                for category, items in self.memory_bank["categories"].items()
            },
            "last_updated": self.memory_bank["last_updated"],
            "storage_used": sum(
                os.path.getsize(f) for f in self.memory_root.rglob("*.json")
            ) / 1024  # KB
        }

        return stats


class MemoryIntegration:
    """他システムとの記憶統合"""

    def __init__(self):
        self.memory = StrategicMemory()
        print(f"[記憶統合] 自律記憶システム統合完了")

    def on_seo_analysis_complete(self, analysis_data: Dict[str, Any]):
        """SEO分析完了時の自動記録"""

        # 高CTRキーワードを自動保存
        if "top_keywords" in analysis_data:
            for keyword in analysis_data["top_keywords"]:
                if keyword.get("ctr", 0) > 0.2:  # CTR 20%以上
                    self.memory.auto_save_insight(
                        "keyword_discovery",
                        keyword,
                        "SEO分析で高CTRキーワード発見"
                    )

        # 改善機会を自動保存
        if "opportunities" in analysis_data:
            for opportunity in analysis_data["opportunities"]:
                self.memory.auto_save_insight(
                    "success_pattern",
                    {
                        "type": "seo_opportunity",
                        "description": opportunity.get("description", ""),
                        "metrics": {
                            "potential_traffic": opportunity.get("potential_clicks", 0)
                        }
                    },
                    "SEO改善機会発見"
                )

    def on_article_published(self, article_data: Dict[str, Any]):
        """記事公開時の自動記録"""

        self.memory.auto_save_insight(
            "performance_milestone",
            {
                "metric": "articles_published",
                "value": 1,
                "article_title": article_data.get("title", ""),
                "expected_mau_impact": article_data.get("expected_mau_impact", 0)
            },
            "新規記事公開"
        )

    def on_mau_update(self, new_mau: int, previous_mau: int):
        """MAU更新時の自動記録"""

        change_percentage = ((new_mau - previous_mau) / previous_mau * 100) if previous_mau > 0 else 0

        self.memory.auto_save_insight(
            "performance_milestone",
            {
                "metric": "MAU",
                "value": new_mau,
                "previous_value": previous_mau,
                "change_percentage": change_percentage,
                "target_value": 15000,
                "achievement_rate": (new_mau / 15000) * 100
            },
            "MAU更新"
        )

    def on_strategy_decision(self, decision_data: Dict[str, Any]):
        """戦略決定時の自動記録"""

        self.memory.auto_save_insight(
            "strategic_decision",
            decision_data,
            "戦略的意思決定"
        )

    def on_error_occurred(self, error_data: Dict[str, Any]):
        """エラー発生時の自動学習"""

        self.memory.auto_save_insight(
            "failure_learning",
            {
                "type": error_data.get("error_type", "unknown"),
                "description": error_data.get("error_message", ""),
                "root_cause": error_data.get("root_cause", "unknown"),
                "lesson": error_data.get("lesson", ""),
                "prevention": error_data.get("prevention", "")
            },
            "エラーからの学習"
        )


def test_strategic_memory():
    """戦略記憶システムのテスト"""

    print("=" * 60)
    print("戦略記憶システム テスト")
    print("=" * 60)

    # 統合システム初期化
    integration = MemoryIntegration()

    # テストデータで自動記録をシミュレート

    # 1. SEO分析結果の自動保存
    print("\n[テスト] SEO分析結果の自動記録")
    integration.on_seo_analysis_complete({
        "top_keywords": [
            {"keyword": "AI導入 失敗", "ctr": 0.35, "position": 8},
            {"keyword": "ChatGPT 比較", "ctr": 0.28, "position": 12}
        ],
        "opportunities": [
            {"description": "タイトル最適化で流入30%増", "potential_clicks": 150}
        ]
    })

    # 2. MAU更新の自動記録
    print("\n[テスト] MAU更新の自動記録")
    integration.on_mau_update(12000, 11000)

    # 3. 戦略決定の自動記録
    print("\n[テスト] 戦略決定の自動記録")
    integration.on_strategy_decision({
        "type": "content_strategy",
        "title": "ロングテールキーワード重視",
        "rationale": "Geminiキーワードで成功したパターンを横展開",
        "expected_outcome": {"mau_increase": 4000}
    })

    # 統計表示
    stats = integration.memory.get_memory_stats()
    print(f"\n📊 記憶統計:")
    print(f"  総記憶数: {stats['total_memories']}")
    print(f"  カテゴリ別: {stats['by_category']}")
    print(f"  使用容量: {stats['storage_used']:.2f} KB")

    # メモリバンク保存
    integration.memory.save_memory_bank()

    print("\n✅ 戦略記憶システム正常動作")


if __name__ == "__main__":
    test_strategic_memory()