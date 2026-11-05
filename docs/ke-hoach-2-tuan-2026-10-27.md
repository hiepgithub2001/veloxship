---
description: "Đối chiếu checklist DEV A/B với mã nguồn hiện tại và kế hoạch 2 tuần (27/10 – 10/11/2026)"
---

# Đối chiếu Checklist & Kế hoạch 2 tuần — 27/10 → 10/11/2026

**Ngày lập**: 27/10/2026 (Thứ Ba)
**Phạm vi**: [`checklist-dev-a.md`](./checklist-dev-a.md), [`checklist-dev-b.md`](./checklist-dev-b.md) so với mã nguồn nhánh `feat/customer-module` @ `2dec977`.
**Mốc tham chiếu**: kế hoạch gốc 12 tuần (28/07 → 10/10/2026) tại [`ke-hoach-trien-khai.md`](./ke-hoach-trien-khai.md).
**Nguồn nghiệp vụ**: [`business-requirements.md`](./business-requirements.md), [`roadmap-tasks.md`](./roadmap-tasks.md).

---

## 0. TL;DR

1. **Checklist đã lệch so với mã nguồn**: 4/10 mục đánh dấu `[x]` chưa phản ánh đúng (UC-WEB-08 chưa làm; 04/05/06 mới ở mức seed hoặc không còn áp dụng), trong khi 2 mục đã xong lại chưa đánh dấu (UC-WEB-03, UC-WEB-10).
2. **Thực trạng**: 8/55 hạng mục hoàn chỉnh, 6 một phần, 38 chưa bắt đầu, 3 bỏ/không còn áp dụng. Riêng 20 báo cáo của Sprint 4 chưa có dòng mã nào. Mốc go-live 10/10 đã trượt **17 ngày**; khối lượng còn lại tương đương **5–6 tuần người**.
3. **Lõi tạo phiếu còn thiếu trường**: form tạo phiếu chưa chọn **hạng dịch vụ**, **COD**, **bảo hiểm**; backend chưa chặn ràng buộc FR-005 (dịch vụ trong nước/quốc tế).
4. **Rủi ro phát hành**: module khách hàng (21/10) **chưa push/merge**; fix seed (22/10) **chưa commit**; test tích hợp cần Docker nên hiện không chạy được; CI chỉ build/push image, **không chạy test**.
5. **2 tuần tới**: DEV A làm **Đối tác 3PL (16/17) + Công nợ (15)**; DEV B làm **hoàn thiện tạo phiếu + Hủy giao hàng thành công (24) + Lịch sử chỉnh sửa (27) + Lấy hàng (18)**. Kho, chuyến xe, COD và báo cáo lùi sang 11–21/11.

---

## 1. Cách đối chiếu

- Đọc 2 checklist, BRD, kế hoạch triển khai, wiki và lịch sử git.
- Kiểm tra thực tế theo 5 lớp: **model + migration → API route → service → frontend route/page/component → test**.
- Chạy kiểm chứng: `pytest tests/unit`, `pytest` (toàn bộ), `npm run build`, `npm run lint`.
- Quy ước kết luận:
  - ✅ **Xong**: có API + UI + phân quyền + test cho use case.
  - 🟡 **Một phần**: có một phần chuỗi (ví dụ chỉ seed + API đọc, hoặc có backend chưa có UI).
  - ⬜ **Chưa bắt đầu**: không có mã nguồn nghiệp vụ.
  - ⛔ **Bỏ/không áp dụng**: đã quyết định không làm hoặc yêu cầu không còn đúng.

---

## 2. Bảng đối chiếu chi tiết

### 2.1 DEV A — 28 hạng mục

| Mã | Checklist (trước đối chiếu) | Thực tế | Bằng chứng | Kết luận |
|---|---|---|---|---|
| UC-WEB-01 | `[ ]` Quản lý phòng ban | Không còn API/UI; đã bị gỡ khỏi module nhân viên | commit `7f0c7fa` (14/10) *remove department and position lookup* | ⛔ Bỏ |
| UC-WEB-02 | `[ ]` Quản lý chức vụ | Như trên | commit `7f0c7fa` | ⛔ Bỏ |
| UC-WEB-03 | `[ ]` Quản lý nhân viên | Có CRUD nhân viên, khóa/mở, reset mật khẩu, vai trò động | [`users.py`](../backend/app/api/v1/users.py) (7 endpoint), `features/staff` | ✅ Xong |
| UC-WEB-10 | `[ ]` Quản lý phân quyền | Có vai trò động + ma trận quyền theo module | [`permissions.py`](../backend/app/api/v1/permissions.py) (6 endpoint), `features/permissions` | ✅ Xong |
| UC-WEB-11 | `[ ]` Dịch vụ / dịch vụ gia tăng | Chỉ seed 9 hạng + `GET /service-tiers`; **không có màn hình quản trị**, form tạo phiếu **không chọn hạng**; chưa có khái niệm dịch vụ gia tăng (chỉ cờ bảo hiểm) | [`service_tiers.py`](../backend/app/api/v1/service_tiers.py), `features/bills/schema.js` | 🟡 Một phần |
| UC-WEB-12 | `[ ]` Loại hàng hóa | Đang dùng enum cứng `document`/`goods`; module `cargo_types` chỉ nằm ở nhánh `feature/cargotypeconfig` **chưa merge** | [`bill.py`](../backend/app/schemas/bill.py), nhánh `feature/cargotypeconfig` | 🟡 Một phần |
| UC-WEB-13 | `[x]` Khách hàng | Đã xong 21/10: tạo/sửa, chi tiết, lịch sử phiếu, chỉ số | [`customers.py`](../backend/app/api/v1/customers.py) (6 endpoint), `features/customers` | ✅ Xong |
| UC-WEB-14 | `[ ]` Bảng giá | **Không có** model/bảng/API (`price_sheets`, `price_rules` không tồn tại) | `alembic/versions/`, `app/models/` | ⬜ Chưa |
| UC-WEB-15 | `[ ]` Công nợ | **Không có** bảng thanh toán/công nợ | `alembic/versions/`, `app/models/` | ⬜ Chưa |
| UC-WEB-16 | `[ ]` Đối tác 3PL | Có bảng `partners` + model, **chưa có API/UI** | [`partner.py`](../backend/app/models/partner.py), migration `0004` | ⬜ Chưa |
| UC-WEB-17 | `[ ]` Bảng giá mua | Có `partner_tariffs` + model, **chưa có API/UI** | [`partner.py`](../backend/app/models/partner.py) | ⬜ Chưa |
| UC-WEB-28…34 | `[ ]` Quản lý kho (7 UC) | **Không có** bảng/API/UI kho; quyền `warehouse:*` mới chỉ là mã trong catalog | [`permissions.py`](../backend/app/core/permissions.py) | ⬜ Chưa |
| UC-WEB-40-A01…A10 | `[ ]` 10 báo cáo tài chính | **Không có** report engine/API/UI | — | ⬜ Chưa |

**Tổng DEV A**: ✅ 3 · 🟡 2 · ⬜ 21 · ⛔ 2 = 28.

### 2.2 DEV B — 27 hạng mục

| Mã | Checklist (trước đối chiếu) | Thực tế | Bằng chứng | Kết luận |
|---|---|---|---|---|
| UC-WEB-04 | `[x]` Tỉnh thành | Seed 34 tỉnh + `GET /locations/provinces`; **không có màn hình quản trị** (đúng phạm vi seed của BRD) | [`locations.py`](../backend/app/api/v1/locations.py) | 🟡 Một phần |
| UC-WEB-05 | `[x]` Quận huyện | **Cấp huyện đã bị bỏ**; phường/xã gắn trực tiếp tỉnh (mô hình 2 cấp) | migration `0005`, [`ward.py`](../backend/app/models/ward.py) | ⛔ Không áp dụng |
| UC-WEB-06 | `[x]` Phường xã | Seed 3.321 phường/xã + API đọc theo tỉnh; **không có màn hình quản trị** | [`locations.py`](../backend/app/api/v1/locations.py) | 🟡 Một phần |
| UC-WEB-07 | `[x]` Bưu cục | CRUD + ảnh + trạng thái | [`depots.py`](../backend/app/api/v1/depots.py), `features/depots` | ✅ Xong |
| UC-WEB-08 | `[x]` Khu vực / tuyến giao nhận | **Chưa có** trường khu vực/tuyến trong `Depot`, không API/UI | [`depot.py`](../backend/app/models/depot.py) | ⬜ Chưa |
| UC-WEB-09 | `[x]` Đội xe | CRUD + loại xe + trạng thái + tài xế + ảnh | [`vehicles.py`](../backend/app/api/v1/vehicles.py), `features/vehicles` | ✅ Xong |
| UC-WEB-18 | `[ ]` Lấy hàng | **Không có** bảng/API/UI yêu cầu lấy hàng | — | ⬜ Chưa |
| UC-WEB-19 | `[x]` Tạo vận đơn | Có API + form; **thiếu chọn hạng dịch vụ/COD/bảo hiểm trên form**; backend chưa chặn FR-005 | `features/bills/pages/BillCreatePage.jsx`, [`bills.py`](../backend/app/api/v1/bills.py) | ✅ Xong (có defect) |
| UC-WEB-23 | `[x]` Danh sách vận đơn | Lọc trạng thái/ngày/mã/người gửi/nhận, xuất Excel, in hàng loạt | [`bills.py`](../backend/app/api/v1/bills.py), `features/bills` | ✅ Xong |
| UC-WEB-24 | `[ ]` Hủy giao hàng thành công | Chỉ có **mã quyền** `bill:rollback`; `delivered` không có transition ra | [`permissions.py`](../backend/app/core/permissions.py), `ALLOWED_TRANSITIONS` | ⬜ Chưa |
| UC-WEB-26 | `[x]` Điều chỉnh COD | Sửa COD qua `PATCH /bills` + `BillCommercialEditor` khi `created` | `features/bills/components/BillCommercialEditor.jsx` | ✅ Xong |
| UC-WEB-27 | `[~]` Lịch sử điều chỉnh | Audit event được ghi + trả về; **UI mới hiển thị timeline trạng thái**, chưa render audit | [`BillDetailView.jsx`](../frontend/src/features/bills/components/BillDetailView.jsx) | 🟡 Một phần |
| UC-WEB-35 | `[ ]` Đội xe (vận hành) | Có trạng thái/tài xế; **chưa có lịch trình sử dụng** | [`vehicle.py`](../backend/app/models/vehicle.py) | 🟡 Một phần |
| UC-WEB-36 | `[ ]` Chuyến xe | Có model `linehauls`; **chưa có API/UI** | [`linehaul.py`](../backend/app/models/linehaul.py) | ⬜ Chưa |
| UC-WEB-37…39 | `[ ]` Thu hộ COD (3 UC) | Có model `cod_handovers`, `cod_handover_items`, `depot_ledgers`; **chưa có API/UI** | [`finance.py`](../backend/app/models/finance.py) | ⬜ Chưa |
| UC-WEB-40-B01…B10 | `[ ]` 10 báo cáo vận hành | **Không có** report engine/API/UI | — | ⬜ Chưa |

**Tổng DEV B**: ✅ 5 · 🟡 4 · ⬜ 17 · ⛔ 1 = 27.

### 2.3 Tổng hợp toàn bộ

| Trạng thái | Số lượng | Tỷ lệ |
|---|---:|---:|
| ✅ Hoàn chỉnh | 8 | 15% |
| 🟡 Một phần | 6 | 11% |
| ⬜ Chưa bắt đầu | 38 | 69% |
| ⛔ Bỏ / không áp dụng | 3 | 5% |
| **Tổng** | **55** | **100%** |

> Nếu loại 20 báo cáo (Sprint 4) ra khỏi phép tính: **8/35 xong (23%)**, 6 một phần, 18 chưa bắt đầu, 3 bỏ.

### 2.4 Độ chính xác của checklist

- Checklist đánh dấu `[x]` **10 mục**, nhưng chỉ **6 mục đúng** (UC-WEB-07, 09, 13, 19, 23, 26) → **độ chính xác 60%**.
- **4 mục `[x]` chưa chính xác**: UC-WEB-08 (chưa làm), UC-WEB-04/06 (chỉ seed + API đọc), UC-WEB-05 (cấp huyện đã bỏ).
- **2 mục đã xong nhưng chưa đánh dấu**: UC-WEB-03, UC-WEB-10.
- **5 mục thực tế mới ở mức một phần nhưng checklist chưa phản ánh**: UC-WEB-11, 12, 04, 06, 35.

---

## 3. Phát hiện & rủi ro

| # | Mức | Phát hiện | Ảnh hưởng | Xử lý đề xuất |
|---|---|---|---|---|
| R1 | 🔴 Cao | Module khách hàng (UC-13) nằm trên nhánh `feat/customer-module`, **chưa push, chưa merge**; `origin/main` dừng ở 14/10 | Main thiếu tính năng mới nhất; rủi ro mất công nếu máy hỏng | Push + PR + merge ngay ngày D1 |
| R2 | 🔴 Cao | Fix seed offline (22/10) **chưa commit** (2 file modified) | `make dev` có thể chết khi mạng lỗi; log wiki đã ghi như đã xong | Commit + PR riêng ngày D1 |
| R3 | 🔴 Cao | Form tạo phiếu thiếu hạng dịch vụ/COD/bảo hiểm; backend không bắt buộc hạng dịch vụ và không kiểm tra scope | Dữ liệu đầu vào thiếu → bảng giá, báo cáo, COD không chính xác | DEV B D1–D2 |
| R4 | 🔴 Cao | Test tích hợp cần Docker; máy hiện tại không chạy Docker → **158 unit test pass nhưng 8 file integration chưa được xác minh** | Không phát hiện regression DB/API | Bật Docker hoặc thêm CI service Postgres |
| R5 | 🟠 TB | CI `.github/workflows/deploy.yml` chỉ build/push image, **không chạy test** | Regression lọt vào main | Thêm job test (pytest + build/lint) |
| R6 | 🟠 TB | `partners`, `partner_tariffs`, `cod_handovers`, `linehauls` có bảng/model nhưng **không có API** | Dead code, lệch kỳ vọng "đã có sẵn" | Đưa vào sprint 2 tuần (đối tác) |
| R7 | 🟠 TB | Không có schema `price_sheets`/`price_rules`/công nợ; BRD còn câu hỏi mở với khách | UC-14/15 không thể bắt đầu nếu chưa chốt quy tắc | Workshop với khách trước 31/10 |
| R8 | 🟠 TB | Bill có `shipper_id`, `origin_depot_id` nhưng **không luồng nào gán** | COD theo bưu tá (37–39) và báo cáo hiệu suất không có dữ liệu | Làm UC-18 (gán bưu tá) trước COD |
| R9 | 🟡 Thấp | Bundle frontend 2,18 MB (gzip 685 kB), chưa code-split | Tải chậm trên mạng yếu | Tách route/lazy import ở sprint sau |
| R10 | 🟡 Thấp | Wiki log 12/09 ghi module `cargo_types` nhưng mã nguồn main không có | Tài liệu sai → ra quyết định sai | Ghi rõ nhánh chưa merge; chốt hướng UC-12 |
| R11 | 🟡 Thấp | Frontend chỉ có 3 file test (`auth`, `redirect`, `api client`), không có e2e | Hồi quy UI không được chặn | Bổ sung test cho luồng tạo phiếu ở sprint sau |
| R12 | 🟡 Thấp | venv local dùng Python 3.14.7 trong khi dự án chốt 3.11 | Test local có thể pass nhưng production lỗi tương thích | Pin 3.11 trong CI; tạo lại venv 3.11 |

---

## 4. Sức khỏe kỹ thuật (kiểm chứng 27/10/2026)

| Hạng mục | Kiểm chứng | Kết quả |
|---|---|---|
| Unit test backend | `pytest tests/unit -q` | ✅ **158 passed** (0,73s) |
| Integration test backend | `pytest -q` | ❌ Dừng ở `test_account_api.py`: `DockerException: Connection refused` (testcontainers cần Docker) |
| Build frontend | `npm run build` | ✅ 3.287 module, 3,02s; ⚠️ JS 2.179,60 kB (gzip 685,45 kB) |
| Lint frontend | `npm run lint` | ✅ Không lỗi |
| Migration | `alembic/versions` | 21 file, mới nhất `0020_add_bill_customer_indexes` |
| Phiên bản Python | `.venv` vs Docker | ⚠️ venv local chạy **3.14.7**, Docker và `pyproject.toml` chốt **3.11** → test local có thể không phản ánh production |
| Git | `git status` / `git log` | Nhánh `feat/customer-module` **ahead 1** so với `origin/main`, chưa có remote branch; 2 file seed **modified chưa commit** |
| CI | `.github/workflows/deploy.yml` | Chỉ build & push Docker image; **không có job test** |

---

## 5. Kế hoạch 2 tuần (27/10 → 10/11/2026)

### 5.1 Mục tiêu & nguyên tắc

**Sprint goal**: *Đưa `main` về trạng thái phát hành được, hoàn thiện lõi tạo phiếu, và mở 3 mảng còn trống có thể ship độc lập: Đối tác 3PL, Công nợ và Lấy hàng.*

Nguyên tắc chọn việc:
1. **Sửa nền trước**: những defect làm dữ liệu downstream sai (hạng dịch vụ, COD, quyền) được ưu tiên hơn tính năng mới.
2. **Chọn việc ship được trọn vẹn trong 11 ngày công** (API + UI + quyền + audit + test), không mở 5 việc dở dang.
3. **Tôn trọng dependency**: COD cần gán bưu tá → làm UC-18 trước; kho cần thiết kế schema → sang sprint sau.
4. **Không chờ khách**: việc nào bị chặn bởi xác nhận nghiệp vụ (bảng giá, công nợ) thì chỉ làm phần đọc/khung, không tự đặt quy tắc.
5. **Migration đánh số theo thứ tự merge**: hai dev tạo migration song song (DEV A `0021` đối tác, `0022` công nợ; DEV B `0023` lấy hàng) — ai merge sau phải rebase `down_revision` theo `main` mới nhất và chạy lại upgrade/downgrade.

**Lịch**: 11 ngày công — D1 27/10, D2 28/10, D3 29/10, D4 30/10, D5 02/11, D6 03/11, D7 04/11, D8 05/11, D9 06/11, D10 09/11, D11 10/11. *Giả định: 2 dev full-time, không nghỉ lễ; nếu có nghỉ, cắt phần "tạo phiếu từ pickup" (D9) trước.*

### 5.2 DEV A — Đối tác 3PL + Công nợ

**Mục tiêu**: UC-WEB-16/17 chạy end-to-end; UC-WEB-15 có MVP xem công nợ + ghi nhận thanh toán.

| Ngày | Việc | Đầu ra |
|---|---|---|
| D1 | **Release train (0,5 ngày)**: push `feat/customer-module`, mở PR, chạy integration test bằng Docker, merge `main`; commit fix seed. **Thiết kế đối tác (0,5 ngày)**: đối chiếu `partners` hiện có với yêu cầu (thông tin liên hệ, dịch vụ, chi phí) | PR merged; danh sách cột bổ sung |
| D2 | Migration `0021` bổ sung cột đối tác (liên hệ/SĐT/email/địa chỉ/loại dịch vụ); schema + service | Migration upgrade/downgrade chạy được |
| D3 | API đối tác: `GET/POST/PATCH /partners`, `GET/POST/PATCH/DELETE /partners/{id}/tariffs`; catalog quyền `partner:view`, `partner:manage`; audit | Endpoint + test unit |
| D4 | Validation + test integration; khóa cứng xóa khi đối tác đã được tham chiếu (nếu có), ngược lại chỉ cho ngừng hoạt động | Test xanh; lỗi tiếng Việt |
| D5 | Frontend: trang `/doi-tac` (danh sách, lọc, trạng thái), `PartnerFormModal` | Route + menu + quyền |
| D6 | Frontend: bảng giá mua trong form đối tác (thêm/sửa/xóa dòng), i18n, responsive | Demo được luồng tạo đối tác + bảng giá |
| D7 | **Công nợ — thiết kế + migration `0022`** `customer_payments` (customer_id, amount, method, paid_at, note, created_by); index | Migration + quy ước công thức |
| D8 | API: `GET /customers/{id}/debt?from&to` (phát sinh = bill có `sender_id` = khách, `payer=sender`, không hủy; đã trả = payments; còn nợ = chênh lệch), `POST/GET /customers/{id}/payments`; audit; test | API + test |
| D9 | Tab **Công nợ** trong `CustomerDetailPage` + modal ghi nhận thanh toán; cập nhật wiki/checklist | Demo cuối sprint |

**Tiêu chí nghiệm thu**
- Tạo/sửa/ngừng hoạt động đối tác; thêm/sửa/xóa bảng giá mua; mọi thao tác ghi audit; quyền `partner:*` chặn đúng ở cả API và UI.
- Công nợ tính đúng với bill `payer=sender`, trạng thái khác `cancelled`; tiền trả về dạng chuỗi `Decimal`; ghi nhận thanh toán làm thay đổi số dư; có test cho công thức.
- Không đổi cấu trúc dữ liệu của `bills`/`customers` ngoài migration mới.

**Rủi ro & dự phòng**
- Nếu chưa chốt quy tắc công nợ (kỳ đối soát, thanh toán từng phần) trước D7 → chỉ ship **tab đọc** (phát sinh/đã trả/còn nợ), hoãn ghi nhận thanh toán sang sprint sau.
- Nếu migration `0021` phát sinh nhiều cột hơn dự kiến → cắt bớt trường không bắt buộc, giữ 5 trường cốt lõi.

### 5.3 DEV B — Hoàn thiện lõi phiếu + Hủy giao thành công + Lịch sử + Lấy hàng

**Mục tiêu**: form tạo phiếu đủ trường theo BRD; UC-24 và UC-27 khép kín; UC-18 có MVP tạo/gán/trạng thái.

| Ngày | Việc | Đầu ra |
|---|---|---|
| D1 | **Release train (0,5 ngày)** cùng DEV A (hỗ trợ CI). **Form tạo phiếu (0,5 ngày)**: thêm Select hạng dịch vụ (nhóm trong nước/quốc tế), COD, bảo hiểm, ghi chú; cập nhật zod + default + payload | UI hiển thị đủ trường |
| D2 | Backend: xác nhận validate hạng dịch vụ tồn tại/đang hoạt động (đã có), lưu `cod_amount`/`is_insurance_required`; bổ sung test tạo phiếu có/không có hạng, có COD/bảo hiểm; chốt có bắt buộc hạng dịch vụ không | API + test |
| D3 | **UC-WEB-24 Hủy giao hàng thành công**: endpoint `POST /bills/{id}/rollback` (delivered → in_transit), bắt buộc lý do, quyền `bill:rollback`, ghi status log + audit; UI nút + modal xác nhận; test | API + UI + test |
| D4 | **UC-WEB-27 Lịch sử chỉnh sửa**: render `audit_events` (ai, khi nào, hành động, before/after) thành tab trong chi tiết phiếu; lọc theo loại | Tab lịch sử |
| D5 | Buffer + **CI test job**: thêm job Postgres service, chạy pytest unit + integration, `npm run build` + `npm run lint` (nếu trượt → chuyển sang sprint sau và ghi nợ) | CI xanh |
| D6 | **UC-WEB-18 Lấy hàng — thiết kế + migration `0023`** `pickup_requests` (mã, khách/SĐT/địa chỉ, thời gian mong muốn, bưu tá, trạng thái, người tạo) | Migration |
| D7 | API: `POST/GET/PATCH /pickups`, gán bưu tá, chuyển trạng thái; catalog quyền `pickup:view`, `pickup:manage`; audit | API + test |
| D8 | Frontend: trang `/lay-hang` (danh sách, lọc trạng thái/ngày), modal tạo, dropdown gán bưu tá | Trang + quyền |
| D9 | Nối tạo phiếu từ yêu cầu lấy hàng (gán `bill.shipper_id` nếu kịp) + wiki/checklist | Demo cuối sprint |

**Tiêu chí nghiệm thu**
- Tạo phiếu có hạng dịch vụ/COD/bảo hiểm; API từ chối hạng dịch vụ không tồn tại; dữ liệu in ra đúng hạng đã chọn.
- Hủy giao thành công: chỉ từ `delivered`, bắt buộc lý do, có audit + status log, chỉ người có `bill:rollback`.
- Lịch sử chỉnh sửa hiển thị được ít nhất `bill.updated`, `bill.status_changed`, `bill.printed`.
- Lấy hàng: tạo → gán bưu tá → picked/cancelled; lọc được; audit đầy đủ.

**Rủi ro & dự phòng**
- UC-18 gói 4 ngày là **sát**: nếu D8 chưa xong UI, cắt phần "tạo phiếu từ pickup" (D9) và chỉ ship danh sách + gán bưu tá.
- Trạng thái đích của UC-24 cần chốt trước D3 (xem §6); nếu chưa chốt, tạm dùng `in_transit` và ghi rõ giả định.

**D10–D11 (09–10/11) — buffer chung**: kiểm thử hồi quy toàn bộ luồng (tạo phiếu → in → trạng thái → rollback; đối tác; công nợ; lấy hàng), sửa lỗi phát sinh, chuẩn bị dữ liệu demo và bàn giao đợt 2.

### 5.4 Mốc kiểm tra & demo

| Mốc | Thời điểm | Nội dung |
|---|---|---|
| M0 | D1 cuối ngày | `main` xanh: customer module + seed fix đã merge; build/lint/unit pass |
| M1 | D4 cuối ngày | Demo nội bộ: API đối tác + form tạo phiếu đủ trường + rollback |
| M2 | D6 cuối ngày | Đối tác UI + migration công nợ; tab lịch sử + migration lấy hàng |
| M3 | D11 15:00 | Demo stakeholder: đối tác, công nợ, tạo phiếu, hủy giao, lấy hàng |
| M4 | D11 16:00 | Retro + cập nhật checklist + chốt backlog 11–21/11 |

### 5.5 Ngoài phạm vi 2 tuần này (đã cân nhắc)

- **Kho (28–34)**: chưa có bảng/API; cần thiết kế schema (bao, kiện, tồn kho, bảng kê) trước — dự kiến 11–21/11.
- **Chuyến xe (35/36)**: model có nhưng chưa có luồng nghiệp vụ; phụ thuộc kho.
- **COD (37–39)**: cần `shipper_id` được gán qua UC-18 → làm ngay sau sprint này.
- **Báo cáo (40)**: 20 báo cáo không thể hoàn thành trong 2 tuần; cần chốt danh sách ưu tiên và làm sau khi có dữ liệu vận hành.
- **Bảng giá (14)**: chờ xác nhận công thức/bảng giá của khách (câu hỏi mở trong BRD).
- **Quản trị địa giới (04–06)**, **app nhân viên**: chưa cần cho go-live lõi.

### 5.6 Phương án thay thế (nếu stakeholder ưu tiên đúng Sprint 3)

> Chuyển DEV A sang **thiết kế schema kho + nhập kho (28)** và DEV B sang **chuyến xe (36)**. Đánh đổi: UC-18 (gán bưu tá) chưa có → COD và báo cáo hiệu suất vẫn không có dữ liệu; UC-24/27 tiếp tục treo. **Không khuyến nghị** vì mở thêm 2 mảng lớn khi nền phiếu còn defect.

---

## 6. Việc cần quyết trước khi triển khai

| # | Quyết định | Người quyết | Hạn | Ảnh hưởng nếu chậm |
|---|---|---|---|---|
| Q1 | Merge module khách hàng + commit fix seed vào `main` | Tech lead | 27/10 | Main thiếu UC-13; rủi ro mất việc |
| Q2 | Mốc go-live mới và phạm vi "Giai đoạn 1" (có gồm 20 báo cáo/app không) | PM + khách | 29/10 | Không thể cam kết tiến độ |
| Q3 | "Hủy giao hàng thành công" (24): trạng thái đích (`in_transit`/`picked_up`), ai có quyền, có giới hạn thời gian? | PM | 28/10 | DEV B D3 bị chặn |
| Q4 | Quy tắc công nợ (15): kỳ đối soát, thanh toán từng phần, bill hủy có tính không? | PM + kế toán | 31/10 | Chỉ ship được tab đọc |
| Q5 | Quy tắc bảng giá (14): bảng giá theo khách/nhóm, route type, công thức | PM + khách | 31/10 | Không thể bắt đầu UC-14 |
| Q6 | Loại hàng (12): giữ enum `document/goods` hay merge nhánh `feature/cargotypeconfig` thành catalog? | Tech lead | 31/10 | Ảnh hưởng pricing + báo cáo |
| Q7 | Địa giới (04–06): seed là đủ hay cần màn hình quản trị? | PM | 31/10 | Nếu cần, cộng thêm 3–4 ngày |
| Q8 | App nhân viên có nằm trong giai đoạn 1? | PM | 05/11 | Ảnh hưởng toàn bộ roadmap sau |

---

## 7. Đề xuất 2 tuần kế tiếp (11/11 → 21/11/2026)

- **DEV A**: thiết kế + triển khai kho — nhập kho (28), xuất kho trung chuyển (30), lịch sử xuất/nhập (34); thiết kế trước 29/31/32/33.
- **DEV B**: COD — thu hộ (37), bưu tá nộp tiền (38), thủ quỹ xác nhận (39), dùng `shipper_id` từ UC-18; sau đó chuyến xe (36).
- **Cả hai**: chốt danh sách báo cáo ưu tiên (40) để làm 24/11 → 05/12.
- **Đề xuất mốc**: go-live nghiệp vụ lõi **05/12/2026**, báo cáo **19/12/2026** (thay mốc 10/10 đã trượt).

---

## 8. Phụ lục — Lệnh kiểm chứng

```bash
# Trạng thái mã nguồn
cd veloxship && git status --short && git log --oneline -10
git rev-list --left-right --count origin/main...HEAD

# Backend
cd backend && . venv/bin/activate
pytest tests/unit -q        # 158 passed
pytest -q                   # cần Docker cho testcontainers

# Frontend
cd frontend && npm run build && npm run lint

# Đối chiếu nhanh
grep -rn "@router\." backend/app/api/v1/*.py
grep -n "path:" frontend/src/routes/index.jsx
ls backend/alembic/versions/
```

**Checklist đã được cập nhật cùng ngày**:
- [`checklist-dev-a.md`](./checklist-dev-a.md): sửa trạng thái 01/02 (bỏ), 03/10 (xong), 11/12 (một phần), 14–17 (chưa), thêm ghi chú bằng chứng.
- [`checklist-dev-b.md`](./checklist-dev-b.md): sửa 04/06 (một phần), 05 (không áp dụng), 08 (chưa), 27/35 (một phần), 24/36/37–39 (chưa), thêm ghi chú.
