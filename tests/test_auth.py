def test_whoami_unauthenticated_fails(runner):
    cli_runner, app = runner
    result = cli_runner.invoke(app, ["auth", "whoami"])

    assert result.exit_code != 0
    assert "No active session" in result.output or "[ERROR]" in result.output



def test_init_and_login_success(runner):
    cli_runner, app = runner

    # Assert the init command creates an admin account
    result = cli_runner.invoke(
        app,
        ["init", "-u", "admin"],
        input="adminpass\nadminpass\n",
    )
    assert result.exit_code == 0, result.output
    assert "Administrator account created" in result.output

    # It is possible to log in as an administrator
    result = cli_runner.invoke(
        app,
        ["auth", "login", "-u", "admin"],
        input="adminpass\n",
    )
    assert result.exit_code == 0, result.output
    assert "Logged in as: admin" in result.output

    # The whoami command works
    result = cli_runner.invoke(app, ["auth", "whoami"])
    assert result.exit_code == 0
    assert "admin" in result.output
    assert "Admin" in result.output



def test_login_missing_username_fails(runner):
    cli_runner, app = runner
    result = cli_runner.invoke(app, ["auth", "login"])

    assert result.exit_code != 0
