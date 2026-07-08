"""initial crm schema

Revision ID: 20260708_0001
Revises:
Create Date: 2026-07-08 12:45:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260708_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "courses",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_courses_id"), "courses", ["id"], unique=False)
    op.create_index(op.f("ix_courses_name"), "courses", ["name"], unique=True)

    op.create_table(
        "sources",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sources_id"), "sources", ["id"], unique=False)
    op.create_index(op.f("ix_sources_name"), "sources", ["name"], unique=True)

    op.create_table(
        "statuses",
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_final", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_statuses_code"), "statuses", ["code"], unique=True)
    op.create_index(op.f("ix_statuses_id"), "statuses", ["id"], unique=False)

    op.create_table(
        "users",
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("role in ('admin', 'manager')", name="ck_users_role"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "leads",
        sa.Column("customer_name", sa.String(length=255), nullable=False),
        sa.Column("contact", sa.String(length=255), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("course_id", sa.Integer(), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("status_id", sa.Integer(), nullable=False),
        sa.Column("assigned_manager_id", sa.Integer(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["assigned_manager_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["status_id"], ["statuses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_leads_assigned_manager_id"),
        "leads",
        ["assigned_manager_id"],
        unique=False,
    )
    op.create_index(op.f("ix_leads_contact"), "leads", ["contact"], unique=False)
    op.create_index(
        op.f("ix_leads_customer_name"),
        "leads",
        ["customer_name"],
        unique=False,
    )
    op.create_index(op.f("ix_leads_id"), "leads", ["id"], unique=False)
    op.create_index(op.f("ix_leads_status_id"), "leads", ["status_id"], unique=False)

    op.create_table(
        "comments",
        sa.Column("lead_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_system", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comments_author_id"), "comments", ["author_id"], unique=False)
    op.create_index(op.f("ix_comments_id"), "comments", ["id"], unique=False)
    op.create_index(op.f("ix_comments_lead_id"), "comments", ["lead_id"], unique=False)

    op.bulk_insert(
        sa.table(
            "statuses",
            sa.column("code", sa.String),
            sa.column("name", sa.String),
            sa.column("is_active", sa.Boolean),
            sa.column("is_final", sa.Boolean),
            sa.column("sort_order", sa.Integer),
        ),
        [
            {
                "code": "new",
                "name": "Новая",
                "is_active": True,
                "is_final": False,
                "sort_order": 10,
            },
            {
                "code": "in_progress",
                "name": "В работе",
                "is_active": True,
                "is_final": False,
                "sort_order": 20,
            },
            {
                "code": "paid",
                "name": "Оплачено",
                "is_active": True,
                "is_final": True,
                "sort_order": 30,
            },
            {
                "code": "lost",
                "name": "Отказ",
                "is_active": True,
                "is_final": True,
                "sort_order": 40,
            },
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_comments_lead_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_author_id"), table_name="comments")
    op.drop_table("comments")
    op.drop_index(op.f("ix_leads_status_id"), table_name="leads")
    op.drop_index(op.f("ix_leads_id"), table_name="leads")
    op.drop_index(op.f("ix_leads_customer_name"), table_name="leads")
    op.drop_index(op.f("ix_leads_contact"), table_name="leads")
    op.drop_index(op.f("ix_leads_assigned_manager_id"), table_name="leads")
    op.drop_table("leads")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_statuses_id"), table_name="statuses")
    op.drop_index(op.f("ix_statuses_code"), table_name="statuses")
    op.drop_table("statuses")
    op.drop_index(op.f("ix_sources_name"), table_name="sources")
    op.drop_index(op.f("ix_sources_id"), table_name="sources")
    op.drop_table("sources")
    op.drop_index(op.f("ix_courses_name"), table_name="courses")
    op.drop_index(op.f("ix_courses_id"), table_name="courses")
    op.drop_table("courses")
