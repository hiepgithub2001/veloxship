# Phase 1 — Quickstart: Running and Testing the PWA

This guide takes you from a fresh checkout to verifying every PWA acceptance scenario from `spec.md`. It assumes feature `001-logistics-bill-app` is already runnable (backend + Postgres + frontend dev).

## Prerequisites

- Node.js 20 LTS, Python 3.11+, PostgreSQL 16 (already required by 001).
- `001-logistics-bill-app` set up per its quickstart — backend running on `:8000`, database seeded, login working.
- A real Android phone (Chrome 100+) **and** a real iOS phone (Safari 16.4+) on the same Wi-Fi as your dev machine.
- Optional: `mkcert` for a locally-trusted HTTPS cert (see step 4 — required for service-worker testing on a phone).

## 1. Install new frontend dependencies

```bash
cd frontend
npm install vite-plugin-pwa@^0.19 workbox-window@^7
npm install -D @vite-pwa/assets-generator@^0.2
```

## 2. Generate PWA icons from the logo (one-off, commit results)

```bash
cd frontend
npx pwa-assets-generator --preset minimal-2023 --transparent ../image_data/logo.jpg --output public
# Inspect public/pwa-icon-192.png, public/pwa-icon-512.png, public/pwa-icon-maskable-512.png
# Also produce apple-touch-icon-180.png from the same source:
npx pwa-assets-generator --preset minimal-2023 --transparent --apple-touch-icon-name apple-touch-icon-180 ../image_data/logo.jpg --output public
git add public/pwa-icon-*.png public/apple-touch-icon-180.png
```

If the carrier-red theme color (`#c0392b`) is wrong, sample a colour from `image_data/logo.jpg` and update `manifest.theme_color` in `vite.config.js` plus the `<meta name="theme-color">` in `index.html`.

## 3. Run the dev build with PWA enabled

```bash
cd frontend
npm run dev -- --host
```

The `--host` exposes the dev server on the LAN (e.g., `http://192.168.1.42:5173`) so the phones can reach it.

> **Note**: service workers require `https://` *or* `http://localhost`. From a phone on the LAN, plain HTTP will block the SW. Use step 4.

## 4. Local HTTPS for on-device testing (one-off)

```bash
brew install mkcert            # or apt / scoop
mkcert -install                 # adds local CA to system trust store
cd frontend
mkcert 192.168.1.42 localhost   # replace with your dev-machine LAN IP
# Move the generated key+cert to a known path, then:
```

Add to `frontend/vite.config.js` under `server`:

```js
import fs from 'node:fs';
// ...
server: {
  port: 5173,
  https: {
    key: fs.readFileSync('192.168.1.42-key.pem'),
    cert: fs.readFileSync('192.168.1.42.pem'),
  },
  proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } },
}
```

Trust the cert on each phone: AirDrop / share to Android, install via Settings → Security.

## 5. Verify on Android (Chrome 100+)

1. Open `https://<your-LAN-IP>:5173/` on the phone.
2. Within the first session, the Vietnamese install banner appears: "Cài đặt ứng dụng vào màn hình chính".
3. Tap **Cài đặt** → confirm Chrome's system dialog → app icon appears on the home screen.
4. Launch from the home screen → standalone window, no Chrome address bar; Vietnamese splash visible briefly.
5. Log in (use any seeded user from 001's quickstart).
6. **US1-AC3**: search a bill by tracking number → tap into detail → tap "Cập nhật trạng thái" → choose "Đã giao" → enter signer name → save → success toast in Vietnamese.
7. **US1-AC5**: rotate the phone to portrait if not already → screens render single-column, no horizontal scroll on a 360-px-wide layout (use Chrome DevTools → Device Toolbar → "Galaxy S5" preset to verify on desktop too).
8. **US1-AC6**: tap "Tạo phiếu mới" → the wizard renders 6 Vietnamese steps. Try to advance from "Người gửi" with empty required fields → step shows red dot in the indicator and inline errors. Fill all sections → "Xác nhận" shows summary → "Lưu & In phiếu".
9. **US1-AC6a**: after save, the PDF preview screen opens with three buttons: **Tải xuống** (downloads `phieu-gui-{id}.pdf`), **Chia sẻ** (opens Android share sheet — try sending to Zalo or Gmail), **In** (opens the Android print picker).
10. **US1-AC7 (connection loss)**: on the phone, enable airplane mode mid-step. Within 5 s the Vietnamese banner "Mất kết nối — vui lòng kiểm tra mạng và thử lại" appears at the top. Type more in the current step — disable airplane mode — banner disappears within 5 s — your typed text is still there → submit succeeds.

## 6. Verify on iOS (Safari 16.4+)

1. Open `https://<your-LAN-IP>:5173/` in mobile Safari.
2. The Vietnamese instruction overlay appears: "Bấm Chia sẻ → Thêm vào Màn hình chính" (with a small share icon illustration).
3. Tap Safari's **Share** → **Add to Home Screen** → confirm the Vietnamese app name "Phiếu Gửi" → app icon (logo) appears on home screen.
4. Launch from the home screen → no Safari chrome; Vietnamese status-bar style.
5. Repeat steps 5–10 from the Android section. On step 9, the **Chia sẻ** button opens the iOS share sheet (AirDrop, Mail, Messages, Zalo if installed); **In** opens AirPrint.

## 7. Auto-update flow

1. With the installed app open on a phone, on your dev machine bump `frontend/package.json`'s `version` (e.g., 0.2.0 → 0.2.1) and rebuild (`npm run build && npm run preview` or just leave dev running — the SW updates on hash change).
2. Refresh the page once on the phone — the Vietnamese affordance "Có phiên bản mới — tải lại để cập nhật" appears at the bottom-right within seconds.
3. If you are mid-wizard (`/bills/new/mobile`), the affordance is suppressed until you leave that route — verify by entering the wizard then triggering the update.
4. Tap **Cập nhật** → page reloads → open Settings/About → version label now reads `Phiên bản: v0.2.1 ({sha})`.

## 8. Run the test suite

```bash
cd frontend
npm test                                      # unit + component tests (Vitest)
npx playwright test --project="Mobile Chrome" # mobile-emulation E2E (Pixel 5)
npx playwright test --project="Mobile Safari" # mobile-emulation E2E (iPhone 14)
```

Coverage targets (per research.md §14):
- Component: `<InstallPrompt>`, `<UpdatePrompt>`, `<ConnectionBanner>`, `<BillCreateMobile>`, `<PdfPreviewScreen>`.
- E2E: install affordance, full wizard happy path, validation badges, connection-loss banner timing, PDF preview action buttons.

## 9. Deploying to staging

The PWA imposes one production constraint not in 001: **the staging URL must be served over HTTPS** (FR's "secure transport" dependency). Once that's in place, no other deploy changes — `npm run build` produces `dist/` containing `sw.js`, `manifest.webmanifest`, and the icon set; serve them statically as before.

## Troubleshooting

- **Install banner never appears on Android**: check that the page is served over HTTPS, the manifest is reachable at `/manifest.webmanifest` (HTTP 200, MIME `application/manifest+json`), and Chrome's `chrome://flags/#bypass-app-banner-engagement-checks` is enabled if you're testing without enough engagement.
- **Service worker doesn't update**: open Chrome DevTools → Application → Service Workers → "Update on reload" + "Bypass for network", then hard reload.
- **iOS shows white screen on launch from home screen**: missing or unreachable `apple-touch-icon-180.png`, or `start_url` is wrong in the manifest.
- **PDF preview shows blank on iOS**: iOS Safari needs `<embed>` or `<object>` for inline PDFs; `<iframe>` works but may need `playsinline` semantics — see `<PdfPreviewScreen>` for the current workaround.
- **`navigator.share({ files: [...] })` rejects**: not all OS versions support file sharing; the fallback "Trình duyệt không hỗ trợ chia sẻ — vui lòng tải xuống" should appear automatically.
