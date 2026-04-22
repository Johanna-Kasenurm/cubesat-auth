from cubesat_auth.db import SessionLocal
from cubesat_auth.models import AuditLog


"""
Write an audit log entry to the database.

Args:
action: the action attempted (e.g. login, logout)
result: the outcome (e.g. SUCCESS, FAILURE, LOCKOUT)
username: the username involved if known
details: extra context about the event
"""
def write_audit_log(
    action: str, 
    result: str, 
    username: str | None = None, 
    details: str | None = None,
    ) -> None:
    with SessionLocal() as db:
        entry = AuditLog(
            username=username,
            action=action,
            result=result,
            details=details,
        )
        db.add(entry)
        db.commit()