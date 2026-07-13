---
description: "Mô tả tính năng VeloxShip theo từng cấu phần — viết cho người dùng cuối. Phạm vi: hệ thống lập đơn & xác nhận trạng thái cho nhóm nội bộ ~50 người."
---

# Mô Tả Tính Năng VeloxShip

**Sản phẩm**: VeloxShip — Quản lý & Xác nhận Trạng thái Đơn Vận chuyển
**Ngày cập nhật**: 2026-07-13
**Đối tượng đọc**: Người dùng cuối (người tạo đơn, tài xế, quản lý) và bộ phận kinh doanh.

> Chi phí từng cấu phần xem [`docs/bao-gia-chi-phi-cau-phan.md`](./bao-gia-chi-phi-cau-phan.md).
> **Trạng thái**: ✅ Đã có · 🚧 Đang phát triển · ⬜ Theo lộ trình.

---

## Tổng quan

VeloxShip là hệ thống **gọn nhẹ** cho đội ngũ nội bộ (**~50 người dùng**). Bài toán cốt lõi: **lập đơn vận chuyển và để mỗi vai trò xác nhận trạng thái phần việc của mình** — người tạo đơn lập phiếu, tài xế xác nhận lấy/giao hàng, quản lý theo dõi tổng thể. Hệ thống tổng hợp thành bức tranh vận hành theo thời gian thực.

Toàn bộ giao diện và phiếu in **bằng tiếng Việt có dấu**; tra cứu **không phân biệt dấu** (gõ không dấu vẫn tìm ra).

---

## Gói lõi

### 1. Quản lý vận đơn & xác nhận trạng thái ⭐

**Bài toán**: chuẩn hóa việc lập đơn và theo dõi tiến độ từng đơn qua các vai trò.

- **Lập vận đơn** ✅ — Người tạo nhập thông tin gửi/nhận, hàng hóa, dịch vụ, cước phí; hệ thống sinh mã vận đơn, mã vạch, mã QR và **in phiếu gửi** đúng mẫu.
- **Xác nhận trạng thái theo vai trò** 🚧 — Mỗi người cập nhật đúng phần việc: *đã lấy hàng → đang giao → đã giao / hoàn / hủy*. Hệ thống ghi lại **ai đổi trạng thái, lúc nào**.
- **Danh sách & tra cứu** ✅ — Tìm nhanh đơn theo mã, tên, số điện thoại, ngày; xem chi tiết và **in lại** khi cần.

**Lợi ích**: ai cũng biết đơn đang ở bước nào; quản lý nhìn thấy toàn bộ vận hành mà không cần hỏi thủ công.

### 2. Người dùng & phân quyền 🚧

**Bài toán**: kiểm soát "ai được làm gì" cho nhóm ~50 người.

- Đăng nhập bảo mật; vài vai trò cơ bản (người tạo, tài xế, quản lý).
- Mỗi vai trò chỉ thấy đúng phần việc của mình; mọi thao tác truy vết được về đúng người.

**Lợi ích**: an toàn dữ liệu, rõ ràng trách nhiệm.

### 3. Quản lý khách hàng 🚧

**Bài toán**: phục vụ nhanh khách gửi thường xuyên.

- Lưu hồ sơ khách; khi lập đơn chỉ cần chọn khách để **tự điền** thông tin người gửi.
- Thông tin được **chụp lại (snapshot)** vào đơn nên sửa hồ sơ sau này không làm thay đổi đơn cũ.

**Lợi ích**: lập đơn nhanh hơn, ít sai sót nhập tay.

### 4. Danh mục cơ bản ✅ / 🚧

**Bài toán**: dữ liệu nền nhất quán cho toàn hệ thống.

- Danh mục dịch vụ ✅ (CPN, PHT, Đường bộ, 48H, Quốc tế…), loại hàng hóa 🚧, và địa điểm (dùng dữ liệu có sẵn — **không cần tích hợp API bên ngoài**).

**Lợi ích**: khai báo một lần, dùng lại mọi nơi, giảm nhầm lẫn.

### 5. Báo cáo cơ bản ⬜

**Bài toán**: theo dõi vận hành bằng số liệu.

- Vài báo cáo cốt lõi về sản lượng đơn và trạng thái đơn, **xuất Excel/PDF**.

**Lợi ích**: nắm tình hình nhanh, hỗ trợ ra quyết định.

---

## Giao diện xác nhận cho tài xế (Mobile Web) ⬜

**Bài toán**: tác nghiệp ngoài hiện trường.

- Tài xế mở trực tiếp trên **điện thoại qua trình duyệt** (không cần cài app) để cập nhật trạng thái lấy/giao và lưu **bằng chứng (ảnh/ký nhận)**.

**Lợi ích**: nhẹ, nhanh, dùng được ngay; cập nhật trạng thái tức thời về hệ thống.

---

## Đặc điểm xuyên suốt

- 🇻🇳 **Tiếng Việt 100%** — nhãn, nút, thông báo, phiếu in đều có dấu đầy đủ.
- 🔎 **Tra cứu không phân biệt dấu** — gõ "nguyen thi hoa" vẫn ra "Nguyễn Thị Hoa".
- 🧾 **In phiếu đúng mẫu** — logo, mã vạch, mã QR, chữ ký, footer của hãng.
- 🔐 **Bảo mật & phân quyền** — đăng nhập bắt buộc, mỗi vai trò thấy đúng phần việc.
- 📜 **Nhật ký** — ghi lại ai đổi trạng thái đơn, lúc nào.

---

## Tùy chọn mở rộng (lộ trình tương lai)

Khi quy mô lớn hơn, có thể bổ sung (mô tả & báo giá riêng): **app di động native**, **quản lý kho đầy đủ** (nhập/xuất/kiểm kê tồn), **điều phối chuyển xe & đội xe**, **quản lý đối tác & bảng giá mua**, **thu hộ COD & đối soát tài chính**, **bộ báo cáo nâng cao (tối đa 20 mẫu)**. Chi tiết danh mục lộ trình xem [`docs/roadmap-tasks.md`](./roadmap-tasks.md).

---

*Tài liệu mô tả tính năng phục vụ giới thiệu & đào tạo người dùng. Trạng thái tính năng đối chiếu với mã nguồn hiện tại.*
