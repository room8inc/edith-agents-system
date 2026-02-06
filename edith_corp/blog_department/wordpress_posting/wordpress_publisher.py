#!/usr/bin/env python3
"""
WordPress投稿足軽 - 記事とアイキャッチ画像の自動投稿システム
記事ディレクトリから一括で記事とメタデータ、画像をWordPressへアップロード
"""

import os
import json
import requests
import base64
import markdown
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# .env.localから環境変数を読み込み
_project_root = Path(__file__).resolve().parent.parent.parent.parent
_env_path = _project_root / '.env.local'
if _env_path.exists():
    load_dotenv(str(_env_path))

# 固定カテゴリーリスト（WordPressに存在するカテゴリー名）
ALLOWED_CATEGORIES = [
    "AIラボ",
    "Webラボ",
    "コワーキングスペース",
    "マーケティング・SEO",
    "働き方・生産性",
    "財務・会計",
    "起業・個人事業主",
]


class WordPressPublisher:
    """WordPress投稿足軽 - 記事と画像の一括投稿"""

    def __init__(self):
        self.rank = "足軽"
        self.specialty = "WordPress自動投稿"
        self.reports_to = "コンテンツ足軽大将"

        # WordPress API設定（環境変数から取得）
        self.wp_site_url = os.environ.get('WORDPRESS_URL') or os.environ.get('WP_SITE_URL', 'https://www.room8.co.jp')
        self.wp_username = os.environ.get('WORDPRESS_USERNAME') or os.environ.get('WP_USERNAME')
        self.wp_app_password = os.environ.get('WORDPRESS_APPLICATION_PASSWORD') or os.environ.get('WP_APP_PASSWORD')

        # API エンドポイント
        self.wp_api_base = f"{self.wp_site_url}/wp-json/wp/v2"

        # カテゴリーIDキャッシュ
        self._category_cache = {}
        self._tag_cache = {}

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

        # 記事コンテンツ読み込み（Markdown → HTML変換）
        content_result = self._load_article_content(article_dir)
        if not content_result["success"]:
            return content_result

        article_html = content_result["content"]

        # 画像アップロード
        images_result = self._upload_images(article_dir)

        # アップロードした画像を記事HTML内に挿入
        if images_result.get("images"):
            article_html = self._insert_images_into_content(article_html, images_result["images"])

        # 記事投稿
        post_result = self._create_wordpress_post(
            meta_data, article_html, images_result.get("featured_image_id")
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
        """記事コンテンツ読み込み（Markdown → HTML変換）"""

        article_path = os.path.join(article_dir, "article.md")

        if not os.path.exists(article_path):
            return {"success": False, "error": "article.mdが見つかりません"}

        try:
            with open(article_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            # 先頭のH1タイトル行を除去（WordPressはtitleフィールドで管理するため）
            lines = md_content.split('\n')
            if lines and lines[0].startswith('# '):
                md_content = '\n'.join(lines[1:]).lstrip('\n')

            # Markdown → HTML変換
            html_content = markdown.markdown(
                md_content,
                extensions=['extra', 'nl2br', 'sane_lists']
            )

            return {"success": True, "content": html_content}

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

        # 画像ファイルをソートして処理（00_が先頭=アイキャッチ）
        image_files = sorted([
            f for f in os.listdir(images_dir)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])

        for idx, image_file in enumerate(image_files):
            image_path = os.path.join(images_dir, image_file)

            upload_result = self._upload_single_image(image_path, image_file)

            if upload_result["success"]:
                uploaded_images.append({
                    "filename": image_file,
                    "media_id": upload_result["media_id"],
                    "url": upload_result["url"]
                })

                # インデックス0の画像をアイキャッチとして使用
                if idx == 0:
                    featured_image_id = upload_result["media_id"]
                    print(f"[WordPress投稿足軽] アイキャッチ画像: {image_file}")

                print(f"[WordPress投稿足軽] 画像アップロード成功: {image_file}")
            else:
                print(f"[WordPress投稿足軽] 画像アップロード失敗: {image_file}")

        return {
            "uploaded_count": len(uploaded_images),
            "images": uploaded_images,
            "featured_image_id": featured_image_id
        }

    def _insert_images_into_content(self, html_content: str, uploaded_images: List[Dict]) -> str:
        """アップロードした画像を記事のH2見出しの直後に挿入する"""

        # アイキャッチ（index 0）は除外、セクション画像（index 1以降）を挿入
        section_images = uploaded_images[1:] if len(uploaded_images) > 1 else []

        if not section_images:
            return html_content

        # H2タグを見つけて、各H2の直後に対応する画像を挿入
        import re
        h2_pattern = re.compile(r'(<h2>.*?</h2>)', re.DOTALL)
        h2_matches = list(h2_pattern.finditer(html_content))

        # 後ろから挿入（インデックスがずれないように）
        for i in range(min(len(h2_matches), len(section_images)) - 1, -1, -1):
            match = h2_matches[i]
            img = section_images[i]
            img_tag = f'\n<figure class="wp-block-image"><img src="{img["url"]}" alt="{img["filename"]}"/></figure>\n'
            insert_pos = match.end()
            html_content = html_content[:insert_pos] + img_tag + html_content[insert_pos:]

        return html_content

    def _upload_single_image(self, image_path: str, filename: str) -> Dict[str, Any]:
        """単一画像のアップロード"""

        if not self.wp_username or not self.wp_app_password:
            return self._mock_image_upload(image_path, filename)

        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # MIMEタイプの判定
            if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                content_type = 'image/jpeg'
            else:
                content_type = 'image/png'

            headers = {
                'Authorization': self._get_auth_header(),
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': content_type
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
            return self._mock_post_creation(meta_data, content, featured_image_id)

        try:
            author_id = self._get_current_user_id()

            post_data = {
                "title": meta_data.get("title", ""),
                "slug": meta_data.get("slug", ""),
                "content": content,
                "status": "draft",
            }

            if author_id:
                post_data["author"] = author_id

            if featured_image_id:
                post_data["featured_media"] = featured_image_id

            # カテゴリー設定（固定リストから選択）
            category = meta_data.get("category", "AIラボ")
            if category not in ALLOWED_CATEGORIES:
                category = "AIラボ"
            category_id = self._get_or_create_category(category)
            if category_id:
                post_data["categories"] = [category_id]

            # タグ設定（meta.jsonのtagsから）
            tags = meta_data.get("tags", [])
            if tags:
                tag_ids = [self._get_or_create_tag(tag) for tag in tags]
                post_data["tags"] = [tid for tid in tag_ids if tid]

            # SEOメタディスクリプション（Yoast SEO対応）
            seo_meta = meta_data.get("seo", {})
            if seo_meta.get("meta_description"):
                post_data["meta"] = {
                    "_yoast_wpseo_metadesc": seo_meta["meta_description"]
                }

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
                try:
                    error_body = response.json()
                    error_detail = error_body.get("message", response.text[:500])
                    error_code = error_body.get("code", "unknown")
                except Exception:
                    error_detail = response.text[:500]
                    error_code = "unknown"
                return {
                    "success": False,
                    "error": f"投稿失敗: {response.status_code} ({error_code}: {error_detail})"
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
        """カテゴリーIDをWordPress APIから取得（なければ作成）"""

        if category_name in self._category_cache:
            return self._category_cache[category_name]

        if not self.wp_username or not self.wp_app_password:
            return 1

        try:
            # 既存カテゴリーを検索
            response = requests.get(
                f"{self.wp_api_base}/categories",
                headers={'Authorization': self._get_auth_header()},
                params={"search": category_name, "per_page": 10},
                timeout=10
            )

            if response.status_code == 200:
                categories = response.json()
                for cat in categories:
                    if cat["name"] == category_name:
                        self._category_cache[category_name] = cat["id"]
                        print(f"[WordPress投稿足軽] カテゴリー取得: {category_name} (ID: {cat['id']})")
                        return cat["id"]

            # 見つからなければ作成
            response = requests.post(
                f"{self.wp_api_base}/categories",
                headers={'Authorization': self._get_auth_header()},
                json={"name": category_name},
                timeout=10
            )

            if response.status_code == 201:
                cat_id = response.json()["id"]
                self._category_cache[category_name] = cat_id
                print(f"[WordPress投稿足軽] カテゴリー作成: {category_name} (ID: {cat_id})")
                return cat_id

        except Exception as e:
            print(f"[WordPress投稿足軽] カテゴリー処理エラー: {e}")

        return None

    def _get_or_create_tag(self, tag_name: str) -> Optional[int]:
        """タグIDをWordPress APIから取得（なければ作成）"""

        if tag_name in self._tag_cache:
            return self._tag_cache[tag_name]

        if not self.wp_username or not self.wp_app_password:
            return None

        try:
            # 既存タグを検索
            response = requests.get(
                f"{self.wp_api_base}/tags",
                headers={'Authorization': self._get_auth_header()},
                params={"search": tag_name, "per_page": 10},
                timeout=10
            )

            if response.status_code == 200:
                tags = response.json()
                for tag in tags:
                    if tag["name"] == tag_name:
                        self._tag_cache[tag_name] = tag["id"]
                        return tag["id"]

            # 見つからなければ作成
            response = requests.post(
                f"{self.wp_api_base}/tags",
                headers={'Authorization': self._get_auth_header()},
                json={"name": tag_name},
                timeout=10
            )

            if response.status_code == 201:
                tag_id = response.json()["id"]
                self._tag_cache[tag_name] = tag_id
                print(f"[WordPress投稿足軽] タグ作成: {tag_name} (ID: {tag_id})")
                return tag_id

        except Exception as e:
            print(f"[WordPress投稿足軽] タグ処理エラー: {e}")

        return None

    def _get_current_user_id(self) -> Optional[int]:
        """認証中ユーザーのWordPress IDを取得"""

        try:
            response = requests.get(
                f"{self.wp_api_base}/users/me",
                headers={'Authorization': self._get_auth_header()},
                timeout=10
            )
            if response.status_code == 200:
                user_id = response.json().get("id")
                print(f"[WordPress投稿足軽] 認証ユーザーID: {user_id}")
                return user_id
            else:
                print(f"[WordPress投稿足軽] ユーザーID取得失敗: {response.status_code}")
                return None
        except Exception as e:
            print(f"[WordPress投稿足軽] ユーザーID取得エラー: {e}")
            return None

    def _get_auth_header(self) -> str:
        """WordPress認証ヘッダー生成"""

        credentials = f"{self.wp_username}:{self.wp_app_password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"

    def _save_wordpress_data(self, article_dir: str, post_data: Dict[str, Any], images_data: Dict[str, Any]):
        """WordPress投稿データの保存"""

        wordpress_dir = os.path.join(article_dir, "wordpress")
        os.makedirs(wordpress_dir, exist_ok=True)

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

        if not os.path.exists(article_dir):
            return {
                "success": False,
                "error": f"記事ディレクトリが存在しません: {article_dir}"
            }

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

        publish_result = self.publisher.publish_article_with_images(article_dir)

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
