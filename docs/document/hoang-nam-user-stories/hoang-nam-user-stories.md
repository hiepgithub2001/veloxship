# Agile User Stories
**Dự án**: Hệ thống Quản lý Chuyển phát nhanh Hoàng Nam (Hoàng Nam Express) — Giai đoạn 1  
**Phiên bản**: 1.0  
**Ngày**: 2026-07-21  
**Tác giả**: BA Antigravity AI  
**Trạng thái**: Draft / In Review  

Tài liệu này chứa tập hợp các User Story chi tiết phục vụ cho việc lập kế hoạch sprint (Sprint Planning) và phát triển chức năng cho dự án Hoàng Nam Express - Giai đoạn 1. Các Story được thiết kế theo tiêu chuẩn **INVEST** và đi kèm **Acceptance Criteria (AC)** dạng Checklist hoặc kịch bản **Given-When-Then**.

---

## Phân Hệ: Quản Lý Nhân Sự & Cài Đặt (Staff & Settings)

### US-STAFF-01 — Quản lý thông tin tài khoản nhân viên

**Story:**  
As an Administrator,  
I want to thêm mới, cập nhật và gán chức vụ/vai trò cho tài khoản nhân viên trên hệ thống,  
So that phân quyền chính xác chức năng làm việc cho từng nhân viên văn phòng, thủ kho, bưu tá và thủ quỹ.

**Background/Context:**  
Dự án cần một hệ thống quản lý tài khoản nội bộ tập trung. Các thông tin phòng ban, chức vụ được tích hợp trực tiếp vào màn hình thông tin nhân sự để tối ưu hóa trải nghiệm quản trị.

**Acceptance Criteria:**  
*   [ ] Có giao diện thêm mới/chỉnh sửa nhân sự gồm các trường: Họ tên, Số điện thoại (bắt buộc, duy nhất), Email, Phòng ban (Dropdown), Chức danh (Dropdown), Nhóm quyền vai trò (Dropdown), Trạng thái tài khoản (Hoạt động/Tạm khóa).
*   [ ] Khi tạo mới nhân sự thành công, hệ thống tự động lưu vào database, băm mật khẩu mặc định và gửi thông tin tài khoản (SĐT đăng nhập + mật khẩu khởi tạo) về SĐT nhân sự qua SMS Gateway.
*   [ ] Số điện thoại nhân viên nhập vào phải đúng định dạng số điện thoại Việt Nam (10 chữ số, bắt đầu bằng đầu số hợp lệ). Nếu trùng SĐT hiện tại, hệ thống báo lỗi "Số điện thoại đã tồn tại".
*   [ ] Quản trị viên có thể chuyển đổi trạng thái tài khoản của nhân viên từ "Hoạt động" sang "Tạm khóa" để ngay lập tức thu hồi quyền đăng nhập của nhân viên đó.

**Out of scope:**  
*   Lịch sử đăng nhập chi tiết của nhân viên (IP, thiết bị).
*   Chức năng tự đổi thông tin cá nhân của nhân viên (làm ở story sau).

**Dependencies:**  
*   Phải hoàn thành thiết kế DB bảng `users`, `roles`, `permissions` trước.

**Estimation:** 5 Story Points (Phức tạp trung bình do tích hợp SMS Gateway gửi mật khẩu).

---

### US-SETTING-01 — Cấu hình dịch vụ vận chuyển và phụ phí hàng cồng kềnh

**Story:**  
As an Administrator,  
I want to thiết lập danh mục dịch vụ vận chuyển chính, dịch vụ gia tăng và công thức quy đổi hàng cồng kềnh,  
So that hệ thống tự động áp dụng để tính toán cước phí chính xác khi nhân viên tạo vận đơn.

**Background/Context:**  
Hệ thống cần quản lý linh hoạt các loại hình dịch vụ giao nhận và có cơ chế tự động chuyển đổi kích thước hàng hóa cồng kềnh thành cân nặng tính cước theo chuẩn bưu chính Việt Nam.

**Acceptance Criteria:**  
*   [ ] Hỗ trợ cấu hình các gói dịch vụ vận chuyển chính: Tiêu chuẩn, Hỏa tốc.
*   [ ] Hỗ trợ cấu hình gói dịch vụ gia tăng: Bảo hiểm bưu gửi, Giao tận tay.
*   [ ] Hỗ trợ cấu hình nhóm hàng hóa: Hàng cồng kềnh, Dễ vỡ, Tài liệu, Chất lỏng.
*   [ ] Hệ thống áp dụng quy tắc quy đổi cồng kềnh tự động: Khối lượng quy đổi = `(Chiều dài x Chiều rộng x Chiều cao) (cm) / 6000`. Cân nặng tính cước cuối cùng là giá trị lớn nhất giữa Khối lượng thực tế và Khối lượng quy đổi.
*   [ ] Cho phép Admin thay đổi hệ số chia quy đổi (mặc định là 6000) và áp dụng lập tức cho các đơn tạo mới sau đó.

**Out of scope:**  
*   Cấu hình bảng cước phí động theo khoảng cách Google Maps (Giai đoạn 1 chỉ dùng bảng giá cước tĩnh theo Tỉnh/Vùng).

**Estimation:** 3 Story Points.

---

## Phân Hệ: Quản Lý Vận Đơn (Waybill Management)

### US-WAYBILL-01 — Tạo vận đơn thủ công tại quầy

**Story:**  
As a Counter Staff,  
I want to nhập thủ công thông tin người gửi, người nhận, thông số gói hàng và cước phí để tạo vận đơn mới,  
So that chính thức ghi nhận đơn hàng lên hệ thống và tiến hành nhận hàng từ người gửi.

**Background/Context:**  
Đây là giao diện làm việc chính của nhân viên quầy khi tiếp nhận hàng gửi trực tiếp. Yêu cầu giao diện nhanh, mượt mà và tự động hóa điền thông tin tối đa.

**Acceptance Criteria:**  
*   [ ] Khi nhập SĐT người gửi, hệ thống tự động tìm kiếm trong DB:
    *   Nếu có: Autofill họ tên, địa chỉ chi tiết và thông tin địa giới hành chính (Tỉnh/Huyện/Xã) của người gửi.
    *   Nếu không: Cho phép nhân viên nhập tay và hệ thống lưu thông tin khách hàng mới này.
*   [ ] Địa chỉ người nhận bắt buộc phải chọn qua dropdown phân cấp: Tỉnh/Thành phố -> Quận/Huyện -> Phường/Xã/Thị trấn để chuẩn hóa tuyến phát hàng.
*   [ ] Khi nhân viên nhập kích thước (Dài, Rộng, Cao cm) của hàng cồng kềnh, hệ thống hiển thị khối lượng quy đổi thời gian thực trên giao diện.
*   [ ] Sau khi bấm "Tính cước", hệ thống hiển thị bảng phân rã cước phí chi tiết (Cước chính, Phí bảo hiểm bưu gửi, Phụ phí hàng hóa, Tiền thu hộ COD và Tổng cước thực tế) dựa trên bảng giá áp dụng của khách hàng.
*   [ ] **Given** nhân viên bấm nút "Tạo vận đơn" và dữ liệu hợp lệ, **When** hệ thống lưu thông tin đơn, **Then** hệ thống thực hiện sao chép thông tin địa chỉ chi tiết người gửi và người nhận vào các cột dữ liệu tĩnh (`sender_name`, `sender_phone`, `sender_address_detail`...) trong bảng `bills` dưới dạng **Data Snapshot** để bảo lưu thông tin cũ khi khách hàng thay đổi thông tin cá nhân.
*   [ ] Trạng thái đơn sau khi tạo thành công mặc định là `Đã tiếp nhận tại bưu cục`.

**Dependencies:**  
*   Cơ sở dữ liệu danh mục hành chính tĩnh và bảng cước phí khách hàng đã hoạt động ổn định.

**Estimation:** 8 Story Points (Phức tạp lớn do yêu cầu data snapshot, logic tính cước đa dạng và autofill dữ liệu).

---

### US-WAYBILL-02 — In phiếu gửi bưu gửi khổ nhiệt từ trình duyệt

**Story:**  
As a Counter Staff,  
I want to xuất in trực tiếp phiếu gửi của vận đơn ra máy in nhiệt khổ A5 hoặc A6 từ trình duyệt,  
So that dán trực tiếp lên bưu gửi để bưu tá quét barcode khi đi trung chuyển hoặc đi phát.

**Acceptance Criteria:**  
*   [ ] Ngay sau khi tạo vận đơn thành công, hệ thống tự động mở popup hiển thị mẫu thiết kế phiếu gửi (hoặc có nút "In phiếu gửi" tại danh sách vận đơn).
*   [ ] Mẫu in phiếu gửi hiển thị rõ ràng: Mã vạch vận đơn (Barcode dạng Code 128), Mã QR code tra cứu nhanh, Thông tin người gửi (Tên, SĐT, Địa chỉ), Thông tin người nhận (Tên, SĐT, Địa chỉ), Chỉ dẫn giao hàng (Cho xem hàng, Không cho xem hàng...), Nội dung bưu gửi, Khối lượng tính cước, Tiền thu hộ COD và Tổng cước thanh toán.
*   [ ] Giao diện in ấn sử dụng HTML/CSS được căn chỉnh biên chính xác cho khổ giấy nhiệt A6 (100mm x 150mm) hoặc A5, đảm bảo không bị tràn trang hoặc mất lề khi in trực tiếp bằng lệnh in của trình duyệt (Ctrl+P / Window.print()).

**Mockup/Design Reference:**  
*   Sử dụng font chữ không chân (Arial/Inter), độ tương phản cao, mã vạch căn giữa chiếm tối thiểu 1/3 chiều rộng phiếu.

**Estimation:** 3 Story Points.

---

### US-WAYBILL-03 — Tìm kiếm hành trình vận đơn hỗ trợ tiếng Việt không dấu

**Story:**  
As a Counter Staff or Administrator,  
I want to tìm kiếm vận đơn theo số điện thoại hoặc họ tên người gửi/nhận bằng tiếng Việt không dấu,  
So that nhanh chóng tra cứu và giải đáp thắc mắc về hành trình đơn hàng cho khách hàng dưới 1 giây.

**Acceptance Criteria:**  
*   **Given** người dùng đang ở giao diện danh sách vận đơn, **When** người dùng nhập từ khóa tìm kiếm tiếng Việt không dấu (ví dụ: "Nguyen Van A" hoặc "Lâm Đồng") vào ô tìm kiếm tên/địa chỉ, **Then** hệ thống truy vấn và hiển thị kết quả khớp với cả tiếng Việt có dấu tương ứng (ví dụ: hiển thị cả "Nguyễn Văn A" và "Lâm Đồng").
*   [ ] Bộ lọc hỗ trợ lọc đơn hàng theo: Mã vận đơn, Khoảng thời gian gửi, Bưu cục gửi/nhận, Trạng thái hành trình đơn hàng.
*   [ ] Thời gian phản hồi của truy vấn tìm kiếm không dấu phải nhỏ hơn **1 giây** đối với cơ sở dữ liệu có trên 100.000 bản ghi vận đơn.

**Technical Notes:**  
*   Sử dụng index `GIN` trên cột địa chỉ và họ tên kết hợp với extension `pg_trgm` của PostgreSQL và viết hàm chuyển đổi ký tự tiếng Việt có dấu về không dấu ở mức DB để tối ưu hóa hiệu năng câu lệnh SELECT.

**Estimation:** 5 Story Points (Phục vụ kỹ thuật tối ưu hóa PostgreSQL).

---

## Phân Hệ: Nghiệp Vụ Kho & Chuyển Xe (Warehouse & Fleet)

### US-WAREHOUSE-01 — Quét xuất kho trung chuyển vận đơn lẻ

**Story:**  
As a Warehouse Keeper,  
I want to quét mã vạch các vận đơn lẻ để xuất kho trung chuyển đi bưu cục/kho đích,  
So that thực hiện xuất kho trung chuyển nhanh chóng và an toàn mà không cần đóng bao.

**Acceptance Criteria:**  
*   [ ] Có màn hình chức năng "Xuất kho trung chuyển đơn lẻ". Người dùng chọn Kho/Bưu cục đích cần chuyển đến.
*   [ ] Hệ thống tạo một bảng kê xuất kho (Manifest ID) ở trạng thái "Đang xuất".
*   [ ] Người dùng đặt con trỏ vào ô quét mã và sử dụng đầu đọc quét barcode đơn lẻ. Hệ thống kiểm tra:
    *   Nếu vận đơn hợp lệ (đang tồn tại ở kho bưu cục thao tác): Thêm vận đơn vào danh sách xuất kho, phát âm thanh báo thành công.
    *   Nếu vận đơn không hợp lệ: Phát âm thanh cảnh báo lỗi và hiển thị toast thông báo lỗi.
*   [ ] Sau khi quét xong toàn bộ, người dùng bấm "Xác nhận xuất kho". Hệ thống cập nhật trạng thái của tất cả vận đơn đã quét sang "Đang trung chuyển" và lưu vết lịch trình.
*   [ ] Hệ thống hỗ trợ in Bảng kê xuất kho (Outbound Manifest) chứa: Mã bảng kê (QR/Barcode), Bưu cục nguồn, Bưu cục đích, Tổng số vận đơn, Tổng khối lượng, và danh sách chi tiết các mã vận đơn bên trong.

**Estimation:** 4 Story Points.

---

## Phân Hệ: Quản Lý Thu Tiền COD (COD Cash Control)

### US-COD-01 — Bưu tá lập bảng kê nộp tiền mặt COD cuối ngày

**Story:**  
As a Shipper/Bưu tá,  
I want to chọn danh sách các đơn đã giao thành công trong ngày để lập bảng kê nộp tiền mặt COD gửi cho thủ quỹ,  
So that báo cáo chính xác dòng tiền thu hộ thực tế và làm thủ tục bàn giao tiền mặt nộp quỹ bưu cục.

**Acceptance Criteria:**  
*   [ ] Bưu tá có màn hình "Bàn giao COD cuối ngày" hiển thị danh sách các đơn hàng có trạng thái "Giao thành công" do mình phụ trách phát trong ngày mà chưa được đối soát COD.
*   [ ] Bưu tá chọn các đơn thực tế đã thu được tiền mặt (hỗ trợ nút chọn tất cả) và bấm "Tạo bảng kê nộp tiền".
*   [ ] Hệ thống tự động tính tổng số tiền COD của các đơn đã chọn và tạo một mã bảng kê nộp tiền ở trạng thái "Chờ thủ quỹ duyệt".
*   [ ] Sau khi tạo bảng kê, bưu tá không thể chỉnh sửa thông tin bảng kê hay tự ý đổi trạng thái của các vận đơn nằm trong bảng kê đó nữa (trừ khi thủ quỹ từ chối duyệt).

**Estimation:** 3 Story Points.

---

### US-COD-02 — Thủ quỹ bưu cục đối soát và duyệt bảng kê tiền mặt COD bưu tá nộp về

**Story:**  
As a Cashier/Thủ quỹ bưu cục,  
I want to kiểm đếm tiền mặt bưu tá nộp về và bấm duyệt bảng kê nộp tiền COD trên hệ thống,  
So that ghi nhận dòng tiền COD vào két sắt bưu cục và giải phóng công nợ tiền mặt trong ngày cho bưu tá.

**Background/Context:**  
Đây là bước chốt dòng tiền mặt vô cùng quan trọng cuối ngày tại bưu cục nhằm phát hiện ngay lập tức các sai lệch thất thoát tiền mặt.

**Acceptance Criteria:**  
*   [ ] Thủ quỹ truy cập danh sách "Duyệt bảng kê COD", tìm kiếm theo tên bưu tá hoặc mã bảng kê để mở chi tiết bảng kê ở trạng thái "Chờ duyệt".
*   [ ] Màn hình chi tiết hiển thị: Danh sách vận đơn, Số tiền COD khai báo của từng đơn và Tổng tiền bưu tá nộp về.
*   [ ] **Scenario: Thủ quỹ duyệt bảng kê khớp số liệu:**
    *   Given thủ quỹ đếm tiền mặt thực nhận từ bưu tá khớp hoàn toàn với tổng tiền khai báo trên bảng kê.
    *   When thủ quỹ nhập số tiền thực nhận và bấm nút "Xác nhận & Duyệt bảng kê".
    *   Then trạng thái bảng kê đổi thành "Đã duyệt - Hoàn tất đối soát", trạng thái các vận đơn liên quan cập nhật sang "Đã đối soát COD nội bộ", và số dư két sắt bưu cục tăng tương ứng.
*   **Scenario: Phát hiện lệch tiền mặt (thừa hoặc thiếu):**
    *   Given tiền mặt bưu tá nộp thực tế bị thiếu hoặc thừa so với tổng tiền khai báo trên bảng kê.
    *   When thủ quỹ nhập số tiền thực nhận (báo lệch khác 0) và bấm nút "Từ chối duyệt".
    *   Then hệ thống yêu cầu nhập lý do từ chối và chuyển trạng thái bảng kê thành "Từ chối - Lệch tiền mặt", ghi nhận số tiền chênh lệch vào log của bảng kê để bưu tá giải trình. Trạng thái các vận đơn lẻ giữ nguyên chờ đối soát lại.

**Estimation:** 5 Story Points (Phức tạp do có luồng xử lý lệch tiền mặt, ghi nhận transaction quỹ két sắt bưu cục).

---
---

# Giai đoạn 2 (Deferred User Stories)

## Phân Hệ: Nghiệp Vụ Kho (Warehouse Bagging)

### US-WAREHOUSE-01 — Quét đóng bao trung chuyển bưu chính

**Story:**  
As a Warehouse Keeper,  
I want to quét mã vạch gom nhiều vận đơn lẻ đóng vào bao hàng tải lớn và in bảng kê bao (Manifest),  
So that thực hiện xuất kho trung chuyển số lượng lớn đơn hàng cùng lúc một cách nhanh chóng và an toàn.

**Acceptance Criteria:**  
*   [ ] Có màn hình chức năng "Đóng bao trung chuyển". Người dùng chọn Kho/Bưu cục đích cần chuyển đến.
*   [ ] Hệ thống tạo mã bao hàng tải lớn (Bag ID) ở trạng thái "Đang đóng".
*   [ ] Người dùng đặt con trỏ vào ô quét mã và sử dụng đầu đọc quét barcode đơn lẻ. Hệ thống kiểm tra:
    *   Nếu đơn hàng hợp lệ (trạng thái là đang tồn ở kho bưu cục thao tác): Thêm đơn hàng vào danh sách bao, phát âm thanh báo thành công.
    *   Nếu đơn hàng không hợp lệ (đang ở trạng thái khác hoặc thuộc kho khác): Phát âm thanh cảnh báo lỗi, không thêm vào bao hàng và hiển thị toast thông báo lỗi.
*   [ ] Sau khi quét xong toàn bộ, người dùng bấm "Hoàn tất đóng bao". Hệ thống đổi trạng thái bao hàng sang "Đã niêm phong". Trạng thái của toàn bộ đơn hàng lẻ bên trong tự động cập nhật liên kết khóa ngoại với mã bao hàng tải và chuyển lịch trình sang trạng thái của bao.
*   [ ] Hệ thống hỗ trợ in Bảng kê bao hàng (Manifest) chứa: Mã vạch bao hàng, Tổng số đơn lẻ, Tổng khối lượng bao (gồm cả vỏ bao tải), và danh sách chi tiết các mã đơn lẻ bên trong bao hàng.

**Estimation:** 5 Story Points.
