#!/usr/bin/env python3
"""
Task Toolベースディスパッチ検証テスト
- department_registry.json の読み込み
- DEPARTMENT_PROMPT.md の存在確認
- run_ashigaru.py の各サブコマンドが有効なJSONを返すか
- edith_ceo.py の get_dispatch_info が正しく動作するか
"""

import sys
import json
import subprocess
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_BLOG_DEPT = _THIS_DIR / "blog_department"
_RUN_ASHIGARU = _BLOG_DEPT / "run_ashigaru.py"

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"


def _run_ashigaru(command: str, params: dict = None) -> dict:
    """run_ashigaru.py をサブプロセスで実行し、stdout JSONを返す"""
    args = [sys.executable, str(_RUN_ASHIGARU), command]
    if params:
        args += ["--json", json.dumps(params, ensure_ascii=False)]

    result = subprocess.run(
        args,
        capture_output=True, text=True, timeout=30,
        cwd=str(_BLOG_DEPT),
    )

    # stdoutの最後の有効なJSON行を探す
    stdout = result.stdout.strip()
    if not stdout:
        raise ValueError(f"No stdout output. stderr: {result.stderr[:500]}")

    # stdout全体がJSONかもしれない、または最後のJSON部分を探す
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        # 複数行の場合、最後の } から逆向きにJSONを探す
        lines = stdout.split("\n")
        # 最後の行からJSON部分を結合して試す
        for i in range(len(lines)):
            candidate = "\n".join(lines[i:])
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
        raise ValueError(f"Could not parse JSON from stdout: {stdout[:500]}")


def test_registry_loading():
    """Test 1: department_registry.json の読み込み"""
    print("\n--- Test 1: department_registry.json ---")

    registry_path = _THIS_DIR / "department_registry.json"
    if not registry_path.exists():
        print(f"  {FAIL}: ファイルが存在しません")
        return FAIL

    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  {FAIL}: JSONパースエラー: {e}")
        return FAIL

    # blog_department エントリの確認
    if "blog_department" not in data:
        print(f"  {FAIL}: blog_department エントリがありません")
        return FAIL

    blog = data["blog_department"]
    required_keys = ["name", "prompt_file", "root_path", "mission_types", "enabled"]
    missing = [k for k in required_keys if k not in blog]
    if missing:
        print(f"  {FAIL}: 必須キーが不足: {missing}")
        return FAIL

    print(f"  {PASS}: レジストリ読み込み成功（{len(data)} 部署）")
    return PASS


def test_department_prompt():
    """Test 2: DEPARTMENT_PROMPT.md の存在確認"""
    print("\n--- Test 2: DEPARTMENT_PROMPT.md ---")

    prompt_path = _BLOG_DEPT / "DEPARTMENT_PROMPT.md"
    if not prompt_path.exists():
        print(f"  {FAIL}: ファイルが存在しません")
        return FAIL

    content = prompt_path.read_text(encoding="utf-8")
    if len(content) < 100:
        print(f"  {FAIL}: 内容が短すぎます（{len(content)} bytes）")
        return FAIL

    # 必須セクションの確認
    required_sections = ["run_ashigaru.py", "Step 1", "Step 9", "最終出力フォーマット"]
    missing = [s for s in required_sections if s not in content]
    if missing:
        print(f"  {FAIL}: 必須セクションが不足: {missing}")
        return FAIL

    print(f"  {PASS}: DEPARTMENT_PROMPT.md 検証成功（{len(content)} bytes）")
    return PASS


def test_ceo_dispatch():
    """Test 3: edith_ceo.py の get_dispatch_info"""
    print("\n--- Test 3: edith_ceo.py get_dispatch_info ---")

    sys.path.insert(0, str(_THIS_DIR))
    try:
        from edith_ceo import EDITHCorporation
        edith = EDITHCorporation()
    except Exception as e:
        print(f"  {FAIL}: EDITHCorporation インポート/初期化エラー: {e}")
        return FAIL

    # daily_blog のディスパッチ
    dispatch = edith.get_dispatch_info("daily_blog")
    if dispatch.get("status") != "ready":
        print(f"  {FAIL}: daily_blog ディスパッチが ready ではない: {dispatch}")
        return FAIL

    if not Path(dispatch.get("prompt_file", "")).exists():
        print(f"  {FAIL}: prompt_file が存在しません: {dispatch.get('prompt_file')}")
        return FAIL

    # 無効な部署のディスパッチ
    dispatch2 = edith.get_dispatch_info("room8_strategy")
    if dispatch2.get("status") != "disabled":
        print(f"  {FAIL}: room8_strategy は disabled であるべき: {dispatch2}")
        return FAIL

    # 未知のミッション
    dispatch3 = edith.get_dispatch_info("nonexistent")
    if dispatch3.get("status") != "not_found":
        print(f"  {FAIL}: nonexistent は not_found であるべき: {dispatch3}")
        return FAIL

    print(f"  {PASS}: ディスパッチ情報の解決が正しく動作")
    return PASS


def test_run_ashigaru_help():
    """Test 4: run_ashigaru.py --help"""
    print("\n--- Test 4: run_ashigaru.py --help ---")

    try:
        result = subprocess.run(
            [sys.executable, str(_RUN_ASHIGARU), "--help"],
            capture_output=True, text=True, timeout=10,
        )
        output = json.loads(result.stdout.strip())
        commands = output.get("available_commands", [])
        expected = ["research", "seo", "writing", "social", "analytics", "image", "wordpress"]
        missing = [c for c in expected if c not in commands]
        if missing:
            print(f"  {FAIL}: 不足コマンド: {missing}")
            return FAIL

        print(f"  {PASS}: 全コマンド ({len(commands)}) が登録済み")
        return PASS
    except Exception as e:
        print(f"  {FAIL}: {e}")
        return FAIL


def test_ashigaru_research():
    """Test 5: research サブコマンド"""
    print("\n--- Test 5: run_ashigaru.py research ---")

    try:
        result = _run_ashigaru("research", {
            "target_audience": "中小企業経営者",
            "content_strategy": "問題解決型",
            "focus_area": "AI活用",
        })
        if "priority_recommendation" not in result:
            print(f"  {FAIL}: priority_recommendation が出力にありません")
            return FAIL

        title = result["priority_recommendation"].get("title", "")
        print(f"  {PASS}: 記事企画取得成功: {title[:40]}")
        return PASS
    except Exception as e:
        print(f"  {FAIL}: {e}")
        return FAIL


def test_ashigaru_analytics():
    """Test 6: analytics サブコマンド"""
    print("\n--- Test 6: run_ashigaru.py analytics ---")

    try:
        result = _run_ashigaru("analytics", {})
        if not isinstance(result, dict):
            print(f"  {FAIL}: 出力がdictではありません")
            return FAIL

        print(f"  {PASS}: 分析レポート取得成功（{len(result)} keys）")
        return PASS
    except Exception as e:
        print(f"  {FAIL}: {e}")
        return FAIL


def test_ashigaru_seo():
    """Test 7: seo サブコマンド"""
    print("\n--- Test 7: run_ashigaru.py seo ---")

    try:
        result = _run_ashigaru("seo", {
            "topic": "ChatGPT vs Gemini 比較",
            "content": "",
        })
        if not isinstance(result, dict):
            print(f"  {FAIL}: 出力がdictではありません")
            return FAIL

        print(f"  {PASS}: SEO分析結果取得成功")
        return PASS
    except Exception as e:
        print(f"  {FAIL}: {e}")
        return FAIL


def main():
    print("=" * 60)
    print("Task Tool ベース ディスパッチ検証テスト")
    print("=" * 60)

    tests = [
        test_registry_loading,
        test_department_prompt,
        test_ceo_dispatch,
        test_run_ashigaru_help,
        test_ashigaru_research,
        test_ashigaru_analytics,
        test_ashigaru_seo,
    ]

    results = {}
    for test_fn in tests:
        name = test_fn.__doc__ or test_fn.__name__
        try:
            results[name] = test_fn()
        except Exception as e:
            print(f"  {FAIL}: 予期せぬエラー: {e}")
            results[name] = FAIL

    # サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v == PASS)
    failed = sum(1 for v in results.values() if v == FAIL)
    skipped = sum(1 for v in results.values() if v == SKIP)

    for name, result in results.items():
        icon = {"PASS": "[OK]", "FAIL": "[NG]", "SKIP": "[--]"}.get(result, "[??]")
        print(f"  {icon} {name}")

    print(f"\n  合計: {passed} passed, {failed} failed, {skipped} skipped / {len(tests)} tests")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
