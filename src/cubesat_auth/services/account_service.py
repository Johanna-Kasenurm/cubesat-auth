from sqlalchemy import select

from cubesat_auth.db import SessionLocal
from cubesat_auth.models import User
from cubesat_auth.security import hash_password
from cubesat_auth.services.auth_service import get_current_user
from cubesat_auth.audit import write_audit_log
from cubesat_auth.roles import Role

"""
Creates a new user account.

Args:
    username: The username for the new account.
    password: The password for the new account.
    role: The role of the new account.

Returns the newly created User object.
Only Admin users are allowed to create new accounts.
"""
def create_account(username: str, password: str, role: str) -> User:
    # Gets the current user
    current_user, _ = get_current_user()

    # Checks if the current user is an Admin
    if current_user.role != Role.ADMIN.value:
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
        


"""
Deletes a user account.

Args:
    username: The username of the account to delete.

Only Admin users are allowed to delete accounts.
"""
def delete_account(username: str) -> None:
    current_user, _ = get_current_user()

    # Checks if the current user is an Admin
    if current_user.role != Role.ADMIN.value:
        write_audit_log(
            action="delete-user",
            result="FAILURE",
            username=current_user.username,
            details=f"Failed to delete a user account {username}. Insufficient permissions."
        )
        raise ValueError("Only Admin users are allowed to delete accounts")

    # Prevents deleting yourself
    if current_user.username == username:
        write_audit_log(
            action="delete-user",
            result="FAILURE",
            username=current_user.username,
            details=f"Failed to delete a user account {username}. You cannot delete yourself."
        )
        raise ValueError("You cannot delete your own account.")

    with SessionLocal() as db:
        # Gets the user from the database
        user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()

        # Checks if the user exists
        if user is None:
            write_audit_log(
                action="delete-user",
                result="FAILURE",
                username=current_user.username,
                details=f"Failed to delete a user account {username}. User not found."
            )
            raise ValueError(f"User {username} not found.")

        # Deletes the user from the database
        db.delete(user)
        db.commit()

        write_audit_log(
            action="delete-user",
            result="SUCCESS",
            username=current_user.username,
            details=f"User {username} deleted successfully."
        )
    

"""
Lists all user accounts.
Returns a list of User objects.
Only Admin users are allowed to list accounts.
"""
def list_accounts() -> list[User]:
    current_user, _ = get_current_user()

    # Checks if the current user is an Admin
    if current_user.role != Role.ADMIN.value:
        write_audit_log(
            action="list-users",
            result="FAILURE",
            username=current_user.username,
            details="Failed to list user accounts. Insufficient permissions."
        )
        raise ValueError("Only Admin users are allowed to list accounts.")

    with SessionLocal() as db:
        # Gets all users from the database
        users = db.execute(select(User).order_by(User.username)).scalars().all()

        write_audit_log(
            action="list-users",
            result="SUCCESS",
            username=current_user.username,
            details="User accounts listed successfully."
        )

        return list(users)


"""
Assigns a role to a user account.
Only Admin users are allowed to assign roles.
"""