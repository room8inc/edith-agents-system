#!/usr/bin/env python3
"""
EDITH指揮系統フルサイクルテスト
CEO → 事業部長 → 足軽大将 → 各足軽 の指揮系統接続を検証
"""

import sys
import json
import argparse
import traceback
from pathlib import Path
from datetime import datetime

# edith_corpディレクトリをパスに追加
_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))


def test_imports():
    """インポートテスト - 各レイヤーが正しくインポートできるか"""

    print("=" * 70)
    print("Phase 1: インポートテスト")
    print("=" * 70)

    results = {}

    # CEO
    try:
        from edith_ceo import EDITHCorporation
        results["EDITHCorporation"] = "OK"
        print(f"  [OK] EDITHCorporation")
    except Exception as e:
        results["EDITHCorporation"] = f"FAIL: {e}"
        print(f"  [FAIL] EDITHCorporation: {e}")

    # 事業部長
    try:
        sys.path.insert(0, str(_THIS_DIR / "blog_department"))
        from blog_department_head import BlogDepartmentHead
        results["BlogDepartmentHead"] = "OK"
        print(f"  [OK] BlogDepartmentHead")
    except Exception as e:
        results["BlogDepartmentHead"] = f"FAIL: {e}"
        print(f"  [FAIL] BlogDepartmentHead: {e}")

    # 足軽大将
    try:
        sys.path.insert(0, str(_THIS_DIR / "blog_department" / "content_taisho"))
        from content_taisho import ContentTaisho
        results["ContentTaisho"] = "OK"
        print(f"  [OK] ContentTaisho")
    except Exception as e:
        results["ContentTaisho"] = f"FAIL: {e}"
        print(f"  [FAIL] ContentTaisho: {e}")

    return results


def test_chain():
    """チェーンテスト - CEO から足軽大将までの接続を検証（実行なし）"""

    print("\n" + "=" * 70)
    print("Phase 2: チェーン接続テスト")
    print("=" * 70)

    # CEO → BlogDepartmentHead の接続確認
    from edith_ceo import EDITHCorporation
    edith = EDITHCorporation()

    # BlogDepartmentHead が import されているか
    from edith_ceo import BlogDepartmentHead as CEO_BDH
    if CEO_BDH:
        print(f"  [OK] CEO → BlogDepartmentHead 接続確認")
    else:
        print(f"  [FAIL] CEO → BlogDepartmentHead 接続なし")
        return False

    # BlogDepartmentHead → ContentTaisho の接続確認
    sys.path.insert(0, str(_THIS_DIR / "blog_department"))
    from blog_department_head import ContentTaisho as BDH_CT
    if BDH_CT:
        print(f"  [OK] BlogDepartmentHead → ContentTaisho 接続確認")
    else:
        print(f"  [FAIL] BlogDepartmentHead → ContentTaisho 接続なし")
        return False

    # ContentTaisho の manages_units に image_generation, wordpress_posting があるか
    sys.path.insert(0, str(_THIS_DIR / "blog_department" / "content_taisho"))
    from content_taisho import ContentTaisho
    taisho = ContentTaisho()
    units = taisho.manages_units
    if "image_generation" in units and "wordpress_posting" in units:
        print(f"  [OK] ContentTaisho manages_units に image_generation + wordpress_posting 含む")
    else:
        print(f"  [FAIL] ContentTaisho manages_units 不足: {units}")
        return False

    # dispatch_daily_mission メソッドの存在確認
    head = CEO_BDH()
    if hasattr(head, 'dispatch_daily_mission'):
        print(f"  [OK] BlogDepartmentHead.dispatch_daily_mission() メソッド確認")
    else:
        print(f"  [FAIL] BlogDepartmentHead.dispatch_daily_mission() メソッド未定義")
        return False

    # _save_mission_report メソッドの存在確認（CEO）
    if hasattr(edith, '_save_mission_report'):
        print(f"  [OK] EDITHCorporation._save_mission_report() メソッド確認")
    else:
        print(f"  [FAIL] EDITHCorporation._save_mission_report() メソッド未定義")
        return False

    print(f"\n  全チェーン接続テスト: PASS")
    return True


def test_mission():
    """ミッション実行テスト - CEO.execute_daily_mission() のフル実行"""

    print("\n" + "=" * 70)
    print("Phase 3: フルミッション実行テスト")
    print("=" * 70)
    print("CEO.execute_daily_mission('daily_blog') を実行...")

    from edith_ceo import EDITHCorporation

    edith = EDITHCorporation()
    result = edith.execute_daily_mission("daily_blog")

    print("\n" + "-" * 70)
    print("ミッション実行結果:")
    print("-" * 70)

    if result is None:
        print("  結果: None（実行されず）")
        return False

    status = result.get("status", "unknown")
    steps = result.get("steps", [])
    deliverables = result.get("final_deliverables", {})
    review = result.get("department_review", {})

    print(f"  ステータス: {status}")
    print(f"  実行ステップ: {len(steps)}")
    for step in steps:
        print(f"    - {step}")
    print(f"  成果物数: {len(deliverables)}")
    print(f"  事業部長レビュー: {review.get('quality_score', 'N/A')}/100")

    if deliverables.get("article_directory"):
        print(f"  記事ディレクトリ: {deliverables['article_directory']}")

    img = deliverables.get("image_generation", {})
    print(f"  画像生成: {img.get('successful_images', 0)}/{img.get('total_images', 0)}枚")

    wp = deliverables.get("wordpress_publishing", {})
    print(f"  WordPress投稿: {'成功' if wp.get('success') else 'スキップ/失敗'}")

    # reports/ にファイルが保存されたか確認
    reports_dir = _THIS_DIR / "reports"
    if reports_dir.exists():
        report_files = list(reports_dir.glob("*.json"))
        print(f"\n  reports/ 内のファイル数: {len(report_files)}")
        for f in sorted(report_files)[-3:]:
            print(f"    - {f.name}")

    return status == "success"


def test_unit_status():
    """足軽部隊状況テスト"""

    print("\n" + "=" * 70)
    print("Phase 4: 足軽部隊状況確認")
    print("=" * 70)

    sys.path.insert(0, str(_THIS_DIR / "blog_department" / "content_taisho"))
    from content_taisho import ContentTaisho

    taisho = ContentTaisho()
    status = taisho.get_unit_status()

    print(f"\n  統括足軽数: {status['taisho_info']['manages_units']}")
    print(f"  部隊稼働率: {status['readiness_score']}%")
    print(f"  ユニット状態:")
    for name, info in status["ashigaru_units"].items():
        print(f"    {name}: {info['status']} ({info['specialty']})")

    return True


def main():
    parser = argparse.ArgumentParser(description="EDITH指揮系統フルサイクルテスト")
    parser.add_argument(
        "--mode",
        choices=["import", "chain", "mission", "status", "all"],
        default="chain",
        help="テストモード: import/chain/mission/status/all"
    )
    args = parser.parse_args()

    print(f"\nEDITH指揮系統テスト 開始: {datetime.now().isoformat()}")
    print(f"テストモード: {args.mode}\n")

    results = {}

    try:
        if args.mode in ("import", "all"):
            results["import"] = test_imports()

        if args.mode in ("chain", "all"):
            results["chain"] = test_chain()

        if args.mode in ("status", "all"):
            results["status"] = test_unit_status()

        if args.mode in ("mission", "all"):
            results["mission"] = test_mission()

    except Exception as e:
        print(f"\nテスト中にエラー発生: {e}")
        traceback.print_exc()
        results["error"] = str(e)

    print(f"\n{'=' * 70}")
    print(f"テスト完了: {datetime.now().isoformat()}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
