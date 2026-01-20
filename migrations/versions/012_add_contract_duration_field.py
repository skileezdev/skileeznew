"""Add duration_minutes field to Contract model

Revision ID: 012
Revises: 011
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade():
    # Add duration_minutes field to Contract table
    op.add_column('contract', sa.Column('duration_minutes', sa.Integer(), nullable=True))
    
    # Set default duration for existing contracts (60 minutes)
    op.execute("UPDATE contract SET duration_minutes = 60 WHERE duration_minutes IS NULL")
    
    # Make the column not nullable after setting defaults
    op.alter_column('contract', 'duration_minutes', nullable=False)


def downgrade():
    # Remove duration_minutes field from Contract table
    op.drop_column('contract', 'duration_minutes')
