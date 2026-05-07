from enum import Enum

class Role(str, Enum):
    ADMIN = "Admin"
    SUPERUSER = "SuperUser"
    USER = "User"

    @classmethod
    def list(cls):
        return [role.value for role in cls]