from datetime import datetime, timezone
from sqlalchemy import select

from cubesat_auth.db import Session
from cubesat_auth.models import User, Session
from cubesat_auth.security import hash_password, verify_password, hash_token, generate_token
from cubesat_auth.sessions import save_local_session, load_local_session, clear_local_session


"""
Authenticates a user using username and password
Creates a DB-backed session
Saves the raw session token to a local file
Hashes the token for storage in the DB
Returns (username, role)
Raises ValueError if authentication fails
"""
def login_user(username: str, password: str) -> tuple[str, str]:
    with Session() as db:
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


