---
description: "Task list for feature 002-pwa-mobile-support"
---

# Tasks: Hỗ trợ Điện thoại qua PWA (PWA Mobile Support)

**Input**: Design documents from `/specs/002-pwa-mobile-support/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/pwa-additions.md`, `quickstart.md`

**Tests**: Component tests (Vitest + Testing Library) and Playwright mobile-emulation E2E tests are included because `research.md` §14 explicitly designs them as part of this feature. They are **not** TDD-style tests-must-fail-first; they are written alongside their implementation tasks and verified to pass before each story's checkpoint.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing. Stories from `spec.md`:

- **US1 (P1)** — Cài đặt và sử dụng ứng dụng từ điện thoại như một app
- **US2 (P2)** — Cập nhật ứng dụng tự động

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: `[US1]` or `[US2]` for story-phase tasks; setup, foundational, and polish tasks have no story label
- File paths are absolute or repo-rooted

## Path Conventions

- **Web app** layout: `backend/` and `frontend/` at repo root
- This feature is **frontend-only** — no `backend/` paths appear

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install PWA build dependencies, generate static PWA assets, and wire the manifest + meta tags into the existing Vite build. After this phase the app builds with a manifest and a service worker, but no PWA-specific UX has been added yet.

- [X] T001 Add `vite-plugin-pwa@^0.19`, `workbox-window@^7`, and dev-dep `@vite-pwa/assets-generator@^0.2` to `frontend/package.json`; run `npm install`.
- [X] T002 Generate the PWA icon set (`pwa-icon-192.png`, `pwa-icon-512.png`, `pwa-icon-maskable-512.png`, `apple-touch-icon-180.png`) from `image_data/logo.jpg` into `frontend/public/` using `@vite-pwa/assets-generator`; commit the generated files (per `research.md` §15, no asset generation at CI time).
- [X] T003 [P] Add the `VitePWA` plugin block to `frontend/vite.config.js` with `registerType: 'prompt'`, `injectRegister: false`, the manifest from `contracts/pwa-additions.md` §1 (Vietnamese `name`, `short_name`, `description`, `lang: 'vi-VN'`, `display: 'standalone'`, `orientation: 'portrait'`, `theme_color: '#c0392b'`, all four icon entries including the `purpose: 'maskable'` one), and Workbox config (`globPatterns: ['**/*.{js,css,html,svg,png,woff2}']`, `navigateFallback: '/index.html'`, `navigateFallbackDenylist: [/^\/api\//]`, `runtimeCaching: [{ urlPattern: /^\/api\//, handler: 'NetworkOnly' }]`, `cleanupOutdatedCaches: true`).
- [X] T004 [P] Add PWA `<head>` meta tags to `frontend/index.html`: replace the current `<meta name="viewport">` with `width=device-width, initial-scale=1, viewport-fit=cover`; add `theme-color`, `apple-mobile-web-app-capable`, `apple-mobile-web-app-status-bar-style`, `apple-mobile-web-app-title="Phiếu Gửi"`, `<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon-180.png">`, and `<link rel="manifest" href="/manifest.webmanifest">` per `contracts/pwa-additions.md` §1.
- [X] T005 [P] Add a Vite `define` block in `frontend/vite.config.js` injecting `__APP_VERSION__` (from `package.json` `version`) and `__APP_GIT_SHA__` (from `git rev-parse --short HEAD`, falling back to `"dev"` outside CI); declare the globals in `frontend/src/global.d.ts` (or jsconfig equivalent) so editors don't flag them as undefined.

**Checkpoint**: Running `npm run build` produces `frontend/dist/sw.js`, `frontend/dist/manifest.webmanifest`, and the icon set; `npm run dev` serves them. The app shell still looks identical — no behaviour change yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Wire the service-worker registration and the cross-cutting hooks/components that every user-story-phase task will mount. **No US1 or US2 task may begin until this phase is complete.**

- [X] T006 Create `frontend/src/pwa/version.js` exporting `APP_VERSION` and `APP_GIT_SHA` constants from the global Vite-injected values, with a helper `formatVersion()` returning the Vietnamese string `Phiên bản: v{APP_VERSION} ({APP_GIT_SHA})`.
- [X] T007 Create `frontend/src/pwa/registerSW.js` wrapping `virtual:pwa-register` from `vite-plugin-pwa`. Export `registerAppSW({ onNeedRefresh, onOfflineReady })` and an event-bus singleton (or React context) that re-emits `onNeedRefresh` so any later component can subscribe. `onOfflineReady` is a no-op (we are online-only — see `research.md` §4).
- [X] T008 [P] Create `frontend/src/pwa/useOnlineStatus.js` — a React hook returning `{ online: boolean }` based on `navigator.onLine` plus `window` `online`/`offline` event listeners; cleans up on unmount.
- [X] T009 [P] Create `frontend/src/styles/mobile.css` adding: tap targets ≥ 44 px on `@media (max-width: 768px)` for Ant Design buttons/menu items; `padding-top/right/bottom/left: env(safe-area-inset-*)` on the app shell container; styles for the install banner, connection banner, and update prompt.
- [X] T010 [P] Create `frontend/src/components/ResponsiveShell.jsx` — exports a hook `useIsMobile()` (uses `Grid.useBreakpoint()` from Ant Design; mobile = `xs || sm` and not `md`+) and a `<ResponsiveShell desktop={…} mobile={…} />` wrapper that picks one child based on the breakpoint.
- [X] T011 Wire setup into `frontend/src/main.jsx`: `import './styles/mobile.css'`, `import { registerAppSW } from './pwa/registerSW'`, and call `registerAppSW({ onNeedRefresh: notify, onOfflineReady: () => {} })` after React mounts.
- [X] T012 Configure React Query in `frontend/src/lib/queryClient.js` (existing file from 001) with `defaultOptions: { queries: { networkMode: 'online', retry: 1 }, mutations: { networkMode: 'online' } }` — pause queries/mutations while offline (per `research.md` §5).
- [X] T013 Update `frontend/src/api/client.js` Axios instance: add a response interceptor that maps `error.code === 'ERR_NETWORK'` (or `!error.response` with `navigator.onLine === false`) to a typed `NetworkError` so callers can distinguish "no network" from real HTTP errors.

**Checkpoint**: Service worker registers on app load. `useOnlineStatus()` reports correctly. React Query and Axios both surface network failures as `NetworkError`. The app still has no PWA-visible UX yet — that arrives in US1.

---

## Phase 3: User Story 1 — Cài đặt và sử dụng ứng dụng từ điện thoại như một app (P1) 🎯 MVP

**Goal**: A user can install the app on their phone, log in, perform every desktop workflow on a phone in portrait (including the full sectioned create-bill wizard), and see a clear Vietnamese banner if connectivity drops with their typed data preserved.

**Independent Test**: Per `quickstart.md` §5/§6 — install on Android Chrome and iOS Safari, log in, search a bill, update its status, complete the create-bill wizard, see the PDF preview, share/download/print it, simulate connection loss and verify the banner + form-data preservation. All Vietnamese with diacritics intact.

### Tests for User Story 1

- [X] T014 [P] [US1] Component test: `<InstallPrompt>` Vietnamese banner appears on `beforeinstallprompt`, `prompt()` is called on accept, dismiss persists for 30 days in `localStorage`, banner is suppressed when `display-mode: standalone` matches — in `frontend/src/pwa/__tests__/InstallPrompt.test.jsx`.
- [X] T015 [P] [US1] Component test: `<ConnectionBanner>` mounts on `offline` event within 5 s, unmounts on `online` event within 5 s, shows the exact Vietnamese text from FR-010 — in `frontend/src/pwa/__tests__/ConnectionBanner.test.jsx`.
- [X] T016 [P] [US1] Component test: `<BillCreateMobile>` renders 6 Vietnamese steps; `next` is blocked when current step has invalid required fields and the step indicator shows a red dot for that step; `<ConfirmStep>` jump-back links preserve data in other sections — in `frontend/src/features/bills/create/__tests__/BillCreateMobile.test.jsx`.
- [X] T017 [P] [US1] Component test: `<PdfPreviewScreen>` fetches the PDF blob, renders the iframe, "Tải xuống" produces a download anchor, "Chia sẻ" calls a mocked `navigator.share` with the file (and falls back gracefully when `canShare({ files })` is false), "In" calls `iframe.contentWindow.print()`, and revokes the object URL on unmount — in `frontend/src/features/bills/create/__tests__/PdfPreviewScreen.test.jsx`.
- [X] T018 [P] [US1] Playwright E2E (Mobile Chrome / Pixel 5): install affordance is shown on first visit, dismiss persists, suppressed after `display-mode: standalone` — in `frontend/tests/e2e/install-android.spec.ts`.
- [X] T019 [P] [US1] Playwright E2E (Mobile Safari / iPhone 14): iOS instruction overlay appears on first visit, dismiss persists, suppressed when `navigator.standalone === true` — in `frontend/tests/e2e/install-ios.spec.ts`.
- [X] T020 [P] [US1] Playwright E2E (Mobile Chrome): full create-bill wizard happy path (fill all 6 sections, jump back from confirm, submit, land on PDF preview); validation-error path (advance from sender with empty receiver phone field, see red dot) — in `frontend/tests/e2e/create-bill-mobile.spec.ts`.
- [X] T021 [P] [US1] Playwright E2E (Mobile Chrome): mid-step `context.setOffline(true)` shows the Vietnamese banner within 5 s, typed data in the current step is preserved across `setOffline(false)` and the banner disappears within 5 s — in `frontend/tests/e2e/connection-loss.spec.ts`.
- [X] T022 [P] [US1] Playwright E2E (Mobile Chrome): PDF preview screen loads after a created bill, "Tải xuống" triggers a `download` event with filename `phieu-gui-{id}.pdf`, "Chia sẻ" is enabled, "In" opens the print dialog (mocked) — in `frontend/tests/e2e/pdf-preview.spec.ts`.

### Implementation for User Story 1

- [X] T023 [P] [US1] Create `frontend/src/pwa/InstallPrompt.jsx` (Android/Chromium variant): listen for `beforeinstallprompt`, stash the deferred event, render a Vietnamese Ant Design `<Alert>` banner with "Cài đặt" / "Để sau" actions; "Cài đặt" calls `deferredPrompt.prompt()`; "Để sau" sets `localStorage.setItem('pwa-install-dismissed-at', Date.now())` and the banner is hidden for 30 days; suppress entirely when `window.matchMedia('(display-mode: standalone)').matches`.
- [X] T024 [P] [US1] Add the iOS instruction overlay variant inside `frontend/src/pwa/InstallPrompt.jsx`: detect iOS Safari via UA + `navigator.standalone === false`, render a dismissible Vietnamese overlay "Bấm Chia sẻ → Thêm vào Màn hình chính" with a small share-icon SVG; same 30-day dismiss persistence key.
- [X] T025 [P] [US1] Create `frontend/src/pwa/ConnectionBanner.jsx`: uses `useOnlineStatus()`, renders a fixed-top Vietnamese Ant Design `<Alert type="warning">` "Mất kết nối — vui lòng kiểm tra mạng và thử lại" when `online === false`.
- [X] T026 [P] [US1] Create `frontend/src/pwa/NoConnectionScreen.jsx`: full-screen Vietnamese message "Cần kết nối mạng để sử dụng ứng dụng" with a "Thử lại" button that calls `window.location.reload()`. Used as the app shell's child when `useOnlineStatus().online === false` AND no app data has been loaded yet (FR-012).
- [X] T027 [P] [US1] Create `frontend/src/pwa/CompatNotice.jsx`: feature-detect `'serviceWorker' in navigator && window.isSecureContext`; if false, render a small once-per-session Vietnamese banner "Trình duyệt không hỗ trợ — phiên bản web vẫn hoạt động" (FR-019).
- [X] T028 [US1] Mount `<InstallPrompt>`, `<ConnectionBanner>`, `<CompatNotice>`, and the `<NoConnectionScreen>` gating logic globally in `frontend/src/App.jsx` (the existing root component).
- [X] T029 [US1] Add `inputMode` hints (FR-007) to bill-form input components shared between desktop and mobile (e.g., `frontend/src/features/bills/components/PhoneInput.jsx`, `WeightInput.jsx`, `FeeInput.jsx`, `QuantityInput.jsx` — adapt to actual file names in 001's frontend) — `tel` for phones, `decimal` for weight/fees, `numeric` for quantity. Vietnamese-text inputs keep default behaviour.
- [X] T030 [P] [US1] Create `frontend/src/features/bills/create/useBillDraft.js` — exports `useBillDraft()` returning a `react-hook-form` instance configured with the existing bill Zod schema (re-imported from the desktop form's schema file), and `<BillDraftProvider>` that wraps children in `FormProvider` so step components can call `useFormContext()`.
- [X] T031 [P] [US1] Create `frontend/src/features/bills/create/steps/SenderStep.jsx` (Người gửi) — renders sender-block fields (name, address, district, province, phone) using `useFormContext()`; exposes the field-name array `SENDER_FIELDS` for per-step validation.
- [X] T032 [P] [US1] Create `frontend/src/features/bills/create/steps/ReceiverStep.jsx` (Người nhận) — receiver fields and `RECEIVER_FIELDS`.
- [X] T033 [P] [US1] Create `frontend/src/features/bills/create/steps/ContentsStep.jsx` (Nội dung hàng) — package contents (description, quantity, weight, length × width × height) and `CONTENTS_FIELDS`.
- [X] T034 [P] [US1] Create `frontend/src/features/bills/create/steps/ServiceStep.jsx` (Dịch vụ) — service category and tier selection and `SERVICE_FIELDS`.
- [X] T035 [P] [US1] Create `frontend/src/features/bills/create/steps/FeesStep.jsx` (Cước phí) — cước chính, phụ phí xăng dầu, phụ phí khác, VAT, tổng cộng, payer (sender vs receiver) and `FEES_FIELDS`.
- [X] T036 [P] [US1] Create `frontend/src/features/bills/create/steps/ConfirmStep.jsx` (Xác nhận) — read-only Vietnamese summary grouped by section, each section header has a "Sửa" link that calls a `goToStep(n)` callback (preserving form data). Submit button "Lưu & In phiếu".
- [X] T037 [US1] Create `frontend/src/features/bills/create/BillCreateMobile.jsx` — wires Ant Design `<Steps direction="horizontal" size="small">`, `<BillDraftProvider>`, renders the active step component, "Tiếp tục" calls `trigger(stepFields)` and advances on pass, validation errors set a per-step error state used to render red dots on `<Steps>`, submit handler reuses the existing desktop `POST /bills` mutation. **Depends on T030–T036**.
- [X] T038 [P] [US1] Create `frontend/src/features/bills/create/PdfPreviewScreen.jsx` — accepts `:id` from route, uses React Query to fetch `GET /api/bills/{id}/print?format=pdf` with `responseType: 'blob'`, creates an object URL, embeds in `<iframe src={url}>`. Three Vietnamese action buttons: "Tải xuống" (anchor with `download="phieu-gui-{id}.pdf"`), "Chia sẻ" (calls `navigator.share({ files: [new File([blob], …)] })` if `navigator.canShare({ files })`, otherwise shows fallback Vietnamese "Trình duyệt không hỗ trợ chia sẻ — vui lòng tải xuống"), "In" (loads PDF into a hidden iframe and calls `iframe.contentWindow.print()`). Revoke object URL on unmount.
- [X] T039 [US1] In `frontend/src/routes/index.jsx`: add routes `/bills/new` (existing — wrap in `<ResponsiveShell desktop={<BillCreateDesktop/>} mobile={<BillCreateMobile/>}/>`) and a new `/bills/new/mobile/preview/:id` route that renders `<PdfPreviewScreen>`.
- [X] T040 [US1] In `frontend/src/features/bills/create/BillCreateMobile.jsx` submit success handler: navigate to `/bills/new/mobile/preview/{newBill.id}` (depends on T039).
- [X] T041 [US1] Update logout in `frontend/src/auth/` (existing module — adapt to actual filename, likely `useAuth.js` or `authSlice.js`): after clearing the JWT, call `if ('caches' in window) await Promise.all((await caches.keys()).filter(k => k.startsWith('user-')).map(k => caches.delete(k)))` (FR-017, FR-020). Today there are no `user-*` caches, but the helper documents the privacy contract.
- [X] T042 [US1] Apply mobile breakpoint to existing list/detail/search/status routes by wrapping their root components in a small media-query CSS class (or by adding `xs={24} md={...}` Ant Design Col props) so they render single-column on phones (FR-005, FR-006). Touch up at minimum: `frontend/src/features/bills/list/BillList.jsx`, `BillDetail.jsx`, `BillStatusUpdate.jsx`, `frontend/src/features/customers/CustomerList.jsx`, `CustomerDetail.jsx` (adapt names to 001's actual files).
- [X] T043 [US1] Run the US1 component + E2E tests: `cd frontend && npm test -- --run` and `npx playwright test --project="Mobile Chrome" --project="Mobile Safari" -g "(install|create-bill-mobile|connection-loss|pdf-preview)"`. Fix any failures before checkpoint.

**Checkpoint**: User Story 1 is fully functional and independently testable. The app installs on Android and iOS, every existing workflow works on a phone, the create-bill wizard guides users through 6 sections with section-level validation, the PDF preview screen lets users download/share/print, and connection loss is surfaced clearly with form data preserved. **This is the MVP — could ship to production here.**

---

## Phase 4: User Story 2 — Cập nhật ứng dụng tự động (P2)

**Goal**: When a new version of the frontend is deployed, every installed phone picks it up automatically; mid-task users see an unobtrusive Vietnamese update affordance and are never interrupted; a Vietnamese version label is visible to support.

**Independent Test**: Per `quickstart.md` §7 — bump `frontend/package.json` version, rebuild, refresh on the installed phone, observe the Vietnamese update affordance, accept it, verify the new version label appears on the Settings/About screen. Verify the prompt is suppressed while on `/bills/new/mobile`.

### Tests for User Story 2

- [X] T044 [P] [US2] Component test: `<UpdatePrompt>` renders the Vietnamese affordance when `onNeedRefresh` fires; clicking "Cập nhật" calls a mocked `updateSW(true)`; the prompt is suppressed when the current route matches `/bills/new/mobile` and re-enabled when navigating away — in `frontend/src/pwa/__tests__/UpdatePrompt.test.jsx`.
- [X] T045 [P] [US2] Component test: `<AboutScreen>` renders the Vietnamese string `Phiên bản: v{APP_VERSION} ({APP_GIT_SHA})` using mocked globals — in `frontend/src/features/settings/__tests__/AboutScreen.test.jsx`.
- [X] T046 [P] [US2] Playwright E2E (Mobile Chrome): mock `virtual:pwa-register` to fire `onNeedRefresh`; assert the Vietnamese affordance is shown; navigate to `/bills/new/mobile` and assert it is suppressed; navigate away and assert it returns; click "Cập nhật" and assert `updateSW(true)` is called — in `frontend/tests/e2e/auto-update.spec.ts`.

### Implementation for User Story 2

- [X] T047 [P] [US2] Create `frontend/src/pwa/UpdatePrompt.jsx` — subscribes to `onNeedRefresh` from the registerSW event bus (T007), renders an Ant Design `notification` placement="bottomRight" with Vietnamese text "Có phiên bản mới — tải lại để cập nhật" and an "Cập nhật" button that calls `updateSW(true)`. Uses `useLocation()` to suppress when `pathname.startsWith('/bills/new/mobile')`; re-enables on route change.
- [X] T048 [US2] Mount `<UpdatePrompt>` globally in `frontend/src/App.jsx`. Verify with the existing US1 mounts that the order doesn't visually overlap (`<UpdatePrompt>` is bottom-right, `<ConnectionBanner>` is top, `<InstallPrompt>` is top-or-bottom; no conflict).
- [X] T049 [P] [US2] Create `frontend/src/features/settings/AboutScreen.jsx` — Ant Design `<Card title="Giới thiệu">` showing `formatVersion()` from `pwa/version.js`, Vietnamese build date from `__APP_BUILT_AT__` (extend the Vite `define` from T005 if not yet included), and a small Vietnamese paragraph describing the carrier app.
- [X] T050 [US2] Add `/settings/about` route to `frontend/src/routes/index.jsx` rendering `<AboutScreen>`. Add an "Giới thiệu / Phiên bản" item to the existing user/avatar dropdown menu (in 001's `frontend/src/components/AppHeader.jsx` or equivalent).
- [X] T051 [US2] Run the US2 tests: `cd frontend && npm test -- --run UpdatePrompt AboutScreen` and `npx playwright test --project="Mobile Chrome" -g "auto-update"`. Fix any failures.

**Checkpoint**: User Story 2 works independently. A new build is picked up by installed clients without manual reinstall; mid-wizard users are not interrupted; the version label is verifiable from the Settings/About screen. Both US1 and US2 are now shippable.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, hygiene, and an end-to-end on-device verification pass.

- [X] T052 [P] Add a "PWA developer flow" section to `frontend/README.md`: how to install `mkcert`, generate a LAN HTTPS cert, run `npm run dev -- --host`, install on a real phone, and regenerate icons after a logo change (cross-link to `specs/002-pwa-mobile-support/quickstart.md`).
- [X] T053 [P] Add a short "PWA" section to the project root `README.md` noting: install URL, the manifest path, where the version label lives, the online-only constraint, and the explicit non-features (offline, push, barcode scanning) with links to the spec's Out-of-Scope section.
- [X] T054 [P] Run `cd frontend && npm run lint && npm run format` across all new and touched files; fix any lint warnings introduced by this feature.
- [ ] T055 Execute the full `quickstart.md` §5 happy-path on a real Android phone (Chrome 100+) — capture pass/fail per scenario against `spec.md` SC-001..SC-008.
- [ ] T056 Execute the full `quickstart.md` §6 happy-path on a real iOS phone (Safari 16.4+) — capture pass/fail per iOS-specific scenario (install overlay, AirPrint, Web Share file support).
- [X] T057 Run the entire test suite once more end-to-end: `cd frontend && npm test -- --run && npx playwright test`. Investigate and fix any regressions introduced by polish changes.
- [ ] T058 Verify `001-logistics-bill-app` desktop scenarios still pass (FR-021, SC-006): run any 001 Playwright specs (`--project="Desktop Chrome"`) and confirm no regressions.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup (T001–T005) being complete.
- **User Story 1 (Phase 3)**: Depends on Foundational (T006–T013).
- **User Story 2 (Phase 4)**: Depends on Foundational (T006–T013). Independent of US1 — can be parallelised with US1 by a second developer; does not require any US1 task to ship.
- **Polish (Phase N)**: Depends on US1 (and US2 if shipping both).

### User Story Dependencies

- **US1 (P1)**: independent of US2. Ships as MVP on its own.
- **US2 (P2)**: independent of US1 (the version label and update affordance work without the install/wizard flow being present). Can be shipped before, after, or alongside US1.

### Within US1

- T014–T022 (tests) parallel with each other; written alongside the implementation tasks they cover.
- T023, T024, T025, T026, T027 (cross-cutting components) all `[P]` — different files.
- T028 mounts them in `App.jsx` — sequential after T023–T027.
- T030 (`useBillDraft`) before T031–T036 (steps) which can all run in parallel.
- T037 (`BillCreateMobile`) depends on T030–T036.
- T038 (`PdfPreviewScreen`) parallel with T037.
- T039 (routes) before T040 (submit-success navigation).
- T041 (logout cache cleanup) and T042 (mobile breakpoints on existing routes) parallel with the wizard work.
- T043 last in US1 — runs the US1 test suite.

### Within US2

- T044–T046 (tests) parallel with implementation.
- T047 and T049 parallel (different files).
- T048 sequential after T047.
- T050 sequential after T049.
- T051 last in US2.

---

## Parallel Example: User Story 1

```bash
# After Foundational (T006–T013) is done, kick off the cross-cutting components in parallel:
Task: "Implement <InstallPrompt> in frontend/src/pwa/InstallPrompt.jsx"           # T023
Task: "Add iOS overlay variant in frontend/src/pwa/InstallPrompt.jsx"             # T024 (same file — sequential after T023)
Task: "Implement <ConnectionBanner> in frontend/src/pwa/ConnectionBanner.jsx"     # T025
Task: "Implement <NoConnectionScreen> in frontend/src/pwa/NoConnectionScreen.jsx" # T026
Task: "Implement <CompatNotice> in frontend/src/pwa/CompatNotice.jsx"             # T027

# In another track, kick off the wizard step components in parallel after T030:
Task: "Create useBillDraft.js"            # T030
# then the six step components in parallel:
Task: "Create SenderStep.jsx"    # T031
Task: "Create ReceiverStep.jsx"  # T032
Task: "Create ContentsStep.jsx"  # T033
Task: "Create ServiceStep.jsx"   # T034
Task: "Create FeesStep.jsx"      # T035
Task: "Create ConfirmStep.jsx"   # T036

# Tests can be written alongside their implementations:
Task: "Component test for <InstallPrompt>"        # T014 — paired with T023/T024
Task: "Component test for <ConnectionBanner>"     # T015 — paired with T025
Task: "Component test for <BillCreateMobile>"     # T016 — paired with T037
Task: "Component test for <PdfPreviewScreen>"     # T017 — paired with T038
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Phase 1 Setup → Phase 2 Foundational → Phase 3 US1.
2. **STOP and VALIDATE**: run `quickstart.md` §5 and §6 on real phones.
3. Deploy to staging (HTTPS required) — **this is a usable product**.

### Incremental Delivery

1. Setup + Foundational ship first as a no-visible-UX increment (manifest + SW only).
2. US1 ships next → users can install the app and use every workflow on a phone.
3. US2 ships next → installed users get auto-updates and a version label.
4. Polish ships continuously (docs and lint can land in any sprint).

### Parallel Team Strategy

- One frontend developer can complete the whole feature in roughly the order above.
- With two frontend developers: after Foundational, Dev A takes the cross-cutting PWA components + connection UX (T014–T015, T023–T028, T041, T042); Dev B takes the wizard + PDF preview (T016, T017, T020, T022, T029–T040). US2 (T044–T051) lands after either developer is free.

---

## Validation Notes

- Every task has a checkbox, sequential ID, and a concrete file path.
- `[Story]` labels (`[US1]`, `[US2]`) appear only on US1/US2-phase tasks; setup, foundational, and polish phases have no story label per the format rules.
- Every `[P]` claim has been verified against file boundaries — parallel-marked tasks touch distinct files.
- No new backend tasks: this feature is frontend-only by design (per `plan.md` Project Structure section). Tasks for backend changes are intentionally omitted; if a future need arises (e.g., `/api/system/version`), it will be a new feature, not a hidden addition here.
- No task introduces offline behaviour, push notifications, or barcode scanning — those are explicitly Out of Scope per the spec's `Clarifications` section.
