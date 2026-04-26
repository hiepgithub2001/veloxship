# Quickstart — Logistics Delivery Bill Management

How to bring the system up locally for development and run the smoke flow that proves the core path (login → create bill → preview/print → status update → search).

This is a developer guide. The eventual production deployment shape is intentionally not pinned in v1 (see [research.md §16](./research.md)).

---

## 1. Prerequisites

- Docker 24+ and Docker Compose v2 (recommended; gives you Postgres for free).
- Or, for native: Python 3.11+, Node.js 20 LTS, PostgreSQL 16 (with the ability to install the `unaccent` and `pg_trgm` extensions — `CREATE EXTENSION` requires superuser).
- A modern Chromium-based browser for the print preview.
- (Backend host only) WeasyPrint dependencies (Pango, Cairo, GDK-PixBuf). On Debian/Ubuntu: `apt install libpango-1.0-0 libpangoft2-1.0-0 libcairo2`.

---

## 2. First-time setup

```bash
git clone <repo>
cd veloxship
git checkout 001-logistics-bill-app

cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

`backend/.env` minimally needs:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/veloxship
JWT_SECRET=change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_TTL_MINUTES=15
REFRESH_TOKEN_TTL_DAYS=7
TRACKING_NUMBER_PREFIX=NL
CARRIER_NAME=Vận Chuyển HN
CARRIER_HOTLINE=0972 160 610
CARRIER_WEBSITE=newlinks.vn
CARRIER_EMAIL=info@newlinks.vn
```

`frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 3. Start the stack (Docker Compose)

```bash
docker compose up -d --build
```

This brings up:

- `db` — Postgres 16 with `unaccent`, `pg_trgm`, `citext` enabled.
- `backend` — FastAPI on `http://localhost:8000` (interactive docs at `/docs`).
- `frontend` — Vite dev server on `http://localhost:5173`.

Apply migrations and seed the service-tier catalogue + an admin user:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.scripts.seed
```

The seed creates an admin login:

```text
username: admin
password: admin123  (change it; this is dev only)
```

---

## 4. Native (no Docker) variant

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
python -m app.scripts.seed
uvicorn app.main:app --reload --port 8000

# Frontend (separate shell)
cd frontend
npm ci
npm run dev   # serves on http://localhost:5173
```

---

## 5. Smoke walkthrough

1. Open `http://localhost:5173`. The login screen is in Vietnamese.
2. Log in as `admin` / `admin123`. You should land on **"Phiếu Gửi"** list (empty).
3. Click **"Tạo phiếu gửi"**. Fill:
   - **Người gửi**: a known customer (after step 6 you can pick a saved one) or new walk-in details.
   - **Người nhận**: any test data with full Vietnamese diacritics, e.g. `Nguyễn Thị Hoa`, `KCN VSIP, Đường 3A`, `TP Từ Sơn`, `Bắc Ninh`, `0974537658`.
   - **Nội dung**: one line, e.g. `Hàng mẫu`, qty `24`, weight `200,00 kg`.
   - **Loại hàng**: `Hàng hoá`. **Dịch vụ**: `Đường bộ`.
   - **Cước phí**: enter values; **Tổng cộng** must equal the sum.
   - **Thanh toán**: `Người nhận thanh toán`.
4. Click **"Lưu & In phiếu"**. The system generates a tracking number (e.g. `NL0000001`) and opens the print preview that reproduces the layout in `image_data/bill_format.jpg` — sender block, receiver block, contents grid, fees, signatures, barcode, QR, Vietnamese footer.
5. Click **"In"** in the browser print dialog (or **"Tải PDF"** for the WeasyPrint-rendered server PDF).
6. Back to the bill list. Search for the recipient name without diacritics (`nguyen thi hoa`) — the new bill must appear (FR-014, SC-005).
7. Open the bill detail. Change status to **"Đã lấy hàng"**, then **"Đang vận chuyển"**, then **"Đã giao"** (provide a recipient signer name). The status history shows three events.
8. Click **"In lại"**. The PDF is byte-identical to the first print and the audit trail records a `bill.printed` event.

---

## 6. Saving a customer profile (for auto-fill)

1. From the side menu **"Khách hàng"** → **"Thêm mới"**.
2. Fill `Mã KH` (e.g. `NL500010`), name (`KHL — Mr Lương Kho HN`), full address, phone. Save.
3. Start a new bill. In the sender block click **"Chọn khách hàng"** and pick the new profile. The block auto-fills; the customer code prints in the **Mã KH** field of the bill (FR-019, FR-020).

---

## 7. Running the tests

```bash
# Backend
cd backend
pytest                 # runs unit + integration (testcontainers spins up Postgres)
pytest tests/contract  # OpenAPI contract drift check

# Frontend
cd frontend
npm test               # vitest + Testing Library
npm run test:e2e       # Playwright smoke (login → create → preview)
```

---

## 8. Troubleshooting

- **`extension "unaccent" does not exist`** — connect as superuser (`postgres`) and run the migration there. The Compose file already does this; the native setup may need `psql -c 'CREATE EXTENSION unaccent;'` once.
- **Vietnamese characters render as `?` on the printed PDF** — install a Vietnamese-capable font in the WeasyPrint container; the included Dockerfile bundles **Be Vietnam Pro**.
- **Searches with diacritics are slower than without** — confirm the GIN trigram indexes were created (`\d+ bills` in psql); the migration adds them but a partial database reset can lose them.
- **CORS errors in dev** — `VITE_API_BASE_URL` must match the FastAPI origin (`http://localhost:8000`); the FastAPI app has CORS allow-list for `http://localhost:5173` in dev.
