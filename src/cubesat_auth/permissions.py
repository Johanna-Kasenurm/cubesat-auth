from enum import Enum

from cubesat_auth.roles import Role


# Define the permissions
class Permission(str, Enum):
    CREATE_ACCOUNT = "create-account"
    DELETE_ACCOUNT = "delete-account"
    ASSIGN_ROLE = "assign-role"
    LIST_ACCOUNTS = "list-accounts"

    VIEW_DATA = "view-data"
    SEND_COMMAND = "send-command"

    VIEW_AUDIT_LOGS = "view-audit-logs"


# Map the roles to the permissions
ROLE_PERMISSIONS = {
    Role.ADMIN: {
        Permission.CREATE_ACCOUNT,
        Permission.DELETE_ACCOUNT,
        Permission.ASSIGN_ROLE,
        Permission.LIST_ACCOUNTS,
        Permission.VIEW_DATA,
        Permission.SEND_COMMAND,
        Permission.VIEW_AUDIT_LOGS,
    },
    Role.SUPERUSER: {
        Permission.VIEW_DATA,
        Permission.SEND_COMMAND,
    },
    Role.USER: {
        Permission.VIEW_DATA,
    }
}


# Checks if a role has a specific permission
def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())