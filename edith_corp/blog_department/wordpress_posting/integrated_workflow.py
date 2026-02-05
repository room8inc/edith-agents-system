#!/usr/bin/env python3
"""
統合ワークフロー - 記事生成から画像作成、WordPress投稿まで完全自動化
ライティング足軽 → 画像生成足軽 → WordPress投稿足軽の連携システム
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# 既存のクラスをインポート
import sys
sys.path.append('/Users/tsuruta/Documents/000AGENTS/edith_corp/blog_department')

from writing.narita_writing_agent import NaritaWritingAshigaru
from image_generation.image_generator import ImageGenerationAshigaru
from wordpress_posting.wordpress_publisher import ArticlePublishingWorkflow

class IntegratedContentWorkflow:
    """統合コンテンツワークフロー - 記事生成から投稿まで完全自動化"""

    def __init__(self):
        self.writer = NaritaWritingAshigaru()
        self.image_generator = ImageGenerationAshigaru()
        self.publisher = ArticlePublishingWorkflow()

        print(f"[統合ワークフロー] 🎯 完全自動化システム起動")
        print(f"[統合ワークフロー] ライティング → 画像生成 → WordPress投稿")

    def create_complete_article(self, article_brief: Dict[str, Any], publish_mode: str = "draft") -> Dict[str, Any]:
        """完全記事作成プロセス（生成→画像→投稿）"""

        print(f"\n[統合ワークフロー] 🚀 完全記事作成開始")
        print(f"[統合ワークフロー] テーマ: {article_brief.get('topic', '')}")

        # ステップ1: 記事生成
        print(f"\n[ステップ1] ✍️ 記事コンテンツ生成")
        article_result = self.writer.generate_narita_style_article(article_brief)

        if not article_result or not article_result.get("content"):
            return {
                "success": False,
                "error": "記事生成に失敗",
                "step_failed": "writing"
            }

        # ステップ2: 記事ディレクトリとメタデータ作成
        print(f"\n[ステップ2] 📁 記事ディレクトリ作成")
        article_data = self._prepare_article_data(article_brief, article_result)
        article_dir = self._create_article_structure(article_data)

        # ステップ3: 画像生成
        print(f"\n[ステップ3] 🎨 アイキャッチ・セクション画像生成")
        image_result = self.image_generator.process_complete_article(article_data)

        # ステップ4: WordPress投稿
        print(f"\n[ステップ4] 🚀 WordPress投稿")
        if publish_mode != "skip_publish":
            publish_result = self.publisher.process_article_directory(article_dir, publish_mode)
        else:
            publish_result = {"workflow_success": True, "message": "投稿スキップ"}

        # 結果統合
        workflow_result = {
            "workflow_success": True,
            "article_directory": article_dir,
            "article_data": {
                "title": article_data.get("title"),
                "word_count": len(article_result.get("content", "")),
                "sections_count": len(article_data.get("sections", []))
            },
            "image_generation": {
                "success": image_result.get("successful_images", 0) > 0,
                "images_created": image_result.get("successful_images", 0),
                "total_images": image_result.get("total_images", 0)
            },
            "wordpress_publishing": {
                "success": publish_result.get("workflow_success", False),
                "post_url": publish_result.get("wordpress_post", {}).get("url"),
                "post_id": publish_result.get("wordpress_post", {}).get("id")
            },
            "completed_at": datetime.now().isoformat()
        }

        # エラーハンドリング
        if not image_result.get("successful_images", 0):
            workflow_result["warnings"] = ["画像生成でエラーが発生しました"]

        if not publish_result.get("workflow_success", False) and publish_mode != "skip_publish":
            workflow_result["warnings"] = workflow_result.get("warnings", []) + ["WordPress投稿でエラーが発生しました"]

        print(f"\n[統合ワークフロー] ✅ 完全記事作成完了")
        print(f"[統合ワークフロー] 記事ディレクトリ: {article_dir}")
        print(f"[統合ワークフロー] 画像: {workflow_result['image_generation']['images_created']}枚")
        print(f"[統合ワークフロー] WordPress: {'✅' if workflow_result['wordpress_publishing']['success'] else '❌'}")

        return workflow_result

    def _prepare_article_data(self, brief: Dict[str, Any], article_result: Dict[str, Any]) -> Dict[str, Any]:
        """記事データの準備"""

        # 基本データ構築
        article_data = {
            "title": brief.get("title", brief.get("topic", "AI活用記事")),
            "slug": self._generate_slug(brief.get("topic", "")),
            "content": article_result.get("content", ""),
            "theme": "AI活用",
            "author": "鶴田（Room8）",
            "category": "AI活用",
            "tags": brief.get("tags", ["AI導入", "中小企業", "デジタル化"]),
            "created_at": datetime.now().isoformat()
        }

        # SEO情報
        article_data["seo"] = {
            "primary_keywords": brief.get("keywords", ["AI導入", "中小企業"]),
            "meta_description": self._generate_meta_description(article_data["content"]),
            "expected_traffic": brief.get("expected_traffic", 800)
        }

        # セクション情報抽出（画像生成用）
        sections = self._extract_sections_from_content(article_data["content"])
        article_data["sections"] = sections

        return article_data

    def _create_article_structure(self, article_data: Dict[str, Any]) -> str:
        """記事ディレクトリ構造の作成"""

        # ディレクトリ作成
        article_dir = self.image_generator.create_article_directory(
            article_data["slug"],
            datetime.now().strftime('%Y%m%d')
        )

        # article.md作成
        article_path = os.path.join(article_dir, "article.md")
        with open(article_path, "w", encoding="utf-8") as f:
            f.write(article_data["content"])

        # meta.json作成
        meta_data = {
            "title": article_data["title"],
            "slug": article_data["slug"],
            "author": article_data["author"],
            "created_at": article_data["created_at"],
            "category": article_data["category"],
            "tags": article_data["tags"],
            "seo": article_data["seo"],
            "images": {
                "featured": "images/featured.png",
                "sections": [
                    {"section": section["title"], "image": f"images/section{i+1}_{section['title'][:10]}.png"}
                    for i, section in enumerate(article_data.get("sections", []))
                ]
            },
            "wordpress": {
                "status": "draft",
                "post_id": None,
                "published_at": None,
                "url": None
            }
        }

        meta_path = os.path.join(article_dir, "meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=2)

        print(f"[統合ワークフロー] 📁 記事構造作成完了: {article_dir}")
        return article_dir

    def _generate_slug(self, topic: str) -> str:
        """記事スラッグ生成"""

        # 日本語をローマ字に変換（簡易版）
        keyword_map = {
            "AI導入": "ai-implementation",
            "失敗": "failure",
            "中小企業": "small-business",
            "Excel": "excel",
            "デジタル化": "digitalization",
            "効率化": "efficiency",
            "ChatGPT": "chatgpt",
            "自動化": "automation"
        }

        slug_parts = []
        for jp_word, en_word in keyword_map.items():
            if jp_word in topic:
                slug_parts.append(en_word)

        if not slug_parts:
            slug_parts = ["ai-business-article"]

        return "-".join(slug_parts)

    def _generate_meta_description(self, content: str) -> str:
        """メタディスクリプション生成"""

        # 記事の最初の段落から抽出
        lines = content.split('\n')
        description_lines = []

        for line in lines[1:6]:  # 最初の見出しの後の数行
            if line.strip() and not line.startswith('#') and not line.startswith('こんにちは'):
                clean_line = line.strip().replace('**', '').replace('*', '')
                description_lines.append(clean_line)

        description = ' '.join(description_lines)[:120]  # 120字以内

        # デフォルトフォールバック
        if len(description) < 30:
            description = "AI導入で失敗しないための実践的なガイド。中小企業の現実的な課題と解決策を成田悠輔風にお伝えします。"

        return description

    def _extract_sections_from_content(self, content: str) -> List[Dict[str, str]]:
        """記事コンテンツからセクション情報抽出"""

        sections = []
        lines = content.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            if line.startswith('## '):  # H2見出し
                # 前のセクションを保存
                if current_section:
                    sections.append({
                        "title": current_section,
                        "content": '\n'.join(current_content)
                    })

                # 新しいセクション開始
                current_section = line.replace('## ', '').strip()
                current_content = []

            elif current_section and line.strip():
                current_content.append(line)

        # 最後のセクション保存
        if current_section:
            sections.append({
                "title": current_section,
                "content": '\n'.join(current_content)
            })

        return sections


def test_integrated_workflow():
    """統合ワークフローのテスト"""

    print("🎯 統合ワークフローテスト")
    print("=" * 80)

    workflow = IntegratedContentWorkflow()

    # テスト記事ブリーフ
    test_brief = {
        "topic": "ChatGPT導入で失敗する中小企業の特徴と対策",
        "title": "『ChatGPT導入失敗』で痛い目に遭った中小企業の現実",
        "target_audience": "個人事業主・中小企業経営者",
        "keywords": ["ChatGPT導入", "中小企業", "失敗事例"],
        "tags": ["ChatGPT", "AI導入", "中小企業", "失敗対策"],
        "expected_traffic": 1000
    }

    print(f"[テスト] 記事ブリーフ: {test_brief['topic']}")

    # 完全ワークフロー実行
    result = workflow.create_complete_article(test_brief, publish_mode="draft")

    print(f"\n📊 統合ワークフロー結果:")
    print(f"  成功: {'✅' if result['workflow_success'] else '❌'}")
    print(f"  記事ディレクトリ: {result['article_directory']}")
    print(f"  文字数: {result['article_data']['word_count']:,}字")
    print(f"  セクション数: {result['article_data']['sections_count']}")
    print(f"  画像生成: {result['image_generation']['images_created']}/{result['image_generation']['total_images']}枚")
    print(f"  WordPress: {'✅' if result['wordpress_publishing']['success'] else '❌'}")

    if result.get('warnings'):
        print(f"  警告: {', '.join(result['warnings'])}")

    return result


if __name__ == "__main__":
    test_integrated_workflow()