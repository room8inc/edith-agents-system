#!/usr/bin/env python3
"""
Excel職人記事用の画像生成
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_image_generator import SimpleImageGenerator

def generate_excel_craftsman_images():
    """Excel職人の変化記事用画像生成（プレースホルダー版）"""

    generator = SimpleImageGenerator()

    article_data = {
        "title": "Excel職人がChatGPTを使い始めて1ヶ月で起きた変化",
        "slug": "excel_craftsman_chatgpt_evolution",
        "theme": "Excel × ChatGPT",
        "sections": [
            {
                "title": "第1週：半信半疑からのスタート",
                "content": "VBA作成が5分で完了。Excel職人がChatGPTの実力を認識。VLOOKUPとピボットテーブルを超えた自動化。"
            },
            {
                "title": "第2週：応用範囲の探索",
                "content": "複雑な関数の組み合わせ、Power Query活用。週40時間の作業が25時間に短縮。データクレンジングの自動化。"
            },
            {
                "title": "第3週：予想外の落とし穴と学び",
                "content": "ChatGPTへの過度な依存で失敗。協働という発想への転換。パートナーとしてのAI活用。"
            },
            {
                "title": "第4週：真の効率化への到達",
                "content": "作業時間50%削減、エラー率80%改善。Excel職人からデータアーキテクトへの進化。"
            }
        ]
    }

    print("\n" + "="*60)
    print("📊 Excel職人×ChatGPT記事の画像生成開始")
    print("="*60)

    result = generator.generate_article_images(article_data)

    print(f"\n✅ 画像生成完了")
    print(f"保存先: {result['article_directory']}")
    print(f"成功: {result['successful_images']}/{result['total_images']}枚")

    return result

if __name__ == "__main__":
    generate_excel_craftsman_images()