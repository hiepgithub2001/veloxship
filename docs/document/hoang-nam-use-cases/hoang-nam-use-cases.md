# Use Case Specifications
**Dự án**: Hệ thống Quản lý Chuyển phát nhanh Hoàng Nam (Hoàng Nam Express) — Giai đoạn 1 & Giai đoạn 2  
**Phiên bản**: 2.0  
**Ngày**: 2026-07-21  
**Tác giả**: BA Antigravity AI  
**Trạng thái**: Draft / In Review  

Tài liệu này đặc tả chi tiết (Fully Dressed Use Cases) cho tất cả các quy trình vận hành cốt lõi và quan trọng nhất của hệ thống Hoàng Nam Express:
*   **Giai đoạn 1 (Hiện tại)**:
    1.  **UC-WAYBILL-01 (Tương ứng UC-WEB-19)**: Tạo vận đơn thủ công và In phiếu gửi.
    2.  **UC-TRIP-01 (Tương ứng UC-WEB-36)**: Điều phối chuyến xe & Bốc xếp vận đơn lên xe (Gắn hàng với Trip).
    3.  **UC-COD-01 (Tương ứng UC-WEB-38)**: Bưu tá lập bảng kê nộp tiền mặt COD cuối ngày (Thu tiền).
    4.  **UC-COD-03 (Tương ứng UC-WEB-39)**: Thủ quỹ bưu cục xác nhận thu tiền COD bưu tá nộp về.
    5.  **UC-WAREHOUSE-01 (Tương ứng UC-WEB-28)**: Quét mã vạch nhập kho bưu cục (Inbound Scan).
    6.  **UC-WAREHOUSE-05 (Tương ứng UC-WEB-32)**: Quét xuất kho bàn giao bưu tá đi phát (Last-mile Outbound).
*   **Giai đoạn 2 (Trì hoãn)**:
    1.  **UC-WAREHOUSE-03 (Tương ứng UC-WEB-30)**: Đóng bao trung chuyển (Bagging & Manifest).

---

## Sơ đồ Tổng Quan Hệ Thống Use Case (Overview Use Case Diagram)

Dưới đây là sơ đồ Use Case thể hiện tổng thể các tác nhân (Actors) và mối quan hệ với toàn bộ các phân hệ chức năng vận hành của hệ thống Hoàng Nam Express:

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'primaryColor': '#ffffff', 'edgeColor': '#333333' }}}%%
flowchart LR
    subgraph Actors_Left ["Tác nhân chính (Primary Actors)"]
        direction TB
        CounterStaff["👤 Counter Staff<br>(Nhân viên quầy)"]
        WarehouseKeeper["👤 Warehouse Keeper<br>(Nhân viên kho)"]
        Cashier["👤 Cashier<br>(Thủ quỹ bưu cục)"]
        Shipper["👤 Shipper / Driver<br>(Bưu tá / Tài xế)"]
    end

    subgraph System ["Hệ thống Hoàng Nam Express"]
        direction TB
        subgraph Waybill_Module ["Phân hệ Vận đơn"]
            UC1(["UC-WAYBILL-01<br>Tạo vận đơn thủ công & In phiếu gửi"])
        end

        subgraph Fleet_Module ["Phân hệ Đội xe & Chuyển xe"]
            UC_Trip(["UC-TRIP-01<br>Điều phối chuyến xe & Gắn hàng lên Trip"])
        end

        subgraph Warehouse_Module ["Phân hệ Quản lý Kho"]
            UC_WH1(["UC-WAREHOUSE-01<br>Quét mã vạch nhập kho bưu cục"])
            UC_WH5(["UC-WAREHOUSE-05<br>Quét xuất kho giao hàng bưu tá"])
            UC2(["[GĐ2] UC-WAREHOUSE-03<br>Đóng bao trung chuyển (Bagging)"])
        end

        subgraph COD_Module ["Phân hệ Quản lý Tiền COD"]
            UC_COD1(["UC-COD-01<br>Bưu tá lập bảng kê nộp tiền COD"])
            UC3(["UC-COD-03<br>Thủ quỹ xác nhận thu tiền COD"])
        end
    end

    subgraph Actors_Right ["Tác nhân phụ (Supporting Actors)"]
        direction TB
        Printer["🖨️ Máy in nhiệt/A6"]
        Database[("🗄️ PostgreSQL Database")]
    end

    %% Connections
    CounterStaff --> UC1
    WarehouseKeeper --> UC_Trip
    WarehouseKeeper --> UC_WH1
    WarehouseKeeper --> UC_WH5
    WarehouseKeeper -.->|"[GĐ2]"| UC2
    Shipper --> UC_COD1
    Cashier --> UC3

    UC1 --> Printer
    UC_Trip --> Database
    UC_WH1 --> Database
    UC_WH5 --> Printer
    UC2 -.->|"[GĐ2]"| Printer
    UC_COD1 --> Cashier
    UC3 --> Database

    %% Styling
    classDef actor fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1;
    classDef usecase fill:#ecfdf5,stroke:#059669,stroke-width:2px,color:#065f46;
    classDef deferred fill:#f1f5f9,stroke:#94a3b8,stroke-width:1.5px,color:#64748b,stroke-dasharray: 3 3;

    class CounterStaff,WarehouseKeeper,Cashier,Shipper,Printer actor;
    class UC1,UC_Trip,UC_WH1,UC_WH5,UC_COD1,UC3 usecase;
    class UC2 deferred;
    
    style Actors_Left fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style System fill:#f1f5f9,stroke:#94a3b8,stroke-width:2px;
    style Actors_Right fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style Waybill_Module fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
    style Fleet_Module fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
    style Warehouse_Module fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
    style COD_Module fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
```

---
---

## UC-WAYBILL-01: Tạo Vận Đơn Thủ Công và In Phiếu Gửi

### Thông tin cơ bản
*   **Mã Use Case**: UC-WAYBILL-01
*   **Tên Use Case**: Tạo vận đơn thủ công và In phiếu gửi
*   **Actor chính**: Counter Staff (Nhân viên quầy bưu cục)
*   **Actor phụ**: Máy in nhiệt bưu cục, Cơ sở dữ liệu PostgreSQL
*   **Mô tả tóm tắt**: Nhân viên quầy nhập thông tin chi tiết về người gửi, người nhận, thông số kiện hàng (khối lượng, thể tích), gói dịch vụ sử dụng và số tiền thu hộ COD. Hệ thống tự động tính cước và sinh mã vận đơn. Nhân viên in phiếu gửi khổ nhiệt (A5/A6) để dán lên kiện hàng.
*   **Trigger**: Nhân viên bấm nút "Tạo Vận Đơn Mới" trên màn hình quản lý vận đơn.
*   **Tần suất thực hiện**: Rất cao (~3,000 lần/ngày trên toàn hệ thống).

### Sơ đồ Use Case Chi Tiết (Detailed Use Case Diagram)

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'primaryColor': '#ffffff', 'edgeColor': '#333333' }}}%%
flowchart LR
    subgraph Primary_Actors ["Tác nhân chính"]
        CounterStaff["👤 Counter Staff<br>(Nhân viên quầy)"]
    end

    subgraph UC_Boundary ["Phạm vi UC-WAYBILL-01: Tạo Vận Đơn Thủ Công & In Phiếu Gửi"]
        direction TB
        MainUC(["UC-WAYBILL-01<br>Tạo vận đơn thủ công & In phiếu gửi"])
        
        subgraph Includes ["Các luồng bắt buộc (<<include>>)"]
            UC_Autofill(["Autofill thông tin người gửi từ DB"])
            UC_ValidateAddr(["Validate địa giới hành chính 3 cấp"])
            UC_CalcFee(["Tính cước quy đổi cồng kềnh Max(W_real, W_dim)"])
            UC_Snapshot(["Khóa Data Snapshot địa chỉ & Sinh mã đơn"])
            UC_Print(["Render & In phiếu gửi A6"])
        end

        subgraph Extensions ["Các luồng mở rộng / Ngoại lệ (<<extend>>)"]
            UC_A1(["[A1] Tạo tạm khách hàng gửi mới"])
            UC_A2(["[A2] Điều chỉnh thông số & Tính lại cước"])
            UC_E1(["[E1] Cảnh báo cước phí âm / Không có tuyến"])
            UC_E2(["[E2] Rollback transaction khi lỗi DB"])
        end

        MainUC -.->|"<<include>>"| UC_Autofill
        MainUC -.->|"<<include>>"| UC_ValidateAddr
        MainUC -.->|"<<include>>"| UC_CalcFee
        MainUC -.->|"<<include>>"| UC_Snapshot
        MainUC -.->|"<<include>>"| UC_Print

        UC_A1 -.->|"<<extend>>"| UC_Autofill
        UC_A2 -.->|"<<extend>>"| UC_CalcFee
        UC_E1 -.->|"<<extend>>"| UC_CalcFee
        UC_E2 -.->|"<<extend>>"| UC_Snapshot
    end

    subgraph Secondary_Actors ["Tác nhân phụ / Hệ thống hỗ trợ"]
        Printer["🖨️ Máy in nhiệt A6"]
        Database[("🗄️ PostgreSQL Database")]
    end

    CounterStaff --> MainUC
    UC_Print --> Printer
    UC_Snapshot --> Database
    UC_Autofill --> Database

    classDef actor fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1;
    classDef mainuc fill:#d1fae5,stroke:#059669,stroke-width:2.5px,color:#065f46;
    classDef inc fill:#fffbeb,stroke:#d97706,stroke-width:1.5px,color:#92400e;
    classDef ext fill:#fef2f2,stroke:#dc2626,stroke-width:1.5px,color:#991b1b;
    classDef db fill:#f3e8ff,stroke:#9333ea,stroke-width:1.5px,color:#6b21a8;

    class CounterStaff,Printer actor;
    class Database db;
    class MainUC mainuc;
    class UC_Autofill,UC_ValidateAddr,UC_CalcFee,UC_Snapshot,UC_Print inc;
    class UC_A1,UC_A2,UC_E1,UC_E2 ext;

    style Primary_Actors fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style UC_Boundary fill:#f1f5f9,stroke:#94a3b8,stroke-width:2px;
    style Secondary_Actors fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style Includes fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
    style Extensions fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
```

### Điều kiện tiền đề (Preconditions)
1.  Nhân viên quầy đã đăng nhập thành công vào Web Portal bưu cục.
2.  Tài khoản nhân viên được cấp quyền tạo vận đơn (`bill:create`).
3.  Danh mục địa giới hành chính tĩnh 3 cấp Việt Nam đã được import đầy đủ lên hệ thống.
4.  Cấu hình bảng giá cước mặc định hoặc bảng giá cước của khách hàng đã tồn tại.

### Điều kiện hậu quả (Postconditions)
*   **Thành công (Success)**:
    1.  Vận đơn được tạo thành công trên hệ thống với mã đơn duy nhất (VD: HN123456789VN) và trạng thái ban đầu là "Đã tiếp nhận tại bưu cục".
    2.  Dữ liệu người gửi/người nhận được khóa cứng dưới dạng **Data Snapshot** trong bảng vận đơn.
    3.  Phiếu gửi (PDF/HTML) chứa đầy đủ barcode/QR code và thông tin thanh toán được hiển thị để in ấn.
*   **Thất bại (Failure)**:
    1.  Không có vận đơn nào được lưu vào database.
    2.  Hiển thị thông báo lỗi cụ thể để nhân viên xử lý thông tin nhập vào.

---

### TIẾN TRÌNH THỰC HIỆN CHÍNH (MAIN FLOW)

| Bước | Actor | Hệ thống |
| :--- | :--- | :--- |
| **1** | Nhân viên quầy nhập số điện thoại người gửi. | Hệ thống kiểm tra số điện thoại trong danh bạ khách hàng. Nếu SĐT đã tồn tại, tự động điền (Autofill) họ tên, địa chỉ chi tiết, khu vực Tỉnh/Huyện/Xã của khách hàng gửi và hiển thị Nhóm khách hàng (ví dụ: Khách shop). |
| **2** | Nhân viên nhập thông tin người nhận (Họ tên, SĐT, Địa chỉ chi tiết) và chọn địa giới hành chính người nhận (Tỉnh/Thành -> Quận/Huyện -> Phường/Xã từ dropdown liên kết). | Hệ thống hỗ trợ tìm kiếm nhanh khu vực hành chính và khóa cấu trúc địa chỉ tương ứng. |
| **3** | Nhân viên nhập thông số hàng hóa: Khối lượng thực tế (kg), kích thước (Dài x Rộng x Cao cm), Giá trị khai báo bảo hiểm (VNĐ) và Số tiền COD thu hộ (VNĐ). | Hệ thống ghi nhận dữ liệu hàng hóa. |
| **4** | Nhân viên chọn Gói dịch vụ chính (Tiêu chuẩn/Hỏa tốc) và chọn hình thức trả cước (Người gửi trả ngay/Người gửi ký nợ/Người nhận trả). | Hệ thống tự động xác định bảng giá áp dụng cho khách hàng gửi (giá riêng của shop hoặc giá mặc định của nhóm khách lẻ). |
| **5** | Nhân viên bấm nút "Tính cước". | Hệ thống kiểm tra khối lượng quy đổi từ kích thước thể tích. Tính cước chính, cước bảo hiểm bưu gửi (nếu có), phụ phí hàng đặc thù (nếu có), cộng thêm tiền COD thu hộ và hiển thị bảng chi tiết tổng cước phí trên màn hình. |
| **6** | Nhân viên xác nhận thông tin cước phí với người gửi và bấm "Tạo Đơn & In". | Hệ thống kiểm tra hợp lệ dữ liệu. Thực hiện lưu thông tin vận đơn vào cơ sở dữ liệu, sinh mã đơn duy nhất, đóng băng dữ liệu địa chỉ gửi nhận (**Data Snapshot**) và trả về mã HTML in nhiệt khổ giấy A6. |
| **7** | Nhân viên bấm nút "In" trên hộp thoại in của trình duyệt. | Máy in nhiệt thực hiện in phiếu gửi. Use case kết thúc. |

---

### TIẾN TRÌNH THAY THẾ (ALTERNATIVE FLOWS)

*   **A1: Khách hàng gửi mới chưa có trong danh mục (tại Bước 1)**
    *   1a. Hệ thống thông báo SĐT người gửi chưa có trong hệ thống.
    *   1b. Nhân viên nhập thủ công họ tên người gửi, địa chỉ chi tiết và chọn địa giới hành chính (Tỉnh/Huyện/Xã).
    *   1c. Hệ thống lưu tạm thông tin khách hàng gửi mới để phục vụ autofill cho các lần tạo đơn sau. Tiếp tục bước 2.

*   **A2: Điều chỉnh thông số hàng hóa sau khi tính cước (tại Bước 5)**
    *   5a. Nhân viên thay đổi cân nặng hoặc dịch vụ gia tăng.
    *   5b. Nhân viên bấm lại nút "Tính cước".
    *   5c. Hệ thống cập nhật tính toán lại bảng cước phí mới. Tiếp tục bước 6.

---

### TIẾN TRÌNH NGOẠI LỆ (EXCEPTION FLOWS)

*   **E1: Lỗi tính cước do không tìm thấy tuyến vận chuyển hoặc cước phí bị âm (tại Bước 5)**
    *   5a. Hệ thống phát hiện cước tính ra bị âm hoặc địa chỉ gửi nhận không nằm trong bảng cước cấu hình.
    *   5b. Hệ thống hiển thị cảnh báo: "Lỗi tính toán cước phí. Vui lòng kiểm tra lại cấu hình bảng giá của khách hàng cho tuyến gửi nhận này hoặc liên hệ Admin".
    *   5c. Hệ thống không cho phép lưu đơn hàng. Nhân viên kiểm tra thông tin hoặc hủy giao dịch.

*   **E2: Trùng mã vận đơn hoặc lỗi lưu DB (tại Bước 6)**
    *   6a. Quá trình lưu đơn vào DB bị ngắt quãng hoặc trùng mã vận đơn do truy cập đồng thời.
    *   6b. Hệ thống tự động rollback transaction database, ghi nhật ký lỗi kỹ thuật.
    *   6c. Hiển thị thông báo: "Lỗi hệ thống khi tạo đơn hàng. Vui lòng thử lại".

---

### CÁC QUY TẮC NGHIỆP VỤ LIÊN QUAN (BUSINESS RULES)
*   **BR-01 (Công thức cước cồng kềnh)**: Khối lượng tính cước = Max (Khối lượng thực tế, Khối lượng quy đổi). Khối lượng quy đổi = `(Dài x Rộng x Cao) / 6000` (đơn vị cm, kg).
*   **BR-02 (Data Snapshot)**: Bảng `bills` lưu trực tiếp các trường: `sender_name`, `sender_phone`, `sender_province`, `sender_district`, `sender_ward`, `sender_address_detail` thay vì liên kết khóa ngoại động để đảm bảo dữ liệu đơn hàng cũ không bị thay đổi khi danh bạ khách hàng cập nhật.
*   **BR-03 (Ràng buộc cước phí DB)**: Tổng cước thực thu = Cước chính + Phí bảo hiểm + Phí phụ thu dịch vụ. Ràng buộc CHECK ở DB bắt buộc tổng này không được âm.

---
---

## UC-TRIP-01: Điều Phối Chuyến Xe & Bốc Xếp Vận Đơn Lên Xe (Gắn Hàng Với Trip)

### Thông tin cơ bản
*   **Mã Use Case**: UC-TRIP-01 (Tương ứng UC-WEB-36)
*   **Tên Use Case**: Điều phối chuyến xe và Bốc xếp vận đơn lên xe trung chuyển (Gắn hàng với Trip)
*   **Actor chính**: Warehouse Keeper / Dispatcher (Nhân viên kho / Điều phối xe)
*   **Actor phụ**: Tài xế xe tải, Cơ sở dữ liệu PostgreSQL
*   **Mô tả tóm tắt**: Nhân viên điều phối chọn kho/bưu cục đích, gán xe tải và tài xế để tạo chuyến xe trung chuyển mới. Sau đó, nhân viên đặt con trỏ vào ô quét mã và sử dụng máy quét barcode quét từng vận đơn lẻ tại bưu cục hiện tại để bốc xếp trực tiếp lên chuyến xe (gắn vận đơn với Trip ID qua bảng `trip_bills`). Kiểm tra giới hạn tải trọng/thể tích thùng xe và xác nhận xuất bến chuyến xe đi bưu cục tiếp theo.
*   **Trigger**: Nhân viên điều phối chọn chức năng "Tạo chuyến xe mới" trên phân hệ Quản lý chuyển xe.
*   **Tần suất thực hiện**: Trung bình (~50 lần/ngày trên toàn hệ thống).

### Sơ đồ Use Case Chi Tiết (Detailed Use Case Diagram)

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'primaryColor': '#ffffff', 'edgeColor': '#333333' }}}%%
flowchart LR
    subgraph Primary_Actors ["Tác nhân chính"]
        Dispatcher["👤 Dispatcher / Warehouse Keeper<br>(Điều phối xe / Thủ kho)"]
    end

    subgraph UC_Boundary ["Phạm vi UC-TRIP-01: Điều Phối Chuyến Xe & Gắn Hàng Với Trip"]
        direction TB
        MainUC(["UC-TRIP-01<br>Điều phối chuyến xe & Gắn hàng với Trip"])
        
        subgraph Includes ["Các luồng bắt buộc (<<include>>)"]
            UC_CreateTrip(["Khởi tạo chuyến xe mới & Gán xe/Tài xế"])
            UC_ScanBillTrip(["Quét gán mã vận đơn lẻ vào Trip (trip_bills)"])
            UC_CheckCap(["Kiểm tra tổng tải trọng & Thể tích thùng xe"])
            UC_DepartTrip(["Xác nhận xuất bến chuyến xe (status='in_transit')"])
        end

        subgraph Extensions ["Các luồng mở rộng / Ngoại lệ (<<extend>>)"]
            UC_RemoveBill(["[A1] Bốc dỡ / Loại bỏ vận đơn khỏi chuyến xe"])
            UC_E1(["[E1] Cảnh báo quá tải trọng/thể tích thùng xe"])
            UC_E2(["[E2] Từ chối vận đơn không hợp lệ / không có tại kho"])
        end

        MainUC -.->|"<<include>>"| UC_CreateTrip
        MainUC -.->|"<<include>>"| UC_ScanBillTrip
        MainUC -.->|"<<include>>"| UC_CheckCap
        MainUC -.->|"<<include>>"| UC_DepartTrip

        UC_RemoveBill -.->|"<<extend>>"| UC_ScanBillTrip
        UC_E1 -.->|"<<extend>>"| UC_CheckCap
        UC_E2 -.->|"<<extend>>"| UC_ScanBillTrip
    end

    subgraph Secondary_Actors ["Tác nhân phụ / Hệ thống hỗ trợ"]
        Driver["👤 Driver / Tài xế xe tải"]
        Scanner["📷 Máy quét Barcode"]
        Database[("🗄️ PostgreSQL Database")]
    end

    Dispatcher --> MainUC
    Scanner --> UC_ScanBillTrip
    UC_DepartTrip --> Driver
    UC_DepartTrip --> Database

    classDef actor fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1;
    classDef mainuc fill:#d1fae5,stroke:#059669,stroke-width:2.5px,color:#065f46;
    classDef inc fill:#fffbeb,stroke:#d97706,stroke-width:1.5px,color:#92400e;
    classDef ext fill:#fef2f2,stroke:#dc2626,stroke-width:1.5px,color:#991b1b;
    classDef db fill:#f3e8ff,stroke:#9333ea,stroke-width:1.5px,color:#6b21a8;

    class Dispatcher,Driver,Scanner actor;
    class Database db;
    class MainUC mainuc;
    class UC_CreateTrip,UC_ScanBillTrip,UC_CheckCap,UC_DepartTrip inc;
    class UC_RemoveBill,UC_E1,UC_E2 ext;

    style Primary_Actors fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style UC_Boundary fill:#f1f5f9,stroke:#94a3b8,stroke-width:2px;
    style Secondary_Actors fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style Includes fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
    style Extensions fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
```

### Điều kiện tiền đề (Preconditions)
1.  Nhân viên đã đăng nhập thành công vào Web Portal bưu cục và có quyền điều phối chuyến xe (`trip:create`).
2.  Xe tải trung chuyển và Tài xế đã được cấu hình trạng thái sẵn sàng (`active`) trên hệ thống.
3.  Các vận đơn cần bốc xếp đang ở kho bưu cục thao tác với trạng thái "Đang ở kho bưu cục".

### Điều kiện hậu quả (Postconditions)
*   **Thành công (Success)**:
    1.  Chuyến xe (`trips`) được tạo thành công với mã chuyến duy nhất (VD: `TRIP2107260012`) ở trạng thái "Đang vận chuyển" (`in_transit`).
    2.  Các vận đơn lẻ được liên kết với Trip ID trong bảng `trip_bills`.
    3.  Trạng thái tất cả vận đơn thuộc chuyến xe tự động đổi sang "Đang trung chuyển" và ghi nhận nhật ký lịch trình xuất bến.
*   **Thất bại (Failure)**:
    1.  Chuyến xe không được lưu. Dữ liệu vận đơn tại bưu cục không thay đổi.

---

### TIẾN TRÌNH THỰC HIỆN CHÍNH (MAIN FLOW)

| Bước | Actor | Hệ thống |
| :--- | :--- | :--- |
| **1** | Nhân viên nhập tên chuyến xe, chọn Kho/Bưu cục đích đến, chọn Xe tải (biển số) và Tài xế phụ trách từ dropdown list. | Hệ thống sinh mã chuyến xe tạm thời, hiển thị thông số tải trọng tối đa (kg) và thể tích tối đa ($m^3$) của xe tải được chọn. |
| **2** | Nhân viên đặt con trỏ vào ô quét và dùng đầu đọc quét barcode mã vận đơn lẻ bốc xếp lên xe. | Hệ thống nhận dạng mã vận đơn, kiểm tra vận đơn đang thuộc kho hiện tại, phát âm thanh báo thành công và gán vận đơn vào chuyến xe. |
| **3** | Hệ thống tự động tính lại tổng số vận đơn, tổng khối lượng (kg) và tổng thể tích ($m^3$) của tất cả vận đơn đã gán lên xe. | Hiển thị tiến trình nạp hàng trên thanh chỉ số dung lượng xe tải (phần trăm tải trọng và thể tích đã sử dụng). |
| **4** | Nhân viên quét xong tất cả vận đơn và bấm "Xuất Bến Chuyến Xe". | Hệ thống kiểm tra điều kiện xuất bến, cập nhật trạng thái chuyến xe sang `in_transit`. Đổi trạng thái lịch trình của toàn bộ vận đơn thuộc chuyến xe sang "Đang trung chuyển". |
| **5** | Hệ thống hiển thị thông báo xuất bến thành công và xuất Bảng kê bốc xếp chuyến xe (Trip Manifest). | Use case kết thúc. |

---

### TIẾN TRÌNH THAY THẾ (ALTERNATIVE FLOWS)

*   **A1: Bốc dỡ / Loại bỏ vận đơn lẻ khỏi chuyến xe (tại Bước 2)**
    *   2a. Nhân viên bấm nút "Hủy gán" tại một dòng vận đơn trên lưới danh sách bốc xếp.
    *   2b. Hệ thống xóa liên kết vận đơn khỏi chuyến xe tạm thời và tính toán lại tổng tải trọng của xe. Continue bước 3.

---

### TIẾN TRÌNH NGOẠI LỆ (EXCEPTION FLOWS)

*   **E1: Quá tải trọng hoặc thể tích xe tải (tại Bước 2)**
    *   2a. Quét thêm 1 vận đơn khiến tổng khối lượng vượt `max_weight_kg` hoặc tổng thể tích vượt `max_volume_m3` của xe tải.
    *   2b. Hệ thống phát âm thanh cảnh báo lỗi (tít còi dài) và hiển thị modal: "Quá tải trọng/thể tích xe tải! Không thể thêm đơn này vào chuyến xe hiện tại".
    *   2c. Vận đơn đó không được thêm vào chuyến xe. Nhân viên điều phối xe khác hoặc giữ lại đơn ở ca sau.

*   **E2: Vận đơn không hợp lệ hoặc không nằm ở kho bưu cục (tại Bước 2)**
    *   2a. Nhân viên quét vận đơn đang ở bưu cục khác hoặc đã phát thành công/đã hủy.
    *   2b. Hệ thống báo lỗi: "Vận đơn X không tồn tại ở bưu cục hiện tại". Vận đơn không được đưa vào danh sách bốc xếp.

---
---

## UC-COD-01: Bưu Tá Lập Bảng Kê Nộp Tiền Mặt COD Cuối Ngày (Thu Tiền)

### Thông tin cơ bản
*   **Mã Use Case**: UC-COD-01 (Tương ứng UC-WEB-38)
*   **Tên Use Case**: Bưu tá lập bảng kê nộp tiền mặt COD cuối ngày (Thu tiền)
*   **Actor chính**: Shipper / Driver (Bưu tá giao hàng)
*   **Actor phụ**: Cashier (Thủ quỹ bưu cục - Nhận nộp tiền), Cơ sở dữ liệu PostgreSQL
*   **Mô tả tóm tắt**: Cuối ca làm việc giao hàng, bưu tá mở giao diện nộp tiền mặt COD, hệ thống hiển thị danh sách tất cả các vận đơn có thu tiền hộ COD đã cập nhật trạng thái "Giao thành công" do bưu tá phụ trách mà chưa đối soát. Bưu tá chọn các đơn thực tế đã thu tiền mặt, hệ thống tự động tính tổng tiền mặt COD cần nộp, tạo mã Bảng kê nộp tiền (ví dụ: `COD2107260088`) ở trạng thái "Chờ thủ quỹ duyệt" và mang cọc tiền mặt đến nộp cho thủ quỹ.
*   **Trigger**: Bưu tá bấm nút "Lập bảng kê nộp tiền COD cuối ngày" trên Web Portal/App bưu cục.
*   **Tần suất thực hiện**: Hàng ngày (Cuối ca làm việc từ 17:00 - 21:00).

### Sơ đồ Use Case Chi Tiết (Detailed Use Case Diagram)

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'primaryColor': '#ffffff', 'edgeColor': '#333333' }}}%%
flowchart LR
    subgraph Primary_Actors ["Tác nhân chính"]
        Shipper["👤 Shipper / Driver<br>(Bưu tá giao hàng)"]
    end

    subgraph UC_Boundary ["Phạm vi UC-COD-01: Bưu Tá Lập Bảng Kê Nộp Tiền COD (Thu Tiền)"]
        direction TB
        MainUC(["UC-COD-01<br>Bưu tá lập bảng kê nộp tiền COD"])
        
        subgraph Includes ["Các luồng bắt buộc (<<include>>)"]
            UC_ListDelivered(["Lọc danh sách vận đơn giao thành công chưa đối soát"])
            UC_SelectBills(["Chọn các vận đơn đã thu tiền mặt thực tế"])
            UC_SumCOD(["Tự động tính tổng tiền COD khai báo nộp"])
            UC_GenHandover(["Tạo mã Bảng kê nộp tiền (status='pending')"])
        end

        subgraph Extensions ["Các luồng mở rộng / Ngoại lệ (<<extend>>)"]
            UC_SelectAll(["[A1] Chọn nhanh toàn bộ danh sách vận đơn thành công"])
            UC_E1(["[E1] Cảnh báo lỗi khi chưa chọn vận đơn nào"])
        end

        MainUC -.->|"<<include>>"| UC_ListDelivered
        MainUC -.->|"<<include>>"| UC_SelectBills
        MainUC -.->|"<<include>>"| UC_SumCOD
        MainUC -.->|"<<include>>"| UC_GenHandover

        UC_SelectAll -.->|"<<extend>>"| UC_SelectBills
        UC_E1 -.->|"<<extend>>"| UC_GenHandover
    end

    subgraph Secondary_Actors ["Tác nhân phụ / Người nhận nộp tiền"]
        Cashier["👤 Cashier<br>(Thủ quỹ bưu cục)"]
        Database[("🗄️ PostgreSQL Database")]
    end

    Shipper --> MainUC
    UC_GenHandover --> Cashier
    UC_GenHandover --> Database

    classDef actor fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1;
    classDef mainuc fill:#d1fae5,stroke:#059669,stroke-width:2.5px,color:#065f46;
    classDef inc fill:#fffbeb,stroke:#d97706,stroke-width:1.5px,color:#92400e;
    classDef ext fill:#fef2f2,stroke:#dc2626,stroke-width:1.5px,color:#991b1b;
    classDef db fill:#f3e8ff,stroke:#9333ea,stroke-width:1.5px,color:#6b21a8;

    class Shipper,Cashier actor;
    class Database db;
    class MainUC mainuc;
    class UC_ListDelivered,UC_SelectBills,UC_SumCOD,UC_GenHandover inc;
    class UC_SelectAll,UC_E1 ext;

    style Primary_Actors fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style UC_Boundary fill:#f1f5f9,stroke:#94a3b8,stroke-width:2px;
    style Secondary_Actors fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style Includes fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
    style Extensions fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
```

### Điều kiện tiền đề (Preconditions)
1.  Bưu tá đã đăng nhập vào hệ thống Web Portal bưu cục.
2.  Bưu tá có ít nhất 1 vận đơn phát thành công có thu tiền COD trong ngày chưa được tạo bảng kê.

### Điều kiện hậu quả (Postconditions)
*   **Thành công (Success)**:
    1.  Mã bảng kê bàn giao COD (`cod_handovers`) được khởi tạo thành công ở trạng thái "Chờ thủ quỹ duyệt" (`pending`).
    2.  Các vận đơn được liên kết với mã bảng kê trong bảng `cod_handover_items`.
    3.  Thông tin bảng kê hiển thị trên màn hình duyệt của Thủ quỹ bưu cục.
*   **Thất bại (Failure)**:
    1.  Bảng kê không được tạo, bưu tá không thể làm thủ tục bàn giao quỹ tiền mặt cuối ngày.

---

### TIẾN TRÌNH THỰC HIỆN CHÍNH (MAIN FLOW)

| Bước | Actor | Hệ thống |
| :--- | :--- | :--- |
| **1** | Bưu tá mở giao diện "Bàn giao tiền COD cuối ngày". | Hệ thống truy vấn DB và hiển thị danh sách tất cả các vận đơn có tiền COD có trạng thái "Giao thành công" do bưu tá phụ trách chưa nộp tiền. |
| **2** | Bưu tá đánh dấu chọn các vận đơn đã thu được tiền mặt thực tế. | Hệ thống cập nhật danh sách chọn và tính tổng số tiền COD tương ứng thời gian thực. |
| **3** | Bưu tá bấm nút "Tạo Bảng Kê Nộp Tiền". | Hệ thống kiểm tra danh sách chọn hợp lệ, sinh mã bảng kê nộp tiền duy nhất (VD: `COD2107260088`), lưu vào bảng `cod_handovers` với trạng thái `pending`. |
| **4** | Bưu tá nhận mã bảng kê nộp tiền và cầm cọc tiền mặt đến quầy thủ quỹ bưu cục. | Hệ thống khóa không cho bưu tá sửa/xóa các đơn đã nằm trong bảng kê pending. Use case kết thúc. |

---

### TIẾN TRÌNH THAY THẾ & NGOẠI LỆ

*   **A1: Chọn nhanh toàn bộ danh sách đơn (tại Bước 2)**
    *   2a. Bưu tá bấm tích chọn "Chọn tất cả đơn trong ngày".
    *   2b. Hệ thống tự động tính tổng tiền COD cho toàn bộ đơn phát thành công. Continue bước 3.

*   **E1: Chưa chọn vận đơn nào (tại Bước 3)**
    *   3a. Bưu tá bấm nút "Tạo bảng kê" khi danh sách tích chọn đang trống (0 đơn).
    *   3b. Hệ thống cảnh báo: "Vui lòng chọn ít nhất 1 vận đơn đã thu tiền để tạo bảng kê".

---
---

## UC-COD-03: Thủ Quỹ Xác Nhận Thu Tiền COD Bưu Tá

### Thông tin cơ bản
*   **Mã Use Case**: UC-COD-03 (Tương ứng UC-WEB-39)
*   **Tên Use Case**: Thủ quỹ bưu cục xác nhận thu tiền COD bưu tá nộp về
*   **Actor chính**: Cashier (Thủ quỹ bưu cục)
*   **Actor phụ**: Shipper / Driver (Bưu tá nộp tiền), Cơ sở dữ liệu PostgreSQL
*   **Mô tả tóm tắt**: Cuối ngày giao hàng, bưu tá bàn giao tiền mặt COD thu được của người nhận về bưu cục. Thủ quỹ đối đếm tiền mặt thực tế, đối chiếu với Bảng kê nộp tiền bưu tá đã tạo trên hệ thống. Nếu khớp, thủ quỹ bấm duyệt để ghi nhận dòng tiền mặt vào quỹ két sắt bưu cục.
*   **Trigger**: Bưu tá cùng thủ quỹ đến quầy quỹ bưu cục làm thủ tục nộp tiền cuối ngày.
*   **Tần suất thực hiện**: Hàng ngày (Vào cuối ca làm việc từ 17:00 - 21:00).

### Sơ đồ Use Case Chi Tiết (Detailed Use Case Diagram)

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'primaryColor': '#ffffff', 'edgeColor': '#333333' }}}%%
flowchart LR
    subgraph Primary_Actors ["Tác nhân chính"]
        Cashier["👤 Cashier<br>(Thủ quỹ bưu cục)"]
    end

    subgraph UC_Boundary ["Phạm vi UC-COD-03: Thủ Quỹ Xác Nhận Thu Tiền COD Bưu Tá"]
        direction TB
        MainUC(["UC-COD-03<br>Xác nhận thu tiền COD bưu tá nộp về"])
        
        subgraph Includes ["Các luồng bắt buộc (<<include>>)"]
            UC_Search(["Tra cứu & Mở bảng kê nộp tiền COD"])
            UC_InputCash(["Nhập số tiền mặt thực đếm"])
            UC_Reconcile(["Tự động đối chiếu thực thu vs khai báo"])
            UC_Approve(["Duyệt bảng kê & Cập nhật đơn đã đối soát"])
            UC_Ledger(["Cộng số dư quỹ két sắt bưu cục (HubLedger)"])
        end

        subgraph Extensions ["Các luồng mở rộng / Ngoại lệ (<<extend>>)"]
            UC_A1(["[A1] Từ chối duyệt & Yêu cầu đối soát lại (Lệch tiền)"])
            UC_E1(["[E1] Tạo hộ bảng kê nộp tiền cho bưu tá tại quầy"])
        end

        MainUC -.->|"<<include>>"| UC_Search
        MainUC -.->|"<<include>>"| UC_InputCash
        MainUC -.->|"<<include>>"| UC_Reconcile
        MainUC -.->|"<<include>>"| UC_Approve
        MainUC -.->|"<<include>>"| UC_Ledger

        UC_A1 -.->|"<<extend>>"| UC_Reconcile
        UC_E1 -.->|"<<extend>>"| UC_Search
    end

    subgraph Secondary_Actors ["Tác nhân phụ / Hệ thống liên quan"]
        Shipper["👤 Shipper / Driver<br>(Bưu tá nộp tiền)"]
        Database[("🗄️ PostgreSQL Database")]
    end

    Cashier --> MainUC
    MainUC --> Shipper
    UC_Approve --> Database
    UC_Ledger --> Database

    classDef actor fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1;
    classDef mainuc fill:#d1fae5,stroke:#059669,stroke-width:2.5px,color:#065f46;
    classDef inc fill:#fffbeb,stroke:#d97706,stroke-width:1.5px,color:#92400e;
    classDef ext fill:#fef2f2,stroke:#dc2626,stroke-width:1.5px,color:#991b1b;
    classDef db fill:#f3e8ff,stroke:#9333ea,stroke-width:1.5px,color:#6b21a8;

    class Cashier,Shipper actor;
    class Database db;
    class MainUC mainuc;
    class UC_Search,UC_InputCash,UC_Reconcile,UC_Approve,UC_Ledger inc;
    class UC_A1,UC_E1 ext;

    style Primary_Actors fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style UC_Boundary fill:#f1f5f9,stroke:#94a3b8,stroke-width:2px;
    style Secondary_Actors fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style Includes fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
    style Extensions fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
```

### Điều kiện tiền đề (Preconditions)
1.  Thủ quỹ đã đăng nhập hệ thống Web Portal bưu cục.
2.  Được cấp quyền phê duyệt dòng tiền COD (`cod:approve`).
3.  Bưu tá đã tạo thành công "Bảng kê nộp tiền COD" trên tài khoản của mình (trạng thái bảng kê là "Chờ thủ quỹ duyệt").

### Điều kiện hậu quả (Postconditions)
*   **Thành công (Success)**:
    1.  Bảng kê nộp tiền COD của bưu tá chuyển sang trạng thái "Đã duyệt - Hoàn tất đối soát".
    2.  Trạng thái các vận đơn nằm trong bảng kê chuyển từ "Giao thành công - Chờ đối soát COD" sang "Đã đối soát COD nội bộ".
    3.  Số dư tiền mặt két sắt bưu cục tăng tương ứng với số tiền đã duyệt.
    4.  Bưu tá được giải phóng công nợ COD trong ngày.
*   **Thất bại (Failure)**:
    1.  Bảng kê giữ nguyên trạng thái "Chờ thủ quỹ duyệt" hoặc bị chuyển sang "Từ chối - Lệch tiền mặt".
    2.  Trạng thái đơn hàng lẻ không thay đổi, dòng tiền quỹ bưu cục không tăng.

---

### TIẾN TRÌNH THỰC HIỆN CHÍNH (MAIN FLOW)

| Bước | Actor | Hệ thống |
| :--- | :--- | :--- |
| **1** | Bưu tá đọc mã bảng kê nộp tiền (hoặc họ tên bưu tá). Thủ quỹ vào màn hình duyệt COD và tìm kiếm bảng kê tương ứng. | Hệ thống hiển thị chi tiết bảng kê nộp tiền: Tổng số tiền mặt COD khai báo nộp, số lượng đơn hàng liên quan và danh sách chi tiết các mã đơn giao thành công. |
| **2** | Bưu tá bàn giao cọc tiền mặt cho thủ quỹ. | Hệ thống hiển thị giao diện kiểm đếm. |
| **3** | Thủ quỹ kiểm đếm tiền mặt thực tế nhận được từ bưu tá và nhập số tiền thực tế đếm được vào ô "Số tiền mặt thực thu". | Hệ thống tự động đối chiếu số tiền thực tế nhập vào với Số tiền khai báo trên bảng kê và tính toán chênh lệch (Lệch = Thực thu - Khai báo). |
| **4** | Số tiền thực đếm khớp hoàn toàn với bảng kê (Lệch = 0). Thủ quỹ bấm nút "Xác nhận và Duyệt bảng kê". | Hệ thống cập nhật bảng kê sang trạng thái "Đã duyệt - Hoàn tất đối soát". Cập nhật các đơn lẻ liên quan sang "Đã đối soát COD nội bộ". Cộng tiền vào số dư két sắt bưu cục hiện tại. Ghi nhận thời gian và mã tài khoản thủ quỹ duyệt đơn. |
| **5** | Hệ thống hiển thị thông báo duyệt thành công. | Use case kết thúc. |

---

### TIẾN TRÌNH THAY THẾ (ALTERNATIVE FLOWS)

*   **A1: Phát hiện lệch tiền mặt (tại Bước 4)**
    *   4a. Số tiền thực tế thủ quỹ đếm được bị thiếu hoặc thừa so với bảng kê (Lệch ≠ 0).
    *   4b. Thủ quỹ nhập số tiền thực tế và bấm nút "Từ chối duyệt - Yêu cầu đối soát lại".
    *   4c. Hệ thống yêu cầu thủ quỹ nhập lý do từ chối (Ví dụ: "Thiếu 200,000đ so với bảng kê").
    *   4d. Hệ thống chuyển trạng thái bảng kê thành "Từ chối - Lệch tiền mặt", ghi nhận số tiền thực nộp tạm thời, không cộng số dư két sắt bưu cục. Bưu tá phải tự kiểm tra lại hành trình các đơn phát và đối chất.

---

### TIẾN TRÌNH NGOẠI LỆ (EXCEPTION FLOWS)

*   **E1: Bưu tá chưa lập bảng kê nộp tiền trên hệ thống (tại Bước 1)**
    *   1a. Bưu tá chưa lập bảng kê nhưng đã mang tiền mặt đến nộp.
    *   1b. Hệ thống không có bảng kê để thủ quỹ thực hiện duyệt.
    *   1c. Thủ quỹ yêu cầu bưu tá đăng nhập tài khoản tự chọn đơn lập bảng kê trước, hoặc thủ quỹ hỗ trợ tạo hộ bảng kê nộp tiền thay bưu tá trên giao diện Admin. Tiếp tục bước 2.

---

### CÁC QUY TẮC NGHIỆP VỤ LIÊN QUAN (BUSINESS RULES)
*   **BR-06 (Quy tắc khóa két sắt cuối ngày)**: Tất cả bảng kê nộp tiền phát sinh trong ngày của bưu cục phải được duyệt hoặc từ chối xử lý trước 22:00 hàng ngày. Sau thời gian này, hệ thống sẽ khóa chức năng duyệt của ngày hôm đó để chốt số dư két sắt cuối ngày phục vụ báo cáo tài chính về kho tổng.
*   **BR-07 (Trách nhiệm tài chính)**: Bưu tá chịu trách nhiệm đền bù 100% số tiền mặt thiếu hụt so với tổng tiền COD hiển thị trên bảng kê của các đơn hàng đã được cập nhật trạng thái "Giao thành công".

---
---

## UC-WAREHOUSE-01: Quét Mã Vạch Nhập Kho Bưu Cục (Inbound Scan)

### Thông tin cơ bản
*   **Mã Use Case**: UC-WAREHOUSE-01 (Tương ứng UC-WEB-28)
*   **Tên Use Case**: Quét mã vạch nhập kho bưu cục (Inbound Scan)
*   **Actor chính**: Warehouse Keeper (Nhân viên kho bưu cục)
*   **Actor phụ**: Máy quét Barcode, Cơ sở dữ liệu PostgreSQL
*   **Mô tả tóm tắt**: Nhân viên kho sử dụng đầu đọc quét mã vạch nhập kho các bưu gửi do bưu tá đi lấy về hoặc từ chuyến xe tải trung chuyển từ bưu cục khác tới. Hệ thống kiểm tra tính hợp lệ của mã vận đơn, phát âm thanh báo nhận thành công, chuyển vị trí đơn về bưu cục hiện tại (`current_hub_id`) và cập nhật trạng thái "Đang ở kho bưu cục".
*   **Trigger**: Nhân viên kho chọn chức năng "Quét nhập kho" trên phân hệ Quản lý kho.
*   **Tần suất thực hiện**: Rất cao (~5,000 lượt quét/ngày trên toàn hệ thống).

### Sơ đồ Use Case Chi Tiết (Detailed Use Case Diagram)

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'primaryColor': '#ffffff', 'edgeColor': '#333333' }}}%%
flowchart LR
    subgraph Primary_Actors ["Tác nhân chính"]
        WarehouseKeeper["👤 Warehouse Keeper<br>(Nhân viên kho)"]
    end

    subgraph UC_Boundary ["Phạm vi UC-WAREHOUSE-01: Quét Mã Vạch Nhập Kho Bưu Cục"]
        direction TB
        MainUC(["UC-WAREHOUSE-01<br>Quét mã vạch nhập kho bưu cục"])
        
        subgraph Includes ["Các luồng bắt buộc (<<include>>)"]
            UC_ScanBarcode(["Quét barcode mã vận đơn"])
            UC_CheckStatus(["Validate trạng thái & vị trí đơn"])
            UC_UpdateHub(["Cập nhật current_hub_id & Trạng thái 'Đang ở kho'"])
            UC_LogAudit(["Ghi nhận nhật ký nhập kho (BillStatusLog)"])
        end

        subgraph Extensions ["Các luồng mở rộng / Ngoại lệ (<<extend>>)"]
            UC_SoundErr(["[E1] Cảnh báo âm thanh lỗi khi đơn đã nhập / Không hợp lệ"])
        end

        MainUC -.->|"<<include>>"| UC_ScanBarcode
        MainUC -.->|"<<include>>"| UC_CheckStatus
        MainUC -.->|"<<include>>"| UC_UpdateHub
        MainUC -.->|"<<include>>"| UC_LogAudit

        UC_SoundErr -.->|"<<extend>>"| UC_CheckStatus
    end

    subgraph Secondary_Actors ["Tác nhân phụ / Thiết bị"]
        Scanner["📷 Máy quét Barcode"]
        Database[("🗄️ PostgreSQL Database")]
    end

    WarehouseKeeper --> MainUC
    Scanner --> UC_ScanBarcode
    UC_UpdateHub --> Database
    UC_LogAudit --> Database

    classDef actor fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1;
    classDef mainuc fill:#d1fae5,stroke:#059669,stroke-width:2.5px,color:#065f46;
    classDef inc fill:#fffbeb,stroke:#d97706,stroke-width:1.5px,color:#92400e;
    classDef ext fill:#fef2f2,stroke:#dc2626,stroke-width:1.5px,color:#991b1b;
    classDef db fill:#f3e8ff,stroke:#9333ea,stroke-width:1.5px,color:#6b21a8;

    class WarehouseKeeper,Scanner actor;
    class Database db;
    class MainUC mainuc;
    class UC_ScanBarcode,UC_CheckStatus,UC_UpdateHub,UC_LogAudit inc;
    class UC_SoundErr ext;

    style Primary_Actors fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style UC_Boundary fill:#f1f5f9,stroke:#94a3b8,stroke-width:2px;
    style Secondary_Actors fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style Includes fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
    style Extensions fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
```

---

## UC-WAREHOUSE-05: Quét Xuất Kho Bàn Giao Bưu Tá Đi Phát (Last-mile Outbound)

### Thông tin cơ bản
*   **Mã Use Case**: UC-WAREHOUSE-05 (Tương ứng UC-WEB-32)
*   **Tên Use Case**: Quét xuất kho bàn giao bưu tá đi phát (Last-mile Outbound)
*   **Actor chính**: Warehouse Keeper (Nhân viên kho bưu cục)
*   **Actor phụ**: Shipper / Driver (Bưu tá nhận đơn), Máy in nhiệt A6, PostgreSQL DB
*   **Mô tả tóm tắt**: Nhân viên kho chọn bưu tá phụ trách tuyến phát, quét mã vạch các vận đơn lẻ đang tồn ở bưu cục để bàn giao cho bưu tá đi giao chặng cuối cho người nhận. Sau khi quét xong, hệ thống cập nhật trạng thái các đơn sang "Đang giao hàng", gán `shipper_id` và tự động in "Bảng kê bàn giao phát hàng" (kèm chữ ký nhận của bưu tá).
*   **Trigger**: Nhân viên kho chọn chức năng "Xuất kho giao hàng" trên phân hệ Quản lý kho.
*   **Tần suất thực hiện**: Cao (~500 lần/ngày trên toàn hệ thống).

### Sơ đồ Use Case Chi Tiết (Detailed Use Case Diagram)

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'primaryColor': '#ffffff', 'edgeColor': '#333333' }}}%%
flowchart LR
    subgraph Primary_Actors ["Tác nhân chính"]
        WarehouseKeeper["👤 Warehouse Keeper<br>(Nhân viên kho)"]
    end

    subgraph UC_Boundary ["Phạm vi UC-WAREHOUSE-05: Quét Xuất Kho Giao Hàng Bưu Tá"]
        direction TB
        MainUC(["UC-WAREHOUSE-05<br>Quét xuất kho bàn giao bưu tá đi phát"])
        
        subgraph Includes ["Các luồng bắt buộc (<<include>>)"]
            UC_SelectShipper(["Chọn bưu tá phụ trách tuyến phát"])
            UC_ScanDeliveryBill(["Quét gán mã vận đơn giao chặng cuối"])
            UC_AssignShipper(["Gán shipper_id & Đổi trạng thái 'Đang giao hàng'"])
            UC_PrintRunsheet(["In Bảng kê bàn giao phát hàng (Runsheet A6/A4)"])
        end

        subgraph Extensions ["Các luồng mở rộng / Ngoại lệ (<<extend>>)"]
            UC_E1(["[E1] Cảnh báo vận đơn không thuộc khu vực/kho hiện tại"])
        end

        MainUC -.->|"<<include>>"| UC_SelectShipper
        MainUC -.->|"<<include>>"| UC_ScanDeliveryBill
        MainUC -.->|"<<include>>"| UC_AssignShipper
        MainUC -.->|"<<include>>"| UC_PrintRunsheet

        UC_E1 -.->|"<<extend>>"| UC_ScanDeliveryBill
    end

    subgraph Secondary_Actors ["Tác nhân phụ / Thiết bị"]
        Shipper["👤 Shipper / Driver<br>(Bưu tá nhận đơn)"]
        Printer["🖨️ Máy in nhiệt/A6"]
        Database[("🗄️ PostgreSQL Database")]
    end

    WarehouseKeeper --> MainUC
    MainUC --> Shipper
    UC_PrintRunsheet --> Printer
    UC_AssignShipper --> Database

    classDef actor fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1;
    classDef mainuc fill:#d1fae5,stroke:#059669,stroke-width:2.5px,color:#065f46;
    classDef inc fill:#fffbeb,stroke:#d97706,stroke-width:1.5px,color:#92400e;
    classDef ext fill:#fef2f2,stroke:#dc2626,stroke-width:1.5px,color:#991b1b;
    classDef db fill:#f3e8ff,stroke:#9333ea,stroke-width:1.5px,color:#6b21a8;

    class WarehouseKeeper,Shipper,Printer actor;
    class Database db;
    class MainUC mainuc;
    class UC_SelectShipper,UC_ScanDeliveryBill,UC_AssignShipper,UC_PrintRunsheet inc;
    class UC_E1 ext;

    style Primary_Actors fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style UC_Boundary fill:#f1f5f9,stroke:#94a3b8,stroke-width:2px;
    style Secondary_Actors fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style Includes fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
    style Extensions fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
```

---
---

# GIAI ĐOẠN 2 (DEFERRED USE CASES)

## UC-WAREHOUSE-03: Đóng Bao Trung Chuyển (Bagging & Manifest)

### Thông tin cơ bản
*   **Mã Use Case**: UC-WAREHOUSE-03
*   **Tên Use Case**: Đóng bao trung chuyển (Bagging & Manifest)
*   **Actor chính**: Warehouse Keeper (Nhân viên kho bưu cục)
*   **Actor phụ**: Máy in nhiệt bưu cục, Máy quét Barcode, PostgreSQL DB
*   **Mô tả tóm tắt**: Nhân viên kho gom nhiều đơn hàng lẻ có chung hướng vận chuyển (ví dụ: cùng đi kho trung chuyển tỉnh Lâm Đồng), quét mã vạch gán tất cả vào một mã bao hàng tải lớn, in bảng kê bao (Manifest) dán ngoài bao tải và quét xuất kho bao hàng đi bưu cục tiếp theo.
*   **Trigger**: Nhân viên kho chọn chức năng "Đóng bao trung chuyển" trên giao diện quản lý kho.
*   **Tần suất thực hiện**: Trung bình (~200 lần/ngày trên toàn hệ thống).

### Sơ đồ Use Case Chi Tiết (Detailed Use Case Diagram)

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'primaryColor': '#ffffff', 'edgeColor': '#333333' }}}%%
flowchart LR
    subgraph Primary_Actors ["Tác nhân chính"]
        WarehouseKeeper["👤 Warehouse Keeper<br>(Nhân viên kho)"]
    end

    subgraph UC_Boundary ["Phạm vi UC-WAREHOUSE-03: Đóng Bao Trung Chuyển (Giai đoạn 2)"]
        direction TB
        MainUC(["[GĐ2] UC-WAREHOUSE-03<br>Đóng bao trung chuyển (Bagging & Manifest)"])
        
        subgraph Includes ["Các luồng bắt buộc (<<include>>)"]
            UC_InitBag(["Tạo mã bao hàng mới (Bag ID)"])
            UC_ScanBill(["Quét gán mã vận đơn lẻ vào bao"])
            UC_CalcWeight(["Tự động tính tổng khối lượng tạm tính"])
            UC_SealBag(["Đóng & Niêm phong bao hàng"])
            UC_PrintManifest(["In bảng kê bao hàng (Manifest PDF)"])
        end

        subgraph Extensions ["Các luồng mở rộng / Ngoại lệ (<<extend>>)"]
            UC_E1(["[E1] Cảnh báo còi lỗi & Từ chối đơn không hợp lệ"])
            UC_E2(["[E2] Hủy bỏ bao hàng đóng dở & Giải phóng đơn"])
        end

        MainUC -.->|"<<include>>"| UC_InitBag
        MainUC -.->|"<<include>>"| UC_ScanBill
        MainUC -.->|"<<include>>"| UC_CalcWeight
        MainUC -.->|"<<include>>"| UC_SealBag
        MainUC -.->|"<<include>>"| UC_PrintManifest

        UC_E1 -.->|"<<extend>>"| UC_ScanBill
        UC_E2 -.->|"<<extend>>"| UC_SealBag
    end

    subgraph Secondary_Actors ["Tác nhân phụ / Thiết bị"]
        Printer["🖨️ Máy in nhiệt<br>(In Manifest)"]
        Scanner["📷 Máy quét Barcode"]
        Database[("🗄️ PostgreSQL Database")]
    end

    WarehouseKeeper --> MainUC
    Scanner --> UC_ScanBill
    UC_PrintManifest --> Printer
    UC_SealBag --> Database

    classDef actor fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1;
    classDef mainuc fill:#f1f5f9,stroke:#94a3b8,stroke-width:2px,color:#64748b;
    classDef inc fill:#fffbeb,stroke:#d97706,stroke-width:1.5px,color:#92400e;
    classDef ext fill:#fef2f2,stroke:#dc2626,stroke-width:1.5px,color:#991b1b;
    classDef db fill:#f3e8ff,stroke:#9333ea,stroke-width:1.5px,color:#6b21a8;

    class WarehouseKeeper,Printer,Scanner actor;
    class Database db;
    class MainUC mainuc;
    class UC_InitBag,UC_ScanBill,UC_CalcWeight,UC_SealBag,UC_PrintManifest inc;
    class UC_E1,UC_E2 ext;

    style Primary_Actors fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style UC_Boundary fill:#f1f5f9,stroke:#94a3b8,stroke-width:2px;
    style Secondary_Actors fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px;
    style Includes fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
    style Extensions fill:#ffffff,stroke:#e2e8f0,stroke-width:1px;
```

### Điều kiện tiền đề (Preconditions)
1.  Nhân viên kho đã đăng nhập vào Web Portal bưu cục.
2.  Được cấp quyền đóng bao và xuất kho (`warehouse:bagging`, `warehouse:outbound`).
3.  Vận đơn lẻ gán vào bao phải có trạng thái hiện tại là "Đang ở kho bưu cục" của bưu cục thao tác.

### Điều kiện hậu quả (Postconditions)
*   **Thành công (Success)**:
    1.  Mã bao hàng (Bag ID) mới được tạo ở trạng thái "Đang đóng bao".
    2.  Các vận đơn lẻ được liên kết với Bag ID và cập nhật trạng thái lịch sử sang "Đã đóng bao trung chuyển".
    3.  In bảng kê bao hàng (Manifest) chứa đầy đủ thông tin danh sách đơn và tổng cân nặng bao.
*   **Thất bại (Failure)**:
    1.  Bao hàng không được tạo.
    2.  Các vận đơn lẻ giữ nguyên trạng thái độc lập ở kho bưu cục.

---

### TIẾN TRÌNH THỰC HIỆN CHÍNH (MAIN FLOW)

| Bước | Actor | Hệ thống |
| :--- | :--- | :--- |
| **1** | Nhân viên kho bấm nút "Tạo bao hàng mới", chọn Bưu cục/Kho đích chuyển đến (Dropdown list). | Hệ thống sinh mã bao hàng duy nhất (ví dụ: BAG123456VN) ở trạng thái "Đang đóng bao". |
| **2** | Nhân viên đặt con trỏ vào ô quét mã vạch và dùng máy quét quét lần lượt mã của các đơn hàng lẻ bốc xếp vào bao. | Hệ thống nhận dạng mã đơn lẻ, kiểm tra trạng thái đơn hợp lệ (phải đang ở kho bưu cục hiện tại), phát tiếng kêu bíp thành công và thêm đơn lẻ vào lưới danh sách đóng bao trên màn hình. Cập nhật khối lượng tạm tính của bao hàng bằng tổng khối lượng các đơn. |
| **3** | Nhân viên quét xong tất cả các đơn lẻ và bấm nút "Đóng và niêm phong bao hàng". | Hệ thống cập nhật trạng thái bao hàng thành "Đã niêm phong". Chuyển trạng thái tất cả đơn lẻ bên trong bao sang "Đang trung chuyển" và liên kết khóa ngoại với mã bao hàng. Ghi nhận lịch sử luân chuyển của từng đơn. |
| **4** | Nhân viên bấm "In bảng kê bao hàng". | Hệ thống xuất bảng PDF manifest chứa mã vạch bao hàng, tên kho nguồn, kho đích, tổng số lượng đơn, tổng khối lượng và danh sách chi tiết các mã đơn lẻ bên trong. |
| **5** | Nhân viên thực hiện quét xuất kho bao hàng lên chuyến xe trung chuyển. | Hệ thống cập nhật trạng thái bao hàng thành "Đã xuất kho trung chuyển", ghi nhận thời gian và nhân viên xuất kho. Use case kết thúc. |

---

### TIẾN TRÌNH NGOẠI LỆ (EXCEPTION FLOWS)

*   **E1: Quét đơn hàng không hợp lệ (tại Bước 2)**
    *   2a. Nhân viên quét một đơn hàng có trạng thái không phải đang tồn ở kho bưu cục hiện tại (ví dụ: đơn chưa lấy, đơn đã phát thành công).
    *   2b. Hệ thống phát âm thanh cảnh báo lỗi (tít còi dài) và hiển thị thông báo: "Đơn hàng X không có trong kho bưu cục hiện tại hoặc trạng thái không hợp lệ để đóng bao".
    *   2c. Đơn hàng đó không được đưa vào danh sách đóng bao. Nhân viên bỏ đơn đó ra ngoài và quét tiếp đơn khác.

*   **E2: Hủy bỏ bao hàng đang đóng dở (tại Bước 3)**
    *   3a. Nhân viên phát hiện gán nhầm kho đích hoặc xảy ra sự cố cần hủy đóng bao.
    *   3b. Nhân viên bấm nút "Hủy đóng bao".
    *   3c. Hệ thống giải phóng tất cả đơn lẻ đã quét khỏi mã bao hàng hiện tại, xóa bao hàng tạm khỏi bộ nhớ. Trạng thái các đơn lẻ quay lại "Đang ở kho bưu cục".

---

### CÁC QUY TẮC NGHIỆP VỤ LIÊN QUAN (BUSINESS RULES)
*   **BR-04 (Quy tắc bao hàng)**: Một đơn hàng lẻ chỉ được gán cho tối đa 1 bao hàng chưa mở tại cùng một thời điểm.
*   **BR-05 (Tổng khối lượng)**: Tổng khối lượng của bao hàng hiển thị trên bảng kê phải bằng tổng khối lượng tính cước của toàn bộ đơn lẻ cộng với khối lượng vỏ bao tải được cấu hình mặc định (ví dụ: +0.2kg).
