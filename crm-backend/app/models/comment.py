from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Comment(TimestampMixin, Base):
    __tablename__ = "comments"

    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    body: Mapped[str] = mapped_column(Text)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    lead = relationship("Lead", back_populates="comments")
    author = relationship("User", back_populates="comments")
