"""Remove video session fields - video functionality removed

Revision ID: 007
Revises: 006
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Video functionality has been removed from this application
    # No video session fields to add
    pass


def downgrade():
    # Video functionality has been removed from this application
    # No video session fields to remove
    pass
