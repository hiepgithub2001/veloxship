# Phase 0 — Research: PWA Mobile Support

This document records every concrete technical decision made before design. Each entry follows the `Decision / Rationale / Alternatives` shape.

## 1. PWA tooling on top of Vite

- **Decision**: Use `vite-plugin-pwa` (currently `^0.19.x`), which wraps Workbox.
- **Rationale**:
  - The frontend already uses Vite 5; this plugin is the canonical Vite integration.
  - Generates `manifest.webmanifest` from a JS config object (no hand-written manifest), produces icons from a single source via `@vite-pwa/assets-generator`, registers the service worker, and exposes `virtual:pwa-register` for in-app update prompts.
  - Active maintenance, large ecosystem, used by Vite-React community at scale.
- **Alternatives considered**:
  - **Hand-rolled Workbox**: rejected — duplicates plumbing the plugin already provides; bigger surface to maintain.
  - **`workbox-build` directly in a Vite plugin**: rejected — same problem one level deeper.
  - **No plugin, raw service-worker file**: rejected — we lose precache versioning, hashed asset URLs, and update lifecycle hooks.

## 2. Web app manifest contents (Vietnamese)

- **Decision**:
  - `name: "VeloxShip — Phiếu Gửi"`
  - `short_name: "Phiếu Gửi"`
  - `description: "Quản lý phiếu gửi vận chuyển"`
  - `lang: "vi-VN"`, `dir: "ltr"`
  - `start_url: "/"`, `scope: "/"`, `display: "standalone"`
  - `background_color: "#ffffff"`, `theme_color: "#c0392b"` (carrier red, sampled from logo)
  - `orientation: "portrait"` for the installed launch
  - Icons: 192×192, 512×512, plus a 512×512 maskable variant for Android adaptive icons; iOS uses a separate `apple-touch-icon` 180×180 declared in `<head>` (Safari ignores manifest icons).
- **Rationale**:
  - `display: standalone` gives the no-browser-chrome look required by FR-003.
  - Vietnamese `name` / `short_name` satisfies FR-001 / FR-002 and SC-007.
  - `orientation: portrait` matches the user-stated phone-portrait usage; doesn't lock desktop.
  - Maskable icon is required for clean Android adaptive icons; iOS still needs a separate PNG.
- **Alternatives**:
  - `display: fullscreen` — rejected: hides the system status bar which loses connectivity-strength awareness for drivers. `standalone` is the right balance.
  - English `name` with Vietnamese `short_name` — rejected: the long name appears in the install dialog and recent apps list; both must be Vietnamese.

## 3. Install affordance (Android + iOS)

- **Decision**:
  - On Android / Chromium: listen for the `beforeinstallprompt` event, stash the deferred event, and surface a custom Vietnamese banner ("Cài đặt ứng dụng vào màn hình chính") with two actions: "Cài đặt" (calls `prompt()` on the deferred event) and "Để sau" (dismisses; remember dismissal in `localStorage` for 30 days).
  - On iOS Safari: there is no `beforeinstallprompt`. Detect iOS Safari via UA + `navigator.standalone === false`, then show a Vietnamese instruction overlay: "Bấm Chia sẻ → Thêm vào Màn hình chính" with a small share-icon illustration, dismissible.
  - Suppress the banner entirely once the app is launched in standalone mode (`window.matchMedia('(display-mode: standalone)').matches === true`) or once the user dismisses it within the rolling window.
- **Rationale**: matches FR-002 exactly; respects platform constraints; doesn't nag (FR-018 spirit even though notifications are deferred — the same "don't pester" principle applies to install too).
- **Alternatives**:
  - Browser's mini-infobar only (no custom UI): rejected — Chrome stopped showing the mini-infobar by default in 2018; users would never see it.
  - In-app permanent settings link only ("Cài đặt từ menu"): rejected — discoverability is too low for first-visit drivers.

## 4. Service-worker caching strategy (online-only constraint)

- **Decision**:
  - **Precache** the app shell (HTML entry, hashed JS/CSS bundles, fonts, PWA icons) via `vite-plugin-pwa`'s built-in Workbox manifest injection. This is what makes the app **installable** and **launchable** quickly — it is *not* an offline data cache.
  - **Runtime caching for `/api/*`**: `NetworkOnly`. No fallback to a cached response. If the network call fails, the request rejects and the app shows the connection banner.
  - **`navigateFallback` set to `index.html`** for SPA routing — but only when the user is online. When offline, the app shows the "Cần kết nối mạng để sử dụng ứng dụng" screen (FR-012).
  - **No background sync**, **no IndexedDB writes**, **no message queue**.
- **Rationale**: The user's clarification explicitly removed offline. Precaching the shell is required by PWA semantics (installable, fast launch) but precaching does *not* mean serving stale business data — those are independent caches. This split satisfies online-only while still meeting SC-001 install/launch performance.
- **Alternatives**:
  - **Don't precache anything**: rejected — installability requires at least the start URL to be available; without precache, the first launch on a poor connection looks broken.
  - **`StaleWhileRevalidate` on `/api/*`**: rejected — would silently show stale data, contradicting FR-009 and FR-012.

## 5. Connection-loss detection and UX

- **Decision**:
  - A `useOnlineStatus()` hook reads `navigator.onLine` and listens to `online` / `offline` window events.
  - On transition to offline, mount `<ConnectionBanner>` at the top of the app shell with the Vietnamese message "Mất kết nối — vui lòng kiểm tra mạng và thử lại". The banner remains until the next `online` event.
  - For React Query: set `networkMode: 'online'` globally so queries pause while offline and resume on reconnect (no automatic retry storms).
  - For form submissions (Axios `POST` / `PUT`): on a network error, the existing form state is preserved (react-hook-form keeps it in component memory until unmount); show a Vietnamese inline retry control next to the submit button.
  - Add a `<NoConnectionScreen>` shown when the app is launched while `navigator.onLine === false`. This screen has a "Thử lại" button and does not render the rest of the app until connectivity is restored.
- **Rationale**: `navigator.onLine` is unreliable on its own (it can return `true` while requests still fail), but combined with actual request-failure handling in Axios interceptors it is the standard approach. The banner reflects browser state; the inline retry handles per-request failure.
- **Alternatives**:
  - Active heartbeat ping every N seconds: rejected — adds traffic, drains battery; the browser's online/offline events plus per-request error handling cover the same ground.
  - Auto-resubmit failed POSTs on reconnect: rejected — would resurrect the offline-queue scope the user explicitly removed.

## 6. Mobile sectioned form (the create-bill wizard)

- **Decision**:
  - On viewport `< 768px` (Ant Design `xs` + `sm` breakpoints), the create-bill route renders `<BillCreateMobile>` instead of `<BillCreateDesktop>`. The desktop component is unchanged.
  - `<BillCreateMobile>` uses Ant Design `<Steps direction="horizontal" size="small">` at the top showing 6 steps with Vietnamese labels and validation status icons (red dot if a step has unresolved errors).
  - All step components share a single `react-hook-form` instance via `<FormProvider>`; each step renders only the fields it owns but submits to the same schema and the same submit handler used by desktop.
  - Per-step "Tiếp tục" button calls `trigger(['fieldA','fieldB',…])` for that step's fields; only proceeds if local validation passes.
  - The final step `<ConfirmStep>` shows a read-only Vietnamese summary grouped by section, with "Sửa" links that jump back to the relevant step (preserving form state).
  - On submit, the same POST `/bills` endpoint is called; on success, navigation goes to `/bills/new/mobile/preview/:id` (the PDF preview screen).
- **Rationale**: matches the user's "smart way to align sections" requirement (clarification Q2). One source of truth for validation. No duplication of business rules.
- **Alternatives**:
  - **Accordion on phone (all sections in one scroll)**: rejected — 20+ fields in a phone scroll loses context and tap reach; the spec explicitly asked for sectioned navigation with a progress indicator.
  - **Tabs on phone**: rejected — tabs imply non-linearity; the bill flow is naturally linear (sender first, fees last). `<Steps>` communicates linearity better.
  - **Independent state per step**: rejected — would require a separate "draft" data model and a save-and-restore mechanism, which is exactly what offline scope was. Sharing one form context keeps state in memory only.

## 7. Mobile print — PDF preview, OS share, OS print

- **Decision**:
  - Reuse `GET /api/bills/{bill_id}/print?format=pdf` (existing endpoint from 001). No backend change.
  - On mobile, after a successful `POST /bills`, navigate to `/bills/new/mobile/preview/:id`.
  - The screen fetches the PDF as a blob via Axios with `responseType: 'blob'`, creates an object URL, and renders it inside an `<iframe>` for preview. Below the preview are three Vietnamese action buttons:
    - **Tải xuống** → anchor with `download="phieu-gui-{id}.pdf"`.
    - **Chia sẻ** → calls `navigator.share({ files: [new File([blob], …)] })` if `navigator.canShare({ files })` returns true; otherwise shows a Vietnamese fallback "Trình duyệt không hỗ trợ chia sẻ — vui lòng tải xuống".
    - **In** → loads the PDF into a hidden iframe and calls `iframe.contentWindow.print()`. iOS Safari and Android Chrome honour this and surface their respective print pickers.
  - Object URLs are revoked on unmount.
- **Rationale**: zero backend work; reuses the existing print pipeline; OS handles printer selection.
- **Alternatives**:
  - **Direct browser print (`window.print()` on the bill HTML)**: rejected — the printable HTML lives only on desktop; on phones we'd need to render the same Vietnamese HTML+barcode+QR exactly, but the WeasyPrint server already does this perfectly. Using its PDF avoids a second print pipeline.
  - **Send PDF to user via email automatically**: rejected — out of scope (no notifications, no email infrastructure changes).

## 8. Auto-update strategy

- **Decision**:
  - `vite-plugin-pwa` `registerType: 'prompt'`. On a new SW being detected (after a deploy), `onNeedRefresh` fires.
  - Show `<UpdatePrompt>`: a small Ant Design `notification` at the bottom-right with "Có phiên bản mới — tải lại để cập nhật" and an "Cập nhật" button. The button calls `updateSW(true)` which triggers `skipWaiting` + reload.
  - Critical: if the user is mid-wizard (URL matches `/bills/new/mobile`), the prompt is suppressed until they leave the wizard — preventing a refresh from blowing away in-progress form data (FR-014).
- **Rationale**: balances FR-013 (auto-update) with FR-014 (don't interrupt). `registerType: 'autoUpdate'` would activate immediately, which violates FR-014.
- **Alternatives**:
  - `registerType: 'autoUpdate'` (no prompt): rejected — would surprise-reload mid-form.

## 9. Version identifier

- **Decision**:
  - Vite `define` block injects `__APP_VERSION__` (from `package.json` `version`) and `__APP_GIT_SHA__` (from `git rev-parse --short HEAD` at build time, falling back to `"dev"` outside CI).
  - Render as "v{version} ({sha})" on a new Settings/About screen reachable from the avatar menu, in Vietnamese ("Phiên bản: v0.2.0 (a1b2c3d)").
- **Rationale**: satisfies FR-015 (version visible to support); zero runtime cost; updates with every build.
- **Alternatives**:
  - Backend version endpoint `/api/system/version`: rejected — couples the frontend version label to a backend round-trip; backend version isn't necessarily the same as deployed frontend version; needless API surface.

## 10. Browser compatibility floor and graceful degradation

- **Decision**: Support floor is **Chrome 100+ on Android**, **Safari 16.4+ on iOS**, **Edge 100+**, **Firefox latest** (Firefox doesn't support installable PWAs on Android out of the box but the responsive site still works). Below the floor, the app degrades to a regular responsive site; FR-019 dictates a small Vietnamese "ứng dụng không thể cài đặt trên trình duyệt này" banner shown once per session via a feature-detection check (`'serviceWorker' in navigator && window.isSecureContext`).
- **Rationale**: Safari 16.4 is the first version that fixes most PWA layout quirks on iOS; older OSes get a working website without install. Chrome 100+ is widely available on Android; Firefox is a small minority on Android in our target market.
- **Alternatives**:
  - Block older browsers: rejected — punishes users for the wrong reason; the responsive site works fine.
  - Force users to install Chrome: rejected — not our place.

## 11. Logout, privacy, and per-user state

- **Decision**:
  - Existing logout (clear JWT in `localStorage`, reset Axios auth header, redirect to `/login`) is unchanged.
  - Add: on logout, also call `caches.delete()` for any per-user runtime caches. Today there are none (we don't cache business data), but the helper is in place to prevent future drift if a teammate later adds runtime caching.
  - Service-worker precache (app shell only) is *not* per-user and is *not* cleared on logout — it contains no business data.
- **Rationale**: FR-017 / FR-020 require that a subsequent user on the same device cannot see business data without re-authenticating. Since we don't cache business data, the JWT clear is sufficient today; the explicit `caches.delete()` hook future-proofs the privacy guarantee.
- **Alternatives**: clearing the precache on logout: rejected — would force every login to re-download the bundle, hurting SC-001.

## 12. Tap-target sizes, viewport, and safe-area handling

- **Decision**:
  - Add a global mobile stylesheet (`src/styles/mobile.css`) that:
    - Overrides Ant Design's default 32 px button height on mobile breakpoints to 44 px (iOS HIG / Android Material guidance).
    - Sets `padding-top: env(safe-area-inset-top)` and matching bottom/left/right on the app shell so notched devices don't clip content.
    - Adds `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">` to `index.html` (replacing the existing tag).
    - Adds `<meta name="theme-color" content="#c0392b">`, `<meta name="apple-mobile-web-app-capable" content="yes">`, `<meta name="apple-mobile-web-app-status-bar-style" content="default">`, and the apple-touch-icon link.
- **Rationale**: meets FR-006; gives the standalone iOS launch a clean status bar; ensures notched devices look right.
- **Alternatives**: per-component overrides — rejected, would scatter sizing rules across many files.

## 13. Mobile keyboard hints

- **Decision**: Existing form inputs use Ant Design `<Input>` / `<InputNumber>`. Add explicit `inputMode` attributes:
  - Phone numbers: `inputMode="tel"`.
  - Weight, dimensions, fees: `inputMode="decimal"` (Vietnamese decimal — comma — is handled by react-hook-form normalisation).
  - Quantity, count fields: `inputMode="numeric"`.
  - Names, addresses, descriptions: default text (Vietnamese diacritic input is handled by the system IME).
- **Rationale**: meets FR-007; one-line attributes; no library work.
- **Alternatives**: HTML `type="number"` for fees: rejected — strips trailing zeros and hides decimal separators on some Android keyboards; `inputMode="decimal"` keeps the visible separator.

## 14. Testing approach for the new mobile surface

- **Decision**:
  - **Component tests** (Vitest + Testing Library) for: `<InstallPrompt>` permission/dismissal flow, `<UpdatePrompt>` `onNeedRefresh` wiring, `<ConnectionBanner>` reaction to `online`/`offline` events, `<BillCreateMobile>` step-navigation and validation badges, `<PdfPreviewScreen>` action buttons (mocking `navigator.share`).
  - **Playwright mobile-emulation E2E** for two devices (Pixel 5 + iPhone 14):
    - Install affordance shown / dismissible / suppressed-after-install.
    - Full create-bill wizard happy path with validation errors.
    - Connection-loss banner appears within 5 s of `context.setOffline(true)` and disappears within 5 s of restoration.
    - PDF preview screen loads, share button is enabled (where supported), download triggers a file save.
  - **No unit tests for the service worker itself** — Workbox's own test suite covers correctness; we test the *registration* hook in `main.jsx` only.
- **Rationale**: matches existing 001 testing layering; Playwright already configured.
- **Alternatives**: Lighthouse CI for PWA score: nice-to-have, deferred to ops; not part of this plan's task list.

## 15. CI/build implications

- **Decision**:
  - Add an icon-generation step to the build (`@vite-pwa/assets-generator` run from a single `image_data/logo.jpg` source) so the four PNG icon variants are produced reproducibly. Generated files are committed under `frontend/public/` so production builds don't depend on the asset generator at build time.
  - The Vite build now emits `sw.js` and `manifest.webmanifest` in addition to the existing bundle.
  - No backend change → no new Alembic migration; no `requirements.txt` change.
- **Rationale**: keeps build deterministic; doesn't add runtime asset generation.
- **Alternatives**: build-time icon generation on every CI run: rejected — adds CI minutes for assets that change rarely.

---

All `[NEEDS CLARIFICATION]` items from the Technical Context have been resolved by the spec's Clarifications session and the decisions above. Ready for Phase 1.
