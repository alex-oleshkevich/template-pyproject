from kupala.console import Group
from kupala.contrib.sqlalchemy import DbSession
from {{cookiecutter.project_name}}.subscriptions.models import Plan, PlanDoesNotExists

group = Group("subscriptions")


@group.command("create-free-plan")
async def create_free_plan(dbsession: DbSession) -> None:
    async with dbsession.begin():
        try:
            await Plan.get_free_plan(dbsession)
        except PlanDoesNotExists:
            await Plan.create_free_plan(dbsession)
