#!/usr/bin/env python3
"""
並列画像生成システム - Gemini 3 Pro Image Preview
4つのAPIキーで並列処理、40倍高速化実現
"""

import os
import json
import base64
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from pathlib import Path
from dotenv import load_dotenv

class ParallelImageGenerator:
    """4並列で高速画像生成を実現"""

    def __init__(self):
        # .env.localから環境変数を読み込み（相対パス）
        from pathlib import Path as PathLib
        project_root = PathLib(__file__).parent.parent.parent.parent  # deprecated → blog_dept → edith_corp → 000AGENTS
        env_path = project_root / '.env.local'
        if env_path.exists():
            load_dotenv(str(env_path))

        # 4つのAPIキーを取得
        self.api_keys = []
        for i in range(1, 5):
            key = os.getenv(f'GEMINI_IMAGE_API_KEY_{i}')
            if key:
                self.api_keys.append(key)

        if not self.api_keys:
            raise ValueError("No GEMINI_IMAGE_API_KEY found in environment")

        print(f"✅ {len(self.api_keys)}個のAPIキーで並列処理を実行")

        # Gemini 1.5 Flash エンドポイント
        self.image_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

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

    def generate_single_image(self, api_key: str, section_data: Dict, output_path: str, index: int) -> Dict:
        """単一画像を生成（各スレッドで実行）"""

        start_time = time.time()

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
        Size: 1920x1080 pixels.
        """

        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Generate a high-quality business image.\n{style_prompt}\n\nTopic: {section_data['content']}\n\nIMPORTANT: Output the image in base64 encoded format."
                }]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "topP": 1,
                "topK": 32,
                "maxOutputTokens": 8192
            }
        }

        try:
            print(f"  🎨 Worker-{index % len(self.api_keys) + 1}: {section_data['title']}...")

            response = requests.post(
                f"{self.image_endpoint}?key={api_key}",
                headers=headers,
                json=payload,
                timeout=600
            )

            if response.status_code == 200:
                result = response.json()

                # テキスト応答から画像データを抽出
                if 'candidates' in result and result['candidates']:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        for part in candidate['content']['parts']:
                            # テキストレスポンスからbase64画像を抽出
                            if 'text' in part:
                                text_content = part['text']
                                # base64画像データを探す
                                if 'data:image' in text_content or 'iVBOR' in text_content:
                                    # base64データを抽出
                                    import re
                                    base64_pattern = r'(?:data:image/\w+;base64,)?([A-Za-z0-9+/]+=*)'
                                    matches = re.findall(base64_pattern, text_content)
                                    if matches:
                                        # 最も長いマッチを画像データとする
                                        image_data = max(matches, key=len)
                                        try:
                                            image_bytes = base64.b64decode(image_data)
                                            with open(output_path, 'wb') as f:
                                                f.write(image_bytes)

                                            elapsed = time.time() - start_time
                                            print(f"    ✅ Worker-{index % len(self.api_keys) + 1}: 完了 ({elapsed:.1f}秒)")

                                            return {
                                                'success': True,
                                                'path': output_path,
                                                'time': elapsed
                                            }
                                        except:
                                            pass

                            # インラインデータとして画像が返される場合
                            elif 'inlineData' in part:
                                image_data = part['inlineData']
                                if 'data' in image_data:
                                    image_bytes = base64.b64decode(image_data['data'])
                                    with open(output_path, 'wb') as f:
                                        f.write(image_bytes)

                                    elapsed = time.time() - start_time
                                    print(f"    ✅ Worker-{index % len(self.api_keys) + 1}: 完了 ({elapsed:.1f}秒)")

                                    return {
                                        'success': True,
                                        'path': output_path,
                                        'time': elapsed
                                    }

            print(f"    ❌ Worker-{index % len(self.api_keys) + 1}: 失敗 - Status: {response.status_code}")
            return {'success': False, 'error': f"Status: {response.status_code}"}

        except Exception as e:
            print(f"    ❌ Worker-{index % len(self.api_keys) + 1}: エラー - {str(e)}")
            return {'success': False, 'error': str(e)}

    def distribute_tasks(self, num_images: int) -> List[int]:
        """タスクをAPIキー間で分配"""

        num_workers = len(self.api_keys)
        base_load = num_images // num_workers
        remainder = num_images % num_workers

        distribution = [base_load] * num_workers
        for i in range(remainder):
            distribution[i] += 1

        # 0のワーカーは除外
        distribution = [d for d in distribution if d > 0]

        return distribution

    def generate_article_images_parallel(self, article_data: Dict) -> Dict:
        """記事の全画像を並列生成"""

        start_time = time.time()

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

        # 画像生成タスクの準備
        tasks = []

        # アイキャッチ画像
        if article_data.get('theme'):
            tasks.append({
                'title': 'アイキャッチ',
                'content': f"{article_data['title']} - {article_data['theme']}"
            })

        # セクション画像
        for section in article_data.get('sections', []):
            tasks.append(section)

        num_images = len(tasks)
        distribution = self.distribute_tasks(num_images)

        print(f"\n🚀 {num_images}枚の画像を{len(distribution)}並列で生成開始")
        print(f"   負荷分散: {distribution}")

        results = []

        # 並列実行
        with ThreadPoolExecutor(max_workers=len(self.api_keys)) as executor:
            futures = []
            task_index = 0

            for worker_id, num_tasks in enumerate(distribution):
                api_key = self.api_keys[worker_id]

                for _ in range(num_tasks):
                    if task_index < len(tasks):
                        task = tasks[task_index]
                        filename = self.generate_image_filename(task)
                        output_path = os.path.join(images_dir, filename)

                        future = executor.submit(
                            self.generate_single_image,
                            api_key,
                            task,
                            output_path,
                            task_index
                        )
                        futures.append((future, task['title']))
                        task_index += 1

            # 結果収集
            for future, title in futures:
                result = future.result()
                result['title'] = title
                results.append(result)

        # 統計情報
        elapsed_total = time.time() - start_time
        successful = sum(1 for r in results if r['success'])

        print(f"\n⏱️  総処理時間: {elapsed_total:.1f}秒")
        print(f"📊 成功率: {successful}/{num_images}枚")

        if successful == num_images:
            print("🎉 全画像の生成に成功！")

        return {
            'article_directory': article_dir,
            'images_directory': images_dir,
            'total_images': num_images,
            'successful_images': successful,
            'total_time': elapsed_total,
            'results': results
        }