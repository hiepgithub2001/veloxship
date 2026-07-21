# Wireframe & Mockup Specification
**Dự án**: Hệ thống Quản lý Chuyển phát nhanh Hoàng Nam (Hoàng Nam Express) — Giai đoạn 1  
**Phiên bản**: 1.0  
**Ngày**: 2026-07-21  
**Tác giả**: BA Antigravity AI  
**Trạng thái**: Draft / In Review  

Tài liệu này đặc tả cấu trúc giao diện (User Interface Layout), Kiến trúc thông tin (Information Architecture) và phác thảo Wireframe cho toàn bộ các màn hình nghiệp vụ của Hệ thống Web Quản lý Hoàng Nam Express - Giai đoạn 1, tích hợp toàn bộ **40 Use Case** trong tệp CSV gốc.

---

## 1. Kiến trúc thông tin & Bố cục chung (App Shell Layout)

Hệ thống được thiết kế theo dạng **Web Desktop Portal** với bố cục 3 phần tiêu chuẩn:
*   **Sidebar (Thanh menu bên trái)**: Rộng 240px, cố định. Chứa logo bưu chính Hoàng Nam, thông tin bưu cục hiện tại và danh mục chức năng phân quyền.
*   **Header (Thanh đầu trang)**: Cao 64px, cố định. Hiển thị thông báo, ngôn ngữ (Tiếng Việt mặc định) và thông tin tài khoản nhân viên (Họ tên, Vai trò) kèm nút đăng xuất.
*   **Main Content (Vùng nội dung chính)**: Chiếm toàn bộ không gian còn lại, tự động responsive cho các khổ màn hình từ tablet đến desktop màn rộng.

### Sơ đồ Bố cục Khung (App Layout Grid)
```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ LOGO    │  Bưu cục: HCM-QUAN1 [Hộp thoại chọn]      [Chuông]  👤 Nguyễn Văn A│
│ HOANG   ├───────────────────────────────────────────────────────────────────┤
│ NAM     │                                                                   │
│         │  NỘI DUNG CHÍNH (MAIN AREA)                                       │
├─────────┤                                                                   │
│ [🏠]Trang│  [Tiêu đề trang]                                                  │
│  chủ    │                                                                   │
│ [📝]Tạo  │  ┌─────────────────────────────────────────────────────────────┐  │
│  đơn    │  │                                                             │  │
│ [📦]Kho  │  │   Vùng làm việc chức năng (Form/Bảng dữ liệu/Quét barcode)  │  │
│  quầy   │  │                                                             │  │
│ [🚚]Xe  │  └─────────────────────────────────────────────────────────────┘  │
│  chạy   │                                                                   │
│ [💵]COD  │                                                                   │
│  Quỹ    │                                                                   │
│ [📊]Báo  │                                                                   │
│  cáo    │                                                                   │
└─────────┴───────────────────────────────────────────────────────────────────┘
```

---

## 2. Thiết kế màn hình Tạo Vận Đơn Mới (UC-WAYBILL-01 / UC-WEB-19)

*   **Mục đích chính**: Cho phép nhân viên quầy tạo đơn gửi nhanh tại bưu cục, tính cước tự động và in phiếu gửi.
*   **CTA chính**: Nút "Tạo Đơn & In Phiếu" (màu xanh dương đậm, góc dưới cùng bên phải).
*   **CTA phụ**: "Tính cước thử", "Hủy bỏ".

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Quản lý vận đơn / Tạo vận đơn mới
================================================================================
[🏠] TẠO VẬN ĐƠN MỚI 

┌─ (1) THÔNG TIN NGƯỜI GỬI ────────────────────────┐┌─ (2) THÔNG TIN NGƯỜI NHẬN ────────────────────────┐
│ Số điện thoại: [ 0901234567               ] (🔍) ││ Số điện thoại: [ 0987654321               ]       │
│ Họ và tên:     [ Nguyễn Văn B                    ] ││ Họ và tên:     [ Trần Thị C                      ] │
│ Địa chỉ nhà:   [ 123 Đường Ba Tháng Hai, P.11    ] ││ Địa chỉ nhà:   [ 456 Lê Lợi, Phường Bến Nghé     ] │
│ Tỉnh/Thành:    [ Thành phố Hồ Chí Minh         [v] ]││ Tỉnh/Thành:    [ Thành phố Hồ Chí Minh         [v] ]│
│ Quận/Huyện:    [ Quận 10                       [v] ]││ Quận/Huyện:    [ Quận 1                        [v] ]│
│ Phường/Xã:     [ Phường 11                     [v] ]││ Phường/Xã:     [ Phường Bến Nghé               [v] ]│
└──────────────────────────────────────────────────┘└──────────────────────────────────────────────────┘

┌─ (3) THÔNG TIN HÀNG HÓA ──────────────────────────────────────────────────────────────────────────────┐
│ Loại hàng: (o) Hàng hóa  ( ) Tài liệu           Cân nặng thực tế: [ 1.50   ] kg                       │
│ Dài: [ 20.0 ] cm  x  Rộng: [ 15.0 ] cm  x  Cao: [ 10.0 ] cm   => Quy đổi: 0.50 kg (Dài*Rộng*Cao/6000) │
│ Giá trị khai báo (bảo hiểm): [ 2,000,000      ] VNĐ   Tiền thu hộ COD: [ 1,500,000      ] VNĐ         │
│ Nội dung bưu gửi: [ Quần áo thời trang                                                              ] │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─ (4) DỊCH VỤ & THANH TOÁN ────────────────────────┐┌─ (5) BẢNG CHI TIẾT CƯỚC TÍNH TOÁN ────────────────┐
│ Dịch vụ chính: [ Tiêu chuẩn                   [v] ]││ Cước chính:                 25,000 VNĐ            │
│ Dịch vụ thêm:  [x] Bảo hiểm bưu gửi                ││ Phí bảo hiểm hàng hóa:      10,000 VNĐ            │
│                [ ] Giao tận tay                   ││ Phụ phí khác:                    0 VNĐ            │
│ Người trả ship:[ Người gửi (Shop ký nợ)       [v] ]││ Thuế VAT (10%):              3,500 VNĐ            │
│ Ghi chú phát:  [ Cho xem hàng, không cho thử  [v] ]││ Tổng cước thực thu:         38,500 VNĐ            │
└──────────────────────────────────────────────────┘└──────────────────────────────────────────────────┘
                                                       [ Hủy đơn ]   [ Tính cước thử ]   [ TẠO ĐƠN & IN PHIẾU ]
```

### Các ghi chú tương tác & Validation (Annotations)
*   **Ô nhập SĐT Người gửi**: Validate đúng định dạng E.164 Việt Nam. Khi nhấn `Tab` hoặc icon `(🔍)`, hệ thống thực hiện truy vấn tự động:
    *   Nếu khách hàng đã có thông tin: Autofill Họ tên, Địa chỉ, dropdown Tỉnh/Huyện/Xã và thiết lập bảng giá ký nợ.
    *   Nếu là SĐT mới: Hiện tooltip gợi ý "SĐT mới - Vui lòng điền thông tin".
*   **Địa giới hành chính**: Cấp dropdown Quận/Huyện sẽ bị khóa (disable) cho đến khi Tỉnh/Thành được chọn. Cấp Phường/Xã bị khóa cho đến khi chọn xong Quận/Huyện.
*   **Cân nặng & Quy đổi**: Khối lượng thực tế và Kích thước chỉ cho phép nhập số dương lớn hơn 0. Khi nhập kích thước, hệ thống tự hiển thị Cân nặng quy đổi. Khối lượng tính cước gửi sang API tính phí sẽ tự chọn giá trị lớn nhất.
*   **Duyệt In ấn**: Khi click CTA "TẠO ĐƠN & IN PHIẾU", nếu dữ liệu lưu DB thành công, hệ thống hiển thị dialog in đè lên màn hình chứa iframe Preview phiếu gửi A6 và tự động gọi câu lệnh in của trình duyệt (`window.print()`).

---

*   **Thiết kế màn hình Đóng Bao Trung Chuyển (Trì hoãn sang Giai đoạn 2)**: Nghiệp vụ này đã được dời xuống phần Giai đoạn 2 (Deferred Wireframes) ở cuối tài liệu này.

---

## 4. Thiết kế màn hình Duyệt Bảng Kê Thu Tiền COD (UC-COD-03 / UC-WEB-39)

*   **Mục đích chính**: Thủ quỹ bưu cục đối soát và phê duyệt bảng kê nộp tiền mặt COD của bưu tá cuối ca.
*   **CTA chính**: "Xác nhận & Duyệt bảng kê" (màu xanh lá cây đậm).
*   **CTA phụ**: "Từ chối duyệt (Lệch tiền mặt)".

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Quản lý COD / Duyệt bảng kê COD bưu tá nộp về
================================================================================
[💵] DUYỆT BẢNG KÊ NỘP TIỀN COD

┌─ (1) THÔNG TIN BẢNG KÊ NỘP TIỀN ──────────────────────────────────────────────────────────────────────┐
│ Mã bảng kê: COD-210726-004             Bưu tá nộp: Nguyễn Văn D (Mã: NV340)                           │
│ Bưu cục thu: Bưu cục HCM-Q10           Thời gian bưu tá lập: 21/07/2026 17:00                         │
│ Số lượng đơn hàng trong bảng kê: 3 đơn Trạng thái: [ CHỜ THỦ QUỸ DUYỆT ]                              │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─ (2) DANH SÁCH ĐƠN HÀNG COD ĐÃ PHÁT THÀNH CÔNG TRONG BẢNG KÊ ─────────────────────────────────────────┐
│ ┌───────┬─────────────────┬───────────────────┬──────────────────────┬─────────────┬──────────────┐ │
│ │ STT   │ Mã Vận Đơn      │ Thời gian phát    │ Người nhận ký        │ COD khai báo│ Trạng thái   │ │
│ ├───────┼─────────────────┼───────────────────┼──────────────────────┼─────────────┼──────────────┤ │
│ │ 1     │ HN002231902VN   │ 21/07/2026 14:15  │ Trần Thị C           │ 1,500,000   │ Giao thành công│
│ │ 2     │ HN002231908VN   │ 21/07/2026 15:30  │ Phạm Văn E           │ 500,000     │ Giao thành công│
│ │ 3     │ HN002231911VN   │ 21/07/2026 16:10  │ Lê Văn F             │ 0           │ Giao thành công│
│ └───────┴─────────────────┴───────────────────┴──────────────────────┴─────────────┴──────────────┘ │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─ (3) ĐỐI SOÁT KIỂM ĐẾM TIỀN MẶT THỰC TẾ ──────────────────────────────────────────────────────────────┐
│ Tổng tiền COD khai báo nộp:    [ 2,000,000   ] VNĐ                                                    │
│ Số tiền mặt thủ quỹ nhận được: [ 2,000,000   ] VNĐ  <== Nhập số tiền mặt thực đếm                     │
│ Chênh lệch lệch tiền:          [ 0           ] VNĐ  (Bằng: Không chênh lệch)                          │
├───────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [!] Ghi chú đối soát (Lý do từ chối nếu lệch tiền):                                                   │
│ [ Nhập lý do nếu tiền mặt bàn giao thực tế không khớp với bảng kê trên hệ thống                     ] │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                         [ TỪ CHỐI DUYỆT (LỆCH TIỀN) ]  [ XÁC NHẬN & DUYỆT BẢNG KÊ COD ]
```

### Các ghi chú tương tác & Validation (Annotations)
*   **Số tiền mặt thủ quỹ nhận được**: Ô input chỉ cho phép nhập ký tự số, tự động hiển thị định dạng phân cách hàng nghìn (ví dụ nhập 2000000 hiển thị `2,000,000`).
*   **Chênh lệch lệch tiền**: calculated field hiển thị thời gian thực khi thủ quỹ gõ số tiền thực thu. Công thức: `Chênh lệch = Thực nhận - Khai báo`.
    *   *Nếu Chênh lệch = 0*: Chữ hiển thị màu xanh lá cây ("Bằng: Không chênh lệch"). Nút "Xác nhận & Duyệt bảng kê COD" được kích hoạt (enabled). Nút "Từ chối duyệt" bị mờ (disabled).
    *   *Nếu Chênh lệch ≠ 0 (Thừa hoặc Thiếu tiền)*: Chữ hiển thị màu đỏ báo động (Ví dụ: "Thiếu 200,000 VNĐ"). Nút "Xác nhận & Duyệt bảng kê COD" bị khóa (disabled), đồng thời bắt buộc thủ quỹ phải nhập vào ô "Ghi chú đối soát" để kích hoạt nút "Từ chối duyệt (Lệch tiền)".
*   **Khi duyệt thành công**: Hệ thống hiện Toast thông báo thành công "Đã duyệt bảng kê COD-210726-004. Đã ghi nhận +2,000,000 VNĐ vào sổ quỹ bưu cục". Chuyển hướng màn hình về danh sách duyệt bảng kê.

---

## 5. Danh sách & Chi tiết Nhân viên (UC-WEB-01 / UC-WEB-02 / UC-WEB-03)

*   **Mục đích chính**: Quản lý thông tin hồ sơ nhân sự, phân cấp phòng ban, gán chức vụ và cấu hình nhóm quyền.
*   **CTA chính**: "Thêm nhân viên mới".

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Quản lý nhân viên
================================================================================
[👤] QUẢN LÝ NHÂN VIÊN                                       [+ THÊM NHÂN VIÊN MỚI ]

Bộ lọc: SĐT/Họ tên: [ Nhập tìm kiếm... ]  Phòng ban: [ Tất cả [v] ] Chức vụ: [ Tất cả [v] ]
┌──────────────────────────────────────────────────────────────────────────────┐
│ Mã NV  │ Họ và tên     │ Số điện thoại │ Phòng ban   │ Chức vụ   │ Trạng thái│ Thao tác     │
├────────┼───────────────┼───────────────┼─────────────┼───────────┼───────────┼──────────────┤
│ NV001  │ Nguyễn Văn A  │ 0901234567    │ Vận hành    │ Thủ kho   │ [ Hoạt động ] [ Sửa ] [Khóa] │
│ NV002  │ Trần Thị B    │ 0912234567    │ Kế toán     │ Thủ quỹ   │ [ Hoạt động ] [ Sửa ] [Khóa] │
│ NV003  │ Lê Văn C      │ 0934234567    │ Vận hành    │ Bưu tá    │ [ Bị khóa  ] [ Sửa ] [Mở ] │
└──────────────────────────────────────────────────────────────────────────────┘

* Popup: Thêm/Sửa nhân viên
┌──────────────────────────────────────────────────────────────────────────────┐
│ Họ tên: [ Nguyễn Văn A       ]   Số điện thoại (đăng nhập): [ 0901234567     ] │
│ Email:  [ a.nguyen@hn.com    ]   Bưu cục làm việc:  [ Bưu cục HCM-Q10    [v] ] │
│ Phòng ban: [ Vận hành   [v] ]   Chức vụ: [ Thủ kho  [v] ]  Nhóm quyền: [ Kho [v] ] │
│                                                          [ Hủy ] [ Lưu tài khoản ] │
└──────────────────────────────────────────────────────────────────────────────┘
```
*   *Ghi chú tương tác*: Khi thêm nhân viên mới, mật khẩu ngẫu nhiên sẽ tự sinh và bắn qua SMS Gateway của SĐT đã nhập. Trạng thái "Bị khóa" sẽ lập tức thu hồi token phiên làm việc hiện tại của nhân sự đó.

---

## 6. Cấu hình Địa giới Hành chính tĩnh (UC-WEB-04 / UC-WEB-05 / UC-WEB-06)

*   **Mục đích chính**: Quản lý danh mục Tỉnh thành, Quận huyện, Phường xã tĩnh.
*   **Bố cục**: Cấu trúc 3 cột dọc (Tỉnh/Thành -> Quận/Huyện -> Phường/Xã) liên kết đồng bộ.

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Cài đặt / Danh mục địa giới
================================================================================
[🗺️] DANH MỤC ĐỊA GIỚI HÀNH CHÍNH TĨNH VIỆT NAM

Cột 1: Tỉnh / Thành Phố         Cột 2: Quận / Huyện (của Tỉnh đã chọn) Cột 3: Phường / Xã (của Huyện)
┌────────────────────────────┐ ┌────────────────────────────┐ ┌────────────────────────────┐
│ Tìm kiếm Tỉnh...     (🔍)  │ │ Tìm kiếm Quận...     (🔍)  │ │ Tìm kiếm Xã...       (🔍)  │
├────────────────────────────┤ ├────────────────────────────┤ ├────────────────────────────┤
│ [*] TP. Hồ Chí Minh    [S] │ │ [*] Quận 1             [S] │ │ [*] Phường Bến Nghé    [S] │
│ [ ] Hà Nội             [S] │ │ [ ] Quận 3             [S] │ │ [ ] Phường Đa Kao      [S] │
│ [ ] Đà Nẵng            [S] │ │ [ ] Quận 10            [S] │ │ [ ] Phường Tân Định    [S] │
├────────────────────────────┤ ├────────────────────────────┤ ├────────────────────────────┤
│ [ + Thêm Tỉnh/Thành ]      │ │ [ + Thêm Quận/Huyện ]      │ │ [ + Thêm Phường/Xã ]       │
└────────────────────────────┘ └────────────────────────────┘ └────────────────────────────┘
```
*   *Ghi chú tương tác*: Nút `[S]` mở modal sửa tên hoặc xóa đơn vị hành chính. Tác vụ xóa kiểm tra khóa ngoại (nếu có đơn hàng nào đang liên kết địa giới này -> Báo lỗi không cho phép xóa).

---

## 7. Quản lý Bưu cục & Tuyến phục vụ (UC-WEB-07 / UC-WEB-08)

*   **Mục đích chính**: Định nghĩa bưu cục và tick chọn các phường/xã bưu cục chịu trách nhiệm lấy phát hàng.

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Cài đặt / Cấu hình bưu cục
================================================================================
[🏢] QUẢN LÝ BƯU CỤC & TUYẾN PHỤC VỤ                         [+ THÊM BƯU CỤC MỚI ]

┌──────────────────────────────────────────────────────────────────────────────┐
│ Mã BC    │ Tên bưu cục         │ Điện thoại    │ Địa chỉ bưu cục    │ Tuyến quản lý  │ Thao tác     │
├──────────┼─────────────────────┼───────────────┼────────────────────┼────────────────┼──────────────┤
│ BCHCM01  │ Bưu cục HCM - Q10   │ 0281234567    │ 12 Ba Tháng Hai,Q10│ 15 Phường/Xã   │ [Cấu hình]   │
│ BCHCM02  │ Bưu cục HCM - Q1    │ 0287654321    │ 45 Lê Lợi, Quận 1  │ 10 Phường/Xã   │ [Cấu hình]   │
└──────────────────────────────────────────────────────────────────────────────┘

* Drawer: Thiết lập Phân Tuyến Bưu Cục (Mở ra khi bấm [Cấu hình])
┌──────────────────────────────────────────────────────────────────────────────┐
│ Thiết lập tuyến cho: Bưu cục HCM - Q1                                       │
│ Chọn địa bàn quản lý lấy/giao hàng:                                          │
│ [v] Thành phố Hồ Chí Minh                                                    │
│    [v] Quận 1                                                                │
│       [x] Phường Bến Nghé (Đang gán: Bưu cục HCM-Q1)                         │
│       [x] Phường Đa Kao   (Đang gán: Bưu cục HCM-Q1)                         │
│       [ ] Phường Tân Định (Đang gán: Bưu cục HCM-Q3)  <-- Check để chuyển bưu cục│
│                                                                [ Hủy ] [ Lưu ]│
└──────────────────────────────────────────────────────────────────────────────┘
```
*   *Ghi chú tương tác*: Khi tích chọn một Phường/Xã đã thuộc bưu cục khác quản lý, hiển thị cảnh báo: "Phường X sẽ được chuyển từ Bưu cục A sang Bưu cục B. Xác nhận?".

---

## 8. Quản lý phân quyền tài khoản (UC-WEB-10)

*   **Mục đích chính**: Định nghĩa vai trò nhóm quyền và check-box gán quyền cụ thể cho từng nhóm.

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Cài đặt / Nhóm quyền hệ thống
================================================================================
[🔐] QUẢN LÝ PHÂN QUYỀN                                       [+ TẠO NHÓM QUYỀN MỚI ]

Cột trái: Danh sách Nhóm Quyền      Cột phải: Quyền hạn chi tiết nhóm [Thủ kho]
┌────────────────────────────┐ ┌──────────────────────────────────────────────────────┐
│ - Admin hệ thống           │ │ [v] Phân hệ Vận đơn:                                 │
│ - Thủ quỹ bưu cục          │ │     [ ] bill:create [v] bill:view [ ] bill:rollback  │
│ - [*] Thủ kho bưu cục      │ │ [v] Phân hệ Kho hàng:                                │
│ - Bưu tá giao nhận         │ │     [v] warehouse:inbound [v] warehouse:bagging      │
│                            │ │     [v] warehouse:outbound [v] warehouse:audit       │
└────────────────────────────┘ └────────────────────────────────────────── [ Lưu ] ──┘
```

---

## 9. Quản lý Đội xe & Khai báo xe (UC-WEB-09 / UC-WEB-35)

*   **Mục đích chính**: Theo dõi biển số xe, loại xe tải/xe máy và gán tài xế.

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Đội xe / Danh sách xe
================================================================================
[🚚] QUẢN LÝ ĐỘI XE                                                [+ ĐĂNG KÝ XE MỚI ]

┌──────────────────────────────────────────────────────────────────────────────┐
│ Biển số xe │ Loại xe │ Tải trọng │ Thể tích │ Tài xế phụ trách │ Trạng thái     │ Thao tác     │
├────────────┼─────────┼───────────┼──────────┼──────────────────┼────────────────┼──────────────┤
│ 29C-123.45 │ Xe tải  │ 5.5 tấn   │ 22 m³    │ Nguyễn Văn A     │ [ Đang đi tour ] [ Sửa ] [Xóa] │
│ 59A-999.99 │ Xe máy  │ 0.1 tấn   │ 0.5 m³   │ Trần Văn B       │ [ Sẵn sàng   ] [ Sửa ] [Xóa] │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Cấu hình Dịch vụ & Phân loại hàng hóa (UC-WEB-11 / UC-WEB-12)

*   **Mục đích chính**: Quản lý các loại dịch vụ vận chuyển chính, gia tăng và hệ số quy đổi thể tích hàng cồng kềnh.

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Cài đặt / Dịch vụ & Hàng hóa
================================================================================
[📦] DỊCH VỤ & LOẠI HÀNG HÓA

[ Tab: Dịch vụ vận chuyển ]    [ Tab: Quy đổi cồng kềnh & Loại hàng hóa ]

┌─ Cấu hình quy đổi thể tích hàng cồng kềnh ────────────────────────────────────┐
│ Công thức quy đổi chuẩn: Khối lượng quy đổi = (Dài x Rộng x Cao) (cm) / [ 6000 ]│
│ Phụ thu hàng chất lỏng nguy hiểm: [ 15 ] % cước chính                         │
└─────────────────────────────────────────────────────────────────── [ Cập nhật ]┘
```

---

## 11. Hồ sơ Khách hàng & Phân nhóm (UC-WEB-13)

*   **Mục đích chính**: CRUD thông tin danh mục shop gửi, gán bảng giá cước ưu đãi.

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Khách hàng / Danh sách khách gửi
================================================================================
[👥] DANH SÁCH KHÁCH HÀNG                                     [+ THÊM KHÁCH HÀNG MỚI ]

┌──────────────────────────────────────────────────────────────────────────────┐
│ Mã KH    │ Tên shop / Khách hàng │ Số điện thoại │ Nhóm khách   │ Bảng giá áp dụng │ Thao tác     │
├──────────┼───────────────────────┼───────────────┼──────────────┼──────────────────┼──────────────┤
│ KH0089   │ Shop Mẹ & Bé Lâm Đồng │ 0905555666    │ Shop lớn     │ Bảng giá VIP 1   │ [ Sửa ] [Xóa]│
│ KH0090   │ Khách vãng lai        │ 0911222333    │ Khách lẻ     │ Giá niêm yết mặc định [ Sửa ] [Xóa]│
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 12. Thiết lập Bảng giá cước Khách hàng (UC-WEB-14)

*   **Mục đích chính**: Thiết lập chi phí cước nền và cước lũy tiến theo từng shop hoặc nhóm khách hàng.

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Khách hàng / Cấu hình bảng giá cước
================================================================================
[💵] CHI TIẾT BẢNG GIÁ: BẢNG GIÁ VIP 1 (Áp dụng: Khách hàng lớn)     [ + THÊM DÒNG GIÁ ]

Gói dịch vụ: [ Tiêu chuẩn [v] ]
┌──────────────────────────────────────────────────────────────────────────────┐
│ Tuyến cước    │ Mốc trọng lượng tối đa │ Cước nền (VND) │ Cước bước tiếp (trên 0.5kg)│
├───────────────┼────────────────────────┼────────────────┼────────────────────────────┤
│ Nội tỉnh      │ 1.000 kg               │ 15,000         │ + 2,500                    │
│ Nội vùng      │ 1.000 kg               │ 22,000         │ + 4,000                    │
│ Liên vùng     │ 1.000 kg               │ 35,000         │ + 7,000                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 13. Đối soát Công nợ gửi Khách hàng (UC-WEB-15)

*   **Mục đích chính**: Gom đơn hàng giao thành công để đối chiếu tiền COD, cước phí và thanh toán cho khách hàng gửi định kỳ.

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Kế toán / Đối soát công nợ gửi shop
================================================================================
[💵] ĐỐI SOÁT CÔNG NỢ KHÁCH HÀNG

Khách hàng: [ Shop Mẹ & Bé Lâm Đồng [v] ]   Kỳ đối soát: [ 15/07/2026 ] đến [ 21/07/2026 ]
┌──────────────────────────────────────────────────────────────────────────────┐
│ Mã Vận Đơn │ Ngày giao  │ COD thu hộ (VND) │ Cước phí (VND) │ Số tiền thanh toán (Shop nhận) │
├────────────┼────────────┼──────────────────┼────────────────┼────────────────────────────────┤
│ HN0088921  │ 18/07/2026 │ 1,500,000        │ 35,000         │ 1,465,000                      │
│ HN0088925  │ 20/07/2026 │ 500,000          │ 22,000         │ 478,000                        │
├────────────┴────────────┼──────────────────┼────────────────┼────────────────────────────────┤
│ TỔNG KỲ ĐỐI SOÁT        │ 2,000,000        │ 57,000         │ 1,943,000                      │
└─────────────────────────┴──────────────────┴────────────────┴────────────────────────────────┘
[ Xuất file Excel đối soát ]                            [ XÁC NHẬN THANH TOÁN (CHI TIỀN CHO SHOP) ]
```

---

## 14. Kết nối đối tác 3PL & Giá mua (UC-WEB-16 / UC-WEB-17)

*   **Mục đích chính**: Quản lý thông tin kết nối và bảng giá mua cước của đối tác 3PL ngoài.

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Đối tác / Cấu hình kết nối 3PL
================================================================================
[🚚] QUẢN LÝ ĐỐI TÁC 3PL VÀ GIÁ MUA

[*] Giao Hàng Nhanh (GHN)    [ ] Giao Hàng Tiết Kiệm (GHTK)     [ ] Viettel Post
┌─ Cấu hình kết nối API đối tác ────────────────────────────────────────────────┐
│ API URL:     [ https://online-gateway.ghn.vn/shiip/public-api/v2/     ]       │
│ API Token:   [ token_auth_ghn_example_xxx                             ] (👁)   │
├─ Cấu hình bảng cước mua của đối tác (Làm căn cứ so khớp hóa đơn đầu vào) ────┤
│ Tuyến liên tỉnh: cước nền (đến 2kg): [ 28,000 ] VNĐ.  Mỗi kg tiếp theo: [ 5,000 ] VNĐ │
└─────────────────────────────────────────────────────────────────── [ Cập nhật ]┘
```

---

## 15. Quản lý Vận đơn & Tra cứu hành trình (UC-WEB-23 / UC-WEB-24 / UC-WEB-26 / UC-WEB-27)

*   **Mục đích chính**: Tìm kiếm đơn, rollback trạng thái giao thành công khi có khiếu nại, sửa COD, xem lịch sử thay đổi đơn hàng (Audit Log).

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Quản lý vận đơn / Tra cứu đơn hàng
================================================================================
[📝] CHI TIẾT VẬN ĐƠN: HN002231902VN 

Trạng thái hiện tại: [ Giao hàng thành công ]        Người nhận ký: Trần Thị C (21/07/2026 14:15)
Hành trình đơn hàng:
  - 21/07/2026 14:15: [Giao thành công] phát bởi bưu tá Nguyễn Văn D.
  - 21/07/2026 08:30: [Đang giao hàng] xuất kho phát hàng bưu cục HCM-Q10.
  - 20/07/2026 16:00: [Nhập kho bưu cục] quét nhận bởi thủ kho bưu cục HCM-Q10.
--------------------------------------------------------------------------------
Nhật ký thay đổi thông tin đơn (Audit Log):
┌───────────────────┬──────────────┬──────────────────┬──────────────┬──────────┐
│ Thời gian thay đổi│ Người thay đổi│ Trường thay đổi  │ Giá trị cũ   │ Giá trị mới│
├───────────────────┼──────────────┼──────────────────┼──────────────┼──────────┤
│ 20/07/2026 17:15  │ Kế toán quầy │ Số tiền COD      │ 2,000,000đ   │ 1,500,000đ│
└───────────────────┴──────────────┴──────────────────┴──────────────┴──────────┘
Thao tác quản trị:  [ SỬA TIỀN COD ]   [ HỦY TRẠNG THÁI GIAO THÀNH CÔNG (ROLLBACK) ]
```

---

## 16. Nghiệp vụ Quét Kho bưu cục (UC-WEB-28 / UC-WEB-29 / UC-WEB-31 / UC-WEB-32 / UC-WEB-33 / UC-WEB-34)

*   **Mục đích chính**: Cho phép thủ kho quét barcode đơn nhập kho bưu tá lấy về, xuất 3PL, xuất giao bưu tá và quét kiểm kê.

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Quản lý kho / Nghiệp vụ quét kho
================================================================================
[📦] QUÉT NHẬP / XUẤT KHO BƯU CỤC

[ Tab: Nhập kho (UC-28) ] [* Tab: Xuất giao bưu tá (UC-32) ] [ Tab: Xuất 3PL (UC-31) ] [ Tab: Kiểm kho (UC-29) ]

Chọn bưu tá phát hàng: [ Nguyễn Văn D (Mã bưu tá: NV340)                     [v] ]
Quét mã vận đơn giao đi: [ HN002231902VN                        ] [ BÀN GIAO (Enter) ]
┌──────────────────────────────────────────────────────────────────────────────┐
│ STT   │ Mã Vận Đơn      │ Khối lượng (kg) │ Người nhận           │ COD (VNĐ) │
├───────┼─────────────────┼─────────────────┼──────────────────────┼───────────┤
│ 1     │ HN002231902VN   │ 1.50            │ Trần Thị C           │ 1,500,000 │
│ 2     │ HN002231908VN   │ 2.20            │ Phạm Văn E           │ 500,000   │
└───────┴─────────────────┴─────────────────┴──────────────────────┴───────────┘
                                                [ HỦY ] [ XUẤT PHÁT HÀNG & IN BẢNG KÊ ]
```

---

## 17. Quản lý Chuyển xe trung chuyển (UC-WEB-35 / UC-WEB-36)

*   **Mục đích chính**: Tạo chuyến xe tải, gán tài xế, bốc xếp trực tiếp các vận đơn lẻ lên xe trung chuyển (không qua bao trung chuyển ở Giai đoạn 1).

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Quản lý chuyển xe / Tạo chuyến xe mới
================================================================================
[🚚] ĐIỀU PHỐI CHUYẾN XE TRUNG CHUYỂN

Tên chuyến: [ Chuyến trung chuyển HCM-Đà Lạt ngày 21/07 ]
Xe tải gán: [ 29C-123.45 (Tải trọng 5.5 tấn) [v] ]  Tài xế: [ Nguyễn Văn A (Mã: TX08) [v] ]
Bưu cục đích: [ Kho trung chuyển Lâm Đồng - Chi nhánh Đà Lạt [v] ]
Quét vận đơn bốc lên xe: [ HN2107260012VN                     ] [ XẾP LÊN XE (Enter) ]
┌──────────────────────────────────────────────────────────────────────────────┐
│ STT   │ Mã Vận Đơn      │ Người nhận      │ Địa chỉ nhận         │ Trọng lượng  │
├───────┼─────────────────┼─────────────────┼──────────────────────┼──────────────┤
│ 1     │ HN2107260012VN  │ Nguyễn Văn B    │ P. Lộc Phát, Đà Lạt  │ 1.50 kg      │
│ 2     │ HN2107260088VN  │ Trần Thị C      │ P. 2, Đà Lạt         │ 2.20 kg      │
└───────┴─────────────────┴─────────────────┴──────────────────────┴──────────────┤
Tổng số vận đơn: 2 đơn                                 Tổng trọng lượng: 3.70 kg
                                                   [ HỦY ] [ XUẤT BẾN CHUYẾN XE ]
```

---

## 18. Báo cáo thống kê (UC-WEB-40)

*   **Mục đích chính**: Kết xuất báo cáo phục vụ quản lý (doanh thu, sản lượng, công nợ, shipper).

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Báo cáo thống kê
================================================================================
[📊] BÁO CÁO THỐNG KÊ DOANH THU & SẢN LƯỢNG

Chỉ số tổng quan hôm nay (21/07/2026):
┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│ Tổng sản lượng đơn      │ │ Tổng cước phí thực thu  │ │ Tổng dòng tiền COD      │
│  [ 1,520 đơn ]          │ │  [ 38,500,000 VNĐ ]     │ │  [ 1,450,000,000 VNĐ ]  │
└─────────────────────────┘ └─────────────────────────┘ └─────────────────────────┘

Chọn loại biểu mẫu báo cáo kết xuất (Hỗ trợ tối đa 20 biểu mẫu):
Chọn báo cáo: [ Báo cáo Hiệu suất Shipper theo tỉ lệ giao thành công         [v] ]
Từ ngày: [ 15/07/2026 ]  Đến ngày: [ 21/07/2026 ]  Bưu cục: [ Tất cả bưu cục [v] ]
                                            [ XUẤT FILE BÁO CÁO (EXCEL) ] [ IN PDF ]
```

---
---

# GIAI ĐOẠN 2 (DEFERRED WIREFRAMES)

## 3. Thiết kế màn hình Đóng Bao Trung Chuyển (UC-WAREHOUSE-03 / UC-WEB-30)

*   **Mục đích chính**: Nhân viên kho thực hiện quét gộp nhiều đơn lẻ vào một bao hàng manifest lớn để gửi đi liên tỉnh/kho tổng.
*   **CTA chính**: "Đóng & Niêm Phong Bao Hàng" (Góc dưới bên phải).
*   **CTA phụ**: "Tạo bao mới", "Hủy bao hiện tại".

### Phác thảo Wireframe (Lo-fi ASCII)
```text
Trang chủ / Quản lý kho / Đóng bao trung chuyển
================================================================================
[📦] ĐÓNG BAO TRUNG CHUYỂN BƯU CHÍNH

┌─ (1) THÔNG TIN KHỞI TẠO BAO HÀNG ─────────────────────────────────────────────────────────────────────┐
│ Mã bao hàng: [ BAG2107260012            ] (Auto-gen)    Bưu cục đóng: Kho trung chuyển HCM-Q10        │
│ Bưu cục đích đến: [ Kho trung chuyển Lâm Đồng - Chi nhánh Đà Lạt                                  [v] ]│
│ Trạng thái bao:   [ ĐANG ĐÓNG BAO             ]         Thời gian mở: 21/07/2026 17:45                │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─ (2) QUÉT MÃ VẠCH ĐƠN LẺ VÀO BA ──────────────────────────────────────────────────────────────────────┐
│ Nhập/Quét mã đơn lẻ: [ NL0011310                            ]  [ ĐƯA VÀO BAO (Enter) ]                  │
│ Cảnh báo âm thanh: (o) Loa âm báo thành công (Bíp)   ( ) Rung phản hồi                                │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─ (3) DANH SÁCH VẬN ĐƠN ĐÃ QUÉT TRONG BAO (Tổng số đơn: 3 đơn - Tổng cân nặng: 5.20 kg) ───────────────┐
│ ┌───────┬─────────────────┬───────────────────┬──────────────────────┬─────────────┬──────────────┐ │
│ │ STT   │ Mã Vận Đơn      │ Khối lượng (kg)   │ Phường/Xã nhận       │ COD (VNĐ)   │ Thao tác     │ │
│ ├───────┼─────────────────┼───────────────────┼──────────────────────┼─────────────┼──────────────┤ │
│ │ 1     │ HN002231902VN   │ 1.50              │ P. Bến Nghé, Quận 1  │ 1,500,000   │ [ Xóa khỏi ] │ │
│ │ 2     │ HN002231908VN   │ 2.20              │ P. Đa Kao, Quận 1    │ 500,000     │ [ Xóa khỏi ] │ │
│ │ 3     │ HN002231911VN   │ 1.50              │ P. Tân Định, Quận 1  │ 0           │ [ Xóa khỏi ] │ │
│ └───────┴─────────────────┴───────────────────┴──────────────────────┴─────────────┴──────────────┘ │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                       [ Hủy bao hàng ]  [ ĐÓNG & NIÊM PHONG BAO HÀNG ]
```

### Các ghi chú tương tác & Validation (Annotations)
*   **Bưu cục đích đến**: dropdown lọc bưu cục bắt buộc nhân viên phải chọn trước khi đặt con trỏ vào ô quét mã đơn lẻ. Nếu chưa chọn kho đích mà quét mã, ô nhập sẽ báo viền đỏ và hiển thị: "Vui lòng chọn bưu cục đích trước".
*   **Ô quét mã đơn lẻ**: Luôn tự động focus sau mỗi lượt quét thành công để nhân viên có thể dùng máy quét cầm tay quét liên tục mà không cần chạm chuột.
*   **Kiểm tra tính hợp lệ của đơn quét**: Khi quét 1 mã đơn, backend check DB qua API:
    *   *Hợp lệ*: Đơn chuyển vào lưới, phát tiếng bíp ngắn.
    *   *Không hợp lệ* (Đơn đang ở kho khác, đơn đã hủy, đơn đã giao thành công): Viền đỏ ô nhập, phát tiếng còi dài cảnh báo lỗi và hiển thị modal cảnh báo đè lên màn hình "Đơn hàng đang ở trạng thái không thể đóng bao". Nhân viên phải click "Bỏ qua" hoặc nhấn phím Space để tắt thông báo lỗi và tiếp tục quét đơn khác.
*   **Đóng & Niêm phong**: Khi bấm nút, hệ thống khóa cứng bao hàng, không cho phép xóa/thêm đơn lẻ và tự động trigger download tệp tin Manifest (Bảng kê chi tiết bao hàng) để thủ kho in dán lên bao.
```
