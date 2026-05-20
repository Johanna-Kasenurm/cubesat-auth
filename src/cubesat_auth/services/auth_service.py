from datetime import datetime, timezone, timedelta
from sqlalchemy import select

from cubesat_auth.db import SessionLocal
from cubesat_auth.config import TOKEN_EXPIRY_HOURS, TOKEN_EXPIRY_MINUTES, MAX_FAILED_LOGIN_ATTEMPTS, ACCOUNT_LOCK_MINUTES
from cubesat_auth.models import User, Session
from cubesat_auth.security import hash_password, verify_password, hash_token, generate_token
from cubesat_auth.sessions import save_local_session, load_local_session, clear_local_session
from cubesat_auth.audit import write_audit_log
from cubesat_auth.validation import validate_username


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
    username = validate_username(username)

    with SessionLocal() as db:
        # Query the database for the user by username
        query = select(User).where(User.username == username)
        user = db.execute(query).scalar_one_or_none()

        if user is None:
            write_audit_log(
                action="login",
                result="FAILURE",
                username=username,
                details="Invalid username or password"
            )
            raise ValueError("Invalid username or password")

        # Check if the account is locked
        if user.locked_until is not None:
            locked_until = normalise_utc(user.locked_until)
            # The account is still locked
            if locked_until > datetime.now(timezone.utc):
                remaining_seconds = int((locked_until - datetime.now(timezone.utc)).total_seconds())
                write_audit_log(
                    action="login",
                    result="LOCKED",
                    username=username,
                    details=f"Account is locked. Please try again in {remaining_seconds} seconds."
                )
                raise ValueError(f"Account is locked. Please try again in {remaining_seconds} seconds.")
            # Lock has expired, reset the account
            else:
                user.locked_until = None
                user.failed_login_attempts = 0
                db.commit()

        # Verify the password
        if not verify_password(password, user.password_hash):
            user.failed_login_attempts += 1

            # Check if the failed login attempts have reached the maximum
            if user.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
                # Lock the account for the specified time
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=ACCOUNT_LOCK_MINUTES)
                db.commit()

                write_audit_log(
                    action="login",
                    result="LOCKED",
                    username=username,
                    details=f"Account locked after {MAX_FAILED_LOGIN_ATTEMPTS} failed login attempts."
                )

                raise ValueError(f"Too many failed login attempts. Account locked for {ACCOUNT_LOCK_MINUTES} minute(s).")
            db.commit()
            remaining_attempts = MAX_FAILED_LOGIN_ATTEMPTS - user.failed_login_attempts

            write_audit_log(
                action="login",
                result="FAILURE",
                username=username,
                details=f"Invalid username or password. {remaining_attempts} attempt(s) remaining."
            )

            raise ValueError(f"Invalid username or password.")

        # Correct password, reset the failed login attempts and clear any old lockout
        user.failed_login_attempts = 0
        user.locked_until = None

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
        # timedelta(hours=TOKEN_EXPIRY_HOURS)
        save_local_session(user.username, raw_token, datetime.now(timezone.utc), datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY_MINUTES))

        write_audit_log(
            action="login",
            result="SUCCESS",
            username=username,
            details="User logged in successfully."
        )

        return user.username, user.role


"""
Retrieves the current user from the database using the session token from the local file
Raises ValueError if the session is invalid or expired
Returns the User object
"""
def get_current_user() -> tuple[User, Session]:
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
            logout_user()
            raise ValueError("Session has expired. Please login again.")

        # Get the user from the session
        user = session_obj.user
        if user is None:
            raise ValueError("Invalid session. Please login again.")

        return user, session_obj


"""
Revokes the current session in the database
Clears the local session file
"""
def logout_user() -> None:
    # Load the session from the local file
    local_session = load_local_session()

    # If the local session file doesn't exist or there is no session token
    if not local_session or "token" not in local_session:

        write_audit_log(
            action="logout",
            result="FAILURE",
            username=None,
            details="Logout attempted with no active local session."
        )

        clear_local_session()
        return

    token_hash = hash_token(local_session["token"])

    with SessionLocal() as db:
        # Query the database for the session using the sessiontoken hash
        query = select(Session).where(Session.token_hash == token_hash)
        session_obj = db.execute(query).scalar_one_or_none()

        # If the session doesn't exist
        if session_obj is None:
            write_audit_log(
                action="logout",
                result="FAILURE",
                username=None,
                details="Logout attempted with invalid or unknown session token."
            )
            clear_local_session()
            return

        username = session_obj.user.username if session_obj.user else None

        # If the session is already revoked
        if session_obj.revoked:
            write_audit_log(
                action="logout",
                result="FAILURE",
                username=username,
                details="Logout attempted on an already revokded session."
            )
            clear_local_session()
            return

        # Revoke the session
        session_obj.revoked = True
        db.commit()

        write_audit_log(
            action="logout",
            result="SUCCESS",
            username=username,
            details="User logged out successfully."
        )

    # Clear the local session file
    clear_local_session()
