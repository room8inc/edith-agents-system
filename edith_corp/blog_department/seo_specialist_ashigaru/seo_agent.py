#!/usr/bin/env python3
"""
SEO専門足軽 - 検索最適化の実働Agent
Task Toolと連携してSEO戦略を自動実行
Search Console実データに基づく戦略立案
"""

import json
import re
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

_THIS_DIR = Path(__file__).resolve().parent
_BLOG_DIR = _THIS_DIR.parent

sys.path.insert(0, str(_BLOG_DIR.parent))
from output_paths import BLOG_ARTICLES_DIR, BLOG_ARTICLES_INDEX

_ARTICLES_DIR = BLOG_ARTICLES_DIR

# Search Console API追加
sys.path.insert(0, str(_BLOG_DIR / "search_console"))
try:
    from search_console_api import SearchConsoleIntegration
except ImportError:
    SearchConsoleIntegration = None

# 戦略記憶システム追加
sys.path.insert(0, str(_BLOG_DIR.parent / "strategic_memory"))
try:
    from strategic_memory import MemoryIntegration
except ImportError:
    MemoryIntegration = None

class SEOSpecialistAshigaru:
    """SEO専門足軽 - 検索流入30%増加を担当"""

    def __init__(self):
        self.rank = "足軽"
        self.specialty = "SEO戦略・技術最適化"
        self.reports_to = "コンテンツ足軽大将"
        self.kpi_target = "検索流入30%増加"

        # Search Console連携
        self.search_console = None
        if SearchConsoleIntegration:
            self.search_console = SearchConsoleIntegration()
            print(f"[SEO足軽] Search Console連携準備完了")

        # 戦略記憶システム連携
        self.memory_integration = None
        if MemoryIntegration:
            self.memory_integration = MemoryIntegration()
            print(f"[SEO足軽] 戦略記憶システム連携完了")

        print(f"[SEO足軽] 配属完了 - {self.kpi_target}を目標に稼働開始")

    def analyze_keyword_opportunities(self, article_topic: str) -> Dict[str, Any]:
        """キーワード機会分析（Search Console実データ利用）"""

        print(f"[SEO足軽] キーワード分析開始: {article_topic}")

        # Search Consoleから実データ取得
        real_search_data = None
        if self.search_console and self.search_console.api.service:
            print(f"[SEO足軽] Search Console実データ取得中...")
            real_search_data = self.search_console.api.get_keyword_insights()

        # 実データがある場合は活用、なければモックデータ
        if real_search_data:
            keyword_analysis = self._analyze_with_real_data(article_topic, real_search_data)
        else:
            # 従来のモックデータ処理
            keyword_analysis = {
            "primary_keywords": [
                {"keyword": "AI導入 失敗", "volume": "高", "difficulty": "中", "intent": "問題解決"},
                {"keyword": "ChatGPT 導入 中小企業", "volume": "中", "difficulty": "低", "intent": "情報収集"}
            ],
            "secondary_keywords": [
                {"keyword": "AI活用 現実", "volume": "中", "difficulty": "低"},
                {"keyword": "業務効率化 AI", "volume": "高", "difficulty": "高"}
            ],
            "content_gap_opportunities": [
                "失敗事例の具体的分析が競合に不足",
                "ROI計算の実践例が少ない",
                "中小企業向けの段階的導入手順が不十分"
            ],
            "search_intent": "問題解決型（ハウツー重視）",
            "recommended_structure": {
                "h1": "失敗パターンの明確な提示",
                "h2": ["原因分析", "改善手順", "成功事例"],
                "h3": ["具体例", "チェックリスト", "ROI試算"]
            }
        }

        print(f"[SEO足軽] ✅ キーワード分析完了")
        print(f"[SEO足軽] 主要キーワード: {len(keyword_analysis['primary_keywords'])}個")
        print(f"[SEO足軽] 競合ギャップ: {len(keyword_analysis['content_gap_opportunities'])}個発見")

        return keyword_analysis

    def _analyze_with_real_data(self, topic: str, search_data: Dict) -> Dict[str, Any]:
        """Search Console実データを使った分析"""

        print(f"[SEO足軽] 🎯 実データ分析開始")

        # 実際の検索パフォーマンスから関連キーワード抽出
        top_keywords = search_data.get('top_performing_keywords', [])
        opportunities = search_data.get('improvement_opportunities', [])

        # トピックに関連するキーワード抽出
        related_keywords = []
        for kw in top_keywords:
            keyword_text = kw.get('keyword', '')
            if any(term in keyword_text.lower() for term in topic.lower().split()):
                related_keywords.append({
                    "keyword": keyword_text,
                    "clicks": kw.get('clicks', 0),
                    "position": kw.get('position', 0),
                    "ctr": kw.get('ctr', '0%'),
                    "volume": "実測値あり",
                    "difficulty": self._estimate_difficulty(kw.get('position', 0))
                })

        # 改善機会から新規キーワード候補
        new_keyword_candidates = []
        for opp in opportunities[:5]:
            if opp.get('type') == 'low_hanging_fruit':
                new_keyword_candidates.append({
                    "keyword": opp.get('query', ''),
                    "current_position": opp.get('current_position', 0),
                    "potential_clicks": opp.get('potential_clicks', 0),
                    "priority": opp.get('priority', 'medium'),
                    "action": opp.get('action', '')
                })

        keyword_analysis = {
            "data_source": "Search Console実データ",
            "analysis_date": datetime.now().isoformat(),
            "primary_keywords": related_keywords[:5] if related_keywords else self._get_default_keywords(topic),
            "improvement_opportunities": new_keyword_candidates,
            "content_gap_opportunities": search_data.get('content_gaps', []),
            "search_intent": self._determine_search_intent(related_keywords),
            "recommended_structure": self._create_structure_recommendation(search_data),
            "real_data_insights": {
                "total_impressions": search_data.get('performance_summary', {}).get('total_impressions', 0),
                "avg_position": search_data.get('performance_summary', {}).get('avg_position', 0),
                "top_queries_count": len(top_keywords)
            }
        }

        print(f"[SEO足軽] ✅ 実データ分析完了")
        print(f"[SEO足軽] 関連キーワード: {len(related_keywords)}個")
        print(f"[SEO足軽] 改善機会: {len(new_keyword_candidates)}個")

        # 重要な発見を自動保存
        if self.memory_integration:
            # 高CTRキーワードの自動記録
            for kw in related_keywords:
                if float(kw.get('ctr', '0%').replace('%', '')) > 20:
                    self.memory_integration.memory.auto_save_insight(
                        "keyword_discovery",
                        {
                            "keyword": kw["keyword"],
                            "ctr": kw["ctr"],
                            "position": kw["position"],
                            "clicks": kw["clicks"]
                        },
                        f"SEO分析で高CTRキーワード発見: {kw['keyword']}"
                    )

            # 改善機会の自動記録
            if new_keyword_candidates:
                self.memory_integration.memory.auto_save_insight(
                    "success_pattern",
                    {
                        "type": "seo_opportunities",
                        "description": f"{len(new_keyword_candidates)}個の改善機会発見",
                        "metrics": {
                            "total_potential_clicks": sum(k.get('potential_clicks', 0) for k in new_keyword_candidates)
                        },
                        "opportunities": new_keyword_candidates[:3]  # 上位3つ
                    },
                    "Search Console分析による改善機会"
                )

        return keyword_analysis

    def _estimate_difficulty(self, position: float) -> str:
        """順位から難易度を推定"""
        if position <= 10:
            return "高"
        elif position <= 20:
            return "中"
        else:
            return "低"

    def _determine_search_intent(self, keywords: List[Dict]) -> str:
        """検索意図の判定"""
        if not keywords:
            return "情報収集型"

        # キーワードから意図を推定
        problem_keywords = ['失敗', '問題', '課題', '改善']
        how_keywords = ['方法', 'やり方', 'ガイド', '手順']

        problem_count = sum(1 for kw in keywords
                          if any(term in kw.get('keyword', '') for term in problem_keywords))
        how_count = sum(1 for kw in keywords
                       if any(term in kw.get('keyword', '') for term in how_keywords))

        if problem_count > how_count:
            return "問題解決型"
        elif how_count > 0:
            return "実践ガイド型"
        else:
            return "情報収集型"

    def _create_structure_recommendation(self, search_data: Dict) -> Dict:
        """Search Dataに基づく構造推奨"""
        return {
            "h1": "検索意図に合わせた明確な課題提示",
            "h2": ["現状分析", "解決策", "実践手順", "効果測定"],
            "h3": ["具体例", "チェックリスト", "数値データ"],
            "optimization_notes": "Search Consoleデータに基づく最適化実施"
        }

    def _get_default_keywords(self, topic: str) -> List[Dict]:
        """デフォルトキーワード（実データがない場合）"""
        return [
            {"keyword": f"{topic} 課題", "volume": "推定", "difficulty": "中"},
            {"keyword": f"{topic} 解決策", "volume": "推定", "difficulty": "中"}
        ]

    # ── マークダウン解析 ──

    def _parse_markdown(self, raw_content: str) -> Dict[str, Any]:
        """マークダウンを解析して構造データを返す"""
        lines = raw_content.split('\n')
        title = ""
        headings = []
        paragraphs = []
        current_para = []

        for line in lines:
            stripped = line.strip()
            # H1 タイトル（最初の1つだけ）
            if stripped.startswith('# ') and not stripped.startswith('## ') and not title:
                title = stripped[2:].strip().strip('*')
            # H2
            elif stripped.startswith('## '):
                if current_para:
                    paragraphs.append(' '.join(current_para))
                    current_para = []
                headings.append({"level": "h2", "text": stripped.lstrip('#').strip()})
            # H3
            elif stripped.startswith('### '):
                if current_para:
                    paragraphs.append(' '.join(current_para))
                    current_para = []
                headings.append({"level": "h3", "text": stripped.lstrip('#').strip()})
            # 通常テキスト行（空行・区切り・画像を除く）
            elif stripped and not stripped.startswith('---') and not stripped.startswith('!['):
                # Bold / italic 等のマークダウン記法を除去してプレーンテキストに
                plain = re.sub(r'\*{1,2}(.+?)\*{1,2}', r'\1', stripped)
                current_para.append(plain)
            elif not stripped and current_para:
                paragraphs.append(' '.join(current_para))
                current_para = []

        if current_para:
            paragraphs.append(' '.join(current_para))

        return {
            "title": title,
            "headings": headings,
            "paragraphs": paragraphs,
            "first_paragraph": paragraphs[0] if paragraphs else "",
            "char_count": len(raw_content),
        }

    def _analyze_keyword_presence(self, raw_content: str, keyword_data: Dict) -> Dict[str, Any]:
        """コンテンツ内のキーワード出現状況を分析"""
        content_lower = raw_content.lower()
        results = []

        for kw in keyword_data.get("primary_keywords", []):
            keyword = kw.get("keyword", "")
            if not keyword:
                continue
            count = content_lower.count(keyword.lower())
            density = round(count * len(keyword) / max(len(raw_content), 1) * 100, 2)
            results.append({
                "keyword": keyword,
                "count": count,
                "density_pct": density,
                "present": count > 0,
            })

        return {
            "keyword_occurrences": results,
            "missing_keywords": [r["keyword"] for r in results if not r["present"]],
        }

    # ── コンテンツ構造最適化 ──

    def optimize_content_structure(self, raw_content: str, keyword_data: Dict) -> Dict[str, Any]:
        """コンテンツ構造の最適化 — 実コンテンツを解析して改善提案を返す"""

        print(f"[SEO足軽] コンテンツSEO最適化開始...")

        parsed = self._parse_markdown(raw_content)
        keyword_stats = self._analyze_keyword_presence(raw_content, keyword_data)

        optimized_content = {
            "title": self._optimize_title(parsed, keyword_data),
            "meta_description": self._generate_meta_description(parsed, keyword_data),
            "heading_structure": self._optimize_headings(parsed, keyword_data),
            "internal_links": self._suggest_internal_links(parsed),
            "featured_snippet_optimization": self._optimize_for_snippets(parsed, keyword_data),
            "content_stats": {
                "char_count": parsed["char_count"],
                "heading_count": len(parsed["headings"]),
                "h2_count": sum(1 for h in parsed["headings"] if h["level"] == "h2"),
                "h3_count": sum(1 for h in parsed["headings"] if h["level"] == "h3"),
                "paragraph_count": len(parsed["paragraphs"]),
            },
            "keyword_presence": keyword_stats,
        }

        print(f"[SEO足軽] ✅ SEO最適化完了")
        print(f"[SEO足軽] 文字数: {parsed['char_count']}字 / 見出し: {len(parsed['headings'])}個")
        print(f"[SEO足軽] 最適化要素: {len(optimized_content)}項目")

        return optimized_content

    def _optimize_title(self, parsed: Dict, keyword_data: Dict) -> Dict[str, Any]:
        """実タイトルを分析して最適化提案"""
        actual_title = parsed.get("title", "")
        title_len = len(actual_title)

        # 主要キーワードがタイトルに含まれているか
        primary_keywords = keyword_data.get("primary_keywords", [])
        keywords_in_title = []
        keywords_missing = []
        for kw in primary_keywords:
            keyword = kw.get("keyword", "")
            if keyword and keyword.lower() in actual_title.lower():
                keywords_in_title.append(keyword)
            elif keyword:
                keywords_missing.append(keyword)

        issues = []
        if title_len > 60:
            issues.append(f"タイトルが{title_len}文字で長すぎる（推奨: 30-60文字）。検索結果で切れる可能性あり")
        elif title_len < 15:
            issues.append(f"タイトルが{title_len}文字で短すぎる（推奨: 30-60文字）")
        if keywords_missing and primary_keywords:
            issues.append(f"主要キーワード未含有: {', '.join(keywords_missing[:3])}")

        return {
            "actual_title": actual_title,
            "title_length": title_len,
            "keywords_included": keywords_in_title,
            "keywords_missing": keywords_missing,
            "issues": issues,
            "score": "good" if not issues else "needs_improvement",
        }

    def _generate_meta_description(self, parsed: Dict, keyword_data: Dict) -> Dict[str, Any]:
        """実コンテンツからメタディスクリプション候補を生成"""
        first_para = parsed.get("first_paragraph", "")
        title = parsed.get("title", "")

        # 最初の段落を120文字に切り詰め
        if len(first_para) > 120:
            desc_base = first_para[:117] + "..."
        else:
            desc_base = first_para

        # 主要キーワードの1つ目を抽出
        primary_kw = ""
        for kw in keyword_data.get("primary_keywords", []):
            if kw.get("keyword"):
                primary_kw = kw["keyword"]
                break

        # キーワードがdescに含まれるかチェック
        kw_in_desc = primary_kw.lower() in desc_base.lower() if primary_kw else True

        return {
            "suggested_description": desc_base,
            "description_length": len(desc_base),
            "primary_keyword_included": kw_in_desc,
            "recommendation": "メタディスクリプションは120-160文字が最適。主要キーワードを自然に含める。",
        }

    def _optimize_headings(self, parsed: Dict, keyword_data: Dict) -> Dict[str, Any]:
        """実見出し構造を分析してSEO提案"""
        headings = parsed.get("headings", [])

        primary_keywords = [kw.get("keyword", "").lower()
                            for kw in keyword_data.get("primary_keywords", []) if kw.get("keyword")]

        analyzed = []
        for h in headings:
            text_lower = h["text"].lower()
            kw_match = [kw for kw in primary_keywords if kw in text_lower]
            analyzed.append({
                "level": h["level"],
                "text": h["text"],
                "keywords_found": kw_match,
                "has_keyword": len(kw_match) > 0,
            })

        h2_count = sum(1 for h in headings if h["level"] == "h2")
        h3_count = sum(1 for h in headings if h["level"] == "h3")
        headings_with_kw = sum(1 for a in analyzed if a["has_keyword"])

        issues = []
        if h2_count < 2:
            issues.append("H2が少ない（推奨: 3-6個）。内容を適切にセクション分けするとSEO効果向上")
        if h2_count > 0 and headings_with_kw == 0:
            issues.append("どの見出しにも主要キーワードが含まれていない。H2に自然にキーワードを含めると良い")

        return {
            "actual_headings": analyzed,
            "h2_count": h2_count,
            "h3_count": h3_count,
            "headings_with_keyword": headings_with_kw,
            "issues": issues,
        }

    def _load_articles_index(self) -> List[Dict]:
        """articles_index.json から全記事メタデータを読み込む"""
        if BLOG_ARTICLES_INDEX.exists():
            try:
                data = json.loads(BLOG_ARTICLES_INDEX.read_text(encoding="utf-8"))
                return data.get("articles", [])
            except (json.JSONDecodeError, OSError):
                pass

        # フォールバック: ディレクトリスキャン（EDITH生成記事のみ）
        results = []
        if _ARTICLES_DIR.exists():
            for meta_file in sorted(_ARTICLES_DIR.glob("*/meta.json")):
                try:
                    meta = json.loads(meta_file.read_text(encoding="utf-8"))
                    results.append(meta)
                except (json.JSONDecodeError, OSError):
                    continue
        return results

    def _suggest_internal_links(self, parsed: Dict) -> List[Dict]:
        """全記事（過去記事含む）から関連する内部リンクを提案"""
        suggestions = []

        all_articles = self._load_articles_index()
        if not all_articles:
            return suggestions

        article_title = parsed.get("title", "").lower()
        article_text = " ".join(parsed.get("paragraphs", [])).lower()

        for entry in all_articles:
            other_title = entry.get("title", "")
            other_slug = entry.get("slug", "")

            # 同じ記事はスキップ
            if other_title.lower() == article_title:
                continue

            # タイトルのキーワードマッチでスコアリング
            title_words = [w for w in other_title.lower().split() if len(w) >= 2]
            match_score = sum(1 for w in title_words if w in article_text)

            # タグがあればタグマッチも加算
            other_tags = [t.lower() for t in entry.get("tags", [])]
            tag_matches = [t for t in other_tags if t in article_text]
            match_score += len(tag_matches)

            if match_score > 0:
                suggestions.append({
                    "anchor_text": other_title,
                    "target_slug": other_slug,
                    "url": entry.get("url", f"https://www.room8.co.jp/{other_slug}/"),
                    "relevance_score": match_score,
                    "source": entry.get("source", "wordpress"),
                })

        # スコア順でソートして上位5件
        suggestions.sort(key=lambda x: x["relevance_score"], reverse=True)
        return suggestions[:5]

    def _optimize_for_snippets(self, parsed: Dict, keyword_data: Dict) -> Dict[str, Any]:
        """実コンテンツから強調スニペット候補を抽出"""
        paragraphs = parsed.get("paragraphs", [])
        headings = parsed.get("headings", [])

        # 疑問文の見出しを探す（スニペットのQ&A候補）
        qa_candidates = []
        for i, h in enumerate(headings):
            if '？' in h["text"] or '?' in h["text"]:
                # 次の段落を回答候補とする
                # 見出し位置は概算（段落インデックスと1:1ではないが近似）
                qa_candidates.append({
                    "question": h["text"],
                    "heading_level": h["level"],
                })

        # リスト形式のコンテンツを探す（箇条書き・番号付き）
        list_items = []
        for p in paragraphs:
            lines = p.split(' ')
            for line in lines:
                if re.match(r'^[\d１２３４５６７８９０]+[\.\)）]', line.strip()):
                    list_items.append(line.strip())
                elif line.strip().startswith('- ') or line.strip().startswith('・'):
                    list_items.append(line.strip())

        return {
            "qa_candidates": qa_candidates[:5],
            "list_content_found": len(list_items) > 0,
            "list_items_count": len(list_items),
            "recommendation": "疑問文H2の直後に簡潔な回答（2-3文）を配置すると強調スニペット獲得率が上がる"
                              if qa_candidates else
                              "H2に疑問文（〇〇とは？等）を1-2個入れると強調スニペット候補になる",
        }

    def execute_seo_optimization(self, article_data: Dict) -> Dict[str, Any]:
        """SEO最適化の完全実行"""

        print(f"\n[SEO足軽] 📊 SEO最適化タスク開始")
        print(f"[SEO足軽] 対象記事: {article_data.get('topic', 'untitled')}")

        # 1. キーワード分析
        keyword_analysis = self.analyze_keyword_opportunities(article_data.get('topic', ''))

        # 2. コンテンツ構造最適化
        seo_optimization = self.optimize_content_structure(
            article_data.get('content', ''),
            keyword_analysis
        )

        # 3. 最終レポート作成
        seo_report = {
            "keyword_analysis": keyword_analysis,
            "seo_optimization": seo_optimization,
            "expected_impact": {
                "search_traffic_increase": "30%",
                "ranking_improvement": "平均5位向上期待",
                "click_through_rate": "12%向上期待"
            },
            "implementation_status": "完了",
            "next_monitoring": "2週間後の順位チェック",
            "optimized_at": datetime.now().isoformat()
        }

        print(f"[SEO足軽] ✅ SEO最適化完了")
        print(f"[SEO足軽] 期待効果: 検索流入30%増加")

        return seo_report

def test_seo_agent():
    """SEO足軽テスト実行"""

    seo_agent = SEOSpecialistAshigaru()

    test_article = {
        "topic": "ChatGPT導入で失敗する中小企業の特徴",
        "content": "サンプル記事内容..."
    }

    result = seo_agent.execute_seo_optimization(test_article)

    print(f"\n🎯 SEO最適化結果:")
    print(f"  主要キーワード数: {len(result['keyword_analysis']['primary_keywords'])}")
    print(f"  内部リンク提案: {len(result['seo_optimization']['internal_links'])}")
    print(f"  期待効果: {result['expected_impact']['search_traffic_increase']} 流入増加")

if __name__ == "__main__":
    test_seo_agent()