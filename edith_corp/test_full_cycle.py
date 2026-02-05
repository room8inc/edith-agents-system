#!/usr/bin/env python3
"""
完全サイクルテスト：家老提案 → CEO承認 → 組織実装
"""

import sys
import os

# 家老システムのインポート
sys.path.append('blog_department')
from blog_department_head import BlogDepartmentHead

# CEOシステムのインポート
from edith_ceo import EDITHCorporation

def test_full_autonomous_cycle():
    """完全自律組織サイクルのテスト"""

    print("🎯 EDITH Corporation 完全自律組織サイクルテスト")
    print("=" * 80)

    # Step 1: 家老の自律分析・提案
    print("\n📋 Step 1: ブログ事業部長（家老）による自律分析・提案")
    blog_head = BlogDepartmentHead()
    analysis_result = blog_head.execute_autonomous_analysis()

    # Step 2: CEOの承認審査
    print("\n🏛️  Step 2: EDITH CEOによる提案審査・承認")
    edith_ceo = EDITHCorporation()
    decision = edith_ceo.review_department_proposal()

    # Step 3: 結果確認
    print("\n🎉 Step 3: 完全サイクル結果確認")
    if decision and decision.get("decision") == "approved":
        print("✅ 完全自律組織サイクル成功！")
        print("  家老提案 → CEO承認 → 組織変更実装 完了")

        # 新しい組織構造確認
        print("\n📁 新組織構造:")
        blog_dept_path = "blog_department"
        if os.path.exists(blog_dept_path):
            for item in os.listdir(blog_dept_path):
                if os.path.isdir(os.path.join(blog_dept_path, item)):
                    print(f"  📂 {item}")

    else:
        print("⚠️  承認プロセスで課題発生")
        if decision:
            print(f"  決定: {decision.get('decision', 'unknown')}")
            print(f"  理由: {decision.get('reasoning', 'N/A')}")

    return decision

if __name__ == "__main__":
    result = test_full_autonomous_cycle()