from __future__ import annotations

import datetime
import decimal

import sqlalchemy as sa
from kupala.choices import TextChoices
from kupala.contrib.sqlalchemy.modelmixins import Timestamps
from kupala.contrib.sqlalchemy.query import query
from kupala.contrib.sqlalchemy.types import AutoCreatedAt, IntPk, LongString, ShortString
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from starlette_babel import gettext_lazy as _
from starlette_babel import timezone

from {{cookiecutter.project_name}}.config.database import Base, UserFk
from {{cookiecutter.project_name}}.models.users import User
from {{cookiecutter.project_name}}.subscriptions.packages import FREE_PACKAGE


class PlanDoesNotExists(ValueError):
    ...


class Plan(Base, Timestamps):
    __tablename__ = "subscriptions_plans"
    __table_args__ = (sa.Index("subscription_plan_package_uidx", "package", unique=True),)
    id: Mapped[IntPk]
    name: Mapped[LongString]
    description: Mapped[str] = mapped_column(sa.Text, default="", server_default="")
    package: Mapped[ShortString]

    @classmethod
    async def get_free_plan(cls, session: AsyncSession) -> Plan:
        return await query(session).one_or_raise(
            sa.select(Plan).filter_by(package=FREE_PACKAGE.name),
            PlanDoesNotExists(),
        )

    @classmethod
    async def create_free_plan(cls, session: AsyncSession) -> Plan:
        plan = Plan(package=FREE_PACKAGE.name, name=str(_("Free")))
        session.add(plan)
        await session.flush()
        return plan


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (sa.Index("subscription_uidx", "user_id", "plan_id", unique=True),)

    class Status(TextChoices):
        ACTIVE = "active"
        TRIALING = "trialing"
        PAST_DUE = "past_due"
        PAUSED = "paused"
        DELETED = "deleted"

    id: Mapped[IntPk]
    plan_id: Mapped[int] = mapped_column(sa.ForeignKey("subscriptions_plans.id"))
    user_id: Mapped[UserFk]
    status: Mapped[ShortString]
    subscribed_at: Mapped[AutoCreatedAt]
    subscribed_until: Mapped[datetime.datetime | None] = mapped_column(sa.DateTime(True))

    @classmethod
    async def subscribe(
        cls, session: AsyncSession, user: User, plan: Plan, status: Status, duration_days: int | None = None
    ) -> Subscription:
        subscribed_until: datetime.datetime | None = None
        if duration_days:
            subscribed_until = timezone.now() + datetime.timedelta(days=duration_days)
        subscription = cls(plan_id=plan.id, user_id=user.id, subscribed_until=subscribed_until, status=status)
        session.add(subscription)
        await session.flush([subscription])
        return subscription


class Invoice(Base):
    __tablename__ = "subscriptions_invoices"

    class Status(TextChoices):
        UNPAID = "unpaid"
        PAID = "paid"

    id: Mapped[IntPk]
    number: Mapped[ShortString]
    status: Mapped[ShortString]
    created_at: Mapped[AutoCreatedAt]
    user_id: Mapped[UserFk]
    subscription_id: Mapped[int] = mapped_column(sa.ForeignKey("subscriptions.id"))
    amount: Mapped[decimal.Decimal] = mapped_column(sa.Numeric, default=0, server_default="0")
    tax: Mapped[decimal.Decimal] = mapped_column(sa.Numeric, default=0, server_default="0")
    tax_rate: Mapped[int] = mapped_column(sa.Integer, default=0, server_default="0")


class Payment(Base):
    __tablename__ = "subscriptions_payments"

    class Status(TextChoices):
        UNPAID = "unpaid"

    id: Mapped[IntPk]
    user_id: Mapped[UserFk]
    status: Mapped[ShortString]
    total: Mapped[decimal.Decimal] = mapped_column(sa.Numeric, default=0, server_default="0")
    created_at: Mapped[AutoCreatedAt]
    paid_at: Mapped[datetime.datetime | None] = mapped_column(sa.DateTime(True))
