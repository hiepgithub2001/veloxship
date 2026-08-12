# Implementation Plan: Depot Management (UC-WEB-07)

## Overview

Implement CRUD operations for depot management using the existing `depots` table. Backend in Python/FastAPI following the layered architecture (api → services → crud → models). Frontend in React with Ant Design, react-hook-form + zod, and TanStack Query. All UI strings in Vietnamese.

## Tasks

- [x] 1. Backend schemas and error codes
  - [x] 1.1 Create Pydantic schemas in `app/schemas/depot.py`
    - Define `DepotCreate`, `DepotUpdate`, `DepotRead`, `DepotPage` schemas
    - Add field validators: code regex `^[A-Z0-9]{3,20}$`, phone regex `^0\d{9}$`, name 1–255 chars, address_detail 1–500 chars
    - Use `model_config = {"from_attributes": True}` for `DepotRead`
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 3.4_

  - [x] 1.2 Register error codes in `app/core/i18n.py`
    - Add `DEPOT_NOT_FOUND`: "Không tìm thấy bưu cục."
    - Add `DEPOT_CODE_EXISTS`: "Mã bưu cục đã tồn tại."
    - Add `WARD_NOT_FOUND`: "Mã phường/xã không hợp lệ."
    - _Requirements: 2.7, 2.8, 3.3, 3.5, 4.2_

- [x] 2. Backend CRUD layer
  - [x] 2.1 Create `app/crud/depot.py` with data access functions
    - Implement `list_depots` with pagination, unaccent search (name/code), is_active filter, joined with Ward → Province for name resolution
    - Implement `get_depot` by id, `get_depot_by_code` by code
    - Implement `create_depot` inserting new record
    - Implement `update_depot` with partial update logic (only set provided fields)
    - Sort by `created_at` descending
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8, 3.1_

- [x] 3. Backend service layer
  - [x] 3.1 Create `app/services/depot_service.py` with business logic
    - `create_depot`: check code uniqueness (ConflictError), validate ward_code existence (AppError WARD_NOT_FOUND), delegate to crud
    - `update_depot`: get depot (NotFoundError), validate ward_code if provided, handle is_active idempotency (skip update if same value to preserve updated_at), delegate to crud
    - _Requirements: 2.7, 2.8, 2.9, 3.1, 3.3, 3.5, 4.1, 4.2, 4.3_

- [x] 4. Backend API router
  - [x] 4.1 Create `app/api/v1/depots.py` with REST endpoints
    - `GET /api/v1/depots` — query params: page, page_size, search, is_active; returns DepotPage
    - `POST /api/v1/depots` — body: DepotCreate; returns DepotRead with status 201
    - `PATCH /api/v1/depots/{id}` — body: DepotUpdate; returns DepotRead with status 200
    - Add proper type hints, dependency injection for db session
    - _Requirements: 1.1, 1.4, 1.5, 2.1, 2.9, 3.1, 3.2, 3.6, 4.1_

  - [x] 4.2 Wire depot router in `app/main.py`
    - Import and include the depot router with prefix `/api/v1/depots` and tag "depots"
    - _Requirements: all_

- [x] 5. Checkpoint - Backend verification
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Backend tests
  - [ ]* 6.1 Create unit tests in `tests/unit/test_depot_schemas.py`
    - Test code validation: valid codes accepted, invalid rejected (lowercase, special chars, too short/long)
    - Test phone validation: valid 10-digit format, invalid formats rejected
    - Test name and address_detail length constraints
    - _Requirements: 2.4, 2.5, 2.6_

  - [ ]* 6.2 Create unit tests in `tests/unit/test_depot_service.py`
    - Test duplicate code detection raises ConflictError
    - Test invalid ward_code raises AppError with WARD_NOT_FOUND
    - Test is_active idempotency: updated_at unchanged when setting same value
    - Test successful create and update flows
    - _Requirements: 2.7, 2.8, 3.3, 3.5, 4.3_

  - [ ]* 6.3 Create integration tests in `tests/integration/test_depot_api.py`
    - Test full CRUD flow: create → list → update → deactivate
    - Test search with diacritics-insensitive matching
    - Test pagination parameters and metadata
    - Test ward/province name resolution in responses
    - Test error responses (duplicate code, not found, invalid ward)
    - _Requirements: 1.1, 1.2, 1.4, 1.8, 2.7, 2.8, 3.3, 4.1_

  - [ ]* 6.4 Write property test for input validation boundaries
    - **Property 4: Input validation boundary correctness**
    - Use Hypothesis to generate random strings, verify acceptance iff matching regex/length rules
    - **Validates: Requirements 2.4, 2.5, 2.6, 3.4**

  - [ ]* 6.5 Write property test for partial update field preservation
    - **Property 5: Partial update field preservation**
    - Use Hypothesis to generate random subsets of updatable fields, verify only those change
    - **Validates: Requirements 3.1**

  - [ ]* 6.6 Write property test for pagination slice correctness
    - **Property 3: Pagination slice correctness**
    - Use Hypothesis to generate dataset sizes + random page/page_size, verify correct slice
    - **Validates: Requirements 1.4**

- [x] 7. Frontend API layer and schema
  - [x] 7.1 Create `src/api/depots.js` with API functions
    - `getDepots({ page, pageSize, search, isActive })` — GET /api/v1/depots
    - `createDepot(data)` — POST /api/v1/depots
    - `updateDepot(id, data)` — PATCH /api/v1/depots/{id}
    - Use existing `src/api/client.js` axios instance
    - _Requirements: 5.7_

  - [x] 7.2 Create `src/features/depots/schema.js` with zod validation
    - Define depot form schema matching backend validation rules
    - Vietnamese error messages for all validation failures
    - _Requirements: 5.5_

- [x] 8. Frontend components
  - [x] 8.1 Create `src/features/depots/components/DepotStatusBadge.jsx`
    - Display "Hoạt động" (green) or "Ngưng hoạt động" (red) badge using Ant Design Tag
    - _Requirements: 4.5, 5.2_

  - [x] 8.2 Create `src/features/depots/components/DepotSearchBar.jsx`
    - Search input with 300ms debounce
    - is_active filter dropdown (Tất cả / Hoạt động / Ngưng hoạt động)
    - _Requirements: 5.6, 1.3_

  - [x] 8.3 Create `src/features/depots/components/DepotTable.jsx`
    - Ant Design Table with columns: code, name, phone, address, ward/province, status, actions
    - Pagination integrated with TanStack Query
    - Action buttons: "Sửa" and activate/deactivate toggle
    - _Requirements: 5.2_

  - [x] 8.4 Create `src/features/depots/components/DepotFormModal.jsx`
    - Modal form for create and edit modes
    - Fields: code (read-only in edit), name, phone, address_detail, cascading select Province → Ward
    - react-hook-form + zod resolver for validation
    - On success: close modal, invalidate queries, show success notification
    - On error: show error notification, keep modal open with form data preserved
    - _Requirements: 5.3, 5.4, 5.5, 5.9, 5.10_

- [x] 9. Frontend page and routing
  - [x] 9.1 Create `src/features/depots/pages/DepotListPage.jsx`
    - Compose DepotSearchBar, DepotTable, DepotFormModal
    - TanStack Query for fetching depot list with search/filter/pagination state
    - "Thêm mới" button to open create modal
    - _Requirements: 5.1, 5.7_

  - [x] 9.2 Add depot route to `src/routes/`
    - Register depot list page route in the app router
    - _Requirements: 5.1_

  - [x] 9.3 Add Vietnamese strings to `src/i18n/vi.js`
    - Add depot-related labels, placeholders, messages, error messages
    - _Requirements: 5.8_

- [x] 10. Final checkpoint - Full integration verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases
- No database migration needed — using existing `depots` table as-is
- Ward model links directly to Province (no District model), so cascading select is Province → Ward

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["3.1"] },
    { "id": 3, "tasks": ["4.1"] },
    { "id": 4, "tasks": ["4.2"] },
    { "id": 5, "tasks": ["6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "7.1", "7.2"] },
    { "id": 6, "tasks": ["8.1", "8.2", "8.3"] },
    { "id": 7, "tasks": ["8.4"] },
    { "id": 8, "tasks": ["9.1", "9.3"] },
    { "id": 9, "tasks": ["9.2"] }
  ]
}
```
