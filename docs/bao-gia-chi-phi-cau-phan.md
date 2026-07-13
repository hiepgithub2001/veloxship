---
description: "Báo giá phần mềm VeloxShip theo từng cấu phần — trình bày theo góc nhìn khách hàng. Phạm vi: hệ thống quản lý & xác nhận trạng thái đơn hàng cho nhóm nội bộ ~50 người."
---

# Báo Giá Phần Mềm VeloxShip

**Sản phẩm**: VeloxShip — Quản lý & Xác nhận Trạng thái Đơn Vận chuyển
**Ngày báo giá**: 2026-07-13
**Hiệu lực**: 30 ngày kể từ ngày báo giá
**Đơn vị tiền tệ**: VNĐ (chưa bao gồm VAT)

---

## 1. Phạm vi & bài toán giải quyết

VeloxShip là hệ thống **gọn nhẹ** phục vụ đội ngũ nội bộ (**quy mô ~50 người dùng**). Bài toán cốt lõi: **lập đơn vận chuyển và xác nhận trạng thái đơn theo từng vai trò** — người tạo đơn, tài xế lấy/giao hàng, quản lý theo dõi. Mỗi người chỉ cần cập nhật đúng trạng thái phần việc của mình; hệ thống tổng hợp thành bức tranh vận hành theo thời gian thực.

Đây **không phải** nền tảng logistics quy mô lớn kiểu bưu chính (nhiều kho, tồn kho phức tạp, tích hợp API tra cứu địa điểm bên ngoài). Nhờ vậy phạm vi tinh gọn, chi phí và thời gian triển khai thấp hơn đáng kể.

> Toàn bộ giao diện và phiếu in **bằng tiếng Việt có dấu**; tra cứu **không phân biệt dấu**.

---

## 2. Tổng quan gói giải pháp

| Gói | Nội dung | Chi phí (VNĐ) |
|---|---|---:|
| **Gói lõi** | Vận đơn + quy trình xác nhận trạng thái + người dùng + khách hàng + danh mục + báo cáo cơ bản | **94.000.000** |
| **Giao diện xác nhận cho tài xế (mobile web)** | Màn hình cập nhật trạng thái tối ưu cho điện thoại | **20.000.000** |
| **Nền tảng, triển khai & đào tạo** | Hạ tầng, bảo mật, cài đặt, đào tạo, nghiệm thu | **30.000.000** |
| | **TỔNG GÓI** | **144.000.000** |

---

## 3. Chi tiết cấu phần (gói lõi)

### 3.1 Quản lý vận đơn & xác nhận trạng thái ⭐ — **50.000.000 VNĐ**
Giải quyết bài toán trung tâm: chuẩn hóa việc lập đơn và để mỗi vai trò xác nhận trạng thái phần việc của mình (tạo đơn → lấy hàng → đang giao → đã giao / hoàn / hủy). Kèm lập & in phiếu, tra cứu, và nhật ký ai đổi trạng thái lúc nào.

### 3.2 Người dùng & phân quyền — **12.000.000 VNĐ**
Giải quyết bài toán "ai được làm gì" cho nhóm ~50 người với vài vai trò (người tạo, tài xế, quản lý). Đăng nhập bảo mật, mỗi vai trò chỉ thấy đúng phần việc của mình.

### 3.3 Quản lý khách hàng — **10.000.000 VNĐ**
Giải quyết bài toán phục vụ khách gửi thường xuyên: lưu hồ sơ để tự điền khi lập đơn, giảm nhập tay và sai sót.

### 3.4 Danh mục cơ bản — **10.000.000 VNĐ**
Giải quyết bài toán dữ liệu nền nhất quán: dịch vụ, loại hàng, địa điểm (dùng dữ liệu có sẵn, không cần tích hợp API bên ngoài).

### 3.5 Báo cáo cơ bản — **12.000.000 VNĐ**
Giải quyết bài toán theo dõi vận hành: vài báo cáo cốt lõi về sản lượng và trạng thái đơn, xuất Excel/PDF.

**Tạm tính gói lõi: 94.000.000 VNĐ**

---

## 4. Giao diện xác nhận cho tài xế (mobile web) — **20.000.000 VNĐ**
Giải quyết bài toán tác nghiệp ngoài hiện trường: tài xế mở trên điện thoại để cập nhật trạng thái lấy/giao và lưu bằng chứng (ảnh/ký), không cần cài app. Nhẹ, nhanh, chi phí thấp hơn nhiều so với app native.

## 5. Nền tảng, triển khai & đào tạo — **30.000.000 VNĐ**
Hạ tầng, bảo mật, thiết kế giao diện, cài đặt, kiểm thử, nghiệm thu và đào tạo người dùng. Quy mô ~50 người nên hạ tầng gọn nhẹ, chi phí vận hành thấp.

---

## 6. Tổng chi phí

| Khoản mục | Chi phí (VNĐ) |
|---|---:|
| Gói lõi | 94.000.000 |
| Giao diện xác nhận cho tài xế (mobile web) | 20.000.000 |
| Nền tảng, triển khai & đào tạo | 30.000.000 |
| **Tổng cộng (chưa VAT)** | **144.000.000** |
| VAT (10%) | 14.400.000 |
| **Tổng cộng (đã gồm VAT)** | **158.400.000** |

**Chi phí vận hành hàng năm (tùy chọn, báo giá riêng):**
- Hạ tầng máy chủ / năm: 12.000.000 – 24.000.000 VNĐ (quy mô ~50 người, gọn nhẹ).
- Bảo trì & hỗ trợ kỹ thuật / năm: 15–20% giá trị phần mềm.

---

## 7. Tùy chọn mở rộng (chưa bao gồm — báo giá riêng khi cần)

Nếu về sau quy mô lớn hơn, có thể bổ sung:
- App di động **native** (thay cho mobile web).
- Quản lý kho đầy đủ (nhập/xuất/kiểm kê tồn).
- Điều phối chuyển xe & đội xe.
- Quản lý đối tác & bảng giá mua.
- Thu hộ COD & đối soát tài chính đầy đủ.
- Bộ báo cáo nâng cao (tối đa 20 mẫu).

---

## 8. Điều khoản

- **Thanh toán (đề xuất)**: 30% tạm ứng — 40% theo tiến độ nghiệm thu — 30% khi bàn giao cuối.
- **Bảo hành**: 03 tháng miễn phí sửa lỗi sau nghiệm thu.
- **Chưa bao gồm**: bản quyền phần mềm bên thứ ba (nếu có), phí SMS/thông báo, cổng thanh toán.
- **Ghi chú**: Báo giá tham khảo; phạm vi và chi phí cuối cùng chốt sau khảo sát nghiệp vụ chi tiết.

---

*Xem mô tả tính năng chi tiết tại [`docs/tinh-nang-chi-tiet-cau-phan.md`](./tinh-nang-chi-tiet-cau-phan.md).*
