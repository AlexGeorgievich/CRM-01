from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Lead(TimestampMixin, Base):
    __tablename__ = "leads"

    customer_name: Mapped[str] = mapped_column(String(255), index=True)
    contact: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str | None] = mapped_column(String(320), index=True)
    notes: Mapped[str | None] = mapped_column(Text)

    course_id: Mapped[int | None] = mapped_column(ForeignKey("courses.id"))
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"))
    status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id"), index=True)
    assigned_manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )
    next_contact_date: Mapped[date | None] = mapped_column(Date, index=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    course = relationship("Course", back_populates="leads")
    source = relationship("Source", back_populates="leads")
    status = relationship("Status", back_populates="leads")
    assigned_manager = relationship(
        "User",
        back_populates="assigned_leads",
        foreign_keys=[assigned_manager_id],
    )
    created_by = relationship(
        "User",
        back_populates="created_leads",
        foreign_keys=[created_by_id],
    )
    comments = relationship(
        "Comment",
        back_populates="lead",
        cascade="all, delete-orphan",
    )
