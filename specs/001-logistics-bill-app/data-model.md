# Data Model — Logistics Delivery Bill Management

**Date**: 2026-04-26
**Source**: [spec.md](./spec.md) Key Entities + Functional Requirements
**Storage**: PostgreSQL 16 with extensions `unaccent`, `pg_trgm`, `citext`. SQLAlchemy 2.x async ORM.

All money fields are `Numeric(14, 2)` in VND. All weights are `Numeric(12, 3)` in kg. All dimensions are `Numeric(8, 2)` in cm. All timestamps are stored as `TIMESTAMPTZ` in UTC and rendered in Asia/Ho_Chi_Minh on the client.

Vietnamese text columns use plain `TEXT` (not `VARCHAR(n)` — no useful length cap on Vietnamese names) with a functional GIN trigram index on `unaccent(lower(column))` where the column is searchable.

---

## Entity overview

```text
User (Nhân viên) ─────┐
                      │ created_by / updated_by / printed_by  (audit)
                      ▼
Customer (Khách hàng) ──┐ optional FK
                        ▼
Bill (Phiếu Gửi) ──────┬──> BillContentLine (1..N)  Nội dung gói hàng
                       ├──> BillFee (1..1)          Cước phí (embedded fields)
                       ├──> BillStatusEvent (1..N)  Lịch sử trạng thái
                       └──> AuditEvent (1..N)       Sự kiện kiểm toán

ServiceTier (Dịch vụ) ──┐ FK
                         ▼
                       Bill
```

A `Bill` carries a snapshot copy of sender/receiver attributes (name, address, district, province, phone) **inline** — the spec mandates that historical bills are immune to later edits to the source `Customer` (FR-020). The snapshot is stored on the `Bill` row itself, not via a foreign key.

---

## Tables

### `users` — Nhân viên (Staff)

| Column | Type | Notes |
|---|---|---|
| `id` | `BIGSERIAL` PK | |
| `username` | `CITEXT` UNIQUE NOT NULL | Login identifier |
| `full_name` | `TEXT` NOT NULL | Vietnamese-friendly |
| `password_hash` | `TEXT` NOT NULL | bcrypt via passlib |
| `role` | `TEXT` NOT NULL CHECK IN (`'staff'`, `'supervisor'`, `'admin'`) | v1 distinguishes staff vs supervisor (status updates) vs admin (user mgmt) |
| `is_active` | `BOOLEAN` NOT NULL DEFAULT `true` | Soft-deactivate |
| `created_at` | `TIMESTAMPTZ` NOT NULL DEFAULT `now()` | |
| `updated_at` | `TIMESTAMPTZ` NOT NULL DEFAULT `now()` | |

**Validation rules**:

- `username` must be 3–64 chars, ASCII letters/digits/underscore.
- `password_hash` is never returned via API.

---

### `customers` — Khách hàng

| Column | Type | Notes |
|---|---|---|
| `id` | `BIGSERIAL` PK | |
| `customer_code` | `CITEXT` UNIQUE NOT NULL | E.g. `NL500010`. Printed in "Mã KH" |
| `display_name` | `TEXT` NOT NULL | E.g. "KHL — Mr Lương Kho HN" |
| `address` | `TEXT` NOT NULL | Free-form Vietnamese address |
| `district` | `TEXT` NOT NULL | Quận/Huyện |
| `province` | `TEXT` NOT NULL | Tỉnh/TP |
| `phone` | `TEXT` NOT NULL | Vietnamese E.164 or local format; validated `^\+?[0-9 \-]{8,20}$` |
| `is_active` | `BOOLEAN` NOT NULL DEFAULT `true` | |
| `created_by` | `BIGINT` FK → `users.id` | |
| `created_at` | `TIMESTAMPTZ` NOT NULL DEFAULT `now()` | |
| `updated_at` | `TIMESTAMPTZ` NOT NULL DEFAULT `now()` | |

**Indexes**:

- `idx_customers_search_name` GIN on `unaccent(lower(display_name))` `gin_trgm_ops`.
- `idx_customers_search_address` GIN on `unaccent(lower(address))` `gin_trgm_ops`.

**Validation rules** (FR-018, FR-019):

- `customer_code` immutable after creation.
- Soft delete only (`is_active = false`) — historic bills depend on this row for reporting.

---

### `service_tiers` — Dịch vụ

Catalogue table. Seeded by Alembic with the values visible on the reference bill.

| Column | Type | Notes |
|---|---|---|
| `code` | `TEXT` PK | `CPN`, `PHT`, `DUONG_BO`, `T48H`, `NGUYEN_CHUYEN`, `KHAC`, `INTL_EXPRESS`, `INTL_ECONOMY`, `INTL_OTHER` |
| `display_name` | `TEXT` NOT NULL | Vietnamese label, e.g. "Đường bộ" |
| `scope` | `TEXT` NOT NULL CHECK IN (`'domestic'`, `'international'`) | Drives FR-005 (one or the other, not both) |
| `is_active` | `BOOLEAN` NOT NULL DEFAULT `true` | |

---

### `bills` — Phiếu Gửi

The core record. Many fields look duplicative with `customers`; this is intentional — it is the snapshot the spec requires.

| Column | Type | Notes |
|---|---|---|
| `id` | `BIGSERIAL` PK | |
| `tracking_number` | `TEXT` UNIQUE NOT NULL | E.g. `NL0011310`. Generated from sequence; see research §6 |
| `customer_code` | `CITEXT` NULL | Snapshot at creation. NULL if walk-in. Printed in "Mã KH" |
| `customer_id` | `BIGINT` FK → `customers.id` NULL | Soft link for analytics; not used by reprint |
| **Sender snapshot** | | |
| `sender_name` | `TEXT` NOT NULL | |
| `sender_address` | `TEXT` NOT NULL | |
| `sender_district` | `TEXT` NOT NULL | |
| `sender_province` | `TEXT` NOT NULL | |
| `sender_phone` | `TEXT` NOT NULL | |
| **Receiver snapshot** | | |
| `receiver_name` | `TEXT` NOT NULL | |
| `receiver_address` | `TEXT` NOT NULL | |
| `receiver_district` | `TEXT` NOT NULL | |
| `receiver_province` | `TEXT` NOT NULL | |
| `receiver_phone` | `TEXT` NOT NULL | |
| **Service** | | |
| `cargo_type` | `TEXT` NOT NULL CHECK IN (`'document'`, `'goods'`) | Tài liệu / Hàng hóa |
| `service_tier_code` | `TEXT` NOT NULL FK → `service_tiers.code` | Exactly one tier (FR-005) |
| **Fees** (all in VND) | | |
| `fee_main` | `NUMERIC(14,2)` NOT NULL DEFAULT 0 | Cước chính |
| `fee_fuel_surcharge` | `NUMERIC(14,2)` NOT NULL DEFAULT 0 | Phụ phí xăng dầu |
| `fee_other_surcharge` | `NUMERIC(14,2)` NOT NULL DEFAULT 0 | Phụ phí khác |
| `fee_vat` | `NUMERIC(14,2)` NOT NULL DEFAULT 0 | VAT |
| `fee_total` | `NUMERIC(14,2)` NOT NULL | Tổng cộng — must equal sum of the four (CHECK constraint) |
| `payer` | `TEXT` NOT NULL CHECK IN (`'sender'`, `'receiver'`) | FR-007 |
| **Lifecycle** | | |
| `status` | `TEXT` NOT NULL CHECK IN (`'da_tao'`, `'da_lay_hang'`, `'dang_van_chuyen'`, `'da_giao'`, `'hoan_tra'`, `'huy'`) DEFAULT `'da_tao'` | FR-016 |
| `delivered_at` | `TIMESTAMPTZ` NULL | Set when status becomes `da_giao` |
| `delivered_to_name` | `TEXT` NULL | Recipient who signed |
| `cancellation_reason` | `TEXT` NULL | Required when status becomes `huy` |
| **Audit & soft-locks** | | |
| `created_by` | `BIGINT` FK → `users.id` NOT NULL | |
| `created_at` | `TIMESTAMPTZ` NOT NULL DEFAULT `now()` | |
| `updated_by` | `BIGINT` FK → `users.id` NOT NULL | |
| `updated_at` | `TIMESTAMPTZ` NOT NULL DEFAULT `now()` | |
| `print_count` | `INTEGER` NOT NULL DEFAULT 0 | Increments on print/reprint |
| `last_printed_at` | `TIMESTAMPTZ` NULL | |
| `last_printed_by` | `BIGINT` FK → `users.id` NULL | |

**Constraints**:

- `CHECK (fee_total = fee_main + fee_fuel_surcharge + fee_other_surcharge + fee_vat)` — enforces FR-006 even if a buggy client tries to bypass it.
- `CHECK (status <> 'huy' OR cancellation_reason IS NOT NULL)`.
- `CHECK (status <> 'da_giao' OR delivered_at IS NOT NULL)`.

**Indexes**:

- `UNIQUE (tracking_number)`.
- `idx_bills_status_created_at` on `(status, created_at DESC)` for the bill list.
- `idx_bills_sender_phone` on `sender_phone`.
- `idx_bills_receiver_phone` on `receiver_phone`.
- `idx_bills_search_sender_name` GIN on `unaccent(lower(sender_name))` `gin_trgm_ops`.
- `idx_bills_search_receiver_name` GIN on `unaccent(lower(receiver_name))` `gin_trgm_ops`.
- `idx_bills_customer_code` on `customer_code`.

---

### `bill_content_lines` — Nội dung gói hàng

A bill has 1..N content lines. The reference paper bill shows up to 5 rows; the system supports more by listing them on the printed bill.

| Column | Type | Notes |
|---|---|---|
| `id` | `BIGSERIAL` PK | |
| `bill_id` | `BIGINT` FK → `bills.id` ON DELETE CASCADE NOT NULL | |
| `line_no` | `INTEGER` NOT NULL | 1-based ordering on the printed bill |
| `description` | `TEXT` NOT NULL | "Mô tả" |
| `quantity` | `INTEGER` NOT NULL CHECK > 0 | "Số lượng" |
| `weight_kg` | `NUMERIC(12,3)` NOT NULL CHECK >= 0 | "Trọng lượng" |
| `length_cm` | `NUMERIC(8,2)` NULL CHECK >= 0 | "Dài" |
| `width_cm` | `NUMERIC(8,2)` NULL CHECK >= 0 | "Rộng" |
| `height_cm` | `NUMERIC(8,2)` NULL CHECK >= 0 | "Cao" |

**Indexes**:

- `UNIQUE (bill_id, line_no)`.

---

### `bill_status_events` — Lịch sử trạng thái

Every status change appends a row.

| Column | Type | Notes |
|---|---|---|
| `id` | `BIGSERIAL` PK | |
| `bill_id` | `BIGINT` FK → `bills.id` ON DELETE CASCADE NOT NULL | |
| `from_status` | `TEXT` NULL | NULL on creation |
| `to_status` | `TEXT` NOT NULL | |
| `note` | `TEXT` NULL | Free text reason / signer name |
| `actor_id` | `BIGINT` FK → `users.id` NOT NULL | |
| `created_at` | `TIMESTAMPTZ` NOT NULL DEFAULT `now()` | |

**Indexes**: `idx_bill_status_events_bill` on `(bill_id, created_at)`.

---

### `audit_events` — Sự kiện kiểm toán

Generic audit trail covering operations beyond status changes (printing, customer edits, login, etc.).

| Column | Type | Notes |
|---|---|---|
| `id` | `BIGSERIAL` PK | |
| `actor_id` | `BIGINT` FK → `users.id` NULL | NULL allowed for system events |
| `action` | `TEXT` NOT NULL | `bill.created`, `bill.updated`, `bill.printed`, `bill.cancelled`, `customer.created`, `customer.updated`, `auth.login`, `auth.failed_login` |
| `entity_type` | `TEXT` NULL | `bill`, `customer`, `user` |
| `entity_id` | `BIGINT` NULL | |
| `details` | `JSONB` NULL | Diff or contextual data |
| `created_at` | `TIMESTAMPTZ` NOT NULL DEFAULT `now()` | |

**Indexes**: `idx_audit_events_entity` on `(entity_type, entity_id, created_at)`.

---

## Bill lifecycle (state machine)

```text
                  ┌────── huy (cancelled) ─────┐
                  │                            │
da_tao ──► da_lay_hang ──► dang_van_chuyen ──► da_giao
   │            │                  │
   │            └──────────────────┴──────► hoan_tra
   │
   └──► huy (cancel before pickup)
```

Allowed transitions (enforced in `bill_service`):

| From | Allowed to |
|---|---|
| `da_tao` | `da_lay_hang`, `huy` |
| `da_lay_hang` | `dang_van_chuyen`, `hoan_tra`, `huy` |
| `dang_van_chuyen` | `da_giao`, `hoan_tra` |
| `da_giao` | *(terminal)* |
| `hoan_tra` | *(terminal)* |
| `huy` | *(terminal)* |

Constraints:

- Transition to `da_giao` requires `delivered_at` (server-set to `now()` if absent) and `delivered_to_name`.
- Transition to `huy` requires non-empty `cancellation_reason`.
- `huy` not allowed once the package is in transit (status >= `dang_van_chuyen`).

---

## Sequences and constants

- `bill_tracking_seq` — `CREATE SEQUENCE bill_tracking_seq START 1 CACHE 50;`
  - Tracking number generator concatenates a configured prefix (default `NL`) + zero-padded 7-digit sequence value, then a 1-character checksum. Example: `NL0011310`. (Adjust width to taste; spec just requires uniqueness and human readability.)

---

## Mapping back to spec requirements

| Spec requirement | Where satisfied |
|---|---|
| FR-001 sender/receiver/contents/service/fees/payment/signatures | `bills` + `bill_content_lines` |
| FR-002 unique tracking number | `bills.tracking_number` UNIQUE + `bill_tracking_seq` |
| FR-003 customer code on bill | `bills.customer_code` |
| FR-004 cargo type | `bills.cargo_type` |
| FR-005 exactly one tier per bill | `bills.service_tier_code` (single FK) |
| FR-006 fee total = sum of components | `CHECK (fee_total = fee_main + ...)` |
| FR-007 payer | `bills.payer` |
| FR-008 mandatory-field validation | NOT NULL columns + Pydantic schemas |
| FR-013 search dimensions | trigram + plain indexes listed above |
| FR-014 diacritic-insensitive search | `unaccent` GIN indexes |
| FR-016 lifecycle status transitions | state machine in `bill_service`, CHECK on `status` |
| FR-017 audit trail | `audit_events` + `bill_status_events` |
| FR-018–FR-020 customer profiles + snapshot semantics | `customers` table + sender snapshot columns on `bills` |
| FR-025 / FR-026 authentication & attribution | `users` + `created_by`/`updated_by`/`actor_id` everywhere |
