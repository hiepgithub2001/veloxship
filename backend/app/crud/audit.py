"""Audit event helper."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_event import AuditEvent


async def log_event(
    db: AsyncSession,
    *,
    actor_id: int | None,
    action: str,
    entity_type: str | None = None,
    entity_id: int | None = None,
    details: dict | None = None,
) -> AuditEvent:
    """Insert an audit event row."""
    event = AuditEvent(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(event)
    await db.flush()
    return event
