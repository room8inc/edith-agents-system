# EDITH階層型Agent組織システム

## ディレクトリ構造

```
edith_system/
├── edith_commander.py          # EDITH将軍（統括指揮）
├── karo/                       # 家老（戦略・企画調整）
│   └── strategy_agent.py       # 戦略Agent
├── ashigaru/                   # 足軽（専門実行部隊）
│   ├── content/                # コンテンツ関連
│   │   └── content_agent.py    # 記事作成Agent
│   ├── seo/                    # SEO関連
│   │   └── seo_agent.py        # SEO最適化Agent
│   ├── image/                  # 画像関連
│   │   └── image_agent.py      # 画像生成Agent
│   ├── wordpress/              # WordPress関連
│   │   └── wordpress_agent.py  # WordPress投稿Agent
│   ├── quality/                # 品質管理
│   │   └── quality_agent.py    # 品質管理Agent
│   ├── research/               # 市場調査
│   │   └── research_agent.py   # 調査Agent
│   ├── analytics/              # データ分析
│   │   └── analytics_agent.py  # 分析Agent
│   └── operations/             # 運営管理
│       └── operations_agent.py # 運営Agent
├── missions/                   # ミッション記録
├── reports/                    # 実行報告
└── README.md                   # このファイル
```

## 指揮系統

```
EDITH（将軍・統括指揮）
    ↓
戦略Agent（家老・企画調整）
    ↓
専門Agent群（足軽・実行部隊）
├─ コンテンツAgent
├─ SEOAgent
├─ 画像企画Agent
├─ WordPress投稿Agent
├─ 品質管理Agent
├─ 市場調査Agent
├─ データ分析Agent
└─ 運営Agent
```

## 使用方法

### 基本実行
```bash
cd edith_system
python3 edith_commander.py
```

### 日刊ブログ生産
```bash
python3 -c "
from edith_commander import EDITHCommander
edith = EDITHCommander()
edith.execute_daily_mission('daily_blog')
"
```

## ファイル役割

- **edith_commander.py**: 全体統括・意思決定
- **karo/strategy_agent.py**: ミッション分解・戦術立案
- **ashigaru/xxx/xxx_agent.py**: 各専門分野の実行
- **missions/**: 作戦計画保存
- **reports/**: 実行結果報告

## 開発状況

- ✅ 階層構造設計完了
- ✅ 基本指揮系統実装
- ⚠️ 各Agent内部実装（Task Tool連携待ち）
- ⚠️ 実際のAPI連携実装待ち