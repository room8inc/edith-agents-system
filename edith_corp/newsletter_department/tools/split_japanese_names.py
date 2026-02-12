#!/usr/bin/env python3
"""
日本語の氏名を姓名に分割

ルールベース + よくある姓のパターンマッチングで判定
"""

import csv
import re
from typing import Dict, Optional, Tuple


# よくある日本の姓（2文字）
COMMON_SURNAMES_2 = [
    '田中', '鈴木', '高橋', '佐藤', '伊藤', '渡辺', '山本', '中村', '小林', '加藤',
    '吉田', '山田', '佐々木', '山口', '松本', '井上', '木村', '林', '斎藤', '清水',
    '山崎', '森', '池田', '橋本', '阿部', '石川', '前田', '藤田', '後藤', '長谷川',
    '村上', '近藤', '石井', '坂本', '遠藤', '青木', '藤井', '西村', '福田', '太田',
    '三浦', '岡田', '藤原', '竹内', '金子', '中島', '原田', '和田', '中川', '森田',
    '岩崎', '小川', '上田', '西田', '中野', '原', '横山', '田村', '宮崎', '高木'
]

# よくある日本の姓（3文字）
COMMON_SURNAMES_3 = [
    '佐々木', '長谷川', '渡邊', '渡邉'
]

# 企業・組織を示すキーワード
COMPANY_KEYWORDS = [
    '株式会社', '有限会社', '合同会社', '合資会社', 'LLC', 'Inc', 'Corp',
    '事務所', '法人', '協会', '組合', 'ホームズ', 'カンパニー',
    '(株)', '(有)', '(合)', '㈱', '㈲'
]


def is_company_name(name: str) -> bool:
    """企業名かどうかを判定"""
    for keyword in COMPANY_KEYWORDS:
        if keyword in name:
            return True
    return False


def split_japanese_name(full_name: str) -> Dict[str, str]:
    """
    日本語氏名を姓名に分割

    Args:
        full_name: フルネーム

    Returns:
        {"lastname": "姓", "firstname": "名", "original": "元の名前"}
    """
    full_name = full_name.strip()

    # 空文字チェック
    if not full_name:
        return {"lastname": "", "firstname": "", "original": ""}

    # 企業名の場合はそのまま返す
    if is_company_name(full_name):
        return {"lastname": "", "firstname": full_name, "original": full_name}

    # 英数字のみ（ローマ字名）の場合はスペース分割
    if re.match(r'^[A-Za-z\s]+$', full_name):
        parts = full_name.split()
        if len(parts) >= 2:
            # 西洋名の場合は "名 姓" が多いが、日本人のローマ字表記は "姓 名" が多い
            # とりあえず最初を姓とする
            return {
                "lastname": parts[0],
                "firstname": " ".join(parts[1:]),
                "original": full_name
            }
        else:
            return {"lastname": "", "firstname": full_name, "original": full_name}

    # スペース区切りがある場合
    if ' ' in full_name or '　' in full_name:
        parts = re.split(r'[\s　]+', full_name)
        if len(parts) >= 2:
            return {
                "lastname": parts[0],
                "firstname": " ".join(parts[1:]),
                "original": full_name
            }

    # 3文字姓のパターンマッチ
    for surname in COMMON_SURNAMES_3:
        if full_name.startswith(surname) and len(full_name) > len(surname):
            return {
                "lastname": surname,
                "firstname": full_name[len(surname):],
                "original": full_name
            }

    # 2文字姓のパターンマッチ
    for surname in COMMON_SURNAMES_2:
        if full_name.startswith(surname) and len(full_name) > 2:
            return {
                "lastname": surname,
                "firstname": full_name[2:],
                "original": full_name
            }

    # パターンマッチできない場合は最初の2文字を姓とする（日本の姓は2文字が多い）
    if len(full_name) >= 3:
        return {
            "lastname": full_name[:2],
            "firstname": full_name[2:],
            "original": full_name
        }

    # 2文字以下の場合は姓のみとする
    return {
        "lastname": full_name,
        "firstname": "",
        "original": full_name
    }


def process_csv(input_csv: str, output_csv: str):
    """
    CSVの名前を姓名に分割

    Args:
        input_csv: 入力CSVパス
        output_csv: 出力CSVパス
    """
    results = []

    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = row.get('NAME', '').strip()
            split_result = split_japanese_name(name)

            # 既存カラム + LASTNAME, FIRSTNAME を追加
            new_row = dict(row)
            new_row['LASTNAME'] = split_result['lastname']
            new_row['FIRSTNAME'] = split_result['firstname']

            results.append(new_row)

    # 出力
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        if results:
            fieldnames = list(results[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    return len(results)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='日本語氏名を姓名に分割')
    parser.add_argument('input_csv', help='入力CSVファイル')
    parser.add_argument('--output', '-o', default='names_split.csv', help='出力CSVファイル')
    parser.add_argument('--test', help='テスト用：1つの名前を分割してみる')

    args = parser.parse_args()

    if args.test:
        # テストモード
        result = split_japanese_name(args.test)
        print(f"元の名前: {result['original']}")
        print(f"姓: {result['lastname']}")
        print(f"名: {result['firstname']}")
    else:
        # CSV処理
        count = process_csv(args.input_csv, args.output)
        print(f"✅ {count}件の名前を分割しました")
        print(f"出力ファイル: {args.output}")


if __name__ == '__main__':
    main()
