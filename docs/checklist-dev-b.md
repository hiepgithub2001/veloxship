---
description: "Danh sách nhiệm vụ phát triển cho DEV B - Phần mềm Hoàng Nam Express (Giai đoạn 1)"
---

# Bảng Theo Dõi Nhiệm Vụ DEV B — Hoàng Nam Express (Giai đoạn 1)

> **Chú thích trạng thái**: `[x]` = Hoàn thành · `[~]` = Đang làm/một phần · `[ ]` = Chưa bắt đầu.  
> **Tài liệu tham chiếu**: [`docs/ke-hoach-trien-khai.md`](./ke-hoach-trien-khai.md), [`Kế hoạch triển khai dự án phần mềm Hoàng Nam - Giai đoạn 1.csv`](../Kế%20hoạch%20triển%20khai%20dự%20án%20phần%20mềm%20Hoàng%20Nam%20-%20Giai%20đoạn%201.csv).  
> **Lưu ý**: Đã bỏ qua Sprint 0 (Pair DB migration & setup đã hoàn thành).

---

## Sprint 1 — Nền tảng Hệ thống (04/08/2026 -> 15/08/2026)

### 1. QUẢN LÝ CÀI ĐẶT (Địa giới, Bưu cục & Đội xe)
- [ ] **[UC-WEB-04] Quản lý tỉnh thành**: Quản lý danh mục Tỉnh/Thành phố trên toàn quốc
- [ ] **[UC-WEB-05] Quản lý quận huyện**: Quản lý danh mục Quận/Huyện liên kết với Tỉnh/Thành
- [ ] **[UC-WEB-06] Quản lý phường xã**: Quản lý danh mục Phường/Xã/Thị trấn trực thuộc Quận/Huyện
- [ ] **[UC-WEB-07] Quản lý Trung tâm/ Chi nhánh/ Bưu cục**: Xem danh sách, thêm, sửa, thiết lập bưu cục giao nhận
- [ ] **[UC-WEB-08] Quản lý khu vực/ tuyến giao nhận**: Cấu hình khu vực hoạt động, tuyến đường vận chuyển của bưu cục *(Gộp vào UC-WEB-07)*
- [ ] **[UC-WEB-09] Quản lý đội xe**: Đăng ký thông tin xe, phân loại xe tải/xe máy

---

## Sprint 2 — Nghiệp vụ Chính (18/08/2026 -> 05/09/2026)

### 1. QUẢN LÝ VẬN ĐƠN
- [ ] **[UC-WEB-18] Quản lý lấy hàng**: Tiếp nhận yêu cầu gửi hàng từ khách hàng, điều phối bưu tá đi lấy hàng
- [ ] **[UC-WEB-19] Tạo vận đơn**: Nhập thủ công thông tin người gửi, người nhận, hàng hóa, cước phí để tạo 1 vận đơn mới
- [ ] **[UC-WEB-23] Danh sách vận đơn**: Bộ lọc tra cứu trạng thái, hành trình chi tiết của mọi vận đơn trong hệ thống
- [ ] **[UC-WEB-24] Hủy giao hàng thành công**: Xử lý nghiệp vụ hủy trạng thái giao hàng thành công khi có khiếu nại hoặc lỗi cập nhật
- [ ] **[UC-WEB-26] Điều chỉnh COD**: Cập nhật/điều chỉnh số tiền thu hộ (COD) trước khi xuất kho đi giao
- [ ] **[UC-WEB-27] Lịch sử điều chỉnh đơn hàng**: Truy vết (Audit Log) toàn bộ lịch sử chỉnh sửa thông tin vận đơn

---

## Sprint 3 — Nghiệp vụ Nâng cao (08/09/2026 -> 26/09/2026)

### 1. QUẢN LÝ CHUYỂN XE
- [ ] **[UC-WEB-35] Quản lý đội xe**: Theo dõi tình trạng hoạt động, lịch trình sử dụng của đội xe tải vận chuyển
- [ ] **[UC-WEB-36] Quản lý chuyến xe**: Tạo chuyến xe, gán tài xế, bốc xếp bao hàng lên xe và xuất phát hành trình liên tỉnh/nội thành

### 2. QUẢN LÝ THU TIỀN (COD)
- [ ] **[UC-WEB-37] Quản lý thu hộ**: Theo dõi đối soát tổng dòng tiền thu hộ COD từ các đơn phát thành công
- [ ] **[UC-WEB-38] Thu tiền nhân viên**: Bưu tá nộp tiền COD tiền mặt thu được trong ngày về bưu cục, lập bảng kê thu tiền
- [ ] **[UC-WEB-39] Xác nhận thu tiền**: Thủ quỹ bưu cục xác nhận đã nhận đủ tiền thực tế từ bưu tá dựa trên bảng kê

---

## Sprint 4 — Báo cáo Thống kê (29/09/2026 -> 10/10/2026)

### 1. BÁO CÁO VẬN HÀNH (DEV B - 10 Báo cáo)
- [ ] **[UC-WEB-40-B01] Báo cáo sản lượng vận đơn**: Thống kê số lượng vận đơn tạo mới và xử lý theo khoảng thời gian
- [ ] **[UC-WEB-40-B02] Báo cáo tỷ lệ giao hàng**: Thống kê tỷ lệ giao thành công, giao thất bại, và tỷ lệ chuyển hoàn
- [ ] **[UC-WEB-40-B03] Báo cáo hiệu suất bưu tá (Shipper)**: Đánh giá số lượng đơn lấy/phát thành công và thời gian xử lý của bưu tá
- [ ] **[UC-WEB-40-B04] Báo cáo sản lượng lấy hàng**: Thống kê chi tiết lượng đơn đã lấy theo bưu cục và tuyến giao nhận
- [ ] **[UC-WEB-40-B05] Báo cáo tồn kho bưu cục**: Thống kê lượng hàng đang lưu kho và thời gian tồn kho trung bình
- [ ] **[UC-WEB-40-B06] Báo cáo vận hành chuyến xe**: Thống kê số lượng chuyến xe đã chạy, tải trọng trung bình và tỷ lệ lấp đầy
- [ ] **[UC-WEB-40-B07] Báo cáo thời gian luân chuyển (Lead time)**: Báo cáo đo lường thời gian xử lý đơn hàng từ lúc gửi đến lúc phát thành công
- [ ] **[UC-WEB-40-B08] Báo cáo xử lý sự cố/khiếu nại**: Thống kê các đơn hàng bị hoãn giao, hỏng hóc, hoặc phát sinh khiếu nại
- [ ] **[UC-WEB-40-B09] Báo cáo sản lượng gửi đối tác 3PL**: Thống kê số lượng vận đơn bàn giao cho từng đối tác vận chuyển
- [ ] **[UC-WEB-40-B10] Báo cáo nộp tiền bưu tá**: Thống kê các bảng kê nộp tiền COD của bưu tá và trạng thái xác nhận của thủ quỹ
