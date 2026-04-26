<!-- SPECKIT START -->
Active feature: **002-pwa-mobile-support** — Hỗ trợ Điện thoại qua PWA (mobile-phone usability for the logistics bill app via Progressive Web App).

For the technical context, project structure, dependencies, and build/test commands, read the current plan: `specs/002-pwa-mobile-support/plan.md`.
Companion artifacts:

- Spec: `specs/002-pwa-mobile-support/spec.md` (with 5-question Clarifications session, 2026-04-26)
- Phase 0 research: `specs/002-pwa-mobile-support/research.md`
- Phase 1 data model: `specs/002-pwa-mobile-support/data-model.md`
- Phase 1 contracts (manifest + reused endpoints): `specs/002-pwa-mobile-support/contracts/pwa-additions.md`
- Phase 1 quickstart: `specs/002-pwa-mobile-support/quickstart.md`

Underlying feature `001-logistics-bill-app` (Vietnamese delivery-bill app) is the substrate — its plan, data model, and OpenAPI contract are referenced from the 002 plan. Stack pinned by user: React (JS) frontend, Python FastAPI backend, PostgreSQL + SQLAlchemy with Alembic migrations, JWT auth. UI/UX strictly Vietnamese.

Scope decisions made during 002 clarification (do not silently expand without consulting the user):
- **Online-only** in v1 — no offline cache, no sync queue, no background sync.
- **Mobile covers all desktop workflows**, including the full sectioned "Phiếu Gửi" creation wizard.
- **Push notifications deferred** to a later feature.
- **Mobile print = PDF preview → OS share / OS print** (reuses existing `GET /bills/{id}/print?format=pdf`).
- **Camera barcode scanning deferred** to a later feature.
<!-- SPECKIT END -->
