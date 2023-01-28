import sys

import click
from kupala.console import Group, printer
from kupala.contrib.sqlalchemy import DbSession
from starlette_babel import gettext_lazy as _

from {{cookiecutter.project_name}}.accounts.passwords import generate_password_hash
from {{cookiecutter.project_name}}.models.users import User

group = Group("accounts")


@group.command("create-user")
async def create_user(dbsession: DbSession) -> None:
    printer.header(_("Create user"))

    email = click.prompt(_("Email"))
    password = click.prompt(_("Password"), hide_input=True, confirmation_prompt=True)

    async with dbsession.begin():
        user = await User.create_user(dbsession, email=email, plain_password=password)

    printer.success(_("User created. ID = {user_id}."), user_id=click.style(user.id, fg="yellow"))


@group.command("set-password")
@click.argument("email")
async def set_user_password(dbsession: DbSession, email: str) -> None:
    printer.header(_("Change password of {email}."), email=click.style(email, fg="yellow"))
    user = await User.get_by_email(dbsession, email)
    if not user:
        raise click.ClickException(_("User does not exists."))

    printer.text(_("Set new password for {user}"), user=click.style(str(user), fg="yellow"))
    password_confirmation = click.prompt(_("Enter new password"), hide_input=True, confirmation_prompt=True)
    user.set_password(password_confirmation)
    await dbsession.commit()
    printer.success(_("Password has been changed."))


@group.command("check-password")
@click.argument("email")
async def check_user_password(dbsession: DbSession, email: str) -> None:
    user = await User.get_by_email(dbsession, email)
    if not user:
        raise click.ClickException(_("User does not exists."))

    printer.header(_("Test password of {user}").format(user=click.style(user, fg="yellow")))
    password = click.prompt(_("Enter password"), hide_input=True)
    if user.check_password(password):
        printer.success(_("Passwords did match."))
    else:
        printer.error(_("Passwords did not match."))


@group.command("hash-password")
@click.argument("password", default="")
@click.option("--show-input", default=False, is_flag=True)
def hash_password(password: str, show_input: bool) -> None:
    match password:
        case "-":
            password = sys.stdin.read()
        case "":
            password = click.prompt(_("Enter plain password"), hide_input=show_input is False)

    printer.text(generate_password_hash(password))
