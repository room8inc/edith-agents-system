# 全部門共通 緊急時復旧プロトコル

**Last Updated:** 2026-02-04
**Version:** 1.0
**適用対象:** EDITH + 全部門Agent

## ⚠️ セッション切断緊急対応（必須暗記）

### 🚨 第一優先: 状況把握（60秒以内）

```bash
# 現在地確認
pwd

# マスター仕様書確認（最重要）
cat /Users/tsuruta/Documents/000AGENTS/edith_corp/EDITH_MASTER_SPECIFICATIONS.md

# 部門別仕様書確認
ls /Users/tsuruta/Documents/000AGENTS/edith_corp/*/SPECIFICATIONS.md
```

### 🔍 第二優先: 作業状況復旧（60秒以内）

```bash
# 最新のファイル変更確認
find /Users/tsuruta/Documents/000AGENTS/edith_corp -type f -name "*.md" -o -name "*.json" | xargs ls -la | sort -k6,7

# 進行中の可能性が高いプロジェクト確認
ls -la /Users/tsuruta/Documents/000AGENTS/edith_corp/*/
```

### 📋 第三優先: ユーザー要求確認（30秒以内）

1. **直前の会話内容確認**
2. **未完了タスクの特定**
3. **緊急度・優先度判断**

---

## 🏢 部門別緊急復旧手順

### EDITH（統括管理）復旧手順
1. **EDITH_MASTER_SPECIFICATIONS.md 確認**
2. **全部門仕様書の整合性確認**
3. **TodoList復旧・作成**
4. **部門Agent起動・指示**

### コンテンツマーケ部門復旧手順
```bash
# 仕様書確認
cat /Users/tsuruta/Documents/000AGENTS/edith_corp/blog_department/CONTENT_MARKETING_SPECIFICATIONS.md

# 進行中記事確認
ls -la /Users/tsuruta/Documents/000AGENTS/edith_corp/blog_department/articles/

# 最新記事状況
find /Users/tsuruta/Documents/000AGENTS/edith_corp/blog_department/articles -name "article.md" -exec stat -f "%m %N" {} \; | sort -n | tail -5
```

### 戦略企画部門復旧手順
```bash
# 仕様書確認（作成予定）
cat /Users/tsuruta/Documents/000AGENTS/edith_corp/room8_strategy_department/STRATEGY_SPECIFICATIONS.md

# 進行中プロジェクト確認
ls -la /Users/tsuruta/Documents/000AGENTS/edith_corp/room8_strategy_department/
```

### 技術開発部門復旧手順
```bash
# 仕様書確認（作成予定）
cat /Users/tsuruta/Documents/000AGENTS/edith_corp/tech_department/TECH_SPECIFICATIONS.md

# 開発中システム確認
find /Users/tsuruta/Documents/000AGENTS -name "*.py" -o -name "*.js" -o -name "*.json" | grep -v node_modules
```

### 分析部門復旧手順
```bash
# 仕様書確認（作成予定）
cat /Users/tsuruta/Documents/000AGENTS/edith_corp/analysis_department/ANALYSIS_SPECIFICATIONS.md

# 分析データ確認
find /Users/tsuruta/Documents/000AGENTS/edith_corp -name "*analytics*" -o -name "*data*" -o -name "*report*"
```

---

## 🚨 緊急事態別対応マトリックス

### ケース1: ファイル・ディレクトリが見つからない
```bash
# 全体検索
find /Users/tsuruta/Documents -name "*keyword*" 2>/dev/null

# ディレクトリ構造確認
find /Users/tsuruta/Documents/000AGENTS -type d | head -20

# 最近の変更確認
find /Users/tsuruta/Documents/000AGENTS -type f -newermt "2026-02-04" | head -10
```

### ケース2: Task Agentが応答しない
1. **直接実行への切り替え**
2. **該当部門仕様書の直接参照**
3. **手動でのタスク実行**
4. **EDITHによる代替判断**

### ケース3: 仕様書と現実が不一致
1. **現実の状況を詳細調査**
2. **仕様書の即座更新**
3. **関連部門への変更通達**
4. **ユーザーへの状況報告**

### ケース4: 作業途中でセッション切断
1. **最後の保存状況確認**
2. **部分完成物の評価**
3. **継続 vs 再開始の判断**
4. **品質保証の再実施**

---

## 📁 重要ファイルの場所（暗記必須）

### 最優先確認ファイル
```
/Users/tsuruta/Documents/000AGENTS/edith_corp/EDITH_MASTER_SPECIFICATIONS.md
/Users/tsuruta/Documents/000AGENTS/edith_corp/blog_department/CONTENT_MARKETING_SPECIFICATIONS.md
/Users/tsuruta/Documents/000AGENTS/edith_corp/EMERGENCY_RECOVERY_PROTOCOL.md（本ファイル）
```

### 作業状況確認場所
```
/Users/tsuruta/Documents/000AGENTS/edith_corp/blog_department/articles/
/Users/tsuruta/Documents/000AGENTS/edith_corp/strategic_memory/
/Users/tsuruta/Documents/000AGENTS/edith_corp/missions/
```

### 設定・データファイル
```
/Users/tsuruta/Documents/000AGENTS/edith_corp/blog_department/series_management/series_management/series_database.json
/Users/tsuruta/Documents/000AGENTS/edith_corp/blog_department/memory_system/knowledge_base/strategies/current_strategy.json
/Users/tsuruta/Documents/000AGENTS/edith_corp/strategic_memory/memory_bank.json
```

---

## 🔄 復旧後の必須アクション

### 1. TodoList復旧（必須）
- 直前の作業状況をTodoWriteで記録
- 未完了タスクの継続・再開始判断
- 新たな優先度設定

### 2. 品質確認（必須）
- 部分完成物の品質評価
- 仕様書との適合性確認
- ユーザー要求との一致確認

### 3. 継続・復旧判断（必須）
- 作業継続 vs 再開始の判断
- 関連部門への影響確認
- スケジュール調整の必要性判断

### 4. ユーザー報告（必須）
```
Status: 緊急復旧完了
What happened: [切断・問題の内容]
Recovery actions: [実施した復旧措置]
Current situation: [現在の状況]
Impact: [作業への影響]
Next steps: [今後の予定]
```

---

## ⚠️ 絶対禁止事項

### やってはいけないこと
- [ ] 推測での作業継続（必ず仕様書確認）
- [ ] 口頭指示への依存（必ず文書確認）
- [ ] 適当なディレクトリでの作業
- [ ] 部分的な情報での判断
- [ ] ユーザーへの不正確な報告

### 必ずやること
- [x] 仕様書の最初確認
- [x] ファイル場所の正確把握
- [x] 作業状況の詳細調査
- [x] TodoListの作成・更新
- [x] ユーザーへの正確な状況報告

---

## 🚨 仕様変更時の絶対更新ルール

### 仕様変更を認識した瞬間→即座実行（例外なし）

#### 更新対象の仕様書
1. **該当部門の仕様書** - 変更内容の詳細記録
2. **EDITH_MASTER_SPECIFICATIONS.md** - 組織全体への影響記録
3. **本ファイル（EMERGENCY_RECOVERY_PROTOCOL.md）** - 復旧手順の更新

#### 絶対禁止
- **「後で更新」** ❌
- **「次回更新」** ❌
- **「セッション終了後に更新」** ❌
- **口頭・記憶による仕様管理** ❌

#### 更新完了まで他作業停止
仕様書更新が完了するまで、他のすべての作業を停止する。

---

**🚨 このファイルは全Agent共通の生命線**
**セッション開始時に必ず確認すること**
**仕様変更時は即座に更新すること（例外なし）**