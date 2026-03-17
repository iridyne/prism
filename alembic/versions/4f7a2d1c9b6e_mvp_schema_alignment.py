"""MVP schema alignment for wizard + async analysis

Revision ID: 4f7a2d1c9b6e
Revises: ad2514f50d73
Create Date: 2026-03-17 10:25:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4f7a2d1c9b6e"
down_revision: Union[str, Sequence[str], None] = "ad2514f50d73"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("portfolios", schema=None) as batch_op:
        batch_op.add_column(sa.Column("positions", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("preferences", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("status", sa.String(), nullable=True))

    with op.batch_alter_table("analysis_results", schema=None) as batch_op:
        batch_op.add_column(sa.Column("overall_score", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("recommendations", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("correlation_warnings", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("backtest_metrics", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("summary", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("agent_insights", sa.JSON(), nullable=True))

    op.create_table(
        "portfolio_snapshots",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("portfolio_id", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("total_value", sa.Float(), nullable=True),
        sa.Column("daily_return", sa.Float(), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_analysis_results_portfolio_created",
        "analysis_results",
        ["portfolio_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_analysis_results_portfolio_created", table_name="analysis_results")
    op.drop_table("portfolio_snapshots")

    with op.batch_alter_table("analysis_results", schema=None) as batch_op:
        batch_op.drop_column("agent_insights")
        batch_op.drop_column("summary")
        batch_op.drop_column("backtest_metrics")
        batch_op.drop_column("correlation_warnings")
        batch_op.drop_column("recommendations")
        batch_op.drop_column("overall_score")

    with op.batch_alter_table("portfolios", schema=None) as batch_op:
        batch_op.drop_column("status")
        batch_op.drop_column("preferences")
        batch_op.drop_column("positions")
