# Requirements Document — Quản lý Đội xe (Vehicles Management)

## Introduction

Chức năng quản lý CRUD cho đội xe vận chuyển của Hoàng Nam Express. Sử dụng bảng `vehicles` hiện có (không thay đổi schema), cung cấp API backend và giao diện frontend để Admin tạo, xem, sửa, và vô hiệu hóa (soft-delete) các phương tiện trong hệ thống.

## Glossary

- **Vehicle**: Phương tiện vận chuyển trong hệ thống (xe tải hoặc xe máy) — tương ứng bảng `vehicles`
- **Admin**: Người dùng có quyền quản trị hệ thống (quản lý đội xe)
- **Vehicle_API**: Nhóm endpoint REST tại `/api/v1/vehicles` xử lý nghiệp vụ vehicle
- **Vehicle_Frontend**: Giao diện quản lý đội xe trong feature folder `src/features/vehicles/`
- **Driver**: Người dùng (bảng `users`) được gán phụ trách phương tiện — tham chiếu qua `driver_id`
- **Depot**: Điểm giao nhận hàng hóa — bảng `depots`, tham chiếu qua `latest_depot_id`
- **Vehicle_Type**: Loại phương tiện, giá trị cho phép: `motorcycle` (xe máy) hoặc `truck` (xe tải)
- **Vehicle_Status**: Trạng thái phương tiện, giá trị cho phép: `active` (hoạt động), `inactive` (ngưng hoạt động), `maintenance` (bảo trì)
- **Pagination**: Phân trang kết quả danh sách với page/page_size

## Requirements

### Requirement 1: Xem danh sách Vehicle

**User Story:** As an Admin, I want to view all vehicles in a paginated list with search and filter, so that I can quickly find and manage vehicle information.

#### Acceptance Criteria

1. WHEN the Admin sends GET /api/v1/vehicles, THE Vehicle_API SHALL return a paginated list of vehicles sorted by created_at descending, including id, license_plate, vehicle_type, max_weight_kg, max_volume_m3, driver name, depot name, and status.
2. WHEN the Admin provides a search query parameter (between 1 and 100 characters), THE Vehicle_API SHALL filter vehicles where license_plate matches the search string (case-insensitive) and return matching results.
3. WHERE the Admin provides a status filter parameter (one of: active, inactive, maintenance), THE Vehicle_API SHALL return only vehicles matching the specified status.
4. WHERE the Admin provides a vehicle_type filter parameter (one of: motorcycle, truck), THE Vehicle_API SHALL return only vehicles matching the specified vehicle type.
5. WHERE the Admin provides a latest_depot_id filter parameter, THE Vehicle_API SHALL return only vehicles assigned to the specified depot.
6. THE Vehicle_API SHALL support Pagination with configurable page_size (minimum 1, default 20, maximum 100) and return metadata including total count, current page, and page size.
7. IF the page or page_size parameters are invalid (non-integer, less than minimum, or exceeding maximum), THEN THE Vehicle_API SHALL return a validation error with status 422.
8. IF no vehicles match the applied filters or search criteria, THEN THE Vehicle_API SHALL return an empty list with total count of 0.
9. WHEN multiple filters are applied simultaneously (search, status, vehicle_type, latest_depot_id), THE Vehicle_API SHALL combine them using AND logic.
10. THE Vehicle_API SHALL join vehicles with users table to resolve driver_id into the driver full name, and join with depots table to resolve latest_depot_id into the depot name in the response.

### Requirement 2: Tạo mới Vehicle

**User Story:** As an Admin, I want to register a new vehicle with all required information, so that the system can track a new transport vehicle.

#### Acceptance Criteria

1. WHEN the Admin sends POST /api/v1/vehicles with a valid request body, THE Vehicle_API SHALL create a new vehicle record with the provided license_plate, vehicle_type, max_weight_kg, and max_volume_m3 fields.
2. THE Vehicle_API SHALL require license_plate, vehicle_type, max_weight_kg, and max_volume_m3 as mandatory fields in the request body.
3. THE Vehicle_API SHALL accept latest_depot_id, driver_id, and status as optional fields in the request body.
4. THE Vehicle_API SHALL validate that license_plate is a non-empty string.
5. THE Vehicle_API SHALL validate that vehicle_type is one of the allowed values: motorcycle or truck.
6. THE Vehicle_API SHALL validate that max_weight_kg is a positive number with maximum 12 digits and 3 decimal places.
7. THE Vehicle_API SHALL validate that max_volume_m3 is a positive number with maximum 8 digits and 2 decimal places.
8. IF the submitted license_plate already exists in the vehicles table, THEN THE Vehicle_API SHALL return a ConflictError with error_code "VEHICLE_LICENSE_PLATE_EXISTS" and message "Biển số xe đã tồn tại trong hệ thống".
9. IF the submitted driver_id is not null and does not reference an existing active user in the users table, THEN THE Vehicle_API SHALL return a validation error with error_code "DRIVER_NOT_FOUND" and message "Tài xế không tồn tại hoặc không hoạt động".
10. IF the submitted latest_depot_id is not null and does not reference an existing depot in the depots table, THEN THE Vehicle_API SHALL return a validation error with error_code "DEPOT_NOT_FOUND" and message "Bưu cục không tồn tại".
11. WHEN a vehicle is created successfully, THE Vehicle_API SHALL set status to "active" by default (if not provided) and return the created vehicle record including its generated id with status 201.

### Requirement 3: Cập nhật thông tin Vehicle

**User Story:** As an Admin, I want to update vehicle information including status and driver assignment, so that I can keep vehicle details current.

#### Acceptance Criteria

1. WHEN the Admin sends PATCH /api/v1/vehicles/{id} with a valid request body, THE Vehicle_API SHALL update only the fields present in the request body and set the updated_at timestamp to the current server time.
2. THE Vehicle_API SHALL allow updating the following fields via PATCH: license_plate, vehicle_type, max_weight_kg, max_volume_m3, latest_depot_id, driver_id, and status.
3. IF the vehicle id does not exist, THEN THE Vehicle_API SHALL return a NotFoundError with error_code "VEHICLE_NOT_FOUND" and message "Không tìm thấy phương tiện".
4. THE Vehicle_API SHALL validate updated fields using the same rules as creation: license_plate non-empty, vehicle_type in allowed values, max_weight_kg positive, max_volume_m3 positive.
5. IF the updated license_plate already exists on a different vehicle, THEN THE Vehicle_API SHALL return a ConflictError with error_code "VEHICLE_LICENSE_PLATE_EXISTS" and message "Biển số xe đã tồn tại trong hệ thống".
6. IF driver_id is provided and does not reference an existing active user, THEN THE Vehicle_API SHALL return a validation error with error_code "DRIVER_NOT_FOUND" and message "Tài xế không tồn tại hoặc không hoạt động".
7. IF latest_depot_id is provided and does not reference an existing depot, THEN THE Vehicle_API SHALL return a validation error with error_code "DEPOT_NOT_FOUND" and message "Bưu cục không tồn tại".
8. WHEN the update succeeds, THE Vehicle_API SHALL return the updated vehicle record with status 200.

### Requirement 4: Xóa mềm Vehicle (Soft Delete)

**User Story:** As an Admin, I want to deactivate a vehicle via the "Xóa" action, so that vehicles no longer in use are hidden from active operations without losing historical data.

#### Acceptance Criteria

1. WHEN the Admin triggers the "Xóa" action on a vehicle, THE Vehicle_Frontend SHALL send a PATCH /api/v1/vehicles/{id} request with status set to "inactive".
2. IF the vehicle id does not exist, THEN THE Vehicle_API SHALL return a NotFoundError with error_code "VEHICLE_NOT_FOUND" and message "Không tìm thấy phương tiện".
3. IF the vehicle already has status equal to "inactive", THEN THE Vehicle_API SHALL return the current vehicle record without modification and preserve the existing updated_at timestamp.

### Requirement 5: Giao diện Frontend Quản lý Đội xe

**User Story:** As an Admin, I want a user-friendly interface to manage vehicles, so that I can perform all CRUD operations efficiently.

#### Acceptance Criteria

1. THE Vehicle_Frontend SHALL be structured under `src/features/vehicles/` following the feature-folder pattern with subdirectories for components, pages, and schema.
2. THE Vehicle_Frontend SHALL display a data table using Ant Design Table component with columns for: Biển số xe (license_plate), Loại xe (vehicle_type), Tải trọng (max_weight_kg), Thể tích (max_volume_m3), Tài xế phụ trách (driver name), Trạng thái (status), and action buttons (Sửa, Xóa), supporting pagination with default page size of 20 rows.
3. WHEN the Admin clicks "ĐĂNG KÝ XE MỚI", THE Vehicle_Frontend SHALL show a modal form with fields: license_plate (text input), vehicle_type (select: Xe máy/Xe tải), max_weight_kg (number input), max_volume_m3 (number input), latest_depot_id (depot select), driver_id (driver select), and status (select).
4. WHEN the Admin clicks "Sửa" on a vehicle row, THE Vehicle_Frontend SHALL show a pre-filled edit modal with all editable fields populated from the selected vehicle's current data.
5. THE Vehicle_Frontend SHALL validate form inputs client-side using react-hook-form with zod schema resolver before submission, and IF validation fails, THEN display inline error messages in Vietnamese adjacent to each invalid field and prevent form submission.
6. WHEN the Admin types in the search input, THE Vehicle_Frontend SHALL filter the vehicle table by license_plate with a 300ms debounce before triggering the API call.
7. THE Vehicle_Frontend SHALL provide filter dropdowns for status (Tất cả / Hoạt động / Ngưng hoạt động / Bảo trì) and vehicle_type (Tất cả / Xe máy / Xe tải).
8. THE Vehicle_Frontend SHALL use TanStack Query for all API data fetching, caching, and mutation state management.
9. THE Vehicle_Frontend SHALL display all labels, placeholders, messages, and errors in Vietnamese sourced from the i18n configuration (src/i18n/vi.js).
10. WHEN the Admin submits a create or edit form and the API call succeeds, THE Vehicle_Frontend SHALL close the modal, invalidate the vehicle list query to refresh data, and display a success notification using Ant Design message component.
11. IF the API call for creating or updating a vehicle fails, THEN THE Vehicle_Frontend SHALL display an error notification with the error message from the API response and preserve the form data without closing the modal.
12. WHEN the Admin clicks "Xóa" on a vehicle row, THE Vehicle_Frontend SHALL show a confirmation dialog, and WHEN confirmed, send the soft-delete request (PATCH with status "inactive").
