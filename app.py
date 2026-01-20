import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, continue without it
    pass



# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Import db from models to avoid circular imports
from models import db
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure CSRF protection
csrf.init_app(app)

# Configure the database
database_url = os.environ.get("DATABASE_URL", "sqlite:///skileez.db")

# Handle different database URL formats
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
elif database_url.startswith("prisma+"):
    # If it's a Prisma URL, fall back to SQLite for now
    print(f"⚠️ Prisma database URL detected: {database_url}")
    print("🔄 Falling back to SQLite database")
    database_url = "sqlite:///skileez.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_timeout": 20,
    "pool_reset_on_return": "commit",
    "connect_args": {
        "sslmode": "require",
        "connect_timeout": 10,
        "application_name": "skileez_app"
    }
}

# EMERGENCY: Run database migration on app start
def run_emergency_migration():
    """Run emergency migration to add Google Meet columns"""
    try:
        import psycopg2
        print("🚨 EMERGENCY MIGRATION: Adding Google Meet columns...")
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Add columns to scheduled_session
        try:
            cursor.execute("ALTER TABLE scheduled_session ADD COLUMN google_meet_url TEXT")
            print("✅ Added google_meet_url to scheduled_session")
        except:
            print("⚠️ google_meet_url already exists in scheduled_session")
            
        try:
            cursor.execute("ALTER TABLE scheduled_session ADD COLUMN meeting_status VARCHAR(50) DEFAULT 'pending'")
            print("✅ Added meeting_status to scheduled_session")
        except:
            print("⚠️ meeting_status already exists in scheduled_session")
            
        try:
            cursor.execute("ALTER TABLE scheduled_session ADD COLUMN meeting_created_at TIMESTAMP")
            print("✅ Added meeting_created_at to scheduled_session")
        except:
            print("⚠️ meeting_created_at already exists in scheduled_session")
            
        try:
            cursor.execute("ALTER TABLE scheduled_session ADD COLUMN meeting_created_by INTEGER")
            print("✅ Added meeting_created_by to scheduled_session")
        except:
            print("⚠️ meeting_created_by already exists in scheduled_session")
            
        try:
            cursor.execute("ALTER TABLE scheduled_session ADD COLUMN meeting_notes TEXT")
            print("✅ Added meeting_notes to scheduled_session")
        except:
            print("⚠️ meeting_notes already exists in scheduled_session")
        
        # Add columns to scheduled_call
        try:
            cursor.execute("ALTER TABLE scheduled_call ADD COLUMN google_meet_url TEXT")
            print("✅ Added google_meet_url to scheduled_call")
        except:
            print("⚠️ google_meet_url already exists in scheduled_call")
            
        try:
            cursor.execute("ALTER TABLE scheduled_call ADD COLUMN meeting_status VARCHAR(50) DEFAULT 'pending'")
            print("✅ Added meeting_status to scheduled_call")
        except:
            print("⚠️ meeting_status already exists in scheduled_call")
            
        try:
            cursor.execute("ALTER TABLE scheduled_call ADD COLUMN meeting_created_at TIMESTAMP")
            print("✅ Added meeting_created_at to scheduled_call")
        except:
            print("⚠️ meeting_created_at already exists in scheduled_call")
            
        try:
            cursor.execute("ALTER TABLE scheduled_call ADD COLUMN meeting_created_by INTEGER")
            print("✅ Added meeting_created_by to scheduled_call")
        except:
            print("⚠️ meeting_created_by already exists in scheduled_call")
            
        try:
            cursor.execute("ALTER TABLE scheduled_call ADD COLUMN meeting_notes TEXT")
            print("✅ Added meeting_notes to scheduled_call")
        except:
            print("⚠️ meeting_notes already exists in scheduled_call")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("🎯 EMERGENCY MIGRATION COMPLETED!")
        
    except Exception as e:
        print(f"❌ Emergency migration failed: {e}")
        print("⚠️ App will start but Google Meet may not work")

# Run migration immediately (commented out for SQLite)
# run_emergency_migration()

# Configure Flask-Mail for Gmail
# Email configuration optimized for reliability and production deployment
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))  # Use TLS port 587
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'skileezverf@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'wghd tnjr kbda mjie')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'skileezverf@gmail.com')
app.config['MAIL_MAX_EMAILS'] = 10
app.config['MAIL_ASCII_ATTACHMENTS'] = False

# Timeout settings - optimized for background sending
app.config['MAIL_TIMEOUT'] = 45  # Timeout for background email threads
app.config['MAIL_SUPPRESS_SEND'] = False  # Ensure emails are actually sent
app.config['MAIL_DEBUG'] = True  # Enable email debugging

# Log email configuration for debugging
app.logger.info(f"📧 Email Configuration:")
app.logger.info(f"   Server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
app.logger.info(f"   TLS: {app.config['MAIL_USE_TLS']}, SSL: {app.config['MAIL_USE_SSL']}")
app.logger.info(f"   Username: {app.config['MAIL_USERNAME']}")
app.logger.info(f"   Sender: {app.config['MAIL_DEFAULT_SENDER']}")
app.logger.info(f"   Password configured: {'Yes' if app.config.get('MAIL_PASSWORD') else 'No'}")
app.logger.info(f"   Password length: {len(app.config.get('MAIL_PASSWORD', '')) if app.config.get('MAIL_PASSWORD') else 0} chars")

# Validate email configuration
if not app.config.get('MAIL_PASSWORD'):
    app.logger.error("🔴 MAIL_PASSWORD not set! Email sending will FAIL!")
    app.logger.error("🔴 Get Gmail App Password from: https://myaccount.google.com/apppasswords")
elif len(app.config.get('MAIL_PASSWORD', '')) < 16:
    app.logger.warning("⚠️ MAIL_PASSWORD seems too short! Should be 16 characters.")
    app.logger.warning("⚠️ Make sure you're using Gmail App Password, not regular password!")
else:
    app.logger.info("✅ Email password configured correctly")

# Set base URL for email verification links (works with Render and Replit)
base_url = os.environ.get('BASE_URL')
if not base_url:
    # Check for Render environment
    render_external_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_external_url:
        base_url = render_external_url
    else:
        # Use Replit environment variables
        replit_url = os.environ.get('REPLIT_URL')
        if replit_url:
            base_url = replit_url
        else:
            # Use REPLIT_DOMAINS (the current development URL)
            dev_domain = os.environ.get('REPLIT_DOMAINS', '')
            if dev_domain:
                base_url = f"https://{dev_domain}"
            else:
                # Fallback to constructing from owner and slug
                repl_slug = os.environ.get('REPL_SLUG', '')
                repl_owner = os.environ.get('REPL_OWNER', '')
                if repl_slug and repl_owner:
                    base_url = f"https://{repl_slug}.{repl_owner}.repl.co"
                else:
                    base_url = 'http://localhost:5000'

app.config['BASE_URL'] = base_url

# Email verification configuration
# ENABLE email verification for new accounts
app.config['ENABLE_EMAIL_VERIFICATION'] = os.environ.get('ENABLE_EMAIL_VERIFICATION', 'true').lower() == 'true'

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Stripe configuration
app.config['STRIPE_SECRET_KEY'] = os.environ.get('STRIPE_SECRET_KEY')
app.config['STRIPE_PUBLISHABLE_KEY'] = os.environ.get('STRIPE_PUBLISHABLE_KEY')
app.config['STRIPE_WEBHOOK_SECRET'] = os.environ.get('STRIPE_WEBHOOK_SECRET')

# Test mode configuration for payment system
app.config['TEST_MODE'] = os.environ.get('TEST_MODE', 'false').lower() == 'true'
app.config['TEST_MODE_ENABLED'] = app.config['TEST_MODE']  # Alias for easier access

# Initialize Stripe
if app.config['STRIPE_SECRET_KEY']:
    import stripe
    stripe.api_key = app.config['STRIPE_SECRET_KEY']
    app.logger.info("Stripe initialized successfully")
else:
    app.logger.warning("Stripe secret key not configured - payment features will be disabled")

# Initialize the app with the extensions
db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)

# Initialize notification scheduler for production deployment
try:
    from notification_scheduler import init_notification_scheduler
    init_notification_scheduler(app)
    app.logger.info("Notification scheduler initialized successfully")
except Exception as e:
    app.logger.error(f"Error initializing notification scheduler: {e}")

with app.app_context():
    # Import models to ensure they are registered with SQLAlchemy
    import models
    
    # Apply database schema fixes for production
    def apply_database_fixes():
        """Apply database schema fixes for production deployment"""
        try:
            from sqlalchemy import text
            
            # Check database type
            db_url = str(db.engine.url)
            is_postgresql = 'postgresql' in db_url.lower()
            
            if not is_postgresql:
                app.logger.info("Skipping database fixes - not PostgreSQL production database")
                return
            
            app.logger.info("Applying production database schema fixes...")
            
            # Check if required tables exist
            try:
                # Check if contract table exists
                contract_exists = db.session.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'contract'
                    );
                """)).scalar()
                
                if not contract_exists:
                    app.logger.info("Contract table does not exist yet, skipping column modifications")
                    return
                
                # Check current contract table columns
                result = db.session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'contract' 
                    AND table_schema = 'public'
                    ORDER BY ordinal_position;
                """))
                existing_columns = [row[0] for row in result.fetchall()]
                app.logger.info(f"Current contract table columns: {existing_columns}")
            except Exception as e:
                app.logger.error(f"Error checking contract table schema: {e}")
                return
            
            # Check if message table exists before adding columns
            message_exists = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'message'
                );
            """)).scalar()
            
            if message_exists:
                # Add message_type column to message table if it doesn't exist
                try:
                    db.session.execute(text("ALTER TABLE message ADD COLUMN message_type VARCHAR(20) DEFAULT 'TEXT';"))
                    db.session.commit()
                    app.logger.info("Added message_type column to message table")
                except Exception as e:
                    db.session.rollback()
                    if "already exists" in str(e) or "duplicate column name" in str(e):
                        app.logger.info("message_type column already exists")
                    else:
                        app.logger.error(f"Error adding message_type column: {e}")
            else:
                app.logger.info("Message table does not exist yet, skipping column modifications")
            
            # Add contract acceptance columns if they don't exist
            if 'accepted_at' not in existing_columns:
                try:
                    db.session.execute(text("ALTER TABLE contract ADD COLUMN accepted_at TIMESTAMP;"))
                    db.session.commit()
                    app.logger.info("Added accepted_at column to contract table")
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f"Error adding accepted_at column: {e}")
            else:
                app.logger.info("accepted_at column already exists")
            
            if 'declined_at' not in existing_columns:
                try:
                    db.session.execute(text("ALTER TABLE contract ADD COLUMN declined_at TIMESTAMP;"))
                    db.session.commit()
                    app.logger.info("Added declined_at column to contract table")
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f"Error adding declined_at column: {e}")
            else:
                app.logger.info("declined_at column already exists")
            
            if 'payment_completed_at' not in existing_columns:
                try:
                    db.session.execute(text("ALTER TABLE contract ADD COLUMN payment_completed_at TIMESTAMP;"))
                    db.session.commit()
                    app.logger.info("Added payment_completed_at column to contract table")
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f"Error adding payment_completed_at column: {e}")
            else:
                app.logger.info("payment_completed_at column already exists")
            
            # Note: Removed contract status reset to prevent active contracts from being reset to pending
            app.logger.info("Skipping contract status reset to preserve active contracts")
            
            app.logger.info("Production database schema fixes applied successfully")
            
        except Exception as e:
            app.logger.error(f"Error applying database fixes: {e}")
            db.session.rollback()
    
    # Create all database tables if they don't exist
    try:
        app.logger.info("Creating database tables...")
        
        # Use SQLAlchemy's create_all() which handles dependencies correctly
        db.create_all()
        app.logger.info("✓ Database tables created successfully")
        
    except Exception as e:
        app.logger.error(f"Error creating database tables: {e}")
    
    # Auto-migrate reschedule_proposed_time column
    try:
        from auto_migrate_reschedule_column import auto_migrate_reschedule_column
        auto_migrate_reschedule_column()
    except Exception as e:
        app.logger.error(f"Error during auto-migration: {e}")
    
    # Apply the fixes
    apply_database_fixes()
    
    # Database migration and fixes are handled by Flask-Migrate
    # These modules are not essential for core functionality
    app.logger.info("Database migration handled by Flask-Migrate")



# Template helper function for profile pictures
@app.template_filter('profile_pic_url')
def profile_pic_url(profile_picture):
    """Convert profile picture path to proper URL"""
    if not profile_picture:
        return None
    
    # If it's already a full URL (starts with http), return as-is
    if profile_picture.startswith('http'):
        return profile_picture
    
    # If it's a relative path (uploaded file), convert to static URL
    from flask import url_for
    return url_for('static', filename=profile_picture)

# Template helper function to extract contract information from message content
@app.template_filter('extract_contract_info')
def extract_contract_info(content):
    """Extract contract information from message content with enhanced parsing"""
    import re
    import json
    from datetime import datetime
    
    if not content:
        return None
    
    contract_info = {}
    
    try:
        # First, try to parse as JSON (for structured contract messages)
        if content.strip().startswith('{') and content.strip().endswith('}'):
            try:
                json_data = json.loads(content)
                if isinstance(json_data, dict):
                    contract_info.update({
                        'project': json_data.get('project', 'Learning Project'),
                        'sessions': str(json_data.get('sessions', 'N/A')),
                        'amount': json_data.get('amount', 'N/A'),  # Keep as number for JSON data
                        'start_date': json_data.get('start_date', 'N/A'),
                        'contract_id': json_data.get('contract_id'),
                        'status': json_data.get('status', 'pending'),
                        'duration': json_data.get('duration', 'N/A'),
                        'rate': json_data.get('rate', 'N/A')
                    })
                    return contract_info
            except json.JSONDecodeError:
                pass  # Continue with regex parsing
        
        # Enhanced regex patterns for different contract message formats
        patterns = [
            # Format 1: **Project:** Title
            (r'\*\*Project:\*\* (.+?)(?:\n|$)', 'project'),
            # Format 2: Project: Title
            (r'Project:\s*(.+?)(?:\n|$)', 'project'),
            # Format 3: 📋 **New Contract Created** format
            (r'📋 \*\*New Contract Created\*\*\n\n\*\*Project:\*\* (.+?)(?:\n|$)', 'project'),
            
            # Sessions patterns
            (r'\*\*Sessions:\*\* (\d+)', 'sessions'),
            (r'Sessions:\s*(\d+)', 'sessions'),
            (r'(\d+)\s*sessions?', 'sessions'),
            
            # Amount patterns
            (r'\*\*Total Amount:\*\* \$([\d,]+\.?\d*)', 'amount'),
            (r'Total Amount:\s*\$([\d,]+\.?\d*)', 'amount'),
            (r'\$([\d,]+\.?\d*)', 'amount'),
            
            # Start date patterns
            (r'\*\*Start Date:\*\* (.+?)(?:\n|$)', 'start_date'),
            (r'Start Date:\s*(.+?)(?:\n|$)', 'start_date'),
            (r'(\w+ \d{1,2}, \d{4})', 'start_date'),
            
            # Contract ID patterns
            (r'Contract ID:\s*(\d+)', 'contract_id'),
            (r'ID:\s*(\d+)', 'contract_id'),
            
            # Status patterns
            (r'Status:\s*(pending|active|completed|cancelled)', 'status'),
            (r'\*\*Status:\*\* (pending|active|completed|cancelled)', 'status'),
            
            # Duration patterns
            (r'Duration:\s*(\d+)\s*minutes?', 'duration'),
            (r'\*\*Duration:\*\* (\d+)\s*minutes?', 'duration'),
            
            # Rate patterns
            (r'Rate:\s*\$([\d,]+\.?\d*)/session', 'rate'),
            (r'\*\*Rate:\*\* \$([\d,]+\.?\d*)/session', 'rate')
        ]
        
        # Apply all patterns
        for pattern, key in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                if key == 'amount' and not value.startswith('$'):
                    value = f"${value}"
                elif key == 'sessions':
                    value = str(value)
                contract_info[key] = value
        
        # Clean up and validate extracted data
        if contract_info:
            # Ensure amount has proper formatting (only for regex-extracted amounts)
            if 'amount' in contract_info and contract_info['amount'] != 'N/A':
                amount = contract_info['amount']
                # Only add $ prefix if it's a string and doesn't already have it
                if isinstance(amount, str) and not amount.startswith('$'):
                    contract_info['amount'] = f"${amount}"
            
            # Ensure sessions is a string
            if 'sessions' in contract_info:
                contract_info['sessions'] = str(contract_info['sessions'])
            
            # Set defaults for missing fields
            contract_info.setdefault('project', 'Learning Project')
            contract_info.setdefault('sessions', 'N/A')
            contract_info.setdefault('amount', 'N/A')
            contract_info.setdefault('start_date', 'N/A')
            contract_info.setdefault('status', 'pending')
            contract_info.setdefault('duration', 'N/A')
            contract_info.setdefault('rate', 'N/A')
            
            return contract_info
        
        return None
        
    except Exception as e:
        app.logger.error(f"Error extracting contract info: {e}")
        return None

# Template helper function to extract session information from message content
@app.template_filter('extract_session_info')
def extract_session_info(content):
    """Extract session information from message content"""
    import re
    import json
    from datetime import datetime
    
    if not content:
        return None
    
    session_info = {}
    
    try:
        # First, try to parse as JSON (for structured session messages)
        if content.strip().startswith('{') and content.strip().endswith('}'):
            try:
                json_data = json.loads(content)
                if isinstance(json_data, dict):
                    session_info.update({
                        'session_id': json_data.get('session_id'),
                        'session_number': json_data.get('session_number'),
                        'scheduled_at': json_data.get('scheduled_at'),
                        'duration': json_data.get('duration', '60'),
                        'status': json_data.get('status', 'scheduled'),
                        'session_type': json_data.get('session_type', 'paid'),
                        'contract_title': json_data.get('contract_title'),
                        'coach_name': json_data.get('coach_name'),
                        'student_name': json_data.get('student_name')
                    })
                    return session_info
            except json.JSONDecodeError:
                pass  # Continue with regex parsing
        
        # Enhanced regex patterns for different session message formats
        patterns = [
            # Session ID patterns
            (r'Session ID:\s*(\d+)', 'session_id'),
            (r'ID:\s*(\d+)', 'session_id'),
            
            # Session number patterns
            (r'Session #(\d+)', 'session_number'),
            (r'Session Number:\s*(\d+)', 'session_number'),
            
            # Date and time patterns
            (r'Scheduled:\s*(.+?)(?:\n|$)', 'scheduled_at'),
            (r'Date:\s*(.+?)(?:\n|$)', 'scheduled_at'),
            (r'Time:\s*(.+?)(?:\n|$)', 'scheduled_at'),
            (r'(\w+ \d{1,2}, \d{4} at \d{1,2}:\d{2} [AP]M)', 'scheduled_at'),
            
            # Duration patterns
            (r'Duration:\s*(\d+)\s*minutes?', 'duration'),
            (r'(\d+)\s*min', 'duration'),
            
            # Status patterns
            (r'Status:\s*(scheduled|confirmed|completed|cancelled|missed)', 'status'),
            (r'\*\*Status:\*\* (scheduled|confirmed|completed|cancelled|missed)', 'status'),
            
            # Session type patterns
            (r'Type:\s*(free consultation|paid session|learning session)', 'session_type'),
            (r'\*\*Type:\*\* (free consultation|paid session|learning session)', 'session_type'),
            
            # Contract title patterns
            (r'Contract:\s*(.+?)(?:\n|$)', 'contract_title'),
            (r'\*\*Contract:\*\* (.+?)(?:\n|$)', 'contract_title'),
            
            # Coach name patterns
            (r'Coach:\s*(.+?)(?:\n|$)', 'coach_name'),
            (r'\*\*Coach:\*\* (.+?)(?:\n|$)', 'coach_name'),
            
            # Student name patterns
            (r'Student:\s*(.+?)(?:\n|$)', 'student_name'),
            (r'\*\*Student:\*\* (.+?)(?:\n|$)', 'student_name')
        ]
        
        # Apply all patterns
        for pattern, key in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                session_info[key] = value
        
        # Clean up and validate extracted data
        if session_info:
            # Set defaults for missing fields
            session_info.setdefault('session_id', None)
            session_info.setdefault('session_number', 'N/A')
            session_info.setdefault('scheduled_at', 'N/A')
            session_info.setdefault('duration', '60')
            session_info.setdefault('status', 'scheduled')
            session_info.setdefault('session_type', 'paid')
            session_info.setdefault('contract_title', 'N/A')
            session_info.setdefault('coach_name', 'N/A')
            session_info.setdefault('student_name', 'N/A')
            
            return session_info
        
        return None
        
    except Exception as e:
        app.logger.error(f"Error extracting session info: {e}")
        return None

# Template helper function to extract consultation information from message content
@app.template_filter('extract_consultation_info')
def extract_consultation_info(content):
    """Extract consultation information from message content"""
    import re
    import json
    from datetime import datetime
    
    if not content:
        return None
    
    consultation_info = {}
    
    try:
        # First, try to parse as JSON (for structured consultation messages)
        if content.strip().startswith('{') and content.strip().endswith('}'):
            try:
                json_data = json.loads(content)
                if isinstance(json_data, dict):
                    consultation_info.update({
                        'consultation_id': json_data.get('consultation_id'),
                        'scheduled_at': json_data.get('scheduled_at'),
                        'status': json_data.get('status', 'scheduled'),
                        'coach_name': json_data.get('coach_name'),
                        'student_name': json_data.get('student_name'),
                        'duration': json_data.get('duration', '15')
                    })
                    return consultation_info
            except json.JSONDecodeError:
                pass  # Continue with regex parsing
        
        # Enhanced regex patterns for different consultation message formats
        patterns = [
            # Consultation ID patterns
            (r'Consultation ID:\s*(\d+)', 'consultation_id'),
            (r'ID:\s*(\d+)', 'consultation_id'),
            
            # Date and time patterns
            (r'Scheduled:\s*(.+?)(?:\n|$)', 'scheduled_at'),
            (r'Date:\s*(.+?)(?:\n|$)', 'scheduled_at'),
            (r'Time:\s*(.+?)(?:\n|$)', 'scheduled_at'),
            (r'(\w+ \d{1,2}, \d{4} at \d{1,2}:\d{2} [AP]M)', 'scheduled_at'),
            
            # Status patterns
            (r'Status:\s*(scheduled|confirmed|completed|cancelled|missed)', 'status'),
            (r'\*\*Status:\*\* (scheduled|confirmed|completed|cancelled|missed)', 'status'),
            
            # Coach name patterns
            (r'Coach:\s*(.+?)(?:\n|$)', 'coach_name'),
            (r'\*\*Coach:\*\* (.+?)(?:\n|$)', 'coach_name'),
            
            # Student name patterns
            (r'Student:\s*(.+?)(?:\n|$)', 'student_name'),
            (r'\*\*Student:\*\* (.+?)(?:\n|$)', 'student_name'),
            
            # Duration patterns (consultations are typically 15 minutes)
            (r'Duration:\s*(\d+)\s*minutes?', 'duration'),
            (r'(\d+)\s*min', 'duration')
        ]
        
        # Apply all patterns
        for pattern, key in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                consultation_info[key] = value
        
        # Clean up and validate extracted data
        if consultation_info:
            # Set defaults for missing fields
            consultation_info.setdefault('consultation_id', None)
            consultation_info.setdefault('scheduled_at', 'N/A')
            consultation_info.setdefault('status', 'scheduled')
            consultation_info.setdefault('coach_name', 'N/A')
            consultation_info.setdefault('student_name', 'N/A')
            consultation_info.setdefault('duration', '15')
            
            return consultation_info
        
        return None
        
    except Exception as e:
        app.logger.error(f"Error extracting consultation info: {e}")
        return None

# Import timezone utilities before routes to avoid circular imports
from utils import (
    get_user_timezone, 
    convert_utc_to_user_timezone, 
    format_datetime_for_user,
    format_relative_time,
    get_timezone_offset
)

# Import routes after app creation
import routes

# Register all routes with the app
try:
    routes.register_routes(app)
    print("✅ All routes registered successfully!")
except Exception as e:
    print(f"❌ Error registering routes: {e}")

# Register template globals
try:
    from utils import get_current_user, get_available_timezones
    app.jinja_env.globals['get_current_user'] = get_current_user
    app.jinja_env.globals['get_available_timezones'] = get_available_timezones
    print("✅ Template globals registered successfully!")
except Exception as e:
    print(f"❌ Error registering template globals: {e}")

# Exempt webhook endpoints from CSRF protection (moved to avoid circular import)
try:
    csrf.exempt(routes.scheduler_webhook)
except AttributeError:
    # scheduler_webhook might not be available due to circular import
    # This is not critical for core functionality
    pass

# ============================================================================
# TIMEZONE TEMPLATE FILTERS
# ============================================================================

@app.template_filter('user_timezone')
def user_timezone_filter(datetime_obj):
    """Convert datetime to user's timezone"""
    from utils import get_current_user
    from datetime import date, datetime
    
    if not datetime_obj:
        return ''
    
    # Handle date objects (no timezone conversion needed for dates)
    if isinstance(datetime_obj, date) and not isinstance(datetime_obj, datetime):
        return datetime_obj
    
    # Get current user
    user = get_current_user()
    user_tz = get_user_timezone(user)
    return convert_utc_to_user_timezone(datetime_obj, user_tz)

@app.template_filter('format_datetime')
def format_datetime_filter(datetime_obj, format_type='full'):
    """Format datetime for user's timezone"""
    from utils import get_current_user
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
    
    # Get current user
    user = get_current_user()
    user_tz = get_user_timezone(user)
    return format_datetime_for_user(datetime_obj, user_tz, format_type)

@app.template_filter('relative_time')
def relative_time_filter(datetime_obj):
    """Format datetime as relative time"""
    from utils import get_current_user
    from datetime import date, datetime
    
    if not datetime_obj:
        return ''
    
    # Handle date objects (no timezone conversion needed for dates)
    if isinstance(datetime_obj, date) and not isinstance(datetime_obj, datetime):
        return format_relative_time(datetime_obj)
    
    # Get current user
    user = get_current_user()
    user_tz = get_user_timezone(user)
    local_time = convert_utc_to_user_timezone(datetime_obj, user_tz)
    return format_relative_time(local_time)

@app.template_filter('timezone_offset')
def timezone_offset_filter(timezone_name):
    """Get timezone offset display"""
    return get_timezone_offset(timezone_name)

@app.template_filter('utc_iso')
def utc_iso_filter(datetime_obj):
    """Convert datetime to UTC ISO format for JavaScript"""
    from datetime import timezone
    
    if not datetime_obj:
        return ''
    
    # Ensure datetime is timezone-aware and in UTC
    if datetime_obj.tzinfo is None:
        datetime_obj = datetime_obj.replace(tzinfo=timezone.utc)
    else:
        datetime_obj = datetime_obj.astimezone(timezone.utc)
    
    return datetime_obj.isoformat()

@app.template_filter('from_json')
def from_json_filter(json_string):
    """Parse JSON string to Python object"""
    try:
        import json
        if isinstance(json_string, str):
            return json.loads(json_string)
        return json_string
    except (json.JSONDecodeError, TypeError):
        return None

# Create notification table if it doesn't exist (for production)
# This will be called after the app is fully initialized

def initialize_app():
    """Initialize the application - create tables, etc."""
    with app.app_context():
        try:
            # Initialize notification scheduler
            from notification_scheduler import init_notification_scheduler
            init_notification_scheduler(app)
            
            app.logger.info("App initialization completed successfully")
        except Exception as e:
            app.logger.error(f"Error during app initialization: {e}")

if __name__ == '__main__':
    initialize_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
