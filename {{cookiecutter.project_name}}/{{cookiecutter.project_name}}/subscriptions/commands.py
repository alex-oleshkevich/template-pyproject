from kupala.console import Group

from {{cookiecutter.project_name}}.config.database import get_async_session
from {{cookiecutter.project_name}}.subscriptions.models import Plan, PlanDoesNotExists

group = Group("subscriptions")


@group.command("create-free-plan")
async def create_free_plan() -> None:
    async with get_async_session() as session:
        async with session.begin():
            try:
                await Plan.get_free_plan(session)
            except PlanDoesNotExists:
                await Plan.create_free_plan(session)
