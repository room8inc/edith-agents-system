# Search Console API 設定ガイド

## 1. API キーの設定場所

### 方法1: 環境変数で設定（推奨）
```bash
export GOOGLE_CREDENTIALS_PATH="/path/to/your/service_account_key.json"
```

### 方法2: 設定ファイルで指定
```python
# 実行時に直接指定
from search_console_api import SearchConsoleIntegration

integration = SearchConsoleIntegration()
integration.setup(
    site_url='https://your-site.com',
    credentials_path='/path/to/service_account_key.json'
)
```

### 方法3: デフォルトパスに配置
```
edith_corp/
└── blog_department/
    └── search_console/
        └── credentials/
            └── claude-agent-486408-2670454f8c9f.json  # ← 現在のファイル
```

## 2. Google Cloud Console での準備

### Step 1: サービスアカウント作成
1. [Google Cloud Console](https://console.cloud.google.com) にアクセス
2. プロジェクト作成 or 選択
3. 「IAMと管理」→「サービスアカウント」
4. 「サービスアカウントを作成」
5. 名前: `search-console-reader` など

### Step 2: Search Console API 有効化
1. 「APIとサービス」→「ライブラリ」
2. 「Google Search Console API」を検索
3. 「有効にする」をクリック

### Step 3: 認証キー作成
1. サービスアカウント詳細ページ
2. 「キー」タブ
3. 「鍵を追加」→「新しい鍵を作成」
4. JSON形式を選択
5. ダウンロードされたJSONファイルを保存

### Step 4: Search Console でサイト所有者として追加
1. [Google Search Console](https://search.google.com/search-console) にアクセス
2. 対象プロパティを選択
3. 「設定」→「ユーザーと権限」
4. 「ユーザーを追加」
5. サービスアカウントのメールアドレスを追加
   （例: `search-console@project-id.iam.gserviceaccount.com`）
6. 権限: 「フル」または「制限付き」

## 3. 実装での使用例

```python
# SEO足軽での自動接続
from seo_agent import SEOSpecialistAshigaru

# 環境変数が設定されていれば自動で接続
seo = SEOSpecialistAshigaru()

# または明示的に設定
seo.search_console.setup(
    site_url='https://your-blog.com',
    credentials_path='/Users/you/keys/search_console_key.json'
)

# 実データを使った分析
keyword_analysis = seo.analyze_keyword_opportunities("AI導入")
# → Search Console実データが自動的に使われる
```

## 4. セキュリティ注意事項

⚠️ **重要**:
- `search_console_key.json` は絶対にGitにコミットしない
- `.gitignore` に追加:
  ```
  credentials/
  *.json
  *_key.json
  ```

## 5. テスト実行

```bash
cd blog_department/search_console
python search_console_api.py

# または足軽経由でテスト
cd ../seo_specialist_ashigaru
python seo_agent.py
```

## トラブルシューティング

### エラー: "認証失敗"
- サービスアカウントがSearch Consoleに追加されているか確認
- JSONファイルのパスが正しいか確認

### エラー: "API not enabled"
- Google Cloud ConsoleでSearch Console APIが有効化されているか確認

### データが取得できない
- Search Consoleにデータが蓄積されているか確認（最低3日必要）
- サイトURLが正しいか確認（`https://` を含む完全なURL）