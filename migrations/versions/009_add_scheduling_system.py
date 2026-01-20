"""Add enterprise scheduling system

Revision ID: 009
Revises: 008
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None

def upgrade():
    # Create coach_availability table
    op.create_table('coach_availability',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('coach_id', sa.Integer(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=True, default=True),
        sa.Column('timezone', sa.String(length=50), nullable=True, default='UTC'),
        sa.Column('monday_start', sa.Integer(), nullable=True, default=540),
        sa.Column('monday_end', sa.Integer(), nullable=True, default=1020),
        sa.Column('tuesday_start', sa.Integer(), nullable=True, default=540),
        sa.Column('tuesday_end', sa.Integer(), nullable=True, default=1020),
        sa.Column('wednesday_start', sa.Integer(), nullable=True, default=540),
        sa.Column('wednesday_end', sa.Integer(), nullable=True, default=1020),
        sa.Column('thursday_start', sa.Integer(), nullable=True, default=540),
        sa.Column('thursday_end', sa.Integer(), nullable=True, default=1020),
        sa.Column('friday_start', sa.Integer(), nullable=True, default=540),
        sa.Column('friday_end', sa.Integer(), nullable=True, default=1020),
        sa.Column('saturday_start', sa.Integer(), nullable=True, default=540),
        sa.Column('saturday_end', sa.Integer(), nullable=True, default=1020),
        sa.Column('sunday_start', sa.Integer(), nullable=True, default=540),
        sa.Column('sunday_end', sa.Integer(), nullable=True, default=1020),
        sa.Column('session_duration', sa.Integer(), nullable=True, default=60),
        sa.Column('buffer_before', sa.Integer(), nullable=True, default=0),
        sa.Column('buffer_after', sa.Integer(), nullable=True, default=15),
        sa.Column('advance_booking_days', sa.Integer(), nullable=True, default=30),
        sa.Column('same_day_booking', sa.Boolean(), nullable=True, default=False),
        sa.Column('instant_confirmation', sa.Boolean(), nullable=True, default=True),
        sa.Column('consultation_duration', sa.Integer(), nullable=True, default=15),
        sa.Column('consultation_available', sa.Boolean(), nullable=True, default=True),
        sa.Column('consultation_advance_hours', sa.Integer(), nullable=True, default=2),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.ForeignKeyConstraint(['coach_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create availability_exception table
    op.create_table('availability_exception',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('availability_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('is_blocked', sa.Boolean(), nullable=True, default=True),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['availability_id'], ['coach_availability.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create booking_rule table
    op.create_table('booking_rule',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('coach_id', sa.Integer(), nullable=False),
        sa.Column('cancellation_hours', sa.Integer(), nullable=True, default=24),
        sa.Column('reschedule_hours', sa.Integer(), nullable=True, default=12),
        sa.Column('no_show_policy', sa.String(length=50), nullable=True, default='charge_full'),
        sa.Column('require_payment_before', sa.Boolean(), nullable=True, default=True),
        sa.Column('allow_partial_payment', sa.Boolean(), nullable=True, default=False),
        sa.Column('send_reminder_hours', sa.Integer(), nullable=True, default=24),
        sa.Column('send_confirmation', sa.Boolean(), nullable=True, default=True),
        sa.Column('send_cancellation', sa.Boolean(), nullable=True, default=True),
        sa.Column('sync_with_calendar', sa.Boolean(), nullable=True, default=False),
        sa.Column('calendar_provider', sa.String(length=50), nullable=True),
        sa.Column('calendar_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.ForeignKeyConstraint(['coach_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create scheduled_session table
    op.create_table('scheduled_session',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('coach_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=True, default='UTC'),
        sa.Column('session_type', sa.String(length=50), nullable=True, default='paid'),
        sa.Column('is_consultation', sa.Boolean(), nullable=True, default=False),
        sa.Column('status', sa.String(length=50), nullable=True, default='scheduled'),
        sa.Column('confirmed_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('payment_status', sa.String(length=50), nullable=True, default='pending'),
        sa.Column('payment_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        # Video functionality has been removed from this application
        # sa.Column('livekit_room_name', sa.String(length=255), nullable=True),
        # sa.Column('livekit_room_sid', sa.String(length=255), nullable=True),
        # sa.Column('video_started_at', sa.DateTime(), nullable=True),
        # sa.Column('video_ended_at', sa.DateTime(), nullable=True),
        sa.Column('reschedule_requested', sa.Boolean(), nullable=True, default=False),
        sa.Column('reschedule_requested_by', sa.String(length=20), nullable=True),
        sa.Column('reschedule_reason', sa.Text(), nullable=True),
        sa.Column('reschedule_deadline', sa.DateTime(), nullable=True),
        sa.Column('original_scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('reminder_sent', sa.Boolean(), nullable=True, default=False),
        sa.Column('confirmation_sent', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.ForeignKeyConstraint(['session_id'], ['session.id'], ),
        sa.ForeignKeyConstraint(['coach_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create calendar_integration table
    op.create_table('calendar_integration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('coach_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('calendar_id', sa.String(length=255), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('sync_enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('sync_direction', sa.String(length=20), nullable=True, default='bidirectional'),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('selected_calendars', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.ForeignKeyConstraint(['coach_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for better performance
    op.create_index(op.f('ix_coach_availability_coach_id'), 'coach_availability', ['coach_id'], unique=False)
    op.create_index(op.f('ix_availability_exception_availability_id'), 'availability_exception', ['availability_id'], unique=False)
    op.create_index(op.f('ix_availability_exception_date'), 'availability_exception', ['date'], unique=False)
    op.create_index(op.f('ix_booking_rule_coach_id'), 'booking_rule', ['coach_id'], unique=False)
    op.create_index(op.f('ix_scheduled_session_coach_id'), 'scheduled_session', ['coach_id'], unique=False)
    op.create_index(op.f('ix_scheduled_session_student_id'), 'scheduled_session', ['student_id'], unique=False)
    op.create_index(op.f('ix_scheduled_session_scheduled_at'), 'scheduled_session', ['scheduled_at'], unique=False)
    op.create_index(op.f('ix_scheduled_session_status'), 'scheduled_session', ['status'], unique=False)
    op.create_index(op.f('ix_calendar_integration_coach_id'), 'calendar_integration', ['coach_id'], unique=False)

def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_calendar_integration_coach_id'), table_name='calendar_integration')
    op.drop_index(op.f('ix_scheduled_session_status'), table_name='scheduled_session')
    op.drop_index(op.f('ix_scheduled_session_scheduled_at'), table_name='scheduled_session')
    op.drop_index(op.f('ix_scheduled_session_student_id'), table_name='scheduled_session')
    op.drop_index(op.f('ix_scheduled_session_coach_id'), table_name='scheduled_session')
    op.drop_index(op.f('ix_booking_rule_coach_id'), table_name='booking_rule')
    op.drop_index(op.f('ix_availability_exception_date'), table_name='availability_exception')
    op.drop_index(op.f('ix_availability_exception_availability_id'), table_name='availability_exception')
    op.drop_index(op.f('ix_coach_availability_coach_id'), table_name='coach_availability')

    # Drop tables
    op.drop_table('calendar_integration')
    op.drop_table('scheduled_session')
    op.drop_table('booking_rule')
    op.drop_table('availability_exception')
    op.drop_table('coach_availability')
