"""Create all missing tables

Revision ID: 002
Revises: 001
Create Date: 2025-01-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create tables that don't exist
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = inspector.get_table_names()
    
    # Create user table if it doesn't exist
    if 'user' not in existing_tables:
        op.create_table('user',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email', sa.String(length=120), nullable=False),
            sa.Column('password_hash', sa.String(length=256), nullable=False),
            sa.Column('first_name', sa.String(length=50), nullable=False),
            sa.Column('last_name', sa.String(length=50), nullable=False),
            sa.Column('is_student', sa.Boolean(), nullable=True),
            sa.Column('is_coach', sa.Boolean(), nullable=True),
            sa.Column('current_role', sa.String(length=20), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('role_switch_enabled', sa.Boolean(), nullable=True),
            sa.Column('last_role_switch', sa.DateTime(), nullable=True),
            sa.Column('role_switch_count', sa.Integer(), nullable=True),
            sa.Column('preferred_default_role', sa.String(length=20), nullable=True),
            sa.Column('email_verified', sa.Boolean(), nullable=True),
            sa.Column('verification_token', sa.String(length=255), nullable=True),
            sa.Column('token_created_at', sa.DateTime(), nullable=True),
            sa.Column('new_email', sa.String(length=120), nullable=True),
            sa.Column('email_change_token', sa.String(length=255), nullable=True),
            sa.Column('email_change_token_created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('email')
        )
    
    # Create student_profile table if it doesn't exist
    if 'student_profile' not in existing_tables:
        op.create_table('student_profile',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('bio', sa.Text(), nullable=True),
            sa.Column('age', sa.Integer(), nullable=True),
            sa.Column('profile_picture', sa.Text(), nullable=True),
            sa.Column('country', sa.String(length=100), nullable=True),
            sa.Column('preferred_languages', sa.String(length=255), nullable=True),
            sa.Column('is_approved', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create coach_profile table if it doesn't exist
    if 'coach_profile' not in existing_tables:
        op.create_table('coach_profile',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('goal', sa.String(length=50), nullable=True),
            sa.Column('coach_title', sa.String(length=80), nullable=True),
            sa.Column('skills', sa.Text(), nullable=True),
            sa.Column('bio', sa.Text(), nullable=True),
            sa.Column('profile_picture', sa.Text(), nullable=True),
            sa.Column('country', sa.String(length=100), nullable=True),
            sa.Column('phone_number', sa.String(length=20), nullable=True),
            sa.Column('date_of_birth', sa.Date(), nullable=True),
            sa.Column('hourly_rate', sa.Float(), nullable=True),
            sa.Column('is_approved', sa.Boolean(), nullable=True),
            sa.Column('rating', sa.Float(), nullable=True),
            sa.Column('total_earnings', sa.Float(), nullable=True),
            sa.Column('onboarding_step', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create learning_request table if it doesn't exist
    if 'learning_request' not in existing_tables:
        op.create_table('learning_request',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('student_id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('skills_needed', sa.String(length=255), nullable=True),
            sa.Column('duration', sa.String(length=50), nullable=True),
            sa.Column('budget', sa.Float(), nullable=True),
            sa.Column('experience_level', sa.String(length=20), nullable=True),
            sa.Column('skill_type', sa.String(length=20), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['student_id'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create message table if it doesn't exist
    if 'message' not in existing_tables:
        op.create_table('message',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('sender_id', sa.Integer(), nullable=False),
            sa.Column('recipient_id', sa.Integer(), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('is_read', sa.Boolean(), nullable=True),
            sa.Column('sender_role', sa.String(length=20), nullable=True),
            sa.Column('recipient_role', sa.String(length=20), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['recipient_id'], ['user.id'], ),
            sa.ForeignKeyConstraint(['sender_id'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create proposal table if it doesn't exist
    if 'proposal' not in existing_tables:
        op.create_table('proposal',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('learning_request_id', sa.Integer(), nullable=False),
            sa.Column('coach_id', sa.Integer(), nullable=False),
            sa.Column('cover_letter', sa.Text(), nullable=False),
            sa.Column('session_count', sa.Integer(), nullable=False),
            sa.Column('price_per_session', sa.Float(), nullable=False),
            sa.Column('session_duration', sa.Integer(), nullable=False),
            sa.Column('total_price', sa.Float(), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['coach_id'], ['user.id'], ),
            sa.ForeignKeyConstraint(['learning_request_id'], ['learning_request.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create experience table if it doesn't exist
    if 'experience' not in existing_tables:
        op.create_table('experience',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('coach_profile_id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=100), nullable=False),
            sa.Column('company', sa.String(length=100), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('start_date', sa.Date(), nullable=True),
            sa.Column('end_date', sa.Date(), nullable=True),
            sa.Column('is_current', sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(['coach_profile_id'], ['coach_profile.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create education table if it doesn't exist
    if 'education' not in existing_tables:
        op.create_table('education',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('coach_profile_id', sa.Integer(), nullable=False),
            sa.Column('institution', sa.String(length=100), nullable=False),
            sa.Column('degree', sa.String(length=100), nullable=True),
            sa.Column('field_of_study', sa.String(length=100), nullable=True),
            sa.Column('start_date', sa.Date(), nullable=True),
            sa.Column('end_date', sa.Date(), nullable=True),
            sa.Column('is_current', sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(['coach_profile_id'], ['coach_profile.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create language table if it doesn't exist
    if 'language' not in existing_tables:
        op.create_table('language',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('coach_profile_id', sa.Integer(), nullable=False),
            sa.Column('language', sa.String(length=50), nullable=False),
            sa.Column('proficiency', sa.String(length=20), nullable=False),
            sa.ForeignKeyConstraint(['coach_profile_id'], ['coach_profile.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create student_language table if it doesn't exist
    if 'student_language' not in existing_tables:
        op.create_table('student_language',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('student_profile_id', sa.Integer(), nullable=False),
            sa.Column('language', sa.String(length=50), nullable=False),
            sa.Column('proficiency', sa.String(length=20), nullable=False),
            sa.ForeignKeyConstraint(['student_profile_id'], ['student_profile.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create portfolio_item table if it doesn't exist
    if 'portfolio_item' not in existing_tables:
        op.create_table('portfolio_item',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('coach_profile_id', sa.Integer(), nullable=False),
            sa.Column('category', sa.String(length=50), nullable=True),
            sa.Column('title', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('project_links', sa.Text(), nullable=True),
            sa.Column('thumbnail_image', sa.String(length=500), nullable=True),
            sa.Column('skills', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['coach_profile_id'], ['coach_profile.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create session table if it doesn't exist
    if 'session' not in existing_tables:
        op.create_table('session',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('proposal_id', sa.Integer(), nullable=False),
            sa.Column('session_number', sa.Integer(), nullable=False),
            sa.Column('scheduled_date', sa.DateTime(), nullable=True),
            sa.Column('completed_date', sa.DateTime(), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=True),
            sa.Column('student_notes', sa.Text(), nullable=True),
            sa.Column('coach_notes', sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(['proposal_id'], ['proposal.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create saved_job table if it doesn't exist
    if 'saved_job' not in existing_tables:
        op.create_table('saved_job',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('coach_id', sa.Integer(), nullable=False),
            sa.Column('learning_request_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['coach_id'], ['user.id'], ),
            sa.ForeignKeyConstraint(['learning_request_id'], ['learning_request.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create screening_question table if it doesn't exist
    if 'screening_question' not in existing_tables:
        op.create_table('screening_question',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('learning_request_id', sa.Integer(), nullable=False),
            sa.Column('question_text', sa.String(length=250), nullable=False),
            sa.Column('order_index', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['learning_request_id'], ['learning_request.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create screening_answer table if it doesn't exist
    if 'screening_answer' not in existing_tables:
        op.create_table('screening_answer',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('screening_question_id', sa.Integer(), nullable=False),
            sa.Column('proposal_id', sa.Integer(), nullable=False),
            sa.Column('answer_text', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['proposal_id'], ['proposal.id'], ),
            sa.ForeignKeyConstraint(['screening_question_id'], ['screening_question.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create role_switch_log table if it doesn't exist
    if 'role_switch_log' not in existing_tables:
        op.create_table('role_switch_log',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('from_role', sa.String(length=20), nullable=True),
            sa.Column('to_role', sa.String(length=20), nullable=False),
            sa.Column('switch_reason', sa.String(length=100), nullable=True),
            sa.Column('ip_address', sa.String(length=45), nullable=True),
            sa.Column('user_agent', sa.String(length=500), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create active_role_session table if it doesn't exist
    if 'active_role_session' not in existing_tables:
        op.create_table('active_role_session',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('active_role', sa.String(length=20), nullable=False),
            sa.Column('session_start', sa.DateTime(), nullable=True),
            sa.Column('last_activity', sa.DateTime(), nullable=True),
            sa.Column('ip_address', sa.String(length=45), nullable=True),
            sa.Column('user_agent', sa.String(length=500), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade():
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('active_role_session')
    op.drop_table('role_switch_log')
    op.drop_table('screening_answer')
    op.drop_table('screening_question')
    op.drop_table('saved_job')
    op.drop_table('session')
    op.drop_table('portfolio_item')
    op.drop_table('student_language')
    op.drop_table('language')
    op.drop_table('education')
    op.drop_table('experience')
    op.drop_table('proposal')
    op.drop_table('message')
    op.drop_table('learning_request')
    op.drop_table('coach_profile')
    op.drop_table('student_profile')
    op.drop_table('user')
