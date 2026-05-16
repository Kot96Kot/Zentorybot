from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from zentory.db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin


class Command(IdMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "commands"

    source: Mapped[str] = mapped_column(String(50), default="telegram")
    command_type: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(50), default="created")
    payload: Mapped[dict] = mapped_column(default=dict)
