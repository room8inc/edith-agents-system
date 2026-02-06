#!/usr/bin/env python3
"""
足軽共通CLIラッパー - 全足軽への統一エントリポイント
Task Toolエージェントが Bash python3 run_ashigaru.py <command> --json '{}' で呼び出す。
結果はstdoutにJSON出力される。
"""

import sys
import json
import traceback
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent


def _add_paths():
    """足軽モジュールのインポートパスを追加"""
    dirs = [
        "research", "keyword_strategy", "structure", "writing",
        "seo_specialist_ashigaru", "social_media_ashigaru",
        "analytics_ashigaru", "image_generation", "wordpress_posting",
    ]
    for d in dirs:
        p = str(_THIS_DIR / d)
        if p not in sys.path:
            sys.path.insert(0, p)


def cmd_research(params: dict) -> dict:
    """リサーチ足軽: トレンド調査・記事企画"""
    from research_agent import ResearchAshigaru
    agent = ResearchAshigaru()
    return agent.execute_research_mission(params)


def cmd_seo(params: dict) -> dict:
    """SEO足軽: キーワード分析・最適化"""
    from seo_agent import SEOSpecialistAshigaru
    agent = SEOSpecialistAshigaru()
    return agent.execute_seo_optimization(params)


def cmd_seo_optimize(params: dict) -> dict:
    """SEO足軽: コンテンツ構造最適化"""
    from seo_agent import SEOSpecialistAshigaru
    agent = SEOSpecialistAshigaru()
    content = params.get("content", "")
    keyword_data = params.get("keyword_data", {})
    return agent.optimize_content_structure(content, keyword_data)


def cmd_writing(params: dict) -> dict:
    """ライティング足軽: 成田悠輔風記事生成"""
    from narita_writing_agent import NaritaWritingAshigaru
    agent = NaritaWritingAshigaru()
    return agent.generate_narita_style_article(params)


def cmd_social(params: dict) -> dict:
    """SNS足軽: 拡散戦略"""
    from social_media_agent import SocialMediaAshigaru
    agent = SocialMediaAshigaru()
    return agent.execute_social_strategy(params)


def cmd_analytics(params: dict) -> dict:
    """分析足軽: MAU分析レポート"""
    from analytics_agent import AnalyticsAshigaru
    agent = AnalyticsAshigaru()
    return agent.generate_mau_report(
        include_recommendations=params.get("include_recommendations", True)
    )


def cmd_image(params: dict) -> dict:
    """画像生成足軽: Gemini 3 画像生成"""
    from gemini3_image_generator import Gemini3ImageGenerator
    gen = Gemini3ImageGenerator()
    return gen.generate_article_images_parallel(params)


def cmd_wordpress(params: dict) -> dict:
    """WordPress投稿足軽: 記事投稿"""
    from wordpress_publisher import ArticlePublishingWorkflow
    workflow = ArticlePublishingWorkflow()
    article_dir = params.get("article_dir", "")
    mode = params.get("mode", "draft")
    return workflow.process_article_directory(article_dir, publish_mode=mode)


COMMANDS = {
    "research": cmd_research,
    "seo": cmd_seo,
    "seo_optimize": cmd_seo_optimize,
    "writing": cmd_writing,
    "social": cmd_social,
    "analytics": cmd_analytics,
    "image": cmd_image,
    "wordpress": cmd_wordpress,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(json.dumps({
            "error": "Usage: python3 run_ashigaru.py <command> [--json '{...}']",
            "available_commands": list(COMMANDS.keys()),
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    command = sys.argv[1]

    if command not in COMMANDS:
        print(json.dumps({
            "error": f"Unknown command: {command}",
            "available_commands": list(COMMANDS.keys()),
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    # --json 引数のパース
    params = {}
    if "--json" in sys.argv:
        json_idx = sys.argv.index("--json")
        if json_idx + 1 < len(sys.argv):
            try:
                params = json.loads(sys.argv[json_idx + 1])
            except json.JSONDecodeError as e:
                print(json.dumps({
                    "error": f"Invalid JSON: {e}",
                }, ensure_ascii=False))
                sys.exit(1)

    _add_paths()

    try:
        result = COMMANDS[command](params)
        # 結果をJSON出力（stderr にログが出るのでstdoutはJSONのみ）
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "traceback": traceback.format_exc(),
            "command": command,
        }, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
