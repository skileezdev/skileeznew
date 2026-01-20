"""Add email change verification fields

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add email change verification fields to user table
    # Check if columns already exist to avoid errors
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_columns = [col['name'] for col in inspector.get_columns('user')]
    
    if 'new_email' not in existing_columns:
        op.add_column('user', sa.Column('new_email', sa.String(length=120), nullable=True))
    
    if 'email_change_token' not in existing_columns:
        op.add_column('user', sa.Column('email_change_token', sa.String(length=255), nullable=True))
    
    if 'email_change_token_created_at' not in existing_columns:
        op.add_column('user', sa.Column('email_change_token_created_at', sa.DateTime(), nullable=True))


def downgrade():
    # Remove email change verification fields from user table
    op.drop_column('user', 'email_change_token_created_at')
    op.drop_column('user', 'email_change_token')
    op.drop_column('user', 'new_email') 