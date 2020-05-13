import pytest
from click.testing import CliRunner
from kultur.cli import main


def test_application(database_full):
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0


def test_application_today(database_full):
    runner = CliRunner()
    result = runner.invoke(main, "-t")
    assert result.exit_code == 0


@pytest.mark.online
def test_application_new(database_light):
    runner = CliRunner()
    result = runner.invoke(main, "-n")
    assert result.exit_code == 0
