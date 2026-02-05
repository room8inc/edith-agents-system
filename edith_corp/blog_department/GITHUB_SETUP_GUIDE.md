# GitHub接続ガイド

## GitHubに接続する方法

### 1. GitHubアカウント作成
1. https://github.com にアクセス
2. Sign up でアカウント作成

### 2. 新しいリポジトリ作成
GitHubで「New repository」をクリック
- Repository name: `edith-blog-department`
- Private または Public を選択
- **重要**: 「Initialize this repository with a README」のチェックは外す

### 3. ローカルリポジトリとGitHubを接続

```bash
# GitHubのリポジトリURLを設定（例）
git remote add origin https://github.com/あなたのユーザー名/edith-blog-department.git

# または SSH を使う場合
git remote add origin git@github.com:あなたのユーザー名/edith-blog-department.git

# 確認
git remote -v
```

### 4. 最初のプッシュ

```bash
# メインブランチをプッシュ
git push -u origin main

# タグもプッシュ
git push --tags
```

### 5. 以降の使い方

```bash
# 変更をGitHubに送る
git push

# GitHubから最新を取得
git pull

# 他のブランチをプッシュ
git push origin ブランチ名
```

## 🔐 認証設定

### HTTPS の場合
```bash
# ユーザー名とパスワード（またはトークン）を入力
# 毎回聞かれるのが面倒な場合：
git config --global credential.helper cache
```

### SSH の場合（推奨）
```bash
# SSHキー生成
ssh-keygen -t ed25519 -C "your_email@example.com"

# 公開鍵をコピー
cat ~/.ssh/id_ed25519.pub

# GitHubの Settings > SSH and GPG keys に登録
```

## ⚠️ 注意事項

### 絶対にプッシュしてはいけないファイル

1. **APIキー・パスワード**
   - .env.local
   - credentials/*.json

2. **個人情報**
   - 実際の顧客データ
   - 本番環境の設定

### .gitignore の確認
```bash
# .gitignore に含まれているか確認
cat .gitignore | grep -E "\.env|credentials"
```

## 💡 GitHub を使うメリット

1. **バックアップ**
   - PCが壊れてもデータは安全
   - どこからでもアクセス可能

2. **履歴の可視化**
   - ブラウザで変更履歴を確認
   - グラフで開発状況を把握

3. **共同作業**（将来的に）
   - 他の開発者と協力
   - コードレビュー
   - Issue でタスク管理

4. **自動化**（GitHub Actions）
   - コミット時に自動テスト
   - 自動デプロイ

## 🚀 次のステップ

### Private リポジトリ（推奨）
- 自分だけがアクセス可能
- APIキーなどの漏洩リスクが低い
- 無料で使える

### Public リポジトリ
- 誰でも見られる
- オープンソースプロジェクト向け
- **重要**: 機密情報は絶対に含めない

---

**判断**:
- 個人的なバックアップ目的 → Private リポジトリ
- コードを公開したい → Public リポジトリ（機密情報を除外後）