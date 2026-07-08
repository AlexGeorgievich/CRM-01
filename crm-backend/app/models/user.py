import enum

from sqlalchemy import Boolean, CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role in ('admin', 'manager')",
            name="ck_users_role",
        ),
    )

    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default=UserRole.MANAGER.value)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    assigned_leads = relationship(
        "Lead",
        back_populates="assigned_manager",
        foreign_keys="Lead.assigned_manager_id",
    )
    created_leads = relationship(
        "Lead",
        back_populates="created_by",
        foreign_keys="Lead.created_by_id",
    )
    comments = relationship("Comment", back_populates="author")
