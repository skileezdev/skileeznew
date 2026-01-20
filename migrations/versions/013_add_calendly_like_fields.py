"""Add Calendly-like fields for automatic meeting activation

Revision ID: 013
Revises: 012_add_contract_duration_field
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '013'
down_revision = '012_add_contract_duration_field'
branch_labels = None
depends_on = None

def upgrade():
    # Add Calendly-like fields to Session table
    op.add_column('session', sa.Column('auto_activated', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('session', sa.Column('reminder_sent', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('session', sa.Column('early_join_enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('session', sa.Column('buffer_minutes', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('session', sa.Column('meeting_started_at', sa.DateTime(), nullable=True))
    op.add_column('session', sa.Column('meeting_ended_at', sa.DateTime(), nullable=True))
    op.add_column('session', sa.Column('waiting_room_enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('session', sa.Column('calendar_event_id', sa.String(255), nullable=True))
    op.add_column('session', sa.Column('calendar_provider', sa.String(50), nullable=True))
    
    # Add Calendly-like fields to ScheduledCall table
    op.add_column('scheduled_call', sa.Column('auto_activated', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('scheduled_call', sa.Column('reminder_sent', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('scheduled_call', sa.Column('early_join_enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('scheduled_call', sa.Column('buffer_minutes', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('scheduled_call', sa.Column('waiting_room_enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('scheduled_call', sa.Column('calendar_event_id', sa.String(255), nullable=True))
    op.add_column('scheduled_call', sa.Column('calendar_provider', sa.String(50), nullable=True))
    op.add_column('scheduled_call', sa.Column('meeting_started_at', sa.DateTime(), nullable=True))
    op.add_column('scheduled_call', sa.Column('meeting_ended_at', sa.DateTime(), nullable=True))
    
    # Add indexes for performance
    op.create_index('ix_session_auto_activated', 'session', ['auto_activated'])
    op.create_index('ix_session_reminder_sent', 'session', ['reminder_sent'])
    op.create_index('ix_session_scheduled_at', 'session', ['scheduled_at'])
    op.create_index('ix_scheduled_call_auto_activated', 'scheduled_call', ['auto_activated'])
    op.create_index('ix_scheduled_call_reminder_sent', 'scheduled_call', ['reminder_sent'])
    op.create_index('ix_scheduled_call_scheduled_at', 'scheduled_call', ['scheduled_at'])

def downgrade():
    # Remove indexes
    op.drop_index('ix_session_auto_activated', 'session')
    op.drop_index('ix_session_reminder_sent', 'session')
    op.drop_index('ix_session_scheduled_at', 'session')
    op.drop_index('ix_scheduled_call_auto_activated', 'scheduled_call')
    op.drop_index('ix_scheduled_call_reminder_sent', 'scheduled_call')
    op.drop_index('ix_scheduled_call_scheduled_at', 'scheduled_call')
    
    # Remove columns from ScheduledCall table
    op.drop_column('scheduled_call', 'meeting_ended_at')
    op.drop_column('scheduled_call', 'meeting_started_at')
    op.drop_column('scheduled_call', 'calendar_provider')
    op.drop_column('scheduled_call', 'calendar_event_id')
    op.drop_column('scheduled_call', 'waiting_room_enabled')
    op.drop_column('scheduled_call', 'buffer_minutes')
    op.drop_column('scheduled_call', 'early_join_enabled')
    op.drop_column('scheduled_call', 'reminder_sent')
    op.drop_column('scheduled_call', 'auto_activated')
    
    # Remove columns from Session table
    op.drop_column('session', 'calendar_provider')
    op.drop_column('session', 'calendar_event_id')
    op.drop_column('session', 'waiting_room_enabled')
    op.drop_column('session', 'meeting_ended_at')
    op.drop_column('session', 'meeting_started_at')
    op.drop_column('session', 'buffer_minutes')
    op.drop_column('session', 'early_join_enabled')
    op.drop_column('session', 'reminder_sent')
    op.drop_column('session', 'auto_activated')
