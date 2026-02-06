#!/usr/bin/env python3
"""
EDITH CEO（最高経営責任者） - 動的組織管理システム
department_registry.json を読み、Task Tool でサブエージェントを起動するための
ディスパッチ情報を提供する。実際のTask Tool呼び出しはClaude/EDITHが行う。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

_THIS_DIR = Path(__file__).resolve().parent

from output_paths import REPORTS_DIR, ensure_dirs


class EDITHCorporation:
    """EDITH Corporation - 動的組織管理CEO"""

    def __init__(self):
        self.position = "CEO"
        self.name = "EDITH"
        self.company_root = str(_THIS_DIR)
        self.departments = {}

        self._initialize_organization()
        print(f"[{self.name} CEO] コーポレーション起動完了")

    def _initialize_organization(self):
        """組織初期化"""

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

        dept_path = Path(self.company_root) / dept_name
        dept_path.mkdir(parents=True, exist_ok=True)

        for unit in ashigaru_list:
            (dept_path / unit).mkdir(parents=True, exist_ok=True)

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

        dept["performance"]["score"] = new_score
        dept["performance"]["last_feedback"] = feedback
        dept["performance"]["evaluated_at"] = datetime.now().isoformat()

        if new_score < 70:
            print(f"[{self.name} CEO] 改善必要。戦略見直しを指示")
            return self._request_improvement_plan(dept_name)
        elif new_score > old_score + 10:
            print(f"[{self.name} CEO] 優秀な成果。予算増額検討")

        return True

    def _request_improvement_plan(self, dept_name: str):
        """改善計画要求"""

        print(f"[{self.name} CEO] {dept_name} に改善計画提出を要求")

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

        dept = self.departments.get(dept_name)
        if not dept:
            return False

        ashigaru_count = len(dept["ashigaru_units"])

        if ashigaru_count >= 4:
            print(f"[{self.name} CEO] 足軽大将配置承認")
            print(f"[{self.name} CEO] {unit_name}足軽大将を任命")

            taisho_dir = Path(self.company_root) / dept_name / f"{unit_name}_taisho"
            taisho_dir.mkdir(parents=True, exist_ok=True)

            dept[f"{unit_name}_taisho"] = {
                "position": "足軽大将",
                "manages": [unit_name],
                "appointed_at": datetime.now().isoformat(),
                "reason": reason
            }

            return True
        else:
            print(f"[{self.name} CEO] 足軽数不足。現在{ashigaru_count}名")
            return False

    def get_organization_status(self):
        """組織状況レポート"""

        print(f"\n{'='*60}")
        print(f"[{self.name} CEO] EDITH Corporation 組織状況")
        print(f"{'='*60}")

        for dept_key, dept in self.departments.items():
            print(f"\n{dept['name']}")
            print(f"   部長: {dept['karo']}")
            print(f"   足軽数: {len(dept['ashigaru_units'])}名")
            print(f"   成績: {dept['performance']['score']}点 ({dept['performance']['status']})")
            print(f"   予算配分: {dept['budget_allocation']}%")

        return self.departments

    def get_dispatch_info(self, mission_type: str = "daily_blog") -> Dict[str, Any]:
        """ミッションタイプからディスパッチ情報を解決する。
        Claude/EDITHがTask Toolで事業部長を起動するための情報を返す。
        実際のTask Tool呼び出しはPythonではなくClaude/EDITHが行う。
        """

        registry = self._load_registry()
        if not registry:
            return {"status": "error", "error": "department_registry.json の読み込み失敗"}

        # mission_type に対応する部署を検索
        for dept_key, dept_info in registry.items():
            if mission_type in dept_info.get("mission_types", []):
                if not dept_info.get("enabled", False):
                    return {
                        "status": "disabled",
                        "department": dept_key,
                        "message": f"{dept_info['name']} は無効化されています",
                    }

                prompt_path = _THIS_DIR / dept_info["prompt_file"]
                return {
                    "status": "ready",
                    "department": dept_key,
                    "department_name": dept_info["name"],
                    "prompt_file": str(prompt_path),
                    "root_path": str(_THIS_DIR / dept_info["root_path"]),
                }

        return {
            "status": "not_found",
            "error": f"ミッションタイプ '{mission_type}' に対応する部署が見つかりません",
        }

    def _load_registry(self) -> Optional[Dict]:
        """department_registry.json を読み込む"""

        registry_path = _THIS_DIR / "department_registry.json"
        if not registry_path.exists():
            print(f"[{self.name} CEO] department_registry.json が見つかりません")
            return None

        try:
            return json.loads(registry_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[{self.name} CEO] レジストリ読み込みエラー: {e}")
            return None

    def execute_daily_mission(self, mission_type: str = "daily_blog"):
        """日常ミッションのディスパッチ情報を返す。
        （後方互換性のために残す。実際のTask Tool呼び出しはClaude/EDITHが行う）
        """

        print(f"\n[{self.name} CEO] 本日のミッション: {mission_type}")

        dispatch = self.get_dispatch_info(mission_type)
        print(f"[{self.name} CEO] ディスパッチ情報: {json.dumps(dispatch, ensure_ascii=False, indent=2)}")

        return dispatch

    def _save_mission_report(self, mission_type: str, result: Dict[str, Any]):
        """CEOレベルのミッション報告保存"""

        ensure_dirs()
        reports_dir = REPORTS_DIR

        report = {
            "mission_type": mission_type,
            "executed_by": self.name,
            "executed_at": datetime.now().isoformat(),
            "mission_status": result.get("status", "unknown"),
            "steps_completed": len(result.get("steps", [])),
            "department_review": result.get("department_review", {}),
            "summary": {
                "deliverables_count": len(result.get("final_deliverables", {})),
                "article_dir": result.get("final_deliverables", {}).get("article_directory"),
            }
        }

        report_file = reports_dir / f"ceo_mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8"
        )

        print(f"[{self.name} CEO] ミッション報告保存: {report_file}")

    def review_department_proposal(self, proposal_file: str = None):
        """事業部提案の審査・承認システム"""

        print(f"\n[{self.name} CEO] 事業部提案審査開始")

        if not proposal_file:
            reports_dir = REPORTS_DIR
            if reports_dir.exists():
                proposal_files = [f for f in reports_dir.iterdir() if f.name.startswith("blog_dept_proposal_")]
                if proposal_files:
                    proposal_file = str(sorted(proposal_files)[-1])
                    print(f"[{self.name} CEO] 最新提案書検出: {proposal_file}")

        if not proposal_file or not Path(proposal_file).exists():
            print(f"[{self.name} CEO] 提案書が見つかりません")
            return None

        with open(proposal_file, "r", encoding="utf-8") as f:
            proposal_data = json.load(f)

        return self._evaluate_and_decide(proposal_data)

    def _evaluate_and_decide(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """提案評価・意思決定"""

        print(f"\n[{self.name} CEO] 提案内容精査中...")

        executive_summary = proposal_data.get("executive_summary", {})
        detailed_proposal = proposal_data.get("detailed_proposal", {})

        print(f"[{self.name} CEO] 提案概要:")
        print(f"  現状: {executive_summary.get('current_situation', 'N/A')}")
        print(f"  目標: {executive_summary.get('target', 'N/A')}")
        print(f"  課題: {executive_summary.get('challenge', 'N/A')}")
        print(f"  解決策: {executive_summary.get('solution', 'N/A')}")
        print(f"  期待結果: {executive_summary.get('expected_result', 'N/A')}")

        approval_score = self._calculate_approval_score(detailed_proposal)

        print(f"\n[{self.name} CEO] 提案評価スコア: {approval_score}/100")

        if approval_score >= 80:
            decision = self._approve_proposal(detailed_proposal)
        elif approval_score >= 60:
            decision = self._conditional_approval(detailed_proposal)
        else:
            decision = self._reject_proposal(detailed_proposal)

        decision_record = {
            "decision": decision["status"],
            "score": approval_score,
            "reasoning": decision["reasoning"],
            "approved_changes": decision.get("approved_changes", []),
            "conditions": decision.get("conditions", []),
            "decided_by": self.name,
            "decided_at": datetime.now().isoformat()
        }

        ensure_dirs()
        decision_file = REPORTS_DIR / f"ceo_decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        decision_file.write_text(
            json.dumps(decision_record, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        print(f"[{self.name} CEO] 決定記録保存: {decision_file}")

        return decision_record

    def _calculate_approval_score(self, proposal: Dict[str, Any]) -> int:
        """提案の承認スコア自動計算"""

        score = 0

        new_ashigaru = proposal.get("new_ashigaru", {})
        for ashigaru_name, details in new_ashigaru.items():
            priority = details.get("priority", 3)
            expected_impact = details.get("expected_impact", "")

            if priority == 1:
                score += 25
            elif priority == 2:
                score += 20
            elif priority == 3:
                score += 15

            if "%" in expected_impact or "倍" in expected_impact:
                score += 10

        budget = proposal.get("budget_request", {})
        payback_period = budget.get("payback_period", "")
        if "ヶ月" in payback_period:
            try:
                months = int(payback_period.replace("ヶ月", ""))
                if months <= 3:
                    score += 20
                elif months <= 6:
                    score += 15
                else:
                    score += 5
            except ValueError:
                pass

        timeline = proposal.get("implementation_timeline", {})
        if len(timeline) >= 3:
            score += 15

        return min(score, 100)

    def _approve_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """提案承認"""

        print(f"\n[{self.name} CEO] 提案承認決定")

        approved_changes = []

        for ashigaru_name, details in proposal.get("new_ashigaru", {}).items():
            approved_changes.append({
                "type": "new_ashigaru",
                "name": ashigaru_name,
                "specialization": details.get("specialization", ""),
                "expected_impact": details.get("expected_impact", "")
            })

            ashigaru_dir = Path(self.company_root) / "blog_department" / ashigaru_name
            ashigaru_dir.mkdir(parents=True, exist_ok=True)
            print(f"[{self.name} CEO] {ashigaru_name} 配置完了")

        taisho = proposal.get("taisho_recommendation")
        if taisho:
            approved_changes.append({
                "type": "taisho_appointment",
                "position": taisho.get("position", ""),
                "manages": taisho.get("manages", [])
            })

            taisho_dir = Path(self.company_root) / "blog_department" / "content_taisho"
            taisho_dir.mkdir(parents=True, exist_ok=True)
            print(f"[{self.name} CEO] コンテンツ足軽大将任命")

        print(f"[{self.name} CEO] 組織改革実行開始指示")

        return {
            "status": "approved",
            "reasoning": "戦略的妥当性・ROI・実装計画すべて優秀",
            "approved_changes": approved_changes,
            "execution_order": "即時実行"
        }

    def _conditional_approval(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """条件付き承認"""

        print(f"\n[{self.name} CEO] 条件付き承認")

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

        print(f"\n[{self.name} CEO] 提案却下")

        rejection_reasons = [
            "ROIの根拠不十分",
            "予算規模が過大",
            "実装計画が曖昧"
        ]

        print(f"[{self.name} CEO] 却下理由:")
        for i, reason in enumerate(rejection_reasons, 1):
            print(f"  {i}. {reason}")

        print(f"[{self.name} CEO] 再提案を要求")

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

    # ディスパッチ情報テスト
    print("\n--- ディスパッチテスト ---")
    dispatch = edith.get_dispatch_info("daily_blog")
    print(json.dumps(dispatch, ensure_ascii=False, indent=2))

    dispatch2 = edith.get_dispatch_info("room8_strategy")
    print(json.dumps(dispatch2, ensure_ascii=False, indent=2))

    dispatch3 = edith.get_dispatch_info("unknown_mission")
    print(json.dumps(dispatch3, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
