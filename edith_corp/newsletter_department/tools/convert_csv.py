#!/usr/bin/env python3
"""
Room8の購読者リストをBrevo用フォーマットに変換
"""

import csv
import sys
from pathlib import Path


def convert_to_brevo_format(input_csv: str, output_csv: str, filter_segment: str = None):
    """
    Room8フォーマットをBrevoフォーマットに変換

    Args:
        input_csv: 入力CSVパス
        output_csv: 出力CSVパス
        filter_segment: セグメントフィルタ（例: "在籍"）
    """
    converted = []
    skipped = []

    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            email = row.get('EMAIL', '').strip()
            name = row.get('NAME', '').strip()
            segment = row.get('SEGMENT', '').strip()
            status = row.get('STATUS', '').strip()

            # メールアドレスが無効な場合はスキップ
            if not email or '@' not in email:
                skipped.append(f"無効なメール: {email}")
                continue

            # 退会者も含めてインポート（セグメント分けで後から制御可能）

            # セグメントフィルタ
            if filter_segment and segment != filter_segment:
                continue

            # Brevoフォーマットに変換
            brevo_row = {
                'EMAIL': email,
                'NAME': name,
                'SEGMENT': segment,
                'STATUS': status,
                'COMPANY': row.get('COMPANY', '').strip(),
                'PHONE': row.get('PHONE', '').strip()
            }

            converted.append(brevo_row)

    # Brevo用CSVに出力
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['EMAIL', 'NAME', 'SEGMENT', 'STATUS', 'COMPANY', 'PHONE']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(converted)

    return {
        'converted_count': len(converted),
        'skipped_count': len(skipped),
        'skipped': skipped
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Room8リストをBrevo用に変換')
    parser.add_argument('input_csv', help='入力CSVファイル')
    parser.add_argument('--output', '-o', default='brevo_converted.csv', help='出力CSVファイル')
    parser.add_argument('--segment', '-s', help='セグメントフィルタ（例: 在籍）')

    args = parser.parse_args()

    result = convert_to_brevo_format(args.input_csv, args.output, args.segment)

    print(f"✅ 変換完了: {result['converted_count']}件")
    print(f"⚠️  スキップ: {result['skipped_count']}件")

    if result['skipped']:
        print("\nスキップ詳細:")
        for skip in result['skipped'][:10]:  # 最初の10件のみ表示
            print(f"  - {skip}")

        if len(result['skipped']) > 10:
            print(f"  ... 他 {len(result['skipped']) - 10}件")

    print(f"\n出力ファイル: {args.output}")


if __name__ == '__main__':
    main()
