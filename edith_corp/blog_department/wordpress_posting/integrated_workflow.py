#!/usr/bin/env python3
"""
統合ワークフロー（非推奨ラッパー）
ContentTaisho に委任するだけの薄いラッパー。
直接 ContentTaisho.execute_daily_blog_mission() を使うことを推奨。
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, Any

# Path(__file__)ベースでインポート
_THIS_DIR = Path(__file__).resolve().parent
_BLOG_DEPT_DIR = _THIS_DIR.parent

sys.path.insert(0, str(_BLOG_DEPT_DIR / "content_taisho"))

try:
    from content_taisho import ContentTaisho
except ImportError as e:
    ContentTaisho = None
    print(f"[統合ワークフロー] ContentTaisho インポート失敗: {e}")


class IntegratedContentWorkflow:
    """統合コンテンツワークフロー（非推奨 → ContentTaishoへ委任）"""

    def __init__(self):
        warnings.warn(
            "IntegratedContentWorkflow is deprecated. Use ContentTaisho directly.",
            DeprecationWarning,
            stacklevel=2
        )
        print(f"[統合ワークフロー] 非推奨ラッパーとして起動")
        print(f"[統合ワークフロー] 推奨: ContentTaisho.execute_daily_blog_mission() を直接使用")

    def create_complete_article(self, article_brief: Dict[str, Any], publish_mode: str = "draft") -> Dict[str, Any]:
        """ContentTaisho に委任して完全記事作成"""

        if not ContentTaisho:
            return {
                "workflow_success": False,
                "error": "ContentTaisho import failed"
            }

        try:
            taisho = ContentTaisho()
            mission_params = {
                "target_audience": article_brief.get("target_audience", "中小企業経営者・個人事業主"),
                "content_strategy": "問題解決型",
                "focus_area": article_brief.get("topic", "AI・デジタル化"),
            }
            result = taisho.execute_daily_blog_mission(mission_params)

            return {
                "workflow_success": result.get("status") == "success",
                "article_directory": result.get("final_deliverables", {}).get("article_directory"),
                "mission_result": result,
                "completed_at": result.get("completed_at"),
            }
        except Exception as e:
            return {
                "workflow_success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    print("統合ワークフロー（非推奨）テスト")
    print("ContentTaisho.execute_daily_blog_mission() を直接使用してください。")
