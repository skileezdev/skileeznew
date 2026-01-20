"""Add Stripe payment fields

Revision ID: 004
Revises: 003
Create Date: 2024-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Add Stripe account ID to coach_profile table
    op.add_column('coach_profile', sa.Column('stripe_account_id', sa.String(length=255), nullable=True))
    
    # Add Stripe customer ID to user table
    op.add_column('user', sa.Column('stripe_customer_id', sa.String(length=255), nullable=True))
    
    # Add indexes for better performance
    op.create_index(op.f('ix_coach_profile_stripe_account_id'), 'coach_profile', ['stripe_account_id'], unique=True)
    op.create_index(op.f('ix_user_stripe_customer_id'), 'user', ['stripe_customer_id'], unique=True)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_user_stripe_customer_id'), table_name='user')
    op.drop_index(op.f('ix_coach_profile_stripe_account_id'), table_name='coach_profile')
    
    # Drop columns
    op.drop_column('user', 'stripe_customer_id')
    op.drop_column('coach_profile', 'stripe_account_id')
