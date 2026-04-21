from pathlib import Path

# Define the application directory
APP_DIR = Path.home() / ".cubesat-auth"
# Create the application directory if it doesn't exist
APP_DIR.mkdir(parents=True, exist_ok=True)

# Define the file paths
DB_PATH = APP_DIR / "cubesat_auth.db"
SESSION_FILE = APP_DIR / "session.json"
LOG_FILE = APP_DIR / "audit.log"

TOKEN_EXPIRY_HOURS = 1
