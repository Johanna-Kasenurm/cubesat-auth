def test_admin_can_create_account(runner):
    cli_runner, app = runner

    cli_runner.invoke(app, ["init", "-u", "admin"], input="adminpass\nadminpass\n")
    cli_runner.invoke(app, ["auth", "login", "-u", "admin"], input="adminpass\n")

    result = cli_runner.invoke(
        app,
        ["account", "create", "-u", "alice"],
        input="alicepass\nalicepass\n",
    )

    assert result.exit_code == 0
    assert "Account created: alice" in result.output


def test_account_create_accepts_default_role(runner):
    cli_runner, app = runner

    cli_runner.invoke(app, ["init", "-u", "admin"], input="adminpass\nadminpass\n")
    cli_runner.invoke(app, ["auth", "login", "-u", "admin"], input="adminpass\n")

    result = cli_runner.invoke(
        app,
        ["account", "create", "--username", "testuser"],
        input="password123\npassword123\n"
        )

    assert result.exit_code == 0


def test_non_admin_cannot_create_account(runner):
    cli_runner, app = runner

    cli_runner.invoke(app, ["init", "-u", "admin"], input="adminpass\nadminpass\n")
    cli_runner.invoke(app, ["auth", "login", "-u", "admin"], input="adminpass\n")
    cli_runner.invoke(app, ["account", "create", "-u", "alice"], input="alicepass\nalicepass\n")

    cli_runner.invoke(app, ["auth", "logout"])
    cli_runner.invoke(app, ["auth", "login", "-u", "alice"], input="alicepass\n")

    result = cli_runner.invoke(
        app,
        ["account", "create", "-u", "bob"],
        input="bobpass\nbobpass\n",
    )

    assert result.exit_code != 0
    assert "Only Admin" in result.output


def test_create_account_missing_username_fails(runner):
    cli_runner, app = runner

    cli_runner.invoke(app, ["init", "-u", "admin"], input="adminpass\nadminpass\n")
    cli_runner.invoke(app, ["auth", "login", "-u", "admin"], input="adminpass\n")

    result = cli_runner.invoke(app, ["account", "create"])

    assert result.exit_code != 0
    assert "Missing option" in result.output