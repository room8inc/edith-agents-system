# Room8システム開発部門

## 担当
Room8 Next.jsアプリ（`/Users/tsuruta/Documents/00_RnD/Room8`）の開発・保守・機能追加

## プロジェクト概要
- **フレームワーク**: Next.js 15 (App Router)
- **DB**: Supabase (PostgreSQL + RLS)
- **決済**: Stripe
- **ホスティング**: Vercel
- **リポジトリ**: git@github.com:room8inc/room8-system.git

## 主要依存
- `@supabase/ssr` / `@supabase/supabase-js` — DB・認証
- `stripe` / `@stripe/react-stripe-js` — 決済
- `@line/bot-sdk` — LINE Bot
- `googleapis` — Google Calendar
- `@vercel/kv` — キャッシュ

## 環境変数
```
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
STRIPE_SECRET_KEY
LINE_CHANNEL_SECRET
LINE_CHANNEL_ACCESS_TOKEN
GOOGLE_SERVICE_ACCOUNT_EMAIL
GOOGLE_PRIVATE_KEY (or GOOGLE_PRIVATE_KEY_BASE64)
GOOGLE_CALENDAR_ID
CRON_SECRET
```

---

## 課金方式の整理

| 種別 | 課金方式 | Stripe | 料金管理 |
|------|---------|--------|---------|
| 月額プラン | サブスクリプション | Stripe Subscription | `plans` テーブル |
| ドロップイン | 都度決済 | Stripe Payment Intent | `dropin_rates` テーブル |
| 会議室 | 都度決済 | Stripe Payment Intent | `meeting_rooms` テーブル（hourly_rate_regular / hourly_rate_non_regular） |

---

## DB設計（新構造 — 055_redesign_plans.sql）

### ★ 再設計の背景
サイトリニューアルで料金の見せ方が変わった:
- 旧: 9プラン（shared_office 3 + coworking 6）が別々に存在
- 新: **6つの時間帯プラン** × **ワークスペース or シェアオフィス(+3,300)**

内容は同じ。見せ方を統一するためにDB構造も合わせた。

### plans — 6つの時間帯プラン

```
code           | name               | workspace_price | shared_office_price | 平日時間        | 土日祝時間
---------------|--------------------|-----------------|--------------------|----------------|----------
holiday        | ホリデー            | 6,600           | 9,900              | —              | 9:00-17:00
night          | ナイト              | 6,600           | 9,900              | 17:00-22:00    | —
night_holiday  | ナイト&ホリデー      | 9,900           | 13,200             | 17:00-22:00    | 9:00-17:00
daytime        | デイタイム          | 11,000          | 14,300             | 9:00-17:00     | —
weekday        | ウィークデイ        | 13,200          | 16,500             | 9:00-22:00     | —
regular        | レギュラー          | 16,500          | 19,800             | 9:00-22:00     | 9:00-17:00
```

**plans テーブル主要カラム:**
- `code` TEXT UNIQUE — プラン識別キー（これが正式。LINE Bot等でも必ずこれを使う）
- `workspace_price` INTEGER — ワークスペース月額（税込）
- `shared_office_price` INTEGER — シェアオフィス月額（税込）= workspace_price + 3,300
- `weekday_start_time` / `weekday_end_time` — 平日利用時間（NULLなら平日利用不可）
- `weekend_start_time` / `weekend_end_time` — 土日祝利用時間（NULLなら土日祝利用不可）
- Stripe Price ID × 6: `stripe_price_id_ws_monthly`, `_ws_yearly`, `_ws_annual_prepaid`, `_so_monthly`, `_so_yearly`, `_so_annual_prepaid`
- 旧カラム（`price`, `start_time`, `end_time`, `features`, 旧stripe_price_id_*）も残存（フェーズ3で削除予定）

### 旧プラン → 新プラン対応表

| 旧code（DB） | 旧name | 新code | plan_type |
|-------------|--------|--------|-----------|
| entrepreneur | 起業家プラン | → bundlesテーブルへ | shared_office |
| regular | レギュラープラン | regular | shared_office |
| light | ライトプラン | weekday | shared_office |
| fulltime | フルタイムプラン | regular | workspace |
| weekday | ウィークデイプラン | weekday | workspace |
| daytime | デイタイムプラン | daytime | workspace |
| night_holiday | ナイト&ホリデープラン | night_holiday | workspace |
| night | ナイトプラン | night | workspace |
| holiday | ホリデープラン | holiday | workspace |

### bundles — セット商品（起業家パック等）

通常プランとは構造が異なるため別テーブル。

```
code          | name       | price   | ベースプラン  | 含まれるオプション
--------------|-----------|---------|-------------|------------------
entrepreneur  | 起業家パック | 55,000 | regular(SO) | 24h + 法人登記 + ロッカー大 + Web制作
```

- `included_plan_code` → plans.code（ベースとなるプラン）
- `included_plan_type` — 'shared_office'
- `included_options` TEXT[] — オプションcode配列
- Stripe Price ID × 3

### plan_options — オプション

```
code                  | name             | price
----------------------|-----------------|------
shared_office         | シェアオフィス     | 3,300
company_registration  | 法人登記          | 5,500
twenty_four_hours     | 24時間利用        | 5,500
locker_large          | ロッカー大        | 4,950
locker_small          | ロッカー小        | 2,750
printer               | プリンター使い放題 | 1,100
```

※ 旧 `plan_options_stripe_prices` テーブルも残存

### dropin_rates — ドロップイン料金

```
rate_type  | amount | description
-----------|--------|----------
hourly     | 420    | 1時間あたり
daily_max  | 2200   | 1日上限
```

### discount_rules — 割引ルール

```
code             | name            | type       | value
-----------------|-----------------|------------|------
yearly_contract  | 長期契約(1年)    | percentage | 20
annual_prepaid   | 年一括前払い     | percentage | 30
group_second     | グループ(2人目~) | percentage | 50
```

### user_plans — 契約管理（変更点）

既存カラムに加えて:
- `plan_type` TEXT — 'workspace' | 'shared_office'（どちらのタイプで契約したか）
- `bundle_id` UUID FK→bundles（起業家パック等のバンドル契約の場合）

### users — ユーザー管理
- `stripe_customer_id` — Stripe顧客ID
- `member_type` — 'regular' | 'dropin' | 'guest'
- `is_admin` — 管理者フラグ

### checkins — チェックイン/アウト（都度決済）
- ドロップイン料金自動計算
- 超過料金: 10分猶予、30分¥200、上限¥2,000

### meeting_rooms — 会議室定義
- `hourly_rate_regular` — 会員料金（¥1,100/h）
- `hourly_rate_non_regular` — 非会員料金（¥2,200/h）

### meeting_room_bookings — 会議室予約（都度決済）
- シェアオフィス会員: 月4h無料（`free_hours_used` で追跡）
- `google_calendar_event_id` でGCal連携

### line_user_states — LINE Bot状態管理
- 状態遷移: idle → asked_usage → asked_time → asked_address → showed_plan → asked_booking → confirmed

---

## APIルート

### Stripe決済
- `POST /api/stripe/create-customer` — 顧客作成
- `POST /api/stripe/create-payment-intent` — 支払い作成
- `POST /api/stripe/create-setup-intent` — カード登録
- `GET /api/stripe/check-payment-method` — 保存済みカード確認

### 契約管理（サブスク）
- `POST /api/plans/complete-contract` — 契約完了（入会金+初月+サブスク作成）
- `POST /api/plans/cancel` — 解約
- `POST /api/plans/cancel/revert` — 解約取消
- `POST /api/plans/change` — プラン変更

### チェックイン（都度決済）
- `POST /api/checkin/create-payment-intent` — ドロップイン決済
- `POST /api/checkout/calculate-and-refund` — 超過料金計算

### 会議室（都度決済）
- `POST /api/meeting-rooms/create-payment-intent` — 会議室決済

### Google Calendar
- `/api/calendar/*` — 可用性確認・イベント作成・削除・同期
- `/api/admin/google-calendar/*` — OAuth・設定管理

### LINE Bot
- `POST /api/line-webhook` — Webhook受信

### Cron
- `GET /api/cron/monthly-billing` — 月次請求
- `GET /api/cron/process-cancellations` — 解約・プラン変更処理
- `GET /api/cron/sync-google-calendar` — カレンダー同期

---

## Supabaseクライアント使い分け
- `lib/supabase/client.ts` — ブラウザ（クライアントコンポーネント用）
- `lib/supabase/server.ts` — サーバー（Server Components・API Routes用、RLS適用）
- `lib/supabase/service-client.ts` — サービスロール（RLSバイパス、Webhook等で使用）

## middleware.ts
- 認証除外: `/api/calendar/webhook-v2`, `/api/line-webhook`, `/api/cron/*`
- 保護パス: `/dashboard`, `/checkin`, `/profile`, `/meeting-rooms`, `/member-card`

## Stripe決済フロー（サブスク）
```
プラン選択 → 契約フォーム（plan_type選択・オプション・開始日・契約期間）
→ チェックアウト（入会金+初月日割り+オプション）
→ Stripe Payment Intent → カード決済
→ 契約完了 → user_plans作成（plan_type記録） → Stripeサブスク作成（翌月1日開始）
```

## ビジネスルール
- 入会金: ¥11,000（キャンペーンで割引可能）
- 解約: 15日までに申請 → 翌月末で終了
- 年間契約の途中解約: 違約金あり
- プラン変更: 15日までに申請 → 翌月から適用
- ドロップイン: `dropin_rates` テーブル参照（1h ¥420、1日上限 ¥2,200）
- 会議室: `meeting_rooms` テーブル参照（会員¥1,100/h、非会員¥2,200/h）

## 料金データの参照先
- **DB（各テーブル）が正**: 月額→plans、ドロップイン→dropin_rates、会議室→meeting_rooms
- **EDITH側 YAML（参考用）**: `edith_corp/shared_data/room8-pricing.yaml`
- コードにハードコードしない。DBから取得する。

---

## マイグレーション状況

### 完了済み
- `055_redesign_plans.sql` — プラン再設計（フェーズ1: テーブル追加・カラム追加・データ投入）
  - plans に workspace_price / shared_office_price / 時間帯カラム / 新Stripe Price IDカラム追加
  - user_plans に plan_type / bundle_id 追加
  - bundles, plan_options, dropin_rates, discount_rules テーブル新規作成
  - 既存データの新カラムへのマッピング
  - **未実行（Supabase SQL Editorで実行が必要）**

### 未着手
- フェーズ2: アプリコード切り替え
  - LINE Bot: ハードコード → DB参照に修正
  - プラン選択UI: `features.type` 分岐 → `plan_type` 選択に変更
  - 契約API: 新Stripe Price IDカラム参照
  - チェックイン時間外判定: weekday/weekend分割の時間カラムに対応
  - 会議室予約: シェアオフィス判定を `user_plans.plan_type` に変更
- フェーズ3: 旧データ移行・旧カラム削除（アプリ安定後）

---

## 影響ファイル一覧（フェーズ2で修正が必要）

| ファイル | 修正内容 |
|---------|---------|
| `app/plans/page.tsx` | features.type分岐 → 6プラン+plan_type選択UIに刷新 |
| `app/plans/plan-list.tsx` | 新カラム構造に対応 |
| `app/plans/plan-type-selector.tsx` | 不要になる可能性（削除orリダイレクト） |
| `app/plans/contract-form.tsx` | plan_type選択追加、オプション判定変更 |
| `app/plans/checkout/page.tsx` | 新Stripe Price IDカラム参照 |
| `app/api/plans/complete-contract/route.ts` | plan_type分岐、新Price ID、user_plans.plan_type保存 |
| `app/api/plans/change/route.ts` | plan_type対応 |
| `components/qr-scanner-modal.tsx` | weekday/weekend時間帯で時間外判定 |
| `app/admin/users/[userId]/user-plan-management.tsx` | 管理者画面対応 |
| `lib/line/plan-recommend.ts` | ハードコード → DB参照 |
| `lib/line/messages.ts` | DB料金で表示 |
| `scripts/create-stripe-test-prices.ts` | 新Price ID体系に対応 |
