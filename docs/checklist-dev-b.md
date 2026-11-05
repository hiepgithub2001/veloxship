---
description: "Danh sách nhiệm vụ phát triển cho DEV B - Phần mềm Hoàng Nam Express (Giai đoạn 1)"
---

# Bảng Theo Dõi Nhiệm Vụ DEV B — Hoàng Nam Express (Giai đoạn 1)

> **Chú thích trạng thái**: `[x]` = Hoàn thành · `[~]` = Đang làm/một phần · `[ ]` = Chưa bắt đầu · `[-]` = Bỏ/không còn áp dụng.
> **Tài liệu tham chiếu**: [`docs/ke-hoach-trien-khai.md`](./ke-hoach-trien-khai.md), [`Kế hoạch triển khai dự án phần mềm Hoàng Nam - Giai đoạn 1.csv`](../Kế%20hoạch%20triển%20khai%20dự%20án%20phần%20mềm%20Hoàng%20Nam%20-%20Giai%20đoạn%201.csv).
> **Lưu ý**: Đã bỏ qua Sprint 0 (Pair DB migration & setup đã hoàn thành).
>
> **Cập nhật 27/10/2026**: Đối chiếu lại với mã nguồn (`feat/customer-module` @ `2dec977`). Lịch sprint bên dưới là lịch gốc và **đã quá hạn**; kế hoạch hiện hành xem [`ke-hoach-2-tuan-2026-10-27.md`](./ke-hoach-2-tuan-2026-10-27.md). Trạng thái `[x]` chỉ được đánh khi có API + UI + phân quyền + test.

---

## Sprint 1 — Nền tảng Hệ thống (04/08/2026 -> 15/08/2026)

### 1. QUẢN LÝ CÀI ĐẶT (Địa giới, Bưu cục & Đội xe)
- [~] **[UC-WEB-04] Quản lý tỉnh thành**: Quản lý danh mục Tỉnh/Thành phố trên toàn quốc *(Seed 34 tỉnh + `GET /locations/provinces`; chưa có màn hình quản trị — đúng phạm vi seed của BRD)*
- [-] **[UC-WEB-05] Quản lý quận huyện**: Quản lý danh mục Quận/Huyện liên kết với Tỉnh/Thành *(Cấp huyện đã bỏ theo migration `0005`; địa chỉ dùng 2 cấp tỉnh → phường/xã)*
- [~] **[UC-WEB-06] Quản lý phường xã**: Quản lý danh mục Phường/Xã/Thị trấn trực thuộc Quận/Huyện *(Seed 3.321 phường/xã + API đọc theo tỉnh; chưa có màn hình quản trị)*
- [x] **[UC-WEB-07] Quản lý Trung tâm/ Chi nhánh/ Bưu cục**: Xem danh sách, thêm, sửa, thiết lập bưu cục giao nhận *(Đã xong: `depots.py`, `DepotListPage`, ảnh + trạng thái)*
- [ ] **[UC-WEB-08] Quản lý khu vực/ tuyến giao nhận**: Cấu hình khu vực hoạt động, tuyến đường vận chuyển của bưu cục *(Chưa có trường khu vực/tuyến trong `Depot`, không API/UI — checklist cũ đánh dấu `[x]` là sai)*
- [x] **[UC-WEB-09] Quản lý đội xe**: Đăng ký thông tin xe, phân loại xe tải/xe máy *(Đã xong: `vehicles.py`, `VehicleListPage`, loại xe + trạng thái + tài xế + ảnh)*

---

## Sprint 2 — Nghiệp vụ Chính (18/08/2026 -> 05/09/2026)

### 1. QUẢN LÝ VẬN ĐƠN
- [ ] **[UC-WEB-18] Quản lý lấy hàng**: Tiếp nhận yêu cầu gửi hàng từ khách hàng, điều phối bưu tá đi lấy hàng *(Chưa có bảng/API/UI; kế hoạch 03–10/11 — cần trước COD vì bill chưa được gán `shipper_id`)*
- [x] **[UC-WEB-19] Tạo vận đơn**: Nhập thủ công thông tin người gửi, người nhận, hàng hóa, cước phí để tạo 1 vận đơn mới *(Đã xong MVP; còn thiếu chọn hạng dịch vụ/COD/bảo hiểm ngay trên form tạo — xử lý 27–28/10)*
- [x] **[UC-WEB-23] Danh sách vận đơn**: Bộ lọc tra cứu trạng thái, hành trình chi tiết của mọi vận đơn trong hệ thống *(Đã xong: lọc trạng thái/ngày/mã/người gửi/nhận, xuất Excel, in hàng loạt)*
- [ ] **[UC-WEB-24] Hủy giao hàng thành công**: Xử lý nghiệp vụ hủy trạng thái giao hàng thành công khi có khiếu nại hoặc lỗi cập nhật *(Chỉ có mã quyền `bill:rollback`; `delivered` không có transition ra — làm 29/10)*
- [x] **[UC-WEB-26] Điều chỉnh COD**: Cập nhật/điều chỉnh số tiền thu hộ (COD) trước khi xuất kho đi giao *(Điều chỉnh qua `PATCH /bills` + `BillCommercialEditor` khi trạng thái `created`)*
- [~] **[UC-WEB-27] Lịch sử điều chỉnh đơn hàng**: Truy vết (Audit Log) toàn bộ lịch sử chỉnh sửa thông tin vận đơn *(Audit event được ghi + trả về qua `/bills/{id}/events`; UI mới hiển thị timeline trạng thái, chưa render audit — làm 30/10)*

---

## Sprint 3 — Nghiệp vụ Nâng cao (08/09/2026 -> 26/09/2026)

### 1. QUẢN LÝ CHUYỂN XE
- [~] **[UC-WEB-35] Quản lý đội xe**: Theo dõi tình trạng hoạt động, lịch trình sử dụng của đội xe tải vận chuyển *(Có trạng thái/tài xế/ảnh; chưa có lịch trình sử dụng)*
- [ ] **[UC-WEB-36] Quản lý chuyến xe**: Tạo chuyến xe, gán tài xế, bốc xếp bao hàng lên xe và xuất phát hành trình liên tỉnh/nội thành *(Có model `linehauls`; chưa có API/UI)*

### 2. QUẢN LÝ THU TIỀN (COD)
> Có model `cod_handovers`/`cod_handover_items`/`depot_ledgers`; chưa có API/UI. Phụ thuộc UC-WEB-18 để gán `shipper_id` — dự kiến 11–21/11.

- [ ] **[UC-WEB-37] Quản lý thu hộ**: Theo dõi đối soát tổng dòng tiền thu hộ COD từ các đơn phát thành công
- [ ] **[UC-WEB-38] Thu tiền nhân viên**: Bưu tá nộp tiền COD tiền mặt thu được trong ngày về bưu cục, lập bảng kê thu tiền
- [ ] **[UC-WEB-39] Xác nhận thu tiền**: Thủ quỹ bưu cục xác nhận đã nhận đủ tiền thực tế từ bưu tá dựa trên bảng kê

---

## Sprint 4 — Báo cáo Thống kê (29/09/2026 -> 10/10/2026)

### 1. BÁO CÁO VẬN HÀNH (DEV B - 10 Báo cáo)
> Chưa có report engine/API/UI. Cần chốt danh sách ưu tiên trước khi triển khai.

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
