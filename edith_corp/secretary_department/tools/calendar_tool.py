#!/usr/bin/env python3
"""
秘書部門 - Google Calendar ツール
Google Calendar API を使って予定の取得・作成・削除を行う。
秘書エージェントが Bash で実行する。

認証: Search Console / GA4 と同じサービスアカウントを使用。
カレンダーオーナーがサービスアカウントのメールアドレスに
カレンダー共有（編集権限）を設定する必要がある。

Usage:
  python3 calendar_tool.py list --from 2026-02-09 --to 2026-02-10
  python3 calendar_tool.py list --from today --to tomorrow
  python3 calendar_tool.py list --from today --to week
  python3 calendar_tool.py create --title "打ち合わせ" --date 2026-02-15 --start 14:00 --end 15:00 [--description "議題: ..."]
  python3 calendar_tool.py delete --event-id <event_id>
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, date, timedelta

_THIS_DIR = Path(__file__).resolve().parent

# サービスアカウント認証情報（Search Console / GA4 と共用）
_CREDENTIALS_PATH = (
    _THIS_DIR.parent.parent
    / "blog_department"
    / "search_console"
    / "credentials"
    / "claude-agent-486408-2670454f8c9f.json"
)

# カレンダー設定
_CONFIG_PATH = _THIS_DIR.parent / "config" / "calendar_config.json"

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def _load_config() -> dict:
    if _CONFIG_PATH.exists():
        try:
            return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "calendar_id": "primary",
        "credentials_path": str(_CREDENTIALS_PATH),
        "timezone": "Asia/Tokyo",
    }


def _get_calendar_service():
    """Google Calendar APIサービスを初期化"""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        print(json.dumps({
            "status": "error",
            "error": "google-api-python-client がインストールされていません。pip install google-api-python-client google-auth で追加してください。",
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    config = _load_config()
    creds_path = config.get("credentials_path", str(_CREDENTIALS_PATH))

    if not Path(creds_path).exists():
        print(json.dumps({
            "status": "error",
            "error": f"認証情報ファイルが見つかりません: {creds_path}",
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    credentials = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES
    )

    service = build("calendar", "v3", credentials=credentials)
    return service, config


def _resolve_date(s: str) -> str:
    """'today', 'tomorrow', 'week' を日付文字列に変換"""
    today = date.today()
    if s == "today":
        return today.isoformat()
    elif s == "tomorrow":
        return (today + timedelta(days=1)).isoformat()
    elif s == "week":
        return (today + timedelta(days=7)).isoformat()
    return s


def cmd_list(args) -> dict:
    """期間内の予定一覧を取得"""
    service, config = _get_calendar_service()
    calendar_id = config.get("calendar_id", "primary")
    timezone = config.get("timezone", "Asia/Tokyo")

    date_from = _resolve_date(args.date_from)
    date_to = _resolve_date(args.date_to)

    # RFC3339 形式に変換（日付のみの場合は時刻を追加）
    time_min = f"{date_from}T00:00:00+09:00"
    time_max = f"{date_to}T23:59:59+09:00"

    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
            timeZone=timezone,
        ).execute()

        events = events_result.get("items", [])

        formatted = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))
            formatted.append({
                "id": event["id"],
                "title": event.get("summary", "(無題)"),
                "start": start,
                "end": end,
                "description": event.get("description", ""),
                "location": event.get("location", ""),
                "all_day": "date" in event["start"],
            })

        return {
            "status": "success",
            "events": formatted,
            "count": len(formatted),
            "period": {"from": date_from, "to": date_to},
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "events": [],
        }


def cmd_create(args) -> dict:
    """予定を作成"""
    service, config = _get_calendar_service()
    calendar_id = config.get("calendar_id", "primary")
    timezone = config.get("timezone", "Asia/Tokyo")

    event_body = {
        "summary": args.title,
    }

    if args.description:
        event_body["description"] = args.description

    if args.location:
        event_body["location"] = args.location

    if args.all_day:
        # 終日イベント
        event_body["start"] = {"date": args.date}
        end_date = args.end_date or args.date
        event_body["end"] = {"date": end_date}
    else:
        # 時間指定イベント
        if not args.start or not args.end:
            return {
                "status": "error",
                "error": "--start と --end を指定してください（例: --start 14:00 --end 15:00）。終日の場合は --all-day を使用。",
            }
        event_body["start"] = {
            "dateTime": f"{args.date}T{args.start}:00+09:00",
            "timeZone": timezone,
        }
        event_body["end"] = {
            "dateTime": f"{args.date}T{args.end}:00+09:00",
            "timeZone": timezone,
        }

    try:
        event = service.events().insert(
            calendarId=calendar_id,
            body=event_body,
        ).execute()

        return {
            "status": "success",
            "action": "created",
            "event": {
                "id": event["id"],
                "title": event.get("summary"),
                "start": event["start"].get("dateTime", event["start"].get("date")),
                "end": event["end"].get("dateTime", event["end"].get("date")),
                "link": event.get("htmlLink", ""),
            },
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def cmd_delete(args) -> dict:
    """予定を削除"""
    service, config = _get_calendar_service()
    calendar_id = config.get("calendar_id", "primary")

    try:
        service.events().delete(
            calendarId=calendar_id,
            eventId=args.event_id,
        ).execute()

        return {
            "status": "success",
            "action": "deleted",
            "deleted_event_id": args.event_id,
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def main():
    parser = argparse.ArgumentParser(description="秘書部門カレンダーツール")
    subparsers = parser.add_subparsers(dest="command", help="コマンド")

    # list
    p_list = subparsers.add_parser("list", help="予定一覧")
    p_list.add_argument("--from", dest="date_from", required=True, help="開始日 (YYYY-MM-DD or today/tomorrow)")
    p_list.add_argument("--to", dest="date_to", required=True, help="終了日 (YYYY-MM-DD or today/tomorrow/week)")

    # create
    p_create = subparsers.add_parser("create", help="予定作成")
    p_create.add_argument("--title", required=True, help="予定タイトル")
    p_create.add_argument("--date", required=True, help="日付 (YYYY-MM-DD)")
    p_create.add_argument("--start", help="開始時刻 (HH:MM)")
    p_create.add_argument("--end", help="終了時刻 (HH:MM)")
    p_create.add_argument("--description", help="詳細")
    p_create.add_argument("--location", help="場所")
    p_create.add_argument("--all-day", dest="all_day", action="store_true", help="終日イベント")
    p_create.add_argument("--end-date", dest="end_date", help="終了日 (終日イベント用、YYYY-MM-DD)")

    # delete
    p_delete = subparsers.add_parser("delete", help="予定削除")
    p_delete.add_argument("--event-id", dest="event_id", required=True, help="イベントID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "list": cmd_list,
        "create": cmd_create,
        "delete": cmd_delete,
    }

    try:
        result = commands[args.command](args)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    except Exception as e:
        import traceback
        print(json.dumps({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
