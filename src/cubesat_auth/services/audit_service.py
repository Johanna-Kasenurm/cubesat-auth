from sqlalchemy import select

from cubesat_auth.db import SessionLocal
from cubesat_auth.models import User, AuditLog
from cubesat_auth.services.auth_service import get_current_user
from cubesat_auth.audit import write_audit_log
from cubesat_auth.roles import Role
from cubesat_auth.permissions import Permission, has_permission

"""
Gets all audit logs.

Args:
    limit: the maximum number of audit logs to return.

Returns a list of AuditLog objects ordered by timestamp in descending order.
Only Admin users are allowed to view audit logs.
"""
def get_audit_logs(limit: int) -> list[AuditLog]:
    current_user, _ = get_current_user()

    # Checks if the current user has the permission to view audit logs
    if not has_permission(Role(current_user.role), Permission.VIEW_AUDIT_LOGS):
        write_audit_log(
            action="view-audit-logs",
            result="FAILURE",
            username=current_user.username,
            details="Failed to view audit logs. Insufficient permissiosn."
        )
        raise ValueError("Only Admin users are allowed to view audit logs.")

    # Gets the audit logs from the database
    with SessionLocal() as db:
         # Query the logs from the database
        query = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
        logs = db.execute(query).scalars().all()

        write_audit_log(
            action="view-audit-logs",
            result="SUCCESS",
            username=current_user.username,
            details="Audit logs viewed successfully."
        )
        
        return list(logs)
