import typing

from kupala.authentication import login_required
from kupala.contrib.sqlalchemy.dependencies import DbSession
from kupala.responses import redirect_to_path
from kupala.routing import Routes
from starlette.requests import Request
from starlette.responses import Response
from starlette_babel import gettext_lazy as _
from starlette_flash import flash

from {{cookiecutter.project_name}}.config.templating import templates
from {{cookiecutter.project_name}}.organizations.forms import CreateOrganizationForm
from {{cookiecutter.project_name}}.organizations.service import create_organization, get_user_organizations, select_organization

routes = Routes()


@routes.get_or_post("/select", name="organizations.select", guards=[login_required()])
async def select_organization_view(request: Request, session: DbSession) -> Response:
    organizations = await get_user_organizations(session, request.user.id)

    if request.method == "POST":
        form_data = await request.form()
        organization_id: str = typing.cast("str", form_data.get("organization_id", ""))
        ids = {str(organization.id): organization for organization in organizations}
        if organization_id in ids:
            select_organization(request, organization_id)
            flash(request).success(
                _("Successfully logged into {organization}.").format(organization=ids[organization_id])
            )
            return redirect_to_path(request, "manage")

        flash(request).error(_("This organization is not available for your account."))
        return redirect_to_path(request, "organizations.select")

    return templates.TemplateResponse(
        request,
        "organizations/select.html",
        {
            "page_title": _("Select organization"),
            "objects": organizations,
        },
    )


@routes.get_or_post("/new", name="organizations.new", guards=[login_required()])
async def new_organization_view(request: Request, session: DbSession) -> Response:
    form = await CreateOrganizationForm.from_request(
        request,
        data={
            "support_email": request.user.email,
        },
    )
    if await form.validate_on_submit(request):
        organization = await create_organization(
            session,
            owner_id=request.user.id,
            name=form.name.data,
            support_email=form.support_email.data,
            support_phone=form.support_phone.data,
        )
        if form.logo.data and form.logo.data.filename:
            organization.logo = await form.logo.upload(extra_placeholders={"pk": organization.id})

        select_organization(request, organization.id)
        await session.commit()
        return redirect_to_path(request, "manage.dashboard")

    return templates.TemplateResponse(
        request,
        "organizations/new.html",
        {
            "page_title": _("Create organization"),
            "form": form,
        },
    )
