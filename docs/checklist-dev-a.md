---
description: "Danh sách nhiệm vụ phát triển cho DEV A - Phần mềm Hoàng Nam Express (Giai đoạn 1)"
---

# Bảng Theo Dõi Nhiệm Vụ DEV A — Hoàng Nam Express (Giai đoạn 1)

> **Chú thích trạng thái**: `[x]` = Hoàn thành · `[~]` = Đang làm/một phần · `[ ]` = Chưa bắt đầu.  
> **Tài liệu tham chiếu**: [`docs/ke-hoach-trien-khai.md`](./ke-hoach-trien-khai.md), [`Kế hoạch triển khai dự án phần mềm Hoàng Nam - Giai đoạn 1.csv`](../Kế%20hoạch%20triển%20khai%20dự%20án%20phần%20mềm%20Hoàng%20Nam%20-%20Giai%20đoạn%201.csv).  
> **Lưu ý**: Đã bỏ qua Sprint 0 (Pair DB migration & setup đã hoàn thành).

---

## Sprint 1 — Nền tảng Hệ thống (04/08/2026 -> 15/08/2026)

### 1. QUẢN LÝ NHÂN VIÊN
- [ ] **[UC-WEB-01] Quản lý phòng ban**: Xem danh sách, thêm, sửa, xóa phòng ban trên hệ thống *(Gộp chung vào giao diện UC-WEB-03)*
- [ ] **[UC-WEB-02] Quản lý chức vụ**: Xem danh sách, thêm, sửa, xóa chức vụ nhân sự *(Gộp chung vào giao diện UC-WEB-03)*
- [ ] **[UC-WEB-03] Quản lý nhân viên**: Xem danh sách, thêm mới, cập nhật thông tin, phân vai trò tài khoản nhân viên. Bao gồm thông tin Phòng Ban, Chức vụ, Phân quyền

### 2. QUẢN LÝ CÀI ĐẶT (Phân quyền)
- [ ] **[UC-WEB-10] Quản lý phân quyền**: Tạo các nhóm quyền và gán chức năng chi tiết cho từng chức vụ/vai trò

---

## Sprint 2 — Nghiệp vụ Chính (18/08/2026 -> 05/09/2026)

### 1. QUẢN LÝ CÀI ĐẶT (Dịch vụ & Loại hàng hóa)
- [ ] **[UC-WEB-11] Quản lý dịch vụ / dịch vụ gia tăng**: Cấu hình dịch vụ vận chuyển chính (tiêu chuẩn, hỏa tốc) và dịch vụ gia tăng (bảo hiểm, giao tận tay) *(Gộp chung với UC-WEB-12)*
- [ ] **[UC-WEB-12] Quản lý loại hàng hóa**: Phân loại nhóm hàng hóa (hàng cồng kềnh, dễ vỡ, tài liệu, chất lỏng) phục vụ tính phí *(Gộp vào UC-WEB-11)*

### 2. QUẢN LÝ KHÁCH HÀNG
- [ ] **[UC-WEB-13] Quản lý thông tin khách hàng**: Quản lý danh sách khách hàng gửi, phân loại nhóm khách hàng *(Lưu ý: Xác nhận thông tin chi tiết với khách hàng)*
- [ ] **[UC-WEB-14] Quản lý bảng giá**: Thiết lập bảng giá cước chi tiết áp dụng cho từng khách hàng hoặc nhóm khách hàng *(Lưu ý: Xác nhận công thức/bảng giá chi tiết với khách hàng)*
- [ ] **[UC-WEB-15] Quản lý công nợ**: Kiểm soát công nợ khách hàng gửi theo định kỳ, lập bảng đối soát, ghi nhận thanh toán

### 3. QUẢN LÝ ĐỐI TÁC
- [ ] **[UC-WEB-16] Quản lý thông tin đối tác**: Quản lý thông tin các đối tác liên kết vận chuyển bên thứ ba (3PL) (Bao gồm thông tin dịch vụ, chi phí)
- [ ] **[UC-WEB-17] Quản lý bảng giá mua**: Quản lý bảng giá cước mua dịch vụ từ các đối tác 3PL *(Gộp vào UC-WEB-16)*

---

## Sprint 3 — Nghiệp vụ Nâng cao (08/09/2026 -> 26/09/2026)

### 1. QUẢN LÝ KHO
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
