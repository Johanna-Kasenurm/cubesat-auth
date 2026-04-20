"""
This module defines the command line interface (CLI) for the CubeSat
authentication and role-based access control (RBAC) system using Typer.

It provides command groups for:
- System initialisation (init)
- Authentication (login, logout, whoami)
- Account management (create, delete, assign-role, list)
- Satellit opertations (view-data, send-command)

"""

import typer

# Crea the main app and sub-apps
app = typer.Typer(help="CubeSat Authentication and Authorisation CLI")
auth_app = typer.Typer(help="Authentication commands")
account_app = typer.Typer(help="Account management commands")
sat_app = typer.Typer(help="Satellite operations commands")

# Add the sub-apps to the main app
app.add_typer(auth_app, name="auth")
app.add_typer(account_app, name="account")
app.add_typer(sat_app, name="sat")


@app.command()
def init(admin_username: str = typer.Option(..., "--admin-username", "-u", help="Username for the initial administrator account.")):
    print(f"Initialising with admin username: {admin_username}")

# Authentication commands
# --------------------------------
@auth_app.command("login")
def login(username: str = typer.Option(..., "--username", "-u", help="Username to login with.")):
    print(f"Logging in with username: {username}")

@auth_app.command("logout")
def logout():
    print("Logging out")

@auth_app.command("whoami")
def whoami():
    print("Current session information")
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

@account_app.command("assign-role")
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
