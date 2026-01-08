"""Initial migration: create users, conversations, messages, tasks tables

Revision ID: bb42fe410f0e
Revises: 
Create Date: 2025-12-28 21:00:39.811009

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bb42fe410f0e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    message_role_enum = postgresql.ENUM('user', 'assistant', name='messagerole', create_type=True)
    task_status_enum = postgresql.ENUM('incomplete', 'complete', name='taskstatus', create_type=True)
    message_role_enum.create(op.get_bind(), checkfirst=True)
    task_status_enum.create(op.get_bind(), checkfirst=True)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_conversations_user_id'),
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('role', message_role_enum, nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tool_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, index=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], name='fk_messages_conversation_id'),
    )

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', task_status_enum, nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_tasks_user_id'),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('tasks')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('users')

    # Drop enum types
    sa.Enum(name='taskstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='messagerole').drop(op.get_bind(), checkfirst=True)
