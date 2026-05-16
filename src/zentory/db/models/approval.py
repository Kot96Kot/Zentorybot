from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from zentory.db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin


class Approval(IdMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "approvals"

    source: Mapped[str] = mapped_column(String(50), default="telegram")
    action_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    payload: Mapped[dict] = mapped_column(default=dict)
