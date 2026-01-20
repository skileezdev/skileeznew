"""Add missing auto_activated columns to scheduled_call and session tables

Revision ID: 014
Revises: 013
Create Date: 2024-01-21 02:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None

def upgrade():
    # Check if auto_activated column exists in scheduled_call table
    try:
        # Try to add the column - if it fails, it probably already exists
        op.add_column('scheduled_call', sa.Column('auto_activated', sa.Boolean(), nullable=False, server_default='false'))
        print("Added auto_activated column to scheduled_call table")
    except Exception as e:
        if "already exists" in str(e) or "duplicate column name" in str(e):
            print("auto_activated column already exists in scheduled_call table")
        else:
            raise e
    
    # Check if auto_activated column exists in session table
    try:
        # Try to add the column - if it fails, it probably already exists
        op.add_column('session', sa.Column('auto_activated', sa.Boolean(), nullable=False, server_default='false'))
        print("Added auto_activated column to session table")
    except Exception as e:
        if "already exists" in str(e) or "duplicate column name" in str(e):
            print("auto_activated column already exists in session table")
        else:
            raise e
    
    # Add other missing columns that might be needed
    missing_columns = [
        ('scheduled_call', 'reminder_sent', sa.Boolean(), 'false'),
        ('scheduled_call', 'early_join_enabled', sa.Boolean(), 'true'),
        ('scheduled_call', 'buffer_minutes', sa.Integer(), '0'),
        ('scheduled_call', 'waiting_room_enabled', sa.Boolean(), 'true'),
        ('scheduled_call', 'calendar_event_id', sa.String(255), None),
        ('scheduled_call', 'calendar_provider', sa.String(50), None),
        ('scheduled_call', 'meeting_started_at', sa.DateTime(), None),
        ('scheduled_call', 'meeting_ended_at', sa.DateTime(), None),
        ('session', 'reminder_sent', sa.Boolean(), 'false'),
        ('session', 'early_join_enabled', sa.Boolean(), 'true'),
        ('session', 'buffer_minutes', sa.Integer(), '0'),
        ('session', 'meeting_started_at', sa.DateTime(), None),
        ('session', 'meeting_ended_at', sa.DateTime(), None),
        ('session', 'waiting_room_enabled', sa.Boolean(), 'true'),
        ('session', 'calendar_event_id', sa.String(255), None),
        ('session', 'calendar_provider', sa.String(50), None),
    ]
    
    for table, column, column_type, default_value in missing_columns:
        try:
            if default_value is not None:
                op.add_column(table, sa.Column(column, column_type, nullable=False, server_default=default_value))
            else:
                op.add_column(table, sa.Column(column, column_type, nullable=True))
            print(f"Added {column} column to {table} table")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column name" in str(e):
                print(f"{column} column already exists in {table} table")
            else:
                print(f"Error adding {column} column to {table} table: {e}")

def downgrade():
    # Remove the columns in reverse order
    columns_to_remove = [
        ('session', 'calendar_provider'),
        ('session', 'calendar_event_id'),
        ('session', 'waiting_room_enabled'),
        ('session', 'meeting_ended_at'),
        ('session', 'meeting_started_at'),
        ('session', 'buffer_minutes'),
        ('session', 'early_join_enabled'),
        ('session', 'reminder_sent'),
        ('session', 'auto_activated'),
        ('scheduled_call', 'meeting_ended_at'),
        ('scheduled_call', 'meeting_started_at'),
        ('scheduled_call', 'calendar_provider'),
        ('scheduled_call', 'calendar_event_id'),
        ('scheduled_call', 'waiting_room_enabled'),
        ('scheduled_call', 'buffer_minutes'),
        ('scheduled_call', 'early_join_enabled'),
        ('scheduled_call', 'reminder_sent'),
        ('scheduled_call', 'auto_activated'),
    ]
    
    for table, column in columns_to_remove:
        try:
            op.drop_column(table, column)
            print(f"Removed {column} column from {table} table")
        except Exception as e:
            print(f"Error removing {column} column from {table} table: {e}")
