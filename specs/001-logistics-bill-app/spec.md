# Feature Specification: Ứng dụng Quản lý Phiếu Gửi Vận Chuyển (Logistics Delivery Bill Management)

**Feature Branch**: `001-logistics-bill-app`
**Created**: 2026-04-26
**Status**: Draft
**Input**: User description: "I want to build app to help logistics industry. We need to create bill for delivering. All basic requirement, logo, bill format I leave them at `/home/lehiep/veloxship/image_data`. This app serve Vietnamese people so all button, UI / UX must be Vietnamese"

## Context From Reference Materials

The user supplied three reference images in `image_data/`:

- **`logo.jpg`** — Brand logo featuring "HN" letters integrated with a road and delivery truck, in red/black, identifying the operator as a Vietnamese express-delivery company.
- **`bill_format.jpg`** — A real "PHIẾU GỬI" (Shipping Slip) from a Vietnamese carrier (NewLinks) showing the exact paper layout the system must reproduce: sender block, receiver block, package contents, service-fee block, signatures, customer code, tracking barcode, and QR code.
- **`requirement.jpg`** — A vendor quotation listing a full logistics management software suite (employee, settings, customer, partner, bill of lading, warehouse, vehicle/COD, reports + a mobile app). This represents the long-term roadmap; v1 scope is intentionally narrowed to **bill creation and management**.

The entire user interface, including buttons, labels, error messages, and printed output, MUST be in Vietnamese. All Vietnamese diacritics (dấu) must be preserved on screen, in storage, in search, and on print.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tạo phiếu gửi mới cho lô hàng (Create a new delivery bill) (Priority: P1)

A counter/branch staff member receives a customer at the office with a package to ship. The staff member opens the application, enters sender information (name, address, district, province, phone), enters receiver information, describes the package contents (description, quantity, weight, length × width × height), selects the service category (Tài liệu / Hàng hóa) and service tier (e.g., CPN, PHT, Đường bộ, 48H, Nguyên chuyến, or International Express/Economy), records the fee breakdown (cước chính, phụ phí xăng dầu, phụ phí khác, VAT, tổng cộng), records who pays (sender or receiver), saves the bill, and prints the physical "Phiếu Gửi" with a unique tracking number, customer code, barcode, and QR code that exactly match the supplied bill format.

**Why this priority**: This is the single core operation of the business — every shipment starts with a phiếu gửi. Without it, no other workflow (pickup, sort, transit, delivery, COD, reporting) can exist. It is therefore the indispensable MVP.

**Independent Test**: A staff member can fully exercise this story end-to-end in isolation: open the app, fill the form, save, print a bill that matches the company template and is recognizably correct to a Vietnamese-reading user. Successful printing with a unique scannable tracking number is the acceptance signal.

**Acceptance Scenarios**:

1. **Given** the application is open and the staff is logged in, **When** the staff fills all required sender, receiver, content, service, and fee fields and clicks "Lưu & In phiếu", **Then** the system saves the bill, generates a unique tracking number (e.g., `NL0011310`-style format) and customer code, and produces a print-ready document whose layout, sections, fonts, and Vietnamese labels match the supplied `bill_format.jpg`.
2. **Given** the staff omits any mandatory field (e.g., người nhận, số điện thoại, trọng lượng), **When** the staff attempts to save, **Then** the system blocks submission and shows a clear Vietnamese error message identifying the missing field.
3. **Given** weight is `200,00 kg` and quantity is `24`, **When** the staff enters these values, **Then** the system accepts Vietnamese decimal format (comma as separator) and renders them on the printed bill exactly as entered.
4. **Given** the staff selects "Người nhận thanh toán", **When** the bill is printed, **Then** the corresponding checkbox is marked on the printed bill and the recipient is recorded as the payer.
5. **Given** a successfully created bill, **When** the staff views the printed/preview output, **Then** it includes the company logo, the carrier hotline and website (Vietnamese footer), the sender-signature line with the date in Vietnamese format ("…ngày … tháng … năm …"), the receiver-signature line, the QR code, and the tracking barcode.

---

### User Story 2 - Tra cứu, in lại và cập nhật trạng thái phiếu gửi (Look up, reprint, and update status) (Priority: P2)

After bills are created, staff and supervisors must be able to find any bill quickly (by tracking number, by sender phone, by receiver phone, by date range, by customer code), view its details, reprint a copy if the original is lost or damaged, and update its lifecycle status (e.g., Đã tạo, Đã lấy hàng, Đang vận chuyển, Đã giao, Hoàn trả, Hủy) so that the operations team has a real-time view of in-flight shipments.

**Why this priority**: Once the carrier handles more than a handful of shipments per day, retrieval and status visibility are required to handle customer enquiries and prevent lost packages. It is the immediate next step after creation but not strictly required for the very first parcel to ship.

**Independent Test**: Create a small set of bills, then exercise search filters and status updates without creating new bills. Confirm reprints are byte-equivalent to originals.

**Acceptance Scenarios**:

1. **Given** several bills exist, **When** the staff searches by tracking number, **Then** the matching bill is shown within 1 second and all fields are displayed in Vietnamese.
2. **Given** a search for a Vietnamese name with diacritics ("Nguyễn Thị Hoa"), **When** the staff searches with or without diacritics, **Then** the system returns the same matching results (diacritic-insensitive search).
3. **Given** a bill in status "Đã tạo", **When** the staff updates it to "Đã giao" with a delivery timestamp and the recipient signer name, **Then** the system records the change with audit trail (who, when, previous value) and the bill detail view shows the new status.
4. **Given** a customer requests a reprint, **When** the staff clicks "In lại", **Then** the reprint is visually identical to the original and is logged as a reprint event.

---

### User Story 3 - Lưu hồ sơ khách hàng thường xuyên để tự điền (Save repeat-customer profiles for auto-fill) (Priority: P3)

Corporate clients (e.g., "CTY CP TM&PT HẢI HÀ" in the reference) ship daily and re-enter the same sender info every time. Staff can save customer profiles once and select them on subsequent bills to auto-fill the sender block, eliminating data-entry errors and saving time.

**Why this priority**: It is a productivity multiplier rather than a baseline capability. Bill creation works without it; this story improves throughput and accuracy.

**Independent Test**: Create a customer profile, then start a new bill, select the customer, and verify the sender block is populated correctly.

**Acceptance Scenarios**:

1. **Given** a saved customer "KHL — Mr Lương Kho HN", **When** the staff selects this customer when creating a new bill, **Then** the sender name, address, district, province, and phone are auto-filled and remain editable.
2. **Given** a customer profile is updated, **When** new bills are created afterwards, **Then** the new values are used; previously created bills retain the snapshot of customer data at the time of creation.
3. **Given** a saved customer has a customer code (e.g., `NL500010`), **When** a bill is created for them, **Then** the customer code is printed in the "Mã KH" field of the printed bill.

---

### Edge Cases

- **Diacritics handling**: All input, storage, search, and printing must preserve Vietnamese diacritics. Search must match diacritic-stripped equivalents (e.g., "ha" finds "Hà").
- **Decimal format**: Vietnamese decimal convention uses comma (`,`) for the fractional separator and dot (`.`) for thousands. The system must accept and display values consistently.
- **Address granularity**: Some receivers provide only a street address; some provide industrial-park / building level (e.g., "KCN VSIP, Đường 3A, TP Từ Sơn"). Free-text address must be supported in addition to the structured Quận/Huyện and Tỉnh/TP fields.
- **Tracking-number collision**: Two staff creating bills concurrently must never receive the same tracking number.
- **Mid-creation interruption**: If the staff loses connection or the device crashes, an in-progress bill should not be silently lost; either auto-save as draft or fail loudly so nothing is invented.
- **Print failure**: If the printer is offline or jams, the bill record must still exist in the system and be reprintable later.
- **Cancellation after creation**: A bill cancelled before pickup must be marked "Hủy" and excluded from operational counts but retained for audit.
- **Field-length and oversized cargo**: A delivery bill that exceeds the standard form size (e.g., very long description or many line items) must still print legibly without overflowing the form.
- **International vs. domestic exclusivity**: The user must not be able to mark both an "International" tier and a "Trong nước" tier on the same bill.
- **VAT / fee total consistency**: Cước chính + Phụ phí xăng dầu + Phụ phí khác + VAT must equal Tổng cộng; the system must enforce this on save.
- **Re-login during shift change**: A new staff user logging in must not see the previous user's draft data unless explicitly assigned.

## Requirements *(mandatory)*

### Functional Requirements

**Bill creation**

- **FR-001**: System MUST allow staff to create a "Phiếu Gửi" containing sender information (full name, address, district, province, phone), receiver information (same fields), package contents (description, quantity, weight in kg, dimensions length × width × height in cm), service classification, fee breakdown, payment party, and signature blocks.
- **FR-002**: System MUST generate a unique, human-readable tracking number for each bill that does not collide under concurrent creation.
- **FR-003**: System MUST associate each bill with a customer code ("Mã KH") when the sender is a saved customer.
- **FR-004**: System MUST allow the staff to classify cargo as "Tài liệu" (Document) or "Hàng hóa/Pack" (Goods).
- **FR-005**: System MUST allow the staff to select exactly one domestic service tier (CPN, PHT, Đường bộ, 48H, Nguyên chuyến, Khác) OR exactly one international tier (International, Express, Economy, Other) per bill, but not both at once.
- **FR-006**: System MUST capture the fee breakdown — Cước chính, Phụ phí xăng dầu, Phụ phí khác, VAT — and compute Tổng cộng as their sum, refusing to save when manual values disagree.
- **FR-007**: System MUST capture which party pays: "Người gửi thanh toán" or "Người nhận thanh toán".
- **FR-008**: System MUST validate that all mandatory fields are present and well-formed before saving; error messages MUST be in Vietnamese and identify the offending field.

**Printing & output**

- **FR-009**: System MUST produce a printable bill whose layout, section ordering, Vietnamese labels, company logo placement, hotline, website, email, footer disclaimer, signature blocks, customer-code placement, tracking barcode, and QR code visually match the supplied `bill_format.jpg`.
- **FR-010**: System MUST embed a scannable barcode encoding the tracking number and a QR code encoding the bill identifier (and any standard tracking URL) on every printed bill.
- **FR-011**: System MUST allow reprinting an existing bill at any time, producing output identical to the original, and MUST log the reprint event (who, when).
- **FR-012**: System MUST allow exporting a bill as a digital file (e.g., PDF) in addition to physical print.

**Lookup & management**

- **FR-013**: Users MUST be able to search bills by tracking number, customer code, sender phone, receiver phone, sender name, receiver name, and creation-date range.
- **FR-014**: Search MUST be diacritic-insensitive for Vietnamese text so that staff can locate records without typing dấu.
- **FR-015**: System MUST display a paginated list of bills with the most recent first, showing tracking number, sender name, receiver name, status, total fee, and creation date.
- **FR-016**: Users MUST be able to update the lifecycle status of a bill among: Đã tạo, Đã lấy hàng, Đang vận chuyển, Đã giao, Hoàn trả, Hủy.
- **FR-017**: System MUST keep an audit trail for every bill recording who created/modified/printed/cancelled it and when.

**Customer profiles**

- **FR-018**: Users MUST be able to create, edit, and deactivate customer profiles holding the sender block fields plus a customer code.
- **FR-019**: System MUST allow selecting a saved customer when creating a new bill to auto-fill the sender block; the auto-filled fields MUST remain editable per bill.
- **FR-020**: System MUST snapshot the customer's information into the bill at creation time so subsequent profile edits do not retroactively change historical bills.

**Internationalisation, accessibility & data quality**

- **FR-021**: The entire user interface (labels, buttons, menus, validation messages, success/error toasts, printed output) MUST be in Vietnamese.
- **FR-022**: System MUST accept and correctly render full Vietnamese diacritics in all text fields and on all printed output.
- **FR-023**: System MUST accept Vietnamese number formatting (comma decimal separator) for weight, dimensions, and fees in input, and render them consistently in the same format on screen and on print.
- **FR-024**: System MUST display dates in Vietnamese form ("ngày … tháng … năm …") on printed output and in a locally familiar format on screen.

**Authentication & access**

- **FR-025**: System MUST require staff to authenticate before creating, modifying, or viewing bills.
- **FR-026**: System MUST attribute every bill, status change, and reprint to the authenticated user.

### Key Entities

- **Phiếu Gửi (Delivery Bill)**: The central record. Holds the unique tracking number, customer code, references to sender and receiver snapshots, package-content lines, service classification (cargo type + tier), fee breakdown and total, payment party, status, signature metadata, and audit timestamps.
- **Người Gửi / Người Nhận (Sender / Receiver) snapshot**: A frozen-at-creation copy of name, address, district, province, and phone attached to a specific bill, so historical bills are unaffected by later edits to a customer profile.
- **Khách hàng (Customer)**: A reusable profile for repeat senders, holding the same fields as a sender plus a customer code. Linked to many bills.
- **Nội dung gói hàng (Package Content line)**: Description, quantity, weight, length, width, height. A bill may have one or several lines.
- **Cước phí (Fee Breakdown)**: Cước chính, Phụ phí xăng dầu, Phụ phí khác, VAT, Tổng cộng — stored as part of the bill.
- **Dịch vụ (Service Tier catalogue)**: The list of selectable tiers (CPN, PHT, Đường bộ, 48H, Nguyên chuyến, Khác / International, Express, Economy, Other) used to classify each bill.
- **Nhân viên (Staff User)**: A user account with credentials. Every audit entry references one.
- **Sự kiện kiểm toán (Audit Event)**: Records who did what to which bill (created, edited, reprinted, status-changed, cancelled) and when.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A trained counter staff member can create and print a complete, correct phiếu gửi from blank form to physical printout in under 90 seconds for a saved customer, and under 3 minutes for a brand-new customer.
- **SC-002**: 100% of UI elements (labels, buttons, menus, validation messages, printed output) presented to end users are in Vietnamese with correct diacritics. A native Vietnamese reviewer finds zero foreign-language strings in a full UI walkthrough.
- **SC-003**: Printed bills are visually faithful to the company template — a Vietnamese carrier-staff reviewer rates layout fidelity (sections, ordering, labels, logo, footer, barcode, QR placement) at 9/10 or higher in a side-by-side comparison with the reference image.
- **SC-004**: Search returns matching bills in under 1 second for a dataset of 100,000 historical bills.
- **SC-005**: Diacritic-insensitive search finds at least 99% of records when the query is typed without diacritics, validated on a labelled sample.
- **SC-006**: Tracking-number collisions occur zero times across an automated stress test of 10,000 concurrent bill creations.
- **SC-007**: Across the first 1,000 production bills, fewer than 1% require correction or cancellation due to data-entry errors traceable to UI ambiguity.
- **SC-008**: 95% of returning customers' bills are created using the auto-fill flow rather than retyping, measured over the first 30 days after launch.
- **SC-009**: Reprint and status-update operations complete in under 2 seconds end-to-end as observed by the user.

## Assumptions

- **Scope is intentionally narrow for v1.** Even though the supplied requirement quotation describes a full logistics suite (warehouse, vehicle dispatch, COD collection, partner price lists, mobile delivery app, 20+ reports), the user's stated immediate need is "create bill for delivering". v1 therefore covers bill creation, lookup, status updates, customer profiles, and printing only. The remaining modules are deferred to later phases.
- **Primary users are counter / branch staff** of a Vietnamese express-delivery carrier creating bills on behalf of paying customers, not end-customers self-serving. This is consistent with the supplied paper bill having signature blocks and being filled out by an attendant.
- **Single carrier / single tenant.** The application is configured for one carrier (its logo, hotline, website, footer text). Multi-tenant carrier hosting is out of scope.
- **Vietnamese language only** for v1. Multi-language UI is deferred.
- **Fees are entered manually** by staff in v1; an automatic rate-table-driven fee calculator is a desirable future enhancement and is not required for MVP. The supplied bill format shows fees as free-form numeric fields, supporting this assumption.
- **Standard office printer.** The bill is printed to whatever printer the branch has configured (laser or thermal), on the company's standard bill paper. The system produces a printable document; choice of physical printer is the operator's concern.
- **Internet-connected operation.** Counter offices have stable connectivity. Offline-first operation is not required for v1.
- **Auditing for internal use only.** No external regulatory export of audit data is required for v1.
- **Brand identity**: the supplied logo (`logo.jpg`) is used as the in-app and on-bill logo. The supplied bill template (`bill_format.jpg`) is used as the canonical layout reference, even though the photographed example carries another carrier's branding (NewLinks); the structure, fields, and labels are what the system reproduces, with the carrier's own logo and footer substituted in.

## Out of Scope (v1)

- Warehouse module (nhập kho, xuất kho, tồn kho, kho trung chuyển, kho đối tác, kho trả hàng, lịch sử)
- Vehicle / trip dispatch (quản lý chuyển xe, đội xe)
- COD money-collection workflow (thu hộ, nộp tiền, danh sách kế nộp tiền)
- Partner & price-list management (quản lý đối tác, bảng giá)
- Employee / department / role administration beyond basic login
- Province/district/ward master-data administration UI (seed data is acceptable)
- Mobile app for pickup / delivery / transit staff
- Bulk bill creation via Excel import
- Advanced reports (the 20-report library mentioned in the quotation)
- Customer self-service portal and public tracking page
