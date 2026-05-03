from sqlalchemy import select

from cubesat_auth.db import SessionLocal
from cubesat_auth.models import User
from cubesat_auth.security import hash_password
from cubesat_auth.services.auth_service import get_current_user
from cubesat_auth.audit import write_audit_log

"""
Creates a new user account.
Only Admin users are allowed to create new accounts.
"""
def create_account(username: str, password: str, role: str) -> User:
    # Gets the current user
    current_user, _ = get_current_user()

    # Checks if the current user is an Admin
    if current_user.role != "Admin":
        write_audit_log(
            action="create-user",
            result="FAILURE",
            username=current_user.username,
            details="Failed to create a new account. Insufficient permissions."
        )
        raise ValueError("Only Admin users are allowed to create new accounts")

    with SessionLocal() as db:
        # Checks if the username is already taken
        existing_user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()

        if existing_user:
            write_audit_log(
                action="create-user",
                result="FAILURE",
                username=current_user.username,
                details=f"Failed to create a new account. User {username} already exists."
            )
            raise ValueError(f"User {username} already exists")

        # Create the new user
        new_user = User(
            username=username,
            password_hash=hash_password(password),
            role=role,
        )

        # Add the new user to the database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Write an audit log entry for the successful account creation
        write_audit_log(
            action="create-user",
            result="SUCCESS",
            username=current_user.username,
            details=f"User {username} created successfully."
        )

        return new_user
        
