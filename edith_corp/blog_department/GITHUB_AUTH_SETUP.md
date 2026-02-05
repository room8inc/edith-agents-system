# GitHub認証設定ガイド

## 🔐 Personal Access Token（推奨）を使った設定

### 1. GitHubでトークンを作成

1. GitHubにログイン
2. 右上のプロフィール → **Settings**
3. 左メニューの一番下 → **Developer settings**
4. **Personal access tokens** → **Tokens (classic)**
5. **Generate new token** → **Generate new token (classic)**

### 2. トークンの設定

- **Note**: `edith-blog-department`（わかりやすい名前）
- **Expiration**: 90 days または No expiration
- **Select scopes**:
  - ✅ repo（すべてチェック）
  - ✅ workflow（オプション）

6. **Generate token** をクリック
7. **トークンをコピー**（この画面でしか見れません！）

### 3. トークンを使ってpush

```bash
# 方法1: URLに含める（一時的）
git remote set-url origin https://あなたのユーザー名:トークン@github.com/room8inc/edith-blog-department.git

# 例:
git remote set-url origin https://room8inc:ghp_xxxxxxxxxxxxx@github.com/room8inc/edith-blog-department.git

# その後push
git push -u origin main
```

### 4. より安全な方法（推奨）

```bash
# 方法2: 認証情報をキャッシュ
git config --global credential.helper cache

# pushする（ユーザー名とパスワードを聞かれる）
git push -u origin main

# Username: あなたのGitHubユーザー名
# Password: 作成したトークン（パスワードではなくトークン）
```

## 🔑 SSHキーを使った設定（より安全）

### 1. SSHキー生成
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# Enterを3回押す（パスフレーズなし）
```

### 2. 公開鍵をコピー
```bash
cat ~/.ssh/id_ed25519.pub
```

### 3. GitHubに登録
1. GitHub → Settings → SSH and GPG keys
2. **New SSH key**
3. Title: `EDITH Mac`
4. Key: コピーした内容を貼り付け
5. **Add SSH key**

### 4. リモートURLをSSHに変更
```bash
git remote set-url origin git@github.com:room8inc/edith-blog-department.git

# 確認
git remote -v

# push
git push -u origin main
```

## 🚀 どちらを選ぶべきか？

### Personal Access Token
- ✅ 設定が簡単
- ✅ すぐ使える
- ⚠️ トークンの有効期限がある
- ⚠️ トークンを安全に管理する必要

### SSH
- ✅ より安全
- ✅ 一度設定すれば永続的
- ⚠️ 初期設定がやや複雑

## 📝 次のステップ

トークンまたはSSHキーを設定したら：

```bash
# 最初のpush
git push -u origin main

# 以降は簡単
git push
```

---

**重要**: トークンは絶対に他人と共有しないでください。