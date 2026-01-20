"""Add scheduling system

Revision ID: 010
Revises: 4cde38d7f66c
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '010'
down_revision = '4cde38d7f66c'
branch_labels = None
depends_on = None

def upgrade():
    # Create scheduled_calls table
    op.create_table('scheduled_call',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('coach_id', sa.Integer(), nullable=False),
        sa.Column('call_type', sa.String(length=20), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True, default=15),
        sa.Column('status', sa.String(length=20), nullable=True, default='scheduled'),
        # Video functionality has been removed from this application
        # sa.Column('livekit_room_name', sa.String(length=255), nullable=True),
        # sa.Column('livekit_room_sid', sa.String(length=255), nullable=True),
        sa.Column('contract_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('rescheduled_from', sa.Integer(), nullable=True),
        sa.Column('reschedule_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['coach_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['contract_id'], ['contract.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['session.id'], ),
        sa.ForeignKeyConstraint(['rescheduled_from'], ['scheduled_call.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create call_notifications table
    op.create_table('call_notification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('call_id', sa.Integer(), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('sent_to_student', sa.Boolean(), nullable=True, default=False),
        sa.Column('sent_to_coach', sa.Boolean(), nullable=True, default=False),
        sa.Column('email_sent', sa.Boolean(), nullable=True, default=False),
        sa.Column('notification_sent', sa.Boolean(), nullable=True, default=False),
        sa.ForeignKeyConstraint(['call_id'], ['scheduled_call.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for better performance
    op.create_index(op.f('ix_scheduled_call_student_id'), 'scheduled_call', ['student_id'], unique=False)
    op.create_index(op.f('ix_scheduled_call_coach_id'), 'scheduled_call', ['coach_id'], unique=False)
    op.create_index(op.f('ix_scheduled_call_scheduled_at'), 'scheduled_call', ['scheduled_at'], unique=False)
    op.create_index(op.f('ix_scheduled_call_status'), 'scheduled_call', ['status'], unique=False)
    op.create_index(op.f('ix_scheduled_call_call_type'), 'scheduled_call', ['call_type'], unique=False)
    op.create_index(op.f('ix_call_notification_call_id'), 'call_notification', ['call_id'], unique=False)
    op.create_index(op.f('ix_call_notification_notification_type'), 'call_notification', ['notification_type'], unique=False)

def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_call_notification_notification_type'), table_name='call_notification')
    op.drop_index(op.f('ix_call_notification_call_id'), table_name='call_notification')
    op.drop_index(op.f('ix_scheduled_call_call_type'), table_name='scheduled_call')
    op.drop_index(op.f('ix_scheduled_call_status'), table_name='scheduled_call')
    op.drop_index(op.f('ix_scheduled_call_scheduled_at'), table_name='scheduled_call')
    op.drop_index(op.f('ix_scheduled_call_coach_id'), table_name='scheduled_call')
    op.drop_index(op.f('ix_scheduled_call_student_id'), table_name='scheduled_call')

    # Drop tables
    op.drop_table('call_notification')
    op.drop_table('scheduled_call')
