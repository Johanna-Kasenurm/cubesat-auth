import json
from typing import Any
from datetime import datetime

from cubesat_auth.config import SESSION_FILE


# Save the raw session token to a local file
def save_local_session(username:str, token:str, created_at:datetime, expires_at:datetime) -> None:
    SESSION_FILE.write_text(json.dumps({"username": username, "token": token, "created_at": created_at.isoformat(), "expires_at": expires_at.isoformat()}, indent=2), encoding="utf-8")


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