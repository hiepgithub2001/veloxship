# Implementation Plan: Vehicles Management (Quản lý Đội xe)

## Overview

Implement CRUD operations for vehicle management using the existing `vehicles` table. Backend in Python/FastAPI following the layered architecture (api → services → crud → models). Frontend in React with Ant Design, react-hook-form + zod, and TanStack Query. All UI strings in Vietnamese. Model already exists at `backend/app/models/vehicle.py` — no model or migration needed.

## Tasks

- [x] 1. Backend schemas and error codes
  - [x] 1.1 Create Pydantic schemas in `app/schemas/vehicle.py`
    - Define `VehicleCreate`, `VehicleUpdate`, `VehicleRead`, `VehiclePage` schemas
    - Use `Decimal` for `max_weight_kg` and `max_volume_m3`
    - Add field validators: license_plate non-empty, vehicle_type in (motorcycle, truck), max_weight_kg positive, max_volume_m3 positive, status in (active, inactive, maintenance)
    - Use `model_config = {"from_attributes": True}` for `VehicleRead`
    - `latest_linehaul_id` is NOT exposed in any schema
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4_

  - [x] 1.2 Register error codes in `app/core/i18n.py`
    - Add `VEHICLE_NOT_FOUND`: "Không tìm thấy phương tiện."
    - Add `VEHICLE_LICENSE_PLATE_EXISTS`: "Biển số xe đã tồn tại trong hệ thống."
    - Add `DRIVER_NOT_FOUND`: "Tài xế không tồn tại hoặc không hoạt động."
    - Add `DEPOT_NOT_FOUND`: "Bưu cục không tồn tại." (check if already exists from depot module, skip if so)
    - _Requirements: 2.8, 2.9, 2.10, 3.3, 3.5, 3.6, 3.7, 4.2_

- [x] 2. Backend CRUD layer
  - [x] 2.1 Create `app/crud/vehicle.py` with data access functions
    - Implement `list_vehicles` with pagination, case-insensitive search on license_plate, status/vehicle_type/latest_depot_id filters (AND logic)
    - Implement `get_vehicle` by id, `get_vehicle_by_license_plate` by license_plate
    - Implement `create_vehicle` inserting new record
    - Implement `update_vehicle` with partial update logic (only set provided fields)
    - Implement `_load_driver_depot` helper to batch-load driver_name (from users) and depot_name (from depots)
    - Sort by `created_at` descending
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 1.9, 1.10, 3.1_

- [x] 3. Backend service layer
  - [x] 3.1 Create `app/services/vehicle_service.py` with business logic
    - `create_vehicle`: check license_plate uniqueness (ConflictError), validate driver_id exists & is active (AppError DRIVER_NOT_FOUND), validate latest_depot_id exists (AppError DEPOT_NOT_FOUND), set default status='active', delegate to crud
    - `update_vehicle`: get vehicle (NotFoundError), check license_plate uniqueness excluding self, validate driver_id if provided, validate latest_depot_id if provided, handle status idempotency (skip update if only status provided and same value to preserve updated_at), delegate to crud
    - _Requirements: 2.1, 2.8, 2.9, 2.10, 2.11, 3.1, 3.3, 3.5, 3.6, 3.7, 4.1, 4.3_

- [x] 4. Backend API router
  - [x] 4.1 Create `app/api/v1/vehicles.py` with REST endpoints
    - `GET /api/v1/vehicles` — query params: page, page_size, search, status, vehicle_type, latest_depot_id; returns VehiclePage
    - `POST /api/v1/vehicles` — body: VehicleCreate; returns VehicleRead with status 201
    - `PATCH /api/v1/vehicles/{id}` — body: VehicleUpdate; returns VehicleRead with status 200
    - Validate page/page_size constraints (page >= 1, page_size 1–100), return 422 on invalid
    - Add proper type hints, dependency injection for db session
    - _Requirements: 1.1, 1.6, 1.7, 2.1, 2.11, 3.1, 3.8, 4.1_

  - [x] 4.2 Wire vehicle router in `app/main.py`
    - Import and include the vehicle router with prefix `/api/v1/vehicles` and tag "vehicles"
    - _Requirements: all_

- [x] 5. Checkpoint - Backend verification
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Backend tests
  - [x] 6.1 Create unit tests in `tests/unit/test_vehicle_schemas.py`
    - Test license_plate validation: non-empty accepted, empty/whitespace rejected
    - Test vehicle_type validation: motorcycle/truck accepted, other values rejected
    - Test max_weight_kg/max_volume_m3: positive accepted, zero/negative rejected
    - Test status validation: active/inactive/maintenance accepted, other rejected
    - _Requirements: 2.4, 2.5, 2.6, 2.7_

  - [x] 6.2 Create unit tests in `tests/unit/test_vehicle_service.py`
    - Test duplicate license_plate detection raises ConflictError
    - Test invalid driver_id raises AppError with DRIVER_NOT_FOUND
    - Test invalid latest_depot_id raises AppError with DEPOT_NOT_FOUND
    - Test status idempotency: updated_at unchanged when setting same value
    - Test successful create and update flows
    - _Requirements: 2.8, 2.9, 2.10, 3.5, 3.6, 3.7, 4.3_

  - [x] 6.3 Create integration tests in `tests/integration/test_vehicle_api.py`
    - Test full CRUD flow: create → list → update → soft-delete
    - Test search case-insensitive matching on license_plate
    - Test filter combinations (status + vehicle_type + latest_depot_id)
    - Test pagination parameters and metadata
    - Test driver_name and depot_name resolution in responses
    - Test error responses (duplicate license_plate, not found, invalid driver/depot)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.9, 1.10, 2.8, 3.3, 4.1_

  - [x] 6.4 Write property test for search filter correctness
    - **Property 1: Search filter correctness**
    - Use Hypothesis to generate random license plates and search substrings, verify inclusion/exclusion
    - **Validates: Requirements 1.2**

  - [x] 6.5 Write property test for filter AND composition
    - **Property 2: Filter AND composition**
    - Use Hypothesis to generate vehicle lists with mixed attributes, apply random filter combos, verify AND logic
    - **Validates: Requirements 1.3, 1.4, 1.5, 1.9**

  - [x] 6.6 Write property test for pagination slice correctness
    - **Property 3: Pagination slice correctness**
    - Use Hypothesis to generate dataset sizes + random page/page_size, verify correct slice
    - **Validates: Requirements 1.6**

  - [x] 6.7 Write property test for input validation boundaries
    - **Property 4: Input validation boundary correctness**
    - Use Hypothesis to generate random strings/decimals, verify acceptance iff matching rules
    - **Validates: Requirements 2.4, 2.5, 2.6, 2.7, 3.4**

  - [x] 6.8 Write property test for license plate uniqueness
    - **Property 5: License plate uniqueness**
    - Use Hypothesis to generate duplicate plates, verify conflict error
    - **Validates: Requirements 2.8, 3.5**

  - [x] 6.9 Write property test for partial update field preservation
    - **Property 7: Partial update field preservation**
    - Use Hypothesis to generate random subsets of updatable fields, verify only those change
    - **Validates: Requirements 3.1**

  - [x] 6.10 Write property test for idempotent status toggle
    - **Property 8: Idempotent status toggle**
    - Use Hypothesis to generate vehicles with random status, set same value, verify updated_at unchanged
    - **Validates: Requirements 4.3**

- [x] 7. Frontend API layer and schema
  - [x] 7.1 Create `src/api/vehicles.js` with API functions
    - `getVehicles({ page, pageSize, search, status, vehicleType, latestDepotId })` — GET /api/v1/vehicles
    - `createVehicle(data)` — POST /api/v1/vehicles
    - `updateVehicle(id, data)` — PATCH /api/v1/vehicles/{id}
    - Use existing `src/api/client.js` axios instance
    - _Requirements: 5.8_

  - [x] 7.2 Create `src/features/vehicles/schema.js` with zod validation
    - Define vehicle form schema matching backend validation rules
    - Vietnamese error messages for all validation failures
    - _Requirements: 5.5_

- [x] 8. Frontend components
  - [x] 8.1 Create `src/features/vehicles/components/VehicleStatusBadge.jsx`
    - Display "Hoạt động" (green), "Ngưng hoạt động" (red), or "Bảo trì" (orange) badge using Ant Design Tag
    - _Requirements: 5.2_

  - [x] 8.2 Create `src/features/vehicles/components/VehicleSearchBar.jsx`
    - Search input with 300ms debounce filtering by license_plate
    - _Requirements: 5.6_

  - [x] 8.3 Create `src/features/vehicles/components/VehicleFilters.jsx`
    - Status filter dropdown (Tất cả / Hoạt động / Ngưng hoạt động / Bảo trì)
    - Vehicle type filter dropdown (Tất cả / Xe máy / Xe tải)
    - _Requirements: 5.7_

  - [x] 8.4 Create `src/features/vehicles/components/VehicleTable.jsx`
    - Ant Design Table with columns: Biển số xe, Loại xe, Tải trọng, Thể tích, Tài xế phụ trách, Trạng thái, actions (Sửa, Xóa)
    - Pagination integrated with TanStack Query, default page size 20
    - _Requirements: 5.2_

  - [x] 8.5 Create `src/features/vehicles/components/VehicleFormModal.jsx`
    - Modal form for create and edit modes
    - Fields: license_plate (text), vehicle_type (select), max_weight_kg (number), max_volume_m3 (number), latest_depot_id (depot select), driver_id (driver select), status (select)
    - react-hook-form + zod resolver for validation
    - On success: close modal, invalidate queries, show success notification
    - On error: show error notification, keep modal open with form data preserved
    - Delete confirmation dialog for "Xóa" action → PATCH with status='inactive'
    - _Requirements: 5.3, 5.4, 5.5, 5.10, 5.11, 5.12_

- [x] 9. Frontend page and wiring
  - [x] 9.1 Create `src/features/vehicles/pages/VehicleListPage.jsx`
    - Compose VehicleSearchBar, VehicleFilters, VehicleTable, VehicleFormModal
    - TanStack Query for fetching vehicle list with search/filter/pagination state
    - "ĐĂNG KÝ XE MỚI" button to open create modal
    - _Requirements: 5.1, 5.8_

  - [x] 9.2 Add Vietnamese strings to `src/i18n/vi.js`
    - Add vehicle-related labels, placeholders, messages, error messages
    - _Requirements: 5.9_

  - [x] 9.3 Add vehicle route to `src/routes/`
    - Register vehicle list page route in the app router
    - _Requirements: 5.1_

- [x] 10. Final checkpoint - Full integration verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases
- No database migration needed — using existing `vehicles` table as-is
- `latest_linehaul_id` is NOT exposed in any vehicle CRUD operation (managed by linehaul module)
- Use `Decimal` (not float) for `max_weight_kg` and `max_volume_m3` per conventions
- Check if `DEPOT_NOT_FOUND` error code already exists from depot module before adding

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["3.1"] },
    { "id": 3, "tasks": ["4.1"] },
    { "id": 4, "tasks": ["4.2"] },
    { "id": 5, "tasks": ["6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "6.8", "6.9", "6.10", "7.1", "7.2"] },
    { "id": 6, "tasks": ["8.1", "8.2", "8.3", "8.4"] },
    { "id": 7, "tasks": ["8.5"] },
    { "id": 8, "tasks": ["9.1", "9.2"] },
    { "id": 9, "tasks": ["9.3"] }
  ]
}
```
