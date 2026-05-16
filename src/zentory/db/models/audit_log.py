from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from zentory.db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin


class AuditLog(IdMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"

    source: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(50), default="recorded")
    actor: Mapped[str] = mapped_column(String(255), default="system")
    payload: Mapped[dict] = mapped_column(default=dict)
