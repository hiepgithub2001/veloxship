# Requirements Document — Quản lý Trung tâm/Chi nhánh/Bưu cục (UC-WEB-07)

## Introduction

Chức năng quản lý CRUD cơ bản cho hệ thống điểm giao nhận (depot) của Hoàng Nam Express. Sử dụng bảng `depots` hiện có (không thay đổi schema), cung cấp API backend và giao diện frontend để Admin tạo, xem, sửa, kích hoạt/vô hiệu hóa các depot.

## Glossary

- **Depot**: Điểm giao nhận hàng hóa trong hệ thống (trung tâm, chi nhánh, hoặc bưu cục) — tương ứng bảng `depots`
- **Admin**: Người dùng có quyền quản trị hệ thống (quản lý cài đặt depot)
- **Depot_API**: Nhóm endpoint REST tại `/api/v1/depots` xử lý nghiệp vụ depot
- **Depot_Frontend**: Giao diện quản lý depot trong feature folder `src/features/depots/`
- **Ward**: Đơn vị hành chính phường/xã — bảng `wards` (code PK, name, district_code FK)
- **District**: Đơn vị hành chính quận/huyện — bảng `districts` (code PK, name, province_code FK)
- **Province**: Đơn vị hành chính tỉnh/thành phố — bảng `provinces` (code PK, name)
- **Pagination**: Phân trang kết quả danh sách với page/page_size
- **Diacritics_Insensitive_Search**: Tìm kiếm không phân biệt dấu tiếng Việt (sử dụng PostgreSQL unaccent extension)

## Requirements

### Requirement 1: Xem danh sách Depot

**User Story:** As an Admin, I want to view all depots in a paginated list with search and filter, so that I can quickly find and manage depot information.

#### Acceptance Criteria

1. WHEN the Admin sends GET /api/v1/depots, THE Depot_API SHALL return a paginated list of depots sorted by created_at descending, including id, code, name, phone, address_detail, ward name, district name, province name, and is_active status.
2. WHEN the Admin provides a search query parameter (between 1 and 100 characters), THE Depot_API SHALL filter depots where name or code matches using Diacritics_Insensitive_Search and return matching results.
3. WHERE the Admin provides an is_active filter parameter (true or false), THE Depot_API SHALL return only depots matching the specified active status.
4. THE Depot_API SHALL support Pagination with configurable page_size (minimum 1, default 20, maximum 100) and return metadata including total_count, current_page, and total_pages.
5. IF the page or page_size parameters are invalid (non-integer, less than minimum, or exceeding maximum), THEN THE Depot_API SHALL return a validation error with status 422.
6. IF no depots match the applied filters or search criteria, THEN THE Depot_API SHALL return an empty list with total_count of 0.
7. WHEN multiple filters are applied simultaneously (search keyword and is_active), THE Depot_API SHALL combine them using AND logic.
8. THE Depot_API SHALL join depots with wards, districts, and provinces tables to resolve ward_code into human-readable ward name, district name, and province name in the response.

### Requirement 2: Tạo mới Depot

**User Story:** As an Admin, I want to create a new depot with all required information, so that the system can track a new operational point.

#### Acceptance Criteria

1. WHEN the Admin sends POST /api/v1/depots with a valid request body, THE Depot_API SHALL create a new depot record with the provided code, name, phone, and address_detail fields.
2. THE Depot_API SHALL require code, name, phone, and address_detail as mandatory fields in the request body.
3. THE Depot_API SHALL accept ward_code as an optional field in the request body.
4. THE Depot_API SHALL validate that code contains only uppercase alphanumeric characters (A-Z, 0-9) with a length between 3 and 20 characters.
5. THE Depot_API SHALL validate that phone matches Vietnamese phone number format (10 digits starting with 0).
6. THE Depot_API SHALL validate that name has a length between 1 and 255 characters, and address_detail has a length between 1 and 500 characters.
7. IF the submitted code already exists in the depots table, THEN THE Depot_API SHALL return a ConflictError with error_code "DEPOT_CODE_EXISTS" and message "Mã bưu cục đã tồn tại".
8. IF the submitted ward_code is not null and does not exist in the wards table, THEN THE Depot_API SHALL return a validation error with error_code "WARD_NOT_FOUND" and message "Mã phường/xã không hợp lệ".
9. WHEN a depot is created successfully, THE Depot_API SHALL set is_active to true by default and return the created depot record including its generated id with status 201.

### Requirement 3: Cập nhật thông tin Depot

**User Story:** As an Admin, I want to update depot information, so that I can keep depot details current.

#### Acceptance Criteria

1. WHEN the Admin sends PATCH /api/v1/depots/{id} with a valid request body, THE Depot_API SHALL update only the fields present in the request body (name, phone, address_detail, ward_code) and set the updated_at timestamp to the current server time.
2. THE Depot_API SHALL treat the code field as immutable — if the request body includes code, THE Depot_API SHALL ignore it without returning an error.
3. IF the depot id does not exist, THEN THE Depot_API SHALL return a NotFoundError with error_code "DEPOT_NOT_FOUND" and message "Không tìm thấy bưu cục".
4. THE Depot_API SHALL validate updated fields using the same rules as creation: name between 1 and 255 characters, phone in Vietnamese format (10 digits starting with 0), address_detail between 1 and 500 characters.
5. IF ward_code is provided and does not exist in the wards table, THEN THE Depot_API SHALL return a validation error with error_code "WARD_NOT_FOUND" and message "Mã phường/xã không hợp lệ".
6. WHEN the update succeeds, THE Depot_API SHALL return the updated depot record with status 200.

### Requirement 4: Kích hoạt / Vô hiệu hóa Depot

**User Story:** As an Admin, I want to activate or deactivate a depot, so that I can control which depots are operational without deleting data.

#### Acceptance Criteria

1. WHEN the Admin sends PATCH /api/v1/depots/{id} with is_active field in the request body, THE Depot_API SHALL update the is_active status of the specified depot and return the updated record.
2. IF the depot id does not exist, THEN THE Depot_API SHALL return a NotFoundError with error_code "DEPOT_NOT_FOUND" and message "Không tìm thấy bưu cục".
3. IF the depot already has the requested is_active status, THEN THE Depot_API SHALL return the current depot record without modification and preserve the existing updated_at timestamp.
4. WHILE a depot has is_active equal to false, THE Depot_API SHALL exclude that depot from selection lists used in operational workflows (e.g., vehicle assignment, bill creation origin/destination selection).
5. WHILE a depot has is_active equal to false, THE Depot_Frontend SHALL display the depot with a visual "Ngưng hoạt động" badge in the list table.

### Requirement 5: Giao diện Frontend Quản lý Depot

**User Story:** As an Admin, I want a user-friendly interface to manage depots, so that I can perform all CRUD operations efficiently.

#### Acceptance Criteria

1. THE Depot_Frontend SHALL be structured under `src/features/depots/` following the feature-folder pattern with subdirectories for components, pages, and schema.
2. THE Depot_Frontend SHALL display a data table using Ant Design Table component with columns for code, name, phone, address, ward/district/province, and status (is_active), supporting sorting on columns and pagination with default page size of 20 rows.
3. WHEN the Admin clicks "Thêm mới", THE Depot_Frontend SHALL show a modal form with fields: code (text input), name (text input), phone (text input), address_detail (text input), and ward selection (cascading selectors: province → district → ward).
4. WHEN the Admin clicks "Sửa" on a depot row, THE Depot_Frontend SHALL show a pre-filled edit modal with all editable fields populated from the selected depot's current data, with the code field displayed as read-only.
5. THE Depot_Frontend SHALL validate form inputs client-side using react-hook-form with zod schema resolver before submission, and IF validation fails, THEN display inline error messages in Vietnamese adjacent to each invalid field and prevent form submission.
6. WHEN the Admin types in the search input, THE Depot_Frontend SHALL filter the depot table using Diacritics_Insensitive_Search with a 300ms debounce before triggering the API call.
7. THE Depot_Frontend SHALL use TanStack Query for all API data fetching, caching, and mutation state management.
8. THE Depot_Frontend SHALL display all labels, placeholders, messages, and errors in Vietnamese sourced from the i18n configuration (src/i18n/vi.js).
9. WHEN the Admin submits a create or edit form and the API call succeeds, THE Depot_Frontend SHALL close the modal, invalidate the depot list query to refresh data, and display a success notification using Ant Design message component.
10. IF the API call for creating or updating a depot fails, THEN THE Depot_Frontend SHALL display an error notification with the error message from the API response and preserve the form data without closing the modal.
