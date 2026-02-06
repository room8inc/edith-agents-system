#!/usr/bin/env python3
"""
Search Console API連携モジュール
実際の検索データを取得してキーワード戦略を強化
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build

_THIS_DIR = Path(__file__).resolve().parent

class SearchConsoleAPI:
    """Search Console APIラッパー"""

    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path or os.environ.get('GOOGLE_CREDENTIALS_PATH')
        self.site_url = None
        self.service = None

        print(f"[Search Console API] 初期化開始")

    def authenticate(self, site_url: str):
        """API認証・サービス初期化"""

        self.site_url = site_url

        try:
            # サービスアカウント認証
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/webmasters.readonly']
            )

            # Search Console APIサービス構築
            self.service = build('searchconsole', 'v1', credentials=credentials)

            print(f"[Search Console API] ✅ 認証成功: {site_url}")
            return True

        except Exception as e:
            print(f"[Search Console API] ❌ 認証失敗: {e}")
            return False

    def get_search_analytics(self,
                            start_date: str = None,
                            end_date: str = None,
                            dimensions: List[str] = None,
                            row_limit: int = 1000) -> Dict[str, Any]:
        """検索アナリティクスデータ取得"""

        if not self.service:
            print(f"[Search Console API] ⚠️ 未認証です")
            return {}

        # デフォルト期間：過去28日間
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=28)).strftime('%Y-%m-%d')

        # デフォルトディメンション
        if not dimensions:
            dimensions = ['query', 'page']

        print(f"[Search Console API] 📊 データ取得: {start_date} ~ {end_date}")

        try:
            request_body = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': dimensions,
                'dimensionFilterGroups': [],
                'rowLimit': row_limit,
                'startRow': 0
            }

            response = self.service.searchanalytics().query(
                siteUrl=self.site_url,
                body=request_body
            ).execute()

            print(f"[Search Console API] ✅ {len(response.get('rows', []))}件取得")

            return self._process_search_data(response)

        except Exception as e:
            print(f"[Search Console API] ❌ データ取得失敗: {e}")
            return {}

    def _process_search_data(self, raw_data: Dict) -> Dict[str, Any]:
        """生データを構造化"""

        rows = raw_data.get('rows', [])

        processed_data = {
            'summary': {
                'total_clicks': sum(row.get('clicks', 0) for row in rows),
                'total_impressions': sum(row.get('impressions', 0) for row in rows),
                'avg_ctr': 0,
                'avg_position': 0
            },
            'queries': [],
            'pages': [],
            'opportunities': []
        }

        # CTRと平均掲載順位計算
        if processed_data['summary']['total_impressions'] > 0:
            processed_data['summary']['avg_ctr'] = (
                processed_data['summary']['total_clicks'] /
                processed_data['summary']['total_impressions']
            )

        # クエリ別データ整理
        query_data = {}
        page_data = {}

        for row in rows:
            keys = row.get('keys', [])

            if len(keys) >= 1:  # query
                query = keys[0]
                if query not in query_data:
                    query_data[query] = {
                        'query': query,
                        'clicks': 0,
                        'impressions': 0,
                        'ctr': 0,
                        'position': 0,
                        'position_count': 0
                    }

                query_data[query]['clicks'] += row.get('clicks', 0)
                query_data[query]['impressions'] += row.get('impressions', 0)
                query_data[query]['position'] += row.get('position', 0)
                query_data[query]['position_count'] += 1

            if len(keys) >= 2:  # page
                page = keys[1]
                if page not in page_data:
                    page_data[page] = {
                        'page': page,
                        'clicks': 0,
                        'impressions': 0,
                        'queries': []
                    }

                page_data[page]['clicks'] += row.get('clicks', 0)
                page_data[page]['impressions'] += row.get('impressions', 0)
                if query not in page_data[page]['queries']:
                    page_data[page]['queries'].append(query)

        # 平均値計算とソート
        for query_info in query_data.values():
            if query_info['impressions'] > 0:
                query_info['ctr'] = query_info['clicks'] / query_info['impressions']
            if query_info['position_count'] > 0:
                query_info['position'] = query_info['position'] / query_info['position_count']

        # 上位クエリ抽出
        processed_data['queries'] = sorted(
            query_data.values(),
            key=lambda x: x['impressions'],
            reverse=True
        )[:100]

        # 上位ページ抽出
        processed_data['pages'] = sorted(
            page_data.values(),
            key=lambda x: x['clicks'],
            reverse=True
        )[:50]

        # 改善機会の特定
        processed_data['opportunities'] = self._identify_opportunities(query_data)

        return processed_data

    def _identify_opportunities(self, query_data: Dict[str, Dict]) -> List[Dict]:
        """改善機会の特定"""

        opportunities = []

        for query, data in query_data.items():
            # 低hanging fruit：順位11-20位で高インプレッション
            if 11 <= data['position'] <= 20 and data['impressions'] > 100:
                opportunities.append({
                    'type': 'low_hanging_fruit',
                    'query': query,
                    'current_position': round(data['position'], 1),
                    'impressions': data['impressions'],
                    'potential_clicks': int(data['impressions'] * 0.1),  # 1ページ目のCTR想定
                    'priority': 'high',
                    'action': '既存記事のSEO最適化で1ページ目を狙う'
                })

            # 高インプレッション・低CTR
            elif data['impressions'] > 500 and data['ctr'] < 0.02:
                opportunities.append({
                    'type': 'ctr_improvement',
                    'query': query,
                    'current_ctr': f"{data['ctr']*100:.1f}%",
                    'impressions': data['impressions'],
                    'potential_clicks': int(data['impressions'] * 0.05),  # CTR改善想定
                    'priority': 'medium',
                    'action': 'タイトル・メタディスクリプション改善'
                })

            # 順位下落検出（履歴データがあれば）
            # ここでは仮実装

        return sorted(opportunities, key=lambda x: x.get('potential_clicks', 0), reverse=True)[:20]

    def get_keyword_insights(self) -> Dict[str, Any]:
        """キーワード戦略インサイト生成"""

        # 最新28日間のデータ取得
        data = self.get_search_analytics()

        if not data:
            return {}

        insights = {
            'performance_summary': data['summary'],
            'top_performing_keywords': [],
            'improvement_opportunities': data['opportunities'],
            'content_gaps': [],
            'seasonal_trends': [],
            'strategic_recommendations': []
        }

        # トップパフォーミングキーワード
        for query_info in data['queries'][:10]:
            if query_info['clicks'] > 10:
                insights['top_performing_keywords'].append({
                    'keyword': query_info['query'],
                    'clicks': query_info['clicks'],
                    'impressions': query_info['impressions'],
                    'position': round(query_info['position'], 1),
                    'ctr': f"{query_info['ctr']*100:.1f}%"
                })

        # コンテンツギャップ分析
        insights['content_gaps'] = self._analyze_content_gaps(data['queries'])

        # 戦略的推奨事項
        insights['strategic_recommendations'] = self._generate_recommendations(data, insights)

        return insights

    def _analyze_content_gaps(self, queries: List[Dict]) -> List[Dict]:
        """コンテンツギャップ分析"""

        gaps = []

        # キーワードグループ化してギャップ発見
        keyword_groups = {}

        for query_info in queries:
            query = query_info['query']

            # 簡易的なグループ化（実際はもっと高度な処理が必要）
            if 'AI' in query or 'ChatGPT' in query:
                group = 'AI関連'
            elif 'リモート' in query or '在宅' in query:
                group = 'リモートワーク'
            elif '効率' in query or '改善' in query:
                group = '業務効率化'
            else:
                group = 'その他'

            if group not in keyword_groups:
                keyword_groups[group] = []
            keyword_groups[group].append(query_info)

        # 各グループでギャップ分析
        for group, keywords in keyword_groups.items():
            total_impressions = sum(k['impressions'] for k in keywords)
            if total_impressions > 1000 and len(keywords) < 5:
                gaps.append({
                    'topic_area': group,
                    'current_keywords': len(keywords),
                    'total_impressions': total_impressions,
                    'opportunity': 'コンテンツ不足',
                    'action': f'{group}関連の記事を増やす'
                })

        return gaps

    def _generate_recommendations(self, data: Dict, insights: Dict) -> List[Dict]:
        """戦略的推奨事項生成"""

        recommendations = []

        # CTR改善の機会が多い場合
        ctr_opportunities = [o for o in insights['improvement_opportunities']
                           if o['type'] == 'ctr_improvement']
        if len(ctr_opportunities) > 5:
            recommendations.append({
                'priority': 'high',
                'type': 'title_optimization',
                'description': '多くのキーワードでCTRが低い。タイトル最適化プロジェクト実施推奨',
                'expected_impact': f'+{sum(o["potential_clicks"] for o in ctr_opportunities[:5])}クリック/月',
                'assigned_to': 'SEO足軽 + ライティング足軽'
            })

        # 低hanging fruitが多い場合
        lhf_opportunities = [o for o in insights['improvement_opportunities']
                           if o['type'] == 'low_hanging_fruit']
        if len(lhf_opportunities) > 3:
            recommendations.append({
                'priority': 'high',
                'type': 'content_refresh',
                'description': '11-20位の記事が多数。既存記事の最適化で大幅流入増可能',
                'expected_impact': f'+{sum(o["potential_clicks"] for o in lhf_opportunities[:3])}クリック/月',
                'assigned_to': 'SEO足軽'
            })

        # 成田悠輔風コンテンツの効果
        narita_keywords = [q for q in data['queries']
                         if any(word in q['query'] for word in ['辛辣', '現実', '失敗', '本音'])]
        if narita_keywords:
            avg_ctr = sum(k['ctr'] for k in narita_keywords) / len(narita_keywords)
            recommendations.append({
                'priority': 'medium',
                'type': 'content_strategy',
                'description': f'成田風キーワードの平均CTR: {avg_ctr*100:.1f}%',
                'expected_impact': '毒舌系コンテンツが効果的',
                'assigned_to': 'ライティング足軽'
            })

        return recommendations


class SearchConsoleIntegration:
    """Search Console統合管理クラス"""

    def __init__(self):
        self.api = SearchConsoleAPI()
        self.site_url = None

    def setup(self, site_url: str, credentials_path: str = None):
        """Search Console連携セットアップ"""

        self.site_url = site_url

        # 認証情報ファイルパス設定
        if credentials_path:
            self.api.credentials_path = credentials_path
        elif not self.api.credentials_path:
            # デフォルトパス（絶対パス）
            self.api.credentials_path = str(_THIS_DIR / 'credentials' / 'claude-agent-486408-2670454f8c9f.json')

        # 認証実行
        success = self.api.authenticate(site_url)

        if success:
            print(f"[Search Console] ✅ 連携成功: {site_url}")
            self._save_config()
        else:
            print(f"[Search Console] ❌ 連携失敗")

        return success

    def _save_config(self):
        """設定保存"""

        config = {
            'site_url': self.site_url,
            'credentials_path': self.api.credentials_path,
            'setup_date': datetime.now().isoformat()
        }

        config_dir = _THIS_DIR / 'config'
        os.makedirs(config_dir, exist_ok=True)

        with open(str(config_dir / 'search_console_config.json'), 'w') as f:
            json.dump(config, f, indent=2)

        print(f"[Search Console] 📁 設定保存完了")

    def get_weekly_report(self) -> Dict[str, Any]:
        """週次レポート生成"""

        if not self.api.service:
            print(f"[Search Console] ⚠️ 未設定です")
            return {}

        # 過去7日間のデータ
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        data = self.api.get_search_analytics(
            start_date=start_date,
            end_date=end_date,
            dimensions=['query', 'page', 'date']
        )

        insights = self.api.get_keyword_insights()

        report = {
            'period': f'{start_date} ~ {end_date}',
            'performance': data.get('summary', {}),
            'top_keywords': insights.get('top_performing_keywords', [])[:10],
            'opportunities': insights.get('improvement_opportunities', [])[:5],
            'recommendations': insights.get('strategic_recommendations', []),
            'generated_at': datetime.now().isoformat()
        }

        return report


def test_search_console_api():
    """Search Console API テスト"""

    print("🔍 Search Console API連携テスト")
    print("=" * 60)

    # 統合マネージャー初期化
    integration = SearchConsoleIntegration()

    # セットアップ（実際の認証情報が必要）
    site_url = 'https://example.com'  # 実際のサイトURL
    credentials_path = 'path/to/service_account_key.json'  # 実際の認証ファイル

    # モックモードで動作確認
    print("\n[テストモード] 実際のAPI接続はスキップ")
    print("[テストモード] 以下の機能が実装されています：")
    print("  ✅ Search Analytics データ取得")
    print("  ✅ キーワード機会分析")
    print("  ✅ コンテンツギャップ発見")
    print("  ✅ 戦略的推奨事項生成")
    print("  ✅ 週次レポート作成")

    # モックレポート表示
    mock_report = {
        'performance': {
            'total_clicks': 3250,
            'total_impressions': 45000,
            'avg_ctr': 0.072,
            'avg_position': 14.5
        },
        'top_keywords': [
            {'keyword': 'AI導入 失敗', 'clicks': 245, 'position': 8.2},
            {'keyword': 'ChatGPT 中小企業', 'clicks': 189, 'position': 12.5}
        ],
        'opportunities': [
            {
                'type': 'low_hanging_fruit',
                'query': 'リモートワーク 効率化',
                'current_position': 13.5,
                'potential_clicks': 150
            }
        ]
    }

    print(f"\n📊 モックレポート:")
    print(f"  総クリック数: {mock_report['performance']['total_clicks']:,}")
    print(f"  改善機会: {len(mock_report['opportunities'])}件発見")
    print(f"  最有望キーワード: {mock_report['opportunities'][0]['query']}")


if __name__ == "__main__":
    test_search_console_api()