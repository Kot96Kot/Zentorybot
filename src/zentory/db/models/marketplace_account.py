from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from zentory.db.base import Base, IdMixin, TenantScopedMixin, TimestampMixin


class MarketplaceAccount(IdMixin, TenantScopedMixin, TimestampMixin, Base):
    __tablename__ = "marketplace_accounts"

    source: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(50), default="mock_connected")
    payload: Mapped[dict] = mapped_column(default=dict)
