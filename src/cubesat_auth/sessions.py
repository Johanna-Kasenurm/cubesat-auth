import json
from typing import Any

from cubesat_auth.config import SESSION_FILE


# Save the raw session token to a local file
def save_local_session(token:str) -> None:
    SESSION_FILE.write_text(json.dumps({"token": token}, indent=2), encoding="utf-8")


# Load the local session file if it exists
def load_local_session() -> dict[str, Any] | None:
    if not SESSION_FILE.exists():
        return None

    try:
        return json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


# Delete the local session file if it exists
def clear_local_session() -> None:
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()