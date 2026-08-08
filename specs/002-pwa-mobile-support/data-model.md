# Phase 1 — Data Model: PWA Mobile Support

## Summary

This feature introduces **no new database tables, no new domain entities, and no schema migrations**. The 2026-04-26 clarifications removed the two would-have-been-stored entities (`Pending Offline Change`, `Notification Subscription`) and the cache snapshot concept (`Cached Reference Data`). The only remaining "entity" is metadata about the running build itself, which lives as a build-time constant — not a row in PostgreSQL.

The feature reuses every existing entity from `001-logistics-bill-app` as-is: `User` (Nhân viên), `Customer` (Khách hàng), `Bill` (Phiếu gửi) with content lines / fees / signatures, `ServiceTier`, and `AuditEvent`. See `specs/001-logistics-bill-app/data-model.md` for those.

## Entities

### `App Version Record` (build-time constant, not stored)

**Purpose**: Identify which version of the frontend bundle a given installed client is running, so support can verify reports against a specific deploy.

**Where it lives**:

- Source: `package.json` `version` + `git rev-parse --short HEAD` at build time.
- Surfaced in code as the build-time-injected globals `__APP_VERSION__` and `__APP_GIT_SHA__` (Vite `define`).
- Re-exported from `frontend/src/pwa/version.js` for easy import.

**Fields**:

| Field | Type | Source | Example |
|-------|------|--------|---------|
| `version` | string | `package.json` `version` | `"0.2.0"` |
| `gitSha` | string (7 chars) | `git rev-parse --short HEAD` at build | `"a1b2c3d"` |
| `builtAt` | ISO-8601 string | build timestamp | `"2026-04-26T10:00:00Z"` |

**Lifecycle**: regenerated on every build; baked into the JS bundle; visible to the user on the Settings/About screen as `Phiên bản: v{version} ({gitSha})`.

**Rationale**: per `research.md` §9, putting this in the bundle (instead of a `/api/system/version` endpoint) keeps the version label tied to the deployed *frontend* (which is what the user actually sees), avoids a backend round-trip on every settings view, and removes a useless API surface.

**Validation rules**: none — values are produced at build time and trusted.

**Persistence**: none in the DB. Per service-worker precache, the bundle (and therefore this constant) is updated atomically on each new deploy.

---

### Removed entities (kept here for traceability)

The following were in the original spec draft and were removed during the 2026-04-26 clarification session. Listed so a future reviewer doesn't reintroduce them by accident:

| Entity | Why removed | Future re-introduction trigger |
|--------|-------------|-------------------------------|
| `Pending Offline Change` | Offline scope removed — clarification Q1. | Only if offline support is added back as a future feature. |
| `Cached Reference Data` | Same — no offline reads. | Same. |
| `Notification Subscription` | Push notifications deferred — clarification Q3. | Only if/when the notifications feature is built. |

---

## Relationships to existing entities

None. This feature does not relate to any existing table at the data layer. It interacts with existing entities only through the existing HTTP API:

- Read `Bill` via `GET /bills/...` (search, detail).
- Update `Bill` status via `PATCH /bills/{id}/status`.
- Create `Bill` via `POST /bills`.
- Read `Customer` via `GET /customers/...`.
- Read the rendered bill PDF via `GET /bills/{id}/print?format=pdf`.

## Validation rules

No new validation rules. The mobile sectioned create-bill wizard reuses the same Zod schema as the desktop form; per-step validation calls `trigger(stepFieldNames)` rather than introducing new rules.

## State transitions

None new. Bill status transitions are unchanged from `001-logistics-bill-app`.

## Migrations

**None.** No Alembic revision is needed for this feature.
