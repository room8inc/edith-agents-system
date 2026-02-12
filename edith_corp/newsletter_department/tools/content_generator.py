#!/usr/bin/env python3
"""
メルマガコンテンツ生成

Claudeを使ってメルマガの件名・本文を自動生成する。
HTMLテンプレートとの組み合わせで完成形を作る。
"""

import json
from typing import Dict, Optional
from pathlib import Path


class ContentGenerator:
    """メルマガコンテンツ生成"""

    TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

    def __init__(self):
        """初期化"""
        self.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    def generate_blog_update(self, blog_title: str, blog_url: str, excerpt: str) -> Dict[str, str]:
        """
        ブログ更新通知メルマガを生成

        Args:
            blog_title: ブログタイトル
            blog_url: ブログURL
            excerpt: 抜粋

        Returns:
            {"subject": "件名", "html_content": "HTML本文", "plain_text": "プレーン本文"}
        """
        subject = f"📝 新着ブログ: {blog_title}"

        html_content = f"""
        <h2>新しいブログ記事を公開しました</h2>
        <h3>{blog_title}</h3>
        <p>{excerpt}</p>
        <p><a href="{blog_url}" style="background-color: #0066cc; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">記事を読む</a></p>
        """

        plain_text = f"""
新しいブログ記事を公開しました

{blog_title}

{excerpt}

続きを読む: {blog_url}
        """

        return {
            "subject": subject,
            "html_content": self._apply_template(html_content),
            "plain_text": plain_text
        }

    def generate_event_announcement(
        self,
        event_name: str,
        event_date: str,
        event_description: str,
        event_url: str
    ) -> Dict[str, str]:
        """
        イベント告知メルマガを生成

        Args:
            event_name: イベント名
            event_date: 開催日時
            event_description: 説明
            event_url: 申し込みURL

        Returns:
            {"subject": "件名", "html_content": "HTML本文", "plain_text": "プレーン本文"}
        """
        subject = f"🎉 {event_name} のご案内"

        html_content = f"""
        <h2>{event_name}</h2>
        <p><strong>📅 日時:</strong> {event_date}</p>
        <p>{event_description}</p>
        <p><a href="{event_url}" style="background-color: #00cc66; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">イベントに申し込む</a></p>
        """

        plain_text = f"""
{event_name}

📅 日時: {event_date}

{event_description}

お申し込みはこちら: {event_url}
        """

        return {
            "subject": subject,
            "html_content": self._apply_template(html_content),
            "plain_text": plain_text
        }

    def generate_monthly_digest(self, items: list) -> Dict[str, str]:
        """
        月次ダイジェストメルマガを生成

        Args:
            items: コンテンツリスト [{"title": "...", "url": "...", "description": "..."}]

        Returns:
            {"subject": "件名", "html_content": "HTML本文", "plain_text": "プレーン本文"}
        """
        subject = "📰 Room8 月間ダイジェスト"

        html_items = ""
        plain_items = ""

        for item in items:
            html_items += f"""
            <div style="margin-bottom: 24px;">
                <h3>{item['title']}</h3>
                <p>{item['description']}</p>
                <p><a href="{item['url']}">続きを読む →</a></p>
            </div>
            """

            plain_items += f"""
{item['title']}
{item['description']}
{item['url']}

"""

        html_content = f"""
        <h2>今月のハイライト</h2>
        {html_items}
        """

        plain_text = f"""
Room8 月間ダイジェスト

今月のハイライト

{plain_items}
        """

        return {
            "subject": subject,
            "html_content": self._apply_template(html_content),
            "plain_text": plain_text
        }

    def _apply_template(self, content: str) -> str:
        """
        HTMLテンプレートを適用

        Args:
            content: 本文コンテンツ

        Returns:
            完成したHTML
        """
        template_path = self.TEMPLATES_DIR / "base.html"

        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()
            return template.replace("{{CONTENT}}", content)
        else:
            # テンプレートがない場合はシンプルなHTMLを返す
            return f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Room8 Newsletter</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        h2 {{
            color: #0066cc;
            border-bottom: 2px solid #0066cc;
            padding-bottom: 8px;
        }}
        h3 {{
            color: #333;
        }}
        a {{
            color: #0066cc;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ccc;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #0066cc;">Room8</h1>
        <p style="color: #666;">AI × コワーキング × コミュニティ</p>
    </div>

    {content}

    <div class="footer">
        <p>株式会社Room8<br>
        〒486-0931 愛知県春日井市松新町1-3 ルネッサンスシティ勝川 Nexia-C<br>
        営業時間: 平日 10:00-18:00<br>
        <a href="https://room8.co.jp">https://room8.co.jp</a></p>
        <p><a href="{{UNSUBSCRIBE_URL}}">配信解除</a></p>
    </div>
</body>
</html>
            """

    def save_template(self, template_name: str, template_content: str) -> None:
        """
        テンプレート保存

        Args:
            template_name: テンプレート名（拡張子なし）
            template_content: HTML内容
        """
        template_path = self.TEMPLATES_DIR / f"{template_name}.html"
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(template_content)


def main():
    """CLI テスト用"""
    import argparse

    parser = argparse.ArgumentParser(description="コンテンツ生成 CLI")
    parser.add_argument("type", choices=["blog", "event", "digest"], help="生成するコンテンツタイプ")

    args = parser.parse_args()

    generator = ContentGenerator()

    if args.type == "blog":
        # ブログ更新通知のサンプル
        content = generator.generate_blog_update(
            blog_title="AIエージェントでビジネスを自動化する5つの方法",
            blog_url="https://room8.co.jp/blog/ai-automation-5-ways",
            excerpt="AIエージェントを活用することで、定型業務を自動化し、本当に価値のある仕事に集中できます。この記事では実践的な5つの方法をご紹介します。"
        )
        print(f"件名: {content['subject']}\n")
        print("HTML:")
        print(content['html_content'])

    elif args.type == "event":
        # イベント告知のサンプル
        content = generator.generate_event_announcement(
            event_name="AI LAB 第1回: ChatGPT活用ワークショップ",
            event_date="2026年2月20日（木） 19:00-21:00",
            event_description="ChatGPTを使った業務効率化の実践ワークショップです。プロンプト設計から実際の活用事例まで、hands-onで学びます。",
            event_url="https://room8.co.jp/ailab/event/001"
        )
        print(f"件名: {content['subject']}\n")
        print("HTML:")
        print(content['html_content'])

    elif args.type == "digest":
        # 月次ダイジェストのサンプル
        content = generator.generate_monthly_digest([
            {
                "title": "AI LAB 第1回イベント 開催レポート",
                "url": "https://room8.co.jp/blog/ailab-report-001",
                "description": "20名の参加者とともに、ChatGPTの実践的な活用方法を学びました。"
            },
            {
                "title": "新サービス: AI導入コンサルティング",
                "url": "https://room8.co.jp/services/ai-consulting",
                "description": "企業向けAI導入支援サービスをスタートしました。"
            }
        ])
        print(f"件名: {content['subject']}\n")
        print("HTML:")
        print(content['html_content'])


if __name__ == "__main__":
    main()
