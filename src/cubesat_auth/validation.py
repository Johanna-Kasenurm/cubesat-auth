import re

# 3-30 characters: letters, numbers, '.', '_' or '-'
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")
# 1-64 characters: letters, numbers, '_' or '-'
SAT_COMMAND_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


# Check that the username matches the defined pattern
def validate_username(username: str) -> str:
    if not username:
        raise ValueError("Username cannot be empty.")

    if not USERNAME_PATTERN.fullmatch(username):
        raise ValueError(
            "Invalid username"
        )

    return username


# Check that the satellite command matches the defined pattern
def validate_sat_command(command: str) -> str:
    if not command:
        raise ValueError("Command cannot be empty.")

    if not SAT_COMMAND_PATTERN.fullmatch(command):
        raise ValueError(
            "Invalid command. Use 1-64 characters: letters, numbers, '_' or '-'"
        )

    return command