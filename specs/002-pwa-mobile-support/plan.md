# Implementation Plan: Hỗ trợ Điện thoại qua PWA (Mobile Support via PWA)

**Branch**: `002-pwa-mobile-support` | **Date**: 2026-04-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-pwa-mobile-support/spec.md`

## Summary

Add mobile-phone usability to the existing logistics bill webapp (`001-logistics-bill-app`) by turning the React + Vite frontend into an installable Progressive Web App. The app must:

1. Install to the home screen on Android (Chrome/Edge) and iOS (Safari) with the company logo, a Vietnamese app name, and a standalone launch experience.
2. Render every existing desktop workflow legibly on a phone in portrait — including the multi-section "Phiếu Gửi" creation form, which becomes a stepped Vietnamese-labelled wizard on small screens (Người gửi → Người nhận → Nội dung hàng → Dịch vụ → Cước phí → Xác nhận).
3. Show a clear Vietnamese connection-loss banner when the device drops connectivity, preserve typed-but-unsent form data, and require an active connection for every read and write workflow (no offline queue, no background sync — explicitly removed by clarification).
4. End the mobile bill-creation flow with a PDF preview screen that reuses the existing `GET /bills/{bill_id}/print?format=pdf` endpoint and hands the file to the OS share sheet (`navigator.share`) and OS print dialog.
5. Auto-update via a service worker: a new build is picked up transparently; mid-task users see an unobtrusive "Có phiên bản mới — tải lại để cập nhật" affordance and are never interrupted.

Push notifications and camera-based barcode scanning are explicitly deferred. The backend domain (bills, customers, statuses, audit) is reused as-is; no new business endpoints are introduced.

## Technical Context

**Language/Version**: JavaScript ES2022 on Node.js 20 LTS (frontend). No new backend language work.

**Primary Dependencies (additions only — existing 001 stack is preserved)**:

- **`vite-plugin-pwa`** (Workbox-based) — generates the web app manifest, registers a service worker, and provides the `registerSW` API for the auto-update affordance. Chosen over hand-rolling Workbox to stay aligned with the existing Vite build.
- **`workbox-window`** (transitive via `vite-plugin-pwa`) — drives the in-page update UX (`onNeedRefresh`, `onOfflineReady`).
- No new backend dependencies. The existing `weasyprint`-generated PDF endpoint is the substrate for mobile print.

**Storage**: No new persistent storage. Service-worker precache stores app-shell files (HTML/JS/CSS, fonts, icons). **No business data is cached** (per the online-only clarification); API calls go straight to the network.

**Testing**:

- Unit / component: existing `vitest` + `@testing-library/react`.
- New: `vite-plugin-pwa` ships `mode: 'development'` for SW work; tests for the manifest and SW registration are smoke-level only.
- E2E: Playwright already in stack — add mobile-emulation specs (Pixel 5, iPhone 14) covering install detection, sectioned create-bill wizard, connection-loss banner, and PDF preview share/print buttons.

**Target Platform**: Mobile browsers — at minimum Chrome 100+ on Android and Safari 16.4+ on iOS (Safari 16.4 is the floor that fixes several PWA quirks). Desktop browsers continue to work as before; the PWA layer is additive.

**Project Type**: Web application — extends the existing `frontend/` + `backend/` split. No new top-level project.

**Performance Goals (mobile)**:

- App-shell cold launch on a typical 4G phone ≤ 3 s (SC-001 install workflow ≤ 2 minutes).
- Bill status update on a phone reflected on a desktop view ≤ 5 s while both are online (SC-002).
- Connection-loss banner visible within 5 s of network drop (SC-003).
- Sectioned mobile create-bill flow no slower than 1.5× desktop creation time (SC-004a).

**Constraints**:

- Online-only — no IndexedDB cache of business data, no background sync, no offline queue (per clarification).
- Must serve over HTTPS in production (PWA hard requirement).
- Print layout on phone PDF preview must match the desktop print layout byte-for-byte where possible (we reuse the existing WeasyPrint pipeline).
- Vietnamese diacritics on every PWA-introduced surface (manifest `name`, `short_name`, install banners, connection banner, update affordance, PDF preview action labels, version label).
- No regression to feature `001-logistics-bill-app` — desktop counter workflow stays exactly as today.

**Scale/Scope**: Same scale as 001 (~10–50 staff users, ~100k bills/year, ~5k saved customers). Mobile usage is a fraction of total; the PWA does not change backend load characteristics.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution at `.specify/memory/constitution.md` is the unfilled template (placeholder principles only). There are therefore **no project-specific gates to evaluate**. The plan adopts the same defaults as feature `001-logistics-bill-app`:

- Tests written alongside features (unit/component + Playwright mobile-emulation).
- Layered structure preserved — the PWA layer sits above existing frontend modules without reorganising them.
- Public surface stays the existing FastAPI HTTP API; no new domain endpoints.

**Result**: PASS (no enforceable gates). Re-evaluation post-Phase 1: still PASS.

## Project Structure

### Documentation (this feature)

```text
specs/002-pwa-mobile-support/
├── spec.md              # Feature specification (with Clarifications session)
├── plan.md              # This file
├── research.md          # Phase 0 — PWA tooling, install affordance, sectioned-form, mobile print, update strategy
├── data-model.md        # Phase 1 — minimal: App Version Record only (no DB tables)
├── quickstart.md        # Phase 1 — local + on-device testing instructions
├── contracts/
│   └── pwa-additions.md # Phase 1 — manifest contract + reused PDF endpoint contract
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 — generated by /speckit-tasks
```

### Source Code (repository root)

This feature **adds files** to the existing layout; it does not move or rename anything in `001-logistics-bill-app`. New paths are marked `[NEW]`.

```text
frontend/
├── public/
│   ├── pwa-icon-192.png         [NEW] derived from image_data/logo.jpg
│   ├── pwa-icon-512.png         [NEW]
│   ├── pwa-icon-maskable-512.png [NEW] safe-area-padded for Android adaptive icons
│   └── apple-touch-icon-180.png [NEW] iOS home-screen icon
├── index.html                    # extend <head>: theme-color, viewport, apple-mobile-web-app-* meta tags
├── vite.config.js                # add VitePWA plugin block (manifest, workbox runtimeCaching, registerType)
├── package.json                  # add vite-plugin-pwa, workbox-window
└── src/
    ├── main.jsx                  # call registerSW() with onNeedRefresh / onOfflineReady callbacks
    ├── pwa/                      [NEW]
    │   ├── registerSW.js         # wrapper around virtual:pwa-register
    │   ├── InstallPrompt.jsx     # Vietnamese install banner (beforeinstallprompt) + iOS overlay
    │   ├── UpdatePrompt.jsx      # "Có phiên bản mới — tải lại để cập nhật"
    │   ├── ConnectionBanner.jsx  # "Mất kết nối — vui lòng kiểm tra mạng và thử lại"
    │   ├── useOnlineStatus.js    # hook over navigator.onLine + online/offline events
    │   └── version.js            # exports __APP_VERSION__ baked at build time
    ├── App.jsx                   # mount InstallPrompt, UpdatePrompt, ConnectionBanner globally
    ├── components/
    │   └── ResponsiveShell.jsx   [NEW] media-query gate that picks mobile vs desktop layout
    ├── features/
    │   └── bills/
    │       ├── create/
    │       │   ├── BillCreateDesktop.jsx   # existing single-page form, unchanged
    │       │   ├── BillCreateMobile.jsx    [NEW] Ant Design <Steps> wizard
    │       │   ├── steps/                  [NEW]
    │       │   │   ├── SenderStep.jsx
    │       │   │   ├── ReceiverStep.jsx
    │       │   │   ├── ContentsStep.jsx
    │       │   │   ├── ServiceStep.jsx
    │       │   │   ├── FeesStep.jsx
    │       │   │   └── ConfirmStep.jsx
    │       │   ├── useBillDraft.js         [NEW] react-hook-form context shared across steps
    │       │   └── PdfPreviewScreen.jsx    [NEW] post-save mobile screen (download / share / print)
    │       └── ...                          # existing list/detail/search/status views
    ├── routes/
    │   └── index.jsx                       # add /bills/new/mobile/preview/:id route
    └── styles/
        └── mobile.css                      [NEW] tap-target sizing, safe-area-inset, viewport-fit
```

**Structure Decision**: Web application, **frontend-only changes**. The backend stays untouched in v1 — the PDF print endpoint already returns `application/pdf` and is sufficient for the mobile preview / OS share / OS print flow. The PWA work is bounded to `frontend/`, with the bulk under `frontend/src/pwa/` (cross-cutting components) and `frontend/src/features/bills/create/` (the sectioned mobile wizard).

## Complexity Tracking

> No constitution violations to justify. Constitution is a placeholder; no gates apply.

This feature introduces *no* new complexity above what its scope demands:

- No new backend endpoints, no new database tables, no new domain entities — the feature is a delivery-channel + UX layer.
- The mobile create-bill wizard duplicates the desktop form's *layout* but shares the same `react-hook-form` schema, validation rules, and submit handler — there is one source of truth for bill validation.
- The service worker uses the simplest viable Workbox strategy: precache the app shell, `NetworkOnly` for `/api/*`. No runtime caching of business data.

| Decision | Why this and not simpler? |
|----------|---------------------------|
| `vite-plugin-pwa` instead of hand-rolled Workbox | Hand-rolling means writing a manifest by hand, registering a service worker by hand, and reimplementing `registerSW`'s update-detection. The plugin is the smaller surface and is the standard for Vite. |
| Separate mobile create-bill component instead of CSS-only responsive form | The form has 6 logical sections and 20+ fields with cross-field validation. A single CSS-only collapse on phone leaves users scrolling through a wall of inputs; the wizard pattern matches the user's stated "smart way to align sections" requirement (clarification Q2). Validation logic is shared, so we don't fork business rules. |

## Phase 0 — Outline & Research

See [`research.md`](./research.md) for the full decisions. Headlines:

1. **PWA tooling** → `vite-plugin-pwa` (Workbox under the hood).
2. **Install affordance** → custom Vietnamese banner driven by `beforeinstallprompt` on Android/Chromium; static instruction overlay on iOS Safari.
3. **Service-worker caching strategy** → app-shell precache only; `NetworkOnly` for all `/api/*` (no business-data cache, per online-only clarification).
4. **Mobile sectioned form pattern** → Ant Design `<Steps>` with a single `react-hook-form` context shared across step components; section progress indicator + per-section validation badges.
5. **Mobile print pipeline** → reuse `GET /bills/{bill_id}/print?format=pdf`; mobile PDF preview screen with three actions: download (anchor with `download` attr), share (`navigator.share` with file), print (`window.print()` on the PDF blob loaded into an iframe).
6. **Update strategy** → `vite-plugin-pwa` `registerType: 'prompt'`; `onNeedRefresh` triggers Vietnamese affordance; user must accept (no surprise reload during a wizard).
7. **Version label** → bake `npm_package_version + git short SHA` via Vite `define`; show on Settings/About screen.
8. **Connection-loss UX** → global `useOnlineStatus` hook; `ConnectionBanner` shown on `offline` event; React Query refuses retries while offline; form state preserved by react-hook-form's component-local store.
9. **Logout clears local state** → existing logout already clears the JWT; explicitly clear PWA-related caches on logout via `caches.delete()` for any per-user namespaces (none today, but documented to prevent future drift).

## Phase 1 — Design & Contracts

See:

- [`data-model.md`](./data-model.md) — minimal: `App Version Record` is a build-time constant, not a DB row. No new tables, no migrations.
- [`contracts/pwa-additions.md`](./contracts/pwa-additions.md) — the web app manifest contract (Vietnamese name, icons, theme color, display mode), the existing PDF endpoint reused as-is, and the explicit "no new backend endpoints" statement.
- [`quickstart.md`](./quickstart.md) — how to run the dev build with PWA enabled, install on a real phone over the LAN, and exercise the wizard + connection-loss + PDF preview flows.

**Constitution re-check (post-design)**: still PASS — no gates to violate.

## Output of `/speckit-plan`

- `specs/002-pwa-mobile-support/plan.md` (this file)
- `specs/002-pwa-mobile-support/research.md`
- `specs/002-pwa-mobile-support/data-model.md`
- `specs/002-pwa-mobile-support/contracts/pwa-additions.md`
- `specs/002-pwa-mobile-support/quickstart.md`
- `CLAUDE.md` SPECKIT block updated to point at this plan

`tasks.md` is **not** generated by this command — run `/speckit-tasks` next.
