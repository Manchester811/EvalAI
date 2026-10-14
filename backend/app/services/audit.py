from datetime import datetime
from app.models.audit_logs import AuditLog
def log_audit_event(db, user_id, action, entity_type, entity_id, details=None):
    if action in ('signin', 'security', 'login') or 'password' in str(details).lower() or 'token' in str(details).lower():
        return None  # never log passwords/tokens
    entry = AuditLog(user_id=user_id, action=action, entity_type=entity_type, entity_id=entity_id)
    db.add(entry)
    db.commit()
    return entry
