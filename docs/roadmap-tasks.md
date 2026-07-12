---
description: "Roadmap implementation tasks for the Express Delivery Management Software (Bản Báo Giá)"
---

# Bảng Theo Dõi Nhiệm Vụ Lộ Trình — Roadmap Tasks

> **Chú thích trạng thái**: `[x]` = Hoàn thành · `[~]` = Đang làm/một phần · `[ ]` = Chưa bắt đầu.
> Yêu cầu nghiệp vụ chi tiết & trạng thái triển khai v1: xem [`docs/business-requirements.md`](./business-requirements.md).

## Tiến độ v1 — Quản lý Phiếu Gửi (feature `001-logistics-bill-app`)

Phạm vi v1 được thu hẹp vào khâu **lập & quản lý phiếu gửi** (ánh xạ vào mục **V. QUẢN LÝ VẬN ĐƠN** bên dưới). Trạng thái đối chiếu mã nguồn ngày 2026-07-12:

- ✅ **US1 — Tạo phiếu gửi** (tạo, sinh mã vận đơn/barcode/QR, in & xuất PDF) — *Hoàn thành (MVP)*.
- ✅ **Danh sách phiếu** (phân trang) + **In lại / Xuất PDF** — *Hoàn thành*.
- 🚧 **US2 còn lại** — tra cứu không phân biệt dấu + cập nhật trạng thái vòng đời — *Đang làm*.
- ⬜ **US3 — Hồ sơ khách hàng** (tự điền người gửi, snapshot) — *Chưa bắt đầu (mới có model + migration)*.
- ⬜ **Kiểm thử SC-004/005/006, CHECK cước, drift OpenAPI** — *Chưa bắt đầu*.

---

## I. HỆ THỐNG QUẢN LÝ

### 1. QUẢN LÝ NHÂN VIÊN
- [ ] Quản lý phòng ban
- [ ] Quản lý chức vụ
- [ ] Quản lý nhân viên

### 2. QUẢN LÝ CÀI ĐẶT
- [ ] Quản lý tỉnh thành
- [ ] Quản lý quận huyện
- [ ] Quản lý phường xã
- [ ] Quản lý Trung tâm/ Chi nhánh/ Bưu cục
- [ ] Quản lý khu vực/ tuyến giao nhận
- [ ] Quản lý đội xe
- [ ] Quản lý phân quyền
- [ ] Quản lý dịch vụ/ dịch vụ gia tăng
- [ ] Quản lý loại hàng hóa

### 3. QUẢN LÝ KHÁCH HÀNG
- [ ] Quản lý thông tin khách hàng
- [ ] Quản lý bảng giá
- [ ] Quản lý công nợ

### 4. QUẢN LÝ ĐỐI TÁC
- [ ] Quản lý thông tin đối tác
- [ ] Quản lý bảng giá mua

### 5. QUẢN LÝ VẬN ĐƠN
- [ ] Quản lý lấy hàng
- [x] Tạo vận đơn
- [ ] Tạo vận đơn excel
- [ ] Đóng gói
- [ ] Mở gói
- [x] Danh sách vận đơn
- [ ] Hủy giao hàng thành công
- [ ] Tiếp tục giao hàng
- [ ] Điều chỉnh COD
- [ ] Lịch sử điều chỉnh đơn hàng

### 6. QUẢN LÝ KHO
- [ ] Nhập kho
- [ ] Kiểm kê kho
- [ ] Xuất kho trung chuyển
- [ ] Xuất hàng đối tác
- [ ] Xuất kho giao hàng
- [ ] Xuất kho trả hàng
- [ ] Lịch sử xuất/nhập kho

### 7. QUẢN LÝ CHUYỂN XE
- [ ] Quản lý đội xe
- [ ] Quản lý chuyến xe

### QUẢN LÝ THU TIỀN (COD)
- [ ] Quản lý thu hộ
- [ ] Thu tiền nhân viên
- [ ] Xác nhận thu tiền

### 8. BÁO CÁO THỐNG KÊ
- [ ] Tối đa 20 báo cáo thống kê theo yêu cầu khách hàng

---

## II. APP NHÂN VIÊN

### 1. LẤY HÀNG
- [ ] Chờ xác nhận đi lấy hàng
- [ ] Đi lấy hàng
- [ ] Đã lấy hàng

### 2. GIAO HÀNG
- [ ] Xác nhận giao hàng
- [ ] Đi giao hàng
- [ ] Đã giao hàng
- [ ] Tiếp tục giao hàng

### 3. TRUNG CHUYỂN
- [ ] Chờ trung chuyển
- [ ] Đi trung chuyển

### 4. NỘP TIỀN
- [ ] Tạo bảng kê nộp tiền
- [ ] Danh sách bảng kê nộp tiền

### 5. KHO
- [ ] Nhập kho
- [ ] Xuất kho phát hàng
- [ ] Xuất kho giao hàng
