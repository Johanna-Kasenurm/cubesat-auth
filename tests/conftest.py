import sys
import os

from cubesat_auth import config

import pytest
from typer.testing import CliRunner


"""
Creates an isolated test environment for each test.

The app database and session file are stored in a temporary directory
instead of the real ~/.cubesat-auth directory.
"""
@pytest.fixture
def runner(tmp_path, monkeypatch):
    test_app_dir = tmp_path / ".cubesat-auth-test"
    monkeypatch.setenv("CUBESAT_AUTH_APP_DIR", str(test_app_dir))

    # Remove cached application modules so config.py is reloaded
    # after the environment variable is set.
    for module_name in list(sys.modules):
        if module_name.startswith("cubesat_auth"):
            del sys.modules[module_name]

    from cubesat_auth.config import APP_DIR, DB_PATH, SESSION_FILE
    from cubesat_auth.cli import app

    # Safety checks: tests must never use the real home directory app data.
    assert APP_DIR == test_app_dir
    assert str(DB_PATH).startswith(str(test_app_dir))
    assert str(SESSION_FILE).startswith(str(test_app_dir))

    return CliRunner(), app