"""Alembic script template."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(as_uuid=False), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=True),
        sa.Column("username", sa.String(100), unique=True, nullable=True),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("display_name", sa.String(150), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("is_anonymous", sa.Boolean(), server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "sessions",
        sa.Column("id", sa.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "user_id",
            sa.UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(32), server_default="active"),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("meta", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    op.create_index("ix_sessions_status", "sessions", ["status"])

    op.create_table(
        "transcripts",
        sa.Column("id", sa.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "session_id",
            sa.UUID(as_uuid=False),
            sa.ForeignKey("sessions.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("language", sa.String(16), nullable=True),
        sa.Column("duration", sa.Float(), nullable=True),
        sa.Column("timestamps", postgresql.JSONB(), nullable=True),
        sa.Column("pronunciation_data", postgresql.JSONB(), nullable=True),
        sa.Column("audio_filename", sa.String(512), nullable=True),
        sa.Column("model_used", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_transcripts_session_id", "transcripts", ["session_id"])

    op.create_table(
        "fluency_metrics",
        sa.Column("id", sa.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "session_id",
            sa.UUID(as_uuid=False),
            sa.ForeignKey("sessions.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "transcript_id",
            sa.UUID(as_uuid=False),
            sa.ForeignKey("transcripts.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("words_per_minute", sa.Float(), server_default="0"),
        sa.Column("filler_words", postgresql.JSONB(), server_default="[]"),
        sa.Column("filler_word_count", sa.Integer(), server_default="0"),
        sa.Column("pause_count", sa.Integer(), server_default="0"),
        sa.Column("longest_pause", sa.Float(), server_default="0"),
        sa.Column("average_pause", sa.Float(), server_default="0"),
        sa.Column("fluency_score", sa.Float(), server_default="0"),
        sa.Column("total_words", sa.Integer(), server_default="0"),
        sa.Column("speech_duration", sa.Float(), server_default="0"),
        sa.Column("extra_metrics", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_fluency_metrics_session_id", "fluency_metrics", ["session_id"])
    op.create_index(
        "ix_fluency_metrics_transcript_id", "fluency_metrics", ["transcript_id"]
    )

    op.create_table(
        "conversations",
        sa.Column("id", sa.UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "session_id",
            sa.UUID(as_uuid=False),
            sa.ForeignKey("sessions.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("role", sa.String(32), server_default="user"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("model_used", sa.String(100), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_conversations_session_id", "conversations", ["session_id"])


def downgrade() -> None:
    op.drop_table("conversations")
    op.drop_table("fluency_metrics")
    op.drop_table("transcripts")
    op.drop_table("sessions")
    op.drop_table("users")
