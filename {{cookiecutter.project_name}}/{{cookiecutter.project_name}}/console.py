import sys

from kupala.console import create_console_app
from kupala.contrib.mail.commands import mail_commands

from {{cookiecutter.project_name}}.accounts.commands import group as auth_commands
from {{cookiecutter.project_name}}.commands.settings import settings_commands
from {{cookiecutter.project_name}}.main import app
from {{cookiecutter.project_name}}.subscriptions.commands import group as subscription_commands

cli = create_console_app(app)

cli.add_command(auth_commands)
cli.add_command(mail_commands)
cli.add_command(settings_commands)
cli.add_command(subscription_commands)


def run_console_app() -> None:
    sys.exit(cli())
