from datetime import datetime
from app.models.audit_logs import AuditLog

def log_audit_event(db, user_id, action, entity_type, entity_id, details=None, commit=True):
    """Log audit event with safe handling.
    
    Policy:
    - Never log secrets (password/token filtering).
    - If commit=True (default), commits independently (current behavior for standalone calls).
    - Callers that manage transactions (evaluations route) should pass commit=False
      so audit participates in same DB transaction and rolls back on failure.
    - A failed audit must not suppress original error or claim success.
    """
    if action in ("signin", "security", "login") or (details and ("password" in str(details).lower() or "token" in str(details).lower())):
        return None  # never log passwords/tokens
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
    )
    db.add(entry)
    if commit:
        try:
            db.commit()
        except Exception:
            # Audit commit failure must not hide operation failure; do not claim success
            db.rollback()
            # Log to stderr / external log if available; never suppress caller error
            raise
    return entry
