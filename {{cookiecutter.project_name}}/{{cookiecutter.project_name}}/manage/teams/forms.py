import sqlalchemy as sa
import wtforms
from kupala.contrib.forms import AsyncForm
from kupala.contrib.sqlalchemy.query import query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_babel import gettext_lazy as _

from {{cookiecutter.project_name}}.models.organizations import Member, MemberInvitation, Organization
from {{cookiecutter.project_name}}.models.users import User


async def validate_not_invited(form: AsyncForm, field: wtforms.Field) -> None:
    organization: Organization = form.context["organization"]
    session: AsyncSession = form.context["dbsession"]
    stmt = sa.select(MemberInvitation).where(
        MemberInvitation.organization_id == organization.id,
        sa.func.lower(MemberInvitation.email) == field.data.lower(),
    )
    if await query(session).exists(stmt):
        raise wtforms.ValidationError(_("This user has been already invited."))


async def validate_not_member(form: AsyncForm, field: wtforms.Field) -> None:
    organization: Organization = form.context["organization"]
    session: AsyncSession = form.context["dbsession"]
    stmt = (
        sa.select(Member)
        .join(Member.user)
        .where(
            Member.organization_id == organization.id,
            sa.func.lower(User.email) == field.data.lower(),
        )
    )
    if await query(session).exists(stmt):
        raise wtforms.ValidationError(_("This user is already a member of this organization."))


class InviteMemberForm(AsyncForm):
    email = wtforms.EmailField(
        _("Email"), validators=[validate_not_invited, validate_not_member, wtforms.validators.data_required()]
    )
    message = wtforms.TextAreaField(_("Message"), default="")
