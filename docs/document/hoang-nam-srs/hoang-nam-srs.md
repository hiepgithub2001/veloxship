# Software Requirements Specification (SRS)
**Sản phẩm**: Hệ thống Quản lý Chuyển phát nhanh Hoàng Nam (Hoàng Nam Express) — Giai đoạn 1  
**Phiên bản SRS**: 1.0  
**Ngày**: 2026-07-22  
**Tác giả**: Tech Lead Antigravity AI  
**Trạng thái**: Approved / Ready for Development  

---

## 1. Giới thiệu (Introduction)

### 1.1 Mục đích
Tài liệu Đặc tả Yêu cầu Phần mềm (Software Requirements Specification - SRS) này quy định chi tiết các yêu cầu chức năng (Functional Requirements - FR), yêu cầu phi chức năng (Non-Functional Requirements - NFR), ràng buộc kiến trúc, giao diện hệ thống và mô hình dữ liệu cho **Hệ thống Quản lý Chuyển phát nhanh Hoàng Nam (Hoàng Nam Express) - Giai đoạn 1**.

Tài liệu phục vụ làm căn cứ chính thức cho:
- Đội ngũ Phát triển Phần mềm (Developers & Solution Architects) triển khai mã nguồn backend, frontend và cơ sở dữ liệu.
- Đội ngũ Kiểm thử (QA/QC Engineeers) lập kế hoạch kiểm thử (Test Plan) và kịch bản kiểm thử (Test Cases).
- Đội ngũ Vận hành & Quản lý Dự án (PO/BA) kiểm thử chấp nhận người dùng (UAT) và nghiệm thu sản phẩm.

### 1.2 Phạm vi sản phẩm
Sản phẩm là ứng dụng **Web Quản lý (Web Portal)** tập trung số hóa quy trình vận hành bưu chính chặng cuối (Last-mile Delivery) của Công ty Hoàng Nam. Nền tảng được phát triển trên kiến trúc Monorepo kế thừa từ VeloxShip.

**Trong phạm vi (In-Scope - Giai đoạn 1)**:
- Quản lý Nhân sự & Phân quyền truy cập chi tiết (RBAC).
- Cấu hình Hệ thống: Địa giới hành chính 3 cấp Việt Nam (Tỉnh/Huyện/Xã), Bưu cục/Chi nhánh và tuyến phụ trách, Đội xe, Dịch vụ & Loại hàng hóa.
- Quản lý Khách hàng, Bảng giá cước chi tiết (khách lẻ, shop VIP, doanh nghiệp) và Công nợ khách hàng gửi định kỳ.
- Quản lý Đối tác 3PL (kết nối API, giá cước mua dịch vụ 3PL).
- Quản lý Vận đơn: Tiếp nhận lấy hàng, Tạo vận đơn thủ công & in phiếu gửi A5/A6 barcode, Tra cứu danh sách vận đơn, Rollback trạng thái giao hàng thành công khi có khiếu nại, Điều chỉnh COD trước xuất kho, Audit Log lịch sử thay đổi.
- Nghiệp vụ Kho bưu cục: Quét mã vạch nhập kho (Inbound Scan), Kiểm điểm tồn kho thực tế, Quét xuất kho trung chuyển đơn lẻ (Bagging đóng bao trì hoãn sang Giai đoạn 2), Quét xuất hàng 3PL, Quét xuất kho bàn giao bưu tá đi phát (Last-mile Outbound), Quét xuất kho trả hàng hoàn, Nhật ký xuất nhập kho.
- Quản lý Chuyển xe: Tạo chuyến xe trung chuyển, gán tài xế, bốc xếp vận đơn lẻ lên xe tải, xuất bến và theo dõi trạng thái.
- Quản lý Dòng tiền thu hộ (COD): Bưu tá lập bảng kê nộp tiền cuối ngày, Thủ quỹ đối soát thực tế và xác nhận nhập quỹ két sắt bưu cục 3 bước.
- Báo cáo Thống kê: Cung cấp tối đa 20 biểu mẫu báo cáo động về doanh thu, sản lượng, công nợ và hiệu suất bưu tá.

**Ngoài phạm vi (Out-of-Scope - Giai đoạn 1)**:
- Mobile App Native/Hybrid (bưu tá thao tác trên Web Responsive).
- Định vị GPS thời gian thực xe tải/bưu tá trên bản đồ số.
- Đóng bao trung chuyển bưu chính (Bagging/Manifest) và bốc xếp bao tải lên xe (dời sang Giai đoạn 2).
- Tích hợp cổng thanh toán trực tuyến tự động (VNPay/MoMo).

### 1.3 Định nghĩa & Viết tắt
| Thuật ngữ / Viết tắt | Định nghĩa đầy đủ |
|---|---|
| BRD | Business Requirements Document (Tài liệu Yêu cầu Nghiệp vụ) |
| SRS | Software Requirements Specification (Tài liệu Đặc tả Yêu cầu Phần mềm) |
| FR | Functional Requirement (Yêu cầu Chức năng) |
| NFR | Non-Functional Requirement (Yêu cầu Phi Chức năng) |
| COD | Cash On Delivery (Tiền thu hộ khi giao hàng) |
| 3PL | Third-Party Logistics (Đối tác vận chuyển thứ ba như GHN, GHTK, Viettel Post) |
| Hub | Bưu cục / Chi nhánh / Kho trung chuyển |
| Waybill / Bill | Vận đơn / Phiếu gửi bưu chính |
| Data Snapshot | Cơ chế đóng băng dữ liệu lịch sử tại thời điểm tạo đơn |
| RBAC | Role-Based Access Control (Kiểm soát truy cập dựa trên vai trò) |
| MoSCoW | Phương pháp phân loại ưu tiên: MUST (Bắt buộc), SHOULD (Nên có), COULD (Có thì tốt), WON'T (Không làm giai đoạn này) |

### 1.4 Tài liệu tham chiếu
- Business Requirements Document (BRD v1.0): `docs_wiki/raw/assets/hoang-nam-brd/hoang-nam-brd.md`
- Database Schema Design (ERD & Data Dictionary v1.0): `docs_wiki/raw/assets/hoang-nam-db/hoang-nam-db.md`
- Delivery Pricing Formulas (Pricing Model v1.0): `docs_wiki/raw/assets/hoang-nam-pricing/hoang-nam-pricing.md`
- Detailed Use Case Specifications (v2.0): `docs_wiki/raw/assets/hoang-nam-use-cases/hoang-nam-use-cases.md`
- User Stories Backlog: `docs_wiki/raw/assets/hoang-nam-user-stories/hoang-nam-user-stories.md`
- UI/UX Wireframes Specification: `docs_wiki/raw/assets/hoang-nam-wireframes/hoang-nam-wireframes.md`

### 1.5 Tổng quan tài liệu
Tài liệu SRS bao gồm 7 chương chính: Chương 1 Giới thiệu; Chương 2 Mô tả tổng thể; Chương 3 Yêu cầu chức năng chi tiết; Chương 4 Yêu cầu phi chức năng; Chương 5 Yêu cầu giao diện; Chương 6 Yêu cầu dữ liệu; Chương 7 Phụ lục & Ma trận truy vết.

---

## 2. Mô tả tổng thể (Overall Description)

### 2.1 Bối cảnh sản phẩm
Hệ thống Hoàng Nam Express Giai đoạn 1 là ứng dụng Web Portal độc lập dành cho nhân sự nội bộ công ty Hoàng Nam, được thiết kế theo mô hình kiến trúc Monorepo kế thừa từ nền tảng VeloxShip. Hệ thống đóng vai trò trung tâm điều hành mọi hoạt động tiếp nhận, trung chuyển, giao nhận, và quản lý tài chính dòng tiền COD tại tất cả các bưu cục chi nhánh và kho tổng.

```
+-----------------------------------------------------------------------+
|                    HOANG NAM EXPRESS WEB PORTAL                       |
|                                                                       |
|  +-----------------+  +-----------------+  +-----------------------+  |
|  |  Counter Staff  |  | Warehouse Keep. |  |   Cashier / Finance   |  |
|  | (Tạo đơn, thu)  |  | (Quét kho, Trip)|  | (Duyệt COD, Công nợ)  |  |
|  +--------+--------+  +--------+--------+  +-----------+-----------+  |
|           |                    |                       |              |
+-----------|--------------------|-----------------------|--------------+
            |                    |                       |
            v                    v                       v
+-----------------------------------------------------------------------+
|                          FASTAPI BACKEND CORE                         |
|   (Python 3.12, Async SQLAlchemy 2.x, Pydantic v2, Auth JWT, OpenAPI)   |
+-----------------------------------------------------------------------+
                                 |
                                 v
+-----------------------------------------------------------------------+
|                        POSTGRESQL 16 DATABASE                         |
|  (Extensions: unaccent, pg_trgm, citext | Strict CHECK constraints)   |
+-----------------------------------------------------------------------+
```

### 2.2 Chức năng chính (High-level Functions)
1. **Phân hệ Nhân sự & Phân quyền**: Quản lý hồ sơ nhân viên, phòng ban, chức vụ và phân quyền chi tiết theo hành động (`action-level RBAC`).
2. **Phân hệ Cấu hình Hệ thống**: Quản lý địa giới hành chính 3 cấp, danh mục bưu cục & tuyến phục vụ, đội xe, dịch vụ vận chuyển & loại hàng hóa.
3. **Phân hệ Khách hàng & Công nợ**: Quản lý danh bạ khách hàng, thiết lập bảng giá cước ưu đãi riêng/nhóm, gom bảng kê đối soát công nợ gửi định kỳ.
4. **Phân hệ Đối tác 3PL**: Quản lý kết nối API 3PL và bảng giá cước mua dịch vụ 3PL.
5. **Phân hệ Vận đơn**: Quản lý lấy hàng, Tạo vận đơn thủ công & in phiếu gửi, Tra cứu vận đơn, Rollback trạng thái giao hàng, Điều chỉnh COD trước xuất kho, Audit Log.
6. **Phân hệ Kho bưu cục**: Quét nhập kho, Kiểm kê tồn kho thực tế, Quét xuất kho trung chuyển đơn lẻ, Quét xuất 3PL, Quét xuất giao hàng bưu tá, Quét xuất trả hàng, Lịch sử xuất nhập kho.
7. **Phân hệ Đội xe & Chuyển xe**: Tạo chuyến xe trung chuyển, gán tài xế, bốc xếp vận đơn lẻ lên xe tải, xác nhận xuất bến và theo dõi hành trình.
8. **Phân hệ Quản lý COD**: Bưu tá lập bảng kê nộp tiền COD cuối ngày, Thủ quỹ đối soát đếm tiền mặt thực tế và phê duyệt nhập quỹ két sắt bưu cục.
9. **Phân hệ Báo cáo Thống kê**: Xuất tối đa 20 mẫu báo cáo doanh thu, sản lượng, công nợ và hiệu suất bưu tá.

### 2.3 User Class & Đặc điểm
| User Class | Số lượng dự kiến | Tần suất sử dụng | Môi trường thiết bị | Đặc điểm & Yêu cầu |
|---|---|---|---|---|
| Nhân viên quầy (Counter Staff) | ~100 | Hàng ngày (liên tục) | Desktop Web (Browser) | Thao tác nhập liệu nhanh, gõ bàn phím chuẩn, in ấn phiếu gửi nhiệt A5/A6 |
| Nhân viên kho (Warehouse Keeper) | ~150 | Hàng ngày (liên tục) | Web Desktop / Mobile Web | Dùng máy quét mã vạch cầm tay (Barcode Scanner), thao tác quét kho siêu tốc |
| Bưu tá / Tài xế (Shipper / Driver) | ~300 | Hàng ngày (cuối ca) | Mobile Web Responsive | Thao tác trên điện thoại thông minh, giao diện responsive, chọn đơn lập bảng kê COD |
| Thủ quỹ bưu cục (Cashier) | ~50 | Hàng ngày (cuối ca) | Desktop Web (Browser) | Kiểm đếm tiền mặt, kiểm soát bảng kê COD, quản lý sổ quỹ bưu cục |
| Quản trị viên / Điều hành (Admin / PO) | ~10 | Hàng tuần | Desktop Web (Browser) | Cấu hình bảng giá, phân quyền, xem báo cáo thống kê, rollback trạng thái đơn |

### 2.4 Môi trường vận hành
- **Client Web Portal**:
  - Trình duyệt: Google Chrome 100+, Microsoft Edge 100+, Mozilla Firefox 100+, Apple Safari 15+
  - Độ phân giải tối thiểu: Responsive từ 360px (Mobile Web bưu tá) đến 1920x1080 (Desktop Web admin/quầy)
- **Backend Application Server**:
  - Hệ điều hành: Linux Ubuntu 22.04 LTS hoặc Docker Container (Python 3.12+)
  - Framework: FastAPI (Async ASGI with Uvicorn/Gunicorn)
- **Database Server**:
  - Hệ quản trị CSDL: PostgreSQL 16+ với các extensions `unaccent`, `pg_trgm`, `citext`
- **Thiết bị ngoại vi**:
  - Máy in nhiệt bưu cục khổ A5/A6 (hỗ trợ in qua lệnh in trình duyệt Browser Print / PDF HTML)
  - Đầu đọc mã vạch / máy quét Barcode USB / Bluetooth emulating Keyboard HID input

### 2.5 Ràng buộc thiết kế & triển khai
- **Bản địa hóa 100%**: Tất cả giao diện, thông báo lỗi, đơn vị đo lường (kg, cm, VNĐ) và định dạng ngày tháng (`dd/mm/yyyy`) chuẩn hóa tiếng Việt.
- **Ràng buộc Data Snapshot**: Thông tin người gửi và người nhận khi tạo đơn phải được lưu cứng dưới dạng Snapshot (`sender_name`, `sender_phone`, `sender_address_detail`, `sender_ward_code`, `receiver_...`) vào bảng `bills`, không tham chiếu khóa ngoại động đến danh bạ khách hàng.
- **Ràng buộc Toàn vẹn CSDL (Strict CHECK Constraints)**:
  - Cước phí: `CHECK (fee_total = fee_main + fee_insurance + fee_other + fee_vat)`
  - Đền bù/Hủy đơn: `CHECK (status <> 'huy' OR cancellation_reason IS NOT NULL)`
  - Phát thành công: `CHECK (status <> 'da_giao' OR (delivered_at IS NOT NULL AND delivered_to_name IS NOT NULL))`
- **Ràng buộc Bảo mật & Pháp lý**: Đặt máy chủ và cơ sở dữ liệu tại các Datacenter trong nước, tuân thủ Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân.

### 2.6 Giả định & Phụ thuộc
- Dữ liệu địa giới hành chính tĩnh 3 cấp Việt Nam (63 Tỉnh/Thành, 705 Quận/Huyện, 10,500+ Phường/Xã) sẵn sàng để import ban đầu.
- Nhân viên bưu cục được trang bị máy tính và kết nối Internet ổn định tại bưu cục.
- Các đối tác 3PL (GHN, GHTK, Viettel Post) cung cấp tài liệu REST API và môi trường Sandbox thử nghiệm ổn định.

---

## 3. Yêu cầu chức năng (Functional Requirements)

### 3.1 Phân hệ Quản lý Nhân sự & Phân Quyền (Staff & Authorization)

#### FR-STAFF-01: Quản lý hồ sơ nhân viên tập trung
- **Mô tả**: Cho phép quản trị viên xem danh sách, tạo mới, cập nhật thông tin và thay đổi trạng thái hoạt động của nhân viên. Gộp thông tin phòng ban (`departments`) và chức vụ (`positions`) vào màn hình quản lý nhân viên.
- **Mức ưu tiên**: MUST
- **Input**: Họ tên, Số điện thoại (duy nhất), Username (duy nhất), Mật khẩu, Phòng ban (`department_id`), Chức vụ (`position_id`), Bưu cục trực thuộc (`hub_id`), Trạng thái (`is_active`).
- **Output**: Tài khoản nhân viên được lưu vào bảng `users`.
- **Business Rules**:
  - BR-STAFF-1.1: SĐT và Username không được trùng lặp trong cơ sở dữ liệu.
  - BR-STAFF-1.2: Mật khẩu bắt buộc mã hóa băm bằng thuật toán Bcrypt (cost factor >= 12) trước khi lưu DB.
- **Truy vết BRD**: BR-STAFF-01 | **Use Case**: UC-WEB-03
- **Acceptance Criteria**:
  - Giao diện hiển thị danh sách nhân viên phân trang, hỗ trợ tìm kiếm theo tên/SĐT/bưu cục.
  - Khi vô hiệu hóa tài khoản (`is_active = false`), nhân viên bị đăng xuất ngay lập tức và không thể đăng nhập lại.

#### FR-STAFF-02: Cấu hình phân quyền chi tiết (RBAC)
- **Mô tả**: Cho phép Quản trị viên định nghĩa các nhóm quyền/vai trò (`permission_groups`) và gán các hành động chi tiết (`permission_actions`) cho từng nhóm quyền.
- **Mức ưu tiên**: MUST
- **Input**: Tên nhóm quyền, Mô tả, Danh sách các mã quyền hạn (`bill:create`, `bill:rollback`, `trip:create`, `cod:approve`, `hub:scan_in`, ...).
- **Output**: Phân quyền được áp dụng tức thì cho tất cả nhân viên gán nhóm quyền đó.
- **Business Rules**:
  - BR-STAFF-2.1: Hệ thống kiểm tra quyền hạn ở mức API Middleware (Backend) dựa trên JWT Token và bảng `permission_actions`.
- **Truy vết BRD**: BR-STAFF-02 | **Use Case**: UC-WEB-10
- **Acceptance Criteria**:
  - Nhân viên không có mã quyền tương ứng sẽ bị ẩn button thao tác trên UI và nhận lỗi HTTP 403 Forbidden nếu gọi API trực tiếp.

---

### 3.2 Phân hệ Cấu hình Hệ thống & Vận hành (Settings)

#### FR-SETTING-01: Quản lý Danh mục Địa giới Hành chính 3 cấp
- **Mô tả**: Hệ thống lưu trữ và cung cấp API tra cứu danh mục Tỉnh/Thành phố (`provinces`), Quận/Huyện (`districts`), và Phường/Xã (`wards`) toàn quốc.
- **Mức ưu tiên**: MUST
- **Input**: File dữ liệu chuẩn địa giới hành chính quốc gia (JSON/CSV).
- **Output**: Cơ sở dữ liệu chứa danh mục 3 cấp sẵn sàng cho dropdown chọn địa chỉ.
- **Truy vết BRD**: BR-SETTING-01 | **Use Case**: UC-WEB-04, UC-WEB-05, UC-WEB-06
- **Acceptance Criteria**:
  - Khi người dùng chọn Tỉnh/Thành, danh sách Quận/Huyện tự động lọc theo tỉnh đó. Chọn Quận/Huyện tự động lọc danh sách Phường/Xã tương ứng.

#### FR-SETTING-02: Quản lý Bưu cục & Tuyến phục vụ
- **Mô tả**: Cho phép tạo bưu cục/chi nhánh (`hubs`) và gán danh sách Phường/Xã chịu trách nhiệm lấy/phát hàng (`hub_service_areas`).
- **Mức ưu tiên**: MUST
- **Input**: Mã bưu cục, Tên bưu cục, SĐT, Địa chỉ chi tiết, Mã Phường/Xã vị trí bưu cục, Danh sách mã Phường/Xã tuyến phụ trách.
- **Business Rules**:
  - BR-SETTING-2.1: Mỗi Phường/Xã chỉ được gán cho tối đa 01 bưu cục phụ trách lấy/phát để tránh chồng chéo tuyến.
- **Truy vết BRD**: BR-SETTING-02 | **Use Case**: UC-WEB-07, UC-WEB-08
- **Acceptance Criteria**:
  - Khi tạo đơn mới, hệ thống dựa vào địa chỉ Phường/Xã người nhận để tự động xác định Bưu cục phát chặng cuối (`destination_hub_id`).

#### FR-SETTING-03: Quản lý Đội xe Vận chuyển
- **Mô tả**: Quản lý thông tin xe tải trung chuyển và xe máy bưu tá (`vehicles`).
- **Mức ưu tiên**: MUST
- **Input**: Biển số xe (duy nhất), Loại xe (xe tải/xe máy), Khối lượng tải tối đa ($W_{max\_kg}$), Thể tích thùng tối đa ($V_{max\_m3}$), Bưu cục quản lý, Tài xế mặc định.
- **Truy vết BRD**: BR-SETTING-03 | **Use Case**: UC-WEB-09
- **Acceptance Criteria**:
  - Xe bị đánh dấu `maintenance` hoặc `inactive` sẽ không xuất hiện trong dropdown chọn xe khi tạo chuyến xe.

#### FR-SETTING-04: Cấu hình Dịch vụ & Loại hàng hóa
- **Mô tả**: Định nghĩa danh mục gói dịch vụ vận chuyển chính (`service_tiers`: Tiêu chuẩn, Hỏa tốc) và phân loại hàng hóa (`cargo_type`: Tài liệu, Hàng hóa cồng kềnh, Dễ vỡ, Chất lỏng).
- **Mức ưu tiên**: MUST
- **Truy vết BRD**: BR-SETTING-04 | **Use Case**: UC-WEB-11, UC-WEB-12

---

### 3.3 Phân hệ Quản lý Khách hàng & Bảng Giá & Công Nợ (Customer & Billing)

#### FR-CUST-01: Quản lý Hồ sơ Khách hàng
- **Mô tả**: Lưu trữ danh bạ khách hàng gửi (`customers`), phân loại nhóm khách hàng (`retail`, `shop`, `enterprise`).
- **Mức ưu tiên**: MUST
- **Input**: Mã khách hàng, Họ tên/Tên công ty, SĐT, Email, Địa chỉ, Mã nhóm khách hàng.
- **Truy vết BRD**: BR-CUSTOMER-01 | **Use Case**: UC-WEB-13

#### FR-CUST-02: Thiết lập Bảng giá cước & Quy tắc cước chi tiết
- **Mô tả**: Cấu hình bảng giá cước (`price_sheets`) áp dụng riêng cho từng khách hàng lớn hoặc áp dụng chung cho nhóm khách hàng, kèm chi tiết các quy tắc tính cước (`price_rules`).
- **Mức ưu tiên**: MUST
- **Input**: Tên bảng giá, Mã khách hàng hoặc Mã nhóm khách hàng, Gói dịch vụ, Loại tuyến đường (`intra_province`, `intra_region`, `inter_region`), Cân nặng nền ($W_{max}$), Cước nền ($F_{base}$), Bước cân ($W_{step}$), Đơn giá bước ($F_{step}$).
- **Business Rules**:
  - BR-CUST-2.1 (Thứ tự ưu tiên tính cước): Bảng giá riêng Khách hàng > Bảng giá Nhóm khách hàng > Bảng giá Mặc định Khách lẻ.
- **Truy vết BRD**: BR-CUSTOMER-02 | **Use Case**: UC-WEB-14
- **Acceptance Criteria**:
  - Cung cấp công cụ mô phỏng thử nghiệm tính cước (Test Price Calculation) cho phép kế toán nhập thông số đơn hàng giả định để kiểm tra kết quả cước trước khi kích hoạt bảng giá.

#### FR-CUST-03: Bảng đối soát Công nợ Khách hàng gửi định kỳ
- **Mô tả**: Gom tất cả các vận đơn phát thành công trong chu kỳ (tuần/tháng) của từng khách hàng shop/doanh nghiệp để lập Bảng kê đối soát công nợ, tính bù trừ giữa Tiền cước vận chuyển và Tiền thu hộ COD.
- **Mức ưu tiên**: MUST
- **Truy vết BRD**: BR-CUSTOMER-03 | **Use Case**: UC-WEB-15

---

### 3.4 Phân hệ Quản lý Đối tác 3PL (Partner Management)

#### FR-3PL-01: Quản lý Kết nối & Giá mua Cước Đối tác 3PL
- **Mô tả**: Lưu thông tin cấu hình tài khoản kết nối API đối tác vận chuyển bên thứ ba (`partners`: GHN, GHTK, Viettel Post) và bảng giá cước mua dịch vụ 3PL (`partner_tariffs`) để tính giá vốn.
- **Mức ưu tiên**: SHOULD
- **Input**: Mã đối tác, Tên đối tác, Endpoint API URL, Token xác thực API, Bảng giá cước mua.
- **Truy vết BRD**: BR-PARTNER-01 | **Use Case**: UC-WEB-16, UC-WEB-17

---

### 3.5 Phân hệ Quản lý Vận đơn (Waybill Management)

#### FR-WAY-01: Quản lý Yêu cầu Lấy hàng
- **Mô tả**: Tiếp nhận yêu cầu gửi hàng, điều phối bưu tá đến địa chỉ người gửi để nhận bưu gửi và chuyển trạng thái "Đang đi lấy" -> "Đã lấy hàng".
- **Mức ưu tiên**: MUST
- **Truy vết BRD**: BR-WAYBILL-01 | **Use Case**: UC-WEB-18

#### FR-WAY-02: Tạo Vận đơn Thủ công & In Phiếu gửi Barcode
- **Mô tả**: Nhân viên quầy nhập thông tin bưu gửi, hệ thống tự động tra cứu danh bạ/địa giới, tính cước tự động, sinh mã vận đơn duy nhất (VD: `HN123456789VN`), khóa **Data Snapshot** và xuất mã in phiếu gửi nhiệt A5/A6.
- **Mức ưu tiên**: MUST
- **Input**: SĐT/Tên/Địa chỉ người gửi, SĐT/Tên/Địa chỉ người nhận (Tỉnh/Huyện/Xã), Cân nặng thực tế ($W_{real}$), Kích thước (D x R x C cm), Tiền COD thu hộ, Giá trị khai báo bảo hiểm, Gói dịch vụ, Người trả cước (người gửi/người nhận).
- **Output**: Vận đơn lưu vào bảng `bills`, bảng `bill_content_lines`, dữ liệu snapshot khóa cứng, mã HTML/PDF in phiếu gửi.
- **Business Rules**:
  - BR-WAY-2.1: Khối lượng tính cước $W_{charge} = \max(W_{real}, (D \times R \times C) / 6000)$.
  - BR-WAY-2.2: Dữ liệu tên/SĐT/địa chỉ người gửi & nhận được lưu snapshot trực tiếp vào bảng `bills` tại cột `sender_...` và `receiver_...`.
- **Truy vết BRD**: BR-WAYBILL-02 | **Use Case**: UC-WAYBILL-01 (UC-WEB-19)
- **Acceptance Criteria**:
  - In phiếu gửi khổ A6 chứa đầy đủ Barcode/QR code mã đơn, thông tin người gửi/nhận, số tiền COD in to rõ ràng, bảng phân rã các khoản cước phí.

#### FR-WAY-03: Danh sách Tra cứu Vận đơn đa điều kiện
- **Mô tả**: Màn hình tra cứu tổng thể danh sách vận đơn với bộ lọc thông minh theo mã đơn, SĐT gửi/nhận, khoảng thời gian tạo đơn, bưu cục hiện tại, bưu tá phụ trách và trạng thái hành trình.
- **Mức ưu tiên**: MUST
- **Truy vết BRD**: BR-WAYBILL-03 | **Use Case**: UC-WEB-23

#### FR-WAY-04: Rollback Trạng thái Giao hàng Thành công
- **Mô tả**: Cho phép Quản lý có thẩm quyền (`bill:rollback`) khôi phục trạng thái đơn từ "Giao thành công" về trạng thái trước đó (như "Đang giao hàng" hoặc "Đã nhập kho phát") khi phát hiện cập nhật nhầm hoặc có khiếu nại.
- **Mức ưu tiên**: MUST
- **Input**: Mã vận đơn, Lý do rollback (bắt buộc nhập text).
- **Output**: Cập nhật trạng thái đơn, ghi nhật ký vào `bill_status_logs`.
- **Business Rules**:
  - BR-WAY-4.1: Đơn hàng đã nằm trong Bảng kê nộp tiền COD đã duyệt (`approved`) KHÔNG ĐƯỢC PHÉP rollback trạng thái.
- **Truy vết BRD**: BR-WAYBILL-04 | **Use Case**: UC-WEB-24

#### FR-WAY-05: Điều chỉnh Tiền thu hộ COD trước khi xuất kho phát
- **Mô tả**: Cho phép sửa số tiền COD thu hộ của vận đơn khi có yêu cầu xác nhận từ người gửi trước khi đơn hàng được quét xuất kho bàn giao cho bưu tá đi giao.
- **Mức ưu tiên**: SHOULD
- **Truy vết BRD**: BR-WAYBILL-05 | **Use Case**: UC-WEB-26

#### FR-WAY-06: Nhật ký Lịch sử Thay đổi (Audit Log Vận đơn)
- **Mô tả**: Tự động ghi lại toàn bộ lịch sử chỉnh sửa thông tin vận đơn, thay đổi tiền cước, thay đổi COD, người thực hiện và thời gian thực hiện.
- **Mức ưu tiên**: MUST
- **Output**: Bảng `bill_status_logs`.
- **Truy vết BRD**: BR-WAYBILL-06 | **Use Case**: UC-WEB-27

---

### 3.6 Phân hệ Nghiệp vụ Kho Bưu cục (Hub Operations)

#### FR-HUB-01: Quét Mã Vạch Nhập Kho Bưu Cục (Inbound Scan)
- **Mô tả**: Nhân viên kho dùng máy quét barcode quét nhận các vận đơn do bưu tá lấy về hoặc từ chuyến xe tải trung chuyển từ bưu cục khác chuyển tới.
- **Mức ưu tiên**: MUST
- **Input**: Con trỏ ở ô quét mã, chuỗi mã vạch vận đơn (`tracking_number`).
- **Output**: Cập nhật `current_hub_id` = ID bưu cục hiện tại, `status` = 'da_lay_hang' hoặc 'dang_van_chuyen', phát âm thanh "Tít" báo thành công.
- **Business Rules**:
  - BR-HUB-1.1: Nếu đơn đã ở kho hiện tại, phát âm thanh cảnh báo lỗi (còi dài) và hiển thị thông báo "Đơn đã nhập kho này trước đó".
- **Truy vết BRD**: BR-WAREHOUSE-01 | **Use Case**: UC-WAREHOUSE-01 (UC-WEB-28)

#### FR-HUB-02: Kiểm Điểm Tồn Kho Thực Tế (Stocktake)
- **Mô tả**: Nhân viên kho quét tất cả hàng hóa hiện đang có tại kho bưu cục để hệ thống đối soát dữ liệu tồn kho trên phần mềm, phát hiện đơn thừa/đơn thiếu.
- **Mức ưu tiên**: MUST
- **Truy vết BRD**: BR-WAREHOUSE-02 | **Use Case**: UC-WEB-29

#### FR-HUB-03: Quét Xuất Kho Trung Chuyển Đơn Lẻ (Single Waybill Outbound Scan)
- **Mô tả**: Quét xuất kho nhiều vận đơn lẻ cần trung chuyển đi bưu cục tiếp theo hoặc kho tổng, in Bảng kê chi tiết danh sách vận đơn trung chuyển (Danh sách đơn, tổng khối lượng, bưu cục đích). *(Lưu ý: Nghiệp vụ Đóng bao trung chuyển Bagging được trì hoãn sang Giai đoạn 2)*.
- **Mức ưu tiên**: MUST
- **Input**: Chọn Bưu cục đích đến, danh sách mã vận đơn quét lẻ.
- **Output**: In bảng kê xuất kho trung chuyển, chuyển trạng thái đơn sang 'dang_van_chuyen'.
- **Truy vết BRD**: BR-WAREHOUSE-03 | **Use Case**: UC-WEB-30

#### FR-HUB-04: Quét Xuất Hàng Bàn Giao Đối Tác 3PL
- **Mô tả**: Quét mã vạch bàn giao đơn cho đối tác 3PL vận chuyển ngoài và in Bảng kê bàn giao 3PL.
- **Mức ưu tiên**: SHOULD
- **Truy vết BRD**: BR-WAREHOUSE-04 | **Use Case**: UC-WEB-31

#### FR-HUB-05: Quét Xuất Kho Bàn Giao Bưu Tá Đi Phát (Last-mile Outbound Scan)
- **Mô tả**: Nhân viên kho chọn bưu tá phụ trách tuyến, quét mã vạch các bưu gửi bàn giao bưu tá đi phát chặng cuối, gán `shipper_id`, chuyển trạng thái 'dang_giao' và in Bảng kê giao hàng (Runsheet).
- **Mức ưu tiên**: MUST
- **Input**: Chọn bưu tá, danh sách mã vận đơn quét.
- **Output**: Bảng `bills` cập nhật `shipper_id`, status = 'dang_giao', in Runsheet A5/A6 có chỗ ký nhận của bưu tá.
- **Truy vết BRD**: BR-WAREHOUSE-05 | **Use Case**: UC-WAREHOUSE-05 (UC-WEB-32)

#### FR-HUB-06: Quét Xuất Kho Trả Hàng Hoàn (Return Outbound)
- **Mô tả**: Xuất kho các đơn phát không thành công nhiều lần để làm thủ tục chuyển hoàn về cho người gửi.
- **Mức ưu tiên**: MUST
- **Truy vết BRD**: BR-WAREHOUSE-06 | **Use Case**: UC-WEB-33

#### FR-HUB-07: Lịch sử Chi tiết Xuất / Nhập Kho
- **Mô tả**: Tra cứu lịch sử mốc thời gian và nhân sự kho thực hiện quét nhập/xuất kho của từng vận đơn.
- **Mức ưu tiên**: MUST
- **Truy vết BRD**: BR-WAREHOUSE-07 | **Use Case**: UC-WEB-34

---

### 3.7 Phân hệ Quản lý Đội xe & Chuyển xe (Fleet & Trip Management)

#### FR-TRIP-01: Quản lý & Điều phối Chuyến xe Trung chuyển
- **Mô tả**: Chọn kho đích, xe tải, tài xế để khởi tạo Chuyến xe (`trips`). Nhân viên đặt con trỏ quét từng vận đơn lẻ bốc xếp lên xe (gán vào bảng `trip_bills`). Kiểm tra tự động giới hạn tải trọng ($W_{max}$) và thể tích thùng xe ($V_{max}$).
- **Mức ưu tiên**: MUST
- **Input**: Bưu cục đích, Chọn Xe tải, Chọn Tài xế, Quét danh sách mã vận đơn lẻ.
- **Output**: Chuyến xe tạo thành công (Mã TRIP duy nhất, VD: `TRIP2107260012`), liên kết `trip_bills`, status chuyến xe = `in_transit`, status các đơn = `dang_van_chuyen`.
- **Business Rules**:
  - BR-TRIP-1.1: Quét thêm 1 vận đơn nếu khiến tổng khối lượng vượt $W_{max\_kg}$ hoặc tổng thể tích vượt $V_{max\_m3}$ của xe tải, hệ thống phải phát còi cảnh báo lỗi và không cho gán đơn đó vào chuyến xe.
- **Truy vết BRD**: BR-TRIP-01, BR-TRIP-02 | **Use Case**: UC-TRIP-01 (UC-WEB-35, UC-WEB-36)
- **Acceptance Criteria**:
  - Hiển thị thanh dung lượng (progress bar) thể hiện phần trăm tải trọng và thể tích đã sử dụng trên thùng xe tải theo thời gian thực khi quét từng đơn.

---

### 3.8 Phân hệ Quản lý Dòng Tiền Thu Hộ COD (COD Handover & Cash Control)

#### FR-COD-01: Bưu tá Lập Bảng Kê Nộp Tiền Mặt COD Cuối Ngày
- **Mô tả**: Cuối ca làm việc, bưu tá mở giao diện nộp tiền, chọn danh sách các đơn hàng có COD phát thành công trong ngày đã thu tiền mặt. Hệ thống tự động tính tổng tiền COD khai báo, tạo mã Bảng kê nộp tiền (`cod_handovers`, VD: `COD2107260088`) ở trạng thái `pending` (Chờ thủ quỹ duyệt).
- **Mức ưu tiên**: MUST
- **Input**: Đánh dấu chọn danh sách vận đơn phát thành công.
- **Output**: Bảng kê `cod_handovers` (status = `pending`), các đơn liên kết trong `cod_handover_items`.
- **Business Rules**:
  - BR-COD-1.1: Các đơn đã nằm trong bảng kê `pending` sẽ bị khóa không cho bưu tá sửa/xóa hay chọn vào bảng kê khác.
- **Truy vết BRD**: BR-COD-01, BR-COD-02 | **Use Case**: UC-COD-01 (UC-WEB-37, UC-WEB-38)

#### FR-COD-02: Thủ quỹ Xác nhận Thu Tiền Mặt COD & Nhập Quỹ Két Sắt (3-Step Reconciliation)
- **Mô tả**: Bưu tá mang cọc tiền mặt đến nộp cho Thủ quỹ bưu cục. Thủ quỹ tra cứu mã bảng kê, đếm tiền mặt thực tế và nhập vào hệ thống:
  - Nếu khớp (Tiền thực đếm = Tiền khai báo): Bấm Duyệt -> Bảng kê chuyển status `approved`, các đơn hàng chuyển status "Đã đối soát COD nội bộ", số dư tiền mặt két sắt bưu cục (`hub_ledgers`) tăng tương ứng.
  - Nếu lệch (Tiền thực đếm khác Tiền khai báo): Bấm Từ chối -> Bảng kê chuyển status `rejected`, yêu cầu bưu tá đối soát lại.
- **Mức ưu tiên**: MUST
- **Input**: Mã bảng kê COD, Số tiền mặt thực thu đếm được, Lý do từ chối (nếu lệch).
- **Output**: Cập nhật `cod_handovers.status`, ghi nhận giao dịch thu quỹ vào `hub_ledgers` (transaction_type = `shipper_remittance`).
- **Business Rules**:
  - BR-COD-2.1 (Khóa két cuối ngày): Bắt buộc tất cả bảng kê COD phát sinh trong ngày phải được duyệt hoặc từ chối xử lý trước 22:00 hàng ngày.
  - BR-COD-2.2: Bưu tá chịu trách nhiệm đền bù 100% số tiền mặt thiếu hụt so với bảng kê các đơn đã cập nhật "Giao thành công".
- **Truy vết BRD**: BR-COD-03 | **Use Case**: UC-COD-03 (UC-WEB-39)

---

### 3.9 Phân hệ Báo cáo Thống kê (Reports & Analytics)

#### FR-REP-01: Hệ thống Báo cáo Thống kê Động (Tối đa 20 biểu mẫu)
- **Mô tả**: Cung cấp các báo cáo dạng bảng và biểu đồ động phục vụ quản lý:
  1. Báo cáo Doanh thu Vận chuyển (theo ngày/tháng/bưu cục).
  2. Báo cáo Sản lượng Vận đơn (theo trạng thái/gói dịch vụ).
  3. Báo cáo Công nợ Khách hàng gửi.
  4. Báo cáo Hiệu suất Giao nhận của Bưu tá (tỷ lệ phát thành công, thời gian giao trung bình).
  5. Báo cáo Quỹ tiền mặt COD bưu cục.
- **Mức ưu tiên**: MUST
- **Input**: Khoảng thời gian, Chọn bưu cục, Loại báo cáo.
- **Output**: Dữ liệu hiển thị dạng Grid/Chart, hỗ trợ export file Excel (.xlsx) / CSV.
- **Truy vết BRD**: BR-REPORT-01 | **Use Case**: UC-WEB-40

---

## 4. Yêu cầu phi chức năng (Non-Functional Requirements)

### 4.1 Performance (Hiệu năng)
- **NFR-P1**: 95% số lượng request API trả về thời gian phản hồi (Response Time) < 500ms ở môi trường production.
- **NFR-P2**: Thời gian tra cứu và hiển thị kết quả tìm kiếm vận đơn không dấu trên cơ sở dữ liệu > 100.000 đơn hàng < 1.0 giây (nhờ sử dụng PostgreSQL GIN Trigram Index).
- **NFR-P3**: Hệ thống đáp ứng tối thiểu 500 người dùng thao tác đồng thời (concurrent users) mà không bị treo hoặc sụt giảm hiệu năng quá 20%.
- **NFR-P4**: Thao tác quét mã vạch kho (Inbound/Outbound Scan) xử lý và trả về phản hồi âm thanh trong vòng < 300ms cho từng lượt quét.

### 4.2 Security (Bảo mật)
- **NFR-S1**: Tất cả mật khẩu người dùng phải được mã hóa băm bằng Bcrypt với cost factor >= 12.
- **NFR-S2**: 100% giao tiếp kết nối Client - Server bắt buộc qua giao thức bảo mật HTTPS (TLS 1.3+).
- **NFR-S3**: Xác thực người dùng thông qua Stateless JWT (JSON Web Token) với thời gian hết hạn access token là 8 giờ, refresh token 7 ngày.
- **NFR-S4**: Áp dụng kiểm soát truy cập RBAC nghiêm ngặt ở cấp API Endpoint (Backend Middleware).
- **NFR-S5**: Toàn bộ thao tác thay đổi dữ liệu nhạy cảm (sửa cước, sửa COD, rollback trạng thái) phải ghi nhật ký Audit Log (`bill_status_logs`) và lưu trữ tối thiểu 24 tháng.
- **NFR-S6**: Giới hạn tần suất truy cập API (Rate Limiting): Tối đa 120 request/phút/IP để phòng chống tấn công brute-force và DDoS.

### 4.3 Reliability & Availability (Độ tin cậy & Sẵn sàng)
- **NFR-R1**: Mức độ sẵn sàng hệ thống (System Availability/Uptime) >= 99.5% (tương ứng tổng thời gian gián đoạn tối đa < 3.6 giờ/tháng).
- **NFR-R2**: Thực hiện sao lưu tự động cơ sở dữ liệu (Database Backup) hàng ngày vào lúc 02:00 sáng, thời gian lưu giữ bản backup tối thiểu 30 ngày.
- **NFR-R3**: Thời gian phục hồi hệ thống khi có sự cố (Recovery Time Objective - RTO) <= 2 giờ.
- **NFR-R4**: Điểm phục hồi dữ liệu tối đa chấp nhận mất (Recovery Point Objective - RPO) <= 1 giờ.

### 4.4 Usability & Accessibility (Dễ sử dụng)
- **NFR-U1**: Giao diện người dùng 100% sử dụng ngôn ngữ tiếng Việt chuẩn bưu chính, thuật ngữ nhất quán.
- **NFR-U2**: Màn hình nghiệp vụ Kho (Quét kho, Bốc xếp xe) được tối ưu thao tác bằng bàn phím và đầu đọc mã vạch, tự động focus lại ô quét mã sau mỗi lượt quét mà không cần dùng chuột.
- **NFR-U3**: Mọi thao tác hủy đơn hoặc rollback trạng thái bắt buộc hiển thị hộp thoại xác nhận (Confirmation Modal) để tránh bấm nhầm.

### 4.5 Scalability (Khả năng mở rộng)
- **NFR-SC1**: Kiến trúc Backend và Database sẵn sàng cho việc mở rộng tải (Horizontal Scaling), hỗ trợ quản lý lên đến 1,000,000 vận đơn/năm trong 3 năm tới.
- **NFR-SC2**: Thiết kế bảng `bills` và các bảng nhật ký sẵn sàng cho việc đánh phân vùng dữ liệu (Table Partitioning) theo tháng/năm khi dung lượng database vượt quá 50GB.

### 4.6 Compatibility (Tương thích)
- **NFR-C1**: Tương thích hiển thị tốt trên các trình duyệt hiện đại: Chrome, Edge, Firefox, Safari.
- **NFR-C2**: Màn hình bưu tá tương thích giao diện Responsive trên màn hình di động độ phân giải từ 360px trở lên.
- **NFR-C3**: Phiếu gửi A5/A6 in ra tương thích hoàn toàn với các dòng máy in nhiệt thông dụng (TSC, Xprinter, Gprinter) thông qua lệnh in trực tiếp của trình duyệt web.

### 4.7 Maintainability (Dễ bảo trì)
- **NFR-M1**: Tài liệu API được tự động sinh (Auto-generated OpenAPI 3.0 / Swagger UI) từ định nghĩa Pydantic Schemas trong FastAPI tại đường dẫn `/docs`.
- **NFR-M2**: Mã nguồn Backend và Frontend tuân thủ nghiêm ngặt chuẩn định dạng mã (ESLint, Prettier cho Frontend; Ruff/Black cho Python).
- **NFR-M3**: Quản lý phiên bản cơ sở dữ liệu (Database Migration) sử dụng Alembic.

### 4.8 Localization & Formatting
- **NFR-L1**: Định dạng tiền tệ: Sử dụng dấu phẩy phân cách hàng nghìn và ký hiệu đ/VNĐ ở sau (ví dụ: `150,000 VNĐ`). Kiểu dữ liệu DB là `NUMERIC(14, 2)`.
- **NFR-L2**: Định dạng khối lượng: Đơn vị `kg`, hiển thị chính xác 3 chữ số thập phân (ví dụ: `1.250 kg`). Kiểu dữ liệu DB là `NUMERIC(12, 3)`.
- **NFR-L3**: Định dạng thời gian: Hiển thị giao diện người dùng theo chuẩn `dd/mm/yyyy HH:MM:SS` (Múi giờ `Asia/Ho_Chi_Minh`), lưu trữ trong CSDL theo chuẩn UTC `TIMESTAMPTZ`.

---

## 5. Yêu cầu giao diện (Interface Requirements)

### 5.1 Giao diện người dùng (User Interface)
Hệ thống bao gồm 5 layout màn hình chính:
1. **Layout Quản trị Admin**: Menu bên trái (Sidebar), thanh điều hướng trên (Header bar hiển thị bưu cục làm việc và thông tin user), vùng nội dung chính (Main Content Grid).
2. **Layout Quầy Giao dịch (Counter Staff)**: Form tạo đơn 2 cột (Cột trái: Thông tin Người gửi & Người nhận; Cột phải: Thông số hàng hóa, Dịch vụ, Tính cước & xem trước phiếu gửi).
3. **Layout Nghiệp vụ Kho (Warehouse)**: Màn hình quét mã vạch tối giản, tập trung vào ô quét mã cỡ lớn, bảng danh sách các đơn đã quét trong phiên kèm chỉ số tổng đơn/tổng cân, và âm thanh phản hồi visual status.
4. **Layout Bưu tá Mobile**: Màn hình xem danh sách đơn phát thành công, ô checkbox chọn đơn và nút nổi "Lập bảng kê nộp tiền COD".
5. **Layout Mẫu in Phiếu gửi / Bảng kê**: Căn chỉnh chuẩn kích thước A6 nhiệt (100mm x 150mm) hoặc A5, loại bỏ header/footer của trình duyệt khi bấm In.

### 5.2 Giao diện Phần cứng (Hardware Interface)
- **Máy quét mã vạch (Barcode Scanner)**: Kết nối qua cổng USB hoặc Bluetooth, hoạt động ở chế độ giả lập bàn phím (Keyboard Emulation/HID).
- **Máy in nhiệt (Thermal Printer)**: Kết nối USB/LAN với máy tính quầy/kho, nhận lệnh in trực tiếp qua HTML Print API của trình duyệt.

### 5.3 Giao diện Phần mềm & Hệ thống bên ngoài (Software Interfaces)
| Hệ thống bên ngoài | Mục đích tích hợp | Giao thức | Định dạng dữ liệu |
|---|---|---|---|
| API GHN (Giao Hàng Nhanh) | Đẩy đơn sang đối tác 3PL & Lấy mã đơn 3PL | HTTPS REST API | JSON |
| API GHTK (Giao Hàng Tiết Kiệm) | Đẩy đơn sang đối tác 3PL & Lấy mã đơn 3PL | HTTPS REST API | JSON |
| API Viettel Post | Đẩy đơn sang đối tác 3PL & Lấy mã đơn 3PL | HTTPS REST API | JSON |
| SMS Gateway (Viettel/FPT) | Gửi SMS OTP / Thông báo hành trình đơn | HTTPS REST API | JSON |

### 5.4 Giao diện Truyền thông (Communication Interface)
- Kết nối giữa Client (React Web Portal) và Backend (FastAPI Core): HTTPS REST API với định dạng payload JSON.
- Đóng gói dữ liệu bảo mật bằng chuẩn TLS 1.3.

---

## 6. Yêu cầu dữ liệu (Data Requirements)

### 6.1 Các thực thể chính (Core Entities)
Cơ sở dữ liệu bao gồm 20 bảng chính (xem chi tiết tại tài liệu `hoang-nam-db.md`):
- Hành chính: `provinces`, `districts`, `wards`
- Bưu cục & Nhân sự: `hubs`, `hub_service_areas`, `departments`, `positions`, `users`, `permission_groups`, `user_permission_groups`, `permission_actions`
- Khách hàng & Giá: `customers`, `price_sheets`, `price_rules`
- Vận đơn: `bills`, `bill_content_lines`, `bill_status_logs`
- Đội xe & Chuyển xe: `vehicles`, `trips`, `trip_bills`
- COD & Sổ quỹ: `cod_handovers`, `cod_handover_items`, `hub_ledgers`
- 3PL: `partners`, `partner_tariffs`

### 6.2 Dung lượng dữ liệu dự kiến (Year 1 Growth Projections)
| Thực thể | Số lượng bản ghi khởi tạo | Tăng trưởng dự kiến / Tháng | Dung lượng lưu trữ dự kiến (Year 1) |
|---|---|---|---|
| `bills` (Vận đơn) | 0 | +10,000 đơn | ~120,000 bản ghi (~150 MB) |
| `bill_status_logs` | 0 | +50,000 logs | ~600,000 bản ghi (~250 MB) |
| `customers` | 500 | +50 shop | ~1,100 bản ghi (~2 MB) |
| `users` | 100 | +5 nhân viên | ~160 bản ghi (< 1 MB) |
| Total Database Size Year 1 | — | — | **< 2 GB** |

### 6.3 Chính sách Lưu trữ & Lưu trữ Lịch sử (Data Retention & Archiving)
- **Vận đơn (`bills`) & Chứng từ tài chính**: Lưu trữ trực tuyến (Online Storage) tối thiểu 5 năm theo quy định của Luật Kế toán Việt Nam.
- **Nhật ký hành trình Audit Log (`bill_status_logs`)**: Lưu trữ truy vấn nhanh 24 tháng, sau 24 tháng chuyển sang lưu kho nén (Archive Cold Storage).
- **Phiên đăng nhập (User Sessions)**: Hết hạn sau 7 ngày.

### 6.4 Bảo vệ Dữ liệu Cá nhân (Data Privacy & Compliance)
- Tuân thủ Nghị định 13/2023/NĐ-CP: Thông tin cá nhân của người gửi và người nhận (Họ tên, SĐT, Địa chỉ) được bảo vệ, chỉ hiển thị cho nhân viên được phân quyền phụ trách đơn đó.
- Dữ liệu Snapshot người gửi/nhận trong bảng `bills` không cho phép xóa bỏ vật lý (Hard Delete), chỉ cho phép đánh dấu hủy đơn (Soft Delete/Status 'huy') để phục vụ đối soát pháp lý.

---

## 7. Phụ lục & Ma trận truy vết (Appendix & Traceability Matrix)

### 7.1 Ma trận Truy vết Yêu cầu (Traceability Matrix)

| Yêu cầu Nghiệp vụ BRD | Use Case | Yêu cầu Chức năng SRS | Bảng Database liên quan |
|---|---|---|---|
| BR-STAFF-01 | UC-WEB-01, 02, 03 | FR-STAFF-01 | `users`, `departments`, `positions` |
| BR-STAFF-02 | UC-WEB-10 | FR-STAFF-02 | `permission_groups`, `permission_actions` |
| BR-SETTING-01 | UC-WEB-04, 05, 06 | FR-SETTING-01 | `provinces`, `districts`, `wards` |
| BR-SETTING-02 | UC-WEB-07, 08 | FR-SETTING-02 | `hubs`, `hub_service_areas` |
| BR-SETTING-03 | UC-WEB-09 | FR-SETTING-03 | `vehicles` |
| BR-SETTING-04 | UC-WEB-11, 12 | FR-SETTING-04 | `service_tiers` |
| BR-CUSTOMER-01 | UC-WEB-13 | FR-CUST-01 | `customers` |
| BR-CUSTOMER-02 | UC-WEB-14 | FR-CUST-02 | `price_sheets`, `price_rules` |
| BR-CUSTOMER-03 | UC-WEB-15 | FR-CUST-03 | `customer_statements` |
| BR-WAYBILL-01 | UC-WEB-18 | FR-WAY-01 | `bills` |
| BR-WAYBILL-02 | UC-WAYBILL-01 (UC-WEB-19) | FR-WAY-02 | `bills`, `bill_content_lines` |
| BR-WAYBILL-03 | UC-WEB-23 | FR-WAY-03 | `bills` |
| BR-WAYBILL-04 | UC-WEB-24 | FR-WAY-04 | `bills`, `bill_status_logs` |
| BR-WAYBILL-05 | UC-WEB-26 | FR-WAY-05 | `bills` |
| BR-WAYBILL-06 | UC-WEB-27 | FR-WAY-06 | `bill_status_logs` |
| BR-WAREHOUSE-01 | UC-WAREHOUSE-01 (UC-WEB-28)| FR-HUB-01 | `bills`, `bill_status_logs` |
| BR-WAREHOUSE-02 | UC-WEB-29 | FR-HUB-02 | `bills` |
| BR-WAREHOUSE-03 | UC-WEB-30 | FR-HUB-03 | `bills` |
| BR-WAREHOUSE-05 | UC-WAREHOUSE-05 (UC-WEB-32)| FR-HUB-05 | `bills` |
| BR-WAREHOUSE-06 | UC-WEB-33 | FR-HUB-06 | `bills` |
| BR-WAREHOUSE-07 | UC-WEB-34 | FR-HUB-07 | `bill_status_logs` |
| BR-TRIP-01, 02 | UC-TRIP-01 (UC-WEB-35, 36) | FR-TRIP-01 | `trips`, `trip_bills`, `vehicles` |
| BR-COD-01, 02 | UC-COD-01 (UC-WEB-37, 38) | FR-COD-01 | `cod_handovers`, `cod_handover_items` |
| BR-COD-03 | UC-COD-03 (UC-WEB-39) | FR-COD-02 | `cod_handovers`, `hub_ledgers` |
| BR-REPORT-01 | UC-WEB-40 | FR-REP-01 | Tất cả các bảng |

### 7.2 Danh mục Sơ đồ Tham chiếu
- Sơ đồ ERD Cơ sở Dữ liệu: `docs_wiki/raw/assets/hoang-nam-db/hoang-nam-db.md` (Chương 1)
- Sơ đồ Tổng quan Use Case: `docs_wiki/raw/assets/hoang-nam-use-cases/hoang-nam-use-cases.md` (Chương Sơ đồ tổng quan)
- Sơ đồ Chi tiết UC-WAYBILL-01: `docs_wiki/raw/assets/hoang-nam-use-cases/hoang-nam-use-cases.md` (Chương UC-WAYBILL-01)
- Sơ đồ Chi tiết UC-TRIP-01: `docs_wiki/raw/assets/hoang-nam-use-cases/hoang-nam-use-cases.md` (Chương UC-TRIP-01)
- Sơ đồ Chi tiết UC-COD-01: `docs_wiki/raw/assets/hoang-nam-use-cases/hoang-nam-use-cases.md` (Chương UC-COD-01)
- Sơ đồ Chi tiết UC-COD-03: `docs_wiki/raw/assets/hoang-nam-use-cases/hoang-nam-use-cases.md` (Chương UC-COD-03)
- Sơ đồ Chi tiết UC-WAREHOUSE-01: `docs_wiki/raw/assets/hoang-nam-use-cases/hoang-nam-use-cases.md` (Chương UC-WAREHOUSE-01)
- Sơ đồ Chi tiết UC-WAREHOUSE-05: `docs_wiki/raw/assets/hoang-nam-use-cases/hoang-nam-use-cases.md` (Chương UC-WAREHOUSE-05)
