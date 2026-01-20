from forms import RoleSwitchForm, UpgradeToCoachForm, UpgradeToStudentForm
from flask import render_template, request, redirect, url_for, flash, session as flask_session, jsonify, send_from_directory
# Remove circular import - csrf will be imported later
from models import *
from forms import *
from utils import *
from utils import get_available_timezones
# Notification utilities imported inside functions to avoid circular imports
from datetime import datetime, timezone
import json
import os
import logging
import traceback
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length
import pytz
from flask_wtf.csrf import CSRFProtect

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def contract_table_exists():
    """Check if the Contract table exists in the database"""
    try:
        app = get_app()
        with app.app_context():
            db = get_db()
            inspector = db.inspect(db.engine)
            return 'contract' in inspector.get_table_names()
    except Exception:
        return False

def contract_feature_required(f):
    """Decorator to check if contract features are available"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not contract_table_exists():
            flash('Contract system is not available yet. Please try again later.', 'warning')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Import app and db lazily to avoid circular imports
def get_app():
    try:
        from app import app
        return app
    except ImportError:
        # If app is not available yet, return None
        return None

def get_db():
    try:
        from app import db
        return db
    except ImportError:
        # If db is not available yet, return None
        return None

def get_csrf():
    try:
        from app import csrf
        return csrf
    except ImportError:
        # If csrf is not available yet, return None
        return None

def create_dynamic_proposal_form(learning_request):
    """Create a dynamic proposal form with screening question fields based on the learning request"""

    class DynamicProposalForm(ProposalForm):
        pass

    # Add screening question answer fields based on the learning request's screening questions
    screening_questions = ScreeningQuestion.query.filter_by(
        learning_request_id=learning_request.id
    ).order_by(ScreeningQuestion.order_index).all()

    for question in screening_questions:
        field_name = f'screening_answer_{question.id}'
        field_label = question.question_text
        # Make each screening answer required
        field = TextAreaField(
            field_label, 
            validators=[DataRequired(), Length(min=1, max=1000)],
            render_kw={'rows': 3, 'placeholder': 'Please provide your answer...'}
        )
        setattr(DynamicProposalForm, field_name, field)

    return DynamicProposalForm()

# Initialize app variable - will be set when routes are imported
app = None

def init_app():
    """Initialize the app variable when routes are imported"""
    global app
    app = get_app()
    return app

# Initialize app if available
try:
    app = init_app()
except Exception:
    app = None

def route_if_app(rule, **options):
    """Decorator that stores route information for later registration"""
    def decorator(f):
        # Store the route information on the function
        f._route_rule = rule
        f._route_methods = options.get('methods', ['GET'])
        return f
    return decorator

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test-animation')
def test_animation():
    return render_template('test-animation.html')

@app.route('/test-form')
def test_form():
    return render_template('test_form.html')

@app.route('/test-session-cards')
def test_session_cards():
    return render_template('test_session_cards.html')

@app.route('/test-coach-update', methods=['GET', 'POST'])
def test_coach_update():
    print(f"DEBUG: test_coach_update called - Method: {request.method}")
    if request.method == 'POST':
        print(f"DEBUG: POST data: {dict(request.form)}")
        return "Form submitted successfully!"
    return "Test route working"

@app.route('/test-meeting-setup')
def test_meeting_setup_function():
    """Test route to verify meeting setup functionality"""
    try:
        from models import ScheduledSession
        sessions = ScheduledSession.query.limit(5).all()
        return f"Found {len(sessions)} sessions. First session: {sessions[0].id if sessions else 'None'}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/test-meeting-setup-route')
def test_meeting_setup_route():
    """Test route to verify the exact meeting setup route"""
    return "Meeting setup route test - this should work!"

@app.route('/debug-meeting-setup')
def debug_meeting_setup():
    """Debug route to test meeting setup functionality"""
    try:
        from models import ScheduledSession
        from google_meet_utils import create_google_meet_url, format_meeting_title
        
        # Get a sample session
        session = ScheduledSession.query.first()
        if session:
            title = format_meeting_title(session)
            meet_url = create_google_meet_url(title, session.scheduled_at, session.duration_minutes)
            return f"""
            <h1>Meeting Setup Debug</h1>
            <p><strong>Session ID:</strong> {session.id}</p>
            <p><strong>Title:</strong> {title}</p>
            <p><strong>Meet URL:</strong> <a href="{meet_url}" target="_blank">{meet_url}</a></p>
            <p><strong>Route exists:</strong> ✅ /session/{session.id}/meeting-setup</p>
            <p><strong>Test URL:</strong> <a href="/session/{session.id}/meeting-setup">/session/{session.id}/meeting-setup</a></p>
            """
        else:
            return "No sessions found in database"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/test-meeting-setup-simple')
def test_meeting_setup_simple():
    """Simple test route to verify Flask routing works"""
    return "Meeting setup simple test - Flask routing is working!"

@app.route('/test-session-123-meeting-setup')
def test_session_123_meeting_setup():
    """Test route to verify the exact meeting setup route pattern"""
    return "Test session 123 meeting setup route - this should work!"

@app.route('/meeting-setup-test/<int:session_id>')
def meeting_setup_test(session_id):
    """Test route with simplified pattern to verify Flask routing works"""
    return f"Meeting setup test route working! Session ID: {session_id}"

@app.route('/simple-meeting-setup/<int:session_id>')
def simple_meeting_setup(session_id):
    """Simple meeting setup route without complex decorators"""
    return f"Simple meeting setup route working! Session ID: {session_id}"

@app.route('/session/<int:session_id>/meeting-setup-simple')
def meeting_setup_simple(session_id):
    """Simplified meeting setup route without complex logic"""
    try:
        return f"""
        <h1>Meeting Setup Simple</h1>
        <p>Session ID: {session_id}</p>
        <p>This route works!</p>
        <p><a href="/session/{session_id}/meeting-setup">Try the full route</a></p>
        """
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/fix-database')
def fix_database():
    """Manual route to fix database schema issues"""
    try:
        # Database fixes are handled by Flask-Migrate
        return jsonify({"status": "success", "message": "Database migration handled by Flask-Migrate"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error: {str(e)}"}), 500

@app.route('/debug/signup-test')
def debug_signup_test():
    """Debug route to test signup functionality"""
    try:
        # Test imports
        from forms import SignupForm
        from models import User, CoachProfile
        from utils import is_email_verification_enabled, get_db
        
        # Test form creation
        form = SignupForm()
        
        # Test database connection
        db = get_db()
        user_count = User.query.count()
        
        # Test email verification status
        email_verification_enabled = is_email_verification_enabled()
        
        # Test CSRF token generation
        csrf_token = None
        try:
            from flask_wtf.csrf import generate_csrf
            csrf_token = generate_csrf()
        except Exception as e:
            csrf_error = str(e)
        
        # Test email utils import
        email_utils_working = False
        try:
            from email_utils import send_verification_email
            email_utils_working = True
        except Exception as e:
            email_utils_error = str(e)
        
        return f"""
        <h1>Signup Debug Test</h1>
        <p>✅ SignupForm imported successfully</p>
        <p>✅ User model imported successfully</p>
        <p>✅ CoachProfile model imported successfully</p>
        <p>✅ Database connection working (User count: {user_count})</p>
        <p>✅ Email verification enabled: {email_verification_enabled}</p>
        <p>✅ CSRF token generation: {'Working' if csrf_token else 'Failed'}</p>
        <p>✅ Email utils import: {'Working' if email_utils_working else 'Failed'}</p>
        <p>✅ All imports and basic functionality working</p>
        
        <h2>Test Form Submission</h2>
        <form method="POST" action="/debug/test-form-submission">
            <input type="hidden" name="csrf_token" value="{csrf_token or ''}"/>
            <input type="text" name="first_name" placeholder="First Name" required/><br><br>
            <input type="text" name="last_name" placeholder="Last Name" required/><br><br>
            <input type="email" name="email" placeholder="Email" required/><br><br>
            <input type="password" name="password" placeholder="Password" required/><br><br>
            <button type="submit">Test Form Submission</button>
        </form>
        """
        
    except Exception as e:
        return f"""
        <h1>Signup Debug Test - ERROR</h1>
        <p>❌ Error: {str(e)}</p>
        <p>❌ Type: {type(e).__name__}</p>
        <p>❌ Traceback: {traceback.format_exc()}</p>
        """

@app.route('/debug/test-form-submission', methods=['POST'])
def debug_test_form_submission():
    """Test form submission to identify issues"""
    try:
        from forms import SignupForm
        
        # Create form instance
        form = SignupForm()
        
        # Check if form validates
        if form.validate_on_submit():
            return f"""
            <h1>Form Submission Test - SUCCESS</h1>
            <p>✅ Form validation passed</p>
            <p>✅ First Name: {form.first_name.data}</p>
            <p>✅ Last Name: {form.last_name.data}</p>
            <p>✅ Email: {form.email.data}</p>
            <p>✅ Password: {'[HIDDEN]' if form.password.data else 'Empty'}</p>
            <p>✅ All form fields processed successfully</p>
            """
        else:
            errors = []
            for field, field_errors in form.errors.items():
                errors.append(f"{field}: {', '.join(field_errors)}")
            
            return f"""
            <h1>Form Submission Test - VALIDATION FAILED</h1>
            <p>❌ Form validation failed</p>
            <p>❌ Errors: {'; '.join(errors)}</p>
            <p>❌ CSRF Token Valid: {form.csrf_token.validate(form)}</p>
            """
            
    except Exception as e:
        return f"""
        <h1>Form Submission Test - ERROR</h1>
        <p>❌ Error: {str(e)}</p>
        <p>❌ Type: {type(e).__name__}</p>
        <p>❌ Traceback: {traceback.format_exc()}</p>
        """

@app.route('/debug/simple-signup-test', methods=['GET', 'POST'])
def debug_simple_signup_test():
    """Simple signup test that bypasses form validation"""
    if request.method == 'POST':
        try:
            print(f"DEBUG: Simple signup test - POST request received")
            print(f"DEBUG: Form data: {request.form}")
            
            # Get form data directly
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            
            print(f"DEBUG: Extracted data - Name: {first_name} {last_name}, Email: {email}")
            
            # Basic validation
            if not all([first_name, last_name, email, password]):
                return f"""
                <h1>Simple Signup Test - VALIDATION FAILED</h1>
                <p>❌ Missing required fields</p>
                <p>❌ First Name: {first_name or 'MISSING'}</p>
                <p>❌ Last Name: {last_name or 'MISSING'}</p>
                <p>❌ Email: {email or 'MISSING'}</p>
                <p>❌ Password: {'[PRESENT]' if password else 'MISSING'}</p>
                """
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return f"""
                <h1>Simple Signup Test - USER EXISTS</h1>
                <p>❌ User with email {email} already exists</p>
                <p>✅ Database connection working</p>
                """
            
            # Create new user
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                email_verified=True  # Skip email verification for test
            )
            user.set_password(password)

            get_db().session.add(user)
            get_db().session.commit()
            
            return f"""
            <h1>Simple Signup Test - SUCCESS</h1>
            <p>✅ User created successfully!</p>
            <p>✅ User ID: {user.id}</p>
            <p>✅ Name: {user.first_name} {user.last_name}</p>
            <p>✅ Email: {user.email}</p>
            <p>✅ Database operations working</p>
            <p>✅ Signup functionality is working correctly!</p>
            """
            
        except Exception as e:
            return f"""
            <h1>Simple Signup Test - ERROR</h1>
            <p>❌ Error: {str(e)}</p>
            <p>❌ Type: {type(e).__name__}</p>
            <p>❌ Traceback: {traceback.format_exc()}</p>
            """
    
    # GET request - show form
    return """
    <h1>Simple Signup Test</h1>
    <p>This test bypasses form validation to test basic signup functionality.</p>
    
    <form method="POST">
        <input type="text" name="first_name" placeholder="First Name" required/><br><br>
        <input type="text" name="last_name" placeholder="Last Name" required/><br><br>
        <input type="email" name="email" placeholder="Email" required/><br><br>
        <input type="password" name="password" placeholder="Password" required/><br><br>
        <button type="submit">Test Simple Signup</button>
    </form>
        """

@app.route('/debug/email-test')
def debug_email_test():
    """Test email configuration"""
    try:
        from email_utils import send_verification_email
        from utils import is_email_verification_enabled
        from flask import current_app
        
        # Check email verification status
        email_enabled = is_email_verification_enabled()
        
        # Check mail configuration
        mail_config = {
            'MAIL_SERVER': current_app.config.get('MAIL_SERVER'),
            'MAIL_PORT': current_app.config.get('MAIL_PORT'),
            'MAIL_USE_TLS': current_app.config.get('MAIL_USE_TLS'),
            'MAIL_USERNAME': current_app.config.get('MAIL_USERNAME'),
            'MAIL_DEFAULT_SENDER': current_app.config.get('MAIL_DEFAULT_SENDER'),
            'MAIL_TIMEOUT': current_app.config.get('MAIL_TIMEOUT'),
            'MAIL_CONNECT_TIMEOUT': current_app.config.get('MAIL_CONNECT_TIMEOUT'),
        }
        
        # Test mail instance
        mail_instance = None
        try:
            from app import mail
            mail_instance = mail
        except Exception as e:
            mail_error = str(e)
        
        return f"""
        <h1>Email Configuration Test</h1>
        <h2>Email Verification Status</h2>
        <p>✅ Email verification enabled: {email_enabled}</p>
        
        <h2>Mail Configuration</h2>
        <p>✅ MAIL_SERVER: {mail_config['MAIL_SERVER']}</p>
        <p>✅ MAIL_PORT: {mail_config['MAIL_PORT']}</p>
        <p>✅ MAIL_USE_TLS: {mail_config['MAIL_USE_TLS']}</p>
        <p>✅ MAIL_USERNAME: {mail_config['MAIL_USERNAME']}</p>
        <p>✅ MAIL_DEFAULT_SENDER: {mail_config['MAIL_DEFAULT_SENDER']}</p>
        <p>✅ MAIL_TIMEOUT: {mail_config['MAIL_TIMEOUT']}</p>
        <p>✅ MAIL_CONNECT_TIMEOUT: {mail_config['MAIL_CONNECT_TIMEOUT']}</p>
        
        <h2>Mail Instance</h2>
        <p>✅ Mail instance available: {'Yes' if mail_instance else 'No'}</p>
        
        <h2>Test Email Send</h2>
        <form method="POST" action="/debug/test-email-send">
            <input type="email" name="test_email" placeholder="Test email address" required/><br><br>
            <button type="submit">Send Test Email</button>
        </form>
        """
        
    except Exception as e:
        return f"""
        <h1>Email Configuration Test - ERROR</h1>
        <p>❌ Error: {str(e)}</p>
        <p>❌ Type: {type(e).__name__}</p>
        <p>❌ Traceback: {traceback.format_exc()}</p>
        """

@app.route('/debug/test-email-send', methods=['POST'])
def debug_test_email_send():
    """Test sending an actual email"""
    try:
        test_email = request.form.get('test_email', '').strip()
        if not test_email:
            return "<h1>Test Email Send - ERROR</h1><p>❌ No email address provided</p>"
        
        # Create a test user
        from models import User
        test_user = User(
            first_name="Test",
            last_name="User",
            email=test_email,
            email_verified=False
        )
        
        # Try to send verification email
        from email_utils import send_verification_email
        success = send_verification_email(test_user)
        
        if success:
            return f"""
            <h1>Test Email Send - SUCCESS</h1>
            <p>✅ Test email sent successfully to {test_email}</p>
            <p>✅ Check your inbox for the verification email</p>
            <p>✅ Email configuration is working correctly!</p>
            """
        else:
            return f"""
            <h1>Test Email Send - FAILED</h1>
            <p>❌ Failed to send test email to {test_email}</p>
            <p>❌ Check the logs for specific error details</p>
            <p>❌ Email configuration may need adjustment</p>
            """
            
    except Exception as e:
        return f"""
        <h1>Test Email Send - ERROR</h1>
        <p>❌ Error: {str(e)}</p>
        <p>❌ Type: {type(e).__name__}</p>
        <p>❌ Traceback: {traceback.format_exc()}</p>
        """

@app.route('/debug/smtp-test')
def debug_smtp_test():
    """Test SMTP connection directly"""
    try:
        import smtplib
        from flask import current_app
        
        # Get SMTP settings
        mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
        mail_port = current_app.config.get('MAIL_PORT', 587)
        mail_username = current_app.config.get('MAIL_USERNAME')
        mail_password = current_app.config.get('MAIL_PASSWORD')
        mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
        
        result = f"""
        <h1>SMTP Connection Test</h1>
        <h2>Configuration</h2>
        <p>✅ Server: {mail_server}</p>
        <p>✅ Port: {mail_port}</p>
        <p>✅ Username: {mail_username}</p>
        <p>✅ Password: {'[SET]' if mail_password else '[NOT SET]'}</p>
        <p>✅ Use TLS: {mail_use_tls}</p>
        
        <h2>Connection Test</h2>
        """
        
        # Test SMTP connection
        try:
            if mail_use_tls:
                server = smtplib.SMTP(mail_server, mail_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(mail_server, mail_port)
            
            if mail_username and mail_password:
                server.login(mail_username, mail_password)
                result += "<p>✅ SMTP connection successful!</p>"
                result += "<p>✅ Authentication successful!</p>"
            else:
                result += "<p>⚠️ SMTP connection successful, but no credentials to test authentication</p>"
            
            server.quit()
            
        except smtplib.SMTPAuthenticationError as e:
            result += f"<p>❌ Authentication failed: {e}</p>"
            result += "<p>💡 Check your Gmail app password</p>"
        except smtplib.SMTPConnectError as e:
            result += f"<p>❌ Connection failed: {e}</p>"
            result += "<p>💡 Check server and port settings</p>"
        except smtplib.SMTPException as e:
            result += f"<p>❌ SMTP error: {e}</p>"
        except Exception as e:
            result += f"<p>❌ General error: {e}</p>"
        
        return result
        
    except Exception as e:
        return f"""
        <h1>SMTP Test - ERROR</h1>
        <p>❌ Error: {str(e)}</p>
        <p>❌ Type: {type(e).__name__}</p>
        <p>❌ Traceback: {traceback.format_exc()}</p>
        """

@app.route('/debug/minimal-signup-test', methods=['GET', 'POST'])
def debug_minimal_signup_test():
    """Minimal signup test to isolate the issue"""
    if request.method == 'POST':
        try:
            print(f"DEBUG: Minimal signup test - POST request received")
            
            # Get form data directly
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            
            print(f"DEBUG: Extracted data - Name: {first_name} {last_name}, Email: {email}")
            
            # Basic validation
            if not all([first_name, last_name, email, password]):
                return f"""
                <h1>Minimal Signup Test - VALIDATION FAILED</h1>
                <p>❌ Missing required fields</p>
                <p>❌ First Name: {first_name or 'MISSING'}</p>
                <p>❌ Last Name: {last_name or 'MISSING'}</p>
                <p>❌ Email: {email or 'MISSING'}</p>
                <p>❌ Password: {'[PRESENT]' if password else 'MISSING'}</p>
                """
            
            # Test imports
            print(f"DEBUG: Testing imports...")
            from models import User
            from utils import get_db, is_email_verification_enabled
            
            print(f"DEBUG: Imports successful")
            
            # Test email verification function
            try:
                email_verification_enabled = is_email_verification_enabled()
                print(f"DEBUG: Email verification enabled: {email_verification_enabled}")
            except Exception as e:
                print(f"DEBUG: Email verification check failed: {e}")
                email_verification_enabled = False
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return f"""
                <h1>Minimal Signup Test - USER EXISTS</h1>
                <p>❌ User with email {email} already exists</p>
                <p>✅ Database connection working</p>
                """
            
            # Create new user
            print(f"DEBUG: Creating user...")
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                email_verified=True  # Skip email verification for test
            )
            user.set_password(password)

            print(f"DEBUG: Adding user to database...")
            get_db().session.add(user)
            get_db().session.commit()
            
            return f"""
            <h1>Minimal Signup Test - SUCCESS</h1>
            <p>✅ User created successfully!</p>
            <p>✅ User ID: {user.id}</p>
            <p>✅ Name: {user.first_name} {user.last_name}</p>
            <p>✅ Email: {user.email}</p>
            <p>✅ Database operations working</p>
            <p>✅ Email verification enabled: {email_verification_enabled}</p>
            <p>✅ Signup functionality is working correctly!</p>
            """
            
        except Exception as e:
            return f"""
            <h1>Minimal Signup Test - ERROR</h1>
            <p>❌ Error: {str(e)}</p>
            <p>❌ Type: {type(e).__name__}</p>
            <p>❌ Traceback: {traceback.format_exc()}</p>
            """
    
    # GET request - show form
    return """
    <h1>Minimal Signup Test</h1>
    <p>This test bypasses all form validation and complex logic to isolate the issue.</p>
    
    <form method="POST">
        <input type="text" name="first_name" placeholder="First Name" required/><br><br>
        <input type="text" name="last_name" placeholder="Last Name" required/><br><br>
        <input type="email" name="email" placeholder="Email" required/><br><br>
        <input type="password" name="password" placeholder="Password" required/><br><br>
        <button type="submit">Test Minimal Signup</button>
    </form>
    """

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        form = SignupForm()
        
        if request.method == 'POST':
            print(f"DEBUG: Signup form submitted")
            print(f"DEBUG: Form data: {request.form}")
            print(f"DEBUG: CSRF token present: {'csrf_token' in request.form}")
            
            if form.validate_on_submit():
                try:
                    print(f"DEBUG: Form validation passed")
                    
                    # Check if user already exists
                    existing_user = User.query.filter_by(email=form.email.data).first()
                    if existing_user:
                        print(f"DEBUG: User already exists: {form.email.data}")
                        flash('Email already registered. Please use a different email.', 'error')
                        return render_template('auth/signup.html', form=form)

                    print(f"DEBUG: Creating new user: {form.email.data}")
                    
                    # Create new user with email verification ALWAYS ENABLED
                    email_verification_enabled = True  # ALWAYS enable email verification
                    print(f"DEBUG: Email verification FORCED to enabled: {email_verification_enabled}")
                    print(f"DEBUG: Creating user with email_verified = False (needs verification)")
                    
                    user = User(
                        first_name=form.first_name.data,
                        last_name=form.last_name.data,
                        email=form.email.data,
                        email_verified=not email_verification_enabled  # Auto-verify if email verification is disabled
                    )
                    user.set_password(form.password.data)

                    get_db().session.add(user)
                    get_db().session.commit()
                    
                    print(f"DEBUG: User created successfully with ID: {user.id}")

                    # ALWAYS send verification email for new accounts
                    print("DEBUG: Sending verification email for new account")
                    try:
                        from email_utils import send_verification_email
                        print(f"DEBUG: Sending verification email to {user.email}")
                        
                        email_success = send_verification_email(user)
                        print(f"DEBUG: Email send result: {email_success}")
                        
                        if email_success:
                            print("DEBUG: Email sent successfully - showing check email page")
                            flash('Account created successfully! Please check your email to verify your account.', 'success')
                            return render_template('auth/check_email.html', user=user)
                        else:
                            print("DEBUG: Email sending failed")
                            flash('Account created but email could not be sent. Please contact support.', 'error')
                            return render_template('auth/check_email.html', user=user, email_failed=True)
                            
                    except Exception as e:
                        print(f"DEBUG: Email sending exception: {e}")
                        print(f"DEBUG: Email sending traceback: {traceback.format_exc()}")
                        flash('Account created but email verification failed. Please contact support.', 'error')
                        return render_template('auth/check_email.html', user=user, email_failed=True)

                except Exception as e:
                    get_db().session.rollback()
                    logger.error(f"Signup error: {e}")
                    logger.error(f"Signup error traceback: {traceback.format_exc()}")
                    # Check if it's a database connection error
                    error_msg = str(e).lower()
                    if 'could not translate host name' in error_msg or 'connection' in error_msg or 'database' in error_msg:
                        flash('Database connection error: Unable to connect to the database. This is a server configuration issue. Please contact support or check your database settings.', 'error')
                        print(f"ERROR: Database connection failed - {str(e)}")
                    else:
                        # Show the actual error message to help with debugging
                        error_detail = str(e)
                        print(f"DEBUG: Signup exception details: {error_detail}")
                        flash(f'An error occurred during account creation: {error_detail[:200]}. Please try again.', 'error')
                    return render_template('auth/signup.html', form=form)
            else:
                # Form validation failed
                print(f"DEBUG: Form validation failed")
                print(f"DEBUG: Form errors: {form.errors}")
                flash('Please correct the errors below.', 'error')

        return render_template('auth/signup.html', form=form)
        
    except Exception as e:
        print(f"CRITICAL: Signup route error: {e}")
        print(f"CRITICAL: Signup route traceback: {traceback.format_exc()}")
        flash('A critical error occurred. Please try again later.', 'error')
        return render_template('auth/signup.html', form=SignupForm())

@app.route('/signup/student', methods=['GET', 'POST'])
def signup_student():
    try:
        form = SignupForm()
        if form.validate_on_submit():
            try:
                # Check if user already exists
                existing_user = User.query.filter_by(email=form.email.data).first()
                if existing_user:
                    flash('Email already registered. Please login to continue.', 'info')
                    return redirect(url_for('login'))

                # Create new user as student
                user = User(
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    is_student=True,
                    current_role='student',  # Set role immediately during signup
                    email_verified=not is_email_verification_enabled()  # Auto-verify if email verification is disabled
                )
                user.set_password(form.password.data)

                # Use a more robust database session handling
                db = get_db()
                try:
                    db.session.add(user)
                    db.session.commit()
                    print(f"DEBUG: User created successfully with ID: {user.id}")
                except Exception as db_error:
                    db.session.rollback()
                    print(f"DEBUG: Database error during user creation: {db_error}")
                    raise db_error

                # Send verification email only if enabled
                if is_email_verification_enabled():
                    try:
                        from email_utils import send_verification_email
                        print(f"DEBUG: Attempting to send verification email to {user.email}")
                        
                        email_success = send_verification_email(user)
                        
                        if email_success:
                            print(f"DEBUG: Email sent successfully - showing check email page")
                            flash('Account created successfully! Please check your email to verify your account.', 'success')
                            return render_template('auth/check_email.html', user=user)
                        else:
                            # Email failed - show error and instructions
                            print(f"DEBUG: Email sending failed")
                            flash('Account created but email could not be sent. Please contact support.', 'error')
                            return render_template('auth/check_email.html', user=user, email_failed=True)
                            
                    except Exception as e:
                        print(f"DEBUG: Email verification exception: {e}")
                        import traceback
                        print(f"DEBUG: Email verification traceback: {traceback.format_exc()}")
                        # Email failed - show error
                        flash('Account created but email verification failed. Please contact support.', 'error')
                        return render_template('auth/check_email.html', user=user, email_failed=True)
                else:
                    flash('Account created successfully! You can now log in.', 'success')
                    return redirect(url_for('login'))
                    
            except Exception as e:
                get_db().session.rollback()
                logger.error(f"Signup student error: {e}")
                logger.error(f"Signup student error traceback: {traceback.format_exc()}")
                # Check if it's a database connection error
                error_msg = str(e).lower()
                if 'could not translate host name' in error_msg or 'connection' in error_msg or 'database' in error_msg:
                    flash('Database connection error. Please check that your database is running and try again.', 'error')
                else:
                    # Show the actual error message to help with debugging
                    error_detail = str(e)
                    print(f"DEBUG: Signup student exception details: {error_detail}")
                    flash(f'An error occurred during account creation: {error_detail[:200]}. Please try again.', 'error')
                return render_template('auth/signup.html', form=form, user_type='student')
        elif request.method == 'POST':
            # Form validation failed
            print(f"DEBUG: Form validation failed for student signup")
            print(f"DEBUG: Form errors: {form.errors}")
            flash('Please correct the errors below.', 'error')

        return render_template('auth/signup.html', form=form, user_type='student')
        
    except Exception as e:
        print(f"CRITICAL: Signup student route error: {e}")
        print(f"CRITICAL: Signup student route traceback: {traceback.format_exc()}")
        flash('A critical error occurred. Please try again later.', 'error')
        return render_template('auth/signup.html', form=SignupForm(), user_type='student')

@app.route('/signup/coach', methods=['GET', 'POST'])
def signup_coach():
    try:
        form = SignupForm()
        if form.validate_on_submit():
            try:
                # Check if user already exists
                existing_user = User.query.filter_by(email=form.email.data).first()
                if existing_user:
                    flash('Email already registered. Please login to continue.', 'info')
                    return redirect(url_for('login'))

                # Create new user as coach
                user = User(
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    is_coach=True,
                    current_role='coach',  # Set role immediately during signup
                    email_verified=not is_email_verification_enabled()  # Auto-verify if email verification is disabled
                )
                user.set_password(form.password.data)

                get_db().session.add(user)
                get_db().session.commit()  # Commit user first to get the ID

                # Create coach profile
                coach_profile = CoachProfile(user_id=user.id)
                get_db().session.add(coach_profile)
                get_db().session.commit()

                # Send verification email only if enabled
                if is_email_verification_enabled():
                    try:
                        from email_utils import send_verification_email
                        print(f"DEBUG: Attempting to send verification email to coach {user.email}")
                        
                        email_success = send_verification_email(user)
                        
                        if email_success:
                            flash('Account created successfully! Please check your email to verify your account.', 'success')
                            return render_template('auth/check_email.html', user=user)
                        else:
                            # Email failed
                            print(f"DEBUG: Email verification failed for coach {user.email}")
                            flash('Account created but email could not be sent. Please contact support.', 'error')
                            return render_template('auth/check_email.html', user=user, email_failed=True)
                            
                    except Exception as e:
                        print(f"Email verification error: {e}")
                        import traceback
                        print(f"DEBUG: Email verification traceback: {traceback.format_exc()}")
                        flash('Account created but email verification failed. Please contact support.', 'error')
                        return redirect(url_for('login'))
                else:
                    flash('Account created successfully! You can now log in.', 'success')
                    return redirect(url_for('login'))
                    
            except Exception as e:
                get_db().session.rollback()
                logger.error(f"Signup coach error: {e}")
                logger.error(f"Signup coach error traceback: {traceback.format_exc()}")
                # Check if it's a database connection error
                error_msg = str(e).lower()
                if 'could not translate host name' in error_msg or 'connection' in error_msg or 'database' in error_msg:
                    flash('Database connection error. Please check that your database is running and try again.', 'error')
                else:
                    # Show the actual error message to help with debugging
                    error_detail = str(e)
                    print(f"DEBUG: Signup coach exception details: {error_detail}")
                    flash(f'An error occurred during account creation: {error_detail[:200]}. Please try again.', 'error')
                return render_template('auth/signup.html', form=form, user_type='coach')
        elif request.method == 'POST':
            # Form validation failed
            print(f"DEBUG: Form validation failed for coach signup")
            print(f"DEBUG: Form errors: {form.errors}")
            flash('Please correct the errors below.', 'error')

        return render_template('auth/signup.html', form=form, user_type='coach')
        
    except Exception as e:
        print(f"CRITICAL: Signup coach route error: {e}")
        print(f"CRITICAL: Signup coach route traceback: {traceback.format_exc()}")
        flash('A critical error occurred. Please try again later.', 'error')
        return render_template('auth/signup.html', form=SignupForm(), user_type='coach')

@app.route('/verify-email/<token>')
def verify_email(token):
    """Verify email with token"""
    # If email verification is disabled, redirect to login
    if not is_email_verification_enabled():
        flash('Email verification is currently disabled.', 'info')
        return redirect(url_for('login'))
    
    from email_utils import verify_email_token
    
    success, message = verify_email_token(token)
    
    if success:
        # Get the user who was verified
        user = User.query.filter_by(verification_token=token).first()
        if user:
            # Clear the verification token after successful verification
            user.verification_token = None
            get_db().session.commit()
            # Set initial role if not set
            if not user.current_role:
                user.set_initial_role()
                get_db().session.commit()
            
            # Log the user in automatically after verification
            session['user_id'] = user.id
            
            # Redirect based on role and profile completion
            if user.current_role == 'coach':
                if not user.coach_profile:
                    # Create coach profile and redirect to onboarding
                    coach_profile = CoachProfile(user_id=user.id)
                    get_db().session.add(coach_profile)
                    get_db().session.commit()
                    flash('Email verified successfully! Please complete your coach profile.', 'success')
                    return redirect(url_for('coach_onboarding', step=1))
                elif user.coach_profile.onboarding_step < 9:
                    flash('Email verified successfully! Please complete your coach profile.', 'success')
                    return redirect(url_for('coach_onboarding', step=user.coach_profile.onboarding_step or 1))
                elif user.coach_profile.onboarding_step == 10 and not user.coach_profile.is_approved:
                    flash('Profile submitted! Your coach profile is pending approval.', 'info')
                    return redirect(url_for('coach_pending'))
                elif user.coach_profile.is_approved:
                    flash('Email verified successfully! Welcome back.', 'success')
                    return redirect(url_for('coach_dashboard'))
                else:
                    # Fallback: send to onboarding
                    return redirect(url_for('coach_onboarding', step=1))
            
            elif user.current_role == 'student':
                if not user.student_profile:
                    flash('Email verified successfully! Please complete your student profile.', 'success')
                    return redirect(url_for('student_onboarding'))
                else:
                    flash('Email verified successfully! Welcome back.', 'success')
                    return redirect(url_for('student_dashboard'))
            else:
                # Fallback: if no role is set, try to determine from user flags
                if user.is_student and not user.is_coach:
                    user.current_role = 'student'
                    get_db().session.commit()
                    flash('Email verified successfully! Please complete your student profile.', 'success')
                    return redirect(url_for('student_onboarding'))
                elif user.is_coach and not user.is_student:
                    user.current_role = 'coach'
                    get_db().session.commit()
                    flash('Email verified successfully! Please complete your coach profile.', 'success')
                    return redirect(url_for('coach_onboarding', step=1))
                else:
                    # Last resort: redirect to role selection
                    flash('Email verified successfully! Please select your role.', 'success')
                    return redirect(url_for('role_selection'))
        else:
            flash('Email verified successfully! You can now log in to your account.', 'success')
            return render_template('auth/verification_success.html')
    else:
        flash(message, 'error')
        return render_template('auth/verification_error.html', error_message=message)

@app.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email"""
    # If email verification is disabled, redirect to login
    if not is_email_verification_enabled():
        flash('Email verification is currently disabled.', 'info')
        return redirect(url_for('login'))
    
    email = request.form.get('email')
    
    if not email:
        flash('Email address is required.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        flash('Email address not found.', 'error')
        return redirect(url_for('login'))
    
    if user.email_verified:
        flash('Email is already verified.', 'info')
        return redirect(url_for('login'))
    
    from email_utils import resend_verification_email
    if resend_verification_email(user):
        flash('Verification email sent successfully! Please check your inbox.', 'success')
    else:
        flash('Failed to send verification email. Please try again later.', 'error')
    
    return render_template('auth/check_email.html', user=user)

@app.route('/test-email')
def test_email():
    """Test email sending - for debugging"""
    try:
        from email_utils import send_email
        test_email_address = request.args.get('email', 'test@example.com')
        
        subject = "Test Email from Skileez"
        html_content = """
        <html>
        <body>
            <h2>Test Email</h2>
            <p>This is a test email from Skileez to verify email functionality.</p>
            <p>If you receive this, email sending is working correctly!</p>
        </body>
        </html>
        """
        
        success = send_email([test_email_address], subject, html_content)
        
        if success:
            return f"✅ Test email sent successfully to {test_email_address}. Check your inbox!"
        else:
            return f"❌ Failed to send test email to {test_email_address}. Check logs for details."
            
    except Exception as e:
        return f"❌ Error: {str(e)}"

@app.route('/verify-email-change/<token>')
def verify_email_change(token):
    """Verify email change with token"""
    # If email verification is disabled, redirect to account settings
    if not is_email_verification_enabled():
        flash('Email verification is currently disabled.', 'info')
        return redirect(url_for('account_settings'))
    
    from email_utils import verify_email_change_token
    
    success, message = verify_email_change_token(token)
    
    if success:
        flash('Email address changed successfully! You can now log in with your new email address.', 'success')
        return render_template('auth/verification_success.html', 
                             title="Email Changed Successfully",
                             message="Your email address has been updated successfully.",
                             action_url=url_for('login'),
                             action_text="Continue to Login")
    else:
        flash(f'Email change failed: {message}', 'error')
        return render_template('auth/verification_error.html',
                             title="Email Change Failed",
                             message=message,
                             action_url=url_for('account_settings'),
                             action_text="Back to Account Settings")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            # Check if email is verified (only if email verification is enabled)
            if is_email_verification_enabled() and not user.email_verified:
                flash('Please verify your email address before logging in. Check your inbox for a verification email.', 'error')
                return render_template('auth/login.html', form=form)
            
            session['user_id'] = user.id

            # NEW: Set initial role if not set
            if not user.current_role:
                user.set_initial_role()
                get_db().session.commit()

            # Use helper function for consistent redirect logic
            redirect_url = get_onboarding_redirect_url(user)
            
            # Add appropriate flash messages
            if user.current_role == 'coach':
                if not user.coach_profile:
                    flash('Welcome! Please complete your coach profile to get started.', 'info')
                elif user.coach_profile.onboarding_step < 9:
                    flash('Please complete your coach profile to continue.', 'info')
                elif not user.coach_profile.is_approved:
                    flash('Your coach profile is pending approval.', 'info')
                else:
                    flash('Welcome back!', 'success')
            elif user.current_role == 'student':
                if not user.student_profile:
                    flash('Welcome! Please complete your student profile to get started.', 'info')
                else:
                    flash('Welcome back!', 'success')
            else:
                flash('Please select your role to continue.', 'info')
            
            return redirect(redirect_url)
        else:
            flash('Invalid email or password.', 'error')

    return render_template('auth/login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/role-selection', methods=['GET', 'POST'])
@login_required
def role_selection():
    user = get_current_user()

    if request.method == 'POST':
        role = request.form.get('role')

        if role == 'coach':
            user.is_coach = True
            user.current_role = 'coach'  # Set current role
            # Create coach profile
            coach_profile = CoachProfile(user_id=user.id)
            get_db().session.add(coach_profile)
            get_db().session.commit()
            return redirect(url_for('coach_onboarding', step=1))

        elif role == 'student':
            user.is_student = True
            user.current_role = 'student'  # Set current role
            get_db().session.commit()
            flash('Welcome! Please complete your student profile to get started.', 'info')
            return redirect(url_for('student_onboarding'))

    return render_template('auth/role_selection.html', user=user)

# Coach Onboarding Routes
@app.route('/coach/onboarding/<int:step>', methods=['GET', 'POST'])
@login_required
def coach_onboarding(step):
    user = get_current_user()
    
    # Check if user is a coach
    if not user.is_coach:
        flash('This onboarding is for coaches only.', 'error')
        return redirect(url_for('role_selection'))
    
    # Create coach profile if it doesn't exist
    if not user.coach_profile:
        coach_profile = CoachProfile(user_id=user.id)
        get_db().session.add(coach_profile)
        get_db().session.commit()
        user = get_current_user()  # Refresh user object
    
    coach_profile = user.coach_profile

    if step == 1:
        form = CoachStep1Form()
        # Pre-populate form with existing data
        if coach_profile.goal:
            form.goal.data = coach_profile.goal
            
        if form.validate_on_submit():
            coach_profile.goal = form.goal.data
            coach_profile.onboarding_step = 2
            get_db().session.commit()
            return redirect(url_for('coach_onboarding', step=2))
        return render_template('onboarding/coach_step1.html', form=form, step=step)

    elif step == 2:
        form = CoachStep3Form()
        # Pre-populate form with existing data
        if coach_profile.skills:
            form.skills.data = coach_profile.skills
            
        if form.validate_on_submit():
            coach_profile.skills = form.skills.data
            coach_profile.onboarding_step = 3
            get_db().session.commit()
            return redirect(url_for('coach_onboarding', step=3))
        return render_template('onboarding/coach_step3.html', form=form, step=step)

    elif step == 3:
        form = CoachStep4Form()
        # Pre-populate form with existing data (use the most recent experience)
        if coach_profile.experiences:
            latest_experience = coach_profile.experiences[-1]  # Get the most recent experience
            form.title.data = latest_experience.title
            form.company.data = latest_experience.company
            form.description.data = latest_experience.description
            form.start_date.data = latest_experience.start_date
            form.end_date.data = latest_experience.end_date
            form.is_current.data = latest_experience.is_current
            
        if form.validate_on_submit():
            if form.title.data:  # Only add if user filled out the form
                experience = Experience(
                    coach_profile_id=coach_profile.id,
                    title=form.title.data,
                    company=form.company.data,
                    description=form.description.data,
                    start_date=form.start_date.data,
                    end_date=form.end_date.data,
                    is_current=form.is_current.data
                )
                get_db().session.add(experience)

            coach_profile.onboarding_step = 4
            get_db().session.commit()
            return redirect(url_for('coach_onboarding', step=4))
        return render_template('onboarding/coach_step4.html', form=form, step=step)

    elif step == 4:
        form = CoachStep5Form()
        # Pre-populate form with existing data (use the most recent education)
        if coach_profile.educations:
            latest_education = coach_profile.educations[-1]  # Get the most recent education
            form.institution.data = latest_education.institution
            form.degree.data = latest_education.degree
            form.field_of_study.data = latest_education.field_of_study
            form.start_date.data = latest_education.start_date
            form.end_date.data = latest_education.end_date
            form.is_current.data = latest_education.is_current
            
        if form.validate_on_submit():
            if form.institution.data:  # Only add if user filled out the form
                education = Education(
                    coach_profile_id=coach_profile.id,
                    institution=form.institution.data,
                    degree=form.degree.data,
                    field_of_study=form.field_of_study.data,
                    start_date=form.start_date.data,
                    end_date=form.end_date.data,
                    is_current=form.is_current.data
                )
                get_db().session.add(education)

            coach_profile.onboarding_step = 5
            get_db().session.commit()
            return redirect(url_for('coach_onboarding', step=5))
        return render_template('onboarding/coach_step5.html', form=form, step=step)

    # New Portfolio Step (skippable)
    elif step == 5:
        form = CoachStep5PortfolioForm()

        if request.method == 'POST':
            action = request.form.get('action')

            if action == 'add_portfolio' and form.validate_on_submit():
                if form.title.data:  # Only add if user provided a title
                    # Get additional fields from form data
                    category = request.form.get('category', 'work_sample')
                    
                    # Handle thumbnail image upload
                    thumbnail_image_path = None
                    if 'thumbnail_image' in request.files:
                        thumbnail_file = request.files['thumbnail_image']
                        if thumbnail_file and thumbnail_file.filename:
                            try:
                                from utils import save_portfolio_thumbnail
                                thumbnail_image_path = save_portfolio_thumbnail(thumbnail_file)
                                if not thumbnail_image_path:
                                    flash('Error uploading thumbnail image. Please try again.', 'error')
                                    return redirect(url_for('coach_onboarding', step=5))
                            except Exception as e:
                                print(f"DEBUG: Error saving portfolio thumbnail: {str(e)}")
                                flash('Error uploading thumbnail image. Please try again.', 'error')
                                return redirect(url_for('coach_onboarding', step=5))

                    portfolio_item = PortfolioItem(
                        coach_profile_id=coach_profile.id,
                        category=category,
                        title=form.title.data,
                        description=form.description.data,
                        project_links=form.project_links.data,
                        thumbnail_image=thumbnail_image_path,
                        skills=form.skills.data
                    )
                    get_db().session.add(portfolio_item)
                    get_db().session.commit()
                    flash('Portfolio item added successfully!', 'success')

                # Clear form after successful submission
                form = CoachStep5PortfolioForm()
                return redirect(url_for('coach_onboarding', step=5))

            elif action == 'remove_portfolio':
                portfolio_id = request.form.get('portfolio_id')
                portfolio_item = PortfolioItem.query.filter_by(
                    id=portfolio_id,
                    coach_profile_id=coach_profile.id
                ).first()

                if portfolio_item:
                    get_db().session.delete(portfolio_item)
                    get_db().session.commit()
                    flash('Portfolio item removed successfully!', 'success')

                return redirect(url_for('coach_onboarding', step=5))

            elif action == 'continue':
                # Portfolio step is skippable, proceed to languages
                coach_profile.onboarding_step = 6
                get_db().session.commit()
                return redirect(url_for('coach_onboarding', step=6))

        return render_template('onboarding/coach_step5_portfolio.html', form=form, step=step, coach_profile=coach_profile)

    elif step == 6:
        form = CoachStep6Form()

        if request.method == 'POST':
            action = request.form.get('action')

            if action == 'add_language':
                # Check if this is an AJAX request
                if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
                    # Get form data directly from request
                    language = request.form.get('language')
                    proficiency = request.form.get('proficiency')
                    
                    # Basic validation
                    if not language or not proficiency:
                        return jsonify({
                            'success': False,
                            'message': 'Language and proficiency are required',
                            'errors': {
                                'language': ['This field is required'] if not language else [],
                                'proficiency': ['This field is required'] if not proficiency else []
                            }
                        })
                    
                    # Check if language already exists for this coach
                    existing_language = Language.query.filter_by(
                        coach_profile_id=coach_profile.id,
                        language=language
                    ).first()

                    if not existing_language:
                        language_obj = Language(
                            coach_profile_id=coach_profile.id,
                            language=language,
                            proficiency=proficiency
                        )
                        get_db().session.add(language_obj)
                        get_db().session.commit()
                        
                        return jsonify({
                            'success': True,
                            'message': 'Language added successfully!',
                            'language': {
                                'id': language_obj.id,
                                'language': language_obj.language,
                                'proficiency': language_obj.proficiency
                            }
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'message': 'You have already added this language.',
                            'errors': {
                                'language': ['You have already added this language']
                            }
                        })
                else:
                    # Traditional form submission (fallback)
                    if form.validate_on_submit():
                        # Check if language already exists for this coach
                        existing_language = Language.query.filter_by(
                            coach_profile_id=coach_profile.id,
                            language=form.language.data
                        ).first()

                        if not existing_language:
                            language = Language(
                                coach_profile_id=coach_profile.id,
                                language=form.language.data,
                                proficiency=form.proficiency.data
                            )
                            get_db().session.add(language)
                            get_db().session.commit()
                            flash('Language added successfully!', 'success')
                        else:
                            flash('You have already added this language.', 'error')

                        return redirect(url_for('coach_onboarding', step=6))

            elif action == 'remove_language':
                language_id = request.form.get('language_id')
                language = Language.query.filter_by(
                    id=language_id,
                    coach_profile_id=coach_profile.id
                ).first()

                if language:
                    get_db().session.delete(language)
                    get_db().session.commit()
                    
                    # Check if this is an AJAX request
                    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
                        return jsonify({
                            'success': True,
                            'message': 'Language removed successfully!'
                        })
                    else:
                        flash('Language removed successfully!', 'success')
                else:
                    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
                        return jsonify({
                            'success': False,
                            'message': 'Language not found'
                        })

                return redirect(url_for('coach_onboarding', step=6))

            elif action == 'continue':
                # Check if coach has at least one language
                if coach_profile.languages:
                    coach_profile.onboarding_step = 7
                    get_db().session.commit()
                    return redirect(url_for('coach_onboarding', step=7))
                else:
                    flash('You must add at least one language to continue.', 'error')

        return render_template('onboarding/coach_step6.html', form=form, step=step, coach_profile=coach_profile)

    elif step == 7:
        form = CoachStep7Form()
        # Pre-populate form with existing data
        if coach_profile.coach_title:
            form.coach_title.data = coach_profile.coach_title
        if coach_profile.bio:
            form.bio.data = coach_profile.bio
            
        if form.validate_on_submit():
            coach_profile.coach_title = form.coach_title.data
            coach_profile.bio = form.bio.data
            coach_profile.onboarding_step = 8
            get_db().session.commit()
            return redirect(url_for('coach_onboarding', step=8))
        return render_template('onboarding/coach_step7.html', form=form, step=step)

    elif step == 8:
        form = CoachStep8Form()
        # Pre-populate form with existing data
        if coach_profile.country:
            form.country.data = coach_profile.country
        if coach_profile.phone_number:
            form.phone_number.data = coach_profile.phone_number
        if coach_profile.date_of_birth:
            form.date_of_birth.data = coach_profile.date_of_birth
        if coach_profile.hourly_rate:
            form.hourly_rate.data = coach_profile.hourly_rate
            
        if form.validate_on_submit():
            # Handle profile picture upload
            if form.profile_picture.data:
                profile_picture_path = save_profile_picture(form.profile_picture.data)
                if profile_picture_path:
                    coach_profile.profile_picture = profile_picture_path

            coach_profile.country = form.country.data
            coach_profile.phone_number = form.phone_number.data
            coach_profile.date_of_birth = form.date_of_birth.data
            coach_profile.hourly_rate = form.hourly_rate.data
            coach_profile.onboarding_step = 9
            get_db().session.commit()
            return redirect(url_for('coach_onboarding', step=9))
        return render_template('onboarding/coach_step8.html', form=form, step=step, coach_profile=coach_profile)

    elif step == 9:
        # Review step
        form = CoachStep9Form()
        if form.validate_on_submit():
            # Submit for approval
            coach_profile.onboarding_step = 10
            get_db().session.commit()
            return redirect(url_for('coach_pending'))
        return render_template('onboarding/coach_step9.html', coach=coach_profile, step=step, form=form)

    return redirect(url_for('coach_onboarding', step=1))

@app.route('/coach/pending')
@login_required
@coach_required
def coach_pending():
    return render_template('onboarding/coach_pending.html')

@app.route('/student/onboarding', methods=['GET', 'POST'])
@login_required
def student_onboarding():
    user = get_current_user()
    
    # Check if user is a student
    if not user.is_student:
        flash('This onboarding is for students only.', 'error')
        return redirect(url_for('role_selection'))
    
    # Check if profile already exists
    if user.student_profile:
        flash('Your student profile is already complete.', 'info')
        return redirect(url_for('student_dashboard'))
    
    form = StudentOnboardingForm()

    if form.validate_on_submit():
        # Get languages data from the hidden input
        languages_data = request.form.get('languages_data', '[]')
        try:
            languages = json.loads(languages_data)
        except (json.JSONDecodeError, TypeError):
            languages = []

        # Validate that at least one language is provided
        if not languages:
            flash('Please add at least one language with proficiency level.', 'error')
            return render_template('onboarding/student_onboarding.html', form=form)

        # Handle profile picture upload
        profile_picture_path = None
        if form.profile_picture.data:
            profile_picture_path = save_profile_picture(form.profile_picture.data)

        student_profile = StudentProfile(
            user_id=user.id,
            bio=form.bio.data,
            age=form.age.data,
            country=form.country.data,
            profile_picture=profile_picture_path,
            is_approved=True  # Auto-approve students
        )
        get_db().session.add(student_profile)
        get_db().session.flush()  # Get the profile ID

        # Add languages
        for lang_data in languages:
            if 'language' in lang_data and 'proficiency' in lang_data:
                student_language = StudentLanguage(
                    student_profile_id=student_profile.id,
                    language=lang_data['language'],
                    proficiency=lang_data['proficiency']
                )
                get_db().session.add(student_language)

        get_db().session.commit()

        flash('Profile created successfully!', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('onboarding/student_onboarding.html', form=form)

@app.route('/student/languages', methods=['GET', 'POST'])
@login_required
@student_required
def student_languages():
    user = get_current_user()
    student_profile = user.student_profile

    if not student_profile:
        flash('Please complete your profile first.', 'error')
        return redirect(url_for('student_onboarding'))

    form = StudentLanguageForm()

    if form.validate_on_submit():
        # Check if language already exists for this student
        existing_language = StudentLanguage.query.filter_by(
            student_profile_id=student_profile.id,
            language=form.language.data
        ).first()

        if existing_language:
            flash('You have already added this language. Please edit it instead.', 'error')
        else:
            language = StudentLanguage(
                student_profile_id=student_profile.id,
                language=form.language.data,
                proficiency=form.proficiency.data
            )
            get_db().session.add(language)
            get_db().session.commit()
            flash('Language added successfully!', 'success')

        return redirect(url_for('student_languages'))

    languages = StudentLanguage.query.filter_by(student_profile_id=student_profile.id).all()
    return render_template('student/languages.html', form=form, languages=languages)

@app.route('/student/languages/<int:language_id>/delete', methods=['POST'])
@login_required
@student_required
def delete_student_language(language_id):
    user = get_current_user()
    student_profile = user.student_profile

    language = StudentLanguage.query.filter_by(
        id=language_id,
        student_profile_id=student_profile.id
    ).first()

    if language:
        get_db().session.delete(language)
        get_db().session.commit()
        flash('Language removed successfully!', 'success')
    else:
        flash('Language not found.', 'error')

    return redirect(url_for('student_languages'))

@app.route('/student/languages/<int:language_id>/edit', methods=['GET', 'POST'])
@login_required
@student_required
def edit_student_language(language_id):
    user = get_current_user()
    student_profile = user.student_profile

    language = StudentLanguage.query.filter_by(
        id=language_id,
        student_profile_id=student_profile.id
    ).first()

    if not language:
        flash('Language not found.', 'error')
        return redirect(url_for('student_languages'))

    form = StudentLanguageForm()

    if form.validate_on_submit():
        # Check if another language with same name exists
        existing_language = StudentLanguage.query.filter_by(
            student_profile_id=student_profile.id,
            language=form.language.data
        ).filter(StudentLanguage.id != language_id).first()

        if existing_language:
            flash('You already have this language. Please choose a different one.', 'error')
        else:
            language.language = form.language.data
            language.proficiency = form.proficiency.data
            get_db().session.commit()
            flash('Language updated successfully!', 'success')
            return redirect(url_for('student_languages'))

    # Pre-populate form with existing data
    if request.method == 'GET':
        form.language.data = language.language
        form.proficiency.data = language.proficiency

    return render_template('student/edit_language.html', form=form, language=language)

# Dashboard Routes
@app.route('/dashboard')
@login_required
def dashboard():
    """Smart dashboard router that redirects to appropriate role dashboard"""
    user = get_current_user()

    # If user doesn't have current_role set, set it
    if not user.current_role:
        user.set_initial_role()
        get_db().session.commit()

    # Use the helper function to get the appropriate redirect URL
    redirect_url = get_onboarding_redirect_url(user)
    return redirect(redirect_url)

@app.route('/coach/dashboard')
@login_required
@coach_required
@profile_completion_required
def coach_dashboard():
    from datetime import datetime
    
    user = get_current_user()
    coach_profile = user.coach_profile

    if not coach_profile.is_approved:
        return redirect(url_for('coach_pending'))

    # Get job recommendations
    all_requests = LearningRequest.query.filter_by(is_active=True).all()

    # Calculate match scores and sort
    best_matches = []
    for request in all_requests:
        score = calculate_match_score(coach_profile, request)
        if score > 0:
            best_matches.append((request, score))

    best_matches.sort(key=lambda x: x[1], reverse=True)
    best_matches = [item[0] for item in best_matches[:5]]

    # Get recent requests
    recent_requests = LearningRequest.query.filter_by(is_active=True).order_by(LearningRequest.created_at.desc()).limit(5).all()

    # Get saved jobs
    saved_jobs = get_db().session.query(LearningRequest).join(SavedJob).filter(
        SavedJob.coach_id == user.id
    ).limit(5).all()

    # Get active contracts with enhanced query - show active, accepted, and pending contracts
    try:
        active_contracts = Contract.query.filter(
            Contract.coach_id == user.id,
            Contract.status.in_(['active', 'accepted', 'pending'])
        ).options(
            db.joinedload(Contract.proposal),
            db.joinedload(Contract.student).joinedload(User.student_profile)
        ).all()
    except Exception as e:
        print(f"Error fetching contracts for coach {user.id}: {e}")
        active_contracts = []
    
    # Get upcoming sessions with enhanced query
    try:
        upcoming_sessions = Session.query.join(Proposal).join(Contract).filter(
            Contract.coach_id == user.id,
            Session.status == 'scheduled',
            Session.scheduled_at > datetime.utcnow()
        ).options(
            db.joinedload(Session.proposal).joinedload(Proposal.contracts),
            db.joinedload(Session.proposal).joinedload(Proposal.student).joinedload(User.student_profile)
        ).order_by(Session.scheduled_at).limit(5).all()
    except Exception:
        upcoming_sessions = []

    # Get dashboard stats
    stats = get_dashboard_stats(user)
    
    # Calculate active students count (students with active contracts)
    try:
        active_students_count = db.session.query(User.id).join(Contract, Contract.student_id == User.id).filter(
            Contract.coach_id == user.id,
            Contract.status.in_(['active', 'accepted'])
        ).distinct().count()
    except Exception as e:
        print(f"Error calculating active students count: {e}")
        active_students_count = 0

    # Get notifications for the coach
    try:
        from models import Notification
        notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(10).all()
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        notifications = []

    return render_template('dashboard/coach_dashboard.html',
                         best_matches=best_matches,
                         recent_requests=recent_requests,
                         saved_jobs=saved_jobs,
                         active_contracts=active_contracts,
                         upcoming_sessions=upcoming_sessions,
                         stats=stats,
                         coach_profile=coach_profile,
                         active_students_count=active_students_count,
                         notifications=notifications)

@app.route('/student/dashboard')
@login_required
@student_required
@profile_completion_required
def student_dashboard():
    from datetime import datetime
    
    user = get_current_user()

    # Get user's learning requests
    learning_requests = LearningRequest.query.filter_by(student_id=user.id).order_by(LearningRequest.created_at.desc()).all()
    
    # Get active contracts with enhanced query - show active, accepted, and pending contracts
    try:
        active_contracts = Contract.query.filter(
            Contract.student_id == user.id,
            Contract.status.in_(['active', 'accepted', 'pending'])
        ).options(
            db.joinedload(Contract.proposal),
            db.joinedload(Contract.coach).joinedload(User.coach_profile)
        ).all()
    except Exception as e:
        print(f"Error fetching contracts for student {user.id}: {e}")
        active_contracts = []
    
    # Get upcoming sessions with enhanced query
    try:
        upcoming_sessions = Session.query.join(Proposal).join(Contract).filter(
            Contract.student_id == user.id,
            Session.status == 'scheduled',
            Session.scheduled_at > datetime.utcnow()
        ).options(
            db.joinedload(Session.proposal).joinedload(Proposal.coach).joinedload(User.coach_profile)
        ).order_by(Session.scheduled_at).limit(5).all()
    except Exception:
        upcoming_sessions = []

    # Get dashboard stats
    stats = get_dashboard_stats(user)

    return render_template('dashboard/student_dashboard.html',
                         learning_requests=learning_requests,
                         active_contracts=active_contracts,
                         upcoming_sessions=upcoming_sessions,
                         stats=stats,
                         student=user.student_profile)

@app.route('/browse-coaches')
@login_required
@student_required
def browse_coaches():
    user = get_current_user()

    # Get filters from query parameters
    search = request.args.get('search', '')
    price_range = request.args.get('price_range', '')
    location = request.args.get('location', '')
    language = request.args.get('language', '')
    skill_tags = request.args.get('skill_tags', '')
    specialties = request.args.get('specialties', '')
    experience = request.args.get('experience', '')
    sort = request.args.get('sort', 'top')

    # Build query for approved coaches
    query = CoachProfile.query.filter_by(is_approved=True)

    # Search functionality - search in coach title, bio, and skills (case-insensitive)
    if search:
        search_term = f"%{search}%"
        # Join with User table to access user information
        query = query.join(User).filter(
            get_db().or_(
                CoachProfile.coach_title.ilike(search_term),
                CoachProfile.bio.ilike(search_term),
                CoachProfile.skills.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term)
            )
        )

    # Language filter - search in coach languages
    if language:
        # Join with Language table to filter by language
        query = query.join(Language).filter(Language.language == language)

    # Skill tags filter - search in coach skills
    if skill_tags:
        skill_terms = [skill.strip() for skill in skill_tags.split(',')]
        skill_filters = []
        for skill in skill_terms:
            if skill:
                skill_term = f"%{skill}%"
                skill_filters.append(CoachProfile.skills.ilike(skill_term))
        
        if skill_filters:
            # Ensure we have the User join for the query
            if not search and not language:  # Only join if not already joined
                query = query.join(User)
            query = query.filter(get_db().or_(*skill_filters))

    # Price range filter
    if price_range:
        if price_range == '10-25':
            query = query.filter(CoachProfile.hourly_rate.between(10, 25))
        elif price_range == '25-50':
            query = query.filter(CoachProfile.hourly_rate.between(25, 50))
        elif price_range == '50-100':
            query = query.filter(CoachProfile.hourly_rate.between(50, 100))
        elif price_range == '100+':
            query = query.filter(CoachProfile.hourly_rate >= 100)

    # Location filter (if you have location data in your model)
    # if location:
    #     query = query.filter(CoachProfile.location == location)

    # Specialties filter - search in coach title, bio, and skills (case-insensitive)
    if specialties:
        specialty_term = f"%{specialties}%"
        # Ensure we have the User join for the query
        if not search and not language and not skill_tags:  # Only join if not already joined
            query = query.join(User)
        query = query.filter(
            get_db().or_(
                CoachProfile.coach_title.ilike(specialty_term),
                CoachProfile.bio.ilike(specialty_term),
                CoachProfile.skills.ilike(specialty_term)
            )
        )

    # Experience level filter (if you have experience data in your model)
    # if experience:
    #     query = query.filter(CoachProfile.experience_years >= experience_min)

    # Sorting
    if sort == 'rating':
        query = query.order_by(CoachProfile.rating.desc())
    elif sort == 'price_low':
        query = query.order_by(CoachProfile.hourly_rate.asc())
    elif sort == 'price_high':
        query = query.order_by(CoachProfile.hourly_rate.desc())
    elif sort == 'recent':
        query = query.order_by(CoachProfile.created_at.desc())
    else:  # 'top' - default sorting
        query = query.order_by(CoachProfile.rating.desc(), CoachProfile.hourly_rate.asc())

    coaches = query.all()

    # Determine the header text based on search/filters
    header_text = "Discover coaches"
    if search:
        header_text = f"Discover {search} coaches"
    elif skill_tags:
        header_text = f"Discover {skill_tags} coaches"
    elif language:
        header_text = f"Discover {language} coaches"

    return render_template('coaches/browse_coaches.html', 
                         coaches=coaches, 
                         header_text=header_text,
                         search_term=search,
                         skill_tags_filter=skill_tags,
                         language_filter=language)

# Job and Request Routes
@app.route('/find-work')
@login_required
@coach_required
def find_work():
    user = get_current_user()

    # Get filters from query parameters
    experience_level = request.args.get('experience_level', '')
    keywords = request.args.get('keywords', '')

    # Build query
    query = LearningRequest.query.filter_by(is_active=True)

    if experience_level:
        query = query.filter(LearningRequest.experience_level == experience_level)

    if keywords:
        query = query.filter(LearningRequest.description.contains(keywords))

    learning_requests = query.order_by(LearningRequest.created_at.desc()).all()

    return render_template('jobs/find_work.html', learning_requests=learning_requests)

@app.route('/job/<int:job_id>')
@login_required
def job_details(job_id):
    learning_request = LearningRequest.query.get_or_404(job_id)
    user = get_current_user()

    # Check if user has already submitted a proposal
    existing_proposal = None
    if user.is_coach:
        existing_proposal = Proposal.query.filter_by(
            learning_request_id=job_id,
            coach_id=user.id
        ).first()

    # Check if job is saved
    is_saved = False
    if user.is_coach:
        is_saved = SavedJob.query.filter_by(
            coach_id=user.id,
            learning_request_id=job_id
        ).first() is not None

    # Get all proposals for this learning request
    proposals = Proposal.query.filter_by(learning_request_id=job_id).order_by(Proposal.created_at.desc()).all()

    # Create proposal form for coaches
    proposal_form = None
    if user and user.is_coach:
        proposal_form = create_dynamic_proposal_form(learning_request)

    return render_template('jobs/job_details.html',
                         learning_request=learning_request,
                         existing_proposal=existing_proposal,
                         is_saved=is_saved,
                         proposals=proposals,
                         proposal_form=proposal_form)

@app.route('/edit-job/<int:job_id>', methods=['GET', 'POST'])
@login_required
@student_required
def edit_job(job_id):
    learning_request = LearningRequest.query.get_or_404(job_id)

    # Verify that the current user owns this learning request
    if learning_request.student_id != session['user_id']:
        flash('You do not have permission to edit this job post.', 'error')
        return redirect(url_for('student_dashboard'))

    form = LearningRequestForm(obj=learning_request)

    # Load existing screening questions
    screening_questions = ScreeningQuestion.query.filter_by(
        learning_request_id=job_id
    ).order_by(ScreeningQuestion.order_index).all()

    if request.method == 'GET':
        # Pre-populate screening question fields
        for i, question in enumerate(screening_questions[:5]):  # Max 5 questions
            field_name = f'screening_question_{i + 1}'
            if hasattr(form, field_name):
                getattr(form, field_name).data = question.question_text

    if form.validate_on_submit():
        # Update learning request
        learning_request.title = form.title.data
        learning_request.description = form.description.data
        learning_request.skills_needed = form.skills_needed.data
        learning_request.duration = form.duration.data
        learning_request.budget = form.budget.data
        learning_request.experience_level = form.experience_level.data
        learning_request.skill_type = form.skill_type.data

        # Delete existing screening questions
        ScreeningQuestion.query.filter_by(learning_request_id=job_id).delete()

        # Handle screening questions (optional)
        screening_questions_data = [
            form.screening_question_1.data,
            form.screening_question_2.data,
            form.screening_question_3.data,
            form.screening_question_4.data,
            form.screening_question_5.data
        ]

        # Save non-empty screening questions to database
        order_index = 1
        for question_text in screening_questions_data:
            if question_text and question_text.strip():
                screening_question = ScreeningQuestion(
                    learning_request_id=learning_request.id,
                    question_text=question_text.strip(),
                    order_index=order_index
                )
                get_db().session.add(screening_question)
                order_index += 1

        get_db().session.commit()

        flash('Job post updated successfully!', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('jobs/edit_request.html', form=form, learning_request=learning_request)

@app.route('/job-management/<int:job_id>')
@login_required
@student_required
def job_management(job_id):
    learning_request = LearningRequest.query.get_or_404(job_id)

    # Verify that the current user owns this learning request
    if learning_request.student_id != session['user_id']:
        flash('You do not have permission to view this job post.', 'error')
        return redirect(url_for('student_dashboard'))

    # Get all proposals for this learning request
    proposals = Proposal.query.filter_by(learning_request_id=job_id).order_by(Proposal.created_at.desc()).all()

    return render_template('jobs/job_management.html',
                         learning_request=learning_request,
                         proposals=proposals)

@app.route('/post-request', methods=['GET', 'POST'])
@login_required
@student_required
def post_request():
    form = LearningRequestForm()

    if form.validate_on_submit():
        learning_request = LearningRequest(
            student_id=session['user_id'],
            title=form.title.data,
            description=form.description.data,
            skills_needed=form.skills_needed.data,
            duration=form.duration.data,
            budget=form.budget.data,
            experience_level=form.experience_level.data,
            skill_type=form.skill_type.data
        )

        get_db().session.add(learning_request)
        get_db().session.commit()

        # Handle screening questions (optional)
        screening_questions = [
            form.screening_question_1.data,
            form.screening_question_2.data,
            form.screening_question_3.data,
            form.screening_question_4.data,
            form.screening_question_5.data
        ]

        # Save non-empty screening questions to database
        order_index = 1
        for question_text in screening_questions:
            if question_text and question_text.strip():
                screening_question = ScreeningQuestion(
                    learning_request_id=learning_request.id,
                    question_text=question_text.strip(),
                    order_index=order_index
                )
                get_db().session.add(screening_question)
                order_index += 1

        get_db().session.commit()

        flash('Learning request posted successfully!', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('jobs/post_request.html', form=form)

@app.route('/api/post-request', methods=['POST'])
@login_required
@student_required
def api_post_request():
    """API endpoint for async job posting"""
    try:
        form = LearningRequestForm()

        if form.validate_on_submit():
            learning_request = LearningRequest(
                student_id=session['user_id'],
                title=form.title.data,
                description=form.description.data,
                skills_needed=form.skills_needed.data,
                duration=form.duration.data,
                budget=form.budget.data,
                experience_level=form.experience_level.data,
                skill_type=form.skill_type.data
            )

            get_db().session.add(learning_request)
            get_db().session.commit()

            # Handle screening questions (optional)
            screening_questions = [
                form.screening_question_1.data,
                form.screening_question_2.data,
                form.screening_question_3.data,
                form.screening_question_4.data,
                form.screening_question_5.data
            ]

            # Save non-empty screening questions to database
            order_index = 1
            for question_text in screening_questions:
                if question_text and question_text.strip():
                    screening_question = ScreeningQuestion(
                        learning_request_id=learning_request.id,
                        question_text=question_text.strip(),
                        order_index=order_index
                    )
                    get_db().session.add(screening_question)
                    order_index += 1

            get_db().session.commit()

            return jsonify({
                'success': True,
                'message': '✅ Your learning request has been posted.',
                'redirect_url': url_for('student_dashboard')
            })
        else:
            # Return form validation errors
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = field_errors

            return jsonify({
                'success': False,
                'message': 'Please fix the errors below.',
                'errors': errors
            }), 400

    except Exception as e:
        get_db().session.rollback()
        app.logger.error(f"Error posting learning request: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while posting your request. Please try again.'
        }), 500

@app.route('/submit-proposal/<int:job_id>', methods=['POST'])
@login_required
@coach_required
def submit_proposal(job_id):
    try:
        learning_request = LearningRequest.query.get_or_404(job_id)
        form = create_dynamic_proposal_form(learning_request)

        if form.validate_on_submit():
            # Validate required data
            if not form.session_count.data or not form.price_per_session.data:
                flash('Session count and price per session are required.', 'error')
                return redirect(url_for('job_details', job_id=job_id))

            total_price = form.session_count.data * form.price_per_session.data

            proposal = Proposal(
                learning_request_id=job_id,
                coach_id=session['user_id'],
                cover_letter=form.cover_letter.data,
                session_count=form.session_count.data,
                price_per_session=form.price_per_session.data,
                session_duration=form.session_duration.data,
                total_price=total_price
            )

            get_db().session.add(proposal)
            get_db().session.flush()  # Get the proposal.id before committing

            # Handle screening question answers
            screening_questions = ScreeningQuestion.query.filter_by(
                learning_request_id=job_id
            ).order_by(ScreeningQuestion.order_index).all()

            for question in screening_questions:
                field_name = f'screening_answer_{question.id}'
                if hasattr(form, field_name):
                    answer_text = getattr(form, field_name).data
                    if answer_text and answer_text.strip():
                        screening_answer = ScreeningAnswer(
                            proposal_id=proposal.id,
                            screening_question_id=question.id,
                            answer_text=answer_text.strip()
                        )
                        get_db().session.add(screening_answer)

            get_db().session.commit()

            flash('Proposal submitted successfully!', 'success')
            return redirect(url_for('job_details', job_id=job_id))
        else:
            # Log form validation errors for debugging
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")

            if error_messages:
                flash(f'Form validation failed: {"; ".join(error_messages)}', 'error')
            else:
                flash('Please fill out all required fields.', 'error')

            return redirect(url_for('job_details', job_id=job_id))

    except Exception as e:
        get_db().session.rollback()
        app.logger.error(f"Error submitting proposal: {str(e)}")
        flash('An error occurred while submitting your proposal. Please try again.', 'error')
        return redirect(url_for('job_details', job_id=job_id))

@app.route('/save-job/<int:job_id>')
@login_required
@coach_required
def save_job(job_id):
    existing_save = SavedJob.query.filter_by(
        coach_id=session['user_id'],
        learning_request_id=job_id
    ).first()

    if not existing_save:
        saved_job = SavedJob(
            coach_id=session['user_id'],
            learning_request_id=job_id
        )
        get_db().session.add(saved_job)
        get_db().session.commit()
        flash('Job saved!', 'success')
    else:
        flash('Job already saved!', 'info')

    return redirect(url_for('job_details', job_id=job_id))

@app.route('/accept-proposal/<int:proposal_id>', methods=['POST'])
@login_required
@student_required
def accept_proposal(proposal_id):
    proposal = Proposal.query.get_or_404(proposal_id)
    learning_request = LearningRequest.query.get_or_404(proposal.learning_request_id)

    # Verify that the current user owns this learning request
    if learning_request.student_id != session['user_id']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'You do not have permission to accept this proposal.'}), 403
        flash('You do not have permission to accept this proposal.', 'error')
        return redirect(url_for('student_dashboard'))

    try:
        # Start database transaction
        db = get_db()
        
        # Update proposal status
        proposal.status = 'accepted'
        proposal.accepted_at = datetime.utcnow()

        # Reject all other proposals for this learning request
        other_proposals = Proposal.query.filter_by(
            learning_request_id=proposal.learning_request_id
        ).filter(Proposal.id != proposal_id).all()

        for other_proposal in other_proposals:
            if other_proposal.status == 'pending':
                other_proposal.status = 'rejected'

        # Mark learning request as inactive since it's been accepted
        learning_request.is_active = False

        db.session.commit()

        # Send notification message to coach
        notification_message = Message(
            sender_id=learning_request.student_id,
            recipient_id=proposal.coach_id,
            content=f"🎉 Great news! Your proposal for '{learning_request.title}' has been accepted! The student would like to discuss the next steps. You can now chat and schedule a 15-minute call to discuss the contract details.",
            sender_role='student',
            recipient_role='coach'
        )
        db.session.add(notification_message)
        
        # Create notification for coach (only if table exists)
        try:
            from sqlalchemy import text
            # Check if notification table exists
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'notification'
                );
            """))
            table_exists = result.scalar()
            
            if table_exists:
                from notification_utils import create_job_notification
                create_job_notification(learning_request, 'job_accepted', proposal)
        except Exception as e:
            # Silently ignore notification errors - don't break the main flow
            pass
        
        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True, 
                'message': 'Proposal accepted successfully! You can now chat with the coach and create a contract.',
                'proposal_id': proposal_id,
                'status': 'accepted',
                'coach_id': proposal.coach_id,
                'redirect_url': url_for('conversation', user_id=proposal.coach_id)
            })
        
        flash('Proposal accepted successfully! You can now chat with the coach and create a contract.', 'success')
        return redirect(url_for('conversation', user_id=proposal.coach_id))
        
    except Exception as e:
        db = get_db()
        db.session.rollback()
        app.logger.error(f"Error accepting proposal: {str(e)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'An error occurred while accepting the proposal.'}), 500
        
        flash('An error occurred while accepting the proposal. Please try again.', 'error')
        return redirect(url_for('job_details', job_id=learning_request.id))

@app.route('/reject-proposal/<int:proposal_id>', methods=['POST'])
@login_required
@student_required
def reject_proposal(proposal_id):
    proposal = Proposal.query.get_or_404(proposal_id)
    learning_request = LearningRequest.query.get_or_404(proposal.learning_request_id)

    # Verify that the current user owns this learning request
    if learning_request.student_id != session['user_id']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'You do not have permission to reject this proposal.'}), 403
        flash('You do not have permission to reject this proposal.', 'error')
        return redirect(url_for('student_dashboard'))

    try:
        # Update proposal status
        proposal.status = 'rejected'
        db = get_db()
        
        # Create notification for coach (only if table exists)
        try:
            from sqlalchemy import text
            # Check if notification table exists
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'notification'
                );
            """))
            table_exists = result.scalar()
            
            if table_exists:
                from notification_utils import create_job_notification
                create_job_notification(learning_request, 'job_rejected', proposal)
        except Exception as e:
            # Silently ignore notification errors - don't break the main flow
            pass
        
        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True, 
                'message': 'Proposal rejected.',
                'proposal_id': proposal_id,
                'status': 'rejected'
            })
        
        flash('Proposal rejected.', 'info')
        return redirect(url_for('job_details', job_id=learning_request.id))
        
    except Exception as e:
        db = get_db()
        db.session.rollback()
        app.logger.error(f"Error rejecting proposal: {str(e)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'An error occurred while rejecting the proposal.'}), 500
        
        flash('An error occurred while rejecting the proposal. Please try again.', 'error')
        return redirect(url_for('job_details', job_id=learning_request.id))

# Add these new API routes for better error handling
@app.route('/api/proposal/<int:proposal_id>/accept', methods=['POST'])
@login_required
@student_required
def api_accept_proposal(proposal_id):
    """API-only route for accepting proposals with better error handling"""
    try:
        proposal = Proposal.query.get_or_404(proposal_id)
        learning_request = LearningRequest.query.get_or_404(proposal.learning_request_id)

        # Verify ownership
        if learning_request.student_id != session['user_id']:
            return jsonify({'success': False, 'error': 'Unauthorized access.'}), 403

        # Check if proposal is still pending
        if proposal.status != 'pending':
            return jsonify({'success': False, 'error': 'This proposal has already been processed.'}), 400

        db = get_db()
        
        # Update proposal status
        proposal.status = 'accepted'

        # Reject other proposals
        other_proposals = Proposal.query.filter(
            Proposal.learning_request_id == proposal.learning_request_id,
            Proposal.id != proposal_id,
            Proposal.status == 'pending'
        ).all()

        for other_proposal in other_proposals:
            other_proposal.status = 'rejected'

        # Mark learning request as inactive
        learning_request.is_active = False

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Proposal accepted successfully!',
            'proposal_id': proposal_id,
            'status': 'accepted',
            'coach_id': proposal.coach_id,
            'redirect_url': url_for('job_details', job_id=learning_request.id)
        })

    except Exception as e:
        db = get_db()
        db.session.rollback()
        app.logger.error(f"API Error accepting proposal {proposal_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Server error occurred.'}), 500

@app.route('/api/proposal/<int:proposal_id>/reject', methods=['POST'])
@login_required
@student_required  
def api_reject_proposal(proposal_id):
    """API-only route for rejecting proposals"""
    try:
        proposal = Proposal.query.get_or_404(proposal_id)
        learning_request = LearningRequest.query.get_or_404(proposal.learning_request_id)

        # Verify ownership
        if learning_request.student_id != session['user_id']:
            return jsonify({'success': False, 'error': 'Unauthorized access.'}), 403

        # Check if proposal is still pending
        if proposal.status != 'pending':
            return jsonify({'success': False, 'error': 'This proposal has already been processed.'}), 400

        db = get_db()
        proposal.status = 'rejected'
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Proposal rejected.',
            'proposal_id': proposal_id,
            'status': 'rejected'
        })

    except Exception as e:
        db = get_db()
        db.session.rollback()
        app.logger.error(f"API Error rejecting proposal {proposal_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Server error occurred.'}), 500

# Profile Routes
@app.route('/coach/<int:coach_id>')
def coach_profile(coach_id):
    coach = User.query.get_or_404(coach_id)
    if not coach.is_coach or not coach.coach_profile:
        flash('Coach profile not found.', 'error')
        return redirect(url_for('index'))

    # Check if current user can view this profile
    current_user = get_current_user()
    can_view = True

    # If the profile is not approved, only admin and the coach themselves can view
    if not coach.coach_profile.is_approved:
        if not current_user or (current_user.id != coach.id and 'admin_logged_in' not in session):
            can_view = False

    if not can_view:
        flash('This coach profile is not available.', 'error')
        return redirect(url_for('index'))

    return render_template('profile/coach_profile.html', coach=coach)

@app.route('/student/<int:student_id>')
@login_required
def student_profile(student_id):
    student = User.query.get_or_404(student_id)
    current_user = get_current_user()

    if not student.is_student or not student.student_profile:
        flash('Student profile not found.', 'error')
        return redirect(url_for('index'))

    # Only coaches who are hired (accepted proposals) can view student profiles
    if current_user.is_coach:
        from utils import coach_can_access_student
        if not coach_can_access_student(current_user.id, student_id):
            flash('Access denied. Student profiles are private and only accessible to hired coaches.', 'error')
            return redirect(url_for('find_work'))
    elif current_user.id != student_id:
        # Students can only view their own profile
        flash('Access denied.', 'error')
        return redirect(url_for('student_dashboard'))

    return render_template('profile/student_profile.html', student=student)

@app.route('/account-settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    """Account settings page for email, password, and account management"""
    user = get_current_user()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'change_email':
            new_email = request.form.get('new_email', '').strip()
            password = request.form.get('password', '')

            if not new_email or not password:
                flash('Please fill in all fields.', 'error')
                return redirect(url_for('account_settings'))

            if not user.check_password(password):
                flash('Incorrect password.', 'error')
                return redirect(url_for('account_settings'))

            # Check if new email is the same as current email
            if new_email.lower() == user.email.lower():
                flash('New email address must be different from your current email.', 'error')
                return redirect(url_for('account_settings'))

            # Check if email is already taken
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user and existing_user.id != user.id:
                flash('Email is already registered by another user.', 'error')
                return redirect(url_for('account_settings'))

            # Check if user already has a pending email change
            if user.new_email and user.email_change_token:
                flash('You already have a pending email change. Please check your email or wait for the current request to expire.', 'error')
                return redirect(url_for('account_settings'))

            # Send email change verification
            from email_utils import send_email_change_verification
            if send_email_change_verification(user, new_email):
                flash('Email change verification sent to your new email address. Please check your inbox and click the verification link to complete the change.', 'success')
            else:
                flash('Failed to send email change verification. Please try again later.', 'error')
            
            return redirect(url_for('account_settings'))

        elif action == 'change_password':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not current_password or not new_password or not confirm_password:
                flash('Please fill in all password fields.', 'error')
                return redirect(url_for('account_settings'))

            if not user.check_password(current_password):
                flash('Current password is incorrect.', 'error')
                return redirect(url_for('account_settings'))

            if new_password != confirm_password:
                flash('New password and confirm password do not match.', 'error')
                return redirect(url_for('account_settings'))

            if user.check_password(new_password):
                flash('New password must be different from your current password.', 'error')
                return redirect(url_for('account_settings'))

            # Password validation
            if len(new_password) < 8:
                flash('Password must be at least 8 characters long.', 'error')
                return redirect(url_for('account_settings'))

            # Check for at least one uppercase, one lowercase, one number, and one special character
            import re
            if not re.search(r'[A-Z]', new_password):
                flash('Password must contain at least one uppercase letter.', 'error')
                return redirect(url_for('account_settings'))
            
            if not re.search(r'[a-z]', new_password):
                flash('Password must contain at least one lowercase letter.', 'error')
                return redirect(url_for('account_settings'))
            
            if not re.search(r'\d', new_password):
                flash('Password must contain at least one number.', 'error')
                return redirect(url_for('account_settings'))
            
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                flash('Password must contain at least one special character.', 'error')
                return redirect(url_for('account_settings'))

            # Update password
            user.set_password(new_password)
            get_db().session.commit()
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('account_settings'))

        elif action == 'delete_account':
            print(f"DEBUG: Delete account action triggered for user {user.id}")
            password = request.form.get('delete_password', '')

            if not password:
                print("DEBUG: No password provided")
                flash('Please enter your password to confirm account deletion.', 'error')
                return redirect(url_for('account_settings'))

            if not user.check_password(password):
                print("DEBUG: Incorrect password provided")
                flash('Incorrect password.', 'error')
                return redirect(url_for('account_settings'))

            print(f"DEBUG: Password verified, attempting to delete user {user.id}")
            
            try:
                # Use the safe deletion utility function
                from utils import safe_delete_user_data
                success = safe_delete_user_data(user.id)
                
                if success:
                    flash('Account deleted successfully.', 'success')
                else:
                    flash('User not found.', 'error')
                    
            except Exception as e:
                print(f"DEBUG: Error deleting user: {str(e)}")
                print(f"DEBUG: Error type: {type(e).__name__}")
                import traceback
                print(f"DEBUG: Full traceback: {traceback.format_exc()}")
                get_db().session.rollback()
                flash(f'An error occurred while deleting your account: {str(e)}', 'error')
                return redirect(url_for('account_settings'))
        
        session.clear()
        flash('Your account has been deleted successfully.', 'info')
        return redirect(url_for('index'))

    return render_template('profile/account_settings.html', user=user)

@app.route('/update-timezone', methods=['POST'])
@login_required
def update_timezone():
    """Update user's timezone preference"""
    try:
        user = get_current_user()
        timezone = request.form.get('timezone', 'UTC')
        
        # Validate timezone
        available_timezones = [tz[0] for tz in get_available_timezones()]
        if timezone not in available_timezones:
            flash('Invalid timezone selected.', 'error')
            return redirect(url_for('account_settings'))
        
        # Update timezone (only if column exists)
        try:
            if hasattr(user, 'timezone'):
                user.timezone = timezone
                get_db().session.commit()
                flash('Timezone updated successfully!', 'success')
            else:
                flash('Timezone feature not available yet. Please try again later.', 'warning')
        except Exception as e:
            # Column doesn't exist yet
            flash('Timezone feature not available yet. Please try again later.', 'warning')
        
        return redirect(url_for('account_settings'))
    except Exception as e:
        flash('Error updating timezone. Please try again later.', 'error')
        return redirect(url_for('account_settings'))



@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Redirect to role-specific edit profile page based on current role"""
    user = get_current_user()

    # Redirect to role-specific edit profile page
    if user.current_role == 'coach':
        return redirect(url_for('edit_coach_profile'))
    elif user.current_role == 'student':
        return redirect(url_for('edit_student_profile'))
    else:
        # Fallback for users without current_role set
        if user.is_coach:
            return redirect(url_for('edit_coach_profile'))
        elif user.is_student:
            return redirect(url_for('edit_student_profile'))
        else:
            flash('Please set up your profile first.', 'info')
            return redirect(url_for('index'))

@app.route('/edit-profile-inline', methods=['GET'])
@login_required
def edit_profile_inline():
    """Inline profile editing - shows public profile view with edit capabilities"""
    user = get_current_user()
    if not user or not user.is_coach or not user.coach_profile:
        flash('Coach access required.', 'error')
        return redirect(url_for('index'))
    
    return render_template('profile/edit_coach_profile.html', user=user)

@app.route('/api/update-profile-field', methods=['POST'])
@login_required
def api_update_profile_field():
    """API endpoint for updating individual profile fields"""
    user = get_current_user()
    if not user or not user.is_coach or not user.coach_profile:
        return jsonify({'success': False, 'error': 'Coach access required.'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
        
    field = data.get('field')
    value = data.get('value', '').strip()
    
    if not field:
        return jsonify({'success': False, 'error': 'Field is required.'}), 400
    
    try:
        # Update the appropriate field
        if field == 'coach_title':
            if len(value) < 5 or len(value) > 80:
                return jsonify({'success': False, 'error': 'Coach title must be between 5 and 80 characters.'}), 400
            user.coach_profile.coach_title = value
        elif field == 'bio':
            if len(value) < 100 or len(value) > 5000:
                return jsonify({'success': False, 'error': 'Bio must be between 100 and 5000 characters.'}), 400
            user.coach_profile.bio = value
        elif field == 'skills':
            user.coach_profile.skills = value
        elif field == 'hourly_rate':
            try:
                rate = float(value)
                if rate < 0:
                    return jsonify({'success': False, 'error': 'Hourly rate must be positive.'}), 400
                user.coach_profile.hourly_rate = rate
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid hourly rate format.'}), 400
        elif field == 'country':
            user.coach_profile.country = value
        elif field == 'phone_number':
            user.coach_profile.phone_number = value
        elif field == 'first_name':
            if not value:
                return jsonify({'success': False, 'error': 'First name is required.'}), 400
            user.first_name = value
        elif field == 'last_name':
            if not value:
                return jsonify({'success': False, 'error': 'Last name is required.'}), 400
            user.last_name = value
        else:
            return jsonify({'success': False, 'error': 'Invalid field.'}), 400
        
        get_db().session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully.'})
        
    except Exception as e:
        get_db().session.rollback()
        return jsonify({'success': False, 'error': f'Error updating profile: {str(e)}'}), 500

@app.route('/edit-coach-profile', methods=['GET', 'POST'])
@login_required
def edit_coach_profile():
    print(f"DEBUG: edit_coach_profile route called - Method: {request.method}")
    print(f"DEBUG: User ID in session: {session.get('user_id')}")
    print(f"DEBUG: Current user: {get_current_user()}")

    # Simple test - if no user, just return a test response
    user = get_current_user()
    if not user:
        print("DEBUG: No user found, returning test response")
        return "Test response - route is working"

    """Coach-specific profile editing"""

    # Ensure user has coach access
    if not user.is_coach:
        flash('Coach access required.', 'error')
        return redirect(url_for('index'))

    # Ensure user has a coach profile
    if not user.coach_profile:
        print(f"DEBUG: User {user.id} has no coach profile")
        flash('Coach profile not found. Please complete your coach onboarding first.', 'error')
        return redirect(url_for('coach_onboarding', step=1))

    if request.method == 'POST':
        print(f"DEBUG: Coach profile update POST request received for user {user.id}")
        print(f"DEBUG: Form data: {dict(request.form)}")
        print(f"DEBUG: CSRF token: {request.form.get('csrf_token')}")
        print(f"DEBUG: All form fields: {list(request.form.keys())}")
        try:
            # Update coach-specific fields
            coach_title = request.form.get('coach_title', '').strip()
            bio = request.form.get('bio', '').strip()
            skills = request.form.get('skills', '').strip()

            # Validate fields only if they are provided and not empty
            validation_errors = []

            if coach_title:  # Only validate if provided
                if len(coach_title) < 5 or len(coach_title) > 80:
                    validation_errors.append('Coach title must be between 5 and 80 characters.')

            if bio:  # Only validate if provided
                if len(bio) < 100 or len(bio) > 5000:
                    validation_errors.append('Bio must be between 100 and 5000 characters.')

            if validation_errors:
                for error in validation_errors:
                    flash(error, 'error')
                return render_template('profile/edit_coach_profile.html', user=user)

            # Update coach-specific fields
            if coach_title:
                user.coach_profile.coach_title = coach_title
            if bio:
                user.coach_profile.bio = bio
            if skills:
                user.coach_profile.skills = skills

                            # Update basic profile info
                country = request.form.get('country', '').strip()
                phone_number = request.form.get('phone_number', '').strip()
                hourly_rate = request.form.get('hourly_rate')

                if country:
                    user.coach_profile.country = country
                if phone_number:
                    user.coach_profile.phone_number = phone_number
                if hourly_rate:
                    try:
                        user.coach_profile.hourly_rate = float(hourly_rate)
                    except ValueError:
                        pass

                # Handle profile picture upload
                if 'profile_picture' in request.files:
                    profile_picture_file = request.files['profile_picture']
                    if profile_picture_file and profile_picture_file.filename:
                        print(f"DEBUG: Processing profile picture upload: {profile_picture_file.filename}")
                        try:
                            # Save the uploaded file
                            from utils import save_profile_picture
                            profile_picture_path = save_profile_picture(profile_picture_file)
                            if profile_picture_path:
                                user.coach_profile.profile_picture = profile_picture_path
                                print(f"DEBUG: Profile picture saved to: {profile_picture_path}")
                            else:
                                print("DEBUG: Failed to save profile picture")
                        except Exception as e:
                            print(f"DEBUG: Error saving profile picture: {str(e)}")
                            flash('Error uploading profile picture. Please try again.', 'error')

            # Update user's basic info
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()

            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name

            get_db().session.commit()
            print(f"DEBUG: Coach profile updated successfully for user {user.id}")
            flash('Coach profile updated successfully!', 'success')
            return redirect(url_for('edit_coach_profile'))

        except Exception as e:
            get_db().session.rollback()
            print(f"DEBUG: Error updating coach profile for user {user.id}: {str(e)}")
            flash(f'Error updating profile: {str(e)}', 'error')
            return render_template('profile/edit_coach_profile.html', user=user)

    return render_template('profile/edit_coach_profile.html', user=user)

@app.route('/edit-student-profile', methods=['GET', 'POST'])
@login_required
def edit_student_profile():
    """Student-specific profile editing"""
    user = get_current_user()

    # Ensure user has student access
    if not user.is_student:
        flash('Student access required.', 'error')
        return redirect(url_for('index'))

    # Ensure user has a student profile
    if not user.student_profile:
        flash('Student profile not found. Please complete your student onboarding first.', 'error')
        return redirect(url_for('student_onboarding'))

    if request.method == 'POST':
        try:
            # Update student bio
            bio = request.form.get('bio', '').strip()
            if bio:
                user.student_profile.bio = bio

            # Update basic profile info
            age = request.form.get('age')

            if age:
                try:
                    user.student_profile.age = int(age)
                except ValueError:
                    pass

            # Handle profile picture upload
            if 'profile_picture' in request.files:
                profile_picture_file = request.files['profile_picture']
                if profile_picture_file and profile_picture_file.filename:
                    print(f"DEBUG: Processing student profile picture upload: {profile_picture_file.filename}")
                    try:
                        # Save the uploaded file
                        from utils import save_profile_picture
                        profile_picture_path = save_profile_picture(profile_picture_file)
                        if profile_picture_path:
                            user.student_profile.profile_picture = profile_picture_path
                            print(f"DEBUG: Student profile picture saved to: {profile_picture_path}")
                        else:
                            print("DEBUG: Failed to save student profile picture")
                    except Exception as e:
                        print(f"DEBUG: Error saving student profile picture: {str(e)}")
                        flash('Error uploading profile picture. Please try again.', 'error')

            # Update user's basic info
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()

            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name

            get_db().session.commit()
            flash('Student profile updated successfully!', 'success')
            return redirect(url_for('edit_student_profile'))

        except Exception as e:
            get_db().session.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')
            return render_template('profile/edit_student_profile.html', user=user)

    return render_template('profile/edit_student_profile.html', user=user)

# Experience Management Routes
@app.route('/add-experience', methods=['GET', 'POST'])
@login_required
@coach_required
def add_experience():
    user = get_current_user()
    coach_profile = user.coach_profile

    form = CoachStep4Form()
    if form.validate_on_submit():
        experience = Experience(
            coach_profile_id=coach_profile.id,
            title=form.title.data,
            company=form.company.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_current=form.is_current.data
        )
        get_db().session.add(experience)
        get_db().session.commit()
        flash('Experience added successfully!', 'success')
        return redirect(url_for('edit_coach_profile') + '#experience')

    return render_template('profile/add_experience.html', form=form)

@app.route('/edit-experience/<int:experience_id>', methods=['GET', 'POST'])
@login_required
@coach_required
def edit_experience(experience_id):
    user = get_current_user()
    experience = Experience.query.filter_by(
        id=experience_id,
        coach_profile_id=user.coach_profile.id
    ).first_or_404()

    form = CoachStep4Form(obj=experience)
    if form.validate_on_submit():
        experience.title = form.title.data
        experience.company = form.company.data
        experience.description = form.description.data
        experience.start_date = form.start_date.data
        experience.end_date = form.end_date.data
        experience.is_current = form.is_current.data
        get_db().session.commit()
        flash('Experience updated successfully!', 'success')
        return redirect(url_for('edit_coach_profile') + '#experience')

    return render_template('profile/edit_experience.html', form=form, experience=experience)

@app.route('/delete-experience/<int:experience_id>', methods=['POST'])
@login_required
@coach_required
def delete_experience(experience_id):
    from flask_wtf import FlaskForm
    from flask import request

    # Create a simple form for CSRF validation
    form = FlaskForm()
    if not form.validate_on_submit():
        flash('Security token invalid. Please try again.', 'error')
        return redirect(url_for('edit_coach_profile') + '#experience')

    user = get_current_user()
    experience = Experience.query.filter_by(
        id=experience_id,
        coach_profile_id=user.coach_profile.id
    ).first_or_404()

    get_db().session.delete(experience)
    get_db().session.commit()
    flash('Experience deleted successfully!', 'success')
    return redirect(url_for('edit_coach_profile') + '#experience')

# Education Management Routes
@app.route('/add-education', methods=['GET', 'POST'])
@login_required
@coach_required
def add_education():
    user = get_current_user()
    coach_profile = user.coach_profile

    form = CoachStep5Form()
    if form.validate_on_submit():
        education = Education(
            coach_profile_id=coach_profile.id,
            institution=form.institution.data,
            degree=form.degree.data,
            field_of_study=form.field_of_study.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_current=form.is_current.data
        )
        get_db().session.add(education)
        get_db().session.commit()
        flash('Education added successfully!', 'success')
        return redirect(url_for('edit_coach_profile') + '#education')

    return render_template('profile/add_education.html', form=form)

@app.route('/edit-education/<int:education_id>', methods=['GET', 'POST'])
@login_required
@coach_required
def edit_education(education_id):
    user = get_current_user()
    education = Education.query.filter_by(
        id=education_id,
        coach_profile_id=user.coach_profile.id
    ).first_or_404()

    form = CoachStep5Form(obj=education)
    if form.validate_on_submit():
        education.institution = form.institution.data
        education.degree = form.degree.data
        education.field_of_study = form.field_of_study.data
        education.start_date = form.start_date.data
        education.end_date = form.end_date.data
        education.is_current = form.is_current.data
        get_db().session.commit()
        flash('Education updated successfully!', 'success')
        return redirect(url_for('edit_coach_profile') + '#education')

    return render_template('profile/edit_education.html', form=form, education=education)

@app.route('/delete-education/<int:education_id>', methods=['POST'])
@login_required
@coach_required
def delete_education(education_id):
    from flask_wtf import FlaskForm
    from flask import request

    # Create a simple form for CSRF validation
    form = FlaskForm()
    if not form.validate_on_submit():
        flash('Security token invalid. Please try again.', 'error')
        return redirect(url_for('edit_coach_profile') + '#education')

    user = get_current_user()
    education = Education.query.filter_by(
        id=education_id,
        coach_profile_id=user.coach_profile.id
    ).first_or_404()

    get_db().session.delete(education)
    get_db().session.commit()
    flash('Education deleted successfully!', 'success')
    return redirect(url_for('edit_coach_profile') + '#education')

# Messaging Routes
@app.route('/messages')
@login_required
def inbox():
    user = get_current_user()

    # Get all conversations
    try:
        conversations = get_db().session.query(Message).filter(
            (Message.sender_id == user.id) | (Message.recipient_id == user.id)
        ).order_by(Message.created_at.desc()).all()
    except Exception as e:
        # Fallback query without message_type if column doesn't exist
        if "message_type" in str(e):
            conversations = get_db().session.execute(
                get_db().text("""
                    SELECT id, sender_id, recipient_id, content, is_read, created_at 
                    FROM message 
                    WHERE sender_id = :user_id OR recipient_id = :user_id 
                    ORDER BY created_at DESC
                """),
                {'user_id': user.id}
            ).fetchall()
            # Convert to Message objects
            conversations = []
            for row in conversations:
                msg = Message()
                msg.id = row[0]
                msg.sender_id = row[1]
                msg.recipient_id = row[2]
                msg.content = row[3]
                msg.is_read = row[4]
                msg.created_at = row[5]
                msg.message_type = 'TEXT'  # Default value
                conversations.append(msg)
        else:
            raise e

    # Group by conversation partner
    conversation_partners = {}
    for message in conversations:
        partner_id = message.recipient_id if message.sender_id == user.id else message.sender_id
        if partner_id not in conversation_partners:
            partner = User.query.get(partner_id)
            conversation_partners[partner_id] = {
                'partner': partner,
                'last_message': message,
                'unread_count': 0
            }

    # Count unread messages
    for partner_id in conversation_partners:
        unread_count = Message.query.filter_by(
            sender_id=partner_id,
            recipient_id=user.id,
            is_read=False
        ).count()
        conversation_partners[partner_id]['unread_count'] = unread_count

    return render_template('messages/inbox.html', conversations=conversation_partners)

@app.route('/messages/<int:user_id>')
@login_required
def conversation(user_id):
    current_user = get_current_user()
    other_user = User.query.get_or_404(user_id)

    # Check if users can message each other
    from utils import can_message_user
    if not can_message_user(current_user.id, user_id):
        if current_user.is_coach and other_user.is_student:
            flash('You can only message students who have contacted you first or who you\'re working with.', 'error')
        else:
            flash('Unable to start conversation with this user.', 'error')
        return redirect(url_for('inbox'))

    # Get messages between users
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()

    # Mark messages as read
    Message.query.filter_by(
        sender_id=user_id,
        recipient_id=current_user.id,
        is_read=False
    ).update({'is_read': True})
    get_db().session.commit()

    form = MessageForm()
    
    # Get proposals for contract creation button (if student is talking to coach)
    proposals = []
    if current_user.current_role == 'student' and other_user.current_role == 'coach':
        proposals = Proposal.query.filter_by(
            coach_id=other_user.id
        ).join(LearningRequest).filter(
            LearningRequest.student_id == current_user.id
        ).all()

    return render_template('messages/conversation.html',
                         messages=messages,
                         other_user=other_user,
                         form=form,
                         proposals=proposals)

@app.route('/send-message/<int:recipient_id>', methods=['POST'])
@login_required
def send_message(recipient_id):
    current_user = get_current_user()

    # Check if user can message recipient
    from utils import can_message_user
    recipient = User.query.get_or_404(recipient_id)
    if not can_message_user(current_user.id, recipient_id):
        error_message = 'You can only message students who have contacted you first or who you\'re working with.' if current_user.is_coach and recipient.is_student else 'Unable to send message to this user.'

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': error_message}), 403

        flash(error_message, 'error')
        return redirect(url_for('inbox'))

    form = MessageForm()

    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            content=form.content.data,
            sender_role=current_user.current_role,
            recipient_role=recipient.current_role
        )

        get_db().session.add(message)
        get_db().session.commit()

        # Create notification for recipient (only if table exists)
        try:
            from sqlalchemy import text
            # Check if notification table exists
            result = get_db().session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'notification'
                );
            """))
            table_exists = result.scalar()
            
            if table_exists:
                from notification_utils import create_message_notification
                create_message_notification(current_user, recipient, form.content.data)
        except Exception as e:
            # Silently ignore notification errors - don't break message sending
            pass

        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'created_at': message.created_at.replace(tzinfo=timezone.utc).isoformat(),
                    'sender_id': message.sender_id,
                    'recipient_id': message.recipient_id,
                    'is_read': message.is_read
                }
            })

        flash('Message sent!', 'success')
    else:
        # Handle form validation errors for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(f"{field}: {error}")
            return jsonify({
                'success': False,
                'error': '; '.join(errors) if errors else 'Invalid form data'
            }), 400

    return redirect(url_for('conversation', user_id=recipient_id))

@app.route('/start-conversation/<int:user_id>')
@login_required
def start_conversation(user_id):
    """Start a conversation with a user, checking permissions first"""
    current_user = get_current_user()
    other_user = User.query.get_or_404(user_id)

    # Check if users can message each other
    from utils import can_message_user
    if not can_message_user(current_user.id, user_id):
        if current_user.is_coach and other_user.is_student:
            flash('You can only message students who have contacted you first or who you\'re working with.', 'error')
        else:
            flash('Unable to start conversation with this user.', 'error')
        return redirect(request.referrer or url_for('index'))

    # Check if conversation already exists
    existing_conversation = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
    ).first()

    if existing_conversation:
        # Redirect to existing conversation
        return redirect(url_for('conversation', user_id=user_id))
    else:
        # Redirect to conversation page to start new conversation
        return redirect(url_for('conversation', user_id=user_id))

@app.route('/messages/<int:user_id>/mark-read', methods=['POST'])
@login_required
def mark_messages_read(user_id):
    """Mark messages from a specific user as read"""
    current_user = get_current_user()

    # Mark messages as read
    updated = Message.query.filter_by(
        sender_id=user_id,
        recipient_id=current_user.id,
        is_read=False
    ).update({'is_read': True})

    get_db().session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'marked_read': updated})

    return redirect(url_for('conversation', user_id=user_id))

@app.route('/messages/<int:user_id>/new-messages')
@login_required
def get_new_messages(user_id):
    """Get new messages from a specific user since last check"""
    current_user = get_current_user()

    # Get timestamp from query parameter
    since = request.args.get('since')
    if since:
        try:
            from datetime import datetime
            since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
        except:
            since_dt = None
    else:
        since_dt = None

    # Build query for new messages
    query = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
    )

    if since_dt:
        query = query.filter(Message.created_at > since_dt)

    messages = query.order_by(Message.created_at.asc()).all()

    # Convert messages to JSON
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'sender_id': msg.sender_id,
            'recipient_id': msg.recipient_id,
            'created_at': msg.created_at.replace(tzinfo=timezone.utc).isoformat(),
            'is_read': msg.is_read,
            'time_display': msg.created_at.strftime('%H:%M')
        })

    return jsonify({
        'success': True,
        'messages': messages_data,
        'current_user_id': current_user.id
    })


# Contract and Call Scheduling Routes for Messages Interface
@app.route('/messages/<int:user_id>/create-contract', methods=['GET', 'POST'])
@login_required
@student_required
def create_contract_from_messages(user_id):
    """Create contract from messages interface"""
    current_user = get_current_user()
    coach = User.query.get_or_404(user_id)
    
    # Check if there's an accepted proposal between these users
    accepted_proposal = Proposal.query.filter_by(
        coach_id=coach.id,
        status='accepted'
    ).join(LearningRequest).filter(
        LearningRequest.student_id == current_user.id
    ).first()
    
    if not accepted_proposal:
        flash('No accepted proposal found for this coach.', 'error')
        return redirect(url_for('conversation', user_id=user_id))
    
    # Ensure the proposal has required data
    if not accepted_proposal.learning_request:
        flash('Learning request not found for this proposal.', 'error')
        return redirect(url_for('conversation', user_id=user_id))
    
    form = ContractForm()
    
    if form.validate_on_submit():
        try:
            # Create contract
            contract = accepted_proposal.create_contract(
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                total_sessions=form.total_sessions.data,
                duration_minutes=form.duration_minutes.data,
                rate=form.rate.data,
                timezone=form.timezone.data,
                cancellation_policy=form.cancellation_policy.data,
                learning_outcomes=form.learning_outcomes.data
            )
            
            # Create structured contract data for better parsing
            contract_data = {
                'project': accepted_proposal.learning_request.title,
                'sessions': contract.total_sessions,
                'amount': float(contract.total_amount),
                'start_date': contract.start_date.strftime('%B %d, %Y'),
                'contract_id': contract.id,
                'status': 'pending',
                'duration': contract.duration_minutes or 60,
                'rate': f"${float(contract.total_amount) / contract.total_sessions:.2f}" if contract.total_sessions > 0 else "N/A"
            }
            
            # Send contract notification message to coach with structured data
            contract_preview = json.dumps(contract_data)
            
            contract_message = Message(
                sender_id=current_user.id,
                recipient_id=coach.id,
                content=contract_preview,
                sender_role='student',
                recipient_role='coach',
                message_type='CONTRACT_OFFER'
            )
            db.session.add(contract_message)
            db.session.commit()
            
            flash('Contract created successfully! The coach has been notified and will review your contract.', 'success')
            return redirect(url_for('conversation', user_id=user_id))
            
        except Exception as e:
            flash(f'Error creating contract: {str(e)}', 'error')
    
    return render_template('messages/create_contract.html', 
                         form=form, 
                         proposal=accepted_proposal,
                         coach=coach)


@app.route('/messages/<int:user_id>/schedule-call', methods=['GET', 'POST'])
@login_required
def schedule_call_from_messages(user_id):
    """Send a consultation request card in the chat instead of showing a form"""
    current_user = get_current_user()
    other_user = User.query.get_or_404(user_id)
    
    # Check if users can message each other
    from utils import can_message_user
    if not can_message_user(current_user.id, user_id):
        flash('Unable to schedule call with this user.', 'error')
        return redirect(url_for('conversation', user_id=user_id))
    
    # Check if coach is approved
    if not other_user.coach_profile or not other_user.coach_profile.is_approved:
        flash('This coach is not available for consultations.', 'error')
        return redirect(url_for('conversation', user_id=user_id))
    
    if request.method == 'POST':
        # Validate CSRF token
        from flask_wtf.csrf import validate_csrf
        try:
            validate_csrf(request.form.get('csrf_token'))
        except:
            flash('Invalid form submission. Please try again.', 'error')
            return redirect(url_for('conversation', user_id=user_id))
        
        # Get call details from form
        call_date = request.form.get('call_date')
        call_time = request.form.get('call_time')
        call_timezone = request.form.get('call_timezone', 'UTC')
        call_notes = request.form.get('call_notes', '')
        
        if call_date and call_time:
            try:
                from datetime import datetime
                call_datetime = datetime.strptime(f"{call_date} {call_time}", "%Y-%m-%d %H:%M")
                
                # Use the new scheduling system
                from scheduling_utils import schedule_free_consultation as schedule_free_consultation_util
                
                # Convert date and time to separate fields
                call_date = call_datetime.date()
                call_time = call_datetime.time()
                
                # Schedule the call using the new system
                try:
                    call = schedule_free_consultation_util(
                        student_id=current_user.id,
                        coach_id=other_user.id,
                        scheduled_date=call_date,
                        scheduled_time=call_time,
                        timezone_name=call_timezone,
                        notes=call_notes
                    )
                    
                    flash('Call scheduled successfully!', 'success')
                    return redirect(url_for('conversation', user_id=user_id))
                    
                except Exception as e:
                    flash('An error occurred while scheduling the call. Please try again.', 'error')
                    logger.error(f"Error scheduling call: {e}")
                    
            except ValueError:
                flash('Invalid date/time format.', 'error')
        else:
            flash('Please provide call date and time.', 'error')
    
    # For GET requests, send a consultation request card in the chat
    try:
        import json
        from datetime import datetime, timedelta
        
        # Create a consultation request message (not a scheduled call yet)
        consultation_request_data = {
            "consultation_id": None,  # Will be set when actually scheduled
            "scheduled_at": "TBD",    # To be determined
            "status": "requested",    # Status is requested, not scheduled
            "coach_name": f"{other_user.first_name} {other_user.last_name}",
            "student_name": f"{current_user.first_name} {current_user.last_name}",
            "duration": "15",
            "request_type": "consultation_request"
        }
        
        # Create the consultation request message
        from models import Message
        consultation_message = Message(
            sender_id=current_user.id,
            recipient_id=other_user.id,
            content=json.dumps(consultation_request_data),
            message_type='FREE_CONSULTATION',
            sender_role=current_user.current_role,
            recipient_role=other_user.current_role
        )
        
        # Save the message
        get_db().session.add(consultation_message)
        get_db().session.commit()
        
        flash('Consultation request sent! The coach will respond with available times.', 'success')
        return redirect(url_for('conversation', user_id=user_id))
        
    except Exception as e:
        flash('An error occurred while sending the consultation request. Please try again.', 'error')
        logger.error(f"Error sending consultation request: {e}")
        return redirect(url_for('conversation', user_id=user_id))


# Portfolio Management Routes
@app.route('/test-contract-card')
def test_contract_card():
    """Test route to verify contract card display"""
    return render_template('test_contract_card.html')

@app.route('/test-contract-card-interactive')
def test_contract_card_interactive():
    """Test route to verify interactive contract card display"""
    test_contract_data = {
        'project': 'Learn Marketing',
        'sessions': 4,
        'amount': 100.0,
        'start_date': 'August 20, 2025',
        'contract_id': 11,
        'status': 'pending',
        'duration': 60,
        'rate': '$25.00'
    }
    return render_template('test_contract_card_interactive.html', test_contract_data=test_contract_data)

@app.route('/portfolio/add', methods=['GET', 'POST'])
@coach_required
def add_portfolio():
    user = get_current_user()
    coach_profile = user.coach_profile

    if not coach_profile:
        flash('Coach profile not found.', 'error')
        return redirect(url_for('coach_dashboard'))

    form = PortfolioForm()

    if form.validate_on_submit():
        print(f"DEBUG: Portfolio form validated successfully for user {user.id}")
        # Handle thumbnail image upload
        thumbnail_path = None
        if form.thumbnail_image.data:
            print(f"DEBUG: Processing thumbnail upload: {form.thumbnail_image.data.filename}")
            from utils import save_portfolio_thumbnail
            thumbnail_path = save_portfolio_thumbnail(form.thumbnail_image.data)
            print(f"DEBUG: Thumbnail saved to: {thumbnail_path}")
        else:
            print("DEBUG: No thumbnail image provided")

        portfolio_item = PortfolioItem(
            coach_profile_id=coach_profile.id,
            category=form.category.data,
            title=form.title.data,
            description=form.description.data,
            project_links=form.project_links.data,
            thumbnail_image=thumbnail_path,
            skills=form.skills.data
        )

        get_db().session.add(portfolio_item)
        get_db().session.commit()

        # Mark coach profile for re-approval if approved
        if coach_profile.is_approved:
            coach_profile.is_approved = False
            get_db().session.commit()
            flash('Portfolio item added! Your profile will need to be re-approved due to this change.', 'success')
        else:
            flash('Portfolio item added successfully!', 'success')

        return redirect(url_for('edit_coach_profile') + '#portfolio')

    if request.method == 'POST' and not form.validate():
        print(f"DEBUG: Portfolio form validation failed for user {user.id}")
        print(f"DEBUG: Form errors: {form.errors}")
    
    return render_template('portfolio/add_portfolio.html', form=form)

@app.route('/portfolio/edit/<int:portfolio_id>', methods=['GET', 'POST'])
@coach_required
def edit_portfolio(portfolio_id):
    user = get_current_user()
    coach_profile = user.coach_profile

    portfolio_item = PortfolioItem.query.filter_by(
        id=portfolio_id,
        coach_profile_id=coach_profile.id
    ).first_or_404()

    form = PortfolioForm(obj=portfolio_item)

    if form.validate_on_submit():
        print(f"DEBUG: Edit portfolio form validated successfully for user {user.id}")
        # Handle thumbnail image upload
        if form.thumbnail_image.data:
            print(f"DEBUG: Processing thumbnail upload: {form.thumbnail_image.data.filename}")
            from utils import save_portfolio_thumbnail
            thumbnail_path = save_portfolio_thumbnail(form.thumbnail_image.data)
            portfolio_item.thumbnail_image = thumbnail_path
            print(f"DEBUG: Thumbnail saved to: {thumbnail_path}")
        else:
            print("DEBUG: No new thumbnail image provided")

        portfolio_item.category = form.category.data
        portfolio_item.title = form.title.data
        portfolio_item.description = form.description.data
        portfolio_item.project_links = form.project_links.data
        portfolio_item.skills = form.skills.data

        get_db().session.commit()

        # Mark coach profile for re-approval if approved
        if coach_profile.is_approved:
            coach_profile.is_approved = False
            get_db().session.commit()
            flash('Portfolio item updated! Your profile will need to be re-approved due to this change.', 'success')
        else:
            flash('Portfolio item updated successfully!', 'success')

        return redirect(url_for('edit_coach_profile') + '#portfolio')

    if request.method == 'POST' and not form.validate():
        print(f"DEBUG: Edit portfolio form validation failed for user {user.id}")
        print(f"DEBUG: Form errors: {form.errors}")
    
    return render_template('portfolio/edit_portfolio.html', form=form, portfolio_item=portfolio_item)

@app.route('/portfolio/delete/<int:portfolio_id>', methods=['POST'])
@coach_required
def delete_portfolio(portfolio_id):
    from flask_wtf import FlaskForm
    from flask import request

    # Create a simple form for CSRF validation
    form = FlaskForm()
    if not form.validate_on_submit():
        flash('Security token invalid. Please try again.', 'error')
        return redirect(url_for('edit_coach_profile') + '#portfolio')

    user = get_current_user()
    coach_profile = user.coach_profile

    portfolio_item = PortfolioItem.query.filter_by(
        id=portfolio_id,
        coach_profile_id=coach_profile.id
    ).first_or_404()

    get_db().session.delete(portfolio_item)
    get_db().session.commit()

    # Mark coach profile for re-approval if approved
    if coach_profile.is_approved:
        coach_profile.is_approved = False
        get_db().session.commit()
        flash('Portfolio item deleted! Your profile will need to be re-approved due to this change.', 'success')
    else:
        flash('Portfolio item deleted successfully!', 'success')

    return redirect(url_for('edit_coach_profile') + '#portfolio')

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    try:
        form = AdminLoginForm()
        if form.validate_on_submit():
            password = form.password.data
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')  # Use environment variable
            if password == admin_password:
                session['admin_logged_in'] = True
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid password', 'error')

        return render_template('admin/login.html', form=form)
    except Exception as e:
        logger.error(f"Error in admin_login: {e}")
        logger.error(traceback.format_exc())
        flash(f'An error occurred: {str(e)}', 'error')
        try:
            return render_template('admin/login.html', form=AdminLoginForm())
        except:
            return f"Error loading admin login: {str(e)}", 500

@app.route('/admin')
@admin_required
def admin_dashboard():
    try:
        # Debug: Check admin session
        print(f"DEBUG: Admin session check - admin_logged_in: {session.get('admin_logged_in')}")
        print(f"DEBUG: All session keys: {list(session.keys())}")
        
        # Get statistics with error handling
        try:
            total_users = User.query.count()
            total_coaches = User.query.filter_by(is_coach=True).count()
            total_students = User.query.filter_by(is_student=True).count()
            pending_approvals = CoachProfile.query.filter_by(is_approved=False).count()
            active_requests = LearningRequest.query.filter_by(is_active=True).count()

            # Get recent users
            recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()

            # Get pending coach approvals
            pending_coaches = CoachProfile.query.filter_by(is_approved=False).all()

            stats = {
                'total_users': total_users,
                'total_coaches': total_coaches,
                'total_students': total_students,
                'pending_approvals': pending_approvals,
                'active_requests': active_requests
            }

            return render_template('admin/dashboard.html',
                                 stats=stats,
                                 recent_users=recent_users,
                                 pending_coaches=pending_coaches,
                                 config=app.config)
        except Exception as db_error:
            logger.error(f"Database error in admin_dashboard: {db_error}")
            logger.error(traceback.format_exc())
            # Return dashboard with error message
            stats = {
                'total_users': 0,
                'total_coaches': 0,
                'total_students': 0,
                'pending_approvals': 0,
                'active_requests': 0
            }
            error_message = f"Database connection error: {str(db_error)}"
            flash(error_message, 'error')
            return render_template('admin/dashboard.html',
                                 stats=stats,
                                 recent_users=[],
                                 pending_coaches=[],
                                 config=app.config,
                                 db_error=error_message)
    except Exception as e:
        logger.error(f"Error in admin_dashboard: {e}")
        logger.error(traceback.format_exc())
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/approve-coach/<int:coach_id>')
@admin_required
def approve_coach(coach_id):
    coach_profile = CoachProfile.query.get_or_404(coach_id)
    coach_profile.is_approved = True
    get_db().session.commit()

    flash(f'Coach {coach_profile.user.first_name} {coach_profile.user.last_name} approved!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject-coach/<int:coach_id>')
@admin_required
def reject_coach(coach_id):
    coach_profile = CoachProfile.query.get_or_404(coach_id)
    # You might want to add a rejection reason and notification system
    get_db().session.delete(coach_profile)
    get_db().session.commit()

    flash(f'Coach profile rejected and deleted.', 'warning')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/test-delete', methods=['POST'])
# @admin_required  # Temporarily commented out for debugging
def test_delete():
    """Test route to check if deletion functionality works"""
    print("DEBUG: test_delete function called")
    print(f"DEBUG: Admin session in test_delete - admin_logged_in: {session.get('admin_logged_in')}")
    print(f"DEBUG: CSRF token from form: {request.form.get('csrf_token')}")
    print(f"DEBUG: All form data: {dict(request.form)}")
    
    try:
        from models import User
        db = get_db()
        
        # Test basic database operations
        user_count = User.query.count()
        print(f"DEBUG: Found {user_count} users in database")
        
        # Test if we can access the database session
        print(f"DEBUG: Database session: {db.session}")
        
        # Test if we can query a specific user
        if user_count > 0:
            first_user = User.query.first()
            print(f"DEBUG: First user: {first_user.id} - {first_user.email}")
        
        flash(f'Test successful. Found {user_count} users in database.', 'success')
    except Exception as e:
        print(f"DEBUG: Error in test_delete: {str(e)}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        flash(f'Test failed: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-all-users', methods=['POST'])
@admin_required
def delete_all_users():
    """Delete all coaches and students accounts and their related data"""
    print("DEBUG: delete_all_users function called")
    try:
        # Get all users and delete them using the safe deletion utility
        from utils import safe_delete_user_data
        from models import User
        users = User.query.all()
        print(f"DEBUG: Found {len(users)} users to delete")
        deleted_count = 0
        
        for user in users:
            try:
                print(f"DEBUG: Attempting to delete user {user.id} ({user.email})")
                if safe_delete_user_data(user.id):
                    deleted_count += 1
                    print(f"DEBUG: Successfully deleted user {user.id}")
                else:
                    print(f"DEBUG: Failed to delete user {user.id} - user not found")
            except Exception as e:
                print(f"DEBUG: Error deleting user {user.id}: {str(e)}")
                import traceback
                print(f"DEBUG: Full traceback: {traceback.format_exc()}")
                continue
        
        print(f"DEBUG: Deletion complete. Deleted {deleted_count} users out of {len(users)}")
        flash(f'Successfully deleted {deleted_count} user accounts.', 'success')

    except Exception as e:
        print(f"DEBUG: Error in delete_all_users: {str(e)}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        get_db().session.rollback()
        flash(f'Error occurred while deleting accounts: {str(e)}', 'error')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-coaches', methods=['POST'])
@admin_required
def delete_all_coaches():
    """Delete all coach accounts and their related data"""
    try:
        # Get all coach users and delete them using the safe deletion utility
        from utils import safe_delete_user_data
        from models import User
        coach_users = User.query.filter_by(is_coach=True).all()
        deleted_count = 0
        
        for coach_user in coach_users:
            try:
                if safe_delete_user_data(coach_user.id):
                    deleted_count += 1
            except Exception as e:
                print(f"Error deleting coach user {coach_user.id}: {str(e)}")
                continue
        
        flash(f'Successfully deleted {deleted_count} coach accounts.', 'success')

    except Exception as e:
        get_db().session.rollback()
        flash(f'Error occurred while deleting coach accounts: {str(e)}', 'error')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete-students', methods=['POST'])
@admin_required
def delete_all_students():
    """Delete all student accounts and their related data"""
    try:
        # Get all student users and delete them using the safe deletion utility
        from utils import safe_delete_user_data
        from models import User
        student_users = User.query.filter_by(is_student=True).all()
        deleted_count = 0
        
        for student_user in student_users:
            try:
                if safe_delete_user_data(student_user.id):
                    deleted_count += 1
            except Exception as e:
                print(f"Error deleting student user {student_user.id}: {str(e)}")
                continue
        
        flash(f'Successfully deleted {deleted_count} student accounts.', 'success')

    except Exception as e:
        get_db().session.rollback()
        flash(f'Error occurred while deleting student accounts: {str(e)}', 'error')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin/toggle-test-mode', methods=['POST'])
@admin_required
def admin_toggle_test_mode():
    """Toggle payment test mode"""
    try:
        test_mode = request.form.get('test_mode') == 'true'
        
        # Update environment variable (this will persist for the current session)
        import os
        os.environ['TEST_MODE'] = str(test_mode).lower()
        
        # Update app config
        app.config['TEST_MODE'] = test_mode
        app.config['TEST_MODE_ENABLED'] = test_mode
        
        # Log the change
        logging.info(f"Payment test mode {'enabled' if test_mode else 'disabled'} by admin")
        
        flash(f'Payment test mode has been {"enabled" if test_mode else "disabled"}.', 'success')
        
    except Exception as e:
        logging.error(f"Error toggling test mode: {str(e)}")
        flash(f'Error toggling test mode: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

# Route to serve uploaded files
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join('static', 'uploads'), filename)

# Route to serve job-related uploaded files
@app.route('/job/uploads/<filename>')
def job_uploaded_file(filename):
    return send_from_directory(os.path.join('static', 'uploads'), filename)

# Route to serve message-related uploaded files
@app.route('/messages/uploads/<filename>')
def messages_uploaded_file(filename):
    return send_from_directory(os.path.join('static', 'uploads'), filename)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    get_db().session.rollback()
    return render_template('errors/500.html'), 500


# Add these new routes to your routes.py file

@app.route('/api/role-switch', methods=['POST'])
@login_required  
def api_role_switch():
    """API endpoint for role switching with enhanced validation"""
    try:
        # Skip CSRF for API endpoint - handle via form instead
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        target_role = data.get('role')
        reason = data.get('reason', 'manual_switch')

        if not target_role:
            return jsonify({'success': False, 'error': 'Role not specified'}), 400

        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 401

        # Enhanced validation
        success, message = user.switch_role_with_validation(
            target_role=target_role,
            reason=reason,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )

        # Log the attempt
        log_role_switch_attempt(
            user_id=user.id,
            target_role=target_role,
            success=success,
            error_message=None if success else message,
            ip_address=request.remote_addr
        )

        if success:
            # Create notification for successful role switch
            try:
                create_profile_notification(user, 'role_switched')
            except Exception as e:
                print(f"Error creating role switch notification: {e}")
                
            return jsonify({
                'success': True,
                'message': message,
                'new_role': user.current_role,
                'dashboard_url': get_role_dashboard_url_enhanced(user)
            })
        else:
            return jsonify({'success': False, 'error': message}), 400

    except Exception as e:
        app.logger.error(f"Role switch API error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/role-switch-page')
@login_required
def role_switch_page():
    """Enhanced role switching page"""
    user = get_current_user()

    if not user.can_switch_roles():
        flash('You do not have multiple roles to switch between.', 'info')
        return redirect(url_for('index'))

    # Get analytics (create empty dict for now)
    analytics = {
        'total_switches': user.role_switch_count or 0,
        'switches_7d': 0,
        'switches_30d': 0,
        'last_switch': user.last_role_switch,
        'recent_switches': []
    }

    # Get role context
    role_context = create_role_context_for_template(user)

    return render_template('role_switch.html', 
                         user=user, 
                         analytics=analytics,
                         role_context=role_context)

@app.route('/api/role-status')
@login_required
def api_role_status():
    """API endpoint to get current role status"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 401

    return jsonify({
        'current_role': user.current_role,
        'available_roles': user.get_available_roles(),
        'can_switch': user.can_switch_roles(),
        'other_role': user.get_other_role(),
        'role_context': create_role_context_for_template(user),
        'dashboard_url': get_role_dashboard_url_enhanced(user)
    })

@app.route('/api/conversation/<int:user_id>/contract')
@login_required
def api_conversation_contract(user_id):
    """API endpoint to get contract for a conversation"""
    current_user = get_current_user()
    other_user = User.query.get_or_404(user_id)
    
    # Find accepted proposal between these users
    if current_user.current_role == 'student':
        # Student looking for coach's contract
        proposal = Proposal.query.filter_by(
            learning_request_id=LearningRequest.query.filter_by(student_id=current_user.id).first().id,
            coach_id=other_user.id,
            status='accepted'
        ).first()
    else:
        # Coach looking for student's contract
        proposal = Proposal.query.filter_by(
            coach_id=current_user.id,
            learning_request_id=LearningRequest.query.filter_by(student_id=other_user.id).first().id,
            status='accepted'
        ).first()
    
    if proposal and proposal.get_contract():
        return jsonify({
            'success': True,
            'contract_id': proposal.get_contract().id
        })
    
    return jsonify({
        'success': False,
        'error': 'No contract found'
    })

@app.route('/contract-preview-demo')
def contract_preview_demo():
    """Demo page for contract preview cards"""
    # Create a test contract data
    test_contract_data = {
        'project': 'Test Learning Project',
        'sessions': 4,
        'amount': 100.0,
        'start_date': 'August 20, 2025',
        'contract_id': 10,
        'status': 'pending',
        'duration': 60,
        'rate': '$25.00'
    }
    
    # Test the extract_contract_info filter
    from app import extract_contract_info
    test_content = json.dumps(test_contract_data)
    extracted_info = extract_contract_info(test_content)
    
    return render_template('contract_preview_demo.html', 
                         test_contract_data=test_contract_data,
                         test_content=test_content,
                         extracted_info=extracted_info)

@app.route('/session-cards-demo')
def session_cards_demo():
    """Demo page for interactive session cards"""
    return render_template('session_cards_demo.html')

@app.route('/contracts/find-from-message/<int:message_id>')
@login_required
def find_contract_from_message(message_id):
    """Find contract from message ID - fallback route"""
    message = Message.query.get_or_404(message_id)
    current_user = get_current_user()
    
    # Verify the user is part of this conversation
    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        flash('You do not have permission to view this message.', 'error')
        return redirect(url_for('dashboard'))
    
    # Find the other user in the conversation
    other_user_id = message.sender_id if message.recipient_id == current_user.id else message.recipient_id
    other_user = User.query.get(other_user_id)
    
    if not other_user:
        flash('User not found.', 'error')
        return redirect(url_for('dashboard'))
    
    # Try to find the contract using the same logic as the API
    if current_user.current_role == 'student':
        proposal = Proposal.query.filter_by(
            learning_request_id=LearningRequest.query.filter_by(student_id=current_user.id).first().id,
            coach_id=other_user.id,
            status='accepted'
        ).first()
    else:
        proposal = Proposal.query.filter_by(
            coach_id=current_user.id,
            learning_request_id=LearningRequest.query.filter_by(student_id=other_user.id).first().id,
            status='accepted'
        ).first()
    
    if proposal and proposal.get_contract():
        return redirect(url_for('view_contract', contract_id=proposal.get_contract().id))
    
    # If no contract found, redirect to contracts list
    flash('Contract not found. Please check your contracts list.', 'warning')
    return redirect(url_for('contracts_list'))

# Add context processor for role switching and current_user
@app.context_processor
def inject_role_context():
    """Inject role context and current_user into all templates"""
    user = get_current_user()
    if user:
        return {
            'role_context': create_role_context_for_template(user),
            'current_user': user
        }
    return {
        'current_user': None
    }










# Template filters
@app.template_filter('currency')
def currency_filter(amount):
    return format_currency(amount)

@app.template_global()
def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None
# Role Switching Routes
@app.route('/simple-role-switch', methods=['POST'])
@login_required
def simple_role_switch():
    """Form-based role switching for reliable browser compatibility"""
    user = get_current_user()
    target_role = request.form.get('role')

    from utils import switch_user_role
    success, message = switch_user_role(user, target_role)

    if success:
        flash(message, 'success')
        if target_role == 'coach':
            return redirect(url_for('coach_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    else:
        flash(message, 'error')
        return redirect(request.referrer or url_for('index'))

@app.route('/role-switch')
@login_required
def role_switch():
    """Display the role switching page for dual-role users"""
    user = get_current_user()
    if not user.can_switch_roles():
        flash('You do not have multiple roles to switch between.', 'info')
        return redirect(url_for('index'))

    return render_template('role_switch.html', user=user)

@app.route('/upgrade-to-coach', methods=['GET', 'POST'])
@login_required
def upgrade_to_coach():
        user = get_current_user()
        if user.is_coach:
            flash('You are already a coach!', 'info')
            return redirect(url_for('coach_dashboard'))

        form = UpgradeToCoachForm()
        if form.validate_on_submit():
            try:
                user.is_coach = True
                # Automatically switch to coach role when upgrading
                user.current_role = 'coach'

                # Create coach profile if it doesn't exist
                if not user.coach_profile:
                    coach_profile = CoachProfile(user_id=user.id)
                    get_db().session.add(coach_profile)

                get_db().session.commit()
                flash('Congratulations! You\'ve been upgraded to a coach.', 'success')
                return redirect(url_for('coach_onboarding', step=1))

            except Exception as e:
                get_db().session.rollback()
                flash('An error occurred during upgrade.', 'error')
                print(f"Upgrade error: {e}")  # Debug print

        return render_template('upgrade_to_coach.html', form=form, user=user)

@app.route('/upgrade-to-student', methods=['GET', 'POST'])
@login_required
def upgrade_to_student():
    user = get_current_user()
    if user.is_student:
        flash('You are already a student!', 'info')
        return redirect(url_for('student_dashboard'))

    form = UpgradeToStudentForm()
    if form.validate_on_submit():
        try:
            user.is_student = True
            # Automatically switch to student role when upgrading
            user.current_role = 'student'
            get_db().session.commit()
            flash('Congratulations! You\'ve been upgraded to a student.', 'success')
            return redirect(url_for('student_onboarding'))
        except Exception as e:
            get_db().session.rollback()
            flash('An error occurred during upgrade.', 'error')

    return render_template('upgrade_to_student.html', form=form, user=user)

@app.template_global()
def get_upgrade_eligibility(user):
    from utils import get_upgrade_eligibility
    return get_upgrade_eligibility(user)

# Contract Management Routes
@app.route('/contracts/create/<int:proposal_id>', methods=['GET', 'POST'])
@login_required
@student_required
@contract_feature_required
def create_contract(proposal_id):
    """Create a contract from an accepted proposal"""
    proposal = Proposal.query.get_or_404(proposal_id)
    
    # Verify ownership and status
    if proposal.learning_request.student_id != session['user_id']:
        flash('You do not have permission to create this contract.', 'error')
        return redirect(url_for('student_dashboard'))
    
    if proposal.status != 'accepted':
        flash('Can only create contract from accepted proposal.', 'error')
        return redirect(url_for('job_details', job_id=proposal.learning_request_id))
    
    contract = proposal.get_contract()
    if contract:
        flash('Contract already exists for this proposal.', 'error')
        return redirect(url_for('view_contract', contract_id=contract.id))
    
    form = ContractForm()
    
    if form.validate_on_submit():
        try:
            # Create contract
            contract = proposal.create_contract(
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                total_sessions=form.total_sessions.data,
                duration_minutes=form.duration_minutes.data,
                rate=form.rate.data,
                timezone=form.timezone.data,
                cancellation_policy=form.cancellation_policy.data,
                learning_outcomes=form.learning_outcomes.data
            )
            
            # Create notification for coach
            create_contract_notification(contract, 'contract_sent')
            
            flash('Contract created successfully! Please complete payment to activate your contract.', 'success')
            return redirect(url_for('contract_payment', contract_id=contract.id))
            
        except Exception as e:
            flash(f'Error creating contract: {str(e)}', 'error')
    
    return render_template('contracts/create_contract.html', 
                         form=form, 
                         proposal=proposal)

@app.route('/contracts/<int:contract_id>')
@login_required
@contract_feature_required
def view_contract(contract_id):
    """View contract details"""
    contract = Contract.query.get_or_404(contract_id)
    user = get_current_user()
    
    # Verify access
    if contract.student_id != user.id and contract.coach_id != user.id:
        flash('You do not have permission to view this contract.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('contracts/view_contract.html', 
                         contract=contract,
                         user=user)

@app.route('/contracts/<int:contract_id>/cancel', methods=['GET', 'POST'])
@login_required
@contract_feature_required
def cancel_contract(contract_id):
    """Cancel a contract"""
    contract = Contract.query.get_or_404(contract_id)
    user = get_current_user()
    
    # Verify access
    if contract.student_id != user.id and contract.coach_id != user.id:
        flash('You do not have permission to cancel this contract.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Get reason from request
        reason = request.json.get('reason', '') if request.is_json else request.form.get('reason', '')
        
        contract.cancel()
        contract.cancellation_reason = reason
        db.session.commit()
        
        flash('Contract cancelled successfully.', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('view_contract', contract_id=contract_id))

# Session Management Routes
@app.route('/contracts/<int:contract_id>/sessions', methods=['GET', 'POST'])
@login_required
@contract_feature_required
def manage_sessions(contract_id):
    """Manage sessions for a contract"""
    from datetime import datetime
    
    contract = Contract.query.get_or_404(contract_id)
    user = get_current_user()
    
    # Verify access
    if contract.student_id != user.id and contract.coach_id != user.id:
        flash('You do not have permission to manage this contract.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if contract is paid and active
    if not contract.can_schedule_sessions():
        if contract.payment_status == 'pending':
            flash('Please complete payment before scheduling sessions.', 'warning')
            return redirect(url_for('contract_payment', contract_id=contract.id))
        elif contract.payment_status == 'paid' and contract.status != 'active':
            flash(f'Contract payment completed but status is {contract.status}. Please contact support to activate the contract.', 'error')
            return redirect(url_for('view_contract', contract_id=contract.id))
        else:
            flash(f'Contract is not active. Payment status: {contract.payment_status}, Contract status: {contract.status}. Please contact support.', 'error')
            return redirect(url_for('view_contract', contract_id=contract.id))
    
    form = SessionScheduleForm()
    
    if form.validate_on_submit():
        try:
            # Parse the datetime string from datetime-local input
            scheduled_datetime = datetime.strptime(form.scheduled_at.data, '%Y-%m-%dT%H:%M')
            
            # Convert from user's timezone to UTC for storage
            from utils import convert_timezone
            user_timezone = form.timezone.data
            utc_datetime = convert_timezone(scheduled_datetime, user_timezone, 'UTC')
            
            # Get the next session number (excluding cancelled sessions)
            existing_sessions = Session.query.filter_by(proposal_id=contract.proposal_id).filter(Session.status != 'cancelled').all()
            next_session_number = len(existing_sessions) + 1
            
            # Check if we haven't exceeded the total sessions for this contract
            if next_session_number > contract.total_sessions:
                flash(f'Cannot schedule more sessions. Contract allows maximum {contract.total_sessions} sessions.', 'error')
                return redirect(url_for('manage_sessions', contract_id=contract_id))
            
            # Create new session
            session = Session(
                proposal_id=contract.proposal_id,
                session_number=next_session_number,
                scheduled_at=utc_datetime,
                duration_minutes=form.duration_minutes.data,
                timezone=form.timezone.data,
                status='scheduled'
            )
            
            db.session.add(session)
            db.session.commit()
            
            # Send session scheduled email notification
            try:
                from email_utils import send_session_scheduled_email
                send_session_scheduled_email(session)
            except Exception as email_error:
                app.logger.error(f"Error sending session scheduled email: {email_error}")
            
            flash(f'Session {session.session_number} scheduled successfully!', 'success')
            return redirect(url_for('manage_sessions', contract_id=contract_id))
            
        except Exception as e:
            flash(f'Error scheduling session: {str(e)}', 'error')
    
    sessions = contract.get_all_sessions()
    active_sessions = contract.get_active_sessions()
    return render_template('contracts/manage_sessions.html', 
                         contract=contract,
                         sessions=sessions,
                         active_sessions=active_sessions,
                         form=form,
                         user=user,
                         now=datetime.utcnow())

@app.route('/sessions/<int:session_id>/confirm', methods=['POST'])
@login_required
@coach_required
@contract_feature_required
def confirm_session(session_id):
    """Confirm a session (coach only)"""
    session = Session.query.options(
        db.joinedload(Session.proposal).joinedload(Proposal.contracts)
    ).get_or_404(session_id)
    user = get_current_user()
    
    # Verify coach owns this session
    if session.proposal.coach_id != user.id:
        flash('You do not have permission to confirm this session.', 'error')
        return redirect(url_for('dashboard'))
    
    session.confirmed_by_coach = True
    db.session.commit()
    
    flash('Session confirmed!', 'success')
    contract = session.get_contract()
    if contract:
        return redirect(url_for('manage_sessions', contract_id=contract.id))
    else:
        return redirect(url_for('dashboard'))

@app.route('/sessions/<int:session_id>/reschedule', methods=['GET', 'POST'])
@login_required
@contract_feature_required
def request_reschedule(session_id):
    """Request a session reschedule with 5-hour policy"""
    session = Session.query.options(
        db.joinedload(Session.proposal).joinedload(Proposal.contracts)
    ).get_or_404(session_id)
    user = get_current_user()
    
    # Verify access with null safety
    contract = session.get_contract()
    if not contract or (contract.student_id != user.id and contract.coach_id != user.id):
        flash('You do not have permission to reschedule this session.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if reschedule is allowed
    if not session.can_request_reschedule(user.current_role):
        flash('Reschedule not allowed at this time.', 'error')
        return redirect(url_for('manage_sessions', contract_id=contract.id))
    
    form = RescheduleRequestForm()
    
    # Set default timezone
    if session.timezone:
        form.timezone.data = session.timezone
    
    if form.validate_on_submit():
        try:
            # Convert new scheduled time to UTC if provided
            new_scheduled_at = None
            if form.new_scheduled_at.data:
                from utils import convert_timezone
                user_timezone = form.timezone.data
                utc_datetime = convert_timezone(form.new_scheduled_at.data, user_timezone, 'UTC')
                new_scheduled_at = utc_datetime
            
            # Request reschedule with 5-hour policy
            result = session.request_reschedule(
                requested_by=user.current_role,
                reason=form.reason.data,
                new_scheduled_at=new_scheduled_at
            )
            
            # Send notifications for reschedule request (only if pending approval)
            if result == "pending_approval":
                try:
                    from email_utils import send_reschedule_request_email
                    from notification_utils import create_reschedule_notification, create_reschedule_message_notification
                    
                    # Get student and coach
                    student = User.query.get(contract.student_id)
                    coach = User.query.get(contract.coach_id)
                    
                    if student and coach:
                        # Send email notification to coach
                        send_reschedule_request_email(session, student, coach)
                        
                        # Create in-app notification for coach
                        create_reschedule_notification(session, 'reschedule_requested', student, coach)
                        
                        # Create message notification in chat
                        create_reschedule_message_notification(session, 'reschedule_requested', student, coach)
                        
                except Exception as e:
                    print(f"Error sending reschedule request notifications: {e}")
                    # Don't fail the request if notifications fail
            
            if result == "auto_approved":
                flash('Session rescheduled successfully! (Automatic approval - more than 5 hours before session)', 'success')
            else:
                flash('Reschedule request sent! Coach will review your request within 24 hours.', 'success')
            
            return redirect(url_for('manage_sessions', contract_id=contract.id))
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('sessions/request_reschedule.html', 
                         session=session,
                         form=form,
                         current_user=user,
                         is_within_5_hours=session.is_within_5_hours())

@app.route('/sessions/<int:session_id>/approve-reschedule', methods=['GET', 'POST'])
@login_required
@contract_feature_required
def approve_reschedule(session_id):
    """Approve a reschedule request (coach only)"""
    session = Session.query.options(
        db.joinedload(Session.proposal).joinedload(Proposal.contracts)
    ).get_or_404(session_id)
    user = get_current_user()
    
    # Debug logging
    print(f"DEBUG: Approve reschedule called for session {session_id}")
    print(f"DEBUG: User: {user.id}, Role: {user.current_role}")
    print(f"DEBUG: Session reschedule_requested: {session.reschedule_requested}")
    print(f"DEBUG: Session reschedule_requested_by: {session.reschedule_requested_by}")
    print(f"DEBUG: Request method: {request.method}")
    print(f"DEBUG: Request is_json: {request.is_json}")
    
    # Verify access and that user is the coach with null safety
    contract = session.get_contract()
    if not contract or contract.coach_id != user.id:
        print(f"DEBUG: Access denied - contract: {contract}, coach_id: {contract.coach_id if contract else None}")
        if request.is_json:
            return jsonify({'success': False, 'error': 'Only coaches can approve reschedule requests.'})
        flash('Only coaches can approve reschedule requests.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if there's a pending reschedule request from student
    if not session.reschedule_requested or session.reschedule_requested_by != 'student':
        print(f"DEBUG: No pending reschedule request - requested: {session.reschedule_requested}, by: {session.reschedule_requested_by}")
        if request.is_json:
            return jsonify({'success': False, 'error': 'No pending reschedule request from student.'})
        flash('No pending reschedule request from student.', 'error')
        return redirect(url_for('manage_sessions', contract_id=contract.id))
    
    if request.method == 'POST':
        try:
            print(f"DEBUG: Processing POST request")
            # Handle both JSON and form data
            if request.is_json:
                data = request.get_json()
                new_scheduled_at = data.get('new_scheduled_at')
                print(f"DEBUG: JSON request, new_scheduled_at: {new_scheduled_at}")
            else:
                # Check if it's a simple form submission (like from the approve button)
                new_scheduled_at = request.form.get('new_scheduled_at')
                print(f"DEBUG: Form request, new_scheduled_at: {new_scheduled_at}")
                print(f"DEBUG: Form data: {dict(request.form)}")
                if not new_scheduled_at:
                    # This is a simple approve button click - approve without changing time
                    print(f"DEBUG: Simple approve button click - approving without changing time")
                    session.approve_reschedule()
                    
                    # Send notifications for reschedule approval
                    try:
                        print(f"DEBUG: Starting reschedule approval notifications")
                        from email_utils import send_reschedule_approved_email
                        from notification_utils import create_reschedule_notification, create_reschedule_message_notification
                        
                        # Get student and coach
                        student = User.query.get(contract.student_id)
                        coach = User.query.get(contract.coach_id)
                        print(f"DEBUG: Student: {student}, Coach: {coach}")
                        
                        if student and coach:
                            print(f"DEBUG: Sending email notification")
                            # Send email notification
                            email_result = send_reschedule_approved_email(session, student, coach)
                            print(f"DEBUG: Email result: {email_result}")
                            
                            print(f"DEBUG: Creating in-app notification")
                            # Create in-app notification
                            create_reschedule_notification(session, 'reschedule_approved', student, coach)
                            
                            print(f"DEBUG: Creating message notification")
                            # Create message notification
                            create_reschedule_message_notification(session, 'reschedule_approved', student, coach)
                            
                            print(f"DEBUG: All notifications sent successfully")
                        else:
                            print(f"DEBUG: Missing student or coach - student: {student}, coach: {coach}")
                            
                    except Exception as e:
                        print(f"Error sending reschedule approval notifications: {e}")
                        import traceback
                        traceback.print_exc()
                    
                    flash('Reschedule approved!', 'success')
                    return redirect(url_for('manage_sessions', contract_id=contract.id))
            
            # Parse the datetime string if new time provided
            from datetime import datetime
            if new_scheduled_at:
                if 'T' in new_scheduled_at:
                    new_scheduled_datetime = datetime.strptime(new_scheduled_at, '%Y-%m-%dT%H:%M')
                else:
                    new_scheduled_datetime = datetime.strptime(new_scheduled_at, '%Y-%m-%d %H:%M')
                session.approve_reschedule(new_scheduled_datetime)
            else:
                # Approve without changing time
                session.approve_reschedule()
            
            # Send notifications for reschedule approval
            try:
                print(f"DEBUG: Starting reschedule approval notifications (POST with time)")
                from email_utils import send_reschedule_approved_email
                from notification_utils import create_reschedule_notification, create_reschedule_message_notification
                
                # Get student and coach
                student = User.query.get(contract.student_id)
                coach = User.query.get(contract.coach_id)
                print(f"DEBUG: Student: {student}, Coach: {coach}")
                
                if student and coach:
                    print(f"DEBUG: Sending email notification")
                    # Send email notification
                    email_result = send_reschedule_approved_email(session, student, coach)
                    print(f"DEBUG: Email result: {email_result}")
                    
                    print(f"DEBUG: Creating in-app notification")
                    # Create in-app notification
                    create_reschedule_notification(session, 'reschedule_approved', student, coach)
                    
                    print(f"DEBUG: Creating message notification")
                    # Create message notification
                    create_reschedule_message_notification(session, 'reschedule_approved', student, coach)
                    
                    print(f"DEBUG: All notifications sent successfully")
                else:
                    print(f"DEBUG: Missing student or coach - student: {student}, coach: {coach}")
                    
            except Exception as e:
                print(f"Error sending reschedule approval notifications: {e}")
                import traceback
                traceback.print_exc()
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'Reschedule approved! Session has been rescheduled.'})
            flash('Reschedule approved! Session has been rescheduled.', 'success')
            return redirect(url_for('manage_sessions', contract_id=contract.id))
            
        except ValueError as e:
            if request.is_json:
                return jsonify({'success': False, 'error': str(e)})
            flash(str(e), 'error')
    else:
        # For GET requests, approve with the proposed time if available
        try:
            # if session.reschedule_proposed_time:  # TEMPORARILY DISABLED
            #     session.approve_reschedule(session.reschedule_proposed_time)
            #     if request.is_json:
            #         return jsonify({'success': True, 'message': 'Reschedule approved with student\'s proposed time!'})
            #     flash('Reschedule approved with student\'s proposed time!', 'success')
            # else:
            session.approve_reschedule()  # Approve without changing time
            
            # Send notifications for reschedule approval
            try:
                print(f"DEBUG: Starting reschedule approval notifications (GET request)")
                from email_utils import send_reschedule_approved_email
                from notification_utils import create_reschedule_notification, create_reschedule_message_notification
                
                # Get student and coach
                student = User.query.get(contract.student_id)
                coach = User.query.get(contract.coach_id)
                print(f"DEBUG: Student: {student}, Coach: {coach}")
                
                if student and coach:
                    print(f"DEBUG: Sending email notification")
                    # Send email notification
                    email_result = send_reschedule_approved_email(session, student, coach)
                    print(f"DEBUG: Email result: {email_result}")
                    
                    print(f"DEBUG: Creating in-app notification")
                    # Create in-app notification
                    create_reschedule_notification(session, 'reschedule_approved', student, coach)
                    
                    print(f"DEBUG: Creating message notification")
                    # Create message notification
                    create_reschedule_message_notification(session, 'reschedule_approved', student, coach)
                    
                    print(f"DEBUG: All notifications sent successfully")
                else:
                    print(f"DEBUG: Missing student or coach - student: {student}, coach: {coach}")
                    
            except Exception as e:
                print(f"Error sending reschedule approval notifications: {e}")
                import traceback
                traceback.print_exc()
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'Reschedule approved!'})
            flash('Reschedule approved!', 'success')
            return redirect(url_for('manage_sessions', contract_id=contract.id))
        except ValueError as e:
            if request.is_json:
                return jsonify({'success': False, 'error': str(e)})
            flash(str(e), 'error')
    
    return redirect(url_for('manage_sessions', contract_id=contract.id))

@app.route('/sessions/<int:session_id>/decline-reschedule', methods=['POST'])
@login_required
@contract_feature_required
def decline_reschedule(session_id):
    """Decline a reschedule request (coach only)"""
    session = Session.query.options(
        db.joinedload(Session.proposal).joinedload(Proposal.contracts)
    ).get_or_404(session_id)
    user = get_current_user()
    
    # Verify access and that user is the coach with null safety
    contract = session.get_contract()
    if not contract or contract.coach_id != user.id:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Only coaches can decline reschedule requests.'})
        flash('Only coaches can decline reschedule requests.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if there's a pending reschedule request from student
    if not session.reschedule_requested or session.reschedule_requested_by != 'student':
        if request.is_json:
            return jsonify({'success': False, 'error': 'No pending reschedule request from student.'})
        flash('No pending reschedule request from student.', 'error')
        return redirect(url_for('manage_sessions', contract_id=contract.id))
    
    try:
        session.decline_reschedule()
        
        # Send notifications for reschedule decline
        try:
            from email_utils import send_reschedule_declined_email
            from notification_utils import create_reschedule_notification, create_reschedule_message_notification
            
            # Get student and coach
            student = User.query.get(contract.student_id)
            coach = User.query.get(contract.coach_id)
            
            if student and coach:
                # Send email notification
                send_reschedule_declined_email(session, student, coach)
                
                # Create in-app notification
                create_reschedule_notification(session, 'reschedule_declined', student, coach)
                
                # Create message notification
                create_reschedule_message_notification(session, 'reschedule_declined', student, coach)
                
        except Exception as e:
            print(f"Error sending reschedule decline notifications: {e}")
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Reschedule request declined. Session remains as originally scheduled.'})
        flash('Reschedule request declined. Session remains as originally scheduled.', 'success')
    except ValueError as e:
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)})
        flash(str(e), 'error')
    
    return redirect(url_for('manage_sessions', contract_id=contract.id))

@app.route('/sessions/<int:session_id>/complete', methods=['POST'])
@login_required
@contract_feature_required
def complete_session(session_id):
    """Mark a session as completed"""
    session = Session.query.options(
        db.joinedload(Session.proposal).joinedload(Proposal.contracts)
    ).get_or_404(session_id)
    user = get_current_user()
    
    # Verify access with null safety
    contract = session.get_contract()
    if not contract or (contract.student_id != user.id and contract.coach_id != user.id):
        flash('You do not have permission to complete this session.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Get notes from form data if available, otherwise use empty string
        notes = request.form.get('notes', '')
        session.mark_completed(
            notes=notes,
            completed_by=user.current_role
        )
        flash('Session marked as completed!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('manage_sessions', contract_id=contract.id))

@app.route('/sessions/<int:session_id>/cancel', methods=['POST'])
@login_required
@contract_feature_required
def cancel_session(session_id):
    """Cancel a session"""
    session = Session.query.options(
        db.joinedload(Session.proposal).joinedload(Proposal.contracts)
    ).get_or_404(session_id)
    user = get_current_user()
    
    # Verify access with null safety
    contract = session.get_contract()
    if not contract or (contract.student_id != user.id and contract.coach_id != user.id):
        flash('You do not have permission to cancel this session.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if session can be cancelled
    if session.status != 'scheduled':
        flash('Only scheduled sessions can be cancelled.', 'error')
        return redirect(url_for('manage_sessions', contract_id=contract.id))
    
    try:
        session.status = 'cancelled'
        db.session.commit()
        flash('Session cancelled successfully.', 'success')
    except Exception as e:
        flash(f'Error cancelling session: {str(e)}', 'error')
    
    return redirect(url_for('manage_sessions', contract_id=contract.id))

@app.route('/sessions/<int:session_id>/missed', methods=['POST'])
@login_required
@contract_feature_required
def mark_session_missed(session_id):
    """Mark a session as missed (for no-shows)"""
    session = Session.query.options(
        db.joinedload(Session.proposal).joinedload(Proposal.contracts)
    ).get_or_404(session_id)
    user = get_current_user()
    
    # Verify access with null safety
    contract = session.get_contract()
    if not contract or (contract.student_id != user.id and contract.coach_id != user.id):
        flash('You do not have permission to mark this session as missed.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if session can be marked as missed
    if session.status != 'scheduled':
        flash('Only scheduled sessions can be marked as missed.', 'error')
        return redirect(url_for('manage_sessions', contract_id=contract.id))
    
    try:
        session.mark_missed()
        flash('Session marked as missed.', 'warning')
    except Exception as e:
        flash(f'Error marking session as missed: {str(e)}', 'error')
    
    return redirect(url_for('manage_sessions', contract_id=contract.id))

@app.route('/sessions/<int:session_id>/complete-form', methods=['GET'])
@login_required
@contract_feature_required
def session_completion_form(session_id):
    """Show session completion form"""
    session = Session.query.options(
        db.joinedload(Session.proposal).joinedload(Proposal.contracts)
    ).get_or_404(session_id)
    user = get_current_user()
    
    # Verify access with null safety
    contract = session.get_contract()
    if not contract or (contract.student_id != user.id and contract.coach_id != user.id):
        flash('You do not have permission to complete this session.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if session can be completed
    if not session.can_be_completed():
        flash('This session cannot be completed at this time.', 'error')
        return redirect(url_for('manage_sessions', contract_id=contract.id))
    
    return render_template('sessions/session_completion.html', 
                         session=session,
                         current_user=user)

@app.route('/sessions/<int:session_id>/reschedule-approval', methods=['GET'])
@login_required
@contract_feature_required
def reschedule_approval_form(session_id):
    """Show reschedule approval form"""
    session = Session.query.options(
        db.joinedload(Session.proposal).joinedload(Proposal.contracts)
    ).get_or_404(session_id)
    user = get_current_user()
    
    # Verify access with null safety
    contract = session.get_contract()
    if not contract or (contract.student_id != user.id and contract.coach_id != user.id):
        flash('You do not have permission to approve this reschedule.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if there's a pending reschedule request
    if not session.reschedule_requested:
        flash('No reschedule request pending for this session.', 'error')
        return redirect(url_for('manage_sessions', contract_id=contract.id))
    
    # Check if user is the other party (not the one who requested)
    if session.reschedule_requested_by == user.current_role:
        flash('You cannot approve your own reschedule request.', 'error')
        return redirect(url_for('manage_sessions', contract_id=contract.id))
    
    return render_template('sessions/reschedule_approval.html', 
                         session=session,
                         current_user=user)

# Payment Routes
@app.route('/contracts/<int:contract_id>/pay', methods=['GET', 'POST'])
@login_required
@contract_feature_required
def contract_payment_old(contract_id):
    """Payment page for contract (legacy)"""
    contract = Contract.query.get_or_404(contract_id)
    user = get_current_user()
    
    # Verify access
    if contract.student_id != user.id:
        flash('You do not have permission to pay for this contract.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if payment is already made
    if contract.payment_status == 'paid':
        flash('Payment has already been made for this contract.', 'info')
        return redirect(url_for('view_contract', contract_id=contract.id))
    
    form = PaymentForm()
    
    if form.validate_on_submit():
        try:
            # TEMPORARY: Simulate successful payment for testing
            # In production, this would create a real Stripe payment intent
            contract.mark_payment_paid("pi_test_placeholder_123")
            
            # Send notification messages
            from models import Message
            
            # Notify student
            student_message = Message(
                sender_id=user.id,
                recipient_id=contract.student_id,
                content=f"✅ Payment received! Contract #{contract.contract_number} is now active. You can start scheduling sessions!"
            )
            db.session.add(student_message)
            
            # Notify coach
            coach_message = Message(
                sender_id=user.id,
                recipient_id=contract.coach_id,
                content=f"💰 Payment received for Contract #{contract.contract_number}! The contract is now active and ready for sessions."
            )
            db.session.add(coach_message)
            
            db.session.commit()
            
            flash('Payment completed successfully! Your contract is now active.', 'success')
            return redirect(url_for('payment_success', contract_id=contract.id))
            
        except Exception as e:
            app.logger.error(f"Payment processing failed: {e}")
            flash('Payment processing failed. Please try again.', 'error')
    
    return render_template('contracts/payment.html', 
                         contract=contract,
                         form=form,
                         config=app.config,
                         stripe_publishable_key=app.config.get('STRIPE_PUBLISHABLE_KEY'))

@app.route('/contracts/<int:contract_id>/payment-success', methods=['GET'])
@login_required
@contract_feature_required
def payment_success(contract_id):
    """Payment success page"""
    contract = Contract.query.get_or_404(contract_id)
    user = get_current_user()
    
    # Verify access
    if contract.student_id != user.id:
        flash('You do not have permission to view this contract.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if payment was actually successful
    if contract.payment_status != 'paid':
        flash('Payment verification failed. Please contact support.', 'error')
        return redirect(url_for('contract_payment', contract_id=contract.id))
    
    return render_template('contracts/payment_success.html', contract=contract)

@app.route('/contracts/<int:contract_id>/payment-cancel', methods=['GET'])
@login_required
@contract_feature_required
def payment_cancel(contract_id):
    """Payment cancel page"""
    contract = Contract.query.get_or_404(contract_id)
    user = get_current_user()
    
    # Verify access
    if contract.student_id != user.id:
        flash('You do not have permission to view this contract.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('contracts/payment_cancel.html', contract=contract)

# Payment webhook route
@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    from payment_utils import verify_webhook_signature, process_payment_webhook
    
    # Get the webhook secret from app config
    webhook_secret = app.config.get('STRIPE_WEBHOOK_SECRET')
    if not webhook_secret:
        app.logger.error("Stripe webhook secret not configured")
        return {'error': 'Webhook secret not configured'}, 500
    
    # Get the signature from the request headers
    signature = request.headers.get('Stripe-Signature')
    if not signature:
        app.logger.error("No Stripe signature found in request")
        return {'error': 'No signature'}, 400
    
    # Get the raw payload
    payload = request.get_data()
    
    try:
        # Verify the webhook signature
        if not verify_webhook_signature(payload, signature, webhook_secret):
            app.logger.error("Invalid webhook signature")
            return {'error': 'Invalid signature'}, 400
        
        # Parse the event
        import stripe
        event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
        
        # Process the webhook event
        success = process_payment_webhook(event.to_dict())
        
        if success:
            return {'status': 'success'}, 200
        else:
            app.logger.error("Failed to process webhook event")
            return {'error': 'Failed to process event'}, 500
            
    except ValueError as e:
        app.logger.error(f"Invalid payload: {e}")
        return {'error': 'Invalid payload'}, 400
    except stripe.error.SignatureVerificationError as e:
        app.logger.error(f"Invalid signature: {e}")
        return {'error': 'Invalid signature'}, 400
    except Exception as e:
        app.logger.error(f"Webhook error: {e}")
        return {'error': 'Webhook error'}, 500

@app.route('/contracts/<int:contract_id>/accept', methods=['GET', 'POST'])
@login_required
@coach_required
def accept_contract(contract_id):
    """Accept a contract as a coach"""
    contract = Contract.query.get_or_404(contract_id)
    current_user = get_current_user()
    
    # Verify the current user is the coach for this contract
    if contract.coach_id != current_user.id:
        flash('You do not have permission to accept this contract.', 'error')
        return redirect(url_for('dashboard'))
    
    if contract.status != 'awaiting_response':
        flash('This contract cannot be accepted.', 'error')
        return redirect(url_for('view_contract', contract_id=contract_id))
    
    try:
        # Update contract status to accepted (not active yet - needs payment)
        contract.status = 'accepted'
        contract.accepted_at = datetime.utcnow()
        db.session.commit()
        
        # Send email notification to student
        try:
            from email_utils import send_contract_accepted_email
            send_contract_accepted_email(contract)
        except:
            pass  # Email sending is optional
        
        # Create notification for student
        try:
            create_contract_notification(contract, 'contract_accepted')
        except:
            pass  # Notification creation is optional
        
        # Send in-app notification to student
        notification_message = Message(
            sender_id=current_user.id,
            recipient_id=contract.student_id,
            content=f"✅ **Contract Accepted!**\n\nI've accepted the contract for '{contract.proposal.learning_request.title}'. Please complete payment to start the learning journey.",
            sender_role='coach',
            recipient_role='student',
            message_type='SYSTEM'
        )
        db.session.add(notification_message)
        db.session.commit()
        
        flash('Contract accepted! The student has been notified and needs to complete payment.', 'success')
        return redirect(url_for('view_contract', contract_id=contract_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error accepting contract: {str(e)}', 'error')
        return redirect(url_for('view_contract', contract_id=contract_id))


@app.route('/contracts/<int:contract_id>/reject', methods=['GET', 'POST'])
@login_required
@coach_required
def reject_contract(contract_id):
    """Reject a contract as a coach"""
    contract = Contract.query.get_or_404(contract_id)
    current_user = get_current_user()
    
    # Verify the current user is the coach for this contract
    if contract.coach_id != current_user.id:
        flash('You do not have permission to reject this contract.', 'error')
        return redirect(url_for('dashboard'))
    
    if contract.status != 'awaiting_response':
        flash('This contract cannot be rejected.', 'error')
        return redirect(url_for('view_contract', contract_id=contract_id))
    
    try:
        # Get reason from request
        reason = request.json.get('reason', '') if request.is_json else request.form.get('reason', '')
        
        # Update contract status
        contract.status = 'rejected'
        contract.rejected_at = datetime.utcnow()
        contract.rejection_reason = reason
        db.session.commit()
        
        # Send email notification to student
        try:
            from email_utils import send_contract_rejected_email
            send_contract_rejected_email(contract)
        except:
            pass  # Email sending is optional
        
        # Create notification for student
        try:
            create_contract_notification(contract, 'contract_rejected')
        except:
            pass  # Notification creation is optional
        
        # Send in-app notification to student
        notification_message = Message(
            sender_id=current_user.id,
            recipient_id=contract.student_id,
            content=f"❌ **Contract Rejected**\n\nI've rejected the contract for '{contract.proposal.learning_request.title}'. You can create a new contract with different terms if you'd like to work together.",
            sender_role='coach',
            recipient_role='student',
            message_type='SYSTEM'
        )
        db.session.add(notification_message)
        db.session.commit()
        
        flash('Contract rejected. The student has been notified.', 'info')
        return redirect(url_for('conversation', user_id=contract.student_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error rejecting contract: {str(e)}', 'error')
        return redirect(url_for('view_contract', contract_id=contract_id))

@app.route('/contracts/<int:contract_id>/decline', methods=['POST'])
@login_required
@coach_required
def decline_contract(contract_id):
    """Decline a contract as a coach (alias for reject)"""
    return reject_contract(contract_id)


@app.route('/contracts/<int:contract_id>/payment', methods=['GET', 'POST'])
@login_required
@student_required
def contract_payment(contract_id):
    """Handle contract payment by student"""
    contract = Contract.query.get_or_404(contract_id)
    current_user = get_current_user()
    
    # Verify the current user is the student for this contract
    if contract.student_id != current_user.id:
        flash('You do not have permission to pay for this contract.', 'error')
        return redirect(url_for('dashboard'))
    
    # Only allow payment when contract status is 'accepted' (not 'active')
    if contract.status != 'accepted':
        flash('This contract is not ready for payment. It must be accepted by the coach first.', 'error')
        return redirect(url_for('view_contract', contract_id=contract_id))
    
    if not contract.can_be_paid():
        flash('This contract is not ready for payment.', 'error')
        return redirect(url_for('view_contract', contract_id=contract_id))
    
    if request.method == 'POST':
        try:
            # Check if we're in test mode
            test_mode = request.form.get('test_mode') == 'true' or app.config.get('TEST_MODE', False)
            
            if test_mode:
                # Test mode: bypass Stripe and simulate successful payment
                logging.info(f"Processing test payment for contract {contract.id} by user {current_user.id}")
                
                # Validate form data (basic validation even in test mode)
                card_number = request.form.get('card_number', '').strip()
                cardholder_name = request.form.get('cardholder_name', '').strip()
                
                if not card_number or not cardholder_name:
                    flash('Please provide card number and cardholder name for test payment.', 'error')
                    return render_template('contracts/payment.html', contract=contract, config=app.config)
                
                # Simulate payment processing delay
                import time
                time.sleep(1)  # Simulate processing time
                
                # Mark payment as successful
                contract.mark_payment_paid()
                contract.payment_completed_at = datetime.utcnow()
                
                # Add test mode indicator to payment record
                contract.payment_notes = f"TEST MODE PAYMENT - Card ending in {card_number[-4:]} - {cardholder_name}"
                
                # Contract is now active - sessions will be created when scheduled
                
                # Send email notifications to both student and coach
                from email_utils import send_payment_successful_email
                send_payment_successful_email(contract)
                
                # Send in-app notification to coach
                notification_message = Message(
                    sender_id=current_user.id,
                    recipient_id=contract.coach_id,
                    content=f"🧪 **Test Payment Completed!**\n\nTest payment has been completed for contract '{contract.proposal.learning_request.title}'. The learning journey can now begin!",
                    sender_role='student',
                    recipient_role='coach',
                    message_type='SYSTEM'
                )
                db.session.add(notification_message)
                db.session.commit()
                
                flash(f'Test payment completed successfully! Your contract is now active. You can now schedule your sessions.', 'success')
                return redirect(url_for('sessions_list'))
                
            else:
                # Production mode: integrate with Stripe
                # For now, we'll simulate payment success
                # In production, this would integrate with Stripe
                contract.mark_payment_paid()
                contract.payment_completed_at = datetime.utcnow()
                
                # Contract is now active - sessions will be created when scheduled
                
                # Send email notifications to both student and coach
                from email_utils import send_payment_successful_email
                send_payment_successful_email(contract)
                
                # Send in-app notification to coach
                notification_message = Message(
                    sender_id=current_user.id,
                    recipient_id=contract.coach_id,
                    content=f"💳 **Payment Completed!**\n\nPayment has been completed for contract '{contract.proposal.learning_request.title}'. The learning journey can now begin!",
                    sender_role='student',
                    recipient_role='coach',
                    message_type='SYSTEM'
                )
                db.session.add(notification_message)
                db.session.commit()
                
                flash(f'Payment completed successfully! Your contract is now active. You can now schedule your sessions.', 'success')
                return redirect(url_for('sessions_list'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Payment processing error: {str(e)}")
            flash(f'Error processing payment: {str(e)}', 'error')
    
    return render_template('contracts/payment.html', contract=contract, config=app.config)


@app.route('/contracts')
@login_required
def contracts_list():
    """List all contracts for the current user"""
    current_user = get_current_user()
    
    if current_user.current_role == 'student':
        contracts = Contract.query.filter_by(student_id=current_user.id).order_by(Contract.created_at.desc()).all()
    else:
        contracts = Contract.query.filter_by(coach_id=current_user.id).order_by(Contract.created_at.desc()).all()
    
    return render_template('contracts/contracts_list.html', contracts=contracts)


@app.route('/sessions')
@login_required
def sessions_list():
    """List all sessions for the current user grouped by relationships (coach-student pairs)"""
    current_user = get_current_user()
    
    # Auto-complete any sessions that should be completed and refresh contract progress
    def refresh_contract_progress(contract):
        """Refresh contract progress by checking all sessions"""
        try:
            # Get all sessions for this contract
            sessions = Session.query.filter_by(proposal_id=contract.proposal_id).all()
            
            # Check if any sessions need to be auto-completed
            for session in sessions:
                if session.should_be_completed():
                    session.auto_complete_if_needed()
            
            # Refresh the contract to get updated progress
            db.session.refresh(contract)
        except Exception as e:
            print(f"Error refreshing contract progress: {e}")
    
    if current_user.current_role == 'student':
        # Get active contracts where user is student
        contracts = Contract.query.filter(
            Contract.student_id == current_user.id,
            Contract.status == 'active'
        ).order_by(Contract.created_at.desc()).all()
        
        # Refresh contract progress for all contracts
        for contract in contracts:
            refresh_contract_progress(contract)
    else:
        # Get active contracts where user is coach
        contracts = Contract.query.filter(
            Contract.coach_id == current_user.id,
            Contract.status == 'active'
        ).order_by(Contract.created_at.desc()).all()
        
        # Refresh contract progress for all contracts
        for contract in contracts:
            refresh_contract_progress(contract)
    
    if current_user.current_role == 'student':
        # Group by coach (each coach is a relationship card)
        relationship_data = []
        for contract in contracts:
            try:
                if contract.coach:
                    # Get all sessions for this coach-student relationship
                    all_sessions = Session.query.filter_by(proposal_id=contract.proposal_id).all()
                    
                    sessions_with_date = [s for s in all_sessions if s.scheduled_at is not None]
                    sessions_without_date = [s for s in all_sessions if s.scheduled_at is None]
                    
                    # Sort sessions with dates in descending order
                    sessions_with_date.sort(key=lambda x: x.scheduled_at, reverse=True)
                    sessions = sessions_with_date + sessions_without_date
                    
                    # Get learning request title
                    learning_request_title = "Unknown Learning Request"
                    if contract.proposal and contract.proposal.learning_request:
                        learning_request_title = contract.proposal.learning_request.title
                    
                    relationship_data.append({
                        'relationship_type': 'coach',
                        'partner': contract.coach,
                        'partner_name': f"{contract.coach.first_name} {contract.coach.last_name}",
                        'contract': contract,
                        'sessions': sessions,
                        'learning_request_title': learning_request_title,
                        'total_sessions': contract.total_sessions,
                        'completed_sessions': contract.completed_sessions,
                        'progress_percentage': contract.get_progress_percentage(),
                        'next_session': contract.get_next_session()
                    })
            except Exception as e:
                print(f"Error processing contract {contract.id}: {str(e)}")
                continue
                
    else:
        # Group by student (each student is a relationship card)
        relationship_data = []
        for contract in contracts:
            try:
                if contract.student:
                    # Get all sessions for this coach-student relationship
                    all_sessions = Session.query.filter_by(proposal_id=contract.proposal_id).all()
                    

                    
                    sessions_with_date = [s for s in all_sessions if s.scheduled_at is not None]
                    sessions_without_date = [s for s in all_sessions if s.scheduled_at is None]
                    
                    # Sort sessions with dates in descending order
                    sessions_with_date.sort(key=lambda x: x.scheduled_at, reverse=True)
                    sessions = sessions_with_date + sessions_without_date
                    
                    # Get learning request_title
                    learning_request_title = "Unknown Learning Request"
                    if contract.proposal and contract.proposal.learning_request:
                        learning_request_title = contract.proposal.learning_request.title
                    
                    relationship_data.append({
                        'relationship_type': 'student',
                        'partner': contract.student,
                        'partner_name': f"{contract.student.first_name} {contract.student.last_name}",
                        'contract': contract,
                        'sessions': sessions,
                        'learning_request_title': learning_request_title,
                        'total_sessions': contract.total_sessions,
                        'completed_sessions': contract.completed_sessions,
                        'progress_percentage': contract.get_progress_percentage(),
                        'next_session': contract.get_next_session()
                    })
            except Exception as e:
                print(f"Error processing contract {contract.id}: {str(e)}")
                continue
    
    # Get upcoming and recent sessions for enhanced view
    upcoming_sessions = []
    recent_sessions = []
    
    for data in relationship_data:
        for session in data['sessions']:
            if session.status in ['scheduled', 'active']:
                upcoming_sessions.append(session)
            elif session.status == 'completed':
                recent_sessions.append(session)
    
    # Sort upcoming sessions by scheduled time
    upcoming_sessions.sort(key=lambda x: x.scheduled_at or datetime.max)
    
    # Sort recent sessions by completion time (most recent first)
    recent_sessions.sort(key=lambda x: x.completed_date or datetime.min, reverse=True)
    
    # Limit recent sessions to last 10
    recent_sessions = recent_sessions[:10]
    
    return render_template('sessions/sessions_list_enhanced.html', 
                         relationship_data=relationship_data,
                         upcoming_sessions=upcoming_sessions,
                         recent_sessions=recent_sessions)


@app.route('/sessions/<int:session_id>')
@login_required
def join_session(session_id):
    """View session details and auto-activate if needed"""
    session = Session.query.get_or_404(session_id)
    current_user = get_current_user()
    
    # Get contract for validation
    contract = session.get_contract()
    if not contract:
        flash('Session not found.', 'error')
        return redirect(url_for('sessions_list'))
    
    # Check if user is authorized to view this session
    if current_user.id not in [contract.coach_id, contract.student_id]:
        flash('You are not authorized to view this session.', 'error')
        return redirect(url_for('sessions_list'))
    
    # Auto-activate meeting if it's time and not already activated
    if session.status == 'scheduled' and session.can_auto_activate() and not session.auto_activated:
        try:
            if session.auto_activate_meeting():
                app.logger.info(f"Auto-activated session {session_id} from join_session route")
                flash('Meeting has been automatically activated!', 'success')
            else:
                app.logger.warning(f"Failed to auto-activate session {session_id}")
        except Exception as e:
            app.logger.error(f"Error auto-activating session {session_id}: {e}")
    
    return render_template('sessions/join_session.html', 
                         session=session, 
                         contract=contract,
                         current_user=current_user)






@app.route('/sessions/<int:session_id>/start', methods=['POST'])
@login_required
def start_session(session_id):
    """Manually start a session for testing"""
    session = Session.query.get_or_404(session_id)
    current_user = get_current_user()
    
    # Validate user can access this session
    contract = session.get_contract()
    if not contract or (current_user.id not in [contract.coach_id, contract.student_id]):
        flash('You do not have permission to access this session.', 'error')
        return redirect(url_for('sessions_list'))
    
    try:
        if session.start_meeting():
            flash('Session started successfully!', 'success')
        else:
            flash('Failed to start session.', 'error')
    except Exception as e:
        flash(f'Error starting session: {str(e)}', 'error')
    
    return redirect(url_for('join_session', session_id=session.id))

@app.route('/sessions/<int:session_id>/waiting-room', methods=['GET'])
@login_required
def waiting_room(session_id):
    """Waiting room for early join participants"""
    session = Session.query.get_or_404(session_id)
    current_user = get_current_user()
    
    # Validate user can access this session
    contract = session.get_contract()
    if not contract or (current_user.id not in [contract.coach_id, contract.student_id]):
        flash('You do not have permission to access this session.', 'error')
        return redirect(url_for('sessions_list'))
    
    # Check if user can join early
    if not session.can_join_early() and session.status != 'active':
        flash('Early join is not available for this session.', 'error')
        return redirect(url_for('join_session', session_id=session.id))
    
    return render_template('sessions/waiting_room.html', session=session, current_user=current_user)

@app.route('/api/coaches/<int:coach_id>/availability', methods=['POST'])
@login_required
def check_coach_availability_api(coach_id):
    """Check coach availability for a specific time slot"""
    try:
        data = request.get_json()
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        duration_minutes = data.get('duration_minutes', 60)
        exclude_session_id = data.get('exclude_session_id')
        
        if not start_time_str:
            return jsonify({'error': 'start_time is required'}), 400
        
        # Parse datetime
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        if end_time_str:
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        else:
            end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Check availability
        from availability_manager import check_coach_availability
        result = check_coach_availability(coach_id, start_time, end_time, exclude_session_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error checking coach availability: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/coaches/<int:coach_id>/availability-slots', methods=['GET'])
@login_required
def get_coach_availability_slots_api(coach_id):
    """Get available time slots for a coach on a specific date"""
    try:
        date_str = request.args.get('date')
        duration_minutes = int(request.args.get('duration_minutes', 60))
        
        if not date_str:
            return jsonify({'error': 'date parameter is required'}), 400
        
        # Parse date
        date = datetime.fromisoformat(date_str).date()
        date_dt = datetime.combine(date, datetime.min.time())
        
        # Get availability slots
        from availability_manager import get_coach_availability_slots
        slots = get_coach_availability_slots(coach_id, date_dt, duration_minutes)
        
        return jsonify({
            'coach_id': coach_id,
            'date': date_str,
            'duration_minutes': duration_minutes,
            'slots': slots
        })
        
    except Exception as e:
        logger.error(f"Error getting coach availability slots: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/book-session/<int:coach_id>', methods=['GET', 'POST'])
@login_required
def enhanced_book_session(coach_id):
    """Enhanced booking interface with calendar picker"""
    try:
        from models import User, Coach
        
        # Get coach
        coach = Coach.query.get_or_404(coach_id)
        
        if request.method == 'POST':
            # Handle booking submission
            selected_date = request.form.get('selected_date')
            selected_time = request.form.get('selected_time')
            duration_minutes = int(request.form.get('duration_minutes', 60))
            notes = request.form.get('notes', '')
            timezone = request.form.get('timezone', 'UTC')
            
            if not selected_date or not selected_time:
                flash('Please select a date and time', 'error')
                return redirect(url_for('enhanced_book_session', coach_id=coach_id))
            
            # Parse datetime
            datetime_str = f"{selected_date} {selected_time}"
            scheduled_datetime = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            
            # Convert to UTC if user has timezone
            current_user = get_current_user()
            if timezone != 'UTC':
                from timezone_utils import convert_from_user_timezone
                scheduled_datetime = convert_from_user_timezone(scheduled_datetime, timezone)
            
            # Check availability
            from availability_manager import check_coach_availability
            end_time = scheduled_datetime + timedelta(minutes=duration_minutes)
            availability_result = check_coach_availability(coach_id, scheduled_datetime, end_time)
            
            if not availability_result['available']:
                flash(f'Time slot not available: {availability_result["message"]}', 'error')
                return redirect(url_for('enhanced_book_session', coach_id=coach_id))
            
            # Create session (you'll need to implement this based on your session creation logic)
            # For now, we'll just show a success message
            flash('Session booked successfully!', 'success')
            return redirect(url_for('sessions_list'))
        
        # GET request - show booking interface
        current_user = get_current_user()
        
        # Get timezone options
        from timezone_utils import get_common_timezones
        timezones = get_common_timezones()
        
        # Get current month calendar data
        from availability_manager import get_coach_calendar_days
        current_date = datetime.now()
        calendar_days = get_coach_calendar_days(coach_id, current_date.year, current_date.month)
        
        return render_template('sessions/enhanced_booking.html',
                             coach=coach,
                             session_duration=60,  # Default duration
                             timezones=timezones,
                             user_timezone=current_user.timezone or 'UTC',
                             current_month=f"{current_date.strftime('%B')} {current_date.year}",
                             calendar_days=calendar_days)
        
    except Exception as e:
        logger.error(f"Error in enhanced booking: {e}")
        flash('Error loading booking interface', 'error')
        return redirect(url_for('sessions_list'))

@app.route('/api/coaches/<int:coach_id>/calendar', methods=['GET'])
@login_required
def get_coach_calendar(coach_id):
    """Get calendar data for a coach for a specific month"""
    try:
        year = int(request.args.get('year', datetime.now().year))
        month = int(request.args.get('month', datetime.now().month))
        
        # Get calendar days for the month
        from availability_manager import get_coach_calendar_days
        calendar_data = get_coach_calendar_days(coach_id, year, month)
        
        return jsonify({
            'coach_id': coach_id,
            'year': year,
            'month': month,
            'days': calendar_data
        })
        
    except Exception as e:
        logger.error(f"Error getting coach calendar: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/coaches/<int:coach_id>/suggest-times', methods=['POST'])
@login_required
def suggest_alternative_times_api(coach_id):
    """Suggest alternative times when requested slot is not available"""
    try:
        data = request.get_json()
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        duration_minutes = data.get('duration_minutes', 60)
        
        if not start_time_str:
            return jsonify({'error': 'start_time is required'}), 400
        
        # Parse datetime
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        if end_time_str:
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
        else:
            end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Get suggestions
        from availability_manager import suggest_alternative_times
        suggestions = suggest_alternative_times(coach_id, start_time, end_time, duration_minutes)
        
        return jsonify({
            'coach_id': coach_id,
            'requested_start': start_time_str,
            'requested_end': end_time_str,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f"Error suggesting alternative times: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/sessions/<int:session_id>/status', methods=['GET'])
@login_required
def check_meeting_status(session_id):
    """Check meeting status for auto-refresh and auto-activate if needed"""
    session = Session.query.get_or_404(session_id)
    current_user = get_current_user()
    
    # Validate user can access this session
    contract = session.get_contract()
    if not contract or (current_user.id not in [contract.coach_id, contract.student_id]):
        return jsonify({'error': 'Access denied'}), 403
    
    # Auto-activate meeting if it's time and not already activated
    if session.status == 'scheduled' and session.can_auto_activate() and not session.auto_activated:
        try:
            if session.auto_activate_meeting():
                app.logger.info(f"Auto-activated session {session_id}")
            else:
                app.logger.warning(f"Failed to auto-activate session {session_id}")
        except Exception as e:
            app.logger.error(f"Error auto-activating session {session_id}: {e}")
    
    # Auto-complete session if it has passed its duration
    try:
        if session.auto_complete_if_needed():
            app.logger.info(f"Auto-completed session {session_id}")
    except Exception as e:
        app.logger.error(f"Error auto-completing session {session_id}: {e}")
    
    return jsonify({
        'status': session.status,
        'can_join_early': session.can_join_early(),
        'scheduled_at': session.scheduled_at.isoformat() if session.scheduled_at else None,
        'meeting_started_at': session.meeting_started_at.isoformat() if session.meeting_started_at else None
    })


# Google Meet Integration Routes
@app.route('/session/<int:session_id>/create-google-meet')
@login_required
def create_google_meet(session_id):
    """Open Google Meet creation in new tab"""
    print(f"DEBUG: create_google_meet called with session_id: {session_id}")
    
    try:
        from models import ScheduledSession
        from google_meet_utils import create_google_meet_url, format_meeting_title
        
        session = ScheduledSession.query.filter_by(session_id=session_id).first_or_404()
        print(f"DEBUG: Found session: {session.id}")
        
        # Verify user is the coach
        current_user = get_current_user()
        if session.coach_id != current_user.id:
            flash('Only the coach can create meetings', 'error')
            return redirect(url_for('join_session', session_id=session_id))
        
        # Generate Google Meet creation URL
        print(f"DEBUG: About to call format_meeting_title")
        title = format_meeting_title(session)
        print(f"DEBUG: Title generated: {title}")
        
        print(f"DEBUG: About to call create_google_meet_url")
        meet_url = create_google_meet_url(title, session.scheduled_at, session.duration_minutes)
        print(f"DEBUG: Generated meet_url: {meet_url}")
        
        return redirect(meet_url)
        
    except Exception as e:
        print(f"DEBUG: Error in create_google_meet: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error creating Google Meet: {str(e)}', 'error')
        return redirect(url_for('meeting_setup', session_id=session_id))

@app.route('/session/<int:scheduled_session_id>/save-meeting-link', methods=['POST'])
@login_required
def save_meeting_link(scheduled_session_id):
    """Save Google Meet link to scheduled session"""
    from models import ScheduledSession
    from google_meet_utils import validate_google_meet_url
    from datetime import datetime
    
    # Get scheduled session by its primary key (id), not by session_id field
    from app import db
    session = ScheduledSession.query.filter_by(id=scheduled_session_id).options(
        db.joinedload(ScheduledSession.coach),
        db.joinedload(ScheduledSession.student)
    ).first_or_404()
    
    # Validate that this is the correct meeting instance
    if not session:
        flash('Scheduled session not found', 'error')
        return redirect(url_for('sessions_list'))
    
    # Validate coach ownership
    if session.coach_id != get_current_user().id:
        flash('Only the coach can add meeting links', 'error')
        return redirect(url_for('sessions_list'))
    
    # Additional validation: ensure this is an active session
    # Allow meeting links for scheduled, confirmed, and started sessions
    # Only block completed, cancelled, and no_show sessions
    print(f"DEBUG: save_meeting_link - Checking session status: '{session.status}'")
    if session.status in ['completed', 'cancelled', 'no_show']:
        print(f"DEBUG: save_meeting_link - Session status '{session.status}' is blocked")
        flash(f'Cannot add meeting links to {session.status} sessions', 'error')
        return redirect(url_for('sessions_list'))
    else:
        print(f"DEBUG: save_meeting_link - Session status '{session.status}' is allowed")
    
    # Allow meeting link setup at any time (no time restrictions)
    # Coaches can set up Google Meet meetings in advance for better planning
    print(f"DEBUG: save_meeting_link - Meeting scheduled for: {session.scheduled_at}")
    print(f"DEBUG: save_meeting_link - Current time: {datetime.now(timezone.utc)}")
    print(f"DEBUG: save_meeting_link - No time restrictions - meeting links can be added anytime")
    
    meeting_url = request.form.get('meeting_url')
    meeting_notes = request.form.get('meeting_notes', '')
    
    # Log the meeting link assignment for debugging
    print(f"DEBUG: save_meeting_link - Updating ScheduledSession ID: {session.id}")
    print(f"DEBUG: save_meeting_link - Session ID (foreign key): {session.session_id}")
    print(f"DEBUG: save_meeting_link - Coach ID: {session.coach_id}")
    print(f"DEBUG: save_meeting_link - Student ID: {session.student_id}")
    print(f"DEBUG: save_meeting_link - Session Status: {session.status}")
    print(f"DEBUG: save_meeting_link - Meeting URL: {meeting_url}")
    
    if meeting_url and validate_google_meet_url(meeting_url):
        session.google_meet_url = meeting_url
        session.meeting_status = 'created'
        session.meeting_created_at = datetime.now(timezone.utc)
        session.meeting_created_by = get_current_user().id
        session.meeting_notes = meeting_notes
        
        db.session.commit()
        
        # Send chat notification to student
        try:
            from notification_utils import create_meeting_link_notification
            create_meeting_link_notification(session, meeting_url)
        except Exception as e:
            print(f"Warning: Could not create chat notification: {e}")
        
        # Send email notification to student
        try:
            from email_utils import send_email
            send_email(
                to_email=session.student.email,
                subject=f"Meeting Link Ready - {session.coach.first_name}",
                template='notifications/meeting_link_ready.html',
                session=session
            )
        except Exception as e:
            print(f"Warning: Could not send email notification: {e}")
        
        flash(f'Meeting link added successfully to Session #{session.session_id}! Student has been notified. Meeting links can be added anytime for better planning.', 'success')
    else:
        flash('Please provide a valid Google Meet link', 'error')
    
    return redirect(url_for('sessions_list'))

@app.route('/session/<int:session_id>/meeting-setup')
@login_required
def meeting_setup(session_id):
    """Load meeting setup form via AJAX"""
    from models import ScheduledSession, Session
    from google_meet_utils import create_google_meet_url, format_meeting_title
    from app import db
    
    # Debug: Check authentication
    current_user = get_current_user()
    print(f"DEBUG: meeting_setup - current_user: {current_user}")
    print(f"DEBUG: meeting_setup - Flask session keys: {list(flask_session.keys())}")
    print(f"DEBUG: meeting_setup - user_id in Flask session: {flask_session.get('user_id')}")
    
    if current_user:
        print(f"DEBUG: meeting_setup - user.id: {current_user.id}")
        print(f"DEBUG: meeting_setup - user.is_coach: {current_user.is_coach}")
        print(f"DEBUG: meeting_setup - user.current_role: {current_user.current_role}")
        print(f"DEBUG: meeting_setup - user.coach_profile: {getattr(current_user, 'coach_profile', None)}")
        print(f"DEBUG: meeting_setup - user.is_student: {current_user.is_student}")
        print(f"DEBUG: meeting_setup - user.email: {current_user.email}")
    else:
        print("DEBUG: meeting_setup - current_user is None!")
        print("DEBUG: meeting_setup - This suggests a session issue!")
        print("DEBUG: meeting_setup - Redirecting to login...")
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('login'))
    
    # Check if user has a role set, if not set it
    if not current_user.current_role:
        print(f"DEBUG: meeting_setup - Setting initial role for user {current_user.id}")
        current_user.set_initial_role()
        from app import db
        db.session.commit()
        # Refresh the user object
        current_user = get_current_user()
        print(f"DEBUG: meeting_setup - After setting role: current_role = {current_user.current_role}")
    
    # Check if user is a coach
    if not current_user.is_coach:
        print(f"DEBUG: meeting_setup - User {current_user.id} is not a coach (is_coach = {current_user.is_coach})")
        flash('Only coaches can access the meeting setup page.', 'error')
        return redirect(url_for('dashboard'))
    
    print(f"DEBUG: meeting_setup - User {current_user.id} is a coach, proceeding...")
    
    # Check if user has a coach profile
    if not hasattr(current_user, 'coach_profile') or not current_user.coach_profile:
        print(f"DEBUG: meeting_setup - User {current_user.id} doesn't have a coach profile, creating one...")
        from models import CoachProfile
        from app import db
        coach_profile = CoachProfile(user_id=current_user.id)
        db.session.add(coach_profile)
        db.session.commit()
        print(f"DEBUG: meeting_setup - Coach profile created for user {current_user.id}")
    
    # Try to find the session - first check ScheduledSession, then Session
    session_obj = None
    
    # First try ScheduledSession
    try:
        session_obj = ScheduledSession.query.filter_by(session_id=session_id).options(
            db.joinedload(ScheduledSession.coach),
            db.joinedload(ScheduledSession.student)
        ).first()
        if session_obj:
            print(f"DEBUG: meeting_setup - Found ScheduledSession with session_id {session_id}")
    except Exception as e:
        print(f"DEBUG: meeting_setup - Error querying ScheduledSession: {e}")
    
    # If not found, try Session
    if not session_obj:
        try:
            session_obj = Session.query.get(session_id)
            if session_obj:
                print(f"DEBUG: meeting_setup - Found Session with id {session_id}")
                # Create a ScheduledSession for this Session if it doesn't exist
                existing_scheduled = ScheduledSession.query.filter_by(session_id=session_id).first()
                if not existing_scheduled:
                    print(f"DEBUG: meeting_setup - Creating ScheduledSession for Session {session_id}")
                    # Get the contract to find coach and student
                    contract = session_obj.get_contract()
                    if contract:
                        scheduled_session = ScheduledSession(
                            session_id=session_id,
                            coach_id=contract.coach_id,
                            student_id=contract.student_id,
                            scheduled_at=session_obj.scheduled_at or session_obj.scheduled_date,
                            duration_minutes=session_obj.duration_minutes or 60,
                            timezone=session_obj.timezone or 'UTC',
                            session_type='paid',
                            status=session_obj.status,
                            payment_status='paid'
                        )
                        db.session.add(scheduled_session)
                        db.session.commit()
                        session_obj = scheduled_session
                        print(f"DEBUG: meeting_setup - Created ScheduledSession {scheduled_session.id}")
                    else:
                        print(f"DEBUG: meeting_setup - No contract found for Session {session_id}")
                        flash('Session contract not found.', 'error')
                        return redirect(url_for('dashboard'))
        except Exception as e:
            print(f"DEBUG: meeting_setup - Error querying Session: {e}")
    
    # If still no session found, return 404
    if not session_obj:
        print(f"DEBUG: meeting_setup - No session found for id {session_id}")
        flash('Session not found.', 'error')
        return redirect(url_for('dashboard'))
    
    # Verify user is the coach for this specific session
    if hasattr(session_obj, 'coach_id'):
        coach_id = session_obj.coach_id
    else:
        # For Session objects, get coach_id from contract
        contract = session_obj.get_contract()
        if contract:
            coach_id = contract.coach_id
        else:
            flash('Session contract not found.', 'error')
            return redirect(url_for('dashboard'))
    
    if coach_id != current_user.id:
        print(f"DEBUG: meeting_setup - User {current_user.id} is not the coach for session {session_id}")
        flash('You can only setup meetings for your own sessions.', 'error')
        return redirect(url_for('dashboard'))
    
    print(f"DEBUG: meeting_setup - User {current_user.id} is the coach for session {session_id}, proceeding...")
    
    # Generate Google Meet creation URL
    title = format_meeting_title(session_obj)
    
    # Get scheduled time and duration
    scheduled_time = getattr(session_obj, 'scheduled_at', None)
    if not scheduled_time:
        scheduled_time = getattr(session_obj, 'scheduled_date', None)
    
    duration = getattr(session_obj, 'duration_minutes', 60)
    
    if scheduled_time:
        meet_url = create_google_meet_url(title, scheduled_time, duration)
    else:
        # Default to tomorrow if no time set
        from datetime import datetime, timedelta, timezone
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        tomorrow = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        meet_url = create_google_meet_url(title, tomorrow, duration)
    
    # Generate Google Meet creation URL
    title = format_meeting_title(session_obj)
    
    # Get scheduled time and duration
    scheduled_time = getattr(session_obj, 'scheduled_at', None)
    if not scheduled_time:
        scheduled_time = getattr(session_obj, 'scheduled_date', None)
    
    duration = getattr(session_obj, 'duration_minutes', 60)
    
    if scheduled_time:
        meet_url = create_google_meet_url(title, scheduled_time, duration)
    else:
        # Default to tomorrow if no time set
        from datetime import datetime, timedelta, timezone
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        tomorrow = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        meet_url = create_google_meet_url(title, tomorrow, duration)
    
    # Return the meeting setup form HTML
    return render_template('google_meet/meeting_setup.html', session=session_obj, meet_url=meet_url)

@app.route('/session/<int:session_id>/join-meeting')
@login_required
def join_meeting(session_id):
    """Show meeting join page for both coaches and students"""
    from models import ScheduledSession
    
    session = ScheduledSession.query.filter_by(session_id=session_id).first_or_404()
    current_user = get_current_user()
    
    # Allow both coach and student to join the meeting
    if current_user.id not in [session.student_id, session.coach_id]:
        flash('You are not authorized to join this meeting', 'error')
        return redirect(url_for('join_session', session_id=session_id))
    
    return render_template('google_meet/meeting_join.html', session=session)

@app.route('/session/<int:session_id>/meeting-dashboard')
@login_required
def meeting_dashboard(session_id):
    """Show meeting dashboard for both users"""
    from models import ScheduledSession
    
    session = ScheduledSession.query.filter_by(session_id=session_id).first_or_404()
    
    if session.coach_id != get_current_user().id and session.student_id != get_current_user().id:
        flash('You can only access your own sessions', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('google_meet/meeting_dashboard.html', session=session)

# Google Meet Integration for ScheduledCall (Main Scheduling System)
@app.route('/calls/<int:call_id>/meeting-setup')
@login_required
def call_meeting_setup(call_id):
    """Load meeting setup form for ScheduledCall via AJAX"""
    from models import ScheduledCall
    from google_meet_utils import create_google_meet_url, format_meeting_title
    from app import db
    
    # Debug: Check authentication
    current_user = get_current_user()
    print(f"DEBUG: call_meeting_setup - current_user: {current_user}")
    
    if not current_user:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('login'))
    
    # Check if user has a role set, if not set it
    if not current_user.current_role:
        current_user.set_initial_role()
        get_db().session.commit()
        current_user = get_current_user()
    
    # Check if user is a coach
    if not current_user.is_coach:
        flash('Only coaches can access the meeting setup page.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get call with relationships loaded
    call = ScheduledCall.query.options(
        db.joinedload(ScheduledCall.coach),
        db.joinedload(ScheduledCall.student)
    ).get_or_404(call_id)
    
    # Verify user is the coach for this specific call
    if call.coach_id != current_user.id:
        flash('You can only setup meetings for your own calls.', 'error')
        return redirect(url_for('dashboard'))
    
    # Generate Google Meet creation URL
    title = format_meeting_title(call)
    meet_url = create_google_meet_url(title, call.scheduled_at, call.duration_minutes)
    
    # Return the meeting setup form HTML
    return render_template('google_meet/call_meeting_setup.html', call=call, meet_url=meet_url)

@app.route('/calls/<int:call_id>/create-google-meet')
@login_required
def create_call_google_meet(call_id):
    """Open Google Meet creation in new tab for ScheduledCall"""
    try:
        from models import ScheduledCall
        from google_meet_utils import create_google_meet_url, format_meeting_title
        
        call = ScheduledCall.query.get_or_404(call_id)
        
        # Verify user is the coach
        current_user = get_current_user()
        if call.coach_id != current_user.id:
            flash('Only the coach can create meetings', 'error')
            return redirect(url_for('view_call', call_id=call_id))
        
        # Generate Google Meet creation URL
        title = format_meeting_title(call)
        meet_url = create_google_meet_url(title, call.scheduled_at, call.duration_minutes)
        
        return redirect(meet_url)
        
    except Exception as e:
        flash(f'Error creating Google Meet: {str(e)}', 'error')
        return redirect(url_for('call_meeting_setup', call_id=call_id))

@app.route('/calls/<int:call_id>/save-meeting', methods=['POST'])
@login_required
def save_call_meeting_link(call_id):
    """Save Google Meet link to ScheduledCall"""
    from models import ScheduledCall, db
    from google_meet_utils import validate_google_meet_url
    from datetime import datetime
    
    # Get call with relationships loaded
    call = ScheduledCall.query.options(
        db.joinedload(ScheduledCall.coach),
        db.joinedload(ScheduledCall.student)
    ).get_or_404(call_id)
    
    if call.coach_id != get_current_user().id:
        flash('Only the coach can add meeting links', 'error')
        return redirect(url_for('view_call', call_id=call_id))
    
    meeting_url = request.form.get('meeting_url')
    meeting_notes = request.form.get('meeting_notes', '')
    
    if meeting_url and validate_google_meet_url(meeting_url):
        call.google_meet_url = meeting_url
        call.meeting_status = 'created'
        call.meeting_created_at = datetime.utcnow()
        call.meeting_created_by = get_current_user().id
        call.meeting_notes = meeting_notes
        
        db.session.commit()
        
        # Send notification to student
        from email_utils import send_email
        send_email(
            to_email=call.student.email,
            subject=f"Meeting Link Ready - {call.coach.first_name}",
            template='notifications/meeting_link_ready.html',
            call=call
        )
        
        flash('Meeting link added successfully! Student has been notified.', 'success')
    else:
        flash('Please provide a valid Google Meet link', 'error')
    
    return redirect(url_for('call_meeting_setup', call_id=call_id))


# Notification routes
@app.route('/api/notifications')
@login_required
def get_notifications():
    """Get recent notifications for the current user"""
    try:
        user = get_current_user()
        
        # Check if notification table exists
        from sqlalchemy import text
        try:
            result = get_db().session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'notification'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                # Return empty notifications if table doesn't exist
                return jsonify({
                    'success': True,
                    'notifications': []
                })
        except Exception:
            # If we can't check table existence, assume it doesn't exist
            return jsonify({
                'success': True,
                'notifications': []
            })
        
        # Table exists, get notifications
        notifications = Notification.get_recent_notifications(user.id, limit=20)
        return jsonify({
            'success': True,
            'notifications': [notification.to_dict() for notification in notifications]
        })
    except Exception as e:
        # Return empty notifications on any error
        return jsonify({
            'success': True,
            'notifications': []
        })

@app.route('/api/notifications/unread-count')
@login_required
def get_unread_count():
    """Get unread notification count for the current user"""
    try:
        user = get_current_user()
        
        # Check if notification table exists
        from sqlalchemy import text
        try:
            result = get_db().session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'notification'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                # Return 0 count if table doesn't exist
                return jsonify({
                    'success': True,
                    'count': 0
                })
        except Exception:
            # If we can't check table existence, assume it doesn't exist
            return jsonify({
                'success': True,
                'count': 0
            })
        
        # Table exists, get count
        count = Notification.get_unread_count(user.id)
        return jsonify({
            'success': True,
            'count': count
        })
    except Exception as e:
        # Return 0 count on any error
        return jsonify({
            'success': True,
            'count': 0
        })

@app.route('/api/notifications/<int:notification_id>/mark-read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a specific notification as read"""
    try:
        user = get_current_user()
        
        # Check if notification table exists
        from sqlalchemy import text
        try:
            result = get_db().session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'notification'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                # Return success if table doesn't exist (nothing to mark)
                return jsonify({'success': True})
        except Exception:
            # If we can't check table existence, return success
            return jsonify({'success': True})
        
        # Table exists, mark as read
        success = Notification.mark_as_read(notification_id, user.id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Notification not found'}), 404
    except Exception as e:
        # Return success on any error
        return jsonify({'success': True})

@app.route('/api/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read for the current user"""
    try:
        user = get_current_user()
        
        # Check if notification table exists
        from sqlalchemy import text
        try:
            result = get_db().session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'notification'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                # Return success if table doesn't exist (nothing to mark)
                return jsonify({'success': True})
        except Exception:
            # If we can't check table existence, return success
            return jsonify({'success': True})
        
        # Table exists, mark all as read
        Notification.mark_all_as_read(user.id)
        return jsonify({'success': True})
    except Exception as e:
        # Return success on any error
        return jsonify({'success': True})

@app.route('/notifications')
@login_required
def notifications_page():
    """Notifications page showing all notifications"""
    try:
        user = get_current_user()
        
        # Check if notification table exists
        from sqlalchemy import text
        try:
            result = get_db().session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'notification'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                # Return empty notifications if table doesn't exist
                return render_template('notifications/notifications.html', notifications=[])
        except Exception:
            # If we can't check table existence, return empty notifications
            return render_template('notifications/notifications.html', notifications=[])
        
        # Table exists, get notifications
        notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()
        return render_template('notifications/notifications.html', notifications=notifications)
    except Exception as e:
        # Return empty notifications on any error
        return render_template('notifications/notifications.html', notifications=[])

@app.route('/admin/fix-database')
def admin_fix_database():
    """Admin route to manually trigger database schema fixes"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        from sqlalchemy import text
        
        # Check database type
        db_url = str(db.engine.url)
        is_postgresql = 'postgresql' in db_url.lower()
        
        if not is_postgresql:
            flash('This fix is only for PostgreSQL production databases', 'warning')
            return redirect(url_for('admin_dashboard'))
        
        # Add message_type column to message table if it doesn't exist
        try:
            db.session.execute(text("ALTER TABLE message ADD COLUMN message_type VARCHAR(20) DEFAULT 'TEXT';"))
            db.session.commit()
            flash('Added message_type column to message table', 'success')
        except Exception as e:
            db.session.rollback()
            if "already exists" in str(e) or "duplicate column name" in str(e):
                flash('message_type column already exists', 'info')
            else:
                flash(f'Error adding message_type column: {e}', 'error')
        
        # Add contract acceptance columns if they don't exist - each in separate transaction
        try:
            db.session.execute(text("ALTER TABLE contract ADD COLUMN accepted_at TIMESTAMP;"))
            db.session.commit()
            flash('Added accepted_at column to contract table', 'success')
        except Exception as e:
            db.session.rollback()
            if "already exists" in str(e) or "duplicate column name" in str(e):
                flash('accepted_at column already exists', 'info')
            else:
                flash(f'Error adding accepted_at column: {e}', 'error')
        
        try:
            db.session.execute(text("ALTER TABLE contract ADD COLUMN declined_at TIMESTAMP;"))
            db.session.commit()
            flash('Added declined_at column to contract table', 'success')
        except Exception as e:
            db.session.rollback()
            if "already exists" in str(e) or "duplicate column name" in str(e):
                flash('declined_at column already exists', 'info')
            else:
                flash(f'Error adding declined_at column: {e}', 'error')
        
        try:
            db.session.execute(text("ALTER TABLE contract ADD COLUMN payment_completed_at TIMESTAMP;"))
            db.session.commit()
            flash('Added payment_completed_at column to contract table', 'success')
        except Exception as e:
            db.session.rollback()
            if "already exists" in str(e) or "duplicate column name" in str(e):
                flash('payment_completed_at column already exists', 'info')
            else:
                flash(f'Error adding payment_completed_at column: {e}', 'error')
        
        # Note: Removed contract status reset to prevent active contracts from being reset to pending
        flash('Skipped contract status reset to preserve active contracts', 'info')
        flash('Database schema fixes applied successfully!', 'success')
        
    except Exception as e:
        flash(f'Error applying database fixes: {e}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin_dashboard'))

# Contract Action API Endpoints
@app.route('/api/contracts/accept', methods=['POST'])
@login_required
def api_accept_contract():
    """API endpoint to accept a contract from message"""
    try:
        data = request.get_json()
        message_id = data.get('message_id')
        contract_data = data.get('contract_data', {})
        
        if not message_id:
            return jsonify({'success': False, 'error': 'Message ID is required'})
        
        # Get the message
        message = Message.query.get(message_id)
        if not message:
            return jsonify({'success': False, 'error': 'Message not found'})
        
        # Find the contract associated with this message
        # This is a simplified approach - you might want to add a contract_id field to messages
        conversation_user_id = message.sender_id if message.sender_id != current_user.id else message.recipient_id
        
        # Find the proposal and contract
        proposal = Proposal.query.filter(
            ((Proposal.student_id == current_user.id) & (Proposal.coach_id == conversation_user_id)) |
            ((Proposal.coach_id == current_user.id) & (Proposal.student_id == conversation_user_id))
        ).filter_by(status='accepted').first()
        
        if not proposal:
            return jsonify({'success': False, 'error': 'No accepted proposal found'})
        
        contract = proposal.get_contract()
        if not contract:
            return jsonify({'success': False, 'error': 'No contract found'})
        
        # Check if user has permission to accept this contract
        if contract.student_id != current_user.id:
            return jsonify({'success': False, 'error': 'You can only accept contracts sent to you'})
        
        # Update contract status
        contract.status = 'accepted'
        contract.accepted_at = datetime.utcnow()
        
        # Create a system message to notify about contract acceptance
        acceptance_message = Message(
            sender_id=current_user.id,
            recipient_id=conversation_user_id,
            content=f"✅ Contract accepted for {contract_data.get('project', 'Learning Project')}",
            message_type='SYSTEM'
        )
        
        db.session.add(acceptance_message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'contract_id': contract.id,
            'message': 'Contract accepted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error accepting contract: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/contracts/decline', methods=['POST'])
@login_required
def api_decline_contract():
    """API endpoint to decline a contract from message"""
    try:
        data = request.get_json()
        message_id = data.get('message_id')
        
        if not message_id:
            return jsonify({'success': False, 'error': 'Message ID is required'})
        
        # Get the message
        message = Message.query.get(message_id)
        if not message:
            return jsonify({'success': False, 'error': 'Message not found'})
        
        # Find the contract associated with this message
        conversation_user_id = message.sender_id if message.sender_id != current_user.id else message.recipient_id
        
        # Find the proposal and contract
        proposal = Proposal.query.filter(
            ((Proposal.student_id == current_user.id) & (Proposal.coach_id == conversation_user_id)) |
            ((Proposal.coach_id == current_user.id) & (Proposal.student_id == conversation_user_id))
        ).filter_by(status='accepted').first()
        
        if not proposal:
            return jsonify({'success': False, 'error': 'No accepted proposal found'})
        
        contract = proposal.get_contract()
        if not contract:
            return jsonify({'success': False, 'error': 'No contract found'})
        
        # Check if user has permission to decline this contract
        if contract.student_id != current_user.id:
            return jsonify({'success': False, 'error': 'You can only decline contracts sent to you'})
        
        # Update contract status
        contract.status = 'cancelled'
        contract.declined_at = datetime.utcnow()
        
        # Create a system message to notify about contract decline
        decline_message = Message(
            sender_id=current_user.id,
            recipient_id=conversation_user_id,
            content="❌ Contract declined",
            message_type='SYSTEM'
        )
        
        db.session.add(decline_message)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Contract declined successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error declining contract: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/contracts/view/<int:message_id>')
@login_required
def api_view_contract_from_message(message_id):
    """API endpoint to get contract details from message"""
    try:
        # Get the message
        message = Message.query.get(message_id)
        if not message:
            return jsonify({'success': False, 'error': 'Message not found'})
        
        # Find the contract associated with this message
        conversation_user_id = message.sender_id if message.sender_id != current_user.id else message.recipient_id
        
        # Find the proposal and contract
        proposal = Proposal.query.filter(
            ((Proposal.student_id == current_user.id) & (Proposal.coach_id == conversation_user_id)) |
            ((Proposal.coach_id == current_user.id) & (Proposal.student_id == conversation_user_id))
        ).filter_by(status='accepted').first()
        
        if not proposal:
            return jsonify({'success': False, 'error': 'No accepted proposal found'})
        
        contract = proposal.get_contract()
        if not contract:
            return jsonify({'success': False, 'error': 'No contract found'})
        
        return jsonify({
            'success': True,
            'contract_id': contract.id,
            'contract_url': url_for('view_contract', contract_id=contract.id)
        })
        
    except Exception as e:
        app.logger.error(f"Error viewing contract from message: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# ENTERPRISE SCHEDULING SYSTEM ROUTES
# ============================================================================

@app.route('/scheduling/availability/<int:coach_id>')
@login_required
def view_coach_availability(coach_id):
    """View coach availability and book sessions"""
    from models import User, CoachProfile
    from utils import get_coach_availability, get_available_slots_for_range
    
    coach = User.query.get_or_404(coach_id)
    if not coach.is_coach:
        flash('User is not a coach', 'error')
        return redirect(url_for('index'))
    
    # Get coach availability
    availability = get_coach_availability(coach_id)
    
    # Get available slots for next 2 weeks
    from datetime import date, timedelta
    start_date = date.today()
    end_date = start_date + timedelta(days=14)
    
    # Get user's timezone
    user_timezone = get_user_timezone(get_current_user())
    
    available_slots = get_available_slots_for_range(
        coach_id, start_date, end_date, timezone=user_timezone
    )
    
    return render_template('scheduling/coach_availability.html',
                         coach=coach,
                         availability=availability,
                         available_slots=available_slots,
                         user_timezone=user_timezone)

@app.route('/api/scheduling/availability/<int:coach_id>')
@login_required
def api_coach_availability(coach_id):
    """API endpoint to get coach availability"""
    from utils import get_available_slots_for_date, get_user_timezone
    from datetime import date, timedelta
    
    # Get date range from query parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if start_date_str:
        start_date = date.fromisoformat(start_date_str)
    else:
        start_date = date.today()
    
    if end_date_str:
        end_date = date.fromisoformat(end_date_str)
    else:
        end_date = start_date + timedelta(days=7)
    
    # Get user's timezone
    user_timezone = get_user_timezone(get_current_user())
    
    # Get available slots
    available_slots = {}
    current_date = start_date
    
    while current_date <= end_date:
        slots = get_available_slots_for_date(coach_id, current_date, timezone=user_timezone)
        if slots:
            available_slots[current_date.isoformat()] = [
                {
                    'start': slot['start'].isoformat(),
                    'end': slot['end'].isoformat(),
                    'available': slot['available']
                }
                for slot in slots
            ]
        current_date += timedelta(days=1)
    
    return jsonify({
        'success': True,
        'available_slots': available_slots,
        'timezone': user_timezone
    })

@app.route('/scheduling/book/<int:coach_id>', methods=['GET', 'POST'])
@login_required
def book_session_with_coach(coach_id):
    """Book a session with a coach"""
    from models import User, CoachProfile
    from utils import (get_coach_availability, get_available_slots_for_date, 
                      book_session, book_consultation, validate_session_booking,
                      can_schedule_post_contract, get_user_timezone)
    from forms import SessionBookingForm
    
    coach = User.query.get_or_404(coach_id)
    if not coach.is_coach:
        flash('User is not a coach', 'error')
        return redirect(url_for('index'))
    
    current_user = get_current_user()
    
    # Check if user is trying to book with themselves
    if current_user.id == coach_id:
        flash('You cannot book a session with yourself', 'error')
        return redirect(url_for('index'))
    
    # Get coach availability
    availability = get_coach_availability(coach_id)
    
    # Check if coach is available
    if not availability.is_available:
        flash('This coach is currently not accepting bookings', 'error')
        return redirect(url_for('view_coach_availability', coach_id=coach_id))
    
    # Determine session type based on contract status
    can_schedule_paid, paid_message = can_schedule_post_contract(current_user.id, coach_id)
    consultation_available = availability.consultation_available
    
    if request.method == 'POST':
        form = SessionBookingForm()
        if form.validate_on_submit():
            try:
                # Validate booking
                scheduled_at = form.scheduled_at.data
                duration_minutes = form.duration_minutes.data
                session_type = form.session_type.data
                
                # Convert to user's timezone
                user_timezone = get_user_timezone(current_user)
                if scheduled_at.tzinfo is None:
                    import pytz
                    tz = pytz.timezone(user_timezone)
                    scheduled_at = tz.localize(scheduled_at)
                
                # Validate booking parameters
                errors = validate_session_booking(
                    coach_id, current_user.id, scheduled_at, duration_minutes, session_type
                )
                
                if errors:
                    for error in errors:
                        flash(error, 'error')
                    return render_template('scheduling/book_session.html',
                                         coach=coach,
                                         availability=availability,
                                         form=form,
                                         can_schedule_paid=can_schedule_paid,
                                         consultation_available=consultation_available)
                
                # Book the session
                if session_type == 'consultation':
                    scheduled_session = book_consultation(
                        coach_id, current_user.id, scheduled_at, user_timezone
                    )
                    flash('Free consultation booked successfully!', 'success')
                else:
                    # For paid sessions, we need to create a session record first
                    from models import Session
                    session = Session(
                        proposal_id=None,  # Will be set when contract is created
                        session_number=1,
                        status='scheduled'
                    )
                    db.session.add(session)
                    db.session.flush()
                    
                    scheduled_session = book_session(
                        coach_id=coach_id,
                        student_id=current_user.id,
                        session_id=session.id,
                        scheduled_at=scheduled_at,
                        duration_minutes=duration_minutes,
                        session_type='paid',
                        timezone=user_timezone
                    )
                    flash('Session booked successfully!', 'success')
                
                # Send notifications
                from utils import send_session_notifications
                send_session_notifications(scheduled_session, 'booking_confirmation')
                
                return redirect(url_for('view_scheduled_session', session_id=scheduled_session.id))
                
            except Exception as e:
                flash(f'Error booking session: {str(e)}', 'error')
                return render_template('scheduling/book_session.html',
                                     coach=coach,
                                     availability=availability,
                                     form=form,
                                     can_schedule_paid=can_schedule_paid,
                                     consultation_available=consultation_available)
    else:
        form = SessionBookingForm()
        # Set default values
        form.session_type.data = 'consultation' if consultation_available else 'paid'
        form.duration_minutes.data = availability.session_duration
    
    return render_template('scheduling/book_session.html',
                         coach=coach,
                         availability=availability,
                         form=form,
                         can_schedule_paid=can_schedule_paid,
                         consultation_available=consultation_available)

@app.route('/api/scheduling/book', methods=['POST'])
@login_required
def api_book_session():
    """API endpoint to book a session"""
    from utils import (book_session, book_consultation, validate_session_booking,
                      get_user_timezone, send_session_notifications)
    
    try:
        data = request.get_json()
        
        coach_id = data.get('coach_id')
        scheduled_at_str = data.get('scheduled_at')
        duration_minutes = data.get('duration_minutes', 60)
        session_type = data.get('session_type', 'paid')
        
        if not all([coach_id, scheduled_at_str]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        current_user = get_current_user()
        
        # Parse scheduled_at
        from datetime import datetime
        import pytz
        
        scheduled_at = datetime.fromisoformat(scheduled_at_str.replace('Z', '+00:00'))
        user_timezone = get_user_timezone(current_user)
        
        if scheduled_at.tzinfo is None:
            tz = pytz.timezone(user_timezone)
            scheduled_at = tz.localize(scheduled_at)
        
        # Validate booking
        errors = validate_session_booking(
            coach_id, current_user.id, scheduled_at, duration_minutes, session_type
        )
        
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        
        # Book the session
        if session_type == 'consultation':
            scheduled_session = book_consultation(
                coach_id, current_user.id, scheduled_at, user_timezone
            )
        else:
            from models import Session
            session = Session(
                proposal_id=None,
                session_number=1,
                status='scheduled'
            )
            db.session.add(session)
            db.session.flush()
            
            scheduled_session = book_session(
                coach_id=coach_id,
                student_id=current_user.id,
                session_id=session.id,
                scheduled_at=scheduled_at,
                duration_minutes=duration_minutes,
                session_type='paid',
                timezone=user_timezone
            )
        
        # Send notifications
        send_session_notifications(scheduled_session, 'booking_confirmation')
        
        return jsonify({
            'success': True,
            'session_id': scheduled_session.id,
            'message': 'Session booked successfully!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/scheduling/session/<int:session_id>')
@login_required
def view_scheduled_session(session_id):
    """View scheduled session details"""
    from models import ScheduledSession
    
    scheduled_session = ScheduledSession.query.get_or_404(session_id)
    current_user = get_current_user()
    
    # Check if user has access to this session
    if scheduled_session.coach_id != current_user.id and scheduled_session.student_id != current_user.id:
        flash('You do not have access to this session', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('scheduling/view_session.html',
                         scheduled_session=scheduled_session,
                         current_user=current_user)

@app.route('/scheduling/session/<int:session_id>/cancel', methods=['POST'])
@login_required
def cancel_scheduled_session(session_id):
    """Cancel a scheduled session"""
    from models import ScheduledSession
    
    scheduled_session = ScheduledSession.query.get_or_404(session_id)
    current_user = get_current_user()
    
    # Check if user has permission to cancel
    if scheduled_session.coach_id != current_user.id and scheduled_session.student_id != current_user.id:
        flash('You do not have permission to cancel this session', 'error')
        return redirect(url_for('view_scheduled_session', session_id=session_id))
    
    try:
        scheduled_session.cancel_session()
        
        # Send cancellation notifications
        from utils import send_session_notifications
        send_session_notifications(scheduled_session, 'cancellation')
        
        flash('Session cancelled successfully', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        flash(f'Error cancelling session: {str(e)}', 'error')
        return redirect(url_for('view_scheduled_session', session_id=session_id))

@app.route('/scheduling/session/<int:session_id>/reschedule', methods=['GET', 'POST'])
@login_required
def reschedule_session(session_id):
    """Request reschedule for a session"""
    from models import ScheduledSession
    from utils import get_available_slots_for_date, get_user_timezone
    from forms import RescheduleRequestForm
    
    scheduled_session = ScheduledSession.query.get_or_404(session_id)
    current_user = get_current_user()
    
    # Check if user has permission to reschedule
    if scheduled_session.coach_id != current_user.id and scheduled_session.student_id != current_user.id:
        flash('You do not have permission to reschedule this session', 'error')
        return redirect(url_for('view_scheduled_session', session_id=session_id))
    
    if request.method == 'POST':
        form = RescheduleRequestForm()
        if form.validate_on_submit():
            try:
                scheduled_session.request_reschedule(
                    requested_by=current_user.current_role,
                    reason=form.reason.data,
                    new_time=form.new_scheduled_at.data
                )
                
                flash('Reschedule request sent successfully', 'success')
                return redirect(url_for('view_scheduled_session', session_id=session_id))
                
            except Exception as e:
                flash(f'Error requesting reschedule: {str(e)}', 'error')
    else:
        form = RescheduleRequestForm()
    
    # Get available slots for rescheduling
    user_timezone = get_user_timezone(current_user)
    from datetime import date, timedelta
    
    available_slots = {}
    for i in range(7):  # Next 7 days
        target_date = date.today() + timedelta(days=i)
        slots = get_available_slots_for_date(
            scheduled_session.coach_id, target_date, 
            scheduled_session.duration_minutes, user_timezone
        )
        if slots:
            available_slots[target_date.isoformat()] = slots
    
    return render_template('scheduling/reschedule_session.html',
                         scheduled_session=scheduled_session,
                         form=form,
                         available_slots=available_slots)

@app.route('/scheduling/session/<int:session_id>/approve-reschedule', methods=['POST'])
@login_required
def approve_scheduled_session_reschedule(session_id):
    """Approve a reschedule request for scheduled sessions"""
    from models import ScheduledSession
    
    scheduled_session = ScheduledSession.query.get_or_404(session_id)
    current_user = get_current_user()
    
    # Only the other party can approve reschedule
    if scheduled_session.coach_id == current_user.id:
        if scheduled_session.reschedule_requested_by != 'student':
            if request.is_json:
                return jsonify({'success': False, 'error': 'You can only approve reschedule requests from students'})
            flash('You can only approve reschedule requests from students', 'error')
            return redirect(url_for('view_scheduled_session', session_id=session_id))
    elif scheduled_session.student_id == current_user.id:
        if scheduled_session.reschedule_requested_by != 'coach':
            if request.is_json:
                return jsonify({'success': False, 'error': 'You can only approve reschedule requests from coaches'})
            flash('You can only approve reschedule requests from coaches', 'error')
            return redirect(url_for('view_scheduled_session', session_id=session_id))
    else:
        if request.is_json:
            return jsonify({'success': False, 'error': 'You do not have permission to approve this reschedule'})
        flash('You do not have permission to approve this reschedule', 'error')
        return redirect(url_for('view_scheduled_session', session_id=session_id))
    
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            new_scheduled_at = data.get('new_scheduled_at')
        else:
            new_scheduled_at = request.form.get('new_scheduled_at')
        
        if new_scheduled_at:
            from datetime import datetime
            # Handle different datetime formats
            try:
                if 'T' in new_scheduled_at:
                    # ISO format with T
                    new_time = datetime.fromisoformat(new_scheduled_at.replace('Z', '+00:00'))
                else:
                    # Simple format YYYY-MM-DD HH:MM
                    new_time = datetime.strptime(new_scheduled_at, '%Y-%m-%d %H:%M')
            except ValueError:
                # Try alternative format
                new_time = datetime.strptime(new_scheduled_at, '%Y-%m-%dT%H:%M')
            
            scheduled_session.approve_reschedule(new_time)
        else:
            scheduled_session.approve_reschedule(scheduled_session.scheduled_at)
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Reschedule approved successfully'})
        flash('Reschedule approved successfully', 'success')
        return redirect(url_for('view_scheduled_session', session_id=session_id))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': f'Error approving reschedule: {str(e)}'})
        flash(f'Error approving reschedule: {str(e)}', 'error')
        return redirect(url_for('view_scheduled_session', session_id=session_id))

@app.route('/scheduling/session/<int:session_id>/decline-reschedule', methods=['POST'])
@login_required
def decline_scheduled_session_reschedule(session_id):
    """Decline a reschedule request for scheduled sessions"""
    from models import ScheduledSession
    
    scheduled_session = ScheduledSession.query.get_or_404(session_id)
    current_user = get_current_user()
    
    # Only the other party can decline reschedule
    if scheduled_session.coach_id == current_user.id:
        if scheduled_session.reschedule_requested_by != 'student':
            if request.is_json:
                return jsonify({'success': False, 'error': 'You can only decline reschedule requests from students'})
            flash('You can only decline reschedule requests from students', 'error')
            return redirect(url_for('view_scheduled_session', session_id=session_id))
    elif scheduled_session.student_id == current_user.id:
        if scheduled_session.reschedule_requested_by != 'coach':
            if request.is_json:
                return jsonify({'success': False, 'error': 'You can only decline reschedule requests from coaches'})
            flash('You can only decline reschedule requests from coaches', 'error')
            return redirect(url_for('view_scheduled_session', session_id=session_id))
    else:
        if request.is_json:
            return jsonify({'success': False, 'error': 'You do not have permission to decline this reschedule'})
        flash('You do not have permission to decline this reschedule', 'error')
        return redirect(url_for('view_scheduled_session', session_id=session_id))
    
    try:
        scheduled_session.decline_reschedule()
        if request.is_json:
            return jsonify({'success': True, 'message': 'Reschedule declined'})
        flash('Reschedule declined', 'info')
        return redirect(url_for('view_scheduled_session', session_id=session_id))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'error': f'Error declining reschedule: {str(e)}'})
        flash(f'Error declining reschedule: {str(e)}', 'error')
        return redirect(url_for('view_scheduled_session', session_id=session_id))

@app.route('/scheduling/coach/settings', methods=['GET', 'POST'])
@login_required
@coach_required
def coach_scheduling_settings():
    """Coach scheduling settings and availability management"""
    from models import CoachAvailability, BookingRule
    from utils import get_coach_availability, get_booking_rules
    from forms import CoachAvailabilityForm, BookingRulesForm
    
    current_user = get_current_user()
    
    # Get or create availability settings
    availability = get_coach_availability(current_user.id)
    booking_rules = get_booking_rules(current_user.id)
    
    if request.method == 'POST':
        if 'availability' in request.form:
            form = CoachAvailabilityForm()
            if form.validate_on_submit():
                # Update availability settings
                availability.is_available = form.is_available.data
                availability.timezone = form.timezone.data
                availability.session_duration = form.session_duration.data
                availability.buffer_before = form.buffer_before.data
                availability.buffer_after = form.buffer_after.data
                availability.advance_booking_days = form.advance_booking_days.data
                availability.same_day_booking = form.same_day_booking.data
                availability.instant_confirmation = form.instant_confirmation.data
                availability.consultation_available = form.consultation_available.data
                availability.consultation_duration = form.consultation_duration.data
                availability.consultation_advance_hours = form.consultation_advance_hours.data
                
                # Update working hours
                for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                    start_field = f'{day}_start'
                    end_field = f'{day}_end'
                    if hasattr(form, start_field) and hasattr(form, end_field):
                        start_time = getattr(form, start_field).data
                        end_time = getattr(form, end_field).data
                        if start_time and end_time:
                            setattr(availability, start_field, start_time.hour * 60 + start_time.minute)
                            setattr(availability, end_field, end_time.hour * 60 + end_time.minute)
                
                db.session.commit()
                flash('Availability settings updated successfully', 'success')
                return redirect(url_for('coach_scheduling_settings'))
        
        elif 'booking_rules' in request.form:
            form = BookingRulesForm()
            if form.validate_on_submit():
                # Update booking rules
                booking_rules.cancellation_hours = form.cancellation_hours.data
                booking_rules.reschedule_hours = form.reschedule_hours.data
                booking_rules.no_show_policy = form.no_show_policy.data
                booking_rules.require_payment_before = form.require_payment_before.data
                booking_rules.allow_partial_payment = form.allow_partial_payment.data
                booking_rules.send_reminder_hours = form.send_reminder_hours.data
                booking_rules.send_confirmation = form.send_confirmation.data
                booking_rules.send_cancellation = form.send_cancellation.data
                
                db.session.commit()
                flash('Booking rules updated successfully', 'success')
                return redirect(url_for('coach_scheduling_settings'))
    else:
        # Pre-populate forms with current values
        availability_form = CoachAvailabilityForm(obj=availability)
        booking_rules_form = BookingRulesForm(obj=booking_rules)
    
    return render_template('scheduling/coach_settings.html',
                         availability=availability,
                         booking_rules=booking_rules,
                         availability_form=availability_form,
                         booking_rules_form=booking_rules_form)

@app.route('/scheduling/coach/exceptions', methods=['GET', 'POST'])
@login_required
@coach_required
def coach_availability_exceptions():
    """Manage availability exceptions (blocked time, special hours)"""
    from models import AvailabilityException
    from utils import get_coach_availability
    from forms import AvailabilityExceptionForm
    
    current_user = get_current_user()
    availability = get_coach_availability(current_user.id)
    
    # Get existing exceptions
    exceptions = AvailabilityException.query.filter_by(
        availability_id=availability.id
    ).order_by(AvailabilityException.date.desc()).all()
    
    if request.method == 'POST':
        form = AvailabilityExceptionForm()
        if form.validate_on_submit():
            exception = AvailabilityException(
                availability_id=availability.id,
                date=form.date.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                is_blocked=form.is_blocked.data,
                reason=form.reason.data
            )
            db.session.add(exception)
            db.session.commit()
            flash('Exception added successfully', 'success')
            return redirect(url_for('coach_availability_exceptions'))
    else:
        form = AvailabilityExceptionForm()
    
    return render_template('scheduling/availability_exceptions.html',
                         exceptions=exceptions,
                         form=form)

@app.route('/scheduling/coach/exceptions/<int:exception_id>/delete', methods=['POST'])
@login_required
@coach_required
def delete_availability_exception(exception_id):
    """Delete an availability exception"""
    from models import AvailabilityException
    from utils import get_coach_availability
    
    current_user = get_current_user()
    availability = get_coach_availability(current_user.id)
    
    exception = AvailabilityException.query.get_or_404(exception_id)
    
    # Check if exception belongs to current coach
    if exception.availability_id != availability.id:
        flash('You do not have permission to delete this exception', 'error')
        return redirect(url_for('coach_availability_exceptions'))
    
    db.session.delete(exception)
    db.session.commit()
    flash('Exception deleted successfully', 'success')
    return redirect(url_for('coach_availability_exceptions'))

@app.route('/scheduling/dashboard')
@login_required
def scheduling_dashboard():
    """Main scheduling dashboard"""
    from utils import get_upcoming_sessions_for_user, get_user_timezone
    
    current_user = get_current_user()
    user_timezone = get_user_timezone(current_user)
    
    # Get upcoming sessions
    upcoming_sessions = get_upcoming_sessions_for_user(
        current_user.id, current_user.current_role, limit=10
    )
    
    # Get recent sessions
    from models import ScheduledSession
    recent_sessions = ScheduledSession.query.filter(
        (ScheduledSession.coach_id == current_user.id) | 
        (ScheduledSession.student_id == current_user.id),
        ScheduledSession.status.in_(['completed', 'cancelled'])
    ).order_by(ScheduledSession.scheduled_at.desc()).limit(5).all()
    
    return render_template('scheduling/dashboard.html',
                         upcoming_sessions=upcoming_sessions,
                         recent_sessions=recent_sessions,
                         user_timezone=user_timezone)





@app.route('/admin/clear-all-data', methods=['POST'])
# @admin_required  # Temporarily commented out for debugging
def clear_all_database_data():
    """Clear ALL data from the database - DANGEROUS OPERATION"""
    print("DEBUG: clear_all_database_data function called")
    
    from flask import session  # Add missing import
    
    # Additional security check - verify admin status
    if 'admin_logged_in' not in session:
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_login'))
    
    # Double-check admin status in database
    try:
        from models import User
        current_user = get_current_user()
        if not current_user or not current_user.is_admin:
            flash('Admin privileges required for this operation.', 'error')
            return redirect(url_for('admin_dashboard'))
    except Exception as e:
        print(f"DEBUG: Error checking admin status: {str(e)}")
        flash('Error verifying admin privileges.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        db = get_db()
        
        # Import all models
        from models import (
            User, StudentProfile, CoachProfile, LearningRequest, Message,
            RoleSwitchLog, SavedJob, Proposal, Session, ScreeningQuestion,
            ScreeningAnswer, ActiveRoleSession, Contract, Language, Experience,
            Education, PortfolioItem, StudentLanguage, ScheduledSession,
            SessionPayment, Notification, NotificationPreference
        )
        
        print("DEBUG: Starting complete database clear...")
        
        # Step 1: Clear session payments (they reference contracts)
        print("DEBUG: Step 1 - Clearing session payments")
        session_payments = SessionPayment.query.all()
        for payment in session_payments:
            db.session.delete(payment)
        db.session.commit()
        print(f"DEBUG: Deleted {len(session_payments)} session payments")
        
        # Step 2: Clear scheduled sessions (they reference sessions)
        print("DEBUG: Step 2 - Clearing scheduled sessions")
        scheduled_sessions = ScheduledSession.query.all()
        for session in scheduled_sessions:
            db.session.delete(session)
        db.session.commit()
        print(f"DEBUG: Deleted {len(scheduled_sessions)} scheduled sessions")
        
        # Step 3: Clear contracts (they reference proposals)
        print("DEBUG: Step 3 - Clearing contracts")
        contracts = Contract.query.all()
        for contract in contracts:
            db.session.delete(contract)
        db.session.commit()
        print(f"DEBUG: Deleted {len(contracts)} contracts")
        
        # Step 4: Clear sessions (they reference proposals)
        print("DEBUG: Step 4 - Clearing sessions")
        sessions = Session.query.all()
        for session in sessions:
            db.session.delete(session)
        db.session.commit()
        print(f"DEBUG: Deleted {len(sessions)} sessions")
        
        # Step 5: Clear screening answers (they reference proposals)
        print("DEBUG: Step 5 - Clearing screening answers")
        screening_answers = ScreeningAnswer.query.all()
        for answer in screening_answers:
            db.session.delete(answer)
        db.session.commit()
        print(f"DEBUG: Deleted {len(screening_answers)} screening answers")
        
        # Step 6: Clear proposals (they reference learning requests and users)
        print("DEBUG: Step 6 - Clearing proposals")
        proposals = Proposal.query.all()
        for proposal in proposals:
            db.session.delete(proposal)
        db.session.commit()
        print(f"DEBUG: Deleted {len(proposals)} proposals")
        
        # Step 7: Clear screening questions (they reference learning requests)
        print("DEBUG: Step 7 - Clearing screening questions")
        screening_questions = ScreeningQuestion.query.all()
        for question in screening_questions:
            db.session.delete(question)
        db.session.commit()
        print(f"DEBUG: Deleted {len(screening_questions)} screening questions")
        
        # Step 8: Clear saved jobs (they reference learning requests and users)
        print("DEBUG: Step 8 - Clearing saved jobs")
        saved_jobs = SavedJob.query.all()
        for job in saved_jobs:
            db.session.delete(job)
        db.session.commit()
        print(f"DEBUG: Deleted {len(saved_jobs)} saved jobs")
        
        # Step 9: Clear learning requests (they reference users)
        print("DEBUG: Step 9 - Clearing learning requests")
        learning_requests = LearningRequest.query.all()
        for request in learning_requests:
            db.session.delete(request)
        db.session.commit()
        print(f"DEBUG: Deleted {len(learning_requests)} learning requests")
        
        # Step 10: Clear messages (they reference users)
        print("DEBUG: Step 10 - Clearing messages")
        messages = Message.query.all()
        for message in messages:
            db.session.delete(message)
        db.session.commit()
        print(f"DEBUG: Deleted {len(messages)} messages")
        
        # Step 11: Clear role switch logs (they reference users)
        print("DEBUG: Step 11 - Clearing role switch logs")
        role_logs = RoleSwitchLog.query.all()
        for log in role_logs:
            db.session.delete(log)
        db.session.commit()
        print(f"DEBUG: Deleted {len(role_logs)} role switch logs")
        
        # Step 12: Clear active role sessions (they reference users)
        print("DEBUG: Step 12 - Clearing active role sessions")
        active_sessions = ActiveRoleSession.query.all()
        for session in active_sessions:
            db.session.delete(session)
        db.session.commit()
        print(f"DEBUG: Deleted {len(active_sessions)} active role sessions")
        
        # Step 13: Clear notifications (they reference users)
        print("DEBUG: Step 13 - Clearing notifications")
        notifications = Notification.query.all()
        for notification in notifications:
            db.session.delete(notification)
        db.session.commit()
        print(f"DEBUG: Deleted {len(notifications)} notifications")
        
        # Step 14: Clear notification preferences (they reference users)
        print("DEBUG: Step 14 - Clearing notification preferences")
        notification_prefs = NotificationPreference.query.all()
        for pref in notification_prefs:
            db.session.delete(pref)
        db.session.commit()
        print(f"DEBUG: Deleted {len(notification_prefs)} notification preferences")
        
        # Step 15: Clear portfolio items (they reference coach profiles)
        print("DEBUG: Step 15 - Clearing portfolio items")
        portfolio_items = PortfolioItem.query.all()
        for item in portfolio_items:
            db.session.delete(item)
        db.session.commit()
        print(f"DEBUG: Deleted {len(portfolio_items)} portfolio items")
        
        # Step 16: Clear student languages (they reference student profiles)
        print("DEBUG: Step 16 - Clearing student languages")
        student_languages = StudentLanguage.query.all()
        for lang in student_languages:
            db.session.delete(lang)
        db.session.commit()
        print(f"DEBUG: Deleted {len(student_languages)} student languages")
        
        # Step 17: Clear coach languages (they reference coach profiles)
        print("DEBUG: Step 17 - Clearing coach languages")
        coach_languages = Language.query.all()
        for lang in coach_languages:
            db.session.delete(lang)
        db.session.commit()
        print(f"DEBUG: Deleted {len(coach_languages)} coach languages")
        
        # Step 18: Clear education records (they reference coach profiles)
        print("DEBUG: Step 18 - Clearing education records")
        education_records = Education.query.all()
        for edu in education_records:
            db.session.delete(edu)
        db.session.commit()
        print(f"DEBUG: Deleted {len(education_records)} education records")
        
        # Step 19: Clear experience records (they reference coach profiles)
        print("DEBUG: Step 19 - Clearing experience records")
        experience_records = Experience.query.all()
        for exp in experience_records:
            db.session.delete(exp)
        db.session.commit()
        print(f"DEBUG: Deleted {len(experience_records)} experience records")
        
        # Step 20: Clear student profiles (they reference users)
        print("DEBUG: Step 20 - Clearing student profiles")
        student_profiles = StudentProfile.query.all()
        for profile in student_profiles:
            db.session.delete(profile)
        db.session.commit()
        print(f"DEBUG: Deleted {len(student_profiles)} student profiles")
        
        # Step 21: Clear coach profiles (they reference users)
        print("DEBUG: Step 21 - Clearing coach profiles")
        coach_profiles = CoachProfile.query.all()
        for profile in coach_profiles:
            db.session.delete(profile)
        db.session.commit()
        print(f"DEBUG: Deleted {len(coach_profiles)} coach profiles")
        
        # Step 22: Finally, clear all users
        print("DEBUG: Step 22 - Clearing all users")
        users = User.query.all()
        user_count = len(users)
        
        # Log admin user deletion warning
        admin_users = [user for user in users if user.is_admin]
        if admin_users:
            print(f"DEBUG: WARNING - Deleting {len(admin_users)} admin users including current user")
            for admin_user in admin_users:
                print(f"DEBUG: Deleting admin user: {admin_user.email}")
        
        for user in users:
            db.session.delete(user)
        db.session.commit()
        print(f"DEBUG: Deleted {user_count} users")
        
        # Clear admin session since admin user is now deleted
        session.clear()
        print("DEBUG: Cleared admin session")
        
        print("DEBUG: Database clear completed successfully!")
        flash(f'Successfully cleared all data from the database! Deleted {user_count} users and all related data.', 'success')
        
    except Exception as e:
        print(f"DEBUG: Error in clear_all_database_data: {str(e)}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        db.session.rollback()
        flash(f'Error occurred while clearing database: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/create-scheduled-session-table', methods=['POST'])
# @admin_required  # Temporarily commented out for debugging
def create_scheduled_session_table():
    """Create the missing scheduled_session table in production"""
    print("DEBUG: create_scheduled_session_table function called")
    
    from flask import session
    from sqlalchemy import text
    
    try:
        db = get_db()
        
        # Check if table already exists
        result = db.session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'scheduled_session'
            );
        """))
        table_exists = result.scalar()
        
        if table_exists:
            flash('Scheduled session table already exists!', 'info')
            return redirect(url_for('admin_dashboard'))
        
        # Create the scheduled_session table
        print("DEBUG: Creating scheduled_session table...")
        
        create_table_sql = """
        CREATE TABLE scheduled_session (
            id SERIAL PRIMARY KEY,
            session_id INTEGER NOT NULL REFERENCES session(id),
            coach_id INTEGER NOT NULL REFERENCES "user"(id),
            student_id INTEGER NOT NULL REFERENCES "user"(id),
            scheduled_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
            duration_minutes INTEGER NOT NULL,
            timezone VARCHAR(50) DEFAULT 'UTC',
            session_type VARCHAR(50) DEFAULT 'paid',
            is_consultation BOOLEAN DEFAULT FALSE,
            status VARCHAR(50) DEFAULT 'scheduled',
            confirmed_at TIMESTAMP WITHOUT TIME ZONE,
            started_at TIMESTAMP WITHOUT TIME ZONE,
            completed_at TIMESTAMP WITHOUT TIME ZONE,
            cancelled_at TIMESTAMP WITHOUT TIME ZONE,
            payment_status VARCHAR(50) DEFAULT 'pending',
            payment_amount NUMERIC(10, 2),
            stripe_payment_intent_id VARCHAR(255),

                                    # Video functionality has been removed from this application
                        # video_started_at TIMESTAMP WITHOUT TIME ZONE,
                        # video_ended_at TIMESTAMP WITHOUT TIME ZONE,
            reschedule_requested BOOLEAN DEFAULT FALSE,
            reschedule_requested_by VARCHAR(20),
            reschedule_reason TEXT,
            reschedule_deadline TIMESTAMP WITHOUT TIME ZONE,
            original_scheduled_at TIMESTAMP WITHOUT TIME ZONE,
            reminder_sent BOOLEAN DEFAULT FALSE,
            confirmation_sent BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        db.session.execute(text(create_table_sql))
        db.session.commit()
        
        print("DEBUG: Successfully created scheduled_session table!")
        flash('Successfully created scheduled_session table! You can now uncomment the scheduling functions.', 'success')
        
    except Exception as e:
        print(f"DEBUG: Error creating scheduled_session table: {str(e)}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        db.session.rollback()
        flash(f'Error creating scheduled_session table: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/test-single-delete', methods=['POST'])
@admin_required
def test_single_delete():
    """Test route to delete a single user directly"""
    print("DEBUG: test_single_delete function called")
    try:
        from models import User
        db = get_db()
        
        # Find a user to delete (not the current admin)
        current_user_id = session.get('user_id')
        test_user = User.query.filter(User.id != current_user_id).first()
        
        if not test_user:
            flash('No test user found to delete.', 'warning')
            return redirect(url_for('admin_dashboard'))
        
        print(f"DEBUG: Attempting to delete test user {test_user.id} ({test_user.email})")
        
        # Try to delete the user directly
        db.session.delete(test_user)
        db.session.commit()
        
        print(f"DEBUG: Successfully deleted test user {test_user.id}")
        flash(f'Successfully deleted test user {test_user.email}.', 'success')
        
    except Exception as e:
        print(f"DEBUG: Error in test_single_delete: {str(e)}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        db.session.rollback()
        flash(f'Test deletion failed: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/test-public-delete', methods=['POST'])
def test_public_delete():
    """Public test route to check if deletion functionality works without any authentication"""
    print("DEBUG: test_public_delete function called")
    print(f"DEBUG: No authentication required for this test")
    
    try:
        from models import User
        db = get_db()
        
        # Test basic database operations
        user_count = User.query.count()
        print(f"DEBUG: Found {user_count} users in database")
        
        # Test if we can access the database session
        print(f"DEBUG: Database session: {db.session}")
        
        # Test if we can query a specific user
        if user_count > 0:
            first_user = User.query.first()
            print(f"DEBUG: First user: {first_user.id} - {first_user.email}")
        
        return jsonify({
            'success': True,
            'message': f'Test successful. Found {user_count} users in database.',
            'user_count': user_count
        })
    except Exception as e:
        print(f"DEBUG: Error in test_public_delete: {str(e)}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Import scheduling utilities
from scheduling_utils import (
    get_scheduling_options, schedule_free_consultation as schedule_free_consultation_util, 
    schedule_paid_session as schedule_paid_session_util,
    check_call_availability,
    get_upcoming_calls, get_coach_upcoming_calls, send_call_notifications
)

@app.route('/schedule/free-consultation/<int:coach_id>', methods=['GET', 'POST'])
@login_required
@student_required
def schedule_free_consultation(coach_id):
    """Schedule a free 15-minute consultation with a coach"""
    user = get_current_user()
    coach = User.query.get_or_404(coach_id)
    
    # Check if coach is approved
    if not coach.coach_profile or not coach.coach_profile.is_approved:
        flash('This coach is not available for consultations.', 'error')
        return redirect(url_for('find_work'))
    
    # Check if there's already a free consultation scheduled
    existing_call = ScheduledCall.query.filter_by(
        student_id=user.id,
        coach_id=coach_id,
        call_type='free_consultation',
        status='scheduled'
    ).first()
    
    if existing_call:
        flash('You already have a free consultation scheduled with this coach.', 'warning')
        return redirect(url_for('conversation', user_id=coach_id))
    
    form = FreeConsultationForm()
    
    if form.validate_on_submit():
        try:
            # Check availability
            if not check_call_availability(
                coach_id, 
                form.scheduled_date.data, 
                form.scheduled_time.data, 
                form.timezone.data
            ):
                flash('Coach is not available at this time. Please choose another time.', 'error')
                return render_template('scheduling/schedule_free_consultation.html', form=form, coach=coach)
            
            # Schedule the call
            call = schedule_free_consultation_util(
                user.id,
                coach_id,
                form.scheduled_date.data,
                form.scheduled_time.data,
                form.timezone.data,
                form.notes.data
            )
            
            flash('Free consultation scheduled successfully! You will receive a confirmation email.', 'success')
            return redirect(url_for('conversation', user_id=coach_id))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred while scheduling the consultation. Please try again.', 'error')
            logger.error(f"Error scheduling free consultation: {e}")
    
    return render_template('scheduling/schedule_free_consultation.html', form=form, coach=coach)

@app.route('/schedule/paid-session/<int:contract_id>', methods=['GET', 'POST'])
@login_required
@student_required
def schedule_paid_session(contract_id):
    """Schedule a paid session for an active contract"""
    user = get_current_user()
    contract = Contract.query.get_or_404(contract_id)
    
    # Verify contract belongs to user and is active
    if contract.student_id != user.id:
        flash('You can only schedule sessions for your own contracts.', 'error')
        return redirect(url_for('student_dashboard'))
    
    if contract.status != 'active' or contract.payment_status != 'paid':
        flash('Contract must be active and paid to schedule sessions.', 'error')
        return redirect(url_for('view_contract', contract_id=contract_id))
    
    form = PaidSessionForm()
    
    if form.validate_on_submit():
        try:
            # Check availability
            if not check_call_availability(
                contract.coach_id, 
                form.scheduled_date.data, 
                form.scheduled_time.data, 
                form.timezone.data,
                form.duration_minutes.data
            ):
                flash('Coach is not available at this time. Please choose another time.', 'error')
                return render_template('scheduling/schedule_paid_session.html', form=form, contract=contract)
            
            # Schedule the call
            call = schedule_paid_session_util(
                user.id,
                contract.coach_id,
                contract_id,
                form.scheduled_date.data,
                form.scheduled_time.data,
                form.timezone.data,
                form.duration_minutes.data,
                form.notes.data
            )
            
            flash('Session scheduled successfully! You will receive a confirmation email.', 'success')
            return redirect(url_for('view_contract', contract_id=contract_id))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred while scheduling the session. Please try again.', 'error')
            logger.error(f"Error scheduling paid session: {e}")
    
    return render_template('scheduling/schedule_paid_session.html', form=form, contract=contract)

@app.route('/calls/<int:call_id>')
@login_required
def view_call(call_id):
    """View call details"""
    user = get_current_user()
    call = ScheduledCall.query.get_or_404(call_id)
    
    # Verify user is part of the call
    if call.student_id != user.id and call.coach_id != user.id:
        flash('You can only view your own calls.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('scheduling/view_call.html', call=call, user=user)





@app.route('/calls/<int:call_id>/end', methods=['POST'])
@login_required
def end_call(call_id):
    """End a call"""
    user = get_current_user()
    call = ScheduledCall.query.get_or_404(call_id)
    
    # Verify user is part of the call
    if call.student_id != user.id and call.coach_id != user.id:
        flash('You can only end your own calls.', 'error')
        return redirect(url_for('dashboard'))
    
    if call.status == 'active':
        try:
            call.end_call()
            flash('Call ended successfully.', 'success')
        except Exception as e:
            flash('Error ending call.', 'error')
    
    return redirect(url_for('view_call', call_id=call_id))

@app.route('/calls/<int:call_id>/cancel', methods=['POST'])
@login_required
def cancel_call(call_id):
    """Cancel a scheduled call"""
    user = get_current_user()
    call = ScheduledCall.query.get_or_404(call_id)
    
    # Verify user is part of the call
    if call.student_id != user.id and call.coach_id != user.id:
        flash('You can only cancel your own calls.', 'error')
        return redirect(url_for('dashboard'))
    
    reason = request.form.get('reason', 'Cancelled by user')
    
    try:
        call.cancel_call(reason)
        flash('Call cancelled successfully.', 'success')
    except Exception as e:
        flash('Error cancelling call.', 'error')
    
    # Redirect based on call type
    if call.is_free_consultation:
        return redirect(url_for('conversation', user_id=call.coach_id if user.id == call.student_id else call.student_id))
    else:
        return redirect(url_for('view_contract', contract_id=call.contract_id))

@app.route('/calls/<int:call_id>/reschedule', methods=['GET', 'POST'])
@login_required
def reschedule_call(call_id):
    """Reschedule a call"""
    user = get_current_user()
    call = ScheduledCall.query.get_or_404(call_id)
    
    # Verify user is part of the call
    if call.student_id != user.id and call.coach_id != user.id:
        flash('You can only reschedule your own calls.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if call can be rescheduled
    if not call.can_be_rescheduled('student'):
        flash('This call cannot be rescheduled at this time.', 'error')
        return redirect(url_for('view_call', call_id=call_id))
    
    form = RescheduleCallForm()
    
    if form.validate_on_submit():
        try:
            # Check availability
            if not check_call_availability(
                call.coach_id, 
                form.new_scheduled_date.data, 
                form.new_scheduled_time.data, 
                form.timezone.data,
                call.duration_minutes
            ):
                flash('Coach is not available at this time. Please choose another time.', 'error')
                return render_template('scheduling/reschedule_call.html', form=form, call=call)
            
            # Reschedule the call
            new_call = call.reschedule_call(
                new_scheduled_at=datetime.combine(form.new_scheduled_date.data, form.new_scheduled_time.data),
                reason=form.reason.data
            )
            
            flash('Call rescheduled successfully!', 'success')
            return redirect(url_for('view_call', call_id=new_call.id))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred while rescheduling the call. Please try again.', 'error')
            logger.error(f"Error rescheduling call: {e}")
    
    return render_template('scheduling/reschedule_call.html', form=form, call=call)

@app.route('/api/scheduling-options/<int:coach_id>')
@login_required
def api_scheduling_options(coach_id):
    """API endpoint to get scheduling options for a coach"""
    user = get_current_user()
    
    try:
        options = get_scheduling_options(user.id, coach_id)
        return jsonify({
            'success': True,
            'options': options
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/check-availability/<int:coach_id>')
@login_required
def api_check_availability(coach_id):
    """API endpoint to check coach availability"""
    try:
        date_str = request.args.get('date')
        time_str = request.args.get('time')
        timezone_name = request.args.get('timezone', 'UTC')
        duration = int(request.args.get('duration', 15))
        
        if not date_str or not time_str:
            return jsonify({'success': False, 'error': 'Date and time required'}), 400
        
        scheduled_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        scheduled_time = datetime.strptime(time_str, '%H:%M').time()
        
        available = check_call_availability(
            coach_id, scheduled_date, scheduled_time, timezone_name, duration
        )
        
        return jsonify({
            'success': True,
            'available': available
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upcoming-calls')
@login_required
def api_upcoming_calls():
    """API endpoint to get upcoming calls"""
    user = get_current_user()
    
    try:
        calls = get_upcoming_calls(user.id, limit=10)
        call_data = []
        
        for call in calls:
            call_data.append({
                'id': call.id,
                'type': call.call_type,
                'scheduled_at': call.scheduled_at.isoformat(),
                'duration_minutes': call.duration_minutes,
                'status': call.status,
                'is_ready': call.is_ready_to_join,
                'time_until': call.time_until_call
            })
        
        return jsonify({
            'success': True,
            'calls': call_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/webhook/scheduler/test', methods=['GET'])
def scheduler_test():
    """Simple test endpoint to verify the webhook is accessible"""
    return jsonify({
        'success': True,
        'message': 'Scheduler webhook is accessible',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/timezones', methods=['GET'])
def api_timezones():
    """API endpoint to get all available timezones for search"""
    from utils import get_timezone_choices
    
    try:
        timezone_choices = get_timezone_choices()
        # Convert to format expected by frontend
        timezones = [{'value': value, 'label': label} for value, label in timezone_choices]
        return jsonify(timezones)
    except Exception as e:
        app.logger.error(f"Error getting timezones: {e}")
        return jsonify([]), 500

@app.route('/api/scheduler', methods=['POST'])
def scheduler_webhook():
    """Webhook endpoint for external cron services to trigger scheduled tasks"""
    try:
        # Check if request has JSON content
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        # Get the task type from the request
        task_type = request.json.get('task', 'all')
        
        # Import the scheduler functions
        from notification_scheduler import (
            check_calls_ready,
            send_24h_reminders, 
            send_1h_reminders,
            send_session_reminders,
            mark_overdue_calls,
            cleanup_old_notifications,
            auto_complete_sessions,
            init_notification_scheduler
        )
        
        # Import Calendly-like meeting activation functions
        from meeting_activation import (
            activate_pending_meetings,
            send_pending_reminders
        )
        
        # Import advanced notification functions
        from notification_manager import send_pending_notifications
        
        # Import enhanced API functions
        from api_manager import get_api_manager, create_api_response, validate_webhook_signature, APIError
        
        # Ensure scheduler is initialized
        try:
            init_notification_scheduler(app)
        except Exception as e:
            app.logger.error(f"Error initializing scheduler in webhook: {e}")
        
        results = {}
        
        try:
            if task_type in ['all', 'calls_ready']:
                results['calls_ready'] = check_calls_ready()
                
            if task_type in ['all', 'reminders_24h']:
                results['reminders_24h'] = send_24h_reminders()
                
            if task_type in ['all', 'reminders_1h']:
                results['reminders_1h'] = send_1h_reminders()
                
            if task_type in ['all', 'session_reminders']:
                results['session_reminders'] = send_session_reminders()
                
            if task_type in ['all', 'mark_overdue']:
                results['mark_overdue'] = mark_overdue_calls()
                
            if task_type in ['all', 'cleanup']:
                results['cleanup'] = cleanup_old_notifications()
                
            if task_type in ['all', 'auto_complete_sessions']:
                results['auto_complete_sessions'] = auto_complete_sessions()
            
            # Calendly-like meeting activation tasks
            if task_type in ['all', 'meeting_activation']:
                results['meeting_activation'] = activate_pending_meetings()
                
            if task_type in ['all', 'meeting_reminders']:
                results['meeting_reminders'] = send_pending_reminders()
            
            # Advanced notification tasks
            if task_type in ['all', 'advanced_notifications']:
                results['advanced_notifications'] = send_pending_notifications()
                
        except Exception as scheduler_error:
            app.logger.error(f"Scheduler function error: {scheduler_error}")
            return jsonify({
                'success': False,
                'error': f'Scheduler error: {str(scheduler_error)}',
                'timestamp': datetime.utcnow().isoformat()
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Scheduler tasks completed',
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error in scheduler webhook: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Enhanced API Endpoints for Phase 5B

@app.route('/api/v1/sessions/<int:session_id>', methods=['GET'])
@login_required
def get_session_api(session_id):
    """Enhanced API endpoint to get session details"""
    try:
        api_manager = get_api_manager()
        
        # Apply rate limiting and error handling
        @api_manager.rate_limit
        @api_manager.handle_errors
        def get_session():
            session_data = api_manager.get_session_data(session_id)
            return create_api_response(data=session_data, message="Session retrieved successfully")
        
        return get_session()
        
    except Exception as e:
        logger.error(f"Error in get_session_api: {e}")
        return create_api_response(message="Error retrieving session", status_code=500)

@app.route('/api/v1/sessions/<int:session_id>/status', methods=['PUT'])
@login_required
def update_session_status_api(session_id):
    """Enhanced API endpoint to update session status"""
    try:
        api_manager = get_api_manager()
        
        @api_manager.rate_limit
        @api_manager.handle_errors
        @api_manager.validate_json(['status'])
        def update_status():
            data = request.get_json()
            status = data['status']
            reason = data.get('reason')
            
            if status not in ['scheduled', 'active', 'completed', 'cancelled']:
                raise APIError("Invalid status value", 400, "invalid_status")
            
            session_data = api_manager.update_session_status(session_id, status, reason)
            return create_api_response(data=session_data, message="Session status updated successfully")
        
        return update_status()
        
    except Exception as e:
        logger.error(f"Error in update_session_status_api: {e}")
        return create_api_response(message="Error updating session status", status_code=500)

@app.route('/api/v1/users/<int:user_id>/sessions', methods=['GET'])
@login_required
def get_user_sessions_api(user_id):
    """Enhanced API endpoint to get user sessions"""
    try:
        api_manager = get_api_manager()
        
        @api_manager.rate_limit
        @api_manager.handle_errors
        def get_sessions():
            status = request.args.get('status')
            limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 sessions
            
            sessions = api_manager.get_user_sessions(user_id, status, limit)
            return create_api_response(data=sessions, message="User sessions retrieved successfully")
        
        return get_sessions()
        
    except Exception as e:
        logger.error(f"Error in get_user_sessions_api: {e}")
        return create_api_response(message="Error retrieving user sessions", status_code=500)

@app.route('/api/v1/webhooks/register', methods=['POST'])
@login_required
def register_webhook_api():
    """Register a webhook for notifications"""
    try:
        api_manager = get_api_manager()
        
        @api_manager.rate_limit
        @api_manager.handle_errors
        @api_manager.validate_json(['event_type', 'webhook_url'])
        def register_webhook():
            data = request.get_json()
            event_type = data['event_type']
            webhook_url = data['webhook_url']
            
            # Validate event type
            valid_events = ['session_status_changed', 'session_created', 'session_cancelled', 'reminder_sent']
            if event_type not in valid_events:
                raise APIError(f"Invalid event type. Must be one of: {', '.join(valid_events)}", 400, "invalid_event_type")
            
            success = api_manager.webhook_manager.register_webhook(event_type, webhook_url)
            
            if success:
                return create_api_response(message="Webhook registered successfully")
            else:
                raise APIError("Failed to register webhook", 500, "webhook_registration_failed")
        
        return register_webhook()
        
    except Exception as e:
        logger.error(f"Error in register_webhook_api: {e}")
        return create_api_response(message="Error registering webhook", status_code=500)

@app.route('/api/v1/webhooks/unregister', methods=['POST'])
@login_required
def unregister_webhook_api():
    """Unregister a webhook"""
    try:
        api_manager = get_api_manager()
        
        @api_manager.rate_limit
        @api_manager.handle_errors
        @api_manager.validate_json(['event_type', 'webhook_url'])
        def unregister_webhook():
            data = request.get_json()
            event_type = data['event_type']
            webhook_url = data['webhook_url']
            
            success = api_manager.webhook_manager.unregister_webhook(event_type, webhook_url)
            
            if success:
                return create_api_response(message="Webhook unregistered successfully")
            else:
                raise APIError("Webhook not found or already unregistered", 404, "webhook_not_found")
        
        return unregister_webhook()
        
    except Exception as e:
        logger.error(f"Error in unregister_webhook_api: {e}")
        return create_api_response(message="Error unregistering webhook", status_code=500)

@app.route('/api/v1/webhooks/test', methods=['POST'])
@login_required
def test_webhook_api():
    """Test webhook delivery"""
    try:
        api_manager = get_api_manager()
        
        @api_manager.rate_limit
        @api_manager.handle_errors
        @api_manager.validate_json(['event_type', 'webhook_url'])
        def test_webhook():
            data = request.get_json()
            event_type = data['event_type']
            webhook_url = data['webhook_url']
            
            # Send test webhook
            test_data = {
                'test': True,
                'message': 'This is a test webhook',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            results = api_manager.webhook_manager.send_webhook(event_type, test_data)
            
            if results and any(results):
                return create_api_response(message="Test webhook sent successfully")
            else:
                raise APIError("Failed to send test webhook", 500, "webhook_test_failed")
        
        return test_webhook()
        
    except Exception as e:
        logger.error(f"Error in test_webhook_api: {e}")
        return create_api_response(message="Error testing webhook", status_code=500)

@app.route('/api/v1/health', methods=['GET'])
def api_health_check():
    """API health check endpoint"""
    try:
        api_manager = get_api_manager()
        
        @api_manager.rate_limit
        def health_check():
            health_data = {
                'status': 'healthy',
                'api_version': api_manager.api_version,
                'timestamp': datetime.utcnow().isoformat(),
                'services': {
                    'database': 'connected',
                    'rate_limiter': 'active',
                    'webhook_manager': 'active'
                }
            }
            return create_api_response(data=health_data, message="API is healthy")
        
        return health_check()
        
    except Exception as e:
        logger.error(f"Error in api_health_check: {e}")
        return create_api_response(message="API health check failed", status_code=500)


        
    except Exception as e:
        app.logger.error(f"Error in scheduler webhook: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/admin/fix-contracts', methods=['GET', 'POST'])
@login_required
def admin_fix_contracts():
    """Admin route to fix contract status issues"""
    user = get_current_user()
    
    # Check if user is admin (you may need to add an admin field to User model)
    if not user or not hasattr(user, 'is_admin') or not user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            # Find and fix contracts that are paid but not active
            problematic_contracts = Contract.query.filter_by(
                payment_status='paid',
                status='accepted'
            ).all()
            
            fixed_count = 0
            for contract in problematic_contracts:
                if contract.fix_status_if_needed():
                    fixed_count += 1
            
            flash(f'Fixed {fixed_count} contracts that were paid but not active.', 'success')
            
        except Exception as e:
            flash(f'Error fixing contracts: {e}', 'error')
    
    # Get contract status summary
    all_contracts = Contract.query.all()
    status_counts = {}
    payment_status_counts = {}
    problematic_contracts = []
    
    for contract in all_contracts:
        status_counts[contract.status] = status_counts.get(contract.status, 0) + 1
        payment_status_counts[contract.payment_status] = payment_status_counts.get(contract.payment_status, 0) + 1
        
        # Find problematic contracts
        if contract.payment_status == 'paid' and contract.status != 'active':
            problematic_contracts.append(contract.get_status_info())
    
    return render_template('admin/fix_contracts.html',
                         status_counts=status_counts,
                         payment_status_counts=payment_status_counts,
                         problematic_contracts=problematic_contracts)









@app.route('/test-cdn')
def test_cdn():
    """Test CDN accessibility"""
    return render_template('test_cdn.html')

@app.route('/network-test')
def network_test():
    """Test network connectivity"""
    return render_template('network_test.html')

def register_routes(app_instance):
    """Register all routes with the Flask app instance"""
    global app
    app = app_instance
    
    print("🔄 Manually registering critical routes...")
    
    # Manually register the critical routes that were failing
    app.add_url_rule('/', 'index', index, methods=['GET'])
    app.add_url_rule('/about', 'about', about, methods=['GET'])
    app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
    app.add_url_rule('/signup', 'signup', signup, methods=['GET', 'POST'])
    app.add_url_rule('/signup/student', 'signup_student', signup_student, methods=['GET', 'POST'])
    app.add_url_rule('/signup/coach', 'signup_coach', signup_coach, methods=['GET', 'POST'])
    app.add_url_rule('/dashboard', 'dashboard', dashboard, methods=['GET'])
    
    # Register the critical meeting setup routes
    app.add_url_rule('/session/<int:session_id>/meeting-setup', 'meeting_setup', meeting_setup, methods=['GET'])
    app.add_url_rule('/session/<int:session_id>/create-google-meet', 'create_google_meet', create_google_meet, methods=['GET'])
    app.add_url_rule('/session/<int:scheduled_session_id>/save-meeting-link', 'save_meeting_link', save_meeting_link, methods=['POST'])
    app.add_url_rule('/session/<int:session_id>/join-meeting', 'join_meeting', join_meeting, methods=['GET'])
    app.add_url_rule('/session/<int:session_id>/meeting-dashboard', 'meeting_dashboard', meeting_dashboard, methods=['GET'])
    
    # Register the call meeting setup routes
    app.add_url_rule('/calls/<int:call_id>/meeting-setup', 'call_meeting_setup', call_meeting_setup, methods=['GET'])
    app.add_url_rule('/calls/<int:call_id>/create-google-meet', 'create_call_google_meet', create_call_google_meet, methods=['GET'])
    app.add_url_rule('/calls/<int:call_id>/save-meeting-link', 'save_call_meeting_link', save_call_meeting_link, methods=['POST'])
    
    # Add a test route to verify routing is working
    app.add_url_rule('/test-route', 'test_route', lambda: "Test route working!", methods=['GET'])
    
    print("✅ All critical routes registered successfully!")

