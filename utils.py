from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request
import os
import uuid
import logging
from werkzeug.utils import secure_filename
import pytz
from datetime import datetime, timezone, timedelta, date

# Import app and db lazily to avoid circular imports
def get_app():
    from app import app
    return app

def get_db():
    from app import db
    return db

def is_email_verification_enabled():
    """Check if email verification is enabled via environment variable"""
    try:
        # Try to get the app context safely
        from flask import current_app
        enabled = current_app.config.get('ENABLE_EMAIL_VERIFICATION', True)
        
        print(f"DEBUG: ENABLE_EMAIL_VERIFICATION from config: {enabled}")
        
        # Email verification is enabled - let's make it work properly
        
        # Additional check: if we're on Render and no mail server is configured, disable email verification
        if enabled:
            mail_server = current_app.config.get('MAIL_SERVER')
            mail_username = current_app.config.get('MAIL_USERNAME')
            mail_password = current_app.config.get('MAIL_PASSWORD')
            
            print(f"DEBUG: MAIL_SERVER: {mail_server}")
            print(f"DEBUG: MAIL_USERNAME: {mail_username}")
            print(f"DEBUG: MAIL_PASSWORD: {'SET' if mail_password else 'NOT SET'}")
            
            if not mail_server:
                logging.warning("Email verification enabled but no mail server configured - disabling")
                print("DEBUG: No mail server configured - disabling email verification")
                return False
            
            if not mail_username or not mail_password:
                logging.warning("Email verification enabled but mail credentials not configured - disabling")
                print("DEBUG: Mail credentials not configured - disabling email verification")
                return False
        
        print(f"DEBUG: Email verification enabled: {enabled}")
        return enabled
    except Exception as e:
        logging.warning(f"Could not check email verification status: {e}")
        print(f"DEBUG: Exception in is_email_verification_enabled: {e}")
        # Default to False to prevent signup issues
        return False

def get_user_model():
    import models
    return models.User

def get_coach_profile_model():
    import models
    return models.CoachProfile

def get_student_profile_model():
    import models
    return models.StudentProfile

def get_message_model():
    import models
    return models.Message

def get_proposal_model():
    import models
    return models.Proposal

def get_session_model():
    import models
    return models.Session

def get_learning_request_model():
    import models
    return models.LearningRequest

def get_role_switch_log_model():
    import models
    return models.RoleSwitchLog

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    """
    Decorator for role-based access control in dual-role system
    @required_role can be 'student', 'coach', or list like ['student', 'coach']
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('login'))

            user = get_user_model().query.get(session['user_id'])
            if not user:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('login'))

            # Handle both single role and list of roles
            if isinstance(required_role, list):
                allowed_roles = required_role
            else:
                allowed_roles = [required_role]

            # Check if user has at least one of the required roles
            user_roles = user.get_available_roles()
            if not any(role in user_roles for role in allowed_roles):
                flash(f'You need to be a {" or ".join(allowed_roles)} to access this page.', 'error')
                return redirect(url_for('index'))

            # For specific role pages, check current role
            if len(allowed_roles) == 1:
                required_single_role = allowed_roles[0]

                # If user doesn't have current_role set, set it
                if not user.current_role:
                    user.set_initial_role()
                    db = get_db()
                    db.session.commit()

                # Check if current role matches required role
                if user.current_role != required_single_role:
                    # If user has both roles, suggest switching
                    if user.can_switch_roles() and required_single_role in user_roles:
                        other_role_name = 'Coach' if required_single_role == 'coach' else 'Student'
                        flash(f'This page requires {other_role_name} access. Please switch to your {other_role_name} role.', 'info')
                        return redirect(url_for('role_switch_page'))
                    else:
                        flash(f'You need to be a {required_single_role} to access this page.', 'error')
                        return redirect(url_for('index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Legacy decorators for backward compatibility
def coach_required(f):
    return role_required('coach')(f)

def student_required(f):
    return role_required('student')(f)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"DEBUG: admin_required check - admin_logged_in: {session.get('admin_logged_in')}")
        print(f"DEBUG: All session keys: {list(session.keys())}")
        if 'admin_logged_in' not in session:
            print("DEBUG: Admin not logged in, redirecting to admin_login")
            return redirect(url_for('admin_login'))
        print("DEBUG: Admin authentication successful")
        return f(*args, **kwargs)
    return decorated_function

def is_profile_complete(user):
    """Check if user's profile is complete based on their role"""
    if not user.current_role:
        return False
    
    if user.current_role == 'coach':
        if not user.coach_profile:
            return False
        # Check if onboarding is complete (step 9 or higher)
        if user.coach_profile.onboarding_step < 9:
            return False
        # Check if profile is approved
        if not user.coach_profile.is_approved:
            return False
        return True
    
    elif user.current_role == 'student':
        if not user.student_profile:
            return False
        # Check if student profile has required fields
        if not user.student_profile.bio or not user.student_profile.country:
            return False
        return True
    
    return False

def get_onboarding_redirect_url(user):
    """Get the appropriate onboarding redirect URL for a user"""
    if not user.current_role:
        return url_for('role_selection')
    
    if user.current_role == 'coach':
        if not user.coach_profile:
            return url_for('coach_onboarding', step=1)
        elif user.coach_profile.onboarding_step < 9:
            return url_for('coach_onboarding', step=user.coach_profile.onboarding_step or 1)
        elif not user.coach_profile.is_approved:
            return url_for('coach_pending')
        else:
            return url_for('coach_dashboard')
    
    elif user.current_role == 'student':
        if not user.student_profile:
            return url_for('student_onboarding')
        else:
            return url_for('student_dashboard')
    
    return url_for('role_selection')

def profile_completion_required(f):
    """Decorator to ensure user has completed their profile before accessing dashboard"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))

        user = get_user_model().query.get(session['user_id'])
        if not user:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))

        # Set initial role if not set
        if not user.current_role:
            user.set_initial_role()
            # Use get_db() instead of importing from app to avoid circular imports
            db = get_db()
            db.session.commit()

        # Check if profile is complete
        if not is_profile_complete(user):
            redirect_url = get_onboarding_redirect_url(user)
            if user.current_role == 'coach':
                if not user.coach_profile:
                    flash('Please complete your coach profile first.', 'info')
                elif user.coach_profile.onboarding_step < 9:
                    flash('Please complete your coach profile to continue.', 'info')
                elif not user.coach_profile.is_approved:
                    flash('Your coach profile is pending approval.', 'info')
            elif user.current_role == 'student':
                flash('Please complete your student profile first.', 'info')
            return redirect(redirect_url)

        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'user_id' in session:
        return get_user_model().query.get(session['user_id'])
    return None

def validate_role_switch(user, target_role):
    """
    Validate if a user can switch to the target role
    Returns (is_valid, error_message)
    """
    if not user:
        return False, "User not found"

    if target_role not in ['student', 'coach']:
        return False, "Invalid role specified"

    if not user.can_switch_roles():
        return False, "You don't have multiple roles to switch between"

    if target_role not in user.get_available_roles():
        return False, f"You don't have {target_role} role"

    if user.current_role == target_role:
        return False, f"You are already in {target_role} mode"

    # Additional validation for coach role
    if target_role == 'coach':
        if not user.coach_profile:
            return False, "Coach profile not found"
        if not user.coach_profile.is_approved:
            return False, "Your coach profile is not approved yet"

    # Additional validation for student role
    if target_role == 'student':
        if not user.student_profile:
            return False, "Student profile not found"

    return True, None

def switch_user_role(user, target_role):
    """
    Switch user to target role with proper validation
    Returns (success, message)
    """
    is_valid, error_message = validate_role_switch(user, target_role)

    if not is_valid:
        return False, error_message

    try:
        user.current_role = target_role
        db = get_db()
        db.session.commit()

        role_name = 'Coach' if target_role == 'coach' else 'Student'
        return True, f"Successfully switched to {role_name} mode"

    except Exception as e:
        db = get_db()
        db.session.rollback()
        return False, f"Error switching roles: {str(e)}"

def get_role_based_messages(user, other_user_id):
    """
    Get messages between users filtered by current roles
    """
    Message = get_message_model()

    if not user.current_role:
        user.set_initial_role()
        db = get_db()
        db.session.commit()

    other_user = get_user_model().query.get(other_user_id)
    if not other_user or not other_user.current_role:
        # Return all messages if role info is missing
        return Message.query.filter(
            ((Message.sender_id == user.id) & (Message.recipient_id == other_user_id)) |
            ((Message.sender_id == other_user_id) & (Message.recipient_id == user.id))
        ).order_by(Message.created_at.asc()).all()

    # Filter messages based on roles
    return Message.query.filter(
        ((Message.sender_id == user.id) & (Message.recipient_id == other_user_id) & 
         (Message.sender_role == user.current_role)) |
        ((Message.sender_id == other_user_id) & (Message.recipient_id == user.id) & 
         (Message.recipient_role == user.current_role))
    ).order_by(Message.created_at.asc()).all()

def get_role_dashboard_url(user):
    """Get the appropriate dashboard URL based on current role"""
    if not user.current_role:
        user.set_initial_role()
        db = get_db()
        db.session.commit()

    if user.current_role == 'coach':
        return url_for('coach_dashboard')
    elif user.current_role == 'student':
        return url_for('student_dashboard')
    else:
        return url_for('index')

def get_upgrade_eligibility(user):
    """
    Check what roles user can upgrade to
    Returns dict with eligibility info
    """
    eligibility = {
        'can_upgrade_to_coach': False,
        'can_upgrade_to_student': False,
        'upgrade_coach_url': None,
        'upgrade_student_url': None
    }

    if not user:
        return eligibility

    # Check if user can upgrade to coach
    if not user.is_coach:
        eligibility['can_upgrade_to_coach'] = True
        eligibility['upgrade_coach_url'] = url_for('upgrade_to_coach')

    # Check if user can upgrade to student
    if not user.is_student:
        eligibility['can_upgrade_to_student'] = True
        eligibility['upgrade_student_url'] = url_for('upgrade_to_student')

    return eligibility

def create_role_context_for_template(user):
    """
    Create role context data for templates
    """
    if not user:
        return {}
    
    return {
        'current_role': user.current_role,
        'available_roles': user.get_available_roles(),
        'can_switch_roles': user.can_switch_roles(),
        'other_role': user.get_other_role() if user.can_switch_roles() else None,
        'role_display_name': user.current_role.title() if user.current_role else 'User',
        'is_dual_role': user.can_switch_roles(),
        'role_switch_enabled': getattr(user, 'role_switch_enabled', True)
    }

# Existing utility functions (keeping all your original functions)
def calculate_match_score(coach_profile, learning_request):
    """Calculate how well a coach matches a learning request"""
    score = 0

    if not coach_profile or not learning_request:
        return 0

    # Check skills match
    if coach_profile.skills and learning_request.skills_needed:
        coach_skills = [skill.strip().lower() for skill in coach_profile.skills.split(',')]
        request_skills = [skill.strip().lower() for skill in learning_request.skills_needed.split(',')]

        matching_skills = set(coach_skills) & set(request_skills)
        score += len(matching_skills) * 10

    # Check if coach is approved
    if coach_profile.is_approved:
        score += 5

    # Check rating
    if coach_profile.rating > 0:
        score += coach_profile.rating * 2

    return score

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def get_dashboard_stats(user):
    """Get dashboard statistics for a user based on current role"""
    from datetime import datetime
    
    stats = {}

    if user.current_role == 'coach' and user.coach_profile:
        Proposal = get_proposal_model()
        Session = get_session_model()
        LearningRequest = get_learning_request_model()
        Contract = get_contract_model()

        # Count active proposals
        try:
            active_proposals = Proposal.query.filter_by(coach_id=user.id, status='pending').count()
        except Exception as e:
            # Handle database transaction errors
            if "InFailedSqlTransaction" in str(e) or "transaction is aborted" in str(e):
                print(f"Database transaction error detected, rolling back: {e}")
                try:
                    db.session.rollback()
                except:
                    pass
                active_proposals = 0
            else:
                print(f"Error counting active proposals: {e}")
                active_proposals = 0

        # Count completed sessions
        try:
            completed_sessions = Session.query.join(Proposal).filter(
                Proposal.coach_id == user.id,
                Session.status == 'completed'
            ).count()
        except Exception as e:
            # Handle missing column errors gracefully
            if "auto_activated" in str(e) or "column" in str(e).lower():
                print(f"Database schema issue detected in dashboard stats: {e}")
                completed_sessions = 0
            else:
                print(f"Error counting completed sessions: {e}")
                completed_sessions = 0

        # Count active contracts
        try:
            active_contracts = Contract.query.filter_by(coach_id=user.id, status='active').count()
        except Exception:
            active_contracts = 0

        # Count upcoming sessions
        try:
            upcoming_sessions = Session.query.join(Proposal).join(Contract).filter(
                Contract.coach_id == user.id,
                Session.status == 'scheduled',
                Session.scheduled_at > datetime.utcnow()
            ).count()
        except Exception:
            upcoming_sessions = 0

        # Count total sessions
        try:
            total_sessions = Session.query.join(Proposal).filter(
                Proposal.coach_id == user.id
            ).count()
        except Exception:
            total_sessions = 0

        # Get total earnings
        total_earnings = user.coach_profile.total_earnings or 0

        stats = {
            'active_proposals': active_proposals,
            'completed_sessions': completed_sessions,
            'active_contracts': active_contracts,
            'upcoming_sessions': upcoming_sessions,
            'total_sessions': total_sessions,
            'total_earnings': total_earnings,
            'rating': user.coach_profile.rating or 0
        }

    elif user.current_role == 'student' and user.student_profile:
        LearningRequest = get_learning_request_model()
        Proposal = get_proposal_model()
        Contract = get_contract_model()
        Session = get_session_model()

        # Count active requests
        try:
            active_requests = LearningRequest.query.filter_by(student_id=user.id, is_active=True).count()
        except Exception as e:
            # Handle database transaction errors
            if "InFailedSqlTransaction" in str(e) or "transaction is aborted" in str(e):
                print(f"Database transaction error detected, rolling back: {e}")
                try:
                    db.session.rollback()
                except:
                    pass
                active_requests = 0
            elif "auto_activated" in str(e) or "column" in str(e).lower():
                print(f"Database schema issue detected in dashboard stats: {e}")
                active_requests = 0
            else:
                print(f"Error counting active requests: {e}")
                active_requests = 0

        # Count received proposals
        try:
            received_proposals = Proposal.query.join(LearningRequest).filter(
                LearningRequest.student_id == user.id
            ).count()
        except Exception as e:
            # Handle database transaction errors
            if "InFailedSqlTransaction" in str(e) or "transaction is aborted" in str(e):
                print(f"Database transaction error detected, rolling back: {e}")
                try:
                    db.session.rollback()
                except:
                    pass
                received_proposals = 0
            else:
                print(f"Error counting received proposals: {e}")
                received_proposals = 0

        # Count active contracts
        try:
            active_contracts = Contract.query.filter_by(student_id=user.id, status='active').count()
        except Exception:
            active_contracts = 0

        # Count upcoming sessions
        try:
            upcoming_sessions = Session.query.join(Proposal).join(Contract).filter(
                Contract.student_id == user.id,
                Session.status == 'scheduled',
                Session.scheduled_at > datetime.utcnow()
            ).count()
        except Exception:
            upcoming_sessions = 0

        # Count completed sessions
        try:
            completed_sessions = Session.query.join(Proposal).join(Contract).filter(
                Contract.student_id == user.id,
                Session.status == 'completed'
            ).count()
        except Exception:
            completed_sessions = 0

        stats = {
            'active_requests': active_requests,
            'received_proposals': received_proposals,
            'active_contracts': active_contracts,
            'upcoming_sessions': upcoming_sessions,
            'completed_sessions': completed_sessions
        }

    return stats

def save_profile_picture(file):
    """Save uploaded profile picture and return the filename"""
    if file and file.filename:
        # Generate unique filename
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"

        # Ensure upload directory exists
        upload_dir = os.path.join('static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)

        # Return relative path for storing in database
        return f"uploads/{unique_filename}"

    return None

def save_portfolio_thumbnail(file):
    """Save uploaded portfolio thumbnail and return the filename"""
    if file and file.filename:
        # Generate unique filename
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1]
        unique_filename = f"portfolio_{uuid.uuid4().hex}{file_ext}"

        # Ensure upload directory exists
        upload_dir = os.path.join('static', 'uploads', 'portfolio')
        os.makedirs(upload_dir, exist_ok=True)

        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)

        # Return relative path for storing in database
        return f"uploads/portfolio/{unique_filename}"

    return None

def coach_can_access_student(coach_id, student_id):
    """Check if a coach has access to a student's profile through an accepted proposal"""
    Proposal = get_proposal_model()
    LearningRequest = get_learning_request_model()

    # Check if there's an accepted proposal between the coach and student
    accepted_proposal = Proposal.query.join(LearningRequest).filter(
        Proposal.coach_id == coach_id,
        Proposal.status == 'accepted',
        LearningRequest.student_id == student_id
    ).first()

    return accepted_proposal is not None

def can_message_user(sender_id, recipient_id):
    """Check if a user can message another user based on Upwork-like rules with role consideration"""
    Message = get_message_model()

    sender = get_user_model().query.get(sender_id)
    recipient = get_user_model().query.get(recipient_id)

    if not sender or not recipient:
        return False

    # If sender is student and recipient is coach - always allowed
    if sender.current_role == 'student' and recipient.current_role == 'coach':
        return True

    # If sender is coach and recipient is student - check conditions
    if sender.current_role == 'coach' and recipient.current_role == 'student':
        # Check if student has messaged the coach first (considering roles)
        student_messaged_first = Message.query.filter_by(
            sender_id=recipient_id,
            recipient_id=sender_id,
            sender_role='student',
            recipient_role='coach'
        ).first() is not None

        # Check if there's an accepted proposal between them
        has_accepted_proposal = coach_can_access_student(sender_id, recipient_id)

        return student_messaged_first or has_accepted_proposal

    # Same role users can't message each other in same role mode
    return False

def validate_role_switch_enhanced(user, target_role):
    """Enhanced role switch validation"""
    if not user:
        return False, "User not found"

    if target_role not in ['student', 'coach']:
        return False, "Invalid role specified"

    if not user.role_switch_enabled:
        return False, "Role switching is disabled for your account"

    if not user.can_switch_roles():
        return False, "You don't have multiple roles to switch between"

    if target_role not in user.get_available_roles():
        return False, f"You don't have {target_role} role"

    if user.current_role == target_role:
        return False, f"You are already in {target_role} mode"

    # Enhanced validation for coach role
    if target_role == 'coach':
        if not user.coach_profile:
            return False, "Coach profile not found"
        if not user.coach_profile.is_approved:
            return False, "Your coach profile is not approved yet"

    # Enhanced validation for student role
    if target_role == 'student':
        if not user.student_profile:
            return False, "Student profile not found"

    return True, None

def get_role_dashboard_url_enhanced(user):
    """Enhanced dashboard URL routing with role context"""
    if not user.current_role:
        user.set_initial_role()
        db = get_db()
        db.session.commit()

    if user.current_role == 'coach':
        if user.coach_profile and user.coach_profile.is_approved:
            return url_for('coach_dashboard')
        elif user.coach_profile and not user.coach_profile.is_approved:
            return url_for('coach_pending')
        else:
            return url_for('coach_onboarding', step=1)
    elif user.current_role == 'student':
        if user.student_profile:
            return url_for('student_dashboard')
        else:
            return url_for('student_onboarding')
    else:
        return url_for('role_selection')

def log_role_switch_attempt(user_id, target_role, success, error_message=None, ip_address=None):
    """Log role switch attempts for security monitoring"""
    try:
        RoleSwitchLog = get_role_switch_log_model()
        log_entry = RoleSwitchLog(
            user_id=user_id,
            to_role=target_role,
            switch_reason='manual_attempt',
            ip_address=ip_address,
            user_agent=request.headers.get('User-Agent') if request else None
        )

        if not success and error_message:
            log_entry.switch_reason = f'failed: {error_message}'

        db = get_db()
        db.session.add(log_entry)
        db.session.commit()

    except Exception as e:
        import logging
        logging.error(f'Failed to log role switch attempt: {e}')

def get_contract_model():
    """Get Contract model with lazy import"""
    from models import Contract
    return Contract

# ============================================================================
# TIMEZONE UTILITY FUNCTIONS
# ============================================================================

def get_user_timezone(user=None):
    """Get user's timezone preference, defaulting to UTC"""
    if user:
        try:
            if hasattr(user, 'timezone') and user.timezone:
                return user.timezone
        except AttributeError:
            # Column doesn't exist yet
            pass
    return 'UTC'

def get_timezone_object(timezone_name):
    """Get pytz timezone object, defaulting to UTC if invalid"""
    try:
        return pytz.timezone(timezone_name)
    except pytz.exceptions.UnknownTimeZoneError:
        return pytz.UTC

def convert_utc_to_user_timezone(utc_datetime, user_timezone='UTC'):
    """Convert UTC datetime to user's local timezone"""
    if not utc_datetime:
        return None
    
    # Handle date objects (convert to datetime at midnight UTC)
    if isinstance(utc_datetime, date) and not isinstance(utc_datetime, datetime):
        # It's a date object, convert to datetime at midnight UTC
        from datetime import datetime as dt
        utc_datetime = dt.combine(utc_datetime, dt.min.time())
    
    # Ensure datetime is timezone-aware
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=pytz.UTC)
    
    # Convert to user timezone
    user_tz = get_timezone_object(user_timezone)
    return utc_datetime.astimezone(user_tz)

def convert_user_timezone_to_utc(local_datetime, user_timezone='UTC'):
    """Convert user's local datetime to UTC"""
    if not local_datetime:
        return None
    
    # Ensure datetime is timezone-aware
    if local_datetime.tzinfo is None:
        user_tz = get_timezone_object(user_timezone)
        local_datetime = user_tz.localize(local_datetime)
    
    # Convert to UTC
    return local_datetime.astimezone(pytz.UTC)

def format_datetime_for_user(datetime_obj, user_timezone='UTC', format_type='full'):
    """Format datetime for user's timezone with different format options"""
    if not datetime_obj:
        return ''
    
    # Handle date objects (they don't need timezone conversion)
    if isinstance(datetime_obj, date) and not isinstance(datetime_obj, datetime):
        # It's a date object, format directly
        if format_type == 'time_only':
            return ''  # No time for date objects
        elif format_type == 'date_only':
            return datetime_obj.strftime('%b %d, %Y')
        elif format_type == 'short':
            return datetime_obj.strftime('%b %d')
        elif format_type == 'relative':
            # For date objects, just return the formatted date
            return datetime_obj.strftime('%b %d, %Y')
        else:  # full
            return datetime_obj.strftime('%B %d, %Y')
    
    # Handle datetime objects (convert to user timezone)
    local_time = convert_utc_to_user_timezone(datetime_obj, user_timezone)
    
    # Format based on type
    if format_type == 'time_only':
        return local_time.strftime('%I:%M %p')
    elif format_type == 'date_only':
        return local_time.strftime('%b %d, %Y')
    elif format_type == 'short':
        return local_time.strftime('%b %d, %I:%M %p')
    elif format_type == 'relative':
        return format_relative_time(local_time)
    else:  # full
        return local_time.strftime('%B %d, %Y at %I:%M %p')

def format_relative_time(datetime_obj):
    """Format datetime as relative time (e.g., '2 hours ago')"""
    if not datetime_obj:
        return ''
    
    # Handle date objects
    if isinstance(datetime_obj, date) and not isinstance(datetime_obj, datetime):
        # For date objects, just return the formatted date
        return datetime_obj.strftime('%b %d, %Y')
    
    # Convert date objects to datetime for comparison
    if isinstance(datetime_obj, date) and not isinstance(datetime_obj, datetime):
        from datetime import datetime as dt
        datetime_obj = dt.combine(datetime_obj, dt.min.time())
    
    # Handle timezone-aware datetime objects
    if hasattr(datetime_obj, 'tzinfo') and datetime_obj.tzinfo:
        now = datetime.now(datetime_obj.tzinfo)
    else:
        now = datetime.now()
    
    diff = now - datetime_obj
    
    if diff.days > 0:
        if diff.days == 1:
            return 'Yesterday'
        elif diff.days < 7:
            return f'{diff.days} days ago'
        else:
            return datetime_obj.strftime('%b %d')
    
    hours = diff.seconds // 3600
    if hours > 0:
        if hours == 1:
            return '1 hour ago'
        else:
            return f'{hours} hours ago'
    
    minutes = (diff.seconds % 3600) // 60
    if minutes > 0:
        if minutes == 1:
            return '1 minute ago'
        else:
            return f'{minutes} minutes ago'
    
    return 'Just now'



def is_dst_active(timezone_name):
    """Check if daylight saving time is active in the given timezone"""
    try:
        tz = pytz.timezone(timezone_name)
        now = datetime.now(tz)
        return now.dst() != timedelta(0)
    except:
        return False

def get_timezone_offset(timezone_name):
    """Get current timezone offset from UTC"""
    try:
        tz = pytz.timezone(timezone_name)
        now = datetime.now(tz)
        offset = now.utcoffset()
        hours = int(offset.total_seconds() // 3600)
        minutes = int((offset.total_seconds() % 3600) // 60)
        
        if hours >= 0:
            return f"+{hours:02d}:{minutes:02d}"
        else:
            return f"-{abs(hours):02d}:{minutes:02d}"
    except:
        return "+00:00"

# ============================================================================
# ENTERPRISE SCHEDULING SYSTEM UTILITIES
# ============================================================================

import pytz
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple
import json

def get_user_timezone(user):
    """Get user's timezone, defaulting to UTC"""
    if hasattr(user, 'timezone') and user.timezone:
        return user.timezone
    return 'UTC'

def convert_timezone(dt, from_tz, to_tz):
    """Convert datetime between timezones"""
    if isinstance(from_tz, str):
        from_tz = pytz.timezone(from_tz)
    if isinstance(to_tz, str):
        to_tz = pytz.timezone(to_tz)
    
    if dt.tzinfo is None:
        dt = from_tz.localize(dt)
    
    return dt.astimezone(to_tz)

def get_coach_availability(coach_id):
    """Get or create coach availability settings"""
    from models import CoachAvailability
    
    availability = CoachAvailability.query.filter_by(coach_id=coach_id).first()
    if not availability:
        availability = CoachAvailability(coach_id=coach_id)
        db.session.add(availability)
        db.session.commit()
    
    return availability

def get_booking_rules(coach_id):
    """Get or create booking rules for a coach"""
    from models import BookingRule
    
    rules = BookingRule.query.filter_by(coach_id=coach_id).first()
    if not rules:
        rules = BookingRule(coach_id=coach_id)
        db.session.add(rules)
        db.session.commit()
    
    return rules

def check_availability_conflict(coach_id, start_time, end_time, exclude_session_id=None):
    """Check if a time slot conflicts with existing sessions"""
    from models import ScheduledSession
    
    # Get all scheduled sessions for the coach in the time range
    query = ScheduledSession.query.filter(
        ScheduledSession.coach_id == coach_id,
        ScheduledSession.status.in_(['scheduled', 'confirmed', 'started']),
        ScheduledSession.scheduled_at < end_time,
        ScheduledSession.scheduled_at + timedelta(minutes=ScheduledSession.duration_minutes) > start_time
    )
    
    if exclude_session_id:
        query = query.filter(ScheduledSession.id != exclude_session_id)
    
    conflicting_sessions = query.all()
    return len(conflicting_sessions) > 0, conflicting_sessions

def get_available_slots_for_date(coach_id, target_date, duration_minutes=None, timezone='UTC'):
    """Get available time slots for a specific date"""
    from models import CoachAvailability, AvailabilityException, ScheduledSession
    
    # Get coach availability
    availability = get_coach_availability(coach_id)
    if not availability.is_available:
        return []
    
    # Convert date to coach's timezone
    coach_tz = pytz.timezone(availability.timezone or 'UTC')
    target_tz = pytz.timezone(timezone)
    
    # Get working hours for the day
    day_of_week = target_date.weekday()
    start_minutes, end_minutes = availability.get_working_hours(day_of_week)
    
    if not availability.is_working_day(day_of_week):
        return []
    
    # Check for exceptions
    exceptions = AvailabilityException.query.filter_by(
        availability_id=availability.id,
        date=target_date
    ).all()
    
    if any(ex.is_blocked for ex in exceptions):
        return []
    
    # Use provided duration or coach's default
    duration = duration_minutes or availability.session_duration
    
    # Generate time slots
    slots = []
    current_time = start_minutes
    
    while current_time + duration <= end_minutes:
        slot_start = datetime.combine(target_date, datetime.min.time()) + timedelta(minutes=current_time)
        slot_end = slot_start + timedelta(minutes=duration)
        
        # Convert to UTC for database queries
        slot_start_utc = coach_tz.localize(slot_start).astimezone(pytz.UTC)
        slot_end_utc = coach_tz.localize(slot_end).astimezone(pytz.UTC)
        
        # Check if slot conflicts with exceptions
        slot_conflicts = False
        for exception in exceptions:
            if exception.overlaps_with(slot_start, slot_end):
                slot_conflicts = True
                break
        
        if not slot_conflicts:
            # Check if slot conflicts with existing sessions
            has_conflict, _ = check_availability_conflict(coach_id, slot_start_utc, slot_end_utc)
            
            if not has_conflict:
                # Convert back to target timezone for display
                slot_start_display = slot_start_utc.astimezone(target_tz)
                slot_end_display = slot_end_utc.astimezone(target_tz)
                
                slots.append({
                    'start': slot_start_display,
                    'end': slot_end_display,
                    'start_utc': slot_start_utc,
                    'end_utc': slot_end_utc,
                    'available': True
                })
        
        current_time += duration + availability.buffer_after
    
    return slots

def get_available_slots_for_range(coach_id, start_date, end_date, duration_minutes=None, timezone='UTC'):
    """Get available slots for a date range"""
    all_slots = {}
    current_date = start_date
    
    while current_date <= end_date:
        slots = get_available_slots_for_date(coach_id, current_date, duration_minutes, timezone)
        if slots:
            all_slots[current_date.isoformat()] = slots
        current_date += timedelta(days=1)
    
    return all_slots

def book_session(coach_id, student_id, session_id, scheduled_at, duration_minutes, 
                session_type='paid', is_consultation=False, timezone='UTC'):
    """Book a new session with availability checking"""
    from models import ScheduledSession, Session
    
    # Convert scheduled_at to UTC
    if isinstance(scheduled_at, str):
        scheduled_at = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
    
    if scheduled_at.tzinfo is None:
        # Assume it's in the specified timezone
        tz = pytz.timezone(timezone)
        scheduled_at = tz.localize(scheduled_at)
    
    scheduled_at_utc = scheduled_at.astimezone(pytz.UTC)
    end_time_utc = scheduled_at_utc + timedelta(minutes=duration_minutes)
    
    # Check for conflicts
    has_conflict, conflicting_sessions = check_availability_conflict(
        coach_id, scheduled_at_utc, end_time_utc
    )
    
    if has_conflict:
        raise ValueError("Selected time slot conflicts with existing sessions")
    
    # Create the scheduled session
    scheduled_session = ScheduledSession(
        session_id=session_id,
        coach_id=coach_id,
        student_id=student_id,
        scheduled_at=scheduled_at_utc,
        duration_minutes=duration_minutes,
        timezone=timezone,
        session_type=session_type,
        is_consultation=is_consultation
    )
    
    db = get_db()
    db.session.add(scheduled_session)
    db.session.commit()
    
    return scheduled_session

def book_consultation(coach_id, student_id, scheduled_at, timezone='UTC'):
    """Book a free consultation session"""
    from models import CoachAvailability, ScheduledSession, Session
    
    # Get coach availability for consultation settings
    availability = get_coach_availability(coach_id)
    
    if not availability.consultation_available:
        raise ValueError("Coach does not offer free consultations")
    
    # Check consultation advance booking requirement
    consultation_deadline = scheduled_at - timedelta(hours=availability.consultation_advance_hours)
    if datetime.utcnow() > consultation_deadline:
        raise ValueError(f"Consultations must be booked at least {availability.consultation_advance_hours} hours in advance")
    
    # Create a temporary session record for the consultation
    temp_session = Session(
        proposal_id=None,  # No proposal for consultations
        session_number=0,
        status='scheduled'
    )
    db = get_db()
    db.session.add(temp_session)
    db.session.flush()  # Get the ID
    
    # Book the consultation
    consultation = book_session(
        coach_id=coach_id,
        student_id=student_id,
        session_id=temp_session.id,
        scheduled_at=scheduled_at,
        duration_minutes=availability.consultation_duration,
        session_type='consultation',
        is_consultation=True,
        timezone=timezone
    )
    
    return consultation

def can_schedule_post_contract(student_id, coach_id):
    """Check if student can schedule post-contract sessions"""
    from models import Contract
    
    # Check if there's an active contract between student and coach
    active_contract = Contract.query.filter_by(
        student_id=student_id,
        coach_id=coach_id,
        status='active'
    ).first()
    
    if not active_contract:
        return False, "No active contract found"
    
    if active_contract.payment_status != 'paid':
        return False, "Contract payment not completed"
    
    if active_contract.completed_sessions >= active_contract.total_sessions:
        return False, "All sessions in contract have been completed"
    
    return True, active_contract

def get_upcoming_sessions_for_user(user_id, role, limit=10):
    """Get upcoming sessions for a user"""
    from models import ScheduledSession
    
    if role == 'coach':
        sessions = ScheduledSession.query.filter(
            ScheduledSession.coach_id == user_id,
            ScheduledSession.status.in_(['scheduled', 'confirmed']),
            ScheduledSession.scheduled_at > datetime.utcnow()
        ).order_by(ScheduledSession.scheduled_at).limit(limit).all()
    else:  # student
        sessions = ScheduledSession.query.filter(
            ScheduledSession.student_id == user_id,
            ScheduledSession.status.in_(['scheduled', 'confirmed']),
            ScheduledSession.scheduled_at > datetime.utcnow()
        ).order_by(ScheduledSession.scheduled_at).limit(limit).all()
    
    return sessions

def send_session_notifications(scheduled_session, notification_type):
    """Send notifications for session events"""
    from models import Notification
    
    if notification_type == 'booking_confirmation':
        # Send to student
        Notification.create_notification(
            user_id=scheduled_session.student_id,
            title="Session Booked Successfully",
            message=f"Your session with {scheduled_session.coach.first_name} {scheduled_session.coach.last_name} has been scheduled for {scheduled_session.scheduled_at.strftime('%B %d, %Y at %I:%M %p')}",
            notification_type='session',
            related_id=scheduled_session.id,
            related_type='scheduled_session'
        )
        
        # Send to coach
        Notification.create_notification(
            user_id=scheduled_session.coach_id,
            title="New Session Booked",
            message=f"{scheduled_session.student.first_name} {scheduled_session.student.last_name} has booked a session for {scheduled_session.scheduled_at.strftime('%B %d, %Y at %I:%M %p')}",
            notification_type='session',
            related_id=scheduled_session.id,
            related_type='scheduled_session'
        )
    
    elif notification_type == 'reminder':
        # Send reminder notifications
        Notification.create_notification(
            user_id=scheduled_session.student_id,
            title="Session Reminder",
            message=f"Your session with {scheduled_session.coach.first_name} {scheduled_session.coach.last_name} starts in 1 hour",
            notification_type='session',
            related_id=scheduled_session.id,
            related_type='scheduled_session'
        )
        
        Notification.create_notification(
            user_id=scheduled_session.coach_id,
            title="Session Reminder",
            message=f"Your session with {scheduled_session.student.first_name} {scheduled_session.student.last_name} starts in 1 hour",
            notification_type='session',
            related_id=scheduled_session.id,
            related_type='scheduled_session'
        )
    
    elif notification_type == 'cancellation':
        # Send cancellation notifications
        Notification.create_notification(
            user_id=scheduled_session.student_id,
            title="Session Cancelled",
            message=f"Your session with {scheduled_session.coach.first_name} {scheduled_session.coach.last_name} has been cancelled",
            notification_type='session',
            related_id=scheduled_session.id,
            related_type='scheduled_session'
        )
        
        Notification.create_notification(
            user_id=scheduled_session.coach_id,
            title="Session Cancelled",
            message=f"Your session with {scheduled_session.student.first_name} {scheduled_session.student.last_name} has been cancelled",
            notification_type='session',
            related_id=scheduled_session.id,
            related_type='scheduled_session'
        )

def format_time_slot(slot, timezone='UTC'):
    """Format a time slot for display"""
    if isinstance(slot['start'], str):
        start_time = datetime.fromisoformat(slot['start'].replace('Z', '+00:00'))
    else:
        start_time = slot['start']
    
    if start_time.tzinfo is None:
        tz = pytz.timezone(timezone)
        start_time = tz.localize(start_time)
    
    return {
        'start': start_time.strftime('%I:%M %p'),
        'end': (start_time + timedelta(minutes=slot.get('duration', 60))).strftime('%I:%M %p'),
        'date': start_time.strftime('%B %d, %Y'),
        'datetime': start_time.isoformat(),
        'available': slot.get('available', True)
    }

def get_timezone_choices():
    """Get comprehensive list of timezone choices for forms"""
    import pytz
    from datetime import datetime
    
    # Get all timezone names
    all_timezones = pytz.all_timezones
    
    # Create a more user-friendly list with current offset
    timezone_choices = []
    now = datetime.now()
    
    # Add UTC first
    timezone_choices.append(('UTC', 'UTC (Coordinated Universal Time)'))
    
    # Group timezones by region for better organization
    regions = {
        'US & Canada': [
            'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
            'America/Phoenix', 'America/Anchorage', 'America/Honolulu', 'America/Toronto',
            'America/Vancouver', 'America/Edmonton', 'America/Winnipeg', 'America/Halifax'
        ],
        'Europe': [
            'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Rome', 'Europe/Madrid',
            'Europe/Amsterdam', 'Europe/Brussels', 'Europe/Vienna', 'Europe/Zurich',
            'Europe/Stockholm', 'Europe/Oslo', 'Europe/Copenhagen', 'Europe/Helsinki',
            'Europe/Warsaw', 'Europe/Prague', 'Europe/Budapest', 'Europe/Bucharest',
            'Europe/Sofia', 'Europe/Athens', 'Europe/Istanbul', 'Europe/Moscow'
        ],
        'Asia': [
            'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Seoul', 'Asia/Singapore', 'Asia/Hong_Kong',
            'Asia/Bangkok', 'Asia/Manila', 'Asia/Jakarta', 'Asia/Kuala_Lumpur',
            'Asia/Ho_Chi_Minh', 'Asia/Dhaka', 'Asia/Kolkata', 'Asia/Karachi',
            'Asia/Dubai', 'Asia/Riyadh', 'Asia/Jerusalem', 'Asia/Tehran',
            'Asia/Almaty', 'Asia/Tashkent', 'Asia/Bishkek', 'Asia/Ulaanbaatar'
        ],
        'Australia & Pacific': [
            'Australia/Sydney', 'Australia/Melbourne', 'Australia/Brisbane',
            'Australia/Perth', 'Australia/Adelaide', 'Australia/Darwin',
            'Pacific/Auckland', 'Pacific/Fiji', 'Pacific/Guam', 'Pacific/Honolulu'
        ],
        'South America': [
            'America/Sao_Paulo', 'America/Buenos_Aires', 'America/Santiago',
            'America/Lima', 'America/Bogota', 'America/Caracas', 'America/Mexico_City'
        ],
        'Africa': [
            'Africa/Cairo', 'Africa/Johannesburg', 'Africa/Lagos', 'Africa/Nairobi',
            'Africa/Casablanca', 'Africa/Algiers', 'Africa/Tunis', 'Africa/Luanda'
        ]
    }
    
    # Add timezones by region
    for region, timezones in regions.items():
        for tz_name in timezones:
            if tz_name in all_timezones:
                try:
                    tz = pytz.timezone(tz_name)
                    offset = tz.utcoffset(now)
                    offset_str = f"UTC{'+' if offset.total_seconds() >= 0 else ''}{int(offset.total_seconds() / 3600):+d}"
                    
                    # Create a user-friendly name
                    if '/' in tz_name:
                        city = tz_name.split('/')[-1].replace('_', ' ')
                        display_name = f"{city} ({offset_str})"
                    else:
                        display_name = f"{tz_name} ({offset_str})"
                    
                    timezone_choices.append((tz_name, display_name))
                except Exception:
                    # Fallback if timezone processing fails
                    timezone_choices.append((tz_name, tz_name))
    
    # Add remaining timezones (not in our organized list)
    for tz_name in all_timezones:
        if tz_name not in [choice[0] for choice in timezone_choices]:
            try:
                tz = pytz.timezone(tz_name)
                offset = tz.utcoffset(now)
                offset_str = f"UTC{'+' if offset.total_seconds() >= 0 else ''}{int(offset.total_seconds() / 3600):+d}"
                
                if '/' in tz_name:
                    city = tz_name.split('/')[-1].replace('_', ' ')
                    display_name = f"{city} ({offset_str})"
                else:
                    display_name = f"{tz_name} ({offset_str})"
                
                timezone_choices.append((tz_name, display_name))
            except Exception:
                timezone_choices.append((tz_name, tz_name))
    
    # Sort by offset for better organization
    def sort_key(choice):
        try:
            tz = pytz.timezone(choice[0])
            offset = tz.utcoffset(now)
            return offset.total_seconds()
        except:
            return 0
    
    # Sort all choices except UTC (which should stay first)
    other_choices = sorted(timezone_choices[1:], key=sort_key)
    timezone_choices = [timezone_choices[0]] + other_choices
    
    return timezone_choices

def get_available_timezones():
    """Get list of available timezones for forms (alias for get_timezone_choices)"""
    return get_timezone_choices()

def get_common_timezones():
    """Get a beautifully organized list of the most common timezones"""
    import pytz
    from datetime import datetime
    
    now = datetime.now()
    common_timezones = []
    
    # Add UTC first with special styling
    common_timezones.append(('UTC', '🌍 UTC (Coordinated Universal Time)'))
    
    # Organized by regions with emojis and better formatting
    regions = {
        '🇺🇸 North America': [
            ('America/New_York', 'New York'),
            ('America/Chicago', 'Chicago'), 
            ('America/Denver', 'Denver'),
            ('America/Los_Angeles', 'Los Angeles'),
            ('America/Toronto', 'Toronto'),
            ('America/Vancouver', 'Vancouver'),
            ('America/Mexico_City', 'Mexico City')
        ],
        '🇪🇺 Europe': [
            ('Europe/London', 'London'),
            ('Europe/Paris', 'Paris'),
            ('Europe/Berlin', 'Berlin'),
            ('Europe/Rome', 'Rome'),
            ('Europe/Madrid', 'Madrid'),
            ('Europe/Amsterdam', 'Amsterdam'),
            ('Europe/Vienna', 'Vienna'),
            ('Europe/Zurich', 'Zurich'),
            ('Europe/Stockholm', 'Stockholm'),
            ('Europe/Moscow', 'Moscow')
        ],
        '🇦🇸 Asia Pacific': [
            ('Asia/Tokyo', 'Tokyo'),
            ('Asia/Shanghai', 'Shanghai'),
            ('Asia/Seoul', 'Seoul'),
            ('Asia/Singapore', 'Singapore'),
            ('Asia/Hong_Kong', 'Hong Kong'),
            ('Asia/Bangkok', 'Bangkok'),
            ('Asia/Manila', 'Manila'),
            ('Asia/Jakarta', 'Jakarta'),
            ('Asia/Kolkata', 'Mumbai'),
            ('Asia/Dubai', 'Dubai')
        ],
        '🇦🇺 Australia & Pacific': [
            ('Australia/Sydney', 'Sydney'),
            ('Australia/Melbourne', 'Melbourne'),
            ('Australia/Brisbane', 'Brisbane'),
            ('Australia/Perth', 'Perth'),
            ('Pacific/Auckland', 'Auckland'),
            ('Pacific/Fiji', 'Fiji')
        ],
        '🌍 Other Regions': [
            ('Africa/Cairo', 'Cairo'),
            ('Africa/Johannesburg', 'Johannesburg'),
            ('America/Sao_Paulo', 'São Paulo'),
            ('America/Buenos_Aires', 'Buenos Aires'),
            ('Asia/Riyadh', 'Riyadh'),
            ('Asia/Jerusalem', 'Jerusalem')
        ]
    }
    
    # Add timezones organized by region
    for region_name, timezones in regions.items():
        # Add region separator
        common_timezones.append(('', f'── {region_name} ──'))
        
        for tz_name, city_name in timezones:
            try:
                tz = pytz.timezone(tz_name)
                offset = tz.utcoffset(now)
                offset_str = f"UTC{'+' if offset.total_seconds() >= 0 else ''}{int(offset.total_seconds() / 3600):+d}"
                
                # Create beautiful display name
                display_name = f"  {city_name} ({offset_str})"
                common_timezones.append((tz_name, display_name))
            except Exception:
                common_timezones.append((tz_name, f"  {city_name}"))
    
    # Add search option at the end
    common_timezones.append(('', '── Search More ──'))
    common_timezones.append(('__more__', '🔍 Search all timezones...'))
    
    return common_timezones

def convert_timezone(datetime_obj, from_tz, to_tz):
    """Convert datetime between timezones"""
    import pytz
    from datetime import date, datetime
    
    if not datetime_obj:
        return None
    
    # Handle date objects (convert to datetime at midnight)
    if isinstance(datetime_obj, date) and not isinstance(datetime_obj, datetime):
        datetime_obj = datetime.combine(datetime_obj, datetime.min.time())
    
    # Make datetime timezone-aware if it isn't already
    if datetime_obj.tzinfo is None:
        from_tz = pytz.timezone(from_tz) if isinstance(from_tz, str) else from_tz
        datetime_obj = from_tz.localize(datetime_obj)
    
    # Convert to target timezone
    to_tz = pytz.timezone(to_tz) if isinstance(to_tz, str) else to_tz
    return datetime_obj.astimezone(to_tz)

def get_timezone_offset(timezone_name):
    """Get current offset for a timezone"""
    import pytz
    from datetime import datetime
    
    try:
        tz = pytz.timezone(timezone_name)
        offset = tz.utcoffset(datetime.now())
        hours = int(offset.total_seconds() / 3600)
        minutes = int((offset.total_seconds() % 3600) / 60)
        
        if minutes == 0:
            return f"UTC{hours:+d}"
        else:
            return f"UTC{hours:+d}:{minutes:02d}"
    except Exception:
        return "UTC"

def format_datetime_in_timezone(datetime_obj, timezone_name, format_str="%Y-%m-%d %H:%M"):
    """Format datetime in a specific timezone"""
    if not datetime_obj:
        return ""
    
    converted = convert_timezone(datetime_obj, 'UTC', timezone_name)
    return converted.strftime(format_str)

def get_user_timezone(user):
    """Get user's timezone, defaulting to UTC if not set"""
    if user and hasattr(user, 'timezone') and user.timezone:
        return user.timezone
    return 'UTC'

def convert_utc_to_user_timezone(datetime_obj, user_timezone):
    """Convert UTC datetime to user's timezone"""
    from datetime import date, datetime
    
    # Handle date objects (no timezone conversion needed for dates)
    if isinstance(datetime_obj, date) and not isinstance(datetime_obj, datetime):
        return datetime_obj
    
    return convert_timezone(datetime_obj, 'UTC', user_timezone)

def format_datetime_for_user(datetime_obj, user_timezone, format_type='full'):
    """Format datetime for user's timezone"""
    from datetime import date, datetime
    
    if not datetime_obj:
        return ''
    
    # Handle date objects differently
    if isinstance(datetime_obj, date) and not isinstance(datetime_obj, datetime):
        # For date objects, just format the date directly
        if format_type == 'date':
            return datetime_obj.strftime('%B %d, %Y')
        elif format_type == 'short':
            return datetime_obj.strftime('%m/%d/%Y')
        else:  # full or any other type
            return datetime_obj.strftime('%B %d, %Y')
    
    # For datetime objects, use timezone conversion
    converted = convert_utc_to_user_timezone(datetime_obj, user_timezone)
    
    if format_type == 'date':
        return converted.strftime('%B %d, %Y')
    elif format_type == 'time':
        return converted.strftime('%I:%M %p')
    elif format_type == 'short':
        return converted.strftime('%m/%d/%Y %I:%M %p')
    else:  # full
        return converted.strftime('%B %d, %Y at %I:%M %p')

def format_relative_time(datetime_obj):
    """Format datetime as relative time (e.g., '2 hours ago')"""
    from datetime import datetime, date
    
    if not datetime_obj:
        return ''
    
    # Handle date objects
    if isinstance(datetime_obj, date) and not isinstance(datetime_obj, datetime):
        now = date.today()
        diff = now - datetime_obj
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.days == 0:
            return "Today"
        else:
            return f"in {abs(diff.days)} day{'s' if abs(diff.days) != 1 else ''}"
    
    # Handle datetime objects
    now = datetime.now(datetime_obj.tzinfo) if datetime_obj.tzinfo else datetime.now()
    diff = now - datetime_obj
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def validate_session_booking(coach_id, student_id, scheduled_at, duration_minutes, session_type):
    """Validate session booking parameters"""
    errors = []
    
    # Check if scheduled time is in the future
    if scheduled_at <= datetime.utcnow():
        errors.append("Session must be scheduled in the future")
    
    # Check duration
    if duration_minutes < 15 or duration_minutes > 480:
        errors.append("Session duration must be between 15 minutes and 8 hours")
    
    # Check for conflicts
    end_time = scheduled_at + timedelta(minutes=duration_minutes)
    has_conflict, _ = check_availability_conflict(coach_id, scheduled_at, end_time)
    if has_conflict:
        errors.append("Selected time slot conflicts with existing sessions")
    
    # Check session type specific rules
    if session_type == 'consultation':
        availability = get_coach_availability(coach_id)
        if not availability.consultation_available:
            errors.append("Coach does not offer free consultations")
        
        consultation_deadline = scheduled_at - timedelta(hours=availability.consultation_advance_hours)
        if datetime.utcnow() > consultation_deadline:
            errors.append(f"Consultations must be booked at least {availability.consultation_advance_hours} hours in advance")
    
    elif session_type == 'paid':
        can_schedule, message = can_schedule_post_contract(student_id, coach_id)
        if not can_schedule:
            errors.append(message)
    
    return errors

def safe_delete_user_data(user_id):
    """
    Safely delete all data associated with a user in the correct order
    to avoid foreign key constraint violations.
    """
    from models import (
        User, StudentProfile, CoachProfile, LearningRequest, Message, 
        RoleSwitchLog, SavedJob, Proposal, Session, ScreeningQuestion, 
        ScreeningAnswer, ActiveRoleSession, Contract, Language, Experience, 
        Education, PortfolioItem, StudentLanguage
    )
    
    user = User.query.get(user_id)
    if not user:
        print(f"DEBUG: User {user_id} not found")
        return False
    
    db = get_db()
    print(f"DEBUG: Got database session for user {user.id}")
    
    try:
        print(f"DEBUG: Starting safe deletion process for user {user.id}")
        
        # Step 1: Delete screening answers first (they reference proposals)
        print("DEBUG: Step 1 - Deleting screening answers")
        screening_answers = ScreeningAnswer.query.join(Proposal).filter(Proposal.coach_id == user.id).all()
        for answer in screening_answers:
            print(f"DEBUG: Deleting screening answer {answer.id}")
            db.session.delete(answer)
        db.session.commit()
        
        # Step 2: Delete contracts (they reference proposals)
        print("DEBUG: Step 2 - Deleting contracts")
        contracts = Contract.query.join(Proposal).filter(Proposal.coach_id == user.id).all()
        for contract in contracts:
            print(f"DEBUG: Deleting contract {contract.id}")
            db.session.delete(contract)
        db.session.commit()
        
        # Step 3: Delete sessions (they reference proposals) - Use no_autoflush to avoid ScheduledSession issues
        print("DEBUG: Step 3 - Deleting sessions")
        sessions = Session.query.join(Proposal).filter(Proposal.coach_id == user.id).all()
        for session_record in sessions:
            print(f"DEBUG: Deleting session {session_record.id}")
            # Use no_autoflush to prevent SQLAlchemy from trying to load related ScheduledSession records
            with db.session.no_autoflush:
                db.session.delete(session_record)
        db.session.commit()
        
        # Step 4: Delete proposals
        print("DEBUG: Step 4 - Deleting proposals")
        proposals = Proposal.query.filter_by(coach_id=user.id).all()
        for proposal in proposals:
            print(f"DEBUG: Deleting proposal {proposal.id}")
            db.session.delete(proposal)
        db.session.commit()
        
        # Step 5: Delete screening questions (they reference learning requests)
        print("DEBUG: Step 5 - Deleting screening questions")
        screening_questions = ScreeningQuestion.query.join(LearningRequest).filter(LearningRequest.student_id == user.id).all()
        for question in screening_questions:
            print(f"DEBUG: Deleting screening question {question.id}")
            db.session.delete(question)
        db.session.commit()
        
        # Step 6: Delete saved jobs
        print("DEBUG: Step 6 - Deleting saved jobs")
        saved_jobs = SavedJob.query.filter_by(coach_id=user.id).all()
        for saved_job in saved_jobs:
            print(f"DEBUG: Deleting saved job {saved_job.id}")
            db.session.delete(saved_job)
        db.session.commit()
        
        # Step 7: Delete learning requests and their associated data
        print("DEBUG: Step 7 - Deleting learning requests")
        learning_requests = LearningRequest.query.filter_by(student_id=user.id).all()
        for lr in learning_requests:
            # Delete contracts for this learning request
            for proposal in lr.proposals:
                contracts = Contract.query.filter_by(proposal_id=proposal.id).all()
                for contract in contracts:
                    db.session.delete(contract)
            
            # Delete sessions for this learning request - Use no_autoflush
            for proposal in lr.proposals:
                sessions = Session.query.filter_by(proposal_id=proposal.id).all()
                for session in sessions:
                    with db.session.no_autoflush:
                        db.session.delete(session)
            
            # Delete proposals for this learning request
            for proposal in lr.proposals:
                db.session.delete(proposal)
            
            # Delete saved jobs for this learning request
            saved_jobs_lr = SavedJob.query.filter_by(learning_request_id=lr.id).all()
            for saved_job in saved_jobs_lr:
                db.session.delete(saved_job)
            
            # Delete the learning request
            print(f"DEBUG: Deleting learning request {lr.id}")
            db.session.delete(lr)
        db.session.commit()
        
        # Step 8: Delete messages
        print("DEBUG: Step 8 - Deleting messages")
        messages = Message.query.filter(
            (Message.sender_id == user.id) | (Message.recipient_id == user.id)
        ).all()
        for message in messages:
            print(f"DEBUG: Deleting message {message.id}")
            db.session.delete(message)
        db.session.commit()
        
        # Step 8.5: Delete notifications (if table exists)
        print("DEBUG: Step 8.5 - Deleting notifications")
        try:
            from models import Notification
            notifications = Notification.query.filter_by(user_id=user.id).all()
            for notification in notifications:
                print(f"DEBUG: Deleting notification {notification.id}")
                db.session.delete(notification)
            db.session.commit()
        except Exception as e:
            print(f"DEBUG: Could not delete notifications (table may not exist): {str(e)}")
            # Continue with deletion even if notification table doesn't exist
            pass
        
        # Step 8.6: Delete coach availability (if table exists)
        print("DEBUG: Step 8.6 - Deleting coach availability")
        try:
            from models import CoachAvailability
            coach_availability = CoachAvailability.query.filter_by(coach_id=user.id).all()
            for availability in coach_availability:
                print(f"DEBUG: Deleting coach availability {availability.id}")
                db.session.delete(availability)
            db.session.commit()
        except Exception as e:
            print(f"DEBUG: Could not delete coach availability (table may not exist): {str(e)}")
            # Continue with deletion even if coach_availability table doesn't exist
            pass
        
        # Step 8.7: Delete booking rules (if table exists)
        print("DEBUG: Step 8.7 - Deleting booking rules")
        try:
            from models import BookingRule
            booking_rules = BookingRule.query.filter_by(coach_id=user.id).all()
            for rule in booking_rules:
                print(f"DEBUG: Deleting booking rule {rule.id}")
                db.session.delete(rule)
            db.session.commit()
        except Exception as e:
            print(f"DEBUG: Could not delete booking rules (table may not exist): {str(e)}")
            # Continue with deletion even if booking_rule table doesn't exist
            pass
        
        # Step 8.8: Delete calendar integrations (if table exists)
        print("DEBUG: Step 8.8 - Deleting calendar integrations")
        try:
            from models import CalendarIntegration
            calendar_integrations = CalendarIntegration.query.filter_by(coach_id=user.id).all()
            for integration in calendar_integrations:
                print(f"DEBUG: Deleting calendar integration {integration.id}")
                db.session.delete(integration)
            db.session.commit()
        except Exception as e:
            print(f"DEBUG: Could not delete calendar integrations (table may not exist): {str(e)}")
            # Continue with deletion even if calendar_integration table doesn't exist
            pass
        
        # Step 8.9: Delete call notifications first (they reference scheduled calls)
        print("DEBUG: Step 8.9 - Deleting call notifications")
        try:
            from models import CallNotification, ScheduledCall
            # Delete notifications for calls where user is the student
            student_calls = ScheduledCall.query.filter_by(student_id=user.id).all()
            for call in student_calls:
                call_notifications = CallNotification.query.filter_by(call_id=call.id).all()
                for notification in call_notifications:
                    print(f"DEBUG: Deleting call notification {notification.id} for call {call.id}")
                    db.session.delete(notification)
            
            # Delete notifications for calls where user is the coach
            coach_calls = ScheduledCall.query.filter_by(coach_id=user.id).all()
            for call in coach_calls:
                call_notifications = CallNotification.query.filter_by(call_id=call.id).all()
                for notification in call_notifications:
                    print(f"DEBUG: Deleting call notification {notification.id} for call {call.id}")
                    db.session.delete(notification)
            
            db.session.commit()
        except Exception as e:
            print(f"DEBUG: Could not delete call notifications (table may not exist): {str(e)}")
            # Continue with deletion even if call_notification table doesn't exist
            pass
        
        # Step 8.10: Delete scheduled calls (both as student and coach)
        print("DEBUG: Step 8.10 - Deleting scheduled calls")
        try:
            from models import ScheduledCall
            # Delete calls where user is the student
            student_calls = ScheduledCall.query.filter_by(student_id=user.id).all()
            for call in student_calls:
                print(f"DEBUG: Deleting scheduled call {call.id} (student)")
                db.session.delete(call)
            
            # Delete calls where user is the coach
            coach_calls = ScheduledCall.query.filter_by(coach_id=user.id).all()
            for call in coach_calls:
                print(f"DEBUG: Deleting scheduled call {call.id} (coach)")
                db.session.delete(call)
            
            db.session.commit()
        except Exception as e:
            print(f"DEBUG: Could not delete scheduled calls (table may not exist): {str(e)}")
            # Continue with deletion even if scheduled_call table doesn't exist
            pass
        
        # Step 8.11: Delete scheduled sessions (both as student and coach)
        print("DEBUG: Step 8.11 - Deleting scheduled sessions")
        try:
            from models import ScheduledSession
            # Delete sessions where user is the student
            student_sessions = ScheduledSession.query.filter_by(student_id=user.id).all()
            for session in student_sessions:
                print(f"DEBUG: Deleting scheduled session {session.id} (student)")
                db.session.delete(session)
            
            # Delete sessions where user is the coach
            coach_sessions = ScheduledSession.query.filter_by(coach_id=user.id).all()
            for session in coach_sessions:
                print(f"DEBUG: Deleting scheduled session {session.id} (coach)")
                db.session.delete(session)
            
            db.session.commit()
        except Exception as e:
            print(f"DEBUG: Could not delete scheduled sessions (table may not exist): {str(e)}")
            # Continue with deletion even if scheduled_session table doesn't exist
            pass
        
        # Step 9: Delete role switch logs
        print("DEBUG: Step 9 - Deleting role switch logs")
        role_logs = RoleSwitchLog.query.filter_by(user_id=user.id).all()
        for log in role_logs:
            print(f"DEBUG: Deleting role switch log {log.id}")
            db.session.delete(log)
        db.session.commit()
        
        # Step 10: Delete active role sessions
        print("DEBUG: Step 10 - Deleting active role sessions")
        active_sessions = ActiveRoleSession.query.filter_by(user_id=user.id).all()
        for session_record in active_sessions:
            print(f"DEBUG: Deleting active role session {session_record.id}")
            db.session.delete(session_record)
        db.session.commit()
        
        # Step 11: Delete student profile and related data
        print("DEBUG: Step 11 - Deleting student profile")
        if user.student_profile:
            # Delete student languages
            student_languages = StudentLanguage.query.filter_by(student_profile_id=user.student_profile.id).all()
            for lang in student_languages:
                db.session.delete(lang)
            
            print(f"DEBUG: Deleting student profile {user.student_profile.id}")
            db.session.delete(user.student_profile)
            db.session.commit()
        
        # Step 12: Delete coach profile and related data
        print("DEBUG: Step 12 - Deleting coach profile")
        if user.coach_profile:
            # Delete portfolio items
            portfolio_items = PortfolioItem.query.filter_by(coach_profile_id=user.coach_profile.id).all()
            for item in portfolio_items:
                db.session.delete(item)
            
            # Delete languages
            languages = Language.query.filter_by(coach_profile_id=user.coach_profile.id).all()
            for language in languages:
                db.session.delete(language)
            
            # Delete education
            education_records = Education.query.filter_by(coach_profile_id=user.coach_profile.id).all()
            for edu in education_records:
                db.session.delete(edu)
            
            # Delete experience
            experience_records = Experience.query.filter_by(coach_profile_id=user.coach_profile.id).all()
            for exp in experience_records:
                db.session.delete(exp)
            
            print(f"DEBUG: Deleting coach profile {user.coach_profile.id}")
            db.session.delete(user.coach_profile)
            db.session.commit()
        
        # Step 13: Finally delete the user
        print("DEBUG: Step 13 - Deleting user")
        db.session.delete(user)
        db.session.commit()
        
        print(f"DEBUG: Successfully deleted all data for user {user_id}")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Error during deletion: {str(e)}")
        raise e