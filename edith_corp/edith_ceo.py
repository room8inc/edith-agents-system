#!/usr/bin/env python3
"""
EDITH CEO（最高経営責任者） - 動的組織管理システム
事業部の新設・評価・改革を動的に実行
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class EDITHCorporation:
    """EDITH Corporation - 動的組織管理CEO"""

    def __init__(self):
        self.position = "CEO"
        self.name = "EDITH"
        self.company_root = "/Users/tsuruta/Documents/000AGENTS/edith_corp"
        self.departments = {}

        self._initialize_organization()
        print(f"[{self.name} CEO] コーポレーション起動完了")

    def _initialize_organization(self):
        """組織初期化"""

        # 事業部登録
        self.departments = {
            "blog_department": {
                "name": "ブログ事業部",
                "karo": "ブログ事業部長",
                "ashigaru_units": [
                    "research", "keyword_strategy", "structure",
                    "writing", "image_generation", "wordpress_posting"
                ],
                "performance": {"score": 85, "status": "好調"},
                "budget_allocation": 40
            },
            "room8_strategy_department": {
                "name": "Room8戦略事業部",
                "karo": "Room8戦略部長",
                "ashigaru_units": [
                    "market_research", "community_planning", "pricing_strategy",
                    "marketing_plan", "partnership", "growth_analysis"
                ],
                "performance": {"score": 75, "status": "開発中"},
                "budget_allocation": 60
            }
        }

    def create_department(self, dept_name: str, specialization: str, ashigaru_list: List[str]):
        """新事業部設立"""

        print(f"\n[{self.name} CEO] 新事業部設立決定")
        print(f"事業部名: {dept_name}")
        print(f"専門分野: {specialization}")

        # ディレクトリ構造作成
        dept_path = f"{self.company_root}/{dept_name}"
        os.makedirs(dept_path, exist_ok=True)

        for unit in ashigaru_list:
            os.makedirs(f"{dept_path}/{unit}", exist_ok=True)

        # 事業部情報登録
        self.departments[dept_name] = {
            "name": dept_name,
            "specialization": specialization,
            "karo": f"{dept_name}_department_head",
            "ashigaru_units": ashigaru_list,
            "performance": {"score": 0, "status": "新設"},
            "budget_allocation": 0,
            "created_at": datetime.now().isoformat()
        }

        print(f"[{self.name} CEO] {dept_name} 事業部設立完了")
        return True

    def evaluate_department(self, dept_name: str, new_score: int, feedback: str):
        """事業部評価・フィードバック"""

        if dept_name not in self.departments:
            print(f"[{self.name} CEO] 事業部 '{dept_name}' は存在しません")
            return False

        dept = self.departments[dept_name]
        old_score = dept["performance"]["score"]

        print(f"\n[{self.name} CEO] {dept['name']} 評価実施")
        print(f"前回スコア: {old_score} → 今回: {new_score}")
        print(f"フィードバック: {feedback}")

        # 評価更新
        dept["performance"]["score"] = new_score
        dept["performance"]["last_feedback"] = feedback
        dept["performance"]["evaluated_at"] = datetime.now().isoformat()

        # 改善指示
        if new_score < 70:
            print(f"[{self.name} CEO] ⚠️ 改善必要。戦略見直しを指示")
            return self._request_improvement_plan(dept_name)
        elif new_score > old_score + 10:
            print(f"[{self.name} CEO] ✅ 優秀な成果。予算増額検討")

        return True

    def _request_improvement_plan(self, dept_name: str):
        """改善計画要求"""

        print(f"[{self.name} CEO] {dept_name} に改善計画提出を要求")

        # 実際の実装では、該当事業部の家老Agentに改善計画作成を指示
        improvement_suggestions = [
            "足軽の専門性向上研修",
            "プロセス効率化の検討",
            "新技術導入の検討",
            "足軽大将の配置検討"
        ]

        print(f"[{self.name} CEO] 改善提案例:")
        for i, suggestion in enumerate(improvement_suggestions, 1):
            print(f"  {i}. {suggestion}")

        return improvement_suggestions

    def propose_taisho_system(self, dept_name: str, unit_name: str, reason: str):
        """足軽大将配置提案"""

        print(f"\n[{self.name} CEO] 足軽大将配置提案受理")
        print(f"対象: {dept_name}/{unit_name}")
        print(f"理由: {reason}")

        # 足軽大将の必要性判定
        dept = self.departments.get(dept_name)
        if not dept:
            return False

        ashigaru_count = len(dept["ashigaru_units"])

        if ashigaru_count >= 4:  # 4名以上で大将配置検討
            print(f"[{self.name} CEO] ✅ 足軽大将配置承認")
            print(f"[{self.name} CEO] {unit_name}足軽大将を任命")

            # 足軽大将配置
            taisho_dir = f"{self.company_root}/{dept_name}/{unit_name}_taisho"
            os.makedirs(taisho_dir, exist_ok=True)

            dept[f"{unit_name}_taisho"] = {
                "position": "足軽大将",
                "manages": [unit_name],
                "appointed_at": datetime.now().isoformat(),
                "reason": reason
            }

            return True
        else:
            print(f"[{self.name} CEO] ❌ 足軽数不足。現在{ashigaru_count}名")
            return False

    def get_organization_status(self):
        """組織状況レポート"""

        print(f"\n{'='*60}")
        print(f"[{self.name} CEO] EDITH Corporation 組織状況")
        print(f"{'='*60}")

        for dept_key, dept in self.departments.items():
            print(f"\n📊 {dept['name']}")
            print(f"   部長: {dept['karo']}")
            print(f"   足軽数: {len(dept['ashigaru_units'])}名")
            print(f"   成績: {dept['performance']['score']}点 ({dept['performance']['status']})")
            print(f"   予算配分: {dept['budget_allocation']}%")

        return self.departments

    def execute_daily_mission(self, mission_type: str = "daily_blog"):
        """日常ミッション実行（事業部制）"""

        print(f"\n[{self.name} CEO] 本日のミッション: {mission_type}")

        if mission_type == "daily_blog":
            target_dept = "blog_department"
        elif mission_type == "room8_strategy":
            target_dept = "room8_strategy_department"
        else:
            print(f"[{self.name} CEO] 新規ミッション。適切な事業部を選定中...")
            return None

        if target_dept in self.departments:
            dept = self.departments[target_dept]
            print(f"[{self.name} CEO] {dept['name']} に実行指示")
            print(f"[{self.name} CEO] 担当部長: {dept['karo']}")

            # 実際の実装では、ここで該当事業部の家老Agentを起動
            return f"{target_dept}_mission_initiated"

        return None

    def review_department_proposal(self, proposal_file: str = None):
        """事業部提案の審査・承認システム"""

        print(f"\n[{self.name} CEO] 📋 事業部提案審査開始")

        # 最新の提案書を自動検出
        if not proposal_file:
            reports_dir = "reports"
            if os.path.exists(reports_dir):
                proposal_files = [f for f in os.listdir(reports_dir) if f.startswith("blog_dept_proposal_")]
                if proposal_files:
                    proposal_file = os.path.join(reports_dir, sorted(proposal_files)[-1])
                    print(f"[{self.name} CEO] 最新提案書検出: {proposal_file}")

        if not proposal_file or not os.path.exists(proposal_file):
            print(f"[{self.name} CEO] ❌ 提案書が見つかりません")
            return None

        # 提案書読み込み
        with open(proposal_file, "r", encoding="utf-8") as f:
            proposal_data = json.load(f)

        return self._evaluate_and_decide(proposal_data)

    def _evaluate_and_decide(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """提案評価・意思決定"""

        print(f"\n[{self.name} CEO] 🔍 提案内容精査中...")

        executive_summary = proposal_data.get("executive_summary", {})
        detailed_proposal = proposal_data.get("detailed_proposal", {})

        # 提案概要表示
        print(f"[{self.name} CEO] 📊 提案概要:")
        print(f"  現状: {executive_summary.get('current_situation', 'N/A')}")
        print(f"  目標: {executive_summary.get('target', 'N/A')}")
        print(f"  課題: {executive_summary.get('challenge', 'N/A')}")
        print(f"  解決策: {executive_summary.get('solution', 'N/A')}")
        print(f"  期待結果: {executive_summary.get('expected_result', 'N/A')}")

        # 自動評価ロジック
        approval_score = self._calculate_approval_score(detailed_proposal)

        print(f"\n[{self.name} CEO] 📈 提案評価スコア: {approval_score}/100")

        # 承認判定
        if approval_score >= 80:
            decision = self._approve_proposal(detailed_proposal)
        elif approval_score >= 60:
            decision = self._conditional_approval(detailed_proposal)
        else:
            decision = self._reject_proposal(detailed_proposal)

        # 決定通知の保存
        decision_record = {
            "decision": decision["status"],
            "score": approval_score,
            "reasoning": decision["reasoning"],
            "approved_changes": decision.get("approved_changes", []),
            "conditions": decision.get("conditions", []),
            "decided_by": self.name,
            "decided_at": datetime.now().isoformat()
        }

        decision_file = f"reports/ceo_decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(decision_file, "w", encoding="utf-8") as f:
            json.dump(decision_record, f, ensure_ascii=False, indent=2)

        print(f"[{self.name} CEO] 📁 決定記録保存: {decision_file}")

        return decision_record

    def _calculate_approval_score(self, proposal: Dict[str, Any]) -> int:
        """提案の承認スコア自動計算"""

        score = 0

        # 新設足軽の妥当性評価
        new_ashigaru = proposal.get("new_ashigaru", {})
        for ashigaru_name, details in new_ashigaru.items():
            priority = details.get("priority", 3)
            expected_impact = details.get("expected_impact", "")

            if priority == 1:  # 最高優先度
                score += 25
            elif priority == 2:
                score += 20
            elif priority == 3:
                score += 15

            # 数値的効果が明記されている場合
            if "%" in expected_impact or "倍" in expected_impact:
                score += 10

        # 予算の妥当性
        budget = proposal.get("budget_request", {})
        payback_period = budget.get("payback_period", "")
        if "ヶ月" in payback_period:
            months = int(payback_period.replace("ヶ月", ""))
            if months <= 3:
                score += 20
            elif months <= 6:
                score += 15
            else:
                score += 5

        # 実装計画の具体性
        timeline = proposal.get("implementation_timeline", {})
        if len(timeline) >= 3:  # 段階的計画がある
            score += 15

        return min(score, 100)  # 最大100点

    def _approve_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """提案承認"""

        print(f"\n[{self.name} CEO] ✅ 提案承認決定")
        print(f"[{self.name} CEO] 理由: 戦略的妥当性高、ROI明確、実装計画具体的")

        # 承認された変更を実装
        approved_changes = []

        # 新設足軽の承認
        for ashigaru_name, details in proposal.get("new_ashigaru", {}).items():
            approved_changes.append({
                "type": "new_ashigaru",
                "name": ashigaru_name,
                "specialization": details.get("specialization", ""),
                "expected_impact": details.get("expected_impact", "")
            })

            # 実際のディレクトリ作成
            ashigaru_dir = f"blog_department/{ashigaru_name}"
            os.makedirs(ashigaru_dir, exist_ok=True)
            print(f"[{self.name} CEO] 📁 {ashigaru_name} 配置完了")

        # 足軽大将の承認
        taisho = proposal.get("taisho_recommendation")
        if taisho:
            approved_changes.append({
                "type": "taisho_appointment",
                "position": taisho.get("position", ""),
                "manages": taisho.get("manages", [])
            })

            taisho_dir = "blog_department/content_taisho"
            os.makedirs(taisho_dir, exist_ok=True)
            print(f"[{self.name} CEO] 👑 コンテンツ足軽大将任命")

        print(f"[{self.name} CEO] 🚀 組織改革実行開始指示")

        return {
            "status": "approved",
            "reasoning": "戦略的妥当性・ROI・実装計画すべて優秀",
            "approved_changes": approved_changes,
            "execution_order": "即時実行"
        }

    def _conditional_approval(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """条件付き承認"""

        print(f"\n[{self.name} CEO] ⚠️ 条件付き承認")

        conditions = [
            "新設足軽は段階的配置（1名ずつ効果検証）",
            "1ヶ月後の中間評価必須",
            "予算上限を80%に制限"
        ]

        print(f"[{self.name} CEO] 条件:")
        for i, condition in enumerate(conditions, 1):
            print(f"  {i}. {condition}")

        return {
            "status": "conditional_approval",
            "reasoning": "基本方針は妥当だが、リスク管理必要",
            "conditions": conditions,
            "review_date": "1ヶ月後"
        }

    def _reject_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """提案却下"""

        print(f"\n[{self.name} CEO] ❌ 提案却下")

        rejection_reasons = [
            "ROIの根拠不十分",
            "予算規模が過大",
            "実装計画が曖昧"
        ]

        print(f"[{self.name} CEO] 却下理由:")
        for i, reason in enumerate(rejection_reasons, 1):
            print(f"  {i}. {reason}")

        print(f"[{self.name} CEO] 🔄 再提案を要求")

        return {
            "status": "rejected",
            "reasoning": "戦略的妥当性・実現可能性に課題",
            "rejection_reasons": rejection_reasons,
            "next_action": "改善後再提案"
        }

def main():
    """EDITH Corporation テスト実行"""

    edith = EDITHCorporation()

    # 組織状況確認
    edith.get_organization_status()

    # 事業部評価
    edith.evaluate_department("blog_department", 90, "コンテンツ品質向上、アクセス数増加")

    # 足軽大将提案テスト
    edith.propose_taisho_system("blog_department", "writing", "ライティング足軽の作業負荷過多")

    # 日常ミッション実行
    edith.execute_daily_mission("daily_blog")

if __name__ == "__main__":
    main()