#!/usr/bin/env python3
"""
画像生成システム - Gemini 3 API + 並列処理（バッチ対応版）
8枚を超える場合は分割処理
"""

import os
import json
import base64
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

class Gemini3ImageGenerator:
    """Gemini 3を使用した並列画像生成（バッチ処理対応）"""

    MAX_BATCH_SIZE = 8  # 1バッチの最大枚数

    def __init__(self):
        # .env.localから環境変数を読み込み（相対パス）
        from pathlib import Path as PathLib
        project_root = PathLib(__file__).parent.parent.parent.parent  # image_gen → blog_dept → edith_corp → 000AGENTS
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

        # Gemini 3 エンドポイント（最新API）
        # 参照: https://ai.google.dev/gemini-api/docs/gemini-3?hl=ja
        self.image_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.0:generateContent"

    def extract_keywords_from_content(self, content: str, max_keywords: int = 3) -> List[str]:
        """コンテンツから重要キーワードを抽出（プレフィックスなし）"""

        # ビジネス用語の英語変換辞書
        term_mapping = {
            'AI': 'ai',
            '人工知能': 'ai',
            'ChatGPT': 'chatgpt',
            'Excel': 'excel',
            '失敗': 'failure',
            '分析': 'analysis',
            '自動化': 'automation',
            '効率化': 'efficiency',
            '改善': 'improvement',
            '戦略': 'strategy',
            'ビジネス': 'business',
            'パターン': 'pattern',
            '導入': 'implementation',
            '期待': 'expectation',
            '現場': 'field',
            'トップダウン': 'topdown'
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

    def _create_image_prompt(self, title: str, content: str) -> str:
        """画像生成用プロンプトを作成"""

        prompt = f"""
        Create a professional business image for a blog article.
        Title: {title}
        Content: {content}

        Requirements:
        - Modern and professional design
        - Business or technology theme
        - High quality and engaging
        - Suitable for a blog header or section image
        - Include subtle elements related to AI, automation, or business
        """
        return prompt

    def _generate_single_image(self, task: Dict, api_key: str) -> Dict:
        """単一画像を生成（APIキー指定）"""

        headers = {
            'Content-Type': 'application/json',
        }

        payload = {
            'contents': [{
                'parts': [{
                    'text': task['prompt']
                }]
            }],
            'generationConfig': {
                'temperature': 0.4,
                'topK': 32,
                'topP': 1,
                'maxOutputTokens': 4096,
            }
        }

        url = f"{self.image_endpoint}?key={api_key}"

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()

                # 画像データの取得（Base64）
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        for part in candidate['content']['parts']:
                            if 'inlineData' in part:
                                image_data = part['inlineData']['data']
                                mime_type = part['inlineData']['mimeType']

                                # Base64デコードして保存
                                image_bytes = base64.b64decode(image_data)
                                with open(task['output_path'], 'wb') as f:
                                    f.write(image_bytes)

                                return {
                                    'success': True,
                                    'path': task['output_path'],
                                    'title': task['title']
                                }

                # 画像データが見つからない場合
                return {
                    'success': False,
                    'error': 'No image data in response',
                    'title': task['title']
                }

            else:
                return {
                    'success': False,
                    'error': f'Status: {response.status_code}',
                    'title': task['title']
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'title': task['title']
            }

    def _distribute_tasks(self, num_images: int) -> List[int]:
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

    def _process_batch(self, tasks: List[Dict], batch_num: int = 1) -> Dict:
        """バッチ単位で画像生成処理"""

        num_images = len(tasks)
        print(f"   処理枚数: {num_images}枚")

        # 負荷分散計算
        distribution = self._distribute_tasks(num_images)
        print(f"   負荷分散: {distribution}")

        results = []
        successful = 0

        # 並列実行
        with ThreadPoolExecutor(max_workers=len(self.api_keys)) as executor:
            futures = {}
            task_index = 0

            for worker_id, num_tasks in enumerate(distribution):
                api_key = self.api_keys[worker_id]

                for _ in range(num_tasks):
                    if task_index < len(tasks):
                        task = tasks[task_index]
                        print(f"  🎨 Worker-{worker_id+1}: {task['title']}...")

                        future = executor.submit(
                            self._generate_single_image,
                            task,
                            api_key
                        )
                        futures[future] = (worker_id, task['title'])
                        task_index += 1

            # 結果収集
            for future in as_completed(futures):
                worker_id, title = futures[future]
                result = future.result()

                if result['success']:
                    print(f"    ✅ Worker-{worker_id+1}: 成功")
                    successful += 1
                else:
                    print(f"    ❌ Worker-{worker_id+1}: 失敗 - {result['error']}")

                results.append(result)

        return {
            'results': results,
            'successful': successful,
            'total': num_images
        }

    def generate_article_images_parallel(self, article_data: Dict) -> Dict:
        """記事の全画像を並列生成（8枚を超える場合は分割処理）"""

        start_time = time.time()

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

        # 生成タスクリスト作成
        all_tasks = []

        # アイキャッチ画像
        if article_data.get('theme'):
            section_data = {
                'title': 'アイキャッチ',
                'content': f"{article_data['title']} - {article_data['theme']}"
            }
            filename = self.generate_image_filename(section_data)
            all_tasks.append({
                'title': 'アイキャッチ',
                'content': article_data['theme'],
                'prompt': self._create_image_prompt(article_data['title'], article_data['theme']),
                'filename': filename,
                'output_path': os.path.join(images_dir, filename)
            })

        # セクション画像
        for i, section in enumerate(article_data.get('sections', [])):
            filename = self.generate_image_filename(section)
            prompt = self._create_image_prompt(section['title'], section['content'])
            all_tasks.append({
                'title': section['title'],
                'content': section['content'],
                'prompt': prompt,
                'filename': filename,
                'output_path': os.path.join(images_dir, filename)
            })

        total_images = len(all_tasks)
        if total_images == 0:
            return {
                'article_directory': article_dir,
                'images_directory': images_dir,
                'total_images': 0,
                'successful_images': 0,
                'results': []
            }

        # 8枚を超える場合は分割処理
        all_results = []
        total_successful = 0

        if total_images > self.MAX_BATCH_SIZE:
            print(f"\n⚠️ {total_images}枚は多いため、{self.MAX_BATCH_SIZE}枚ずつバッチ処理します")

            # バッチに分割
            for batch_start in range(0, total_images, self.MAX_BATCH_SIZE):
                batch_end = min(batch_start + self.MAX_BATCH_SIZE, total_images)
                batch_tasks = all_tasks[batch_start:batch_end]
                batch_num = (batch_start // self.MAX_BATCH_SIZE) + 1

                print(f"\n📦 バッチ {batch_num}: {batch_start+1}-{batch_end}枚目を処理")

                # バッチ処理実行
                batch_results = self._process_batch(batch_tasks, batch_num)
                all_results.extend(batch_results['results'])
                total_successful += batch_results['successful']

                # 次のバッチがある場合は少し待機
                if batch_end < total_images:
                    print(f"   ⏳ 次のバッチまで3秒待機...")
                    time.sleep(3)
        else:
            # 8枚以下なら通常処理
            print(f"\n🚀 {total_images}枚の画像を{len(self.api_keys)}並列で生成開始")
            batch_results = self._process_batch(all_tasks)
            all_results = batch_results['results']
            total_successful = batch_results['successful']

        # 処理時間
        elapsed_time = time.time() - start_time

        print(f"\n⏱️  総処理時間: {elapsed_time:.1f}秒")
        print(f"📊 成功率: {total_successful}/{total_images}枚")

        return {
            'article_directory': article_dir,
            'images_directory': images_dir,
            'total_images': total_images,
            'successful_images': total_successful,
            'results': all_results,
            'processing_time': elapsed_time
        }


if __name__ == "__main__":
    # テスト実行
    generator = Gemini3ImageGenerator()

    # 10枚のテストデータ（8枚を超えるケース）
    test_article = {
        'title': 'AI活用で失敗する企業の特徴',
        'slug': 'ai-failure-patterns-test',
        'theme': 'AI導入に失敗する企業のパターン分析',
        'sections': [
            {'title': f'セクション{i+1}', 'content': f'テストコンテンツ{i+1}'}
            for i in range(9)  # 合計10枚（アイキャッチ+9セクション）
        ]
    }

    print("🚀 Gemini 3 API バッチ処理テスト開始...")
    result = generator.generate_article_images_parallel(test_article)

    print(f"\n✅ テスト完了")
    print(f"   成功: {result['successful_images']}/{result['total_images']}枚")
    print(f"   処理時間: {result.get('processing_time', 0):.1f}秒")