from cubesat_auth.models import User
from cubesat_auth.services.auth_service import get_current_user
from cubesat_auth.audit import write_audit_log
from cubesat_auth.roles import Role
from cubesat_auth.permissions import Permission, has_permission


"""
Simulate receiving telemetry data from the satellite.
"""
def view_satellite_data() -> dict[str, str]:
    current_user, _ = get_current_user()

    # Checks if the current user has the permission to view telemetry data
    if not has_permission(Role(current_user.role), Permission.VIEW_DATA):
        write_audit_log(
            action="view-data",
            result="FAILURE",
            username=current_user.username,
            details="Failed to view telemetry data. Insufficient permissions."
        )
        raise ValueError("Insufficient permissions to view telemetry data.")

    # Simulates receiving telemetry data from the satellite
    telemetry = {
        "battery": "92%",
        "mode": "SAFE",
        "temperature": "18.4 C",
        "signal": "Nominal",
        "last_contact": "Simulated ground-station contact",
    }

    write_audit_log(
        action="view-data",
        result="SUCCESS",
        username=current_user.username,
        details="Telemetry data viewed successfully."
    )

    return telemetry


