"""update lessons table for parse tasks

Revision ID: a1b2c3d4e5f6
Revises: 70973bc52058
Create Date: 2026-04-17 20:35:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "70973bc52058"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure lessons table matches parser task requirements.
    op.alter_column(
        "lessons",
        "task_status",
        existing_type=sa.String(length=20),
        nullable=False,
        server_default=sa.text("'processing'::character varying"),
        comment="任务状态：processing/completed/failed",
    )
    op.alter_column(
        "lessons",
        "file_info",
        existing_type=sa.JSON(),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=True,
        comment="文件信息（大小、页数等）",
        postgresql_using="file_info::jsonb",
    )
    op.add_column(
        "lessons",
        sa.Column("mind_map", postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="课件全局思维导图（树状结构）"),
    )


def downgrade() -> None:
    op.drop_column("lessons", "mind_map")
    op.alter_column(
        "lessons",
        "file_info",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        type_=sa.JSON(),
        existing_nullable=True,
        comment="文件信息",
        postgresql_using="file_info::json",
    )
    op.alter_column(
        "lessons",
        "task_status",
        existing_type=sa.String(length=20),
        nullable=True,
        server_default=sa.text("'processing'::character varying"),
        comment="任务状态",
    )
