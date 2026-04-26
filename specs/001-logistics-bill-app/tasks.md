---
description: "Implementation tasks for the logistics delivery bill app"
---

# Tasks: Ứng dụng Quản lý Phiếu Gửi Vận Chuyển (Logistics Delivery Bill Management)

**Input**: Design documents from `/specs/001-logistics-bill-app/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/openapi.yaml](./contracts/openapi.yaml), [quickstart.md](./quickstart.md)

**Tests**: The spec did not explicitly request TDD, so per-story unit/contract tests are intentionally **omitted**. The Polish phase keeps a small targeted test set (concurrency, diacritic search, fee CHECK, contract drift) because those tests are the only way to claim Success Criteria SC-004, SC-005, SC-006 from the spec.

**Organization**: Tasks are grouped by user story (US1 P1, US2 P2, US3 P3) and follow the `backend/` + `frontend/` web-app layout pinned in `plan.md`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other [P] tasks in the same block (different files, no dependency on incomplete tasks).
- **[Story]**: Maps to a user story from `spec.md`: `[US1]` (P1 — Create bill), `[US2]` (P2 — Lookup/reprint/status), `[US3]` (P3 — Customer profiles). Setup, Foundational, and Polish phases have no story label.
- All paths are project-relative.

## Path Conventions

Web application layout from `plan.md` § Project Structure: `backend/app/...`, `frontend/src/...`, with `docker-compose.yml` at the repo root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Bring the monorepo skeleton up so backend and frontend work in parallel afterwards.

- [ ] T001 Create the top-level monorepo skeleton: `backend/`, `frontend/`, `docker-compose.yml`, root `README.md` referencing `specs/001-logistics-bill-app/quickstart.md`.
- [ ] T002 [P] Initialize the backend Python project at `backend/pyproject.toml` with dependencies pinned in `research.md` §1–§8 (`fastapi`, `uvicorn[standard]`, `sqlalchemy>=2`, `asyncpg`, `alembic`, `pydantic>=2`, `pydantic-settings`, `python-jose[cryptography]`, `passlib[bcrypt]`, `python-multipart`, `weasyprint`, `qrcode`, `python-barcode`, `unidecode`, `structlog`, plus `[dev]` extras `pytest`, `pytest-asyncio`, `httpx`, `testcontainers[postgres]`, `ruff`, `black`).
- [ ] T003 [P] Initialize the frontend project at `frontend/package.json` via Vite + React 18 with the dependencies pinned in `research.md` §9–§12 (`react`, `react-dom`, `react-router-dom`, `@tanstack/react-query`, `axios`, `antd`, `dayjs`, `react-hook-form`, `zod`, `@hookform/resolvers`, `jsbarcode`, `qrcode.react`, `react-to-print`, plus dev: `vite`, `@vitejs/plugin-react`, `vitest`, `@testing-library/react`, `msw`, `@playwright/test`, `eslint`, `prettier`).
- [ ] T004 [P] Configure backend tooling: `backend/ruff.toml` and `backend/.editorconfig` per `research.md`; ensure `ruff` + `black` agree on line-length 100.
- [ ] T005 [P] Configure frontend tooling: `frontend/.eslintrc.cjs`, `frontend/.prettierrc`, `frontend/vite.config.js` (with `server.proxy` for `/api` → `http://localhost:8000` in dev).
- [ ] T006 [P] Create `backend/.env.example` with the keys listed in `quickstart.md` §2 (`DATABASE_URL`, `JWT_SECRET`, `JWT_ALGORITHM`, `ACCESS_TOKEN_TTL_MINUTES`, `REFRESH_TOKEN_TTL_DAYS`, `TRACKING_NUMBER_PREFIX`, `CARRIER_NAME`, `CARRIER_HOTLINE`, `CARRIER_WEBSITE`, `CARRIER_EMAIL`).
- [ ] T007 [P] Create `frontend/.env.example` with `VITE_API_BASE_URL=http://localhost:8000/api/v1`.
- [ ] T008 [P] Copy/optimize the carrier logo from `image_data/logo.jpg` to `frontend/src/assets/logo.png` and `backend/app/static/logo.png` (keep aspect ratio; PNG with transparent background if possible).
- [ ] T009 Author `docker-compose.yml` at the repo root with three services per `quickstart.md` §3 (`db`: postgres:16 with init script enabling `unaccent`, `pg_trgm`, `citext`; `backend`: build from `backend/Dockerfile`, depends on db; `frontend`: build from `frontend/Dockerfile`, mounts source for HMR).
- [ ] T010 [P] Author `backend/Dockerfile` (Python 3.11 slim + WeasyPrint native deps `libpango-1.0-0 libpangoft2-1.0-0 libcairo2`, install Be Vietnam Pro font for diacritic-faithful PDFs).
- [ ] T011 [P] Author `frontend/Dockerfile` (Node 20 LTS, `npm ci`, expose 5173, `npm run dev -- --host`).

**Checkpoint**: `docker compose up -d --build` brings all three services up. Backend serves a 404 (no routes yet); frontend serves the Vite dev page.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Wire database, configuration, auth, i18n catalogues, and shared infrastructure that every user story depends on. **No user-story work begins until this phase is checkpointed.**

### Backend foundations

- [ ] T012 Create `backend/app/main.py` — FastAPI app with CORS allowing `http://localhost:5173` in dev, the v1 API router mount at `/api/v1`, and the global exception handler stub.
- [ ] T013 [P] Create `backend/app/core/config.py` using `pydantic-settings` to read `.env`; expose strongly-typed `settings` object.
- [ ] T014 [P] Create `backend/app/core/i18n.py` — Vietnamese error-message catalogue keyed by `error_code` (e.g. `BILL_NOT_FOUND` → "Không tìm thấy phiếu gửi.", `FEE_TOTAL_MISMATCH` → "Tổng cước không khớp với tổng các khoản.").
- [ ] T015 Create `backend/app/core/exceptions.py` + register handlers in `main.py`: convert Pydantic `ValidationError` and domain `AppError` instances into the `ErrorResponse` schema from `contracts/openapi.yaml`, translating messages via `core/i18n.py`.
- [ ] T016 [P] Create `backend/app/core/security.py` — `hash_password`, `verify_password` (passlib bcrypt), `create_access_token`, `create_refresh_token`, `decode_token` (python-jose, HS256, TTLs from settings).
- [ ] T017 [P] Create `backend/app/db/base.py` — SQLAlchemy 2.x `DeclarativeBase` with naming conventions for indexes/constraints.
- [ ] T018 [P] Create `backend/app/db/session.py` — async engine via `asyncpg`, `AsyncSession` factory, `get_db` dependency.
- [ ] T019 Initialize Alembic at `backend/alembic/` (configure `env.py` for async + autogenerate using `app.db.base.Base.metadata`); create `backend/alembic.ini`.
- [ ] T020 First Alembic migration `backend/alembic/versions/0001_init_extensions.py` — `CREATE EXTENSION IF NOT EXISTS unaccent; pg_trgm; citext;` plus the `bill_tracking_seq` SEQUENCE per `data-model.md`.
- [ ] T021 [P] Create `backend/app/models/user.py` — `User` model per `data-model.md` `users` table (id, username CITEXT unique, full_name, password_hash, role check, is_active, timestamps).
- [ ] T022 [P] Create `backend/app/models/service_tier.py` — `ServiceTier` model per `data-model.md` (code PK, display_name, scope check, is_active).
- [ ] T023 [P] Create `backend/app/models/audit_event.py` — `AuditEvent` model per `data-model.md` (action, entity_type, entity_id, JSONB details, actor_id FK).
- [ ] T024 Alembic migration `backend/alembic/versions/0002_users_service_tiers_audit.py` — create `users`, `service_tiers`, `audit_events` tables with indexes; seed `service_tiers` rows (`CPN`, `PHT`, `DUONG_BO`, `T48H`, `NGUYEN_CHUYEN`, `KHAC`, `INTL_EXPRESS`, `INTL_ECONOMY`, `INTL_OTHER`) with their Vietnamese display names.
- [ ] T025 [P] Create `backend/app/crud/audit.py` — `log_event(db, actor_id, action, entity_type, entity_id, details)` helper, used by every mutation.
- [ ] T026 [P] Create `backend/app/crud/user.py` — `get_by_username`, `authenticate(username, password)`, `create_user`.
- [ ] T027 [P] Create `backend/app/services/tracking.py` — `next_tracking_number()` reads `bill_tracking_seq` via SQLAlchemy `text("SELECT nextval('bill_tracking_seq')")` and formats as `{TRACKING_NUMBER_PREFIX}{seq:07d}` per `research.md` §6.
- [ ] T028 Create `backend/app/api/v1/deps.py` — `get_current_user` dependency that decodes the JWT bearer, loads the user, and 401s with Vietnamese error on failure; `require_role(role)` factory.
- [ ] T029 [P] Create `backend/app/schemas/auth.py` — `LoginRequest`, `RefreshRequest`, `TokenPair`, `User` (read) Pydantic models matching `contracts/openapi.yaml`.
- [ ] T030 [P] Create `backend/app/schemas/common.py` — `ErrorResponse`, paging primitives (`Page[T]` generic if helpful).
- [ ] T031 [P] Create `backend/app/schemas/service_tier.py` — `ServiceTier` Pydantic schema.
- [ ] T032 Create `backend/app/api/v1/auth.py` — `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me`; logs `auth.login` / `auth.failed_login` audit events.
- [ ] T033 Create `backend/app/api/v1/service_tiers.py` — `GET /service-tiers?scope=domestic|international`.
- [ ] T034 Wire all routers into `backend/app/main.py` under `/api/v1` and add structured-logging middleware (`structlog` JSON formatter, request-ID per request).
- [ ] T035 Create `backend/app/scripts/seed.py` — creates an admin user (`admin` / `admin123` for dev) and verifies service-tier seed (idempotent).

### Frontend foundations

- [ ] T036 [P] Create `frontend/src/i18n/vi.js` — single Vietnamese string catalogue; export a `t(path)` helper. Seed with auth, layout, common form labels (`'Lưu'`, `'Huỷ'`, `'Tạo phiếu gửi'`, `'Tra cứu'`, `'Đăng nhập'`, `'Đăng xuất'`, etc.).
- [ ] T037 [P] Create `frontend/src/styles/theme.js` — Ant Design theme tokens with brand red/black extracted from the supplied logo; export a configured `<ConfigProvider locale={viVN} theme={theme}>` wrapper component.
- [ ] T038 [P] Create `frontend/src/lib/format.js` — `formatVND(n)`, `formatWeight(n)`, `formatViDate(d)`, `parseViNumber(str)` (accepts comma decimals).
- [ ] T039 [P] Create `frontend/src/lib/diacritics.js` — small helpers for client-side fallback (server is the source of truth for search; this is for sort/highlight only).
- [ ] T040 Create `frontend/src/api/client.js` — Axios instance reading `VITE_API_BASE_URL`; request interceptor adds `Authorization: Bearer <access>` from auth context; response interceptor on 401 calls `/auth/refresh` and retries once, else logs out.
- [ ] T041 [P] Create `frontend/src/api/auth.js` — `login(username, password)`, `refresh(refreshToken)`, `me()`.
- [ ] T042 Create `frontend/src/auth/AuthContext.jsx` — provider holding access token in memory, refresh token in `localStorage`, plus `login`, `logout`, `currentUser` API.
- [ ] T043 Create `frontend/src/auth/ProtectedRoute.jsx` — redirects to `/dang-nhap` when not authenticated.
- [ ] T044 Create `frontend/src/features/auth/pages/LoginPage.jsx` — Vietnamese login form using Ant Design `Form` + `vi_VN` locale.
- [ ] T045 [P] Create `frontend/src/components/layout/AppShell.jsx` — sidebar + header with Vietnamese menu items (`Phiếu Gửi`, `Khách hàng`, `Đăng xuất`), carrier logo from `assets/logo.png`.
- [ ] T046 Create `frontend/src/routes/index.jsx` — react-router routes `/dang-nhap`, `/`, `/phieu-gui`, `/phieu-gui/tao-moi`, `/phieu-gui/:id`, `/khach-hang`; wire `ProtectedRoute` for all but login.
- [ ] T047 Create `frontend/src/main.jsx` and `frontend/src/App.jsx` — mount `<QueryClientProvider>`, `<AntdConfigProvider>`, `<AuthProvider>`, `<RouterProvider>`.

**Checkpoint**: User can `docker compose up`, navigate to `http://localhost:5173`, log in as `admin`/`admin123`, see the empty Vietnamese app shell. `GET /api/v1/auth/me` returns the user. `GET /api/v1/service-tiers` returns the seeded catalogue.

---

## Phase 3: User Story 1 - Tạo phiếu gửi mới cho lô hàng (Priority: P1) 🎯 MVP

**Goal**: A logged-in counter staff member can fill the bill form (sender, receiver, contents, service, fees, payer), save it, and produce a Vietnamese print-ready bill that visually matches `image_data/bill_format.jpg`, with a unique tracking number and a scannable barcode + QR.

**Independent Test**: Log in → click "Tạo phiếu gửi" → fill the full form including diacritic Vietnamese names and `200,00 kg` weight → click "Lưu & In phiếu" → see the print preview that matches the reference layout → confirm a tracking number was generated and the bill is retrievable via `GET /api/v1/bills/{id}`.

### Backend — bill data model and creation

- [ ] T048 [P] [US1] Create `backend/app/models/bill.py` — `Bill` SQLAlchemy model per `data-model.md` `bills` table (sender/receiver snapshot columns, fees, service_tier_code FK, payer, lifecycle, audit, `print_count`).
- [ ] T049 [P] [US1] Create `backend/app/models/bill_content_line.py` — `BillContentLine` model (FK to bill, line_no UNIQUE per bill, qty, weight, dimensions).
- [ ] T050 [P] [US1] Create `backend/app/models/bill_status_event.py` — `BillStatusEvent` model (from_status, to_status, note, actor_id, created_at).
- [ ] T051 [US1] Alembic migration `backend/alembic/versions/0003_bills.py` — create `bills`, `bill_content_lines`, `bill_status_events`; add CHECKs for `fee_total = sum(...)`, `status='huy' ⇒ cancellation_reason`, `status='da_giao' ⇒ delivered_at`; create `idx_bills_status_created_at` and the GIN trigram indexes on `unaccent(lower(sender_name))` / `unaccent(lower(receiver_name))` / `unaccent(lower(sender_address))` / `unaccent(lower(receiver_address))`; create `idx_bills_sender_phone` / `idx_bills_receiver_phone` / `idx_bills_customer_code`.
- [ ] T052 [P] [US1] Create `backend/app/schemas/bill.py` — `Party`, `BillContentLine`, `FeeBreakdown`, `BillCreate`, `Bill`, `BillStatus` enum, `BillStatusUpdate`, `BillStatusEvent`, matching `contracts/openapi.yaml`. Include a Pydantic validator on `FeeBreakdown` that rejects when `fee_total != main + fuel + other + vat`.
- [ ] T053 [US1] Create `backend/app/crud/bill.py` — `create_bill(db, *, payload, actor_id)` inserts the bill row with sender/receiver snapshot + content lines in one transaction, allocates the tracking number via `services/tracking.next_tracking_number`, writes a `da_tao` row in `bill_status_events`, and emits a `bill.created` audit event; `get_bill(db, bill_id)` returns the bill with content lines eager-loaded.
- [ ] T054 [US1] Create `backend/app/services/bill_service.py` — `create_bill(payload, actor)` wraps `crud.bill.create_bill` and additionally enforces FR-005 (cargo_type+tier scope match — domestic tiers go with domestic bills, international with international), FR-006 (fee total), FR-007 (payer), and the snapshot-from-customer rule (when `customer_id` provided, copy customer fields into sender block server-side and freeze `customer_code`).
- [ ] T055 [US1] Create `backend/app/api/v1/bills.py` and add `POST /api/v1/bills` endpoint and `GET /api/v1/bills/{bill_id}`; wire it into `main.py`.

### Backend — print rendering

- [ ] T056 [P] [US1] Create `backend/app/static/bill_template.html` — Jinja2 HTML template that exactly reproduces `image_data/bill_format.jpg` layout: header with carrier logo and "PHIẾU GỬI" + tracking barcode + QR code on the right, two-column sender/receiver blocks, content grid (Mô tả/Số lượng/Trọng lượng/Kích thước), fee block (Cước chính/Phụ phí xăng dầu/Phụ phí khác/VAT/Tổng cộng), service-tier checkboxes (cargo type + tier), payer checkboxes, signature lines with Vietnamese date format ("…ngày <DD> tháng <MM> năm <YYYY>"), Vietnamese footer (Hotline/Website/Email + disclaimer text). Loads `Be Vietnam Pro` font.
- [ ] T057 [P] [US1] Create `backend/app/static/print.css` — print-only stylesheet for both browser printing and WeasyPrint (`@page` size, margins, hides screen-only elements).
- [ ] T058 [US1] Create `backend/app/services/print_service.py` — `render_bill_html(bill)` returns the Jinja-rendered HTML; `render_bill_pdf(bill)` runs that through WeasyPrint and returns the PDF bytes; barcode (Code128) and QR are inlined as SVG/PNG via `python-barcode` + `qrcode`.
- [ ] T059 [US1] Add `GET /api/v1/bills/{bill_id}/print?as=pdf|html` endpoint to `bills.py`; on each call, increment `print_count`, set `last_printed_at`/`last_printed_by`, and emit a `bill.printed` audit event.

### Frontend — bill creation page

- [ ] T060 [P] [US1] Create `frontend/src/api/bills.js` — `createBill(payload)`, `getBill(id)`, `downloadBillPdf(id)`.
- [ ] T061 [P] [US1] Create `frontend/src/features/bills/schema.js` — Zod schema mirroring `BillCreate` (Party, content lines, fee breakdown, payer, cargo_type+tier mutual exclusion). All error messages in Vietnamese.
- [ ] T062 [P] [US1] Create `frontend/src/features/bills/components/SenderBlock.jsx` — fields: name, address, district, province, phone. Uses Ant Design `Form.Item`. Vietnamese labels.
- [ ] T063 [P] [US1] Create `frontend/src/features/bills/components/ReceiverBlock.jsx` — same structure as SenderBlock.
- [ ] T064 [P] [US1] Create `frontend/src/features/bills/components/ContentTable.jsx` — editable table of content lines (add/remove rows), columns Mô tả / Số lượng / Trọng lượng (kg) / Dài / Rộng / Cao (cm); accepts comma-decimal input via Ant Design `InputNumber decimalSeparator=","`.
- [ ] T065 [P] [US1] Create `frontend/src/features/bills/components/ServiceTierSelector.jsx` — radio-group for cargo_type (`document` / `goods`); fetches `/service-tiers` and presents two mutually exclusive checkbox columns (Trong nước / Quốc tế); enforces FR-005 by disabling the other column when one is selected.
- [ ] T066 [P] [US1] Create `frontend/src/features/bills/components/FeeBreakdownInput.jsx` — four numeric inputs (cước chính, phụ phí xăng dầu, phụ phí khác, VAT) and a read-only `Tổng cộng` that auto-recomputes; payer radio (`Người gửi thanh toán` / `Người nhận thanh toán`).
- [ ] T067 [US1] Create `frontend/src/features/bills/pages/BillCreatePage.jsx` — composes the blocks above with React Hook Form + Zod resolver; "Lưu & In phiếu" button submits via React Query mutation calling `createBill`; on success, opens the print preview (T069) and navigates to `/phieu-gui/:id`.
- [ ] T068 [P] [US1] Create `frontend/src/features/bills/components/BillPrintView.jsx` — a React component that renders the same layout as `bill_template.html` (Vietnamese labels, sender/receiver/content/fees/signatures), embeds a JsBarcode `<svg>` for the tracking number and a `qrcode.react` `<QRCodeSVG>` for the tracking URL, applies `print.css` print rules.
- [ ] T069 [US1] Wire `react-to-print` in `BillCreatePage.jsx`: on success, render an off-screen `BillPrintView` and trigger the print dialog automatically; offer a "Tải PDF" button that calls `downloadBillPdf(id)` to get the WeasyPrint PDF.
- [ ] T070 [US1] Add the `/phieu-gui/tao-moi` route to `routes/index.jsx`; sidebar menu item navigates here. Make sure all toasts/validation messages come from `i18n/vi.js`.

**Checkpoint**: User Story 1 fully functional. Counter staff can log in, create a complete bill, see it printed/previewed in Vietnamese with the correct layout, and retrieve it from the API. SC-001 (90 s creation), SC-002 (Vietnamese-only UI), SC-003 (layout fidelity) are testable now. SC-006 (no tracking-number collisions) verified by Polish tasks.

---

## Phase 4: User Story 2 - Tra cứu, in lại và cập nhật trạng thái phiếu gửi (Priority: P2)

**Goal**: Staff can search bills by tracking number / customer code / phone / name (with diacritic-insensitive matching), view detail with full status history, transition status through the lifecycle, and reprint at will.

**Independent Test**: After creating several bills via US1, type `nguyen thi hoa` (no diacritics) into the search bar — the bill with `Nguyễn Thị Hoa` is returned. Open detail, click "Cập nhật trạng thái" → Đã giao with a signer name → status timeline updates and the bill appears with the new status in the list. Click "In lại" → identical PDF downloads and `print_count` increments.

### Backend

- [ ] T071 [P] [US2] Create `backend/app/services/search_service.py` — builds the SQLAlchemy where-clause for bill search: applies `unaccent(lower(...))` to user input and uses `% (similarity)` against the GIN-indexed columns; supports filters `status`, `customer_code`, `created_from`, `created_to`, `q` (diacritic-insensitive partial match against tracking number, sender/receiver name, sender/receiver phone).
- [ ] T072 [P] [US2] Extend `backend/app/schemas/bill.py` (or `common.py`) — add `BillPage` paged response matching `contracts/openapi.yaml`.
- [ ] T073 [US2] Extend `backend/app/crud/bill.py` — `list_bills(db, *, q, status, customer_code, created_from, created_to, page, page_size)` returns `(items, total)`; `get_by_tracking_number(tracking_number)`; `get_events(bill_id)` returns status events + audit events.
- [ ] T074 [US2] Extend `backend/app/services/bill_service.py` — `transition_status(bill_id, payload, actor)` validates the state-machine table from `data-model.md`, requires `delivered_to_name` for `da_giao` and `cancellation_reason` for `huy`, refuses `huy` once status >= `dang_van_chuyen`, writes a `bill_status_events` row, emits a `bill.updated` audit event.
- [ ] T075 [US2] Extend `backend/app/api/v1/bills.py` — add `GET /api/v1/bills` (filters + pagination), `GET /api/v1/bills/by-tracking/{tracking_number}`, `POST /api/v1/bills/{bill_id}/status`, `GET /api/v1/bills/{bill_id}/events`.

### Frontend

- [ ] T076 [P] [US2] Extend `frontend/src/api/bills.js` — `listBills(params)`, `getBillByTracking(tn)`, `updateStatus(id, payload)`, `getBillEvents(id)`.
- [ ] T077 [P] [US2] Create `frontend/src/features/bills/pages/BillListPage.jsx` — Ant Design `Table` of bills with columns Mã VD / Người gửi / Người nhận / Trạng thái / Tổng cước / Ngày tạo; debounced search input ("Tìm theo mã VD, tên, SĐT..."); filter dropdowns for trạng thái + ngày tạo; uses React Query `useInfiniteQuery` or paged `useQuery`.
- [ ] T078 [P] [US2] Create `frontend/src/features/bills/pages/BillDetailPage.jsx` — read-only view of bill data + status timeline (status_events) + audit log; "In lại" button (calls `downloadBillPdf`) and "Cập nhật trạng thái" button.
- [ ] T079 [P] [US2] Create `frontend/src/features/bills/components/StatusUpdateDrawer.jsx` — drawer/dialog with Vietnamese labels: select target status (from allowed transitions for the current status), capture `delivered_to_name` for Đã giao or `cancellation_reason` for Huỷ, optional `note`.
- [ ] T080 [US2] Add the `/phieu-gui` (list) and `/phieu-gui/:id` (detail) routes; sidebar menu links to the list. Default landing page for authenticated users is the bill list.
- [ ] T081 [US2] Wire diacritic-insensitive UX: empty-state message in Vietnamese ("Không tìm thấy phiếu gửi nào."), highlight matched substrings using `lib/diacritics.js`.

**Checkpoint**: User Story 2 fully functional. Search/lookup, status transitions, reprints all work end-to-end with audit trail. Spec SC-005 (diacritic-insensitive search) and SC-009 (≤2 s reprint/status) become measurable.

---

## Phase 5: User Story 3 - Lưu hồ sơ khách hàng thường xuyên để tự điền (Priority: P3)

**Goal**: Save corporate / repeat customers as profiles. When creating a new bill, pick a customer from a searchable list to auto-fill the sender block. Customer code prints in the "Mã KH" field. Profile edits do not retroactively change historical bills.

**Independent Test**: Create a customer profile (`NL500010` / `KHL — Mr Lương Kho HN` / address / phone). Start a new bill, click "Chọn khách hàng", pick the profile — sender block auto-fills and the customer code goes into the print preview's "Mã KH" field. Edit the customer's address; existing bills still show the old address; new bills use the new address.

### Backend

- [ ] T082 [P] [US3] Create `backend/app/models/customer.py` — `Customer` model per `data-model.md` (customer_code CITEXT unique, display_name, address, district, province, phone, is_active, created_by, timestamps).
- [ ] T083 [US3] Alembic migration `backend/alembic/versions/0004_customers.py` — create `customers`; add GIN trigram indexes on `unaccent(lower(display_name))` and `unaccent(lower(address))`; add FK column `bills.customer_id` (NULLable) — note the column was already declared in the bill model in T048; this migration just adds the index.
- [ ] T084 [P] [US3] Create `backend/app/schemas/customer.py` — `CustomerBase`, `CustomerCreate`, `CustomerUpdate`, `Customer`, `CustomerPage` matching `contracts/openapi.yaml`.
- [ ] T085 [US3] Create `backend/app/crud/customer.py` — `list_customers(q, is_active, page, page_size)` (diacritic-insensitive), `get`, `create` (unique customer_code), `update` (cannot change customer_code), `deactivate` (soft delete).
- [ ] T086 [US3] Create `backend/app/services/customer_service.py` — wraps CRUD with `customer.created`/`customer.updated` audit events.
- [ ] T087 [US3] Create `backend/app/api/v1/customers.py` — `GET /api/v1/customers`, `POST /api/v1/customers`, `GET /api/v1/customers/{id}`, `PATCH /api/v1/customers/{id}`, `DELETE /api/v1/customers/{id}`; wire into `main.py`.
- [ ] T088 [US3] Extend `backend/app/services/bill_service.py` — when `BillCreate.customer_id` is provided, snapshot the customer's `display_name`, `address`, `district`, `province`, `phone` into the sender block server-side and freeze `customer_code`; ignore any conflicting client-supplied sender values.

### Frontend

- [ ] T089 [P] [US3] Create `frontend/src/api/customers.js` — `listCustomers(params)`, `getCustomer(id)`, `createCustomer(payload)`, `updateCustomer(id, payload)`, `deactivateCustomer(id)`.
- [ ] T090 [P] [US3] Create `frontend/src/features/customers/pages/CustomerListPage.jsx` — Ant Design table with search, status filter, "Thêm mới" button.
- [ ] T091 [P] [US3] Create `frontend/src/features/customers/components/CustomerFormDrawer.jsx` — create/edit drawer with Vietnamese labels (Mã KH, Tên hiển thị, Địa chỉ, Quận/Huyện, Tỉnh/TP, Số điện thoại); customer_code field disabled in edit mode.
- [ ] T092 [P] [US3] Create `frontend/src/features/customers/components/CustomerPicker.jsx` — typeahead dropdown for use inside the bill SenderBlock; searches via `listCustomers({ q })` with debounce; selecting a customer fires `onSelect(customer)`.
- [ ] T093 [US3] Update `frontend/src/features/bills/components/SenderBlock.jsx` — add a "Chọn khách hàng" button that opens the `CustomerPicker`; on select, populates the sender fields (name, address, district, province, phone) via React Hook Form `setValue`; stores the chosen `customer_id` in the form so the backend can snapshot.
- [ ] T094 [US3] Add the `/khach-hang` route + sidebar entry; wire `CustomerListPage`.

**Checkpoint**: User Story 3 fully functional. SC-008 (95% of returning-customer bills use auto-fill) becomes measurable in production.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, the targeted tests required to verify Success Criteria, performance verification, and Vietnamese-UI audit.

- [ ] T095 [P] Backend test `backend/tests/integration/test_tracking_concurrency.py` — verifies SC-006: spawn ~200 concurrent `create_bill` calls (parameterizable up to 10 000 in CI's slow-tier), assert all tracking numbers are unique and sequential.
- [ ] T096 [P] Backend test `backend/tests/integration/test_diacritic_search.py` — verifies SC-005: seed bills with names like `Nguyễn Thị Hoa`, `Lương Kho HN`, `Bắc Ninh`; query without diacritics; assert ≥99% recall on a labelled sample.
- [ ] T097 [P] Backend test `backend/tests/integration/test_fee_total_check.py` — attempts to insert a bill where `fee_total != sum(...)` directly into the DB; expects the `CHECK` to reject it. Plus a test going through the API that asserts the Vietnamese error message and 400.
- [ ] T098 [P] Backend test `backend/tests/contract/test_openapi_drift.py` — asserts that the FastAPI-generated OpenAPI matches `specs/001-logistics-bill-app/contracts/openapi.yaml` for paths/methods/required schemas; fails the build on drift.
- [ ] T099 [P] Backend test `backend/tests/integration/test_status_state_machine.py` — exercises every legal and illegal transition from the matrix in `data-model.md`; asserts illegal ones return 409 with Vietnamese messages.
- [ ] T100 [P] Frontend Playwright smoke `frontend/tests/e2e/create-bill.spec.js` — login → create bill with diacritic Vietnamese inputs → assert print preview opens and contains rendered Vietnamese text + barcode/QR; tagged so CI can opt-out.
- [ ] T101 Performance check `backend/tests/perf/test_bill_list_perf.py` — seeds 100 000 bills, runs a paginated list query with `q=Nguyễn`, asserts p95 ≤ 1000 ms (SC-004).
- [ ] T102 [P] Vietnamese-only UI audit script `frontend/scripts/audit-vi-strings.mjs` — greps the source for hardcoded Latin-only English strings outside `i18n/vi.js`; lists offenders. Run in CI.
- [ ] T103 [P] Update `README.md` at the repo root with the Vietnamese-language project description and a pointer to `specs/001-logistics-bill-app/quickstart.md`.
- [ ] T104 Manually walk through `quickstart.md` §5 end-to-end on a fresh Compose environment; record any deviation as a follow-up task.
- [ ] T105 [P] Add `docker-compose.prod.yml.example` showing the reverse-proxy / TLS / persistent-volume shape so the operator can stand up a single-tenant prod environment.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies; start immediately.
- **Foundational (Phase 2)**: requires Phase 1. Blocks every user story.
- **User Story 1 (Phase 3, P1, MVP)**: requires Phase 2. After completion, the system is shippable as MVP.
- **User Story 2 (Phase 4, P2)**: requires Phase 2 (and the bill model from US1, since search/status operate on bills). Implementable in parallel with US3 once US1's bill model migration (T051) is in.
- **User Story 3 (Phase 5, P3)**: requires Phase 2 (and the bill model from US1 to wire customer_id snapshot). Implementable in parallel with US2.
- **Polish (Phase 6)**: requires whichever user stories you intend to ship — at minimum US1 for the MVP test set; the perf test (T101) and contract test (T098) cover all stories.

### Story-level dependencies

- US1 owns the bill model and migration (T048–T051). US2 and US3 read but do not redefine these.
- US3 adds an Alembic migration that depends on the bills table existing (T051 must be applied first).

### Within each user story

- Models → schemas → CRUD → service → router → frontend api → frontend pages.
- Backend and frontend within a story can be split across two engineers as soon as the OpenAPI contract is honored on both sides.

### Parallel opportunities

- Phase 1 — T002, T003, T004, T005, T006, T007, T008, T010, T011 are all `[P]`.
- Phase 2 — backend and frontend foundations are independent: one engineer on T012–T035, another on T036–T047.
- Phase 3 (US1) — within backend: T048/T049/T050 parallel; T056/T057 (template + CSS) parallel with the model work. Frontend: T060–T066 are all `[P]` once the schema (T061) lands.
- Phases 4 and 5 — fully independent of each other after US1 lands; can be staffed in parallel.
- Phase 6 — every test file and the audit script are `[P]`.

---

## Implementation Strategy

### MVP scope (ship first)

**Phases 1 + 2 + 3 only.** This already delivers the core business operation: a counter-staff user can authenticate and create+print a Vietnamese delivery bill with a unique tracking number, barcode, and QR. Everything else is value-add.

### Incremental delivery

1. MVP = US1 (Phases 1–3). Demo to the carrier; gather feedback on the print template.
2. Increment 2 = US2 (Phase 4). Adds operational visibility — search, status, reprint.
3. Increment 3 = US3 (Phase 5). Adds the productivity multiplier for repeat senders.
4. Hardening = Phase 6. Run before any external customer rollout.

### Parallel team layout (suggested)

- **Engineer A (backend)**: Phase 1 (T002, T004, T009, T010), Phase 2 (T012–T035), then US1 backend (T048–T059), then US2 backend (T071–T075), then US3 backend (T082–T088).
- **Engineer B (frontend)**: Phase 1 (T003, T005, T011), Phase 2 (T036–T047), then US1 frontend (T060–T070), then US2 frontend (T076–T081), then US3 frontend (T089–T094).
- **Engineer C (QA / hardening, joining at MVP)**: Phase 6 in full.

### Format validation

All 105 tasks above use the `- [ ] T### [P?] [Story?] Description with file path` format. Story labels appear only on US1/US2/US3 phases. Setup, Foundational, and Polish phases carry no story label, per the rules in the command outline.

---

## Summary

- **Total tasks**: 105
- **Phase 1 — Setup**: 11 tasks (T001–T011)
- **Phase 2 — Foundational**: 36 tasks (T012–T047)
- **Phase 3 — User Story 1 (P1, MVP)**: 23 tasks (T048–T070)
- **Phase 4 — User Story 2 (P2)**: 11 tasks (T071–T081)
- **Phase 5 — User Story 3 (P3)**: 13 tasks (T082–T094)
- **Phase 6 — Polish**: 11 tasks (T095–T105)
- **Suggested MVP**: Phases 1 + 2 + 3 → 70 tasks → fully demoable bill-creation-and-print system.
