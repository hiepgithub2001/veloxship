# Customer improvements — edit, bill history, metrics

Date: 2026-09-25
Branch: `feature/customer-improvements`

## Goal

Make the customer directory actionable: allow editing a customer profile, view
that customer's bill history, and surface a couple of headline metrics. Today
customers are read-only and created implicitly when a bill is recorded.

## Scope

1. **Edit customer** — all profile fields except the auto-generated `code`.
2. **Bill history** — paginated list of bills where the customer is sender or
   receiver, with a role filter.
3. **Metrics** — total bills and total revenue (minimal set).

## Backend

### Schema (`app/schemas/customer.py`)

- `CustomerUpdate` — partial update. Fields: `name`, `phone`, `customer_type`,
  `address_detail`, `province_code`, `province_name`, `ward_code`, `ward_name`,
  `is_active`. Address fields are flattened into `metadata` JSONB exactly like
  `CustomerCreate`.
- `CustomerMetrics` — `{ total_bills: int, total_revenue: float }`.

### CRUD

- `customer.update_customer(db, customer, payload)` — merge explicit fields;
  address fields into `metadata` (preserve unspecified metadata keys).
- `bill.list_bills_by_customer(db, customer_id, role, page, page_size)` —
  `sender_id == id OR receiver_id == id`, filtered by `role` (`sender` |
  `receiver` | `all`). Reuses the `list_bills` aliased-join + `selectinload`
  pattern and `BillRead` serialization.
- `bill.customer_bill_metrics(db, customer_id)` — `COUNT(*)` and
  `SUM(fee_total)` over non-cancelled bills for the customer.

### API (`app/api/v1/customers.py`)

- `PATCH /customers/{customer_id}` → `CustomerRead`. `get_current_user` only
  (role gate to be added later by the user).
- `GET /customers/{customer_id}/bills` → `BillPage`. Query params: `page`,
  `page_size`, `role` (`all` default).
- `GET /customers/{customer_id}/metrics` → `CustomerMetrics`.

## Frontend

### Route

- New route `khach-hang/:id` → `CustomerDetailPage`.

### API (`api/customers.js`)

- `updateCustomer(id, payload)`, `getCustomerBills(id, { page, pageSize, role })`,
  `getCustomerMetrics(id)`.

### Pages

- `CustomerListPage` — name / action buttons navigate to `/khach-hang/:id`
  instead of opening the drawer.
- `CustomerDetailPage` — three tabs:
  - **Info / Edit** — form (name, phone, type, address detail, province → ward
    cascade, active toggle) prefilled from `getCustomer`; save via `updateCustomer`.
  - **Bills** — table (tracking number, sender, receiver, status, fee_total,
    created_at) with role filter (All / Sender / Receiver) + pagination.
  - **Metrics** — two stat cards (total bills, total revenue).

### i18n

- New keys under `customers` (edit form labels, tabs, metrics, bill-history
  columns) and a `common`/`bills` reuse where possible.

## Decisions

- Metrics exclude `cancelled` bills (both count and revenue).
- `total_revenue` = `SUM(fee_total)` over non-cancelled bills where the customer
  is sender or receiver.
- Customer `code` is immutable; not editable via this feature.
- No role restriction on edit for now (user will wire authorization later).

## Testing

- Backend: unit/integration tests for `PATCH` (partial update, metadata merge,
  not-found), customer-scoped bill listing + role filter, and metrics.
- Frontend: existing build/lint; manual QA of the new page.
