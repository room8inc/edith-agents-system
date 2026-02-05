#!/usr/bin/env python3
"""
画像生成システム - Gemini 3 Pro Image Preview
通常版（単一処理・安定性重視）
"""

import os
import json
import base64
import requests
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv

class ImageGenerator:
    """Gemini 3 Pro Image Preview を使用した画像生成"""

    def __init__(self):
        # .env.localから環境変数を読み込み（相対パス）
        from pathlib import Path as PathLib
        project_root = PathLib(__file__).parent.parent.parent.parent  # deprecated → blog_dept → edith_corp → 000AGENTS
        env_path = project_root / '.env.local'
        if env_path.exists():
            load_dotenv(str(env_path))

        # 最初のAPIキーを使用
        self.api_key = os.getenv('GEMINI_IMAGE_API_KEY_1')
        if not self.api_key:
            # 旧環境変数名にフォールバック
            self.api_key = os.getenv('GEMINI_IMAGE_API_KEY')

        if not self.api_key:
            raise ValueError("No GEMINI_IMAGE_API_KEY found in environment")

        # Gemini 3 Pro Image Preview エンドポイント（最高品質）
        self.image_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent"

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
            '戦略': 'strategy'
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

    def generate_image(self, prompt: str, output_path: str) -> bool:
        """単一画像を生成"""

        headers = {
            'Content-Type': 'application/json',
        }

        # 高品質画像生成プロンプト
        style_prompt = """
        Professional business infographic style.
        Modern, clean design with professional color scheme.
        High contrast, clear visual hierarchy.
        Minimalist but impactful.
        Corporate presentation quality.
        """

        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Generate a high-quality image: {style_prompt}\n\nCreate image for: {prompt}"
                }]
            }],
            "generationConfig": {
                "responseMimeType": "image/png"
            }
        }

        try:
            print(f"  🎨 生成中: {output_path.split('/')[-1]}...")

            response = requests.post(
                f"{self.image_endpoint}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=600  # 10分タイムアウト
            )

            if response.status_code == 200:
                result = response.json()

                if 'candidates' in result and result['candidates']:
                    image_data = result['candidates'][0]['content']['parts'][0].get('inlineData', {})
                    if 'data' in image_data:
                        # 画像保存
                        image_bytes = base64.b64decode(image_data['data'])
                        with open(output_path, 'wb') as f:
                            f.write(image_bytes)

                        print(f"    ✅ 保存完了: {output_path}")
                        return True

            print(f"    ❌ 生成失敗: Status {response.status_code}")
            return False

        except Exception as e:
            print(f"    ❌ エラー: {str(e)}")
            return False

    def generate_article_images(self, article_data: Dict) -> Dict:
        """記事の全画像を生成（順次処理）"""

        # 保存先ディレクトリを統一仕様に合わせる
        date_str = datetime.now().strftime('%Y%m%d')
        slug = article_data.get('slug', 'untitled')

        # 記事と画像の統一保存先（相対パス）
        from pathlib import Path as PathLib
        blog_dept_dir = PathLib(__file__).parent.parent  # deprecated → blog_department
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

            if self.generate_image(section_data['content'], output_path):
                successful += 1
                results.append({'success': True, 'path': output_path})
            else:
                results.append({'success': False})

        # セクション画像
        for i, section in enumerate(article_data.get('sections', [])):
            filename = self.generate_image_filename(section)
            output_path = os.path.join(images_dir, filename)

            if self.generate_image(section['content'], output_path):
                successful += 1
                results.append({'success': True, 'path': output_path})
            else:
                results.append({'success': False})

        total = len(results)
        print(f"\n📊 生成結果: {successful}/{total}枚成功")

        return {
            'article_directory': article_dir,
            'images_directory': images_dir,
            'total_images': total,
            'successful_images': successful,
            'results': results
        }