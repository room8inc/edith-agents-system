# 安全プロトコル - セッション破壊の防止

## 🚨 危険な操作の前に必ずやること

### 1. 現在の状態を保存
```bash
git add .
git commit -m "save: 作業中の状態を保存"
git push
```

### 2. 実験用ブランチ作成
```bash
git checkout -b experiment/危険な操作名
```

### 3. 危険な操作の例
- ❌ 壊れた画像ファイルを読み込む
- ❌ 大きすぎるファイルを読み込む
- ❌ 無限ループの可能性があるスクリプト実行
- ❌ 不明なバイナリファイルを開く

## 🔄 セッションが壊れた場合の復旧

### 新しいセッションで実行
```bash
# 1. リポジトリをクローン
git clone https://github.com/あなた/edith-blog-department.git
cd edith-blog-department

# 2. 最後の安全な状態を確認
git log --oneline -10

# 3. 安全なコミットに戻る
git checkout main  # または特定のコミットID

# 4. 危険なファイルを確認（読み込まずに）
ls -la 問題のディレクトリ/
file 問題のファイル  # ファイルタイプだけ確認

# 5. 危険なファイルを削除または移動
rm 壊れたファイル
# または
mv 壊れたファイル /tmp/
```

## 📝 コミット戦略

### こまめにコミット
```bash
# 動作確認できた瞬間
git commit -m "feat: 画像生成成功"

# 危険な操作の前
git commit -m "save: 実験前の安全な状態"

# 仕様書更新時
git commit -m "docs: 仕様書更新"
```

### タグで重要な地点をマーク
```bash
# 完全に動作する状態にタグ
git tag -a stable-v1 -m "安定版: すべて正常動作"
git push --tags

# 後で戻れる
git checkout stable-v1
```

## 🛡️ 予防的措置

### 画像ファイルの安全確認
```bash
# 読み込む前に確認
file image.png
# 出力例: PNG image data, 1920 x 1080

# サイズ確認
ls -lh image.png
# 1MB以下なら安全

# 壊れていないか確認（読み込まずに）
python3 -c "from PIL import Image; Image.open('image.png').verify()"
```

### .gitignoreに危険なファイルを追加
```bash
# 壊れたファイル
broken_files/
*.corrupt
*.broken

# 大きすぎるファイル
*.mp4
*.zip
```

## 💡 ベストプラクティス

1. **朝一番でpush**
   ```bash
   git push  # 昨日の作業を確実に保存
   ```

2. **昼休み前にcommit**
   ```bash
   git commit -am "save: 午前の作業"
   ```

3. **実験は必ずブランチで**
   ```bash
   git checkout -b experiment/test
   ```

4. **終業時にpush**
   ```bash
   git push origin main
   ```

---

**重要：** このプロトコルに従えば、セッションが壊れても必ず復旧できます。