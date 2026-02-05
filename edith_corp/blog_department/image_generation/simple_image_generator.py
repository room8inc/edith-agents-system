#!/usr/bin/env python3
"""
シンプルなプレースホルダー画像生成システム
"""

import os
from datetime import datetime
from typing import Dict, List
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

class SimpleImageGenerator:
    """プレースホルダー画像を生成"""

    def __init__(self):
        self.width = 1920
        self.height = 1080

    def extract_keywords_from_content(self, content: str, max_keywords: int = 3) -> List[str]:
        """コンテンツから重要キーワードを抽出（プレフィックスなし）"""

        # ビジネス用語の英語変換辞書
        term_mapping = {
            'AI': 'ai',
            '人工知能': 'ai',
            'ChatGPT': 'chatgpt',
            'Excel': 'excel',
            'VBA': 'vba',
            'ピボット': 'pivot',
            '中小企業': 'sme',
            'FAX': 'fax',
            'デジタル化': 'digitization',
            'DX': 'dx',
            '失敗': 'failure',
            '分析': 'analysis',
            'ROI': 'roi',
            '効果': 'effect',
            'ツール': 'tools',
            '自動化': 'automation',
            '効率化': 'efficiency',
            '改善': 'improvement',
            '戦略': 'strategy',
            'マクロ': 'macro',
            'クエリ': 'query',
            'データ': 'data',
            '作業': 'work',
            '時間': 'time',
            '削減': 'reduction',
            'エラー': 'error',
            '品質': 'quality',
            '職人': 'craftsman',
            'アーキテクト': 'architect'
        }

        keywords = []
        content_lower = content.lower()

        # 優先キーワード抽出
        for term, english in term_mapping.items():
            if term.lower() in content_lower:
                if english not in keywords:
                    keywords.append(english)
                    if len(keywords) >= max_keywords:
                        return keywords

        # 足りない場合は汎用的なキーワードを追加
        generic_terms = ['business', 'tech', 'innovation']
        for term in generic_terms:
            if len(keywords) < max_keywords:
                keywords.append(term)

        return keywords[:max_keywords]

    def generate_image_filename(self, section_data: Dict) -> str:
        """画像ファイル名を生成（プレフィックスなし）"""

        content = f"{section_data.get('title', '')} {section_data.get('content', '')}"
        keywords = self.extract_keywords_from_content(content)

        # プレフィックスなしでファイル名生成
        filename = '_'.join(keywords) + '.png'

        return filename

    def generate_placeholder_image(self, title: str, content: str, output_path: str):
        """プレースホルダー画像を生成"""

        # ランダムな背景色
        colors = [
            (41, 128, 185),   # 青
            (52, 152, 219),   # 明るい青
            (155, 89, 182),   # 紫
            (46, 204, 113),   # 緑
            (52, 73, 94),     # 濃い青
            (231, 76, 60),    # 赤
            (230, 126, 34),   # オレンジ
        ]
        bg_color = random.choice(colors)

        # 画像作成
        img = Image.new('RGB', (self.width, self.height), color=bg_color)
        draw = ImageDraw.Draw(img)

        # テキストを描画（フォントはシステムデフォルトを使用）
        try:
            # macOSのシステムフォントを試す
            from PIL import ImageFont
            font_large = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 60)
            font_small = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 30)
        except:
            # フォントが見つからない場合はデフォルトフォント
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # タイトルを描画（中央上部）
        text_bbox = draw.textbbox((0, 0), title, font=font_large)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (self.width - text_width) // 2
        y = self.height // 3
        draw.text((x, y), title, fill=(255, 255, 255), font=font_large)

        # 内容の一部を描画（中央下部）
        if len(content) > 50:
            content = content[:50] + "..."
        text_bbox = draw.textbbox((0, 0), content, font=font_small)
        text_width = text_bbox[2] - text_bbox[0]
        x = (self.width - text_width) // 2
        y = self.height // 2
        draw.text((x, y), content, fill=(255, 255, 255, 200), font=font_small)

        # 保存
        img.save(output_path)
        print(f"    ✅ 保存完了: {output_path}")

    def generate_article_images(self, article_data: Dict) -> Dict:
        """記事の全画像を生成"""

        # 保存先ディレクトリを統一仕様に合わせる
        date_str = datetime.now().strftime('%Y%m%d')
        slug = article_data.get('slug', 'untitled')

        # 記事と画像の統一保存先（相対パス）
        from pathlib import Path as PathLib
        blog_dept_dir = PathLib(__file__).parent.parent  # image_generation → blog_department
        article_dir = blog_dept_dir / 'articles' / f"{date_str}_{slug}"
        images_dir = article_dir / 'images'

        # ディレクトリ作成
        Path(images_dir).mkdir(parents=True, exist_ok=True)

        print(f"\n📁 保存先: {images_dir}")

        results = []
        successful = 0

        # アイキャッチ画像
        if article_data.get('theme'):
            section_data = {
                'title': 'アイキャッチ',
                'content': f"{article_data['title']} - {article_data['theme']}"
            }
            filename = self.generate_image_filename(section_data)
            output_path = os.path.join(images_dir, filename)

            self.generate_placeholder_image(article_data['title'], article_data['theme'], output_path)
            successful += 1
            results.append({'success': True, 'path': output_path})

        # セクション画像
        for i, section in enumerate(article_data.get('sections', [])):
            filename = self.generate_image_filename(section)
            output_path = os.path.join(images_dir, filename)

            self.generate_placeholder_image(section['title'], section['content'], output_path)
            successful += 1
            results.append({'success': True, 'path': output_path})

        total = len(results)
        print(f"\n📊 生成結果: {successful}/{total}枚成功")

        return {
            'article_directory': article_dir,
            'images_directory': images_dir,
            'total_images': total,
            'successful_images': successful,
            'results': results
        }