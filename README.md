# EDITH Multi-Agent System

**統括管理AI「EDITH」によるマルチエージェントシステム**

## 🚀 概要

このシステムは、統括管理AI「EDITH」を中心とした専門部門エージェントによるマルチエージェント組織です。

```
EDITH（統括管理）
    ↓ 指示・管理
┌─────────────────────────────────────┐
│ 専門部門Agent（各部門独立運営）           │
├─ edith_corp/                         │
│  ├─ blog_department/    # ブログ部門   │
│  ├─ strategic_memory/   # 戦略記憶     │
│  └─ edith_ceo.py       # CEO管理      │
├─ edith_system/         # EDITH本体     │
└─ agent_hierarchy_system.py # 階層管理  │
```

## 📁 ディレクトリ構造

```
000AGENTS/
├── edith_corp/              # EDITH Corporation
│   ├── blog_department/     # ブログ部門（完全仕様書体制）
│   │   ├── articles/        # 完成記事保管
│   │   ├── image_generation/ # 画像生成システム
│   │   ├── wordpress_posting/ # WordPress投稿
│   │   ├── seo_specialist_ashigaru/ # SEO専門
│   │   └── *.md            # 厳格な仕様書群
│   ├── strategic_memory/    # 戦略記憶システム
│   └── edith_ceo.py        # CEO管理システム
├── edith_system/            # EDITH本体システム
├── agent_hierarchy_system.py # エージェント階層管理
├── edith_command_center.py  # コマンドセンター
└── .env.local              # 環境変数（Git除外）
```

## 🎯 主要機能

### ブログ部門 (`edith_corp/blog_department/`)
- **記事作成**: 構造化された記事生成
- **画像生成**: Pillowベースプレースホルダー（Gemini API制限対応）
- **SEO最適化**: 専門エージェントによる最適化
- **WordPress投稿**: 自動投稿システム
- **仕様書管理**: 厳格な仕様書体制

### システム管理
- **階層管理**: エージェント間の指示系統
- **記憶システム**: 戦略・知識の永続化
- **相対パス**: ポータブルなシステム構成

## 🔧 セットアップ

### 1. 環境変数設定
```bash
cp .env.example .env.local
# 必要なAPIキーを.env.localに設定
```

### 2. 必要な依存関係
```bash
pip install pillow python-dotenv requests
```

### 3. ブログ記事生成テスト
```bash
cd edith_corp/blog_department/image_generation/
python3 simple_image_generator.py
```

## 📋 仕様書体制

ブログ部門は厳格な仕様書管理を採用：

1. **SPECIFICATION_ENFORCEMENT_RULES.md** - 仕様書管理の絶対ルール
2. **CONTENT_MARKETING_SPECIFICATIONS.md** - 部門統括仕様
3. **IMAGE_GENERATION_SPECIFICATIONS.md** - 画像生成仕様
4. **FILE_STRUCTURE_SPECIFICATION.md** - ファイル構成仕様

**重要**: 仕様変更時は該当仕様書の即座更新が絶対義務

## 🚨 重要な制限事項

### 画像生成について
- **Gemini API**: 画像生成機能なし（テキスト生成のみ）
- **現在の対策**: Pillowライブラリによるプレースホルダー生成
- **将来の対策**: Imagen/DALL-E/Stable Diffusion API導入予定

### セキュリティ
- `.env.local`ファイルはGitに含まれません
- APIキー等の機密情報は適切に管理
- WordPress認証情報の保護

## 🔄 Git管理

### ブランチ戦略
```bash
main              # 安定版
feature/*         # 新機能開発
experiment/*      # 実験的変更
fix/*            # バグ修正
```

### コミット規則
```bash
feat: 新機能追加
fix: バグ修正
docs: ドキュメント更新
style: コードスタイル変更
refactor: リファクタリング
```

## 👥 エージェント組織

### 統括管理
- **EDITH**: 戦略判断・部門調整・進捗管理

### 専門部門
- **ブログ部門**: コンテンツ作成・SEO・投稿管理
- **戦略企画**: 事業戦略・市場分析
- **技術開発**: システム構築・API統合

## 📞 サポート

### 緊急時復旧
- `EMERGENCY_RECOVERY_PROTOCOL.md`を参照
- 仕様書を基準とした復旧手順

### 問い合わせ
- Issues: GitHub Issues
- 仕様書: 各部門の仕様書を参照

---

**🤖 Generated with Claude Code**

**管理者**: EDITH Corporation
**最終更新**: 2026-02-05