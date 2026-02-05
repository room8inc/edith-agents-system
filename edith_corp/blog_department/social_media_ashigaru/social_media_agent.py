#!/usr/bin/env python3
"""
SNS管理足軽 - 拡散戦略の実働Agent
Task Toolと連携してSNS拡散を自動実行
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

class SocialMediaAshigaru:
    """SNS管理足軽 - ソーシャル拡散・エンゲージメント専門"""

    def __init__(self):
        self.rank = "足軽"
        self.specialty = "SNS拡散・エンゲージメント戦略"
        self.reports_to = "コンテンツ足軽大将"
        self.target_increase = "SNS経由流入40%増加"
        self.managed_platforms = [
            "X (Twitter)",
            "Facebook",
            "LinkedIn",
            "Instagram",
            "note"
        ]

        print(f"[SNS足軽] 配属完了 - {self.target_increase}を目標に稼働")

    def analyze_content_for_social(self, article_content: Dict[str, Any]) -> Dict[str, Any]:
        """記事のSNS適性分析"""

        print(f"[SNS足軽] 📊 SNS適性分析開始")
        print(f"[SNS足軽] 対象記事: {article_content.get('title', 'untitled')}")

        # 実際の実装では、Task Toolを使ってコンテンツ分析Agentを呼び出し
        # Task(subagent_type="general-purpose", prompt="SNS拡散分析実行...")

        content_analysis = {
            "shareability_score": self._calculate_shareability(article_content),
            "platform_fit": {
                "twitter": {
                    "score": 85,
                    "reason": "毒舌・辛辣な内容がバズりやすい",
                    "optimal_format": "連続ツイート＋画像"
                },
                "linkedin": {
                    "score": 90,
                    "reason": "ビジネス課題解決がターゲット層にマッチ",
                    "optimal_format": "要約＋実用的ポイント強調"
                },
                "facebook": {
                    "score": 75,
                    "reason": "中小企業経営者の情報収集需要あり",
                    "optimal_format": "事例紹介＋コメント促進"
                },
                "note": {
                    "score": 80,
                    "reason": "長文読解層がターゲット",
                    "optimal_format": "記事要約＋追加insight"
                }
            },
            "viral_elements": [
                "現実的な数値データ（ROI計算等）",
                "共感できる失敗体験",
                "具体的なチェックリスト",
                "毒舌だが建設的な指摘"
            ],
            "engagement_triggers": [
                "「あるある」体験の共有促進",
                "実体験コメントの収集",
                "改善成果の報告依頼",
                "反論・意見交換の歓迎"
            ]
        }

        print(f"[SNS足軽] ✅ 適性分析完了")
        print(f"[SNS足軽] 総合拡散スコア: {content_analysis['shareability_score']}/100")

        return content_analysis

    def generate_social_content(self, article_data: Dict, platform_strategy: Dict) -> Dict[str, Any]:
        """プラットフォーム別コンテンツ生成"""

        print(f"[SNS足軽] ✏️ SNS投稿コンテンツ生成開始")

        social_content = {}

        # Twitter投稿生成
        social_content["twitter"] = self._create_twitter_thread(article_data)

        # LinkedIn投稿生成
        social_content["linkedin"] = self._create_linkedin_post(article_data)

        # Facebook投稿生成
        social_content["facebook"] = self._create_facebook_post(article_data)

        # note投稿生成
        social_content["note"] = self._create_note_summary(article_data)

        print(f"[SNS足軽] ✅ 全プラットフォーム投稿生成完了")
        print(f"[SNS足軽] 生成プラットフォーム: {len(social_content)}個")

        return social_content

    def _calculate_shareability(self, content: Dict[str, Any]) -> int:
        """拡散可能性スコア計算"""

        score = 50  # ベーススコア

        title = content.get('title', '')
        article_content = content.get('content', '')

        # タイトルの拡散要素チェック
        viral_keywords = ['失敗', '現実', '辛辣', '大コケ', '本音', '暴露']
        for keyword in viral_keywords:
            if keyword in title:
                score += 8

        # 数値データの存在
        if any(char in article_content for char in ['%', '倍', '万円', '時間']):
            score += 10

        # 具体例・チェックリストの存在
        if 'チェック' in article_content or '手順' in article_content:
            score += 8

        # 感情的フック
        emotional_words = ['クスっと', 'あるある', '現実逃避', '本末転倒']
        for word in emotional_words:
            if word in article_content:
                score += 5

        return min(score, 100)

    def _create_twitter_thread(self, article_data: Dict) -> Dict[str, Any]:
        """Twitter連続ツイート生成"""

        title = article_data.get('title', '')

        thread = {
            "tweet1": {
                "content": f"【{title}】\n\n最近よく聞く相談👇\n\n「ChatGPT導入したいんですが...」\n\n話を聞くと...\n📠 まだFAXで発注書\n✋ Excelが手入力\n⏰ メール返信が3日遅れ\n\nちょっと待って😅\n\n1/5 🧵",
                "media": "infographic_suggestion",
                "hashtags": ["#AI導入", "#中小企業", "#デジタル化"]
            },
            "tweet2": {
                "content": "【なぜこうなる？】\n\nAI導入前にやるべき地味な改善：\n✅ FAX廃止 → 月2万円削減\n✅ クラウド移行 → 効率30%向上\n✅ ペーパーレス → 検索時間90%短縮\n\nこれだけで月20-30万円の効果が...\n\n2/5",
                "media": "comparison_chart",
                "hashtags": ["#業務効率化", "#コスト削減"]
            },
            "tweet3": {
                "content": "【ROI比較が衝撃】📊\n\n| 改善項目 | 初期コスト | 回収期間 |\n|---------|------------|----------|\n| FAX→クラウド | 5万円 | 2.5ヶ月 |\n| 手入力→自動化 | 15万円 | 1.9ヶ月 |\n| AI導入 | 100万円 | 6.7ヶ月 |\n\n基礎デジタル化の方が圧倒的に効率良い...\n\n3/5",
                "media": "roi_table",
                "hashtags": ["#ROI", "#投資効果"]
            },
            "tweet4": {
                "content": "【今すぐできること】💪\n\nWeek1: FAX機の電源を切る（物理的に）\nWeek2: 手入力作業を全部記録\nWeek3: 自動化ツール選定\nWeek4: 効果測定開始\n\n地味だけど確実に効果出ます📈\n\n4/5",
                "media": "checklist_image",
                "hashtags": ["#実践ガイド", "#業務改善"]
            },
            "tweet5": {
                "content": "【結論】\n\n地味な改善の積み重ね = 最強の競争力\n\nAI導入はその後で十分。\n順番を間違えなければ年300万円の効果も現実的🎯\n\n詳細は記事で👇\n[記事URL]\n\n皆さんの改善体験もぜひシェアしてください！\n\n5/5 fin",
                "media": "summary_card",
                "hashtags": ["#成果報告", "#体験談募集"]
            }
        }

        return {
            "platform": "twitter",
            "format": "thread",
            "thread_data": thread,
            "posting_schedule": self._calculate_optimal_posting_time("twitter"),
            "engagement_strategy": "体験談シェア促進・リツイート狙い"
        }

    def _create_linkedin_post(self, article_data: Dict) -> Dict[str, Any]:
        """LinkedIn投稿生成"""

        title = article_data.get('title', '')

        post_content = f"""💼 {title}

最近、「AI導入で業務効率化」の相談が急増していますが、話を聞くと基礎的なデジタル化が未完了のケースが大半です。

📊 実際のデータで比較すると：

▶️ FAX廃止→クラウド移行：月2万円削減（投資回収2.5ヶ月）
▶️ 手入力→自動化：月8万円削減（投資回収1.9ヶ月）
▶️ AI導入：月15万円削減（投資回収6.7ヶ月）

基礎デジタル化の方が明らかにROIが高いのが現実です。

✅ 順序を正しく進めれば：
1. 3ヶ月で月25万円のコスト削減
2. 6ヶ月でさらなる効率化
3. 12ヶ月でAI導入による本格的競争優位

結果として年300万円の効果と業務効率50%向上が実現可能です。

「地味だけど確実」な改善の積み重ねが、最も効果的な競争力になります。

皆さんの会社ではどのような業務改善を実践されていますか？
ぜひ経験をお聞かせください。

詳細記事：[記事URL]

#業務効率化 #デジタル化 #AI導入 #中小企業経営 #ROI"""

        return {
            "platform": "linkedin",
            "format": "single_post",
            "content": post_content,
            "posting_schedule": self._calculate_optimal_posting_time("linkedin"),
            "engagement_strategy": "経験談の質問・業界別事例収集"
        }

    def _create_facebook_post(self, article_data: Dict) -> Dict[str, Any]:
        """Facebook投稿生成"""

        title = article_data.get('title', '')

        post_content = f"""🔥 {title}

中小企業経営者の皆さん、こんな経験ありませんか？

「うちもAI導入を検討中...」と言いながら
📠 まだFAXで注文受付
✋ Excel在庫管理が手入力
📧 メール返信に3日かかる

実は、AI導入前にできる「地味な改善」だけで、月20〜30万円のコスト削減が可能なんです。

【驚きのROI比較】
• FAX廃止：2.5ヶ月で投資回収
• 手入力撲滅：1.9ヶ月で投資回収
• AI導入：6.7ヶ月で投資回収

基礎固めの方が圧倒的に効率的ですよね😅

記事では、今日からできる具体的な改善手順を成田悠輔風に辛辣解説しています。

読んでクスっと笑えて、でも実用的。そんな内容を目指しました。

皆さんの「業務改善あるある」もコメントで教えてください！
きっと他の経営者の方の参考になります✨

記事はこちら→ [記事URL]

#中小企業 #業務効率化 #AI導入 #デジタル化 #経営改善"""

        return {
            "platform": "facebook",
            "format": "single_post",
            "content": post_content,
            "posting_schedule": self._calculate_optimal_posting_time("facebook"),
            "engagement_strategy": "あるある体験談・コメント促進"
        }

    def _create_note_summary(self, article_data: Dict) -> Dict[str, Any]:
        """note要約投稿生成"""

        title = article_data.get('title', '')

        note_content = f"""# {title}

## 📋 記事の要約

最近増えている中小企業のAI導入相談。でも話を聞くと、基礎的なデジタル化が全然できてない現実が...

### 🔍 よくある勘違いパターン
- 「ChatGPT導入したい」（FAXはまだ現役）
- 「AI活用で売上アップ」（Excel管理は手入力）
- 「最新技術で競争力を」（メール返信3日遅れ）

### 📊 データで見る現実
基礎デジタル化の方がAI導入よりもROIが圧倒的に高い事実を数値で解説。

| 項目 | 投資回収期間 | 月間効果 |
|------|-------------|----------|
| FAX廃止 | 2.5ヶ月 | 2万円削減 |
| 自動化 | 1.9ヶ月 | 8万円削減 |
| AI導入 | 6.7ヶ月 | 15万円削減 |

### ✅ 正しい改善順序
1. **基礎デジタル化**（3ヶ月）→ 月25万円削減
2. **システム統合**（6ヶ月）→ さらなる効率化
3. **AI導入**（12ヶ月）→ 本格的競争優位

### 💡 今日からできること
- Week1: FAX機の電源を切る（物理的に）
- Week2-3: 手入力業務の洗い出し・時間測定
- Week4: 効果測定システム構築

### 🎯 実際の効果
この手順で進めた企業の平均結果：
- 業務時間短縮：35%
- コスト削減：月25万円
- エラー率減少：70%
- 従業員満足度：40%向上

## 💭 追加insight

記事では辛辣に書きましたが、実際に多くの企業が陥りがちなパターンです。

大切なのは「順序」。地味でも確実な改善を積み重ねることで、AI導入時には既に強固な基盤ができています。

皆さんの会社の「デジタル化あるある」もぜひ教えてください。きっと同じ悩みを持つ経営者の方がいるはずです。

---
📖 詳細記事はこちら：[記事URL]

#中小企業経営 #業務効率化 #デジタル化 #AI導入 #経営改善"""

        return {
            "platform": "note",
            "format": "summary_article",
            "content": note_content,
            "posting_schedule": self._calculate_optimal_posting_time("note"),
            "engagement_strategy": "関連記事リンク・読者の体験談収集"
        }

    def _calculate_optimal_posting_time(self, platform: str) -> Dict[str, Any]:
        """プラットフォーム別最適投稿時間算出"""

        base_datetime = datetime.now()

        # プラットフォーム別最適時間
        optimal_times = {
            "twitter": {"hour": 12, "weekday": True},  # 平日昼休み
            "linkedin": {"hour": 9, "weekday": True},   # 平日朝
            "facebook": {"hour": 20, "weekday": False}, # 週末夜
            "note": {"hour": 22, "weekday": True}      # 平日夜
        }

        platform_setting = optimal_times.get(platform, {"hour": 12, "weekday": True})

        # 最適な投稿日時を計算
        target_hour = platform_setting["hour"]
        weekday_required = platform_setting["weekday"]

        optimal_date = base_datetime
        if weekday_required and optimal_date.weekday() >= 5:  # 土日の場合
            days_to_monday = 7 - optimal_date.weekday()
            optimal_date += timedelta(days=days_to_monday)

        optimal_datetime = optimal_date.replace(
            hour=target_hour, minute=0, second=0, microsecond=0
        )

        return {
            "optimal_datetime": optimal_datetime.isoformat(),
            "platform": platform,
            "reasoning": f"ターゲット層のアクティブ時間帯（{target_hour}時）",
            "engagement_expectation": "高"
        }

    def execute_social_strategy(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """SNS戦略の完全実行"""

        print(f"\n[SNS足軽] 🚀 SNS拡散戦略実行開始")
        print(f"[SNS足軽] 対象記事: {article_data.get('title', 'untitled')}")

        # 1. SNS適性分析
        content_analysis = self.analyze_content_for_social(article_data)

        # 2. プラットフォーム別コンテンツ生成
        social_content = self.generate_social_content(article_data, content_analysis["platform_fit"])

        # 3. 投稿スケジュール作成
        posting_schedule = self._create_posting_schedule(social_content)

        # 4. エンゲージメント戦略
        engagement_plan = self._create_engagement_plan(content_analysis)

        # 5. 最終戦略レポート
        social_strategy_report = {
            "content_analysis": content_analysis,
            "social_content": social_content,
            "posting_schedule": posting_schedule,
            "engagement_plan": engagement_plan,
            "expected_results": {
                "reach_increase": "SNS総フォロワーの15%",
                "traffic_increase": "40%（目標値）",
                "engagement_rate": "平均3.5%期待",
                "viral_potential": "中〜高（数値データと毒舌要素による）"
            },
            "monitoring_plan": [
                "投稿後24時間のエンゲージメント測定",
                "週次の流入分析",
                "月次のフォロワー増減チェック"
            ],
            "executed_at": datetime.now().isoformat()
        }

        print(f"[SNS足軽] ✅ SNS戦略実行完了")
        print(f"[SNS足軽] 投稿予定プラットフォーム: {len(social_content)}個")
        print(f"[SNS足軽] 期待効果: SNS流入40%増加")

        return social_strategy_report

    def _create_posting_schedule(self, social_content: Dict) -> List[Dict]:
        """投稿スケジュール作成"""

        schedule = []
        base_time = datetime.now()

        # プラットフォーム別のタイムラグ
        timing_offset = {
            "twitter": timedelta(hours=1),
            "linkedin": timedelta(hours=3),
            "facebook": timedelta(hours=6),
            "note": timedelta(hours=12)
        }

        for platform, content_data in social_content.items():
            posting_time = base_time + timing_offset.get(platform, timedelta(hours=1))

            schedule.append({
                "platform": platform,
                "posting_time": posting_time.isoformat(),
                "content_type": content_data.get("format", "single_post"),
                "priority": self._get_platform_priority(platform)
            })

        return sorted(schedule, key=lambda x: x["priority"], reverse=True)

    def _create_engagement_plan(self, analysis: Dict) -> Dict[str, Any]:
        """エンゲージメント計画作成"""

        return {
            "initial_response": {
                "first_30min": "投稿監視・初期反応チェック",
                "first_2hours": "コメント返信・シェア促進",
                "first_24hours": "エンゲージメント分析・追加促進"
            },
            "content_amplification": [
                "体験談シェアの積極的促進",
                "質問・議論の呼びかけ",
                "関連情報の追加提供"
            ],
            "cross_platform_strategy": "Twitter → LinkedIn → Facebook の順で拡散",
            "monitoring_metrics": [
                "リーチ数", "エンゲージメント率",
                "クリック数", "コメント質"
            ]
        }

    def _get_platform_priority(self, platform: str) -> int:
        """プラットフォーム優先度"""

        priority_map = {
            "twitter": 4,    # 最優先（リアルタイム性）
            "linkedin": 3,   # 高優先（ターゲット層）
            "facebook": 2,   # 中優先（拡散力）
            "note": 1        # 低優先（じっくり読みたい層）
        }

        return priority_map.get(platform, 1)

def test_social_media_agent():
    """SNS足軽テスト実行"""

    sns_manager = SocialMediaAshigaru()

    test_article = {
        "title": "ChatGPT導入で失敗する中小企業の特徴",
        "content": "サンプル記事内容...",
        "url": "https://example.com/article"
    }

    result = sns_manager.execute_social_strategy(test_article)

    print(f"\n🎯 SNS戦略結果:")
    print(f"  拡散スコア: {result['content_analysis']['shareability_score']}/100")
    print(f"  投稿プラットフォーム: {len(result['social_content'])}")
    print(f"  期待流入増加: {result['expected_results']['traffic_increase']}")

if __name__ == "__main__":
    test_social_media_agent()