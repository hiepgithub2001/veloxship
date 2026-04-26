# Feature Specification: Hỗ trợ Điện thoại qua PWA (Mobile Support via Progressive Web App)

**Feature Branch**: `002-pwa-mobile-support`
**Created**: 2026-04-26
**Status**: Draft
**Input**: User description: "We need to develop this project as webapp, it means that user can use this product via their phone. We choose PWA as most suitable method here, please plan and breakdown to implement base on pre-existing codebase."

## Context

The Vietnamese logistics bill management app (feature `001-logistics-bill-app`) currently delivers a desktop-oriented web experience for counter staff: they sit at a desk, fill the "Phiếu Gửi" form, print to a thermal/A4 printer, and look up bills from a workstation.

The business now needs the same product to be **usable from a phone** so the staff who are *not* sitting at the counter — pickup drivers, last-mile delivery staff, supervisors visiting branches, and counter staff who occasionally take orders away from their desk — can perform their work directly from a phone they already carry.

The chosen delivery vehicle is a **Progressive Web App (PWA)**: the existing browser-based app must be installable to the phone home screen, launchable like a native app, and mobile-touch-friendly. **The app requires an active internet connection** — when connectivity is unavailable, the user is told in Vietnamese to retry once they are online; the app does not attempt to operate offline in v1.

This feature is a **delivery-channel capability** layered on top of the existing app. It does not change the core domain (bills, customers, statuses) — it changes *where* and *on which form factor* users can interact with that domain.

The product remains strictly Vietnamese in all UI text, install prompts, error messages, and connection indicators.

## Clarifications

### Session 2026-04-26

- Q: Should offline / weak-network workflows be supported in v1? → A: No — v1 requires an active internet connection for all workflows. The previous "Keep working when offline" user story (P2) and all related queue / sync / conflict-resolution requirements are removed. Connection loss is handled by clearly informing the user in Vietnamese that they must reconnect to continue.
- Q: Should mobile cover all desktop workflows, or only field-staff workflows? → A: All workflows — including the full "Phiếu Gửi" creation form, customer profile management, and every other desktop capability. The mobile UI MUST intelligently lay out long forms in logical sections so the user can complete the same fields available on desktop without losing context on a small screen.
- Q: Should push notifications ship in v1? → A: No — push notifications are deferred to a later feature. Story 2 keeps only the auto-update behaviour. The "Notification Subscription" entity and FR-016/17/18 are removed; notifications are added to "Out of Scope".
- Q: How should "Lưu & In phiếu" behave on a phone (no paired printer)? → A: Save the bill, then open the bill's print-ready document as a PDF preview the user can download, share via the native OS share sheet (email, Zalo, Messenger, etc.), or print via the OS print dialog (Android print framework / iOS AirPrint). Reuses the same print layout as desktop; no bespoke share UI is built inside the app.
- Q: Should mobile lookup support camera-based barcode/QR scanning of the printed slip in v1? → A: No — deferred to a later feature. Mobile lookup remains text-input only in v1. Camera permission UX and an in-app scanner are added to "Out of Scope". The printed slip's human-readable tracking number remains the fallback.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cài đặt và sử dụng ứng dụng từ điện thoại như một app (Install and use the app from a phone like a native app) (Priority: P1)

A delivery staff member opens the carrier's web address on their phone for the first time. The site detects it is being viewed on a phone and offers a clear, Vietnamese prompt to "Cài đặt ứng dụng" (Install app). The staff member accepts; the app icon (the company logo) appears on their phone home screen. From that point on, tapping the icon launches the app full-screen — no browser address bar, no tabs — with a Vietnamese splash screen showing the company logo. The staff member logs in once and stays logged in across launches. They can perform every workflow they need on the road: look up a bill by tracking number or phone number, view its details, update its status (e.g., "Đã lấy hàng" → "Đang vận chuyển" → "Đã giao"), capture the recipient signer name and delivery timestamp, and receive a clear "Lưu thành công" confirmation.

**Why this priority**: This is the core value of the feature. Without an installable, touch-usable app on the phone, nothing else this feature offers matters. Mobile lookup + status update is also the single highest-volume mobile workflow in the business — it is what every driver does at every drop.

**Independent Test**: A tester opens the production URL in mobile Chrome on Android and mobile Safari on iOS, accepts the install prompt, launches the installed icon, logs in, finds a real bill by tracking number, updates its status to "Đã giao" with a signer name, and confirms the change is visible to a desktop user without any further action. The whole sequence must be completed in Vietnamese, in portrait orientation, using only thumb taps, while the device has a normal mobile-data connection.

**Acceptance Scenarios**:

1. **Given** a first-time visitor on a PWA-capable mobile browser (Chrome on Android, Safari on iOS, Edge on mobile), **When** they load the app's URL, **Then** the system offers a Vietnamese install affordance ("Cài đặt ứng dụng vào màn hình chính") within the first session, and the affordance is dismissible without recurring on every page load.
2. **Given** the user has installed the app, **When** they tap the home-screen icon, **Then** the app launches in standalone mode (no browser UI), shows a branded Vietnamese splash with the company logo, and resumes at the screen they last visited (or the login screen if their session expired).
3. **Given** the user is logged in on the installed app and has an active internet connection, **When** they perform any read or write workflow that already exists on the desktop product (bill search, bill detail view, status update, reprint trigger, customer lookup), **Then** the workflow completes successfully on a phone with the screen rendered legibly in portrait orientation, all controls reachable by thumb, and all Vietnamese diacritics preserved on input and display.
4. **Given** a session is active, **When** the user closes and re-opens the installed app within the session-validity window, **Then** they remain logged in and are not asked to re-enter credentials.
5. **Given** the user is on a phone with a small screen (≤ 360 px wide), **When** any screen with a data table or wide form is shown, **Then** the layout adapts to a single-column or card view — no horizontal scrolling is required to reach a primary action.
6. **Given** the user is creating a new "Phiếu Gửi" on a phone, **When** they open the create-bill flow, **Then** the form is presented as logical Vietnamese sections (Người gửi → Người nhận → Nội dung hàng → Dịch vụ → Cước phí → Xác nhận) with a visible progress indicator; the user can move forward and backward between sections without losing data already entered in any section, sees validation errors marked on the section that contains the field, and can review every value on a final "Xác nhận" section before saving. Every field collected by the desktop form is collectable through this mobile flow.
6a. **Given** the user has filled the create-bill flow on a phone and taps "Lưu & In phiếu", **When** the bill is saved, **Then** the app opens the bill's PDF preview using the same print layout as desktop, and the user can download the PDF, share it via the OS share sheet (email, Zalo, Messenger, etc.), or print it via the OS print dialog. Vietnamese diacritics, barcode, and QR are preserved and scannable in the PDF.
7. **Given** the user loses internet connectivity at any point, **When** they attempt any workflow, **Then** the app shows a clearly visible Vietnamese banner ("Mất kết nối — vui lòng kiểm tra mạng và thử lại") and blocks the action without losing the data the user has already typed into the current form or current section.

---

### User Story 2 - Cập nhật ứng dụng tự động (Automatic app updates) (Priority: P2)

When the operations team ships a new version of the app, every installed phone picks up the update automatically without the user having to reinstall, find an app store, or learn anything new — the next time they launch the app (or refresh), the latest version is loaded.

**Why this priority**: Auto-update keeps the field reliable without IT visits to every driver. It is secondary to install and mobile-touch usability but essential for sustainable operation once the app is in users' hands.

**Independent Test**: Deploy a new version with a visible Vietnamese version label change. Confirm that an already-installed phone, on next launch, displays the new label without any manual user action.

**Acceptance Scenarios**:

1. **Given** the user has the app installed and a new version has been deployed, **When** the user launches the app while online, **Then** the new version is downloaded and activated transparently — at the latest by the user's *next* launch — without breaking any work in progress.
2. **Given** the user is mid-task when a new version becomes available, **When** the new version is ready, **Then** the user is shown an unobtrusive Vietnamese affordance ("Có phiên bản mới — tải lại để cập nhật") that they can dismiss; the active task is never interrupted automatically.
3. **Given** a new version has been activated, **When** the user opens the settings/about screen, **Then** the visible Vietnamese version identifier reflects the new version.

---

### Edge Cases

- **Browser without PWA support**: An older browser that cannot install the app must still get a working responsive website, with a small Vietnamese notice that "ứng dụng không thể cài đặt trên trình duyệt này".
- **iOS install quirks**: iOS Safari does not show a built-in install prompt. The app must show its own Vietnamese instruction overlay ("Bấm Chia sẻ → Thêm vào Màn hình chính") on first iOS visit, dismissible.
- **Connectivity loss mid-action**: If the device drops connectivity while the user is filling a form or saving a status update, the app must (a) show a Vietnamese "Mất kết nối" banner, (b) preserve the data the user has already typed in the current form so they can retry once back online, and (c) never silently submit a partial action.
- **Connectivity loss on launch**: If the app is launched without connectivity, the user sees a Vietnamese "Cần kết nối mạng để sử dụng ứng dụng" screen with a retry control; no business data is shown until connection is restored.
- **Privacy on a shared / lost device**: If a phone is borrowed or stolen, business data must not be visible without authentication; logging out must clear any session state from the device.
- **Permission denied**: If the user denies install or notification permissions, every workflow that does not require that permission must still work; the app must not nag.
- **Print from phone**: Phones do not typically have direct access to the office's thermal/A4 bill printer. On a phone, "Lưu & In phiếu" saves the bill and opens the bill's PDF preview; from there the user downloads, shares via the OS share sheet, or prints via the OS print dialog. The app does not attempt direct thermal-printer integration.
- **Vietnamese diacritic handling everywhere**: The mobile virtual keyboard must input full Vietnamese diacritics; submitted data must round-trip them perfectly; every prompt, banner, and notification must render them correctly.

## Requirements *(mandatory)*

### Functional Requirements

#### Installability and app shell

- **FR-001**: The system MUST be installable to the home screen of any PWA-capable mobile browser (at minimum Chrome on Android and Safari on iOS in their currently-supported versions), using the existing company logo as the app icon and a Vietnamese app name.
- **FR-002**: The system MUST present a Vietnamese install affordance on PWA-capable browsers that support the prompt natively, and a Vietnamese instructional overlay on iOS Safari (which does not).
- **FR-003**: The installed app MUST launch in standalone mode (no browser address bar/tabs), display a Vietnamese splash with the company logo, and resume at the user's last-visited screen when relaunched within the session window.
- **FR-004**: The app MUST keep the user logged in across launches within the existing session-validity window; no re-authentication is required if the session is still valid.

#### Mobile-first usability

- **FR-005**: Every workflow available on the desktop product (bill creation, search, detail view, status update, reprint, customer profile management, and any other desktop workflow) MUST be usable on a phone in portrait orientation without horizontal scrolling.
- **FR-006**: All interactive controls MUST be reachable and operable by thumb on a screen as narrow as 360 px, with touch targets sized per platform accessibility guidance.
- **FR-007**: All input fields MUST trigger the appropriate mobile keyboard (numeric for phone numbers and weight, decimal for fees, text with Vietnamese support for names and addresses).
- **FR-008**: All Vietnamese text — labels, errors, empty states, install prompts, connection banners, version label, error states — MUST preserve diacritics on screen and on storage round-trips.
- **FR-008a**: For long forms on a phone (notably the "Phiếu Gửi" creation form, but also customer profile create/edit), the system MUST present the form in logical Vietnamese-labelled sections (e.g., Người gửi → Người nhận → Nội dung hàng → Dịch vụ → Cước phí → Xác nhận), with clear section navigation, a visible progress indicator, and partial-input preservation when the user moves between sections. The set of fields collected MUST match the desktop form one-for-one — no field is dropped on mobile.
- **FR-008b**: On the long-form sectioned flow, the user MUST be able to review all entered data on a final "Xác nhận" section before saving, and MUST be able to jump back to any prior section to edit without losing data already entered in other sections.
- **FR-008c**: Validation errors on a long form MUST be surfaced at the section that contains the offending field; the navigation indicator MUST mark sections containing unresolved errors so the user can locate them on a small screen.
- **FR-008d**: On a phone, "Lưu & In phiếu" MUST save the bill and then present the bill's print-ready document as an in-app PDF preview. From the preview the user MUST be able to (a) download the PDF to the device, (b) hand it to the OS share sheet (email, Zalo, Messenger, etc.), and (c) hand it to the OS print dialog. The PDF layout MUST be identical to the desktop print layout (no field omitted, Vietnamese diacritics preserved, barcode and QR scannable). The app MUST NOT attempt direct thermal-printer integration on the phone.

#### Connectivity and online-only behaviour

- **FR-009**: The app MUST require an active internet connection for every read and write workflow. No business data MUST be cached locally for offline use, and no actions MUST be queued for later sync.
- **FR-010**: On detecting loss of connectivity, the app MUST display a clearly visible Vietnamese banner ("Mất kết nối — vui lòng kiểm tra mạng và thử lại") within 5 seconds, and remove it within 5 seconds of connection return.
- **FR-011**: When the user submits an action (e.g., "Lưu", "Cập nhật trạng thái") and the request fails due to lost connectivity, the app MUST preserve the user's currently-entered form data and offer a Vietnamese "Thử lại" control; it MUST NOT silently submit a partial action and MUST NOT discard the user's typed data.
- **FR-012**: If the app is launched without connectivity, the app MUST show a Vietnamese "Cần kết nối mạng để sử dụng ứng dụng" screen with a retry control, and MUST NOT show stale business data.

#### Updates and freshness

- **FR-013**: New versions of the app MUST be picked up by installed clients without manual user intervention; the next launch (or current session, when the user accepts the update affordance) loads the new version.
- **FR-014**: An in-progress task (e.g., a half-filled form) MUST NOT be interrupted by an automatic update; the user is offered a Vietnamese affordance to reload at a safe moment.
- **FR-015**: The app MUST display a Vietnamese version identifier somewhere accessible (e.g., on the settings/about screen) so support can verify which version a user is running.

#### Compatibility, security, and graceful degradation

- **FR-016**: On a browser that does not support PWA installation, every existing workflow MUST continue to function as a regular responsive website, with a small Vietnamese notice that installation is not available on this browser.
- **FR-017**: Logging out MUST clear the local session state so a subsequent user on the same device cannot access business data without authenticating.
- **FR-018**: The desktop experience for counter staff MUST NOT regress in any acceptance scenario covered by feature `001-logistics-bill-app` (bill creation, print fidelity, search, status, customer profiles, audit trail).

### Key Entities *(include if feature involves data)*

- **App Version Record**: The deployed version identifier surfaced to the user (FR-015) and used to decide when an update is available (FR-013). One value at a time per installed client.

> Two entities were removed during the 2026-04-26 clarifications: "Pending Offline Change" and "Cached Reference Data" (along with all offline scope), and "Notification Subscription" (push notifications deferred).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A delivery staff member can install the app on a typical Android or iOS phone in under 2 minutes from first visit, without help from IT, in Vietnamese.
- **SC-002**: A bill status update performed on a phone is visible on a desktop view within 5 seconds while both devices are online.
- **SC-003**: When connectivity is lost while a user is mid-action, the user sees a clear Vietnamese connection-lost banner within 5 seconds and the data they have already typed in the current form is preserved 100% of the time across an end-to-end test suite.
- **SC-004**: 90% of workflows already supported on desktop are completed end-to-end on a phone in portrait orientation, by a tester unfamiliar with the new mobile layout, on the first attempt — including the full "Phiếu Gửi" creation flow with no field omitted relative to the desktop form.
- **SC-004a**: A typical counter-staff member can complete a full "Phiếu Gửi" creation on a phone in no more than 1.5× the time they take on desktop, measured against a baseline of current desktop timings.
- **SC-005**: A new app version deployed to the server is running on at least 95% of active installed clients within 24 hours, with no manual reinstall.
- **SC-006**: No regression is observed in the acceptance scenarios of feature `001-logistics-bill-app` after the PWA work ships.
- **SC-007**: All user-facing text introduced by this feature (install prompts, connection banner, version label, error states) is in Vietnamese with correct diacritics, verified by a Vietnamese-speaking reviewer.
- **SC-008**: Time spent by a delivery staff member to look up a bill and mark it "Đã giao" from a phone is reduced compared to the same task done by phoning the counter — measured against a baseline of current-process timings — by at least 50%.

## Assumptions

- **Mobile must support every desktop workflow.** Per the 2026-04-26 clarification, mobile is a full-capability surface — including bill creation and customer profile management — not a read-only field tool. Counter staff at a desktop remain the primary bill-creation channel, but creating a bill from a phone must be a real, complete workflow.
- **Internet connectivity is required for every workflow.** Per the 2026-04-26 clarification, v1 does not attempt to operate offline; users in low-signal areas must reconnect to use the app.
- **Printing on a phone goes through the OS** — PDF preview, then OS share sheet or OS print dialog (per the 2026-04-26 clarification). The app does not embed a printer driver, does not pair to Bluetooth thermal printers directly, and does not build its own share UI. Identical print layout to desktop.
- **Authentication reuses the existing login mechanism.** No new identity provider or 2FA flow is introduced by this feature; session lifetime and refresh behaviour remain as defined in feature `001-logistics-bill-app`.
- **The target devices are mainstream Android and iOS phones in their currently-supported OS versions.** Older devices and non-PWA-capable browsers fall back to the regular responsive website with a notice.
- **The existing codebase is the implementation substrate.** This feature extends the current product rather than replacing it; the data model and contracts of feature `001-logistics-bill-app` are reused as-is. Concrete stack choices belong in the plan, not here.

## Out of Scope

- **All offline functionality** — read-from-cache, queued writes, background sync, conflict resolution. Explicitly removed by the 2026-04-26 clarification.
- **Push notifications** (browser / system push for status changes). Deferred to a later feature per the 2026-04-26 clarification; in-app status badges from feature `001-logistics-bill-app` cover this need until then.
- **Camera-based barcode / QR scanning** for mobile lookup. Deferred to a later feature per the 2026-04-26 clarification; users type the tracking number printed on the slip in v1.
- Native iOS or Android app published to App Store / Play Store.
- Direct Bluetooth or USB integration with thermal/dot-matrix bill printers from the phone.
- Real-time collaboration features (e.g., live cursors, presence indicators) beyond the existing audit trail.
- New authentication mechanisms (SSO, 2FA, biometrics) — the existing login is reused as-is.
- Bulk data export and reporting beyond what already exists on desktop.

## Dependencies

- Feature `001-logistics-bill-app` (the underlying domain — bills, customers, statuses, audit trail) must be in place. This feature layers a delivery channel on top of it.
- The deployed app must be served over a secure transport (a hard requirement for PWA installability in every modern browser).
- The existing authentication, bill, customer, and audit-trail capabilities are inputs as-is; this feature introduces no new domain capabilities.
