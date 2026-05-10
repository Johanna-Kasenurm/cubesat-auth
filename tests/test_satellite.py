def test_user_can_view_data(runner):
    cli_runner, app = runner

    cli_runner.invoke(app, ["init", "-u", "admin"], input="adminpass\nadminpass\n")
    cli_runner.invoke(app, ["auth", "login", "-u", "admin"], input="adminpass\n")
    cli_runner.invoke(app, ["account", "create", "-u", "alice"], input="alicepass\nalicepass\n")

    cli_runner.invoke(app, ["auth", "logout"])
    cli_runner.invoke(app, ["auth", "login", "-u", "alice"], input="alicepass\n")

    result = cli_runner.invoke(app, ["sat", "view-data"])

    assert result.exit_code == 0
    assert "telemetry" in result.output.lower()


def test_view_data_unauthenticated_fails(runner):
    cli_runner, app = runner

    cli_runner.invoke(app, ["init", "-u", "admin"], input="adminpass\nadminpass\n")

    result = cli_runner.invoke(app, ["sat", "view-data"])

    assert result.exit_code != 0
    assert "No active session" or "[ERROR]" in result.output


def test_send_command_requires_command_argument(runner):
    cli_runner, app = runner

    cli_runner.invoke(app, ["init", "-u", "admin"], input="adminpass\nadminpass\n")
    cli_runner.invoke(app, ["auth", "login", "-u", "admin"], input="adminpass\n")

    result = cli_runner.invoke(app, ["sat", "send-command"])

    assert result.exit_code != 0
    assert "Missing option" in result.output


def test_user_cannot_send_command(runner):
    cli_runner, app = runner

    cli_runner.invoke(app, ["init", "-u", "admin"], input="adminpass\nadminpass\n")
    cli_runner.invoke(app, ["auth", "login", "-u", "admin"], input="adminpass\n")
    cli_runner.invoke(app, ["account", "create", "-u", "alice"], input="alicepass\nalicepass\n")

    cli_runner.invoke(app, ["auth", "logout"])
    cli_runner.invoke(app, ["auth", "login", "-u", "alice"], input="alicepass\n")

    result = cli_runner.invoke(app, ["sat", "send-command", "-c", "deploy_antenna"])

    assert result.exit_code != 0
    assert "permission" in result.output.lower()