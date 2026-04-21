from datetime import datetime, timezone
from sqlalchemy import select

from cubesat_auth.db import SessionLocal
from cubesat_auth.models import User, Session
from cubesat_auth.security import hash_password, verify_password, hash_token, generate_token
from cubesat_auth.sessions import save_local_session, load_local_session, clear_local_session


# Normalise the timezone of a datetime object to UTC for safe comparison
def normalise_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


"""
Authenticates a user using username and password
Creates a DB-backed session
Saves the raw session token to a local file
Hashes the token for storage in the DB
Returns (username, role)
Raises ValueError if authentication fails
"""
def login_user(username: str, password: str) -> tuple[str, str]:
    with SessionLocal() as db:
        # Query the database for the user by username
        query = select(User).where(User.username == username)
        user = db.execute(query).scalar_one_or_none()

        if user is None:
            raise ValueError("Invalid username or password")

        # Verify the password
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid username or password")
        
        # Generate a new session token
        raw_token = generate_token()
        token_hash = hash_token(raw_token)

        # Create a new session in the database
        db_session = Session(
            user_id=user.id,
            token_hash=token_hash,
        )
        db.add(db_session)
        db.commit()

        # Save the raw session token to the local file
        save_local_session(raw_token)
        return user.username, user.role


"""
Retrieves the current user from the database using the session token from the local file
Raises ValueError if the session is invalid or expired
Returns the User object
"""
def get_current_user() -> User:
    # Get the session token from the local file
    local_session = load_local_session()
    if not local_session or "token" not in local_session:
        raise ValueError("No active session. Please login first.")

    token_hash = hash_token(local_session["token"])

    with SessionLocal() as db:
        # Query the database for the session using the token hash
        query = (
            select(Session)
            .where(Session.token_hash == token_hash)
            .where(Session.revoked.is_(False))
        )
        session_obj = db.execute(query).scalar_one_or_none()

        if session_obj is None:
            raise ValueError("Invalid session. Please login again.")
        
        if normalise_utc(session_obj.expires_at) < datetime.now(timezone.utc):
            raise ValueError("Session has expired. Please login again.")

        # Get the user from the session
        user = session_obj.user
        if user is None:
            raise ValueError("Invalid session. Please login again.")

        return user


"""
Revokes the current session in the database
Clears the local session file
"""
def logout_user() -> None:
    # Load the session from the local file
    local_session = load_local_session()
    if not local_session or "token" not in local_session:
        clear_local_session()
        return

    token_hash = hash_token(local_session["token"])

    with SessionLocal() as db:
        # Query the database for the session using the sessiontoken hash
        query = select(Session).where(Session.token_hash == token_hash)
        session_obj = db.execute(query).scalar_one_or_none()

        # Revoke the session if it exists
        if session_obj is not None:
            session_obj.revoked = True
            db.commit()

        # Clear the local session file
        clear_local_session()
