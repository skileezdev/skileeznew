"""Add contract system fields

Revision ID: 003
Revises: 002
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Add new fields to LearningRequest table
    op.add_column('learning_request', sa.Column('preferred_times', sa.Text(), nullable=True))
    op.add_column('learning_request', sa.Column('sessions_needed', sa.Integer(), nullable=True))
    op.add_column('learning_request', sa.Column('timeframe', sa.String(length=100), nullable=True))
    op.add_column('learning_request', sa.Column('skill_tags', sa.Text(), nullable=True))
    
    # Add new fields to Proposal table
    op.add_column('proposal', sa.Column('accepted_at', sa.DateTime(), nullable=True))
    op.add_column('proposal', sa.Column('accepted_terms', sa.Text(), nullable=True))
    op.add_column('proposal', sa.Column('availability_match', sa.Boolean(), nullable=True, default=False))
    op.add_column('proposal', sa.Column('approach_summary', sa.Text(), nullable=True))
    op.add_column('proposal', sa.Column('answers', sa.Text(), nullable=True))
    op.add_column('proposal', sa.Column('payment_model', sa.String(length=20), nullable=True, default='per_session'))
    op.add_column('proposal', sa.Column('hourly_rate', sa.Float(), nullable=True))
    
    # Add new fields to Session table
    op.add_column('session', sa.Column('scheduled_at', sa.DateTime(), nullable=True))
    op.add_column('session', sa.Column('duration_minutes', sa.Integer(), nullable=True))
    op.add_column('session', sa.Column('timezone', sa.String(length=50), nullable=True, default='UTC'))
    op.add_column('session', sa.Column('reschedule_requested', sa.Boolean(), nullable=True, default=False))
    op.add_column('session', sa.Column('reschedule_requested_by', sa.String(length=20), nullable=True))
    op.add_column('session', sa.Column('reschedule_reason', sa.Text(), nullable=True))
    op.add_column('session', sa.Column('reschedule_deadline', sa.DateTime(), nullable=True))
    op.add_column('session', sa.Column('confirmed_by_coach', sa.Boolean(), nullable=True, default=False))
    
    # Create Contract table
    op.create_table('contract',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('proposal_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('coach_id', sa.Integer(), nullable=False),
        sa.Column('contract_number', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True, default='active'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('total_sessions', sa.Integer(), nullable=False),
        sa.Column('completed_sessions', sa.Integer(), nullable=True, default=0),
        sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('paid_amount', sa.Numeric(precision=10, scale=2), nullable=True, default=0.00),
        sa.Column('payment_model', sa.String(length=20), nullable=False),
        sa.Column('rate', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=True, default='UTC'),
        sa.Column('cancellation_policy', sa.Text(), nullable=True),
        sa.Column('learning_outcomes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['coach_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposal.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contract_number')
    )
    
    # Create SessionPayment table
    op.create_table('session_payment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True, default='pending'),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_transfer_id', sa.String(length=255), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.ForeignKeyConstraint(['contract_id'], ['contract.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['session.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index(op.f('ix_contract_contract_number'), 'contract', ['contract_number'], unique=True)
    op.create_index(op.f('ix_contract_status'), 'contract', ['status'], unique=False)
    op.create_index(op.f('ix_contract_student_id'), 'contract', ['student_id'], unique=False)
    op.create_index(op.f('ix_contract_coach_id'), 'contract', ['coach_id'], unique=False)
    op.create_index(op.f('ix_session_payment_status'), 'session_payment', ['status'], unique=False)
    op.create_index(op.f('ix_session_payment_contract_id'), 'session_payment', ['contract_id'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_session_payment_contract_id'), table_name='session_payment')
    op.drop_index(op.f('ix_session_payment_status'), table_name='session_payment')
    op.drop_index(op.f('ix_contract_coach_id'), table_name='contract')
    op.drop_index(op.f('ix_contract_student_id'), table_name='contract')
    op.drop_index(op.f('ix_contract_status'), table_name='contract')
    op.drop_index(op.f('ix_contract_contract_number'), table_name='contract')
    
    # Drop tables
    op.drop_table('session_payment')
    op.drop_table('contract')
    
    # Drop columns from Session table
    op.drop_column('session', 'confirmed_by_coach')
    op.drop_column('session', 'reschedule_deadline')
    op.drop_column('session', 'reschedule_reason')
    op.drop_column('session', 'reschedule_requested_by')
    op.drop_column('session', 'reschedule_requested')
    op.drop_column('session', 'timezone')
    op.drop_column('session', 'duration_minutes')
    op.drop_column('session', 'scheduled_at')
    
    # Drop columns from Proposal table
    op.drop_column('proposal', 'hourly_rate')
    op.drop_column('proposal', 'payment_model')
    op.drop_column('proposal', 'answers')
    op.drop_column('proposal', 'approach_summary')
    op.drop_column('proposal', 'availability_match')
    op.drop_column('proposal', 'accepted_terms')
    op.drop_column('proposal', 'accepted_at')
    
    # Drop columns from LearningRequest table
    op.drop_column('learning_request', 'skill_tags')
    op.drop_column('learning_request', 'timeframe')
    op.drop_column('learning_request', 'sessions_needed')
    op.drop_column('learning_request', 'preferred_times')
