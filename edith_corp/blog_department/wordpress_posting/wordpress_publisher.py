#!/usr/bin/env python3
"""
WordPress投稿足軽 - 記事とアイキャッチ画像の自動投稿システム
記事ディレクトリから一括で記事とメタデータ、画像をWordPressへアップロード
"""

import os
import json
import requests
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class WordPressPublisher:
    """WordPress投稿足軽 - 記事と画像の一括投稿"""

    def __init__(self):
        self.rank = "足軽"
        self.specialty = "WordPress自動投稿"
        self.reports_to = "コンテンツ足軽大将"

        # WordPress API設定（環境変数から取得）
        self.wp_site_url = os.environ.get('WP_SITE_URL', 'https://www.room8.co.jp')
        self.wp_username = os.environ.get('WP_USERNAME')
        self.wp_app_password = os.environ.get('WP_APP_PASSWORD')

        # API エンドポイント
        self.wp_api_base = f"{self.wp_site_url}/wp-json/wp/v2"

        print(f"[WordPress投稿足軽] 配属完了 - {self.specialty}を担当")

    def publish_article_with_images(self, article_dir: str) -> Dict[str, Any]:
        """記事ディレクトリから完全投稿（記事+画像+メタデータ）"""

        print(f"[WordPress投稿足軽] 📤 記事投稿開始: {article_dir}")

        # ディレクトリ構造確認
        if not os.path.exists(article_dir):
            return {"success": False, "error": f"記事ディレクトリが存在しません: {article_dir}"}

        # メタデータ読み込み
        meta_result = self._load_article_metadata(article_dir)
        if not meta_result["success"]:
            return meta_result

        meta_data = meta_result["data"]

        # 記事コンテンツ読み込み
        content_result = self._load_article_content(article_dir)
        if not content_result["success"]:
            return content_result

        article_content = content_result["content"]

        # 画像アップロード
        images_result = self._upload_images(article_dir)

        # 記事投稿
        post_result = self._create_wordpress_post(
            meta_data, article_content, images_result.get("featured_image_id")
        )

        if post_result["success"]:
            # WordPressデータを保存
            self._save_wordpress_data(article_dir, post_result["post_data"], images_result)

        result = {
            "article_directory": article_dir,
            "post_success": post_result["success"],
            "post_data": post_result.get("post_data", {}),
            "images_uploaded": images_result.get("uploaded_count", 0),
            "published_at": datetime.now().isoformat()
        }

        if not post_result["success"]:
            result["error"] = post_result["error"]

        print(f"[WordPress投稿足軽] {'✅ 投稿完了' if post_result['success'] else '❌ 投稿失敗'}")
        return result

    def _load_article_metadata(self, article_dir: str) -> Dict[str, Any]:
        """記事メタデータ読み込み"""

        meta_path = os.path.join(article_dir, "meta.json")

        if not os.path.exists(meta_path):
            return {"success": False, "error": "meta.jsonが見つかりません"}

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta_data = json.load(f)

            return {"success": True, "data": meta_data}

        except Exception as e:
            return {"success": False, "error": f"メタデータ読み込みエラー: {str(e)}"}

    def _load_article_content(self, article_dir: str) -> Dict[str, Any]:
        """記事コンテンツ読み込み"""

        article_path = os.path.join(article_dir, "article.md")

        if not os.path.exists(article_path):
            return {"success": False, "error": "article.mdが見つかりません"}

        try:
            with open(article_path, "r", encoding="utf-8") as f:
                content = f.read()

            return {"success": True, "content": content}

        except Exception as e:
            return {"success": False, "error": f"記事コンテンツ読み込みエラー: {str(e)}"}

    def _upload_images(self, article_dir: str) -> Dict[str, Any]:
        """記事用画像の一括アップロード"""

        images_dir = os.path.join(article_dir, "images")

        if not os.path.exists(images_dir):
            print(f"[WordPress投稿足軽] 画像ディレクトリなし: {images_dir}")
            return {"uploaded_count": 0, "images": []}

        uploaded_images = []
        featured_image_id = None

        # 画像ファイルを検索してアップロード
        for image_file in os.listdir(images_dir):
            if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(images_dir, image_file)

                upload_result = self._upload_single_image(image_path, image_file)

                if upload_result["success"]:
                    uploaded_images.append({
                        "filename": image_file,
                        "media_id": upload_result["media_id"],
                        "url": upload_result["url"]
                    })

                    # アイキャッチ画像の特定
                    if "featured" in image_file.lower():
                        featured_image_id = upload_result["media_id"]

                    print(f"[WordPress投稿足軽] 画像アップロード成功: {image_file}")
                else:
                    print(f"[WordPress投稿足軽] 画像アップロード失敗: {image_file}")

        return {
            "uploaded_count": len(uploaded_images),
            "images": uploaded_images,
            "featured_image_id": featured_image_id
        }

    def _upload_single_image(self, image_path: str, filename: str) -> Dict[str, Any]:
        """単一画像のアップロード"""

        if not self.wp_username or not self.wp_app_password:
            # 認証情報がない場合はモック実装
            return self._mock_image_upload(image_path, filename)

        try:
            # ファイル読み込み
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # WordPress REST API メディアアップロード
            headers = {
                'Authorization': self._get_auth_header(),
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'image/png'  # 適切なMIMEタイプを設定
            }

            response = requests.post(
                f"{self.wp_api_base}/media",
                headers=headers,
                data=image_data
            )

            if response.status_code == 201:
                media_data = response.json()
                return {
                    "success": True,
                    "media_id": media_data["id"],
                    "url": media_data["source_url"]
                }
            else:
                return {
                    "success": False,
                    "error": f"アップロード失敗: {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _mock_image_upload(self, image_path: str, filename: str) -> Dict[str, Any]:
        """モック画像アップロード（開発用）"""

        # 開発時のモック実装
        import random
        mock_media_id = random.randint(1000, 9999)
        mock_url = f"https://www.room8.co.jp/wp-content/uploads/2026/02/{filename}"

        print(f"[WordPress投稿足軽] モック画像アップロード: {filename} (ID: {mock_media_id})")

        return {
            "success": True,
            "media_id": mock_media_id,
            "url": mock_url
        }

    def _create_wordpress_post(self, meta_data: Dict[str, Any], content: str, featured_image_id: Optional[int] = None) -> Dict[str, Any]:
        """WordPress記事投稿"""

        if not self.wp_username or not self.wp_app_password:
            # 認証情報がない場合はモック実装
            return self._mock_post_creation(meta_data, content, featured_image_id)

        try:
            # 投稿データ構築
            post_data = {
                "title": meta_data.get("title", ""),
                "content": content,
                "status": "draft",  # デフォルトは下書き
                "author": 1,  # 適切な作成者IDを設定
                "meta": {
                    "seo_description": meta_data.get("seo", {}).get("meta_description", ""),
                    "primary_keywords": meta_data.get("seo", {}).get("primary_keywords", [])
                }
            }

            # アイキャッチ画像設定
            if featured_image_id:
                post_data["featured_media"] = featured_image_id

            # カテゴリー設定
            category = meta_data.get("category", "AI活用")
            category_id = self._get_or_create_category(category)
            if category_id:
                post_data["categories"] = [category_id]

            # タグ設定
            tags = meta_data.get("tags", [])
            if tags:
                tag_ids = [self._get_or_create_tag(tag) for tag in tags]
                post_data["tags"] = [tag_id for tag_id in tag_ids if tag_id]

            # 投稿実行
            response = requests.post(
                f"{self.wp_api_base}/posts",
                headers={'Authorization': self._get_auth_header()},
                json=post_data
            )

            if response.status_code == 201:
                created_post = response.json()
                return {
                    "success": True,
                    "post_data": {
                        "id": created_post["id"],
                        "url": created_post["link"],
                        "status": created_post["status"],
                        "title": created_post["title"]["rendered"]
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"投稿失敗: {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _mock_post_creation(self, meta_data: Dict[str, Any], content: str, featured_image_id: Optional[int] = None) -> Dict[str, Any]:
        """モック記事投稿（開発用）"""

        import random
        mock_post_id = random.randint(100, 999)
        slug = meta_data.get("slug", "test-article")
        mock_url = f"https://www.room8.co.jp/{slug}/"

        print(f"[WordPress投稿足軽] モック記事投稿: {meta_data.get('title', '')} (ID: {mock_post_id})")

        return {
            "success": True,
            "post_data": {
                "id": mock_post_id,
                "url": mock_url,
                "status": "draft",
                "title": meta_data.get("title", ""),
                "featured_media": featured_image_id
            }
        }

    def _get_or_create_category(self, category_name: str) -> Optional[int]:
        """カテゴリー取得または作成"""

        # モック実装
        category_map = {
            "AI活用": 1,
            "デジタル化": 2,
            "業務効率": 3
        }

        return category_map.get(category_name, 1)  # デフォルトはAI活用

    def _get_or_create_tag(self, tag_name: str) -> Optional[int]:
        """タグ取得または作成"""

        # モック実装
        import hashlib
        tag_hash = int(hashlib.md5(tag_name.encode()).hexdigest()[:6], 16)
        return tag_hash % 1000 + 100  # 100-1099の範囲

    def _get_auth_header(self) -> str:
        """WordPress認証ヘッダー生成"""

        credentials = f"{self.wp_username}:{self.wp_app_password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"

    def _save_wordpress_data(self, article_dir: str, post_data: Dict[str, Any], images_data: Dict[str, Any]):
        """WordPress投稿データの保存"""

        wordpress_dir = os.path.join(article_dir, "wordpress")
        os.makedirs(wordpress_dir, exist_ok=True)

        # 投稿データ保存
        publish_data = {
            "post_id": post_data.get("id"),
            "post_url": post_data.get("url"),
            "status": post_data.get("status"),
            "published_at": datetime.now().isoformat(),
            "featured_media": post_data.get("featured_media"),
            "images_uploaded": images_data.get("images", [])
        }

        publish_data_path = os.path.join(wordpress_dir, "publish_data.json")
        with open(publish_data_path, "w", encoding="utf-8") as f:
            json.dump(publish_data, f, ensure_ascii=False, indent=2)

        print(f"[WordPress投稿足軽] 投稿データ保存: {publish_data_path}")


class ArticlePublishingWorkflow:
    """記事投稿ワークフロー統合クラス"""

    def __init__(self):
        self.publisher = WordPressPublisher()

    def process_article_directory(self, article_dir: str, publish_mode: str = "draft") -> Dict[str, Any]:
        """記事ディレクトリの完全処理"""

        print(f"[記事投稿ワークフロー] 📁 処理開始: {article_dir}")

        # 1. ディレクトリ存在確認
        if not os.path.exists(article_dir):
            return {
                "success": False,
                "error": f"記事ディレクトリが存在しません: {article_dir}"
            }

        # 2. 必要ファイル確認
        required_files = ["article.md", "meta.json"]
        missing_files = []

        for file_name in required_files:
            file_path = os.path.join(article_dir, file_name)
            if not os.path.exists(file_path):
                missing_files.append(file_name)

        if missing_files:
            return {
                "success": False,
                "error": f"必要ファイルが不足: {', '.join(missing_files)}"
            }

        # 3. WordPress投稿実行
        publish_result = self.publisher.publish_article_with_images(article_dir)

        # 4. 結果統合
        workflow_result = {
            "workflow_success": publish_result["post_success"],
            "article_directory": article_dir,
            "wordpress_post": publish_result.get("post_data", {}),
            "images_processed": publish_result.get("images_uploaded", 0),
            "processing_mode": publish_mode,
            "completed_at": datetime.now().isoformat()
        }

        if not publish_result["post_success"]:
            workflow_result["error"] = publish_result.get("error", "不明なエラー")

        status = "✅ 成功" if workflow_result["workflow_success"] else "❌ 失敗"
        print(f"[記事投稿ワークフロー] {status}")

        return workflow_result


def test_wordpress_publishing():
    """WordPress投稿システムのテスト"""

    print("🚀 WordPress投稿システムテスト")
    print("=" * 60)

    workflow = ArticlePublishingWorkflow()

    # テスト記事ディレクトリパスを探索
    articles_base = "articles"
    if os.path.exists(articles_base):
        # 最新の記事ディレクトリを使用
        article_dirs = [d for d in os.listdir(articles_base) if os.path.isdir(os.path.join(articles_base, d))]
        if article_dirs:
            latest_article = sorted(article_dirs)[-1]
            test_article_dir = os.path.join(articles_base, latest_article)

            print(f"[テスト] 使用記事ディレクトリ: {test_article_dir}")

            # ワークフロー実行
            result = workflow.process_article_directory(test_article_dir, "draft")

            print(f"\n📊 処理結果:")
            print(f"  成功: {'✅' if result['workflow_success'] else '❌'}")
            print(f"  WordPress投稿ID: {result['wordpress_post'].get('id', 'N/A')}")
            print(f"  画像処理数: {result['images_processed']}枚")
            print(f"  投稿URL: {result['wordpress_post'].get('url', 'N/A')}")

        else:
            print("[テスト] 記事ディレクトリが見つかりません")
    else:
        print("[テスト] articlesディレクトリが存在しません")


if __name__ == "__main__":
    test_wordpress_publishing()