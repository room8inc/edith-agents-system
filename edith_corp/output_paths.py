"""
EDITH Corporation - 生成物出力先の中央パス設定
全モジュールがここから出力先パスをimportする。
パスを変えたい場合はこのファイル1つだけ変更すればよい。
"""

from pathlib import Path

OUTPUT_ROOT = Path.home() / "Documents" / "edith_output"
BLOG_ARTICLES_DIR = OUTPUT_ROOT / "blog" / "articles"
BLOG_ARTICLES_INDEX = OUTPUT_ROOT / "blog" / "articles_index.json"
REPORTS_DIR = OUTPUT_ROOT / "reports"
BRIEFS_DIR = OUTPUT_ROOT / "briefs"


def ensure_dirs():
    """出力先ディレクトリを自動作成"""
    BLOG_ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)
