---
description: "Business Requirements Document (BRD) — VeloxShip Logistics Delivery-Bill Management. Consolidates specs/001-logistics-bill-app and docs/roadmap-tasks.md into a single stakeholder-facing requirements reference."
---

# Tài liệu Yêu cầu Nghiệp vụ — Business Requirements Document (BRD)

**Sản phẩm**: VeloxShip — Ứng dụng Quản lý Phiếu Gửi Vận Chuyển
**Feature v1**: `001-logistics-bill-app` (Quản lý Phiếu Gửi)
**Ngày cập nhật**: 2026-07-12
**Trạng thái**: v1 đang triển khai (MVP đã hoàn thành phần Tạo phiếu — xem §9 Trạng thái hiện tại)
**Nguồn tham chiếu**:
- Đặc tả tính năng: [`specs/001-logistics-bill-app/spec.md`](../specs/001-logistics-bill-app/spec.md)
- Kế hoạch kỹ thuật: [`specs/001-logistics-bill-app/plan.md`](../specs/001-logistics-bill-app/plan.md)
- Mô hình dữ liệu: [`specs/001-logistics-bill-app/data-model.md`](../specs/001-logistics-bill-app/data-model.md)
- Hợp đồng API: [`specs/001-logistics-bill-app/contracts/openapi.yaml`](../specs/001-logistics-bill-app/contracts/openapi.yaml)
- Lộ trình đầy đủ: [`docs/roadmap-tasks.md`](./roadmap-tasks.md)
- Tài liệu tham chiếu ảnh: `image_data/logo.jpg`, `image_data/bill_format.jpg`, `image_data/requirement.jpg`

> Tài liệu này là **nguồn sự thật về nghiệp vụ (business source of truth)**. Khi có mâu thuẫn giữa BRD và các đặc tả kỹ thuật, ưu tiên làm rõ nghiệp vụ tại đây trước, rồi mới cập nhật đặc tả kỹ thuật cho khớp.

---

## 1. Tóm tắt điều hành (Executive Summary)

VeloxShip là phần mềm quản lý vận chuyển cho một hãng chuyển phát nhanh Việt Nam. Nghiệp vụ cốt lõi — điểm khởi đầu của **mọi** lô hàng — là lập **Phiếu Gửi** (shipping slip) tại quầy: nhân viên nhập thông tin người gửi / người nhận, mô tả hàng hoá, chọn dịch vụ, ghi cước phí, lưu và **in phiếu vật lý** có mã vận đơn duy nhất, mã vạch (barcode) và mã QR đúng theo mẫu phiếu của hãng.

Phạm vi **v1 được thu hẹp có chủ đích** vào bốn năng lực: (1) tạo & in phiếu, (2) tra cứu / in lại / cập nhật trạng thái, (3) hồ sơ khách hàng để tự điền, (4) xác thực & nhật ký kiểm toán. Toàn bộ bộ phần mềm logistics đầy đủ (kho, điều xe, thu hộ COD, đối tác, app tài xế, 20+ báo cáo) trong `requirement.jpg` là **lộ trình dài hạn**, được quản lý riêng tại [`docs/roadmap-tasks.md`](./roadmap-tasks.md) và nằm ngoài phạm vi v1.

**Ràng buộc bất biến xuyên suốt**: toàn bộ giao diện, thông báo, và bản in **phải bằng tiếng Việt có dấu đầy đủ**; tra cứu phải **không phân biệt dấu** (gõ không dấu vẫn tìm ra).

---

## 2. Bối cảnh & Vấn đề nghiệp vụ (Business Context & Problem)

| Yếu tố | Mô tả |
|---|---|
| **Ngành** | Chuyển phát nhanh / logistics nội địa & quốc tế tại Việt Nam. |
| **Vấn đề hiện tại** | Lập phiếu gửi thủ công (viết tay / mẫu rời) gây sai sót, chậm, không tra cứu được, không có mã vận đơn thống nhất, khó đối soát. |
| **Cơ hội** | Số hoá khâu lập phiếu để chuẩn hoá dữ liệu ngay từ điểm nhập, tạo nền tảng cho các nghiệp vụ downstream (lấy hàng, trung chuyển, giao hàng, COD, báo cáo). |
| **Người mua / chủ sở hữu** | Hãng chuyển phát (single-tenant — một hãng, một thương hiệu, một hotline/website/footer). |
| **Tài sản thương hiệu** | Logo hãng (`logo.jpg`); bố cục phiếu chuẩn theo `bill_format.jpg` (mẫu tham chiếu mang nhãn NewLinks — ta tái tạo **cấu trúc & nhãn**, thay logo/footer của hãng mình). |

**Tuyên bố giá trị (Value proposition)**: Rút thời gian lập & in một phiếu gửi hoàn chỉnh xuống **dưới 90 giây** cho khách quen và **dưới 3 phút** cho khách mới, với dữ liệu chuẩn hoá, tra cứu tức thời và bản in trung thực với mẫu giấy của hãng.

---

## 3. Mục tiêu nghiệp vụ & Chỉ số thành công (Objectives & Success Metrics)

| Mã | Mục tiêu nghiệp vụ | Chỉ số đo lường (đối chiếu SC trong spec) |
|---|---|---|
| BO-1 | Lập & in phiếu nhanh, ít sai sót | ≤ 90 giây/phiếu (khách quen), ≤ 3 phút (khách mới) — *SC-001* |
| BO-2 | Giao diện & bản in 100% tiếng Việt | Người bản ngữ rà soát: **0** chuỗi ngoại ngữ trong toàn bộ UI — *SC-002* |
| BO-3 | Bản in trung thực với mẫu hãng | Nhân viên hãng chấm độ khớp bố cục ≥ **9/10** so với ảnh mẫu — *SC-003* |
| BO-4 | Tra cứu tức thời trên khối lượng lớn | Trả kết quả < **1 giây** trên tập 100.000 phiếu — *SC-004* |
| BO-5 | Tra cứu không phân biệt dấu | Gõ không dấu tìm được ≥ **99%** bản ghi — *SC-005* |
| BO-6 | Mã vận đơn không trùng khi tạo đồng thời | **0** trùng mã qua stress test 10.000 lượt tạo đồng thời — *SC-006* |
| BO-7 | Giảm sai sót nhập liệu | < **1%** trong 1.000 phiếu đầu cần sửa/huỷ do lỗi nhập — *SC-007* |
| BO-8 | Tận dụng hồ sơ khách quen | **95%** phiếu của khách quay lại dùng luồng tự điền trong 30 ngày đầu — *SC-008* |
| BO-9 | Thao tác vận hành nhanh | In lại & cập nhật trạng thái hoàn tất < **2 giây** — *SC-009* |

---

## 4. Phạm vi (Scope)

### 4.1 Trong phạm vi v1 (In Scope)

1. **Tạo phiếu gửi** — nhập người gửi/nhận, nội dung gói hàng (nhiều dòng), phân loại dịch vụ, cước phí, bên thanh toán; sinh mã vận đơn duy nhất, mã KH, barcode, QR.
2. **In & xuất phiếu** — in vật lý trung thực với mẫu; xuất PDF; in lại bản giống hệt bản gốc (có ghi nhật ký).
3. **Tra cứu & quản lý** — tìm theo mã VĐ / mã KH / SĐT gửi-nhận / tên gửi-nhận / khoảng ngày; tìm không phân biệt dấu; danh sách phân trang; cập nhật trạng thái vòng đời.
4. **Hồ sơ khách hàng** — tạo/sửa/vô hiệu hoá hồ sơ khách quen; chọn khi tạo phiếu để tự điền khối người gửi; **snapshot** thông tin vào phiếu tại thời điểm tạo.
5. **Xác thực & kiểm toán** — đăng nhập JWT; mọi thao tác gắn với người dùng; nhật ký kiểm toán (ai, làm gì, khi nào).
6. **Ngôn ngữ & định dạng VN** — UI/bản in tiếng Việt có dấu; số kiểu Việt (dấu phẩy thập phân); ngày kiểu "ngày … tháng … năm …" trên bản in.

### 4.2 Ngoài phạm vi v1 (Out of Scope — chuyển sang roadmap)

Kho (nhập/xuất/kiểm kê/trung chuyển), điều xe & đội xe, thu hộ COD & nộp tiền, quản lý đối tác & bảng giá mua, quản trị nhân viên/phòng ban/chức vụ/phân quyền nâng cao, quản trị dữ liệu danh mục tỉnh/huyện/xã bằng UI (seed dữ liệu là đủ), app di động cho tài xế, import phiếu hàng loạt từ Excel, 20+ báo cáo nâng cao, cổng tra cứu công khai cho khách. → Xem [`docs/roadmap-tasks.md`](./roadmap-tasks.md).

---

## 5. Đối tượng người dùng (Personas)

| Persona | Vai trò | Nhu cầu chính | Quyền |
|---|---|---|---|
| **Nhân viên quầy** (staff) | Lập phiếu cho khách tại bưu cục | Nhập nhanh, in chuẩn, tự điền khách quen | Tạo/xem/in phiếu, tra cứu, quản lý khách hàng |
| **Giám sát** (supervisor) | Theo dõi vận hành | Tra cứu, cập nhật trạng thái, in lại, xem nhật ký | Như staff + cập nhật trạng thái vòng đời |
| **Quản trị** (admin) | Quản trị hệ thống | Quản lý người dùng (nền tảng cho phân quyền tương lai) | Toàn quyền v1 + quản lý user |

*Ghi chú*: v1 phân biệt 3 vai trò ở tầng dữ liệu (`role` trong bảng `users`); phân quyền chi tiết theo màn hình là hạng mục lộ trình.

---

## 6. Yêu cầu chức năng theo User Story (Functional Requirements)

> Ưu tiên: **P1** = MVP bắt buộc; **P2** = tăng khả năng vận hành; **P3** = nhân năng suất.

### US1 — Tạo phiếu gửi mới cho lô hàng (P1 · MVP) 🎯

**Nghiệp vụ**: Nhân viên quầy tiếp khách có gói hàng → nhập đủ thông tin → **"Lưu & In phiếu"** → hệ thống lưu, sinh mã vận đơn duy nhất + mã KH, xuất bản in đúng mẫu hãng.

| FR | Yêu cầu |
|---|---|
| FR-001 | Lập Phiếu Gửi gồm: người gửi (họ tên, địa chỉ, quận/huyện, tỉnh/TP, SĐT), người nhận (tương tự), nội dung gói (mô tả, số lượng, trọng lượng kg, kích thước D×R×C cm), phân loại dịch vụ, cước phí, bên thanh toán, khối chữ ký. |
| FR-002 | Sinh **mã vận đơn duy nhất**, dễ đọc, **không trùng khi tạo đồng thời** (sequence + unique constraint). |
| FR-003 | Gắn **mã KH** khi người gửi là khách đã lưu. |
| FR-004 | Phân loại hàng: **Tài liệu** hoặc **Hàng hóa/Pack**. |
| FR-005 | Chọn **đúng một** hạng dịch vụ trong nước (CPN, PHT, Đường bộ, 48H, Nguyên chuyến, Khác) **hoặc** đúng một hạng quốc tế (International, Express, Economy, Other) — **không được chọn cả hai**. |
| FR-006 | Ghi cước: Cước chính, Phụ phí xăng dầu, Phụ phí khác, VAT; **Tổng cộng = tổng 4 khoản**; từ chối lưu nếu lệch. |
| FR-007 | Ghi bên thanh toán: **Người gửi** hoặc **Người nhận**. |
| FR-008 | Kiểm tra bắt buộc & định dạng trước khi lưu; thông báo lỗi **tiếng Việt**, chỉ rõ trường thiếu. |

**Tiêu chí chấp nhận (rút gọn)**: điền đủ → lưu → có mã vận đơn + bản in khớp mẫu; thiếu trường → chặn lưu + báo lỗi tiếng Việt; nhận `200,00 kg` (thập phân dấu phẩy); tick "Người nhận thanh toán" hiển thị đúng trên bản in; bản in có logo, hotline/website, dòng chữ ký + ngày kiểu Việt, QR, barcode.

### US2 — Tra cứu, in lại & cập nhật trạng thái (P2)

**Nghiệp vụ**: Sau khi có phiếu, nhân viên/giám sát tìm nhanh mọi phiếu, xem chi tiết, in lại nếu mất/hỏng, và cập nhật trạng thái vòng đời để đội vận hành thấy tình trạng lô hàng theo thời gian thực.

| FR | Yêu cầu |
|---|---|
| FR-009 | Bản in trung thực mẫu `bill_format.jpg`: bố cục, thứ tự khối, nhãn tiếng Việt, vị trí logo, hotline/website/email, footer, khối chữ ký, vị trí mã KH, barcode, QR. |
| FR-010 | Nhúng **barcode** mã hoá mã vận đơn (Code128) và **QR** mã hoá định danh phiếu (+URL tra cứu chuẩn) trên mọi bản in. |
| FR-011 | **In lại** bất kỳ lúc nào, bản giống hệt bản gốc; **ghi nhật ký** sự kiện in lại (ai, khi nào). |
| FR-012 | **Xuất PDF** (ngoài in vật lý). |
| FR-013 | Tìm theo: mã VĐ, mã KH, SĐT gửi, SĐT nhận, tên gửi, tên nhận, khoảng ngày tạo. |
| FR-014 | Tìm **không phân biệt dấu** cho văn bản tiếng Việt (unaccent). |
| FR-015 | Danh sách **phân trang**, mới nhất trước; cột: mã VĐ, tên gửi, tên nhận, trạng thái, tổng cước, ngày tạo. |
| FR-016 | Cập nhật trạng thái vòng đời: **Đã tạo → Đã lấy hàng → Đang vận chuyển → Đã giao / Hoàn trả / Hủy** (theo máy trạng thái §8). |
| FR-017 | **Nhật ký kiểm toán** cho mọi phiếu: tạo/sửa/in/huỷ — ai & khi nào. |

### US3 — Lưu hồ sơ khách hàng thường xuyên để tự điền (P3)

**Nghiệp vụ**: Khách doanh nghiệp gửi hàng ngày; lưu hồ sơ một lần, chọn lại ở các phiếu sau để tự điền khối người gửi, giảm sai sót và thời gian nhập.

| FR | Yêu cầu |
|---|---|
| FR-018 | Tạo/sửa/vô hiệu hoá (soft delete) hồ sơ khách: các trường khối người gửi + mã KH. |
| FR-019 | Chọn khách đã lưu khi tạo phiếu để **tự điền** khối người gửi; các trường tự điền **vẫn sửa được** theo từng phiếu. |
| FR-020 | **Snapshot** thông tin khách vào phiếu tại thời điểm tạo; sửa hồ sơ về sau **không** làm đổi phiếu cũ. Mã KH bất biến sau khi tạo. |

### Yêu cầu nền tảng (áp dụng cho mọi story)

| FR | Yêu cầu |
|---|---|
| FR-021 | **100% UI + bản in bằng tiếng Việt** (nhãn, nút, menu, thông báo lỗi/thành công). |
| FR-022 | Chấp nhận & hiển thị **đầy đủ dấu tiếng Việt** ở mọi trường & bản in. |
| FR-023 | Chấp nhận **định dạng số kiểu Việt** (dấu phẩy thập phân) cho trọng lượng/kích thước/cước; hiển thị nhất quán trên màn hình & bản in. |
| FR-024 | Ngày kiểu Việt ("ngày … tháng … năm …") trên bản in; định dạng quen thuộc trên màn hình. |
| FR-025 | Bắt buộc **đăng nhập** trước khi tạo/sửa/xem phiếu. |
| FR-026 | Gắn **mọi phiếu, thay đổi trạng thái, in** với người dùng đã xác thực. |

---

## 7. Yêu cầu phi chức năng (Non-Functional Requirements)

| Nhóm | Yêu cầu |
|---|---|
| **Hiệu năng** | Tra cứu ≤ 1s trên 100k phiếu (SC-004); in lại & cập nhật trạng thái ≤ 2s (SC-009); p95 latency API tạo phiếu ≤ 300ms. |
| **Đồng thời** | Mã vận đơn không trùng dưới tải đồng thời (sequence DB + unique constraint) — 0 trùng/10.000 lượt (SC-006). |
| **Bản địa hoá** | Tiếng Việt-only v1; giữ trọn dấu ở nhập/lưu/tìm/in; tìm không phân biệt dấu (PostgreSQL `unaccent` + `pg_trgm`). |
| **Tính toàn vẹn** | CHECK ở DB: `fee_total = tổng 4 khoản`; `huy ⇒ có lý do huỷ`; `da_giao ⇒ có delivered_at`. |
| **Độ tin cậy** | Lỗi in không được làm mất phiếu — phiếu vẫn tồn tại & in lại được; không "âm thầm" mất phiếu đang nhập dở (auto-save nháp hoặc báo lỗi rõ). |
| **Bảo mật** | JWT (access + refresh), mật khẩu băm bcrypt; mật khẩu không bao giờ trả qua API; CORS giới hạn origin. |
| **Kiểm toán** | Nhật ký kiểm toán nội bộ cho mọi mutation (không yêu cầu xuất cho cơ quan quản lý ở v1). |
| **Vận hành** | Chạy online (không yêu cầu offline-first v1); single-tenant; máy in văn phòng chuẩn (laser/nhiệt). |
| **Trình duyệt/thiết bị** | 2 phiên bản mới nhất của Chrome/Edge/Firefox/Safari; hiển thị hợp lý trên tablet tại quầy. |
| **Quy mô mục tiêu** | ~10–50 người dùng, ~100k phiếu/năm, ~5k hồ sơ khách; 1 PostgreSQL primary. |

---

## 8. Thực thể & Vòng đời (Entities & Lifecycle)

### 8.1 Thực thể chính (tóm tắt — chi tiết ở `data-model.md`)

- **Phiếu Gửi (`bills`)** — bản ghi trung tâm: mã vận đơn (unique), mã KH (snapshot), snapshot người gửi/nhận inline, phân loại dịch vụ (cargo_type + service_tier_code), cước phí + tổng, bên thanh toán, trạng thái vòng đời, dữ liệu giao/huỷ, kiểm toán, `print_count`.
- **Nội dung gói hàng (`bill_content_lines`)** — 1..N dòng: mô tả, số lượng, trọng lượng, D×R×C.
- **Khách hàng (`customers`)** — hồ sơ khách quen tái sử dụng: mã KH (bất biến), tên hiển thị, địa chỉ, quận/huyện, tỉnh/TP, SĐT, is_active.
- **Dịch vụ (`service_tiers`)** — danh mục hạng dịch vụ (domestic/international) — seed sẵn.
- **Nhân viên (`users`)** — tài khoản đăng nhập; role staff/supervisor/admin.
- **Lịch sử trạng thái (`bill_status_events`)** & **Sự kiện kiểm toán (`audit_events`)** — vết theo dõi.

### 8.2 Máy trạng thái vòng đời phiếu (Bill State Machine)

```
da_tao ──► da_lay_hang ──► dang_van_chuyen ──► da_giao (terminal)
   │            │                  │
   │            └──────────────────┴──────► hoan_tra (terminal)
   │
   └──► huy (huỷ trước khi lấy hàng)
```

| Từ trạng thái | Được chuyển sang |
|---|---|
| `da_tao` (Đã tạo) | `da_lay_hang`, `huy` |
| `da_lay_hang` (Đã lấy hàng) | `dang_van_chuyen`, `hoan_tra`, `huy` |
| `dang_van_chuyen` (Đang vận chuyển) | `da_giao`, `hoan_tra` |
| `da_giao` (Đã giao) | *(kết thúc)* |
| `hoan_tra` (Hoàn trả) | *(kết thúc)* |
| `huy` (Hủy) | *(kết thúc)* |

**Ràng buộc**: chuyển sang `da_giao` cần `delivered_at` (server tự đặt nếu thiếu) + `delivered_to_name`; chuyển sang `huy` cần `cancellation_reason`; **không** được `huy` khi đã `dang_van_chuyen` trở đi.

---

## 9. Trạng thái triển khai hiện tại (Current Implementation Status)

*Đối chiếu mã nguồn thực tế tại `backend/` và `frontend/` ngày 2026-07-12.* Ký hiệu: ✅ Hoàn thành · 🚧 Đang làm/một phần · ⬜ Chưa bắt đầu.

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| **Hạ tầng nền tảng** (auth JWT, config, i18n, DB session, migrations, seed, app shell, đăng nhập, danh mục dịch vụ) | ✅ | Đầy đủ và đã wire trong `main.py`; migrations `0001`–`0003` + `0002b_customers`. |
| **US1 — Tạo phiếu gửi** (P1/MVP) | ✅ | Model + migration `0003_bills`, CRUD, `bill_service`, `POST/GET /bills`, `print_service` + `bill_template.html` + `print.css`, form frontend đầy đủ (Sender/Receiver/Content/ServiceTier/Fee) + `BillPrintView` (barcode/QR) + tải PDF. |
| **US2 — Danh sách phiếu** | ✅ | `GET /bills` phân trang; `BillListPage` hiển thị bảng + trạng thái. |
| **US2 — In lại / Xuất PDF** | ✅ | `GET /bills/{id}/print?as=pdf\|html` tăng `print_count` + ghi kiểm toán; nút tải PDF ở chi tiết. |
| **US2 — Tra cứu không phân biệt dấu** | 🚧 | `list_bills` **chưa** có tham số tìm/lọc; **thiếu** `search_service.py`; ô tìm kiếm ở `BillListPage` chưa có. |
| **US2 — Cập nhật trạng thái vòng đời** | 🚧 | **Thiếu** `POST /bills/{id}/status`, `transition_status` trong `bill_service`, endpoint `by-tracking`, `events`, và `StatusUpdateDrawer` frontend. `api/bills.js` đã có hàm gọi nhưng backend chưa có endpoint (sẽ 404). |
| **US3 — Hồ sơ khách hàng** (P3) | ⬜ | Chỉ có model `customers` + migration. **Thiếu** `crud/customer.py`, `customer_service.py`, router `customers.py` (chưa wire `main.py`), toàn bộ frontend khách hàng (đang là trang placeholder), `api/customers.js`, `CustomerPicker`, tự điền người gửi. |
| **Kiểm thử & tôi luyện** (Phase 6) | ⬜ | Thư mục test chỉ có `__init__.py`; chưa có test đồng thời (SC-006), tìm không dấu (SC-005), CHECK cước, drift OpenAPI, hiệu năng (SC-004), audit chuỗi tiếng Việt. |

**Kết luận MVP**: Nghiệp vụ cốt lõi (đăng nhập → tạo → in phiếu tiếng Việt có mã vận đơn/barcode/QR) **đã chạy được**. Hai hạng mục cần hoàn thiện tiếp theo để "đủ vận hành": **(1)** tra cứu không phân biệt dấu + cập nhật trạng thái (US2 phần còn lại), **(2)** hồ sơ khách hàng tự điền (US3).

---

## 10. Các trường hợp biên & Quy tắc nghiệp vụ (Edge Cases & Rules)

- **Dấu tiếng Việt**: giữ trọn ở nhập/lưu/tìm/in; tìm khớp cả bản không dấu ("ha" tìm ra "Hà").
- **Số kiểu Việt**: dấu phẩy `,` là thập phân, dấu chấm `.` là hàng nghìn — chấp nhận & hiển thị nhất quán.
- **Địa chỉ linh hoạt**: hỗ trợ địa chỉ tự do (VD "KCN VSIP, Đường 3A, TP Từ Sơn") song song với trường Quận/Huyện & Tỉnh/TP.
- **Chống trùng mã**: hai nhân viên tạo đồng thời **không bao giờ** nhận cùng mã vận đơn.
- **Gián đoạn giữa chừng**: mất kết nối/sập máy → phiếu dở không được **âm thầm** mất (auto-save nháp hoặc báo lỗi rõ).
- **Lỗi in**: máy in hỏng/kẹt → phiếu vẫn tồn tại & in lại được sau.
- **Huỷ sau khi tạo**: phiếu huỷ trước khi lấy hàng → đánh dấu `huy`, loại khỏi đếm vận hành nhưng **giữ để kiểm toán**.
- **Hàng quá khổ / nhiều dòng**: bản in vẫn phải đọc được, không tràn mẫu.
- **Loại trừ nội địa/quốc tế**: không được đánh dấu đồng thời hạng "quốc tế" và "trong nước" trên cùng phiếu.
- **Nhất quán cước/VAT**: Cước chính + Phụ phí xăng dầu + Phụ phí khác + VAT = Tổng cộng — bắt buộc khi lưu.
- **Đổi ca đăng nhập**: người dùng mới không thấy dữ liệu nháp của người trước trừ khi được gán rõ ràng.

---

## 11. Giả định & Ràng buộc (Assumptions & Constraints)

- Phạm vi v1 **cố ý hẹp** (chỉ lập phiếu + tra cứu + trạng thái + khách hàng + in); các module còn lại → roadmap.
- Người dùng chính là **nhân viên quầy/bưu cục**, không phải khách tự phục vụ.
- **Single-tenant** (một hãng); đa hãng nằm ngoài phạm vi.
- **Tiếng Việt-only** v1; đa ngôn ngữ để sau.
- **Cước nhập tay** v1; máy tính cước theo bảng giá là nâng cấp tương lai.
- **Máy in văn phòng chuẩn**; hệ thống xuất tài liệu in được, việc chọn máy in vật lý là của người vận hành.
- **Hoạt động online**; offline-first ngoài phạm vi.
- **Kiểm toán nội bộ**; không yêu cầu xuất cho cơ quan quản lý ở v1.
- **Thương hiệu**: dùng logo hãng; tái tạo **cấu trúc/nhãn** mẫu phiếu, thay logo & footer của hãng mình.

---

## 12. Kiến trúc kỹ thuật (tóm tắt — chi tiết ở `plan.md`)

- **Frontend**: React 18 (JavaScript) + Vite, Ant Design (locale `vi_VN`), React Query, React Hook Form + Zod, `jsbarcode` + `qrcode.react`, `react-to-print`, `dayjs` (locale `vi`).
- **Backend**: Python 3.11 + FastAPI, SQLAlchemy 2.x async, Alembic, Pydantic v2, `python-jose` (JWT), `passlib[bcrypt]`, `weasyprint` (HTML→PDF), `qrcode` + `python-barcode`, `unidecode`.
- **CSDL**: PostgreSQL 16 với `unaccent`, `pg_trgm`, `citext`; bản in trung thực qua `bill_template.html` (WeasyPrint cho PDF + in trình duyệt cho xem trước).
- **Cấu trúc**: monorepo `backend/` (api → services → crud → models) + `frontend/` (feature-folder, chuỗi tiếng Việt gom về `src/i18n/vi.js`).

---

## 13. Bước tiếp theo được khuyến nghị (Recommended Next Steps)

1. **Hoàn thiện US2** — thêm `search_service` + tham số tìm/lọc cho `GET /bills` (unaccent + trigram); thêm `POST /bills/{id}/status`, `by-tracking`, `events` và `transition_status`; ô tìm kiếm + `StatusUpdateDrawer` ở frontend.
2. **Triển khai US3** — `crud/customer` + `customer_service` + router `customers` (wire `main.py`); frontend `api/customers.js`, `CustomerListPage`, `CustomerFormDrawer`, `CustomerPicker` + tự điền người gửi + snapshot server-side.
3. **Phase 6** — bổ sung test cho SC-004/005/006, CHECK cước, drift OpenAPI, và script rà chuỗi tiếng Việt (SC-002).
4. **Đối soát bản in** — nhân viên hãng chấm độ khớp so với `bill_format.jpg` (mục tiêu ≥ 9/10, SC-003).

---

*Tài liệu này được sinh từ đặc tả `specs/001-logistics-bill-app/` và lộ trình `docs/roadmap-tasks.md`, đối chiếu với mã nguồn thực tế. Cập nhật khi phạm vi hoặc trạng thái triển khai thay đổi.*
