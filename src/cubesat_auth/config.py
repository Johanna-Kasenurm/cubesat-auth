from pathlib import Path
import os

# Define the application directory and allow test to override it
_app_dir_override = os.environ.get("CUBESAT_AUTH_APP_DIR")

if _app_dir_override:
    APP_DIR = Path(_app_dir_override)
else:
    APP_DIR = Path.home() / ".cubesat-auth"

# Create the application directory if it doesn't exist
APP_DIR.mkdir(parents=True, exist_ok=True)

# Define the file paths
DB_PATH = APP_DIR / "cubesat_auth.db"
SESSION_FILE = APP_DIR / "session.json"
LOG_FILE = APP_DIR / "audit.log"

TOKEN_EXPIRY_HOURS = 1
MAX_FAILED_LOGIN_ATTEMPTS = 3
ACCOUNT_LOCK_MINUTES = 1
