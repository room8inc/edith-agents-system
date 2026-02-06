#!/usr/bin/env python3
"""
リサーチ部門ツールラッパー
Task Toolエージェントが Bash python3 run_research_tools.py <command> で呼び出す。
結果はstdoutにJSON出力される。

Usage:
  python3 run_research_tools.py search_console
  python3 run_research_tools.py existing_articles
  python3 run_research_tools.py known_keywords
"""

import sys
import json
import traceback
from pathlib import Path
from datetime import datetime

_THIS_DIR = Path(__file__).resolve().parent
_BLOG_DIR = _THIS_DIR.parent / "blog_department" if (_THIS_DIR.parent / "blog_department").exists() else _THIS_DIR.parent / "edith_corp" / "blog_department"

# blog_departmentの正確なパスを解決
if not _BLOG_DIR.exists():
    # フォールバック: edith_corp同階層
    _BLOG_DIR = _THIS_DIR.parent / "blog_department"

sys.path.insert(0, str(_THIS_DIR.parent))
from output_paths import BLOG_ARTICLES_DIR, BLOG_ARTICLES_INDEX


def cmd_search_console() -> dict:
    """Search Console APIからキーワードデータを取得"""
    search_console_dir = _BLOG_DIR / "search_console"
    sys.path.insert(0, str(search_console_dir))

    try:
        from search_console_api import SearchConsoleIntegration
        from config import SEARCH_CONSOLE_CONFIG

        integration = SearchConsoleIntegration()
        success = integration.setup(
            site_url=SEARCH_CONSOLE_CONFIG["site_url"],
            credentials_path=SEARCH_CONSOLE_CONFIG.get("credentials_path"),
        )

        if not success:
            return {
                "status": "error",
                "error": "Search Console API認証失敗",
                "data": {},
            }

        insights = integration.api.get_keyword_insights()

        return {
            "status": "success",
            "data": {
                "top_keywords": insights.get("top_performing_keywords", []),
                "opportunities": insights.get("improvement_opportunities", []),
                "content_gaps": insights.get("content_gaps", []),
                "performance_summary": insights.get("performance_summary", {}),
            },
            "retrieved_at": datetime.now().isoformat(),
        }

    except ImportError as e:
        return {
            "status": "error",
            "error": f"Search Console モジュール読み込み失敗: {e}",
            "data": {},
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "data": {},
        }


def cmd_existing_articles() -> dict:
    """既存記事一覧を取得（articles_index.json優先、なければディレクトリスキャン）"""

    # articles_index.json があればそこから読む（過去記事含む全記事）
    if BLOG_ARTICLES_INDEX.exists():
        try:
            data = json.loads(BLOG_ARTICLES_INDEX.read_text(encoding="utf-8"))
            all_articles = data.get("articles", [])
            return {
                "status": "success",
                "articles": [
                    {
                        "title": a.get("title", ""),
                        "slug": a.get("slug", ""),
                        "url": a.get("url", ""),
                        "published_date": a.get("published_date", ""),
                        "source": a.get("source", "wordpress"),
                        "excerpt": a.get("excerpt", ""),
                    }
                    for a in all_articles
                ],
                "count": len(all_articles),
                "index_updated_at": data.get("updated_at", ""),
                "retrieved_at": datetime.now().isoformat(),
            }
        except (json.JSONDecodeError, OSError):
            pass

    # フォールバック: ディレクトリスキャン（EDITH生成記事のみ）
    articles_dir = BLOG_ARTICLES_DIR
    articles = []

    if not articles_dir.exists():
        return {
            "status": "success",
            "articles": [],
            "count": 0,
            "note": f"articles ディレクトリが見つかりません: {articles_dir}",
        }

    for meta_file in sorted(articles_dir.glob("*/meta.json")):
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            dir_name = meta_file.parent.name
            date_str = dir_name[:8] if len(dir_name) >= 8 else ""

            articles.append({
                "title": meta.get("title", ""),
                "slug": meta.get("slug", ""),
                "published_date": date_str,
                "source": "edith",
            })
        except (json.JSONDecodeError, Exception) as e:
            articles.append({
                "directory": meta_file.parent.name,
                "error": str(e),
            })

    return {
        "status": "success",
        "articles": articles,
        "count": len(articles),
        "retrieved_at": datetime.now().isoformat(),
    }


def cmd_known_keywords() -> dict:
    """memory_systemから既知の成功キーワードデータを取得"""
    discoveries_path = (
        _BLOG_DIR / "memory_system" / "knowledge_base" / "keywords" / "discoveries.json"
    )

    if not discoveries_path.exists():
        return {
            "status": "success",
            "keywords": [],
            "count": 0,
            "note": f"discoveries.json が見つかりません: {discoveries_path}",
        }

    try:
        raw = json.loads(discoveries_path.read_text(encoding="utf-8"))

        keywords = []
        for keyword, data in raw.items():
            keywords.append({
                "keyword": keyword,
                "ctr": data.get("performance", {}).get("ctr", 0),
                "clicks": data.get("performance", {}).get("clicks", 0),
                "discovered_at": data.get("discovered_at", ""),
                "context": data.get("context", ""),
            })

        return {
            "status": "success",
            "keywords": keywords,
            "count": len(keywords),
            "retrieved_at": datetime.now().isoformat(),
        }

    except (json.JSONDecodeError, Exception) as e:
        return {
            "status": "error",
            "error": str(e),
            "keywords": [],
        }


COMMANDS = {
    "search_console": cmd_search_console,
    "existing_articles": cmd_existing_articles,
    "known_keywords": cmd_known_keywords,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(json.dumps({
            "error": "Usage: python3 run_research_tools.py <command>",
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

    try:
        result = COMMANDS[command]()
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
