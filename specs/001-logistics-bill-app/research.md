# Phase 0 Research — Logistics Delivery Bill Management

**Date**: 2026-04-26
**Inputs**: [spec.md](./spec.md), user-supplied stack (React, FastAPI, PostgreSQL+SQLAlchemy, JWT)

The user pinned the headline stack. Phase 0 nails down the specific libraries and versions, plus the hard problems that need a deliberate decision: tracking-number generation, diacritic-insensitive search, Vietnamese-faithful print output, JWT lifecycle, and Vietnamese UI.

---

## 1. Backend runtime

**Decision**: Python 3.11 + FastAPI 0.110+, served by Uvicorn (with `--workers` in production).
**Rationale**: User-pinned. FastAPI's Pydantic v2 stack gives strong, declarative validation suitable for the dense bill form. Async support pairs with SQLAlchemy 2.x async for non-blocking PostgreSQL access.
**Alternatives considered**:

- Flask + Marshmallow — older ergonomics, weaker async story.
- Django + DRF — heavier; we only need a thin JSON API, not Django's batteries.

## 2. ORM and migrations

**Decision**: SQLAlchemy 2.x with the new typed `Mapped[...]` style, async engine via `asyncpg`. Alembic for migrations.
**Rationale**: User pinned SQLAlchemy. 2.x async is the current best practice with FastAPI. Alembic is the canonical migration tool and integrates cleanly.
**Alternatives considered**:

- SQLModel — wraps SQLAlchemy + Pydantic; convenient but its async maturity lags behind raw SQLAlchemy 2.x and it adds a layer of abstraction we do not need.
- Tortoise ORM, Piccolo — non-SQLAlchemy, contradicts user direction.

## 3. Database engine

**Decision**: PostgreSQL 16, with extensions `unaccent` and `citext` enabled in the initial Alembic migration.
**Rationale**: User pinned PostgreSQL. `unaccent` is the standard solution for diacritic-insensitive search on Vietnamese text (FR-014, SC-005). `citext` makes phone numbers / customer codes case-insensitive without bespoke logic.
**Alternatives considered**:

- MySQL/MariaDB — accent-folding via collations is less flexible than `unaccent` + functional index; user pinned PostgreSQL anyway.
- SQLite — fine for tests, not for production with 100k+ records.

## 4. Diacritic-insensitive search

**Decision**: Functional GIN trigram index on `unaccent(lower(field))` for searchable text columns (sender_name, receiver_name, sender_address, receiver_address, customer name). Search service applies the same `unaccent(lower(...))` to the input. Uses the `pg_trgm` extension for fuzzy matching.
**Rationale**: PostgreSQL's combination of `unaccent` + `pg_trgm` GIN is the canonical pattern for Vietnamese text and meets the 1-second-on-100k-rows bar (SC-004) without bespoke search infrastructure.
**Alternatives considered**:

- Application-side normalisation only — does not benefit from indexes; will not meet SC-004 at scale.
- Elasticsearch / Meilisearch — overkill for v1 scale; an extra moving part to operate.

## 5. Authentication

**Decision**: JWT access token (15-minute lifetime) + refresh token (7-day lifetime) signed with HS256 by default. `python-jose[cryptography]` for encode/decode; `passlib[bcrypt]` for password hashing. Tokens delivered via JSON response on `/auth/login`; the frontend stores them in memory (access) and `localStorage` (refresh) — see frontend research item 13 for the trade-off.
**Rationale**: User pinned JWT. Short-lived access + longer refresh is the standard pattern that keeps requests stateless while limiting blast radius if a token leaks.
**Alternatives considered**:

- Server-side sessions / cookies — simpler in some respects but contradicts user direction.
- Stateless single long-lived JWT — easier but a leaked token is valid until expiry; rejected.
- RS256 with key pair — more operational complexity; defer until a second service needs to verify tokens.

## 6. Tracking-number generation

**Decision**: Format `<PREFIX><10-digit-zero-padded-sequence>`, e.g. `NL0011310`. The numeric part comes from a dedicated PostgreSQL `SEQUENCE` (`bill_tracking_seq`); the prefix is a per-carrier constant from configuration.
**Rationale**: PostgreSQL sequences are atomically unique under any concurrency level (satisfies FR-002 and the 0-collision stress test in SC-006). A sequence is dramatically simpler and faster than UUIDs while still producing the human-readable, scannable code expected on the printed bill.
**Alternatives considered**:

- `uuid4` — guaranteed unique but unfriendly on a paper barcode and inconsistent with the reference bill.
- Application-generated `MAX(id)+1` — race-prone; rejected.
- Snowflake-style ID — overkill for single-tenant, single-DB v1.

## 7. Printed bill rendering

**Decision**: A single canonical HTML+CSS template at `backend/app/static/bill_template.html`. Server-side rendering via `WeasyPrint` produces a PDF (for download, archive, reprint). The frontend renders the same template inline for on-screen preview and uses the browser's native print + `print.css` (via `react-to-print`) for direct counter printing.
**Rationale**: One template, two consumers — guarantees the print-out and the on-screen preview cannot drift apart, defending SC-003 (9/10 layout-fidelity rating). HTML/CSS gives precise control over the multi-section grid in the reference bill (sender/receiver/contents/fees/signatures) and preserves Vietnamese diacritics through Unicode fonts. WeasyPrint supports custom fonts (e.g., a Vietnamese-friendly font like Roboto or Be Vietnam Pro).
**Alternatives considered**:

- ReportLab — programmatic PDF; harder to keep visually faithful to the reference layout.
- Browser-only printing — would mean no archived PDF and no consistent reprint from the server.
- LaTeX — overkill, slow build, deployment friction.

## 8. Barcode and QR code

**Decision**: Server generates the barcode (Code128 of the tracking number) and the QR code (encoding the tracking URL like `https://<carrier>/tra-cuu/<tracking>`) inline in the print template using:

- `python-barcode` (Code128, SVG output embedded in the HTML template).
- `qrcode` library for QR PNG/SVG.

The frontend uses `jsbarcode` and `qrcode.react` for the on-screen preview so it is rendered without a server round-trip.
**Rationale**: Code128 is the industry-standard 1D barcode for shipping. Generating both formats inline keeps the template self-contained.
**Alternatives considered**:

- External barcode SaaS — unnecessary dependency.
- QR-only — rejected because the reference bill prints both.

## 9. Frontend stack

**Decision**:

- **Framework**: React 18 + Vite 5, JavaScript (per user "react js"; not TypeScript). Strict ESLint config to compensate for absence of types.
- **Routing**: React Router v6.
- **Server state**: React Query (TanStack Query v5) for fetch / cache / mutate.
- **Forms**: React Hook Form + Zod for declarative validation matching backend Pydantic constraints.
- **UI kit**: Ant Design v5 — chosen because it ships first-class Vietnamese locale (`vi_VN`) for built-in widgets (date picker, number, table, message), supports comma-decimal localisation, and its dense form layout matches the multi-section bill UI. Theme tokens tuned to the brand red+black from the supplied logo.
- **Date/number**: `dayjs` + `dayjs/locale/vi`; Ant Design's `ConfigProvider` with `vi_VN` for the rest.

**Rationale**: All choices serve FR-021 (Vietnamese-only UI) directly; Ant Design is the lowest-risk path to a counter-staff-grade Vietnamese admin UI. Vite gives fast dev cycles.
**Alternatives considered**:

- TypeScript — rejected because user said "react js"; revisit later.
- Material UI / Chakra — Vietnamese localisation requires more manual wiring than Ant Design.
- Redux Toolkit — unnecessary; React Query covers server state, React Context covers the small auth state.
- Formik — slower and more verbose than React Hook Form for a form this large.

## 10. Vietnamese UI string catalogue

**Decision**: All visible strings live in a single module `frontend/src/i18n/vi.js` exported as a tree (`{ bills: { create: { sender: 'Người gửi', ... } } }`). A tiny `t(key)` helper looks them up. No runtime locale switching for v1; the file just enforces "no English string is rendered to the user".
**Rationale**: Lightweight, zero-dep, and gives reviewers a single file to audit for the SC-002 acceptance criterion (zero foreign-language strings). Sets up cleanly for `react-i18next` later if a second locale is added.
**Alternatives considered**:

- `react-i18next` from day one — fine but extra ceremony for a single-locale v1.
- Inline strings — fails the audit criterion in spec.

## 11. Vietnamese number format

**Decision**: Use `Intl.NumberFormat('vi-VN', ...)` for display. For input, use Ant Design `InputNumber` with `decimalSeparator=","` so users type `200,00` naturally. Backend stores numbers as `Numeric(12,3)` (weight) / `Numeric(14,2)` (money) and accepts either decimal style on the wire (frontend always normalises to dot before sending JSON).
**Rationale**: Display matches user expectation (FR-023, SC-002); transport stays standards-compliant.
**Alternatives considered**:

- Sending comma decimals over JSON — non-standard, breaks tooling. Rejected.

## 12. Vietnamese date format on print

**Decision**: Print template renders dates as `…ngày <DD> tháng <MM> năm <YYYY>` using a Jinja-like helper. On screen, dates use Ant Design's `DatePicker` with `vi_VN` locale.
**Rationale**: Matches reference bill verbatim (FR-024).

## 13. JWT token storage on the client

**Decision**: Access token kept in JavaScript memory (React state); refresh token kept in `localStorage`. Axios request interceptor adds `Authorization: Bearer <access>` and a response interceptor refreshes the access token on `401`.
**Rationale**: A real httpOnly cookie would be better for refresh tokens, but the FastAPI backend and the React frontend may be served from different origins in dev (Vite on 5173, FastAPI on 8000), and CORS+cookie config is fiddly. `localStorage` is acceptable for an internal counter-staff app on hardened machines, and avoids the production gotchas we'd otherwise hit. Tokens are short-lived to limit blast radius.
**Alternatives considered**:

- httpOnly cookie + same-site lax + CSRF token — strictly safer; acceptable as a v1.1 hardening.
- Tokens in `sessionStorage` — same XSS exposure as `localStorage` but lost on tab close, which counter staff would find annoying.

## 14. Backend testing strategy

**Decision**: `pytest` + `pytest-asyncio`; integration tests against an ephemeral PostgreSQL via `testcontainers-python` (preferred over `pytest-postgresql` because it tests the actual `unaccent` extension we depend on). Contract tests assert generated OpenAPI matches `specs/001-logistics-bill-app/contracts/openapi.yaml`.
**Rationale**: Real-DB tests catch the hard-to-fake bits (functional indexes, sequence atomicity, unaccent behaviour). Contract tests prevent silent API drift.
**Alternatives considered**:

- SQLite in tests — diacritic-insensitive search would not behave the same; rejected.

## 15. Frontend testing strategy

**Decision**: `vitest` + `@testing-library/react` for component tests; `msw` to mock the API; Playwright for one end-to-end smoke (login → create bill → preview print → status update). No exhaustive E2E suite for v1.
**Rationale**: Component tests catch the form-validation logic where most bugs hide; the single Playwright run protects the print-preview path that is hard to exercise in unit tests.

## 16. Deployment shape

**Decision**: Docker Compose for dev (`postgres`, `backend`, `frontend`). Production left intentionally open (the user has not specified an environment); the Compose file is structured so each service becomes a deployable container without changes. Document this clearly in `quickstart.md`.
**Rationale**: Lowest-friction onboarding; defers production-infra decisions until the user provides them.

## 17. Observability

**Decision**: Structured JSON logs (Python `structlog`) with request-ID middleware. No metrics/tracing stack in v1.
**Rationale**: Adequate for a single-tenant counter-staff system; can layer OpenTelemetry on later without redesign.

## 18. Locale of error messages

**Decision**: Error messages returned by the backend in Vietnamese, keyed via a small catalogue (`backend/app/core/i18n.py`). Pydantic validation errors are caught and re-rendered in Vietnamese before being returned (custom exception handler).
**Rationale**: FR-008 mandates Vietnamese errors and FR-021 forbids English from reaching the UI. Translating at the boundary keeps backend code readable in English while the user sees Vietnamese.

---

## NEEDS CLARIFICATION resolution

The Technical Context introduced no `NEEDS CLARIFICATION` markers — every entry was either pinned by the user or filled with a defensible decision above. Phase 0 is complete.
