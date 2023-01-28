from sqlalchemy.orm import Mapped, relationship

from {{cookiecutter.project_name}}.config.database import AutoCreatedAt, Base, IntPk, LongString, OrganizationFk, Text
from {{cookiecutter.project_name}}.models.organizations import Organization


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[IntPk]
    name: Mapped[LongString]
    phone: Mapped[LongString]
    email: Mapped[LongString]
    address: Mapped[LongString]
    acquisition_channel: Mapped[LongString]
    notes: Mapped[Text]
    organization_id: Mapped[OrganizationFk]
    created_at: Mapped[AutoCreatedAt]

    organization: Mapped[Organization] = relationship("Organization")
