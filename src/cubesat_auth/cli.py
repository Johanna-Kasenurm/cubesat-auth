"""
This module defines the command line interface (CLI) for the CubeSat
authentication and role-based access control (RBAC) system using Typer.

It provides command groups for:
- System initialisation (init)
- Authentication (login, logout, whoami)
- Account management (create, delete, assign-role, list)
- Satellit opertations (view-data, send-command)

"""

from enum import Enum
from sqlalchemy import select
import typer

from cubesat_auth.services.auth_service import login_user, get_current_user, logout_user
from cubesat_auth.db import SessionLocal, init_db
from cubesat_auth.models import User
from cubesat_auth.security import hash_password


# Crea the main app and sub-apps
app = typer.Typer(help="CubeSat Authentication and Authorisation CLI")
auth_app = typer.Typer(help="Authentication commands")
account_app = typer.Typer(help="Account management commands")
sat_app = typer.Typer(help="Satellite operations commands")

# Add the sub-apps to the main app
app.add_typer(auth_app, name="auth")
app.add_typer(account_app, name="account")
app.add_typer(sat_app, name="sat")


class Role(str, Enum):
    ADMIN = "Admin"
    SUPERUSER = "SuperUser"
    USER = "User"


# Initialise the system and create the initial administrator account
@app.command()
def init(admin_username: str = typer.Option(..., "--admin-username", "-u", help="Username for the initial administrator account.")):
    init_db()

    password = typer.prompt("Admin password", hide_input=True, confirmation_prompt=True)

    with SessionLocal() as db:
        # Check if an administrator account already exists
        existing = db.execute(select(User).where(User.role == Role.ADMIN)).scalar_one_or_none()
        if existing:
            typer.echo("[ERROR] An administrator account already exists.")
            raise typer.Exit(1)

        # Create the administrator account
        user = User(
            username=admin_username,
            password_hash=hash_password(password),
            role=Role.ADMIN
            )
        db.add(user)
        db.commit()

        print(f"[OK] Administrator account created: {admin_username}")




# Authentication commands
# --------------------------------
@auth_app.command("login", help="Login to the system")
def login(username: str = typer.Option(..., "--username", "-u", help="Username to login with.")):
    # Prompt for a password (input hidden)
    password = typer.prompt("Password", hide_input=True, confirmation_prompt=False)

    if not password:
        typer.echo("[ERROR] Password can not be empty.")
        return
    
    try:
        logged_in_user, role = login_user(username, password)
    except ValueError as e:
        typer.echo(f"[ERROR] {e}")
        raise typer.Exit(1)

    typer.echo(f"[AUTHN] Username/password verified")
    typer.echo(f"[SESSION] Logged in as {logged_in_user}")
    typer.echo(f"[AUTHZ] User role: {role}")
    


# Log out the current user
@auth_app.command("logout", help="Logout of the system")
def logout():
    logout_user()
    typer.echo("[SESSION] Logged out")
    

# Show information about the current session
@auth_app.command("whoami", help="Display the current session information")
def whoami():
    try:
        current_user = get_current_user()
    except ValueError as e:
        typer.echo(f"[ERROR] {e}")
        raise typer.Exit(1)
    
    typer.echo(f"[SESSION] Logged in as {current_user.username}")
    typer.echo(f"[AUTHZ] User role: {current_user.role}")
# --------------------------------




# Account management commands
# --------------------------------
@account_app.command("list")
def list():
    print("Listing all accounts")

@account_app.command("create")
def create(username: str = typer.Option(..., "--username", "-u", help="Username for the new account."), 
    role: str = typer.Option("User", "--role", "-r", help="Possible roles are User, SuperUser and Admin. The default role is User.")):
    print(f"Creating account with username: {username} and role: {role}")

@account_app.command("delete")
def delete(username: str = typer.Option(..., "--username", "-u", help="Username of the account to delete.")):
    print(f"Deleting account with username: {username}")


@account_app.command("assign-role", help="Assign a role to an account")
def assign_role(username: str = typer.Option(..., "--username", "-u", help="Username of the account to assign the role to."), 
    role: str = typer.Option(..., "--role", "-r", help="Possible roles are User, SuperUser and Admin.")):
    print(f"Assigning role {role} to account with username: {username}")
# --------------------------------





# Satellite operations commands
# --------------------------------
@sat_app.command("view-data")
def view_data():
    print("Display satellite telemetry data")

@sat_app.command("send-command")
def send_command(command: str = typer.Option(..., "--command", "-c", help="command to send to the satellite.")):
    print(f"Sending command: {command}")
# --------------------------------



if __name__ == "__main__":
    app()
