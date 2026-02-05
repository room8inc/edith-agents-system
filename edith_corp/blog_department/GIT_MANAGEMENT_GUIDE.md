# Git版数管理ガイド

**作成日:** 2026-02-05
**リポジトリ:** ./ (blog_department/)

## 🔄 基本的な使い方

### 現在の状態を確認
```bash
git status
```

### 変更履歴を見る
```bash
git log --oneline -10
```

### 変更内容を確認
```bash
git diff
```

## 📝 コミットの作り方

### 1. 変更をステージング
```bash
# すべての変更を追加
git add -A

# 特定ファイルのみ
git add ファイル名
```

### 2. コミット作成
```bash
git commit -m "変更内容の説明"
```

## 🌿 ブランチの使い方

### ブランチ作成・切り替え
```bash
# 新機能開発用ブランチ作成
git checkout -b feature/画像生成API追加

# 実験用ブランチ作成
git checkout -b experiment/gemini-api-test

# バグ修正用ブランチ作成
git checkout -b fix/画像生成エラー
```

### ブランチ一覧
```bash
git branch -a
```

### メインブランチに戻る
```bash
git checkout main
```

### ブランチをマージ
```bash
git checkout main
git merge feature/画像生成API追加
```

## 🏷️ タグ（バージョン）管理

### バージョンタグを付ける
```bash
# v1.0.0 のようなタグを作成
git tag -a v1.0.0 -m "初期リリース: 仕様書体制確立"
git tag -a v1.0.1 -m "バグ修正: 画像生成エラー対応"
git tag -a v1.1.0 -m "機能追加: DALL-E API対応"
```

### タグ一覧
```bash
git tag
```

## 📚 重要なコミット履歴

### 2026-02-05
- `92edc1b` 初期コミット: ブログ部門システムの完全仕様書化とクリーンアップ完了

## 🔄 仕様変更時のワークフロー

### 1. 新しいブランチを作成
```bash
git checkout -b feature/新機能名
```

### 2. 仕様書を更新
- 必ず仕様書を先に更新
- SPECIFICATION_ENFORCEMENT_RULES.md に従う

### 3. 実装を変更
- 仕様書に基づいて実装

### 4. テスト
```bash
python3 テストスクリプト.py
```

### 5. コミット
```bash
git add -A
git commit -m "feat: 新機能の説明

- 仕様書更新
- 実装完了
- テスト済み"
```

### 6. メインブランチにマージ
```bash
git checkout main
git merge feature/新機能名
```

## 🚨 緊急時の対応

### 直前のコミットを取り消し（まだpushしていない場合）
```bash
git reset --soft HEAD~1
```

### 特定のファイルを前の状態に戻す
```bash
git checkout HEAD -- ファイル名
```

### 特定のコミットまで戻る
```bash
git log --oneline  # コミットIDを確認
git checkout コミットID
```

## 📋 コミットメッセージの規則

### プレフィックス
- `feat:` 新機能追加
- `fix:` バグ修正
- `docs:` ドキュメント更新
- `style:` コードスタイル変更
- `refactor:` リファクタリング
- `test:` テスト追加・修正
- `chore:` その他の変更

### 例
```bash
git commit -m "feat: DALL-E API画像生成機能を追加

- OpenAI APIキー設定追加
- dalle_image_generator.py作成
- 仕様書更新完了"
```

## 🔍 便利なコマンド

### 変更されたファイル一覧
```bash
git diff --name-only
```

### 特定ファイルの変更履歴
```bash
git log -p ファイル名
```

### 誰がいつ変更したか確認
```bash
git blame ファイル名
```

## 💡 ベストプラクティス

1. **こまめにコミット**
   - 大きな変更は分割してコミット
   - 1コミット1機能

2. **仕様書ファースト**
   - 必ず仕様書を先に更新
   - 実装は仕様書に従う

3. **ブランチ活用**
   - 実験的な変更は別ブランチで
   - mainブランチは常に動作する状態を保つ

4. **タグ活用**
   - 重要なマイルストーンにタグを付ける
   - セマンティックバージョニング（v1.0.0）を使用

---

**注意:** このリポジトリはローカル管理です。GitHubなどのリモートリポジトリに接続する場合は、別途設定が必要です。