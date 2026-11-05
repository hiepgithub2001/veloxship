---
description: "Danh sách nhiệm vụ phát triển cho DEV A - Phần mềm Hoàng Nam Express (Giai đoạn 1)"
---

# Bảng Theo Dõi Nhiệm Vụ DEV A — Hoàng Nam Express (Giai đoạn 1)

> **Chú thích trạng thái**: `[x]` = Hoàn thành · `[~]` = Đang làm/một phần · `[ ]` = Chưa bắt đầu · `[-]` = Bỏ/không còn áp dụng.
> **Tài liệu tham chiếu**: [`docs/ke-hoach-trien-khai.md`](./ke-hoach-trien-khai.md), [`Kế hoạch triển khai dự án phần mềm Hoàng Nam - Giai đoạn 1.csv`](../Kế%20hoạch%20triển%20khai%20dự%20án%20phần%20mềm%20Hoàng%20Nam%20-%20Giai%20đoạn%201.csv).
> **Lưu ý**: Đã bỏ qua Sprint 0 (Pair DB migration & setup đã hoàn thành).
>
> **Cập nhật 27/10/2026**: Đối chiếu lại với mã nguồn (`feat/customer-module` @ `2dec977`). Lịch sprint bên dưới là lịch gốc và **đã quá hạn**; kế hoạch hiện hành xem [`ke-hoach-2-tuan-2026-10-27.md`](./ke-hoach-2-tuan-2026-10-27.md). Trạng thái `[x]` chỉ được đánh khi có API + UI + phân quyền + test.

---

## Sprint 1 — Nền tảng Hệ thống (04/08/2026 -> 15/08/2026)

### 1. QUẢN LÝ NHÂN VIÊN
- [-] **[UC-WEB-01] Quản lý phòng ban**: Xem danh sách, thêm, sửa, xóa phòng ban trên hệ thống *(Bỏ theo refactor `7f0c7fa` ngày 14/10; không còn màn hình/API phòng ban)*
- [-] **[UC-WEB-02] Quản lý chức vụ**: Xem danh sách, thêm, sửa, xóa chức vụ nhân sự *(Bỏ cùng refactor `7f0c7fa`)*
- [x] **[UC-WEB-03] Quản lý nhân viên**: Xem danh sách, thêm mới, cập nhật thông tin, phân vai trò tài khoản nhân viên. Bao gồm thông tin Phòng Ban, Chức vụ, Phân quyền *(Đã xong: `users.py` 7 endpoint, `StaffPage`, vai trò động; phòng ban/chức vụ đã gỡ)*

### 2. QUẢN LÝ CÀI ĐẶT (Phân quyền)
- [x] **[UC-WEB-10] Quản lý phân quyền**: Tạo các nhóm quyền và gán chức năng chi tiết cho từng chức vụ/vai trò *(Đã xong: bảng `roles` + `role_permissions`, `permissions.py` 6 endpoint, `PermissionPage`)*

---

## Sprint 2 — Nghiệp vụ Chính (18/08/2026 -> 05/09/2026)

### 1. QUẢN LÝ CÀI ĐẶT (Dịch vụ & Loại hàng hóa)
- [~] **[UC-WEB-11] Quản lý dịch vụ / dịch vụ gia tăng**: Cấu hình dịch vụ vận chuyển chính (tiêu chuẩn, hỏa tốc) và dịch vụ gia tăng (bảo hiểm, giao tận tay) *(Mới có seed 9 hạng + `GET /service-tiers`; chưa có màn hình quản trị, form tạo phiếu chưa chọn hạng)*
- [~] **[UC-WEB-12] Quản lý loại hàng hóa**: Phân loại nhóm hàng hóa (hàng cồng kềnh, dễ vỡ, tài liệu, chất lỏng) phục vụ tính phí *(Đang dùng enum cứng `document`/`goods`; module `cargo_types` chỉ ở nhánh `feature/cargotypeconfig` chưa merge)*

### 2. QUẢN LÝ KHÁCH HÀNG
- [x] **[UC-WEB-13] Quản lý thông tin khách hàng**: Quản lý danh sách khách hàng gửi, phân loại nhóm khách hàng *(Đã xong 21/10: xem/tạo/sửa hồ sơ, lịch sử phiếu, chỉ số; địa chỉ lưu trong `metadata`, không đổi cấu trúc bảng)*
- [ ] **[UC-WEB-14] Quản lý bảng giá**: Thiết lập bảng giá cước chi tiết áp dụng cho từng khách hàng hoặc nhóm khách hàng *(Chưa có bảng `price_sheets`/`price_rules`; cần xác nhận công thức/bảng giá với khách hàng trước)*
- [ ] **[UC-WEB-15] Quản lý công nợ**: Kiểm soát công nợ khách hàng gửi theo định kỳ, lập bảng đối soát, ghi nhận thanh toán *(Chưa có schema thanh toán/công nợ; kế hoạch MVP 03–10/11)*

### 3. QUẢN LÝ ĐỐI TÁC
- [ ] **[UC-WEB-16] Quản lý thông tin đối tác**: Quản lý thông tin các đối tác liên kết vận chuyển bên thứ ba (3PL) (Bao gồm thông tin dịch vụ, chi phí) *(Đã có bảng `partners` + model; chưa có API/UI — làm 27–30/10)*
- [ ] **[UC-WEB-17] Quản lý bảng giá mua**: Quản lý bảng giá cước mua dịch vụ từ các đối tác 3PL *(Đã có `partner_tariffs` + model; chưa có API/UI)*

---

## Sprint 3 — Nghiệp vụ Nâng cao (08/09/2026 -> 26/09/2026)

### 1. QUẢN LÝ KHO
> Chưa có bảng/API/UI kho; các mã quyền `warehouse:*` mới chỉ nằm trong catalog. Dự kiến thiết kế + làm từ 10/11/2026.

- [ ] **[UC-WEB-28] Nhập kho**: Quét mã vạch nhập kho bưu cục khi nhận hàng từ bưu tá hoặc bưu cục khác chuyển đến
- [ ] **[UC-WEB-29] Kiểm điểm kho**: Đối soát, kiểm kê số lượng hàng thực tế tồn trong kho bưu cục (Đối soát số lượng, danh sách hàng hóa, tổng cân nặng)
- [ ] **[UC-WEB-30] Xuất kho trung chuyển**: Quét mã vạch xuất bao hàng trung chuyển đi bưu cục tiếp theo hoặc kho tổng (Xuất bảng kê bao chi tiết hàng hóa các bill đến bưu cục/kho/chi nhánh)
- [ ] **[UC-WEB-31] Xuất hàng đối tác**: Quét xuất kho bàn giao hàng cho đối tác vận chuyển bên thứ ba (3PL) (Xuất bảng kê chuyển các bill qua đối tác)
- [ ] **[UC-WEB-32] Xuất kho giao hàng**: Quét bàn giao danh sách đơn hàng cho bưu tá đi phát (Xuất bảng kê cho tài xế/nhân viên phát hàng)
- [ ] **[UC-WEB-33] Xuất kho trả hàng**: Thực hiện xuất kho trả hàng hoàn về cho người gửi *(Ghi chú: Chưa cần dùng đến mục này trong giai đoạn hiện tại)*
- [ ] **[UC-WEB-34] Lịch sử xuất/nhập kho**: Theo dõi chi tiết lịch sử và thời gian thực hiện xuất/nhập kho của từng đơn hàng

---

## Sprint 4 — Báo cáo Thống kê (29/09/2026 -> 10/10/2026)

### 1. BÁO CÁO TÀI CHÍNH (DEV A - 10 Báo cáo)
> Chưa có report engine/API/UI. Cần chốt danh sách ưu tiên trước khi triển khai.

- [ ] **[UC-WEB-40-A01] Báo cáo doanh thu tổng hợp**: Thống kê doanh thu theo khoảng thời gian (ngày, tuần, tháng, quý, năm)
- [ ] **[UC-WEB-40-A02] Báo cáo doanh thu theo bưu cục/chi nhánh**: Phân tích doanh thu phát sinh theo từng đơn vị vận hành
- [ ] **[UC-WEB-40-A03] Báo cáo doanh thu theo khách hàng**: Thống kê doanh thu chi tiết cho từng khách hàng hoặc nhóm khách hàng
- [ ] **[UC-WEB-40-A04] Báo cáo doanh thu dịch vụ gia tăng**: Thống kê doanh thu từ các dịch vụ phụ phí, bảo hiểm, giao tận tay
- [ ] **[UC-WEB-40-A05] Báo cáo công nợ khách hàng gửi**: Bảng tổng hợp công nợ chưa thanh toán theo kỳ đối soát
- [ ] **[UC-WEB-40-A06] Báo cáo lịch sử thanh toán công nợ**: Theo dõi các đợt thanh toán và số dư nợ còn lại của khách hàng
- [ ] **[UC-WEB-40-A07] Báo cáo chi phí đối tác (3PL)**: Thống kê tổng chi phí cước mua từ các đối tác vận chuyển thứ ba
- [ ] **[UC-WEB-40-A08] Báo cáo chênh lệch cước phí (Lợi nhuận gộp)**: Báo cáo đối soát giữa cước thu khách hàng và cước trả đối tác/vận hành
- [ ] **[UC-WEB-40-A09] Báo cáo tổng hợp dòng tiền COD**: Thống kê dòng tiền COD đã thu, đã chuyển trả khách hàng và còn tồn giữ
- [ ] **[UC-WEB-40-A10] Báo cáo nợ cước tồn đọng**: Thống kê các khoản cước quá hạn chưa thu hồi
