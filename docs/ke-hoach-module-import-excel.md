# Kế hoạch triển khai Module Import Excel — Phiếu gửi (v2)

> **Trạng thái:** ✅ **ĐÃ TRIỂN KHAI** (backend + frontend) — 05/11/2026 · **Phiên bản kế hoạch:** v2
> **Kết quả kiểm chứng:** 346 unit test backend pass · 47 test frontend pass · `npm run lint` + `npm run build` sạch · migration sinh SQL hợp lệ · **integration test đã viết nhưng CHƯA chạy được** (Docker daemon không phản hồi trên máy này)
> **Nguồn dữ liệu:** `5.11 Mr Hải Logex.xlsx` — **import trực tiếp từ file gốc, KHÔNG cần chuẩn hoá lại file**
> **File đối chiếu đi kèm:** [`templates/du-lieu-mau-va-ket-qua-mong-doi.xlsx`](./templates/du-lieu-mau-va-ket-qua-mong-doi.xlsx)

---

## 0. TL;DR

| Hạng mục | Kết luận |
|---|---|
| **Đầu vào** | **File gốc của khách** (layout `Mr Hải Logex`), đọc trực tiếp. Không phát hành file mẫu mới ở giai đoạn này |
| **Mã đơn** | `HNLG5`, `HNLG10`… → **lưu thẳng vào `bills.tracking_number`** (mã vận đơn) |
| **Địa điểm giao** | Lưu **tỉnh mới** (để lọc/báo cáo) **+ giữ tỉnh cũ** nguyên văn; **địa chỉ chi tiết lưu NGUYÊN VĂN** đúng như Excel |
| **Số kiện** | → `bill_content_lines.quantity` |
| **Trọng lượng** | → `bill_content_lines.weight_kg` + `bills.actual_weight_kg` |
| **Số lượng Catalogue** | → **thông tin thêm** của line: `bill_content_lines.metadata.catalogue_quantity` |
| **Liên hệ** | 1 người **chính** vào hồ sơ khách; người còn lại → **bình luận** |
| **Khối lượng** | ~13,5 ngày công (backend ~9 + frontend ~2,5 + chốt/QA ~2) · ~1,5–2 tuần lịch |
| **Còn phải chốt** | 2 điểm: người gửi mặc định, và cách hiển thị/in "Số lượng catalogue" |
| **Trạng thái** | ✅ **Đã code xong** — xem [§12.6](#126-nhật-ký-triển-khai--sai-lệch-so-với-kế-hoạch) |

### Thay đổi so với v1

| Nội dung | v1 | **v2 (chốt theo yêu cầu khách)** |
|---|---|---|
| Định dạng đầu vào | Phải dùng file mẫu chuẩn 24 cột | **Đọc thẳng file gốc 10 cột** — bỏ yêu cầu chuẩn hoá file |
| Mã đơn | `partner_bill_code` (D1 chưa chốt) | **`tracking_number`** — chốt |
| Số kiện | Đề xuất thêm cột `bills.package_count` (D2 chưa chốt) | **`bill_content_lines.quantity`** — không cần migration |
| Số lượng catalogue | Cột riêng `bill_content_lines.quantity` | **`metadata` = "thông tin thêm"**, `quantity` dành cho số kiện |
| Địa điểm | Chỉ lưu tỉnh mới | Lưu **cả cũ và mới**, địa chỉ nguyên văn |
| Ngày tạo phiếu | Có cột ngày (D3) | File gốc **không có cột ngày** → `created_at` = thời điểm import |
| Số cột file nguồn | 24 | **10** (đúng file gốc) |
| Endpoint | 7 | **6** (bỏ endpoint tải file mẫu) |
| Ngày công | ~16 | **~13,5** |

---

## 1. Mục tiêu & phạm vi

### 1.1 Trong phạm vi

1. **Import phiếu gửi trực tiếp từ file gốc** `5.11 Mr Hải Logex.xlsx` (và các file cùng layout).
2. **Kiểm tra trước khi ghi (preview):** mỗi dòng phân loại `OK` / `CẢNH BÁO` / `LỖI` kèm lý do tiếng Việt; người dùng xem trước rồi mới xác nhận.
3. **Mã đơn thành mã vận đơn** — phiếu in ra và tra cứu bằng đúng mã `HNLG5` của khách.
4. **Quy tắc liên hệ:** 1 người chính vào hồ sơ khách; người còn lại tự động thành **bình luận**.
5. **Báo cáo kết quả:** tải file Excel kết quả (dữ liệu gốc + cột trạng thái/lỗi); lịch sử các lần import.
6. **Ánh xạ địa danh cũ → mới** theo bảng quy đổi 34 tỉnh sau sáp nhập 2025.

### 1.2 Ngoài phạm vi (giai đoạn này)

- **Chuẩn hoá file nguồn / phát hành file mẫu mới** — để giai đoạn sau (xem [§12.4](#124-giai-đoạn-2--chuẩn-hoá-file-nguồn-không-làm-ở-giai-đoạn-1)).
- Import khách hàng độc lập (file gốc không có; khách được tạo tự động từ phiếu).
- Import từ CSV / API đối tác.
- **Cập nhật** phiếu đã tồn tại — giai đoạn này chỉ tạo mới, trùng thì bỏ qua và cảnh báo.
- Tự tính cước từ bảng giá (file không có cột cước → cước = 0).

---

## 2. Hiện trạng hệ thống (đã khảo sát mã nguồn)

### 2.1 Tái sử dụng được

| Thành phần | Đường dẫn | Dùng cho |
|---|---|---|
| Nghiệp vụ tạo phiếu | `app/services/bill_service.py:create_bill` | Get-or-create khách theo SĐT, snapshot bất biến, ghi `bill_status_logs`, audit |
| Model phiếu | `app/models/bill.py` | `tracking_number` là `Text UNIQUE NOT NULL` → **chứa được `HNLG5`** |
| Model line item | `app/models/bill_content_line.py` | `quantity`, `weight_kg`, **`metadata` JSONB** = "thông tin thêm" |
| Model khách | `app/models/customer.py` | Địa chỉ/liên hệ nằm trong `metadata` JSONB — **không cần migration** |
| Bình luận | `app/models/comment.py`, `app/services/comment_service.py` | `entity_type ∈ (bill, customer, …)` → chứa liên hệ phụ |
| In phiếu + barcode | `app/services/print_service.py:47` | `barcode.get("code128", bill.tracking_number)` → **Code 128 nhận chữ + số**, `HNLG5` in được |
| Danh mục địa lý | `provinces` (34 tỉnh sau sáp nhập) + `wards` | Chuẩn hoá "Địa điểm giao" |
| Hiển thị metadata line | `frontend/.../BillCommercialEditor.jsx:21` | Đã render "thông tin thêm" dạng `Key: value` |
| Upload file | `app/api/v1/files.py`, `app/services/storage/validators.py` | Allowlist `.xlsx` có sẵn |

### 2.2 Khoảng trống phải bù

| # | Khoảng trống | Ảnh hưởng | Cách xử lý |
|---|---|---|---|
| G1 | Không có module/route import | — | Tạo mới (§6) |
| G2 | **`create_bill()` luôn tự sinh** `tracking_number` (`crud/bill.py:63`) | Không nhập được mã `HNLG5` | Thêm tham số `tracking_number` tùy chọn (§6.9) |
| G3 | Không có trường **tên người liên hệ** (chỉ có `customers.phone`) | Mất "Chị Hương" | `customers.metadata.contact_name` (JSONB, không migration) |
| G4 | Không có chỗ lưu **tỉnh cũ** | Mất dấu vết quy đổi địa danh | `BillParty.province_raw` + vào snapshot (§6.9) |
| G5 | Không có bảng quy đổi địa danh cũ → mới | 10/21 giá trị (14/70 dòng) không khớp `provinces` | Bảng alias trong `importing/locations.py` |
| G6 | Chưa có quyền import | Không gác được | Action `bill:import` + migration cấp quyền |
| G7 | Không có cơ chế chống trùng | Nhập lại file = nhân đôi | `file_hash` + `tracking_number` UNIQUE |
| G8 | **`provinces` không seed bằng migration** (nạp từ API ngoài) | DB mới có 0 tỉnh → mọi dòng lỗi | Báo `IMPORT_PROVINCES_NOT_SEEDED`; test tự seed |
| G9 | `formatMetadata` hiển thị key thô (`catalogue_quantity` → "Catalogue quantity") | Không phải tiếng Việt | Thêm bảng nhãn i18n (§6.10) |
| G10 | In phiếu hiện in `line.quantity` dưới nhãn "Số lượng" | Nhãn sai nghĩa (nay là số kiện) | Đổi nhãn thành "Số kiện" (§6.10) |

---

## 3. File nguồn: phân tích & cách đọc

### 3.1 Cấu trúc thực tế

```
Workbook: 2 sheet — "Sheet2" (dữ liệu) và "Sheet1" (RỖNG)  ← phải dò theo header, không hard-code "Sheet1"
Sheet2:
├── Dòng 1 : tiêu đề "HNB - MINI CATALOGUE 2H.2026" + H1/I1/J1 = công thức =SUM(...)
├── Dòng 2 : header  A="Mã đơn"  C="Mã đơn"  ← TRÙNG TÊN (A là số, B là tiền tố, C là mã đầy đủ)
└── Dòng 3–72 : 70 dòng dữ liệu

A: Mã đơn (số)         5
B: Tiền tố             'HNLG'
C: Mã đơn              =B3&A3        ← CÔNG THỨC → giá trị cache = "HNLG5"
D: Địa điểm giao       Hà Nội
E: Tên đại lý nhận     HẰNG HÒA
F: Địa chỉ giao        "B2 10 Shop house 24H Đường Tố Hữu, Phường Hà Đông, Hà Nội."
G: Liên hệ             "Chị Hương: 0949988999"
H: Số lượng Catalogue  150
I: Số kiện             3
J: Trọng lượng (kg)    43.5
```

### 3.2 Cách nhận diện file (thay cho "kiểm tra đúng mẫu")

Không bắt người dùng dùng đúng một file mẫu. Thay vào đó `readers.py` **dò header**:

1. Quét tối đa 10 dòng đầu, mỗi sheet; chọn sheet/dòng có **nhiều nhất** các header đã biết.
2. Từ điển header chấp nhận được (chuẩn hoá: bỏ dấu, lower, gộp khoảng trắng):

| Trường logic | Header chấp nhận |
|---|---|
| `tracking` | `mã đơn`, `mã vận đơn`, `ma don`, `ma van don`, `code` |
| `destination` | `địa điểm giao`, `địa điểm`, `tỉnh/thành phố giao`, `tinh`, `tỉnh` |
| `receiver_name` | `tên đại lý nhận`, `tên đại lý`, `tên khách hàng nhận`, `tên khách nhận`, `khách hàng` |
| `address` | `địa chỉ giao chi tiết`, `địa chỉ giao`, `địa chỉ` |
| `contact` | `liên hệ`, `thông tin liên hệ`, `người liên hệ` |
| `catalogue_qty` | `số lượng catalogue`, `số lượng catalog`, `số lượng` |
| `packages` | `số kiện`, `kiện` |
| `weight` | `trọng lượng (kg)`, `trọng lượng`, `kg` |

3. Bắt buộc tối thiểu: `tracking` (hoặc `prefix`+`số`), `destination`, `receiver_name`, `contact`, `packages`, `weight`. Thiếu → `IMPORT_COLUMNS_NOT_FOUND` kèm danh sách cột tìm được/thiếu.
4. Dùng **`openpyxl.load_workbook(read_only=True, data_only=True)`** để lấy **giá trị cache** của ô công thức (`HNLG5` thay vì `=B3&A3`).
5. Nếu cột C (mã đầy đủ) trống → ghép `B + A`; nếu vẫn trống → dòng LỖI.
6. Kiến trúc cho phép thêm "adapter" cho layout khác sau này (`SOURCE_ADAPTERS`, giai đoạn 1 chỉ 1 adapter).

### 3.3 Mười vấn đề dữ liệu đo được (giữ từ v1 — đều đã xử lý trong thiết kế)

| # | Vấn đề | Số liệu thực tế | Cách xử lý |
|---|---|---|---|
| 1 | Header trùng tên "Mã đơn" | 2 cột (A và C) | Ưu tiên cột C (mã đầy đủ), fallback ghép B+A |
| 2 | Ô công thức | **76 ô** (C: 70 dòng; H1/I1/J1; H72/I72/J72) | `data_only=True` |
| 3 | Dòng tiêu đề + dòng tổng lẫn dữ liệu | Dòng 1 có 3 ô số | Dò header theo tên cột, bỏ mọi dòng trước header |
| 4 | Địa danh không còn là tỉnh | **10/21 giá trị, 14/70 dòng** | Bảng quy đổi (§4.2) |
| 5 | Nhiều người trong 1 ô liên hệ | **12/70 dòng** | Parser liên hệ (§5) |
| 6 | Không có tên người liên hệ | **8/70 dòng** (chỉ số bàn/hotline) | Chấp nhận: chỉ lưu SĐT |
| 7 | SĐT không chuẩn hoá | dấu nháy `'0976758807`, `(024) 3853 2294`, 2 số 1 ô | Chuẩn hoá về chữ số (§4.4) |
| 8 | Sai số float ở trọng lượng | **46/70 dòng** (`28.999999999999996`) | `Decimal` quantize 3 lẻ |
| 9 | Tên đại lý VIẾT HOA | **58/70 dòng** | **Giữ nguyên văn** (xem [D-a](#11-việc-cần-quyết-trước-khi-triển-khai)) |
| 10 | Không có cước/COD/người gửi | 0/70 dòng | Cước = 0; người gửi = mặc định công ty |

---

## 4. Ánh xạ dữ liệu — **CHỐT**

Mỗi dòng file → **1 phiếu + 1 line item + (0–1) bình luận** (chưa tính khách được dedupe).

### 4.1 Bảng ánh xạ

| # | Cột file gốc | Trường đích | Quy tắc |
|---|---|---|---|
| 1 | **C `Mã đơn`** (fallback `B+A`) | **`bills.tracking_number`** | Trim. Không rỗng, ≤ 50 ký tự, chỉ `A-Z a-z 0-9 . _ -`. **UNIQUE toàn hệ thống** — trùng thì bỏ qua + cảnh báo |
| 2 | D `Địa điểm giao` | `customers.metadata.province_code` / `province_name` = **tỉnh mới**<br>`receiver_snapshot.province_raw` = **tỉnh cũ nguyên văn** | Tra bảng quy đổi (§4.2). Không khớp → LỖI |
| 3 | E `Tên đại lý nhận` | `customers.name` + `receiver_snapshot.name` | Trim, gộp khoảng trắng. **Giữ nguyên chữ hoa/thường** |
| 4 | F `Địa chỉ giao chi tiết` | `customers.metadata.address_detail` + `receiver_snapshot.address_detail` | **NGUYÊN VĂN** — chỉ trim đầu/cuối, gộp khoảng trắng thừa, **không sửa nội dung** |
| 5 | G `Liên hệ` — người chính | `customers.phone` + `customers.metadata.contact_name` + `receiver_snapshot.phone` | Xem §5 |
| 6 | G `Liên hệ` — người thứ 2, 3… | **`comments`** (entity `bill`) | Xem §5 |
| 7 | **H `Số lượng Catalogue`** | **`bill_content_lines.metadata.catalogue_quantity`** — hiển thị ở "thông tin thêm" | Số nguyên ≥ 0 (có thể trống) |
| 8 | **I `Số kiện`** | **`bill_content_lines.quantity`** | Số nguyên > 0. Trống → mặc định **1** + cảnh báo |
| 9 | **J `Trọng lượng (kg)`** | `bill_content_lines.weight_kg` **và** `bills.actual_weight_kg` | `Decimal` quantize 3 lẻ, > 0 |
| 10 | (hằng số) | `bill_content_lines.description` | `"Catalogue"` — cấu hình được (`options.catalogue_description`) |

### 4.2 Địa danh: lưu **tương ứng cũ — mới**

`provinces` hiện chỉ có **34** đơn vị sau sáp nhập 2025. Với mỗi dòng:

```
destination_raw  = D (nguyên văn)                                   → lưu ở receiver_snapshot.province_raw
province_name    = tên tỉnh MỚI (bỏ tiền tố "Tỉnh"/"Thành phố")     → lưu chuẩn
province_code    = mã tỉnh MỚI                                      → lưu chuẩn
address_detail   = F (NGUYÊN VĂN, KHÔNG bị sửa theo bảng quy đổi)
```

Bảng quy đổi áp dụng cho file mẫu (**10 giá trị / 14 dòng**):

| Giá trị trong file | Số dòng | Tỉnh chuẩn | Mã | Loại |
|---|:--:|---|:--:|---|
| Hải Dương | 3 | Hải Phòng | 31 | sáp nhập 2025 |
| Vĩnh Phúc | 2 | Phú Thọ | 25 | sáp nhập 2025 |
| Bắc Giang | 2 | Bắc Ninh | 24 | sáp nhập 2025 |
| Thái Bình | 1 | Hưng Yên | 33 | sáp nhập 2025 |
| Hòa Bình | 1 | Phú Thọ | 25 | sáp nhập 2025 |
| Nam Định | 1 | Ninh Bình | 37 | sáp nhập 2025 |
| Hà Nam | 1 | Ninh Bình | 37 | sáp nhập 2025 |
| Yên Bái | 1 | Lào Cai | 15 | sáp nhập 2025 |
| **Hạ Long** | 1 | Quảng Ninh | 22 | thành phố thuộc tỉnh (không phải tỉnh) |
| **Chi Nhánh HN** | 1 | Hà Nội | 1 | bưu cục nội bộ → cảnh báo đặc biệt |

Bảng alias đầy đủ cho cả 34 tỉnh nằm trong `importing/locations.py` (gồm các tỉnh chưa xuất hiện trong file mẫu: Bắc Kạn→Thái Nguyên, Hà Giang→Tuyên Quang, Quảng Bình→Quảng Trị, Kon Tum→Quảng Ngãi, Bình Định/Phú Yên→Gia Lai, Ninh Thuận→Khánh Hòa, Đắk Nông/Bình Thuận→Lâm Đồng, Bình Phước→Đồng Nai, Bình Dương/Bà Rịa–Vũng Tàu→Hồ Chí Minh, Long An→Tây Ninh, Tiền Giang→Đồng Tháp, Bến Tre/Trà Vinh→Vĩnh Long, Kiên Giang→An Giang, Sóc Trăng/Hậu Giang→Cần Thơ, Bạc Liêu→Cà Mau, Thừa Thiên Huế→Huế, Quảng Nam→Đà Nẵng).

### 4.3 Giá trị mặc định (file gốc không có)

| Trường | Giá trị | Ghi chú |
|---|---|---|
| `bills.cargo_type` | `goods` | Hằng số |
| `bills.payer` | `receiver` | Hằng số |
| `bills.fee_main` / `fee_insurance` / `fee_other` / `fee_vat` | `0` | Không có cột cước → `fee_total = 0` (thỏa `ck_bills_fee_total`) |
| `bills.cod_amount` | `0` | |
| `bills.service_tier_code` | `null` | Trống = không gán dịch vụ |
| `bills.status` | `created` | Phiếu mới ở trạng thái khởi tạo |
| `bills.created_at` | thời điểm import | File gốc **không có cột ngày** |
| `bills.partner_id` / `partner_bill_code` | `null` | Không dùng (mã đơn đã là mã vận đơn) |
| `sender` (bắt buộc bởi `BillCreate`) | Khách gửi mặc định = `settings.CARRIER_NAME` / `CARRIER_HOTLINE` | Xem [D-b](#11-việc-cần-quyết-trước-khi-triển-khai) |
| `bill_content_lines.description` | `"Catalogue"` | Cấu hình được |
| `bill_content_lines.cargo_type` | `goods` | |
| `bill_content_lines.length/width/height` | `null` | → `chargeable_weight = actual_weight` |

### 4.4 Chuẩn hoá trường tối thiểu (không phải "chuẩn hoá file")

| Trường | Quy tắc |
|---|---|
| Số điện thoại | Bỏ mọi ký tự không phải số; `+84`→`0`; chấp nhận **9–11 chữ số** (cả số bàn). Trùng chuỗi = cùng khách (hệ thống dedupe theo **đúng chuỗi** `customers.phone`) |
| Trọng lượng | `Decimal(str(v)).quantize(0.001, ROUND_HALF_UP)` — `28.999999999999996` → `29.000` |
| Số nguyên | Bỏ dấu phân cách nghìn nếu có; âm → LỖI |
| Mã đơn | Trim; giữ nguyên chữ/số/gạch; **không** đổi hoa/thường |
| Địa chỉ | Trim đầu/cuối + gộp khoảng trắng thừa. **Không sửa nội dung** |
| Tên đại lý | Trim + gộp khoảng trắng. **Không đổi hoa/thường** ([D-a](#11-việc-cần-quyết-trước-khi-triển-khai)) |

---

## 5. Quy tắc liên hệ — chi tiết (yêu cầu trọng tâm)

Ô G chứa 1–2 người với rất nhiều kiểu viết. Bộ parser đã được **kiểm chứng trên 70/70 dòng** của file mẫu.

### 5.1 Thuật toán

```
1. Chuẩn hoá: bỏ dấu nháy ' và ’, thống nhất \r\n → \n
2. Tách mạnh theo: xuống dòng | "/" | " - " (CHỈ khi có khoảng trắng hai bên)
3. Mỗi mảnh: tách SĐT (9–11 chữ số, hỗ trợ (024) 3853 2294 và +84) và phần chữ còn lại
4. Gộp mảnh "chỉ có tên" với mảnh "chỉ có số" liền sau  (Mr. Thành \n 0911 166 177)
5. Bỏ danh xưng ở đầu: Chị/Anh/Em/Cô/Bác/Ông/Chú/Ms/Mrs/Mr/Miss/C
      ⚠ CHỈ bỏ khi phần còn lại vẫn có chữ — "Anh" một mình là TÊN THẬT, không bỏ
6. Bỏ nhiễu: "Hotline:", "Hot line", "SR 1:", "CN 1:", "ĐT:", "Điện thoại:"
7. CHỌN NGƯỜI CHÍNH: mảnh đầu tiên có CẢ tên và SĐT
      → nếu không có: mảnh đầu tiên có SĐT
      → nếu không có: mảnh đầu tiên có tên
8. Các mảnh còn lại = "liên hệ khác" → 1 BÌNH LUẬN
```

### 5.2 Ví dụ đã kiểm chứng trên file mẫu

| Chuỗi gốc | Người chính | SĐT chính | → Bình luận |
|---|---|---|---|
| `Chị Hương: 0949988999` | Hương | 0949988999 | — |
| `Chị Loan 0983280816/ Ngọc 0973319660` | Loan | 0983280816 | Ngọc – 0973319660 |
| `(024) 3853 2294\nChị Hoa: 0868327760` | Hoa | 0868327760 | 02438532294 |
| `SR 1: Ms. Thoa 0972 173 867\nSR 2: Ms. Nghĩa 0988 406 555` | Thoa | 0972173867 | Nghĩa – 0988406555 |
| `Mr. Thành \n0911 166 177` | Thành | 0911166177 | — |
| `0938888838 (Mrs. Thơ)` | Thơ | 0938888838 | — |
| `ms.Anh 0365446686` | Anh | 0365446686 | — |
| `Ms, Huệ 097 227 3064` | Huệ | 0972273064 | — |
| `02253 591 335 - 0929 853 969` | *(trống)* | 02253591335 | 0929853969 |
| `Hotline: 0917 632 211` | *(trống)* | 0917632211 | — |

**Kết quả trên 70 dòng:** 70/70 tách được SĐT chính · 62/70 có tên người · **12/70 có liên hệ khác → 12 bình luận** · 8/70 chỉ có số bàn (không có tên — đúng bản chất dữ liệu).

### 5.3 Ghi dữ liệu

```
Người chính:
  customers.phone                     = normalize_phone(primary.phone)   ← khoá dedupe
  customers.metadata.contact_name     = primary.name
  customers.metadata.contact_raw      = ô G nguyên văn                   ← không mất dữ liệu gốc
  receiver_snapshot.phone             = primary.phone

Liên hệ khác (nếu có) → ĐÚNG MỘT bình luận, qua comment_service:
  await comment_service.create_comment(
      db,
      CommentCreate(
          entity_type="bill",
          entity_id=bill.id,
          body="<p><strong>Liên hệ khác (nhập từ Excel):</strong></p>"
               "<ul><li>Ngọc – 0973319660</li>…</ul>",
          images=[],
      ),
      current_user,
  )
```

> **Không dựng `Comment(...)` trực tiếp.** Phải qua `comment_service.create_comment()` vì: (a) kiểm tra entity tồn tại, (b) trả `comment.author` cho response, (c) `CommentCreate` mới là nơi **sanitize `nh3`** — dựng model trực tiếp sẽ bỏ qua toàn bộ bước chống XSS.
> `CommentCreate.body` bắt buộc có nội dung text sau khi bóc HTML → body phải là HTML, không được rỗng.

**Vì sao dùng bình luận:** đúng yêu cầu; không thêm bảng liên hệ; hiển thị ngay ở `CommentSection` đang có; ghi được tác giả + thời điểm; **không bị đè** khi hồ sơ khách cập nhật sau này.

---

## 6. Kiến trúc kỹ thuật

### 6.1 Luồng xử lý

```
[1] UPLOAD + KIỂM TRA   POST /api/v1/imports  (multipart: file, options?)
        │  openpyxl read_only + data_only → dò sheet/header → parse từng dòng
        │  → chuẩn hoá → validate → ghi import_rows (JSONB)   ★ CHƯA chạm bills/customers
        ▼
[2] XEM TRƯỚC           GET /imports/{id}  +  GET /imports/{id}/rows?status=error
        │  người dùng lọc dòng LỖI, tải file lỗi, quyết định bỏ qua cảnh báo
        ▼
[3] XÁC NHẬN GHI        POST /imports/{id}/commit
        │  → tạo phiếu (tracking = mã đơn) + line item + khách + bình luận liên hệ phụ
        ▼
[4] TẢI KẾT QUẢ         GET /imports/{id}/result  → .xlsx gốc + cột trạng thái/lỗi
```

### 6.2 Cấu trúc mã nguồn

```
backend/app/
├── api/v1/imports.py                     # router /imports — đăng ký ở main.py
├── core/
│   ├── permissions.py                    # + bill:import
│   └── i18n.py                           # + 15 mã lỗi IMPORT_*
├── models/import_batch.py                # ImportBatch, ImportRow  (+ khai báo ở models/__init__.py)
├── schemas/import_batch.py               # ImportBatchRead, ImportRowRead, ImportSummary, CommitRequest
├── crud/import_batch.py                  # tạo/đọc batch & rows, cập nhật trạng thái
├── services/
│   ├── import_service.py                 # ĐIỀU PHỐI (file phẳng): validate_file(), commit_batch()
│   └── importing/                        # package HELPER THUẦN — tiền lệ: services/storage/
│       ├── __init__.py                   # re-export tường minh
│       ├── template.py                   # ĐỊNH NGHĨA TRƯỜNG LOGIC + từ điển header
│       ├── readers.py                    # dò sheet/header, đọc ô, lấy giá trị cache
│       ├── normalize.py                  # text/number/phone/name/address
│       ├── contacts.py                   # parser liên hệ → (primary, extras)  [§5]
│       ├── locations.py                  # 34 tỉnh + bảng quy đổi cũ→mới
│       └── validators.py                 # rule engine → (status, error_code, message)
└── alembic/versions/<tự cấp>_add_import_batches.py

frontend/src/
├── api/imports.js
└── features/imports/
    ├── components/ImportWizard.jsx        # 3 bước: Upload → Xem trước → Kết quả
    ├── components/ImportPreviewTable.jsx  # bảng preview + Tag trạng thái + lọc
    └── components/ImportResultPanel.jsx
```

**Vì sao chia package như trên.** Trong `app/services/` hiện chỉ có **một** sub-package là `storage/` (helper thuần) đi kèm `storage_service.py` mỏng. Bám đúng hình mẫu đó:

- `import_service.py` — **file phẳng**, giữ toàn bộ điều phối + I/O DB.
- `importing/` — **chỉ helper thuần, không I/O DB, không nghiệp vụ entity** → test unit được **không cần database**.
- **Không** tạo lớp `handlers/` trung gian: `import_service` gọi thẳng `bill_service.create_bill()` / `comment_service.create_comment()` (service gọi service là hợp lệ).

**Bắt buộc đăng ký (dễ quên):** `app/models/__init__.py` (để Alembic thấy model), `app/main.py` (import tuple + `include_router`), `app/core/i18n.py` (mọi mã `IMPORT_*` **phải** có message, nếu không `get_message` rơi về `INTERNAL_ERROR` và người dùng chỉ thấy "lỗi hệ thống").

### 6.3 Mô hình dữ liệu mới

> Số hiệu migration **do hook `process_revision_directives` trong `alembic/env.py` tự cấp** (`max+1`) — không tự đặt tay.

```sql
CREATE TABLE import_batches (
    id            BIGSERIAL PRIMARY KEY,
    entity_type   VARCHAR(20)  NOT NULL CHECK (entity_type IN ('bill')),   -- mở rộng sau
    file_name     TEXT         NOT NULL,
    file_hash     CHAR(64)     NOT NULL,          -- SHA-256 chống import trùng
    source_layout VARCHAR(32)  NOT NULL DEFAULT 'legacy_logex',
    status        VARCHAR(20)  NOT NULL DEFAULT 'validating',
                  -- validating | validated | committing | completed | partially_completed | failed
    total_rows    INTEGER      NOT NULL DEFAULT 0,
    ok_rows       INTEGER      NOT NULL DEFAULT 0,
    warning_rows  INTEGER      NOT NULL DEFAULT 0,
    error_rows    INTEGER      NOT NULL DEFAULT 0,
    imported_rows INTEGER      NOT NULL DEFAULT 0,
    customers_created INTEGER  NOT NULL DEFAULT 0,
    warnings      JSONB        NOT NULL DEFAULT '[]',
    options       JSONB        NOT NULL DEFAULT '{}',
    error_message TEXT,
    created_by    BIGINT       NOT NULL REFERENCES users(id),
    created_at    TIMESTAMP    NOT NULL DEFAULT now(),
    committed_at  TIMESTAMP
);
CREATE INDEX ix_import_batches_creator ON import_batches(created_by, created_at DESC);
CREATE INDEX ix_import_batches_hash    ON import_batches(file_hash);

CREATE TABLE import_rows (
    id               BIGSERIAL PRIMARY KEY,
    batch_id         BIGINT      NOT NULL REFERENCES import_batches(id) ON DELETE CASCADE,
    row_number       INTEGER     NOT NULL,        -- số dòng THẬT trong Excel (để báo lỗi chính xác)
    raw_data         JSONB       NOT NULL,        -- nguyên văn từng ô
    normalized_data  JSONB       NOT NULL DEFAULT '{}',
    status           VARCHAR(10) NOT NULL,        -- ok | warning | error | imported | skipped
    error_code       VARCHAR(64),
    error_message    TEXT,
    warnings         JSONB       NOT NULL DEFAULT '[]',
    target_id        BIGINT,                      -- bill_id sau khi ghi
    created_at       TIMESTAMP   NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX ux_import_rows_batch_row ON import_rows(batch_id, row_number);
```

> Bảng này là **audit trail**: biết ai import file nào, dòng Excel số mấy lỗi vì sao, dòng nào tạo ra phiếu nào.

### 6.4 API contract (6 endpoint)

| Method | Path | Quyền | Mô tả |
|---|---|---|---|
| `POST` | `/api/v1/imports` | `bill:import` | Upload file → tạo batch + kiểm tra. Trả `batch_id` + preview 200 dòng + thống kê |
| `GET` | `/api/v1/imports` | `bill:import` | Lịch sử import (phân trang) |
| `GET` | `/api/v1/imports/{batch_id}` | `bill:import` | Chi tiết batch + thống kê |
| `GET` | `/api/v1/imports/{batch_id}/rows` | `bill:import` | `?status=error&page=&page_size=` |
| `POST` | `/api/v1/imports/{batch_id}/commit` | `bill:import` | `{"skip_error_rows": true}` → ghi thật (action sub-resource) |
| `GET` | `/api/v1/imports/{batch_id}/result` | `bill:import` | File kết quả `.xlsx` |

> Đặt theo `docs/conventions.md` §4.5: danh từ số nhiều kebab-case, **không nhét động từ vào path** (nên upload là `POST /imports`, **không** phải `/imports/validate`); hành động không-CRUD dùng sub-resource (`/imports/{id}/commit`).

`POST /api/v1/imports` — `multipart/form-data`:

| Field | Kiểu | Ghi chú |
|---|---|---|
| `file` | File | `.xlsx`, ≤ **5 MB**, ≤ **5.000 dòng** |
| `options` | JSON string? | `{"catalogue_description":"Catalogue","default_packages":1,"normalize_names":false}` |

Response rút gọn:

```json
{
  "id": 12,
  "status": "validated",
  "source_layout": "legacy_logex",
  "summary": { "total_rows": 70, "ok_rows": 55, "warning_rows": 15, "error_rows": 0 },
  "preview": [
    { "row_number": 3, "status": "ok",
      "normalized_data": {
        "tracking_number": "HNLG5",
        "destination_raw": "Hà Nội", "province_name": "Hà Nội", "province_code": "1",
        "receiver_name": "HẰNG HÒA",
        "address_detail": "B2 10 Shop house 24H Đường Tố Hữu, Phường Hà Đông, Hà Nội.",
        "contact_name": "Hương", "contact_phone": "0949988999",
        "packages": 3, "weight_kg": "43.500", "catalogue_quantity": 150
      }, "warnings": [] },
    { "row_number": 21, "status": "warning",
      "warnings": ["'Hải Dương' → quy đổi 'Hải Phòng'", "Có 1 liên hệ khác → sẽ tạo bình luận"] }
  ]
}
```

### 6.5 Bộ mã lỗi (thêm vào `app/core/i18n.py`)

| Mã | Mức | Thông điệp |
|---|---|---|
| `IMPORT_FILE_REQUIRED` | file | Vui lòng chọn file Excel. |
| `IMPORT_ROW_LIMIT_EXCEEDED` | file | File vượt quá 5.000 dòng dữ liệu. |
| `IMPORT_COLUMNS_NOT_FOUND` | file | Không nhận diện được cột dữ liệu. Thiếu: {columns}. |
| `IMPORT_PROVINCES_NOT_SEEDED` | hệ thống | Danh mục tỉnh/thành chưa được nạp. Chạy `make db-seed` trước khi import. |
| `IMPORT_BATCH_NOT_FOUND` | 404 | Không tìm thấy lần nhập dữ liệu. |
| `IMPORT_BATCH_ALREADY_COMMITTED` | 409 | Lần nhập này đã được xác nhận trước đó. |
| `IMPORT_NOTHING_TO_IMPORT` | 400 | Không có dòng hợp lệ để nhập. |
| `IMPORT_ROW_REQUIRED_EMPTY` | dòng | Cột bắt buộc đang trống: {column}. |
| `IMPORT_TRACKING_INVALID` | dòng | Mã đơn không hợp lệ: "{value}". |
| `IMPORT_DUPLICATE_TRACKING` | cảnh báo | Mã vận đơn "{value}" đã tồn tại — bỏ qua dòng này. |
| `IMPORT_PROVINCE_NOT_FOUND` | dòng | Không khớp tỉnh/thành nào: "{value}". |
| `IMPORT_PHONE_INVALID` | dòng | Số điện thoại không hợp lệ: "{value}". |
| `IMPORT_NUMBER_INVALID` | dòng | Giá trị số không hợp lệ: "{value}". |
| `IMPORT_WEIGHT_INVALID` | dòng | Trọng lượng phải lớn hơn 0. |
| `IMPORT_DUPLICATE_FILE` | cảnh báo | File này đã được nhập ngày {date}. |

> **Tái dùng mã có sẵn, không tạo trùng:** kiểm tra định dạng/kích thước file dùng `FILE_TYPE_NOT_ALLOWED` và `FILE_SIZE_EXCEEDED` (`app/core/exceptions.py`, đã có cho `POST /files/upload`) + `services/storage/validators.py`. Chỉ thêm `IMPORT_ROW_LIMIT_EXCEEDED` vì là giới hạn riêng của import.

### 6.6 Giao dịch & hiệu năng

- **Validate:** không mở transaction ghi nghiệp vụ; chỉ ghi `import_batches` + `import_rows` (1 commit).
- **Commit:** **chunk 200 dòng**, mỗi chunk 1 transaction, mỗi dòng bọc `SAVEPOINT` → 1 dòng lỗi kỹ thuật không làm sập cả chunk.
- **Nạp trước:** `provinces` (34), `customers` theo lô SĐT (`WHERE phone IN (...)` 500 dòng/lần); **không** query từng dòng.
- **Audit:** `import.batch_committed` (1 event/batch) + `bill.imported` (1 event/phiếu, `details={batch_id, row_number}`) qua `audit_crud.log_event`.
- **Mục tiêu:** 1.000 dòng < 10 s; 5.000 dòng < 60 s (chưa tính upload).

### 6.7 Chống import trùng

1. **Theo file:** `SHA-256` nội dung → trùng với batch `completed` trước đó → cảnh báo, cho phép khẳng định lại.
2. **Theo dòng:** `bills.tracking_number` là **UNIQUE** → kiểm tra trước khi ghi; trùng → `skipped` + `IMPORT_DUPLICATE_TRACKING` (vẫn tính vào kết quả, không làm fail batch).
3. **Theo khách:** dedupe bằng `customers.phone` (đúng hành vi `_resolve_customer` hiện tại) — trùng thì **dùng lại khách cũ**, không ghi đè tên/SĐT.

### 6.8 Phân quyền

Thêm 1 action vào `PERMISSION_CATALOG` (module `bill`):

```python
{"code": "bill:import", "label": "Nhập vận đơn từ Excel"}
```

Kèm migration cấp `bill:import` cho vai trò `operator` và `depot_manager` (`admin` đã bypass). Không dùng lại `bill:create` để tránh nhân viên quầy nhập hàng loạt ngoài kiểm soát.

> Quyền là **dòng dữ liệu** trong `role_permissions` (migration `0019`) → thêm code vào catalog **chưa đủ**, phải có migration cấp quyền.

### 6.9 Phải mở rộng phần đang có (bắt buộc)

Theo `docs/conventions.md` §3 (model/schema/crud/service/contract đổi cùng nhau):

| # | File | Thay đổi | Lý do |
|---|---|---|---|
| 1 | `app/services/bill_service.py:create_bill` | Thêm tham số **`tracking_number: str \| None = None`** (truyền xuống crud) | Không có đường ghi mã `HNLG5` |
| 2 | `app/crud/bill.py:create_bill` | Nhận `tracking_number`; dùng nếu có, ngược lại `next_tracking_number(db)`; kiểm tra trùng trước khi insert + bắt `IntegrityError` làm lưới an toàn | Như trên |
| 3 | `app/schemas/bill.py:BillParty` + `app/crud/bill.py:party_snapshot` | Thêm `province_raw: str \| None` (ghi vào snapshot JSONB) | Lưu **tỉnh cũ** cạnh tỉnh mới (§4.2) |
| 4 | `frontend/.../BillCommercialEditor.jsx:formatMetadataLabel` | Bảng nhãn i18n: `catalogue_quantity` → "Số lượng catalogue" | Đang hiện "Catalogue quantity" |
| 5 | `backend/app/static/bill_template.html:74` | Đổi nhãn cột `Số lượng` → **`Số kiện`** | `line.quantity` nay là số kiện |
| 6 | `specs/001-logistics-bill-app/contracts/openapi.yaml` | 6 endpoint + schema import + `BillParty.province_raw` | Contract phải khớp |

> **Không** thêm `tracking_number` vào `BillCreate` (schema HTTP). Để ở **tham số service** thì `POST /bills` không bị mở quyền đặt mã tùy ý, chỉ luồng import dùng được.
> **Không** cần thêm cột `package_count` và **không** dùng `partner_bill_code` nữa (khác v1).

### 6.10 Ảnh hưởng lên in phiếu & hiển thị

| Điểm | Hiện tại | Sau khi import | Việc cần làm |
|---|---|---|---|
| Barcode trên phiếu in | `Code 128` từ `tracking_number` | `HNLG5` → hợp lệ (Code 128 nhận chữ + số) | Không cần sửa — **chỉ cần test in thử** |
| Nhãn cột "Số lượng" trên phiếu in | In `line.quantity` | Nay là **số kiện** | Đổi nhãn → "Số kiện" (§6.9 dòng 5) |
| "Thông tin thêm" của line | `formatMetadata` in `Key: value` | `catalogue_quantity: 150` | Thêm nhãn tiếng Việt (§6.9 dòng 4) |
| In phiếu có metadata không? | **Không** (`bill_template.html` chỉ in description/quantity/weight) | Số lượng catalogue **không xuất hiện trên phiếu in** | Nếu khách cần in → thêm 1 dòng phụ dưới mô tả (task nhỏ — [D-c](#11-việc-cần-quyết-trước-khi-triển-khai)) |

---

## 7. Frontend

### 7.1 Thành phần

| Component | Mô tả |
|---|---|
| `ImportWizard` | `Steps` 3 bước (bỏ bước "tải file mẫu"), giữ state file + batch |
| `ImportUploadStep` | `Upload.Dragger` (chỉ `.xlsx`, ≤ 5 MB) + mô tả layout file được chấp nhận |
| `ImportPreviewTable` | `Table`: Dòng Excel · Mã vận đơn · Khách nhận · Tỉnh (cũ → mới) · SĐT · **Trạng thái (Tag)** · Lỗi/Cảnh báo. Lọc theo trạng thái; `Alert` tổng hợp; nút *Tải file lỗi* |
| `ImportResultPanel` | Số phiếu tạo · số khách tạo mới · số bình luận; nút *Tải file kết quả*, *Xem danh sách phiếu* |

### 7.2 Vị trí

- Nút **"Nhập Excel"** (`ImportOutlined`) trên `BillListPage` — cạnh *Xuất Excel*, gác `bill:import`, mở `ImportWizard` dạng `Modal` rộng.
- Route tùy chọn `/nhap-du-lieu` cho lịch sử import.

### 7.3 Tuân thủ quy ước

antd v5 + component chung, **không** hard-code màu (lấy token từ `AntdConfigProvider`); gọi API qua `src/api/imports.js` (dùng `client` axios sẵn có, upload `FormData`); dữ liệu server qua **React Query**; text tiếng Việt qua `src/i18n/vi.js`.

---

## 8. Kiểm thử

| Loại | File | Nội dung | Case |
|---|---|---|---|
| Unit | `tests/unit/test_import_contacts.py` | 20+ chuỗi **lấy nguyên từ file mẫu** + ca biên (rỗng, chỉ số, 3 người, nháy, `+84`, `Anh` là tên thật) | 30 |
| Unit | `tests/unit/test_import_locations.py` | 34 tỉnh chuẩn, 10 giá trị cần quy đổi, có tiền tố `Tỉnh`/`TP.`, không khớp | 50 |
| Unit | `tests/unit/test_import_normalize.py` | SĐT, trọng lượng float, số nguyên, địa chỉ nguyên văn (không bị sửa) | 25 |
| Unit | `tests/unit/test_import_readers.py` | Dò đúng sheet `Sheet2` (Sheet1 rỗng), bỏ dòng tiêu đề, lấy **giá trị cache** của ô công thức, ghép `B+A` khi C trống | 15 |
| Property | `tests/property/test_import_normalize.py` | `normalize_phone` idempotent; `quantize_weight` không tăng sai số; parse liên hệ không mất SĐT | 4 |
| Integration | `tests/integration/test_import_api.py` | Upload **file mẫu thật** → validate → commit; 403 thiếu quyền; thiếu cột; 1 dòng lỗi không chặn cả file; import lại bị skip; **bình luận liên hệ phụ được tạo**; rollback chunk khi lỗi DB | 20 |
| Contract | `specs/001-logistics-bill-app/contracts/openapi.yaml` | 6 endpoint + schema mới + `BillParty.province_raw` | — |
| Perf | `tests/perf/test_import_perf.py` | 5.000 dòng: validate < 20 s, commit < 60 s | 1 |

**Bộ dữ liệu vàng:** dùng **chính file gốc** `5.11 Mr Hải Logex.xlsx` làm fixture, đối chiếu với sheet "Kết quả mong đợi" trong [`templates/du-lieu-mau-va-ket-qua-mong-doi.xlsx`](./templates/du-lieu-mau-va-ket-qua-mong-doi.xlsx). Kỳ vọng sau commit:

| Kỳ vọng | Số lượng | Vì sao |
|---|---|---|
| Phiếu được tạo | **70** | 70 dòng; dòng `HNLG0-GT` vẫn nhập (chỉ cảnh báo) |
| Khách hàng được tạo | **69** | `CƯỜNG THƠ` 2 dòng cùng SĐT `0938888838` → dùng lại 1 khách |
| Bình luận "Liên hệ khác" | **12** | 12/70 dòng có ≥ 2 người |
| Line item | **70** | mỗi phiếu 1 line: `quantity` = số kiện, `weight_kg` = J, `metadata.catalogue_quantity` = H |
| Dòng lỗi (bị bỏ) | **0** | toàn bộ địa danh quy đổi được |

> **Hạ tầng test — đã kiểm chứng, khác giả định thông thường:**
> - Repo **không có `conftest.py`** ở bất kỳ đâu. Mỗi file integration tự dựng testcontainer PostgreSQL + `Base.metadata.create_all` + fixture autouse `_seed_roles` (xem `tests/integration/test_bill_api.py`). → `test_import_api.py` phải làm theo đúng khuôn đó.
> - DB test mới **không có tỉnh/thành** (không có migration seed) → thêm fixture `_seed_provinces` (insert 34 dòng từ hằng số trong `importing/locations.py`); kèm 1 test cho hành vi **DB rỗng** → `IMPORT_PROVINCES_NOT_SEEDED`.

---

## 9. Kế hoạch triển khai

### 9.1 Phân rã công việc

| GĐ | Nội dung | Phụ trách | Ngày công | Phụ thuộc |
|---|---|---|---|---|
| **P0** | Chốt 2 điểm còn treo (§11) + xác nhận mapping ở sheet "Kết quả mong đợi" | PM + khách | 0.5 | — |
| **P1** | `importing/` **hàm thuần, không I/O DB**: `template.py` (trường logic + từ điển header), `readers.py` (dò sheet/header, đọc cache, ghép B+A), `normalize.py`, `locations.py` (+ bảng quy đổi 34 tỉnh), `contacts.py` | DEV A | 3.0 | P0 |
| **P2** | `validators.py` + model/schema/crud `import_batches`/`import_rows` + migration + đăng ký model/router + API `POST /imports`, `GET /imports`, `GET /imports/{id}`, `.../rows` | DEV A | 2.0 | P1 |
| **P3** | `import_service.commit_batch()` gọi `bill_service.create_bill(tracking_number=…)` + mở rộng `create_bill`/`crud.create_bill`/`BillParty.province_raw` + bình luận liên hệ phụ qua `comment_service` + audit | DEV B | 2.5 | P2 |
| **P4** | File kết quả + 15 mã lỗi i18n + quyền `bill:import` + migration cấp quyền + lịch sử | DEV B | 1.0 | P3 |
| **P5** | `ImportWizard` 3 bước + `ImportPreviewTable` + `ImportResultPanel` + `api/imports.js` + gắn `BillListPage` + nhãn metadata + nhãn in phiếu | DEV FE | 2.5 | P2 (mock) / P4 (thật) |
| **P6** | Test §8 + `openapi.yaml` + wiki + tài liệu hướng dẫn | DEV A + B | 2.0 | P4, P5 |

**Tổng: ~13,5 ngày công** (backend ~9, frontend ~2,5, P0+P6 ~2).

| Cách bố trí | Thời gian lịch |
|---|---|
| 1 backend làm tuần tự | ~13–14 ngày làm việc (~3 tuần) |
| **2 backend song song + 1 frontend** | **~7–8 ngày làm việc ≈ 1,5–2 tuần lịch** |

> Ước lượng thô, chưa gồm thời gian chờ khách chốt và sửa sau UAT. So với v1 giảm ~2,5 ngày nhờ **bỏ chuẩn hoá file**, **không cần migration `package_count`**, **không cần API phát file mẫu**.

### 9.2 Mốc bàn giao

| Đợt | Phạm vi | Tiêu chí nghiệm thu |
|---|---|---|
| **Đợt 1** (sau P2) | Kiểm tra + xem trước | Upload **chính file gốc** → thấy đúng 70 dòng, phân loại OK/CẢNH BÁO/LỖI và lý do tiếng Việt rõ ràng |
| **Đợt 2** (sau P4) | Ghi dữ liệu thật | Import → 70 phiếu mang mã `HNLG5`…, 69 khách, 12 bình luận; tra cứu + in phiếu bằng mã `HNLG5` được; import lại bị chặn trùng |
| **Đợt 3** (sau P6) | Hoàn thiện | Test xanh, giao diện hoàn chỉnh, tài liệu + wiki cập nhật |

### 9.3 Thứ tự ưu tiên nếu cắt phạm vi

1. **Bắt buộc:** import phiếu + validate + commit + liên hệ phụ → bình luận.
2. **Nên có:** file kết quả, chống trùng, lịch sử.
3. **Có thể lùi:** sửa tay trên bảng preview, in "Số lượng catalogue" trên phiếu.

---

## 10. Rủi ro & phương án

| # | Rủi ro | Khả năng | Tác động | Phương án |
|---|---|---|---|---|
| R1 | Parser liên hệ sai với dữ liệu mới | Trung bình | Sai người liên hệ | Đã kiểm chứng 70/70; **luôn lưu `contact_raw`**; sửa tay ở preview (P5+) |
| R2 | Địa danh cũ → mới sai | **Cao** | Giao nhầm tuyến | Bảng quy đổi có kiểm chứng + cảnh báo rõ từng dòng bị quy đổi; địa chỉ giao giữ nguyên văn để shipper đối chiếu |
| R3 | **Mã đơn của khách đụng mã vận đơn nội bộ** | Thấp | Trùng UNIQUE, fail dòng | Tra `get_by_tracking_number` trước; trùng → skip + cảnh báo; `IntegrityError` bắt làm lưới an toàn |
| R4 | **Mã đơn không phải mã vận đơn chuẩn** (`HNLG0-GT` có dấu `-`) | Trung bình | In barcode / tra cứu | Code 128 nhận chữ + số + gạch; **test in thử 3 mã đại diện** ở P6; quy tắc charset chặn ký tự lạ |
| R5 | Phiếu import có **cước = 0** → báo cáo doanh thu sai | **Cao** | Số liệu tài chính | Ghi rõ với khách; tùy chọn tính cước từ bảng giá là task riêng |
| R6 | Dedupe khách lệch do SĐT cũ chưa chuẩn hoá | Trung bình | Trùng hồ sơ khách | Chuẩn hoá SĐT **trước** khi tra; task rà soát SĐT toàn hệ thống |
| R7 | `nextval('bill_tracking_seq')` ngoài transaction → nhảy số (chỉ ảnh hưởng phiếu nhập tay) | Cao | Khoảng trống dãy `NL…` | Chấp nhận; ghi rõ tài liệu |
| R8 | File có layout khác (khách đổi tên cột) | Trung bình | Không import được | Dò header theo **từ điển tên cột** + báo `IMPORT_COLUMNS_NOT_FOUND` kèm danh sách thiếu |
| R9 | DB chưa seed `provinces` | Trung bình | Toàn bộ dòng lỗi khó hiểu | Kiểm tra `count(provinces)` trước; bằng 0 → `IMPORT_PROVINCES_NOT_SEEDED` + hướng dẫn `make db-seed` |

---

## 11. Việc cần quyết trước khi triển khai

### Đã chốt (theo yêu cầu khách)

| # | Nội dung | Quyết định |
|---|---|---|
| **C1** | Định dạng đầu vào | Import **trực tiếp file gốc**, không cần chuẩn hoá file |
| **C2** | Mã đơn | Lưu thành **`bills.tracking_number`** (`HNLG5`) |
| **C3** | Địa điểm | Lưu **tỉnh mới** + **tỉnh cũ**; **địa chỉ chi tiết nguyên văn** đúng Excel |
| **C4** | Số kiện | `bill_content_lines.quantity` |
| **C5** | Trọng lượng | `bill_content_lines.weight_kg` + `bills.actual_weight_kg` |
| **C6** | Số lượng Catalogue | `bill_content_lines.metadata.catalogue_quantity` ("thông tin thêm") |
| **C7** | Liên hệ | 1 người chính vào hồ sơ khách; còn lại → bình luận |

### Còn treo (cần chốt ở P0)

| # | Câu hỏi | Đề xuất ✅ | Phương án khác | Ảnh hưởng |
|---|---|---|---|---|
| **D-a** | Tên đại lý có chuẩn hoá chữ hoa/thường không? (`HẰNG HÒA` → `Hằng Hòa`) | **Giữ nguyên văn** (an toàn, đúng dữ liệu khách); bật `normalize_names: true` nếu muốn | Tự Title Case | Đổi hành vi tìm kiếm/báo cáo; có thể sai tên viết tắt |
| **D-b** | **Người gửi mặc định của công ty là ai?** (`BillCreate.sender` bắt buộc nhưng file không có) | Dùng `settings.CARRIER_NAME` / `CARRIER_HOTLINE` → tự tạo 1 khách hàng công ty và dùng lại | Bắt nhập cột người gửi / tạo khách riêng theo từng đại lý | Không có thì **không tạo được phiếu** |
| **D-c** | Có in "Số lượng catalogue" lên phiếu in không? | **Không** ở giai đoạn 1 (chỉ hiện ở "thông tin thêm" trên web) | Thêm dòng phụ dưới mô tả trên phiếu | Cần sửa `bill_template.html` + test in |

> **Đã tự giải quyết:** cước = 0 (file không có cột cước) — chấp nhận, ghi cảnh báo trên preview; rủi ro doanh thu ghi ở R5.

---

## 12. Phụ lục

### 12.1 File đối chiếu đi kèm

| File | Mục đích |
|---|---|
| [`templates/du-lieu-mau-va-ket-qua-mong-doi.xlsx`](./templates/du-lieu-mau-va-ket-qua-mong-doi.xlsx) | **Dùng ngay ở giai đoạn 1.** 3 sheet: `1. File gốc` (70 dòng nguyên trạng) · `2. Kết quả mong đợi` (từng dòng sẽ ghi vào đâu: mã vận đơn, tỉnh cũ→mới, địa chỉ nguyên văn, người liên hệ chính, liên hệ khác, số kiện, trọng lượng, SL catalogue, cảnh báo) · `3. Quy đổi địa danh` (10 giá trị) |
| [`templates/import-excel-mau-chuan.xlsx`](./templates/import-excel-mau-chuan.xlsx) | **Để dành giai đoạn 2** — file mẫu chuẩn hoá 24 cột cho người dùng nhập tay (xem §12.4) |

### 12.2 Số liệu chuẩn hoá 70 dòng

| Chỉ số | Số dòng |
|---|---|
| Tổng dòng dữ liệu | 70 |
| Tách được SĐT người liên hệ chính | 70 |
| Có tên người liên hệ | 62 |
| Có thêm liên hệ khác → sinh bình luận | 12 |
| Địa điểm phải quy đổi do sáp nhập tỉnh | 12 |
| Địa điểm là thành phố thuộc tỉnh ("Hạ Long") | 1 |
| Địa điểm là bưu cục nội bộ ("Chi Nhánh HN") | 1 |
| Trọng lượng có sai số float (đã quantize) | 46 |
| Tên đại lý VIẾT HOA toàn bộ (giữ nguyên) | 58 |
| Khách hàng duy nhất (dedupe theo SĐT) | 69 |
| Line item | 70 |

### 12.3 Lệnh kiểm chứng sau khi triển khai

```bash
cd veloxship/backend && . venv/bin/activate

# Test module import
pytest tests/unit/test_import_*.py tests/integration/test_import_api.py -v

# Import thử file gốc rồi so với sheet "Kết quả mong đợi"
python -m app.scripts.check_import "../5.11 Mr Hải Logex.xlsx" --dry-run

# Toàn bộ
cd .. && make lint-all && make format-all && make test
cd frontend && npm run build && npm run lint
```

### 12.4 Giai đoạn 2 — chuẩn hoá file nguồn (KHÔNG làm ở giai đoạn 1)

Khi cần phát hành file mẫu cho người dùng tự nhập tay (thay vì import file cũ), dùng lại [`templates/import-excel-mau-chuan.xlsx`](./templates/import-excel-mau-chuan.xlsx) — đã thiết kế sẵn 4 sheet (`Hướng dẫn` / `Danh mục` / `Phiếu gửi` 24 cột / `Khách hàng` 10 cột), dropdown, header 2 màu bắt buộc–tùy chọn. Khi đó bổ sung:

- Adapter thứ 2 trong `readers.py` cho layout chuẩn (kiến trúc đã mở).
- Endpoint `GET /api/v1/imports-templates/{entity_type}` **sinh file mẫu từ `template.py`** (không lưu tĩnh để khỏi lệch với parser).
- Import Khách hàng độc lập.

### 12.5 Kết quả review độc lập với mã nguồn (v1, phần lớn vẫn áp dụng)

Các nhận định về codebase đã được review chéo bằng cách đọc trực tiếp source. **12/14 nhận định đúng, 2 chưa chính xác** (đã sửa), **12 khoảng trống bị bỏ sót đã bổ sung**. Những điểm còn nguyên giá trị ở v2:

| Phát hiện | Trạng thái ở v2 |
|---|---|
| 34 tỉnh **không seed bằng migration** → DB test rỗng | Giữ: `IMPORT_PROVINCES_NOT_SEEDED` + fixture `_seed_provinces` (§8) |
| Đã có hạ tầng upload + allowlist `.xlsx` + mã `FILE_*` | Giữ: tái dùng, không tạo mã trùng (§6.5) |
| Dựng `Comment(...)` trực tiếp bỏ qua sanitize `nh3` | Giữ: dùng `comment_service` (§5.3) |
| **Không có `conftest.py`**; integration test tự dựng testcontainer | Giữ: ghi chú hạ tầng test (§8) |
| Model mới phải đăng ký ở `app/models/__init__.py`; router ở `main.py`; mã lỗi phải có message | Giữ (§6.2) |
| `nextval` ngoài transaction → nhảy số | Giữ: rủi ro R7 |
| Tên bảng là `bill_status_logs` (không phải `bill_status_events`) | Giữ |
| Lớp `handlers/` không có tiền lệ → bỏ | Giữ: reshape theo `services/storage/` (§6.2) |
| Migration không tự đặt số | Giữ (§6.3) |
| ~~`partner_bill_code` không hiện trong `BillRead`/search/export~~ | **Không còn áp dụng** — v2 dùng `tracking_number`, vốn đã có trong `BillRead` + tìm kiếm + export |
| ~~`BillCreate` không có đường ghi `partner_bill_code`, `package_count`~~ | **Không còn áp dụng** — v2 chỉ cần thêm tham số `tracking_number` ở tầng service |

### 12.6 Nhật ký triển khai & sai lệch so với kế hoạch

Triển khai ngày **05/11/2026**.

| GĐ | Nội dung | Trạng thái |
|---|---|---|
| P0 | Chốt quyết định | ✅ Theo yêu cầu khách (C1–C7); D-a giữ nguyên tên, D-b dùng `settings.CARRIER_NAME/HOTLINE`, D-c không in SL catalogue |
| P1 | Package `importing/` (template, readers, normalize, locations, contacts, validators) | ✅ Xong — 6 module thuần, không I/O DB |
| P2 | `validators` + model/schema/crud + migration + API validate/list/get/rows | ✅ Xong |
| P3 | `commit_batch` + mở rộng `create_bill`/`BillParty`/snapshot + bình luận + audit | ✅ Xong |
| P4 | File kết quả + mã lỗi + quyền + đăng ký router/model | ✅ Xong |
| P5 | Frontend wizard 3 bước + nút Nhập Excel + nhãn metadata | ✅ Xong |
| P6 | Test + contract + tài liệu | ⚠️ Unit test xong; **integration chưa chạy** |

**File backend:**

```
mới  app/services/importing/{__init__,template,readers,normalize,contacts,locations,validators}.py
mới  app/services/import_service.py
mới  app/api/v1/imports.py
mới  app/models/import_batch.py          → ImportBatch, ImportRow
mới  app/schemas/import_batch.py
mới  app/crud/import_batch.py
mới  alembic/versions/0021_add_import_batches.py
mới  alembic/versions/0022_grant_bill_import_permission.py
sửa  app/services/bill_service.py        → create_bill(tracking_number=…), _resolve_customer(contact_*)
sửa  app/crud/bill.py                    → create_bill(tracking_number=…), party_snapshot(+province_raw/contact_*)
sửa  app/schemas/bill.py                 → BillParty(+province_raw/contact_name/contact_raw), CustomerRef(+province_raw)
sửa  app/schemas/customer.py             → CustomerCreate(+contact_name/contact_raw)
sửa  app/crud/customer.py                → _build_metadata(+contact_*)
sửa  app/models/__init__.py, app/main.py, app/core/permissions.py, app/core/i18n.py
mới  tests/unit/test_import_{normalize,contacts,locations,readers,validators}.py   (188 case)
mới  tests/integration/test_import_api.py                                          (~20 case)
mới  tests/fixtures/import-mr-hai-logex.xlsx
sửa  specs/001-logistics-bill-app/contracts/openapi.yaml                           (+5 path, +4 schema)
```

**File frontend:** `src/api/imports.js`, `src/features/imports/` (wizard + 3 bước + `importStatus.js` + test), `BillListPage.jsx` (nút *Nhập Excel*), `BillCommercialEditor.jsx` (nhãn i18n), `src/i18n/vi.js`, `src/styles/global.css`.

**Sai lệch so với kế hoạch (đã cân nhắc):**

| # | Sai lệch | Lý do |
|---|---|---|
| 1 | `import_batches` thêm `customers_created` và `warnings` | Panel kết quả cần "khách mới"; cảnh báo trùng file ở cấp batch |
| 2 | Khoá JSON trả về là **`normalized_data`** (kế hoạch ghi `normalized`) | Trùng tên cột DB; FE dùng thống nhất |
| 3 | `create_batch` append qua **relationship** thay vì `db.add(row)` | Tránh lazy-load trong async session khi trả preview |
| 4 | Service **không tự `commit()`** — chỉ `flush()` | `get_db` sở hữu transaction boundary (quy ước repo) |
| 5 | Migration dùng **tên constraint không tiền tố** (`name="status"`) | Naming convention tự thêm `ck_<table>_`; truyền tên đầy đủ sẽ bị nhân đôi (conventions §4.2) |
| 6 | `skip_error_rows` hiện luôn bỏ dòng LỖI | Tham số giữ chỗ cho tương lai; dòng lỗi không bao giờ được ghi |

**Chưa kiểm chứng được trên máy này:**

- **Integration test** `tests/integration/test_import_api.py` — cần Docker/testcontainers; `docker ps` timeout 15 s không phản hồi ⇒ **chưa chạy lần nào**. Phải chạy ở máy có Docker trước khi bàn giao.
- **Chưa chạy `alembic upgrade head` thật** — mới kiểm tra `alembic upgrade 0020:0022 --sql`.
- **Chưa smoke test UI thật** — FE mới kiểm bằng unit test + build.
- **Chưa in thử barcode** với mã `HNLG5` / `HNLG0-GT`.

**Lỗi phát hiện sau triển khai (khách test trên trình duyệt):**

| Triệu chứng | Nguyên nhân gốc | Sửa |
|---|---|---|
| Kéo file `.xlsx` vào → báo **"Dữ liệu không hợp lệ"** (mã `VALIDATION_ERROR`, 400) | `src/api/client.js` đặt mặc định `Content-Type: application/json`. Axios 1.x thấy FormData + JSON content-type thì **serialize FormData thành JSON** (`axios/lib/defaults/index.js:56`: `hasJSONContentType ? JSON.stringify(formDataToJSON(data)) : data`) ⇒ trình duyệt gửi `{"file": {}}`, **không có part file** ⇒ FastAPI trả 422 ⇒ handler đổi thành 400 `VALIDATION_ERROR` | `validateImport()` override `headers: { 'Content-Type': 'multipart/form-data' }` (đúng pattern `uploadFile()` trong `api/files.js`). Thêm `src/api/imports.test.js` (6 case) pin hành vi qua **adapter thật của axios** — đã kiểm chứng test **fail khi bỏ fix** và pass khi khôi phục |
| Thông báo lỗi chung chung, không biết sai ở đâu | FE chỉ hiện `data.message` | Thêm `importErrorMessage()` nối thêm `details.errors[0]` ⇒ hiện `"Dữ liệu không hợp lệ. (file: Field required)"` |

> Unit test cũ **không bắt được** lỗi này vì `ImportWizard` test mock cả module `api/imports`. Đây là lý do cần smoke test UI thật trước khi bàn giao.

### 12.7 Bổ sung tuỳ chọn **Người gửi** (sau phản hồi của khách)

Bản đầu tiên luôn dùng người gửi mặc định của công ty (`settings.CARRIER_NAME` / `CARRIER_HOTLINE`, hiện là "Vận Chuyển HN") vì file gốc không có cột người gửi. Khách yêu cầu nhập được người gửi cụ thể (VD `Mr Hải: 0392492229`), nên đã bổ sung **3 đường**, ưu tiên từ trên xuống:

| # | Nguồn | Cách dùng |
|---|---|---|
| 1 | **Cột trong file Excel** | `Người gửi` + `SĐT người gửi` (tách cột), hoặc **một cột gộp** `Mr Hải: 0392492229`. File không có cột thì bỏ qua |
| 2 | **Tuỳ chọn khi import** | Ô "Người gửi" / "SĐT người gửi" ở bước tải file (gửi lên qua `options.sender_name` / `options.sender_phone`) |
| 3 | **Mặc định công ty** | `settings.CARRIER_NAME` / `CARRIER_HOTLINE` |

Điểm kỹ thuật đáng lưu ý:

- Người gửi dùng `parse_sender()` — **giữ nguyên danh xưng** (`Mr Hải` ở lại `Mr Hải`), khác `parse_contact()` dùng cho người nhận (bỏ "Chị/Anh/Mr" để lưu tên người liên hệ).
- Thứ tự kiểm tra: cột gộp → cột SĐT riêng → tuỳ chọn → mặc định. Chỉ cảnh báo "không đọc được SĐT người gửi" **sau khi** đã xét cột SĐT riêng (nếu không, file 2 cột sẽ báo cảnh báo giả cho cả 70 dòng).
- File mẫu mới: [`templates/5.11 Mr Hai Logex - co nguoi gui.xlsx`](./templates/5.11%20Mr%20Hai%20Logex%20-%20co%20nguoi%20gui.xlsx) — đúng 70 dòng của file gốc + 2 cột `Người gửi` = `Mr Hải`, `SĐT người gửi` = `0392492229`.
- Hiển thị: bảng **preview** trong wizard có thêm cột **Người gửi** (tên + SĐT; dòng không có thì hiện "Mặc định"), và **file Excel kết quả** có thêm 2 cột `Người gửi` / `SĐT người gửi` (16 cột).
- Kiểm chứng: 361 unit test backend pass (+15 case người gửi), 49 test frontend pass (+2 case); upload thật qua API trả `sender='Mr Hải'` cho cả 70 dòng, snapshot phiếu tạo ra có `name: "Mr Hải"`, file kết quả 16 cột khớp header/dữ liệu.
