# VeloxShip — Quy ước phát triển (Development Conventions)

Tài liệu này là **nguồn tham chiếu chung** cho cả team khi phát triển VeloxShip.
Code review dựa trên tài liệu này; nếu một quy ước cản trở công việc, hãy mở PR
sửa tài liệu thay vì lặng lẽ làm khác.

> Ngôn ngữ: tài liệu và code viết bằng **tiếng Anh**, thuật ngữ nghiệp vụ chú
> thích tiếng Việt trong ngoặc — giống style sẵn có trong code
> (`"""Bill (Phiếu Gửi) model."""`). **UI/UX hiển thị cho người dùng luôn 100%
> tiếng Việt.**

---

## 0. Nguyên tắc vàng

1. **Một thay đổi schema = model + migration + schema + crud, trong cùng một PR.**
2. **Hướng phụ thuộc chỉ đi một chiều:** `api → services → crud → models`.
3. **Tiền là `Decimal`, không bao giờ là `float`.**
4. **Lỗi trả về người dùng luôn có `error_code` + thông điệp tiếng Việt.**
5. **Không sửa migration đã được apply lên môi trường chung.**
6. **Mọi hàm Python có type hint đầy đủ cho tham số và giá trị trả về.**

---

## 1. Database migrations

### 1.1 Đặt tên

Migration theo định dạng `<NNNN>_<reason>.py`, `NNNN` từ `0001` đến `9999`:

```
0001_init_extensions.py
0002_users_service_tiers_audit.py
0003_bills.py
0005_add_cod_ledger.py
```

`revision` bên trong file là **số trần** (`'0005'`), không kèm hậu tố.

### 1.2 Cách tạo

```bash
make db-revision m="add cod ledger"      # tương đương alembic revision --autogenerate
```

Số thứ tự được gán **tự động** bởi hook `process_revision_directives` trong
`backend/alembic/env.py`, nên chạy `alembic revision` trực tiếp cũng ra đúng
định dạng. Ba mảnh ghép:

| Thành phần | Ở đâu | Vai trò |
|---|---|---|
| `file_template` | `alembic.ini` | định dạng tên file `<rev>_<reason>.py` |
| `process_revision_directives` | `alembic/env.py` | gán `rev_id = max(hiện có) + 1` |
| `revision_environment` | `alembic.ini` | nạp `env.py` cả khi không `--autogenerate` |

> Lịch sử: `8e6679d4b6ec_setup_database_v2.py` lọt vào giữa chuỗi vì trước đây
> `alembic.ini` thiếu `file_template`. Các id cũ không đúng chuẩn (`0002b`,
> `0004_drop_districts`, `8e6679d4b6ec`) **giữ nguyên** — đổi tên đồng nghĩa
> viết lại `down_revision` của chuỗi đã apply lên DB dev.

### 1.3 Bắt buộc review output của `--autogenerate`

Autogenerate **không phải** kết quả cuối. Ba lỗi đã thực sự xảy ra trong repo này:

**a. `CheckConstraint` trên bảng đã tồn tại không được sinh ra.**
Khi thêm `__table_args__` vào một model đã có bảng, Alembic chỉ sinh
`add_column`/`alter_column` — constraint bị bỏ qua im lặng. Phải tự thêm:

```python
op.create_check_constraint(
    "ck_bills_status",
    "bills",
    "status IN ('created', 'picked_up', 'in_transit', 'delivered', 'returned', 'cancelled')",
)
```

*Hiện trạng:* toàn bộ check constraint của `Bill`, `Customer`, `User` khai báo
trong model nhưng **chưa hề tồn tại trong DB** — cần một migration bù.

**b. Cột `NOT NULL` thêm vào bảng đã có dữ liệu sẽ làm migration chết.**
Luôn dùng một trong hai cách:

```python
# Cách 1 — có giá trị mặc định hợp lý
op.add_column("bills", sa.Column("cod_amount", sa.Numeric(14, 2),
                                 nullable=False, server_default="0"))

# Cách 2 — thêm nullable → backfill → siết NOT NULL
op.add_column("wards", sa.Column("province_code", sa.String(), nullable=True))
op.execute("UPDATE wards SET province_code = ...")
op.alter_column("wards", "province_code", nullable=False)
```

**c. Đổi tên cột = mất dữ liệu nếu dùng drop + add.**
`fee_fuel_surcharge → fee_insurance` phải là `op.alter_column(..., new_column_name=...)`
hoặc kèm bước copy dữ liệu, không phải `drop_column` + `add_column`.

### 1.4 Quy tắc khác

- `downgrade()` phải chạy được thật, không để `pass`.
- Migration đã push lên `main` thì **không sửa** — viết migration mới đè lên.
- Migration đổi dữ liệu (data migration) tách riêng khỏi migration đổi cấu trúc.
- Chạy thử `alembic upgrade head && alembic downgrade -1 && alembic upgrade head`
  trên DB có sẵn dữ liệu trước khi mở PR.

---

## 2. Kiến trúc backend

### 2.1 Quyết định: phân lớp thực dụng, không phải Clean Architecture đầy đủ

Chúng ta **không** dùng ports-and-adapters đầy đủ (repository interface +
dependency inversion). Lý do:

- Async SQLAlchemy mất khả năng compose query khi bị giấu sau repository interface.
- Phải viết port cho ~15 entity để đổi lấy khả năng test mà một DB test
  chạy trong transaction đã cung cấp rẻ hơn nhiều.
- App thiên về CRUD nghiệp vụ logistics, không có nhiều domain logic thuần tuý.

Thứ chúng ta **bắt buộc** giữ là **hướng phụ thuộc một chiều** — phần giá trị
nhất của Clean Architecture, không kèm chi phí boilerplate.

### 2.2 Các lớp

```
app/api/v1/     HTTP: routing, status code, dependency injection, serialize
      ↓
app/services/   Nghiệp vụ: validate rule, chuyển trạng thái, điều phối
      ↓
app/crud/       Truy cập dữ liệu: query, insert, update — không có business rule
      ↓
app/models/     SQLAlchemy ORM — không import gì từ 3 lớp trên
```

Ngoài luồng: `app/schemas/` (Pydantic, dùng bởi `api` + `services`),
`app/core/` (config, security, i18n, exceptions — dùng được ở mọi nơi).

**Luật:** mũi tên chỉ đi xuống. `crud` không import `services`. `models` không
import `crud`. `api` không gọi thẳng `crud` khi thao tác có kèm nghiệp vụ.

### 2.3 Cái gì thuộc lớp nào

| Việc | Lớp |
|---|---|
| Đọc query param, trả HTTP status | `api` |
| Kiểm tra quyền theo role | `api` (dependency) hoặc `services` |
| Validate service tier còn active | `services` |
| Kiểm tra chuyển trạng thái hợp lệ | `services` |
| Sinh tracking number | `services` |
| Ghi `audit_events` | `services` |
| `select()` / `db.add()` / eager load | `crud` |
| Định nghĩa cột, quan hệ, constraint | `models` |

### 2.4 Vi phạm hiện có — backlog dọn dẹp

| Vị trí | Vấn đề |
|---|---|
| `api/v1/bills.py:67-94` | endpoint print tự mutate model, ghi audit, chọn renderer — việc của `services` |
| `crud/bill.py:82` | `crud` ghi audit event → side effect nghiệp vụ nằm trong lớp dữ liệu |
| `crud/bill.py:12` | `crud` import từ `services` → mũi tên ngược |
| `api/v1/bills.py:72,89,93` | `import` giữa thân hàm thay vì đầu file |

Không bắt buộc sửa hết ngay, nhưng **code mới không được thêm vi phạm kiểu này**.

---

## 3. Model, schema và crud phải đổi cùng nhau

Đổi model mà không đổi `schemas/` + `crud/` sẽ làm vỡ runtime mà **không có lỗi
lúc import** — Python chỉ chết khi hàm được gọi.

> **Hiện trạng `main` đang hỏng vì lý do này.** Model `Bill` đã bỏ `sender_name`,
> `fee_fuel_surcharge` và đổi `status_events → status_logs`, nhưng
> `crud/bill.py` và `schemas/bill.py` vẫn tham chiếu tên cũ. `create_bill` và
> `get_bill` sẽ ném `AttributeError`/`TypeError` ngay khi gọi.

Checklist khi đổi một model:

- [ ] `app/models/<entity>.py`
- [ ] Migration tương ứng
- [ ] `app/schemas/<entity>.py` (kể cả `from_model`)
- [ ] `app/crud/<entity>.py`
- [ ] `app/services/<entity>_service.py`
- [ ] Contract test / OpenAPI
- [ ] Frontend nếu response đổi hình dạng

---

## 4. Quy ước đặt tên

### 4.1 Database

| Đối tượng | Quy ước | Ví dụ |
|---|---|---|
| Bảng | `snake_case`, số nhiều | `bill_status_logs` |
| Cột | `snake_case`, số ít | `chargeable_weight_kg` |
| Khoá ngoại | `<entity>_id` | `origin_depot_id` |
| Cột tiền | hậu tố `_amount` hoặc tiền tố `fee_` | `cod_amount`, `fee_vat` |
| Cột thời điểm | hậu tố `_at` | `delivered_at` |
| Cột boolean | tiền tố `is_` / `has_` | `is_active` |

### 4.2 Tên constraint — **không tự thêm tiền tố**

`app/db/base.py` đã cấu hình `naming_convention` tự sinh tiền tố:

```python
"ck": "ck_%(table_name)s_%(constraint_name)s"
```

Nên trong model chỉ đặt **phần đuôi**:

```python
# ✅ Đúng → ck_vehicles_status
CheckConstraint("status IN ('active', 'inactive')", name="status")

# ❌ Sai → ck_vehicles_ck_vehicles_status (bị nhân đôi)
CheckConstraint("status IN ('active', 'inactive')", name="ck_vehicles_status")
```

*Hiện trạng:* các model mới (`finance.py`, `vehicle.py`, `linehaul.py`,
`partner.py`) đang bị nhân đôi tiền tố — sửa dần khi đụng tới.

### 4.3 Giá trị enum trong DB

Dùng **tiếng Anh `snake_case`**, không dùng tiếng Việt không dấu:

```python
status = "created" | "picked_up" | "in_transit" | "delivered" | "returned" | "cancelled"
```

Nhãn tiếng Việt hiển thị cho người dùng nằm ở frontend (`src/i18n/vi.js`), không
nằm trong DB. *(Chuỗi cũ kiểu `da_tao` đã được migrate sang tiếng Anh.)*

### 4.4 Error code

`SCREAMING_SNAKE_CASE`, khai báo trong `app/core/i18n.py` kèm thông điệp tiếng Việt:

```python
"BILL_NOT_FOUND": "Không tìm thấy phiếu gửi.",
```

### 4.5 Endpoint

- Danh từ số nhiều, kebab-case: `/api/v1/bills`, `/api/v1/cod-handovers`
- Hành động không CRUD dùng sub-resource: `POST /bills/{id}/status`
- Không nhét động từ vào path: ~~`/bills/create`~~

### 4.6 Python

- Module `snake_case`, class `PascalCase`, hằng `SCREAMING_SNAKE`.
- Router file đặt theo resource số nhiều: `api/v1/bills.py`.
- Service file: `<entity>_service.py`.
- Ruff quản lý import order và format — chạy `ruff check --fix` trước khi commit.

### 4.7 Type hint

**Mọi hàm Python phải có type hint đầy đủ cho tham số và giá trị trả về.**

```python
# ✅
async def get_bill(db: AsyncSession, bill_id: int) -> Bill | None: ...

# ❌ thiếu kiểu tham số và kiểu trả về
async def get_bill(db, bill_id): ...
```

**Dùng cú pháp hiện đại của Python 3.11** — ruff (rule `UP`) sẽ cảnh báo nếu dùng
kiểu cũ:

| Dùng | Không dùng |
|---|---|
| `str \| None` | `Optional[str]` |
| `list[Bill]` | `List[Bill]` |
| `dict[str, Any]` | `Dict[str, Any]` |
| `tuple[list[Bill], int]` | `Tuple[List[Bill], int]` |

**Quy tắc cụ thể:**

- Hàm không trả về giá trị vẫn phải ghi `-> None`.
- Hàm `async` ghi kiểu của **giá trị đã await**, không bọc `Coroutine`:
  `async def f() -> Bill:` chứ không phải `-> Coroutine[..., Bill]`.
- Cột model dùng `Mapped[...]` + `mapped_column(...)`, đã áp dụng nhất quán
  trong `app/models/`.
- Tiền dùng `Decimal`, không dùng `float` (xem mục 5.2).
- Hạn chế `Any`. Buộc phải dùng thì kèm comment giải thích lý do.
- **Không dùng `from module import *`** — làm hỏng khả năng phân giải tên của cả
  người đọc lẫn IDE. *(`alembic/env.py:16` đang vi phạm.)*

**Forward reference:** khi khai báo quan hệ tới model khác, tên trong chuỗi phải
thực sự import được. Import trong khối `if TYPE_CHECKING:` để tránh vòng lặp
import lúc chạy:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.depot import Depot

class Bill(Base):
    origin_depot: Mapped["Depot | None"] = relationship("Depot", ...)
```

*Hiện trạng cần sửa dần:* `services/bill_service.py:16` khai báo `-> "Bill"`
nhưng `Bill` không hề được import trong file — chuỗi này không phân giải được.
Các chỗ còn thiếu type hint: endpoint trong `api/v1/bills.py` (thiếu kiểu trả
về), `schemas/bill.py:50` (`validate_total`), `core/exceptions.py:42`
(`register_exception_handlers`), `alembic/env.py` (`do_run_migrations`).

---

## 5. Pydantic schemas

### 5.1 Hậu tố

| Hậu tố | Dùng cho |
|---|---|
| `<Entity>Create` | body của POST |
| `<Entity>Update` | body của PATCH/PUT |
| `<Entity>Read` | response |
| `<Entity>Page` | response phân trang |

### 5.2 Tiền dùng `Decimal`

```python
from decimal import Decimal

fee_total: Decimal      # ✅
fee_total: float        # ❌ sai số nhị phân trên tiền VND
```

Model đã dùng `Numeric(14, 2)` → `Decimal`. **`app/schemas/bill.py` hiện vẫn dùng
`float`, cần sửa.**

### 5.3 `from_model`

Khi ORM và response khác hình dạng (ví dụ gộp cột thành object `Party`), viết
`@classmethod from_model`. Khi trùng khớp 1-1, dùng
`model_config = {"from_attributes": True}` và `model_validate`.

### 5.4 Validate ở đâu

- **Schema:** kiểu dữ liệu, bắt buộc/không, định dạng, ràng buộc trong một record.
- **Service:** ràng buộc cần truy vấn DB (tier có tồn tại? chuyển trạng thái hợp lệ?).
- **DB constraint:** bất biến cuối cùng, không được vi phạm dù đi đường nào.

Ràng buộc quan trọng nên có ở **cả ba** — schema báo lỗi đẹp, DB đảm bảo đúng.

---

## 6. Xử lý lỗi

### 6.1 Luôn dùng `AppError`, không dùng `HTTPException`

```python
from app.core.exceptions import NotFoundError

raise NotFoundError("BILL_NOT_FOUND")           # ✅
raise HTTPException(404, "Bill not found")      # ❌ mất error_code + tiếng Việt
```

Các lớp có sẵn trong `app/core/exceptions.py`: `AppError` (400),
`NotFoundError` (404), `ConflictError` (409), `ForbiddenError` (403).

### 6.2 Hình dạng response lỗi

```json
{
  "error_code": "BILL_NOT_FOUND",
  "message": "Không tìm thấy phiếu gửi.",
  "details": { }
}
```

Frontend hiển thị theo `message`, phân nhánh logic theo `error_code` — **không
bao giờ so khớp chuỗi `message`**.

### 6.3 ⚠️ Cần sửa

`app/core/exceptions.py:69-73` trả nguyên `traceback` về client khi có lỗi 500.
Lộ đường dẫn file, tên biến và cấu trúc nội bộ. Phải ghi log traceback ở server
và chỉ trả về `INTERNAL_ERROR` cho client.

---

## 7. Testing

Thư mục đã có trong `backend/tests/` nhưng **hiện đang rỗng** — phần này là mục
tiêu cần đạt, không phải mô tả hiện trạng.

| Thư mục | Nội dung |
|---|---|
| `tests/unit/` | logic thuần, không chạm DB |
| `tests/integration/` | service + crud trên DB thật (testcontainers) |
| `tests/contract/` | request/response khớp `contracts/openapi.yaml` |
| `tests/perf/` | ngưỡng hiệu năng |

Quy ước:

- Đặt tên `test_<hành vi>_<điều kiện>`, ví dụ `test_create_bill_rejects_empty_contents`.
- Mỗi test tự dọn dẹp; chạy trong transaction rồi rollback.
- Bug được sửa phải kèm một test tái hiện bug đó.

**Bắt buộc có test khi:** thêm/sửa business rule trong `services/`, đổi hình dạng
API, hoặc sửa bug. Không bắt buộc với: đổi tên thuần tuý, thay đổi chỉ ở tài liệu.

---

## 8. Frontend

### 8.1 Cấu trúc thư mục

```
src/
  api/                 axios client + hàm gọi API theo resource
  auth/                AuthContext, ProtectedRoute
  components/layout/   thành phần dùng chung toàn app
  features/<feature>/
    components/        component riêng của feature
    pages/             component cấp route
    schema.js          zod schema của feature
  i18n/vi.js           toàn bộ chuỗi tiếng Việt
  lib/                 tiện ích thuần (format, diacritics)
```

**Luật:** `features/A` không import từ `features/B`. Dùng chung thì nâng lên
`components/` hoặc `lib/`.

### 8.2 Gọi API

Mọi request đi qua `src/api/client.js` (đã gắn sẵn JWT interceptor và tự refresh
khi 401). Không gọi `axios` hay `fetch` trực tiếp trong component.

Hàm gọi API gom theo resource trong `src/api/<resource>.js`; component dùng
TanStack Query, không tự quản lý loading/error state bằng `useState`.

### 8.3 Form

`react-hook-form` + `zod` qua `@hookform/resolvers`. Schema đặt tại
`features/<feature>/schema.js`. Thông báo lỗi validate viết bằng tiếng Việt.

### 8.4 Tiếng Việt

- Mọi chuỗi hiển thị nằm trong `src/i18n/vi.js`, không hardcode trong JSX.
- Tìm kiếm phải bỏ dấu được (dùng `lib/diacritics.js`).
- Tiền định dạng theo `vi-VN`: `1.234.567 ₫`.
- Ngày giờ `DD/MM/YYYY`, dùng `dayjs`.

---

## 9. Git

### 9.1 Branch

```
<type>/<mô-tả-ngắn>

feat/cod-handover-api
fix/bill-fee-total-mismatch
chore/alembic-sequential-migration-ids
refactor/bill-service-layering
docs/conventions
```

### 9.2 Commit — Conventional Commits

```
<type>(<scope>): <mô tả ngắn, thức mệnh lệnh>

<thân: giải thích VÌ SAO, không phải CÁI GÌ>
```

`type`: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `perf`.

```
feat(bills): add COD handover approval flow
fix(alembic): restore missing check constraints on bills
```

### 9.3 Pull request

- PR nhắm vào `main`, không commit thẳng lên `main`.
- Tiêu đề theo đúng format commit.
- Mô tả nêu rõ: **vấn đề**, **cách tiếp cận**, **cách đã kiểm chứng**.
- Nêu rõ phần chưa làm / đánh đổi đã chấp nhận.
- PR đụng schema phải liệt kê checklist ở mục 3.

---

## 10. Cấu hình & bảo mật

- **Không commit secret.** `backend/.env` nằm trong `.gitignore`; mọi biến mới
  phải được thêm vào `backend/.env.example` với giá trị giả.
- `DATABASE_URL` không có giá trị mặc định trong code — thiếu thì app phải chết
  ngay lúc khởi động, không âm thầm chạy sai DB.
- `docker-compose.yml` đọc `POSTGRES_PASSWORD` từ môi trường và **không có
  default**. ⚠️ Repo hiện thiếu `.env.example` ở thư mục gốc, nên `docker compose up`
  trên máy mới sẽ fail — cần bổ sung.
- Không log mật khẩu, token, hay `api_token` của partner.

---

## Phụ lục — các việc cần dọn

Tổng hợp những chỗ tài liệu này chỉ ra là đang lệch chuẩn:

| # | Việc | Vị trí |
|---|---|---|
| 1 | `crud`/`schemas` của Bill chưa cập nhật theo model mới → runtime lỗi | `crud/bill.py`, `schemas/bill.py` |
| 2 | Check constraint của `bills`/`customers`/`users` chưa có trong DB | cần migration mới |
| 3 | Traceback bị trả về client khi lỗi 500 | `core/exceptions.py:69-73` |
| 4 | Tiền dùng `float` trong schema | `schemas/bill.py` |
| 5 | Tên check constraint bị nhân đôi tiền tố | `models/finance.py`, `vehicle.py`, `linehaul.py`, `partner.py` |
| 6 | Thiếu `.env.example` ở thư mục gốc cho docker compose | root |
| 7 | Vi phạm hướng phụ thuộc | mục 2.4 |
| 8 | Thư mục test rỗng | `backend/tests/` |
| 9 | Makefile trỏ tới `docker-compose.db.yml` / `.local.yml` không tồn tại | `Makefile` |
| 10 | Thiếu type hint rải rác; `import *` trong `env.py`; forward ref không phân giải được | mục 4.7 |
