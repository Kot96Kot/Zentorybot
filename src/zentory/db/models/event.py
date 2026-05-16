from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from zentory.db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin


class Event(IdMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "events"

    source: Mapped[str] = mapped_column(String(50), index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(50), default="received")
    payload: Mapped[dict] = mapped_column(default=dict)
