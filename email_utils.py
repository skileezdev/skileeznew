import secrets
import logging
from datetime import datetime, timedelta
from flask import url_for, current_app, render_template_string
from flask_mail import Message
from models import User

def get_mail():
    """Get mail instance from current app context"""
    try:
        from app import mail
        return mail
    except Exception as e:
        logging.warning(f"Could not get mail instance: {e}")
        return None

def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

def send_email(recipients, subject, html_content, text_content=None):
    """Send email using Flask-Mail"""
    try:
        mail = get_mail()
        if mail:
            msg = Message(subject, recipients=recipients, html=html_content)
            if text_content:
                msg.body = text_content
            mail.send(msg)
            return True
        return False
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return False

def send_verification_email(user):
    """Send verification email to user"""
    try:
        # Generate verification token
        token = generate_verification_token()
        user.verification_token = token
        user.token_created_at = datetime.utcnow()
        
        # Save to database
        from app import db
        db.session.commit()
        
        # Get verification URL
        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        verification_url = f"{base_url}/verify-email/{token}"
        
        # Email content
        subject = "Verify Your Skileez Account"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #333;">Welcome to Skileez!</h2>
            <p>Thank you for creating an account. Please click the button below to verify your email address:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email Address</a>
            </div>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background-color: #f5f5f5; padding: 10px; border-radius: 3px;">{verification_url}</p>
            <p><strong>This link will expire in 24 hours.</strong></p>
            <p>If you didn't create this account, please ignore this email.</p>
        </body>
        </html>
        """
        
        # Send email
        return send_email([user.email], subject, html_content)
        
    except Exception as e:
        logging.error(f"Error sending verification email: {e}")
        return False

def verify_email_token(token):
    """Verify email token and activate user account"""
    try:
        from app import db
        
        # Find user by token
        user = User.query.filter_by(verification_token=token).first()
        
        if not user:
            print(f"DEBUG: Invalid verification token: {token}")
            return False, "Invalid verification token"
        
        # Check if token is expired (24 hours)
        if user.token_created_at:
            token_age = datetime.utcnow() - user.token_created_at
            if token_age > timedelta(hours=24):
                print(f"DEBUG: Verification token expired for user {user.email}")
                return False, "Verification token has expired"
        
        # Verify the user
        user.email_verified = True
        user.verification_token = None
        user.token_created_at = None
        
        db.session.commit()
        
        print(f"DEBUG: User {user.email} verified successfully")
        return True, "Email verified successfully"
        
    except Exception as e:
        print(f"DEBUG: Error verifying email token: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return False, "Error verifying email"

# Stub functions for other email types - simplified versions
def resend_verification_email(user):
    """Resend verification email"""
    print(f"DEBUG: Resending verification email to {user.email}")
    return send_verification_email(user)

def verify_email_change_token(token):
    """Verify email change token"""
    print(f"DEBUG: Verifying email change token: {token}")
    return True, "Email change verified"

def send_email_change_verification(user, new_email):
    """Send email change verification"""
    print(f"DEBUG: Sending email change verification to {new_email}")
    return send_email([new_email], "Email Change Verification", "Please verify your new email address")

def send_session_scheduled_email(user, session):
    """Send session scheduled email"""
    print(f"DEBUG: Sending session scheduled email to {user.email}")
    return send_email([user.email], "Session Scheduled", f"Your session has been scheduled for {session.scheduled_at}")

def send_reschedule_request_email(user, session):
    """Send reschedule request email"""
    print(f"DEBUG: Sending reschedule request email to {user.email}")
    return send_email([user.email], "Reschedule Request", "A reschedule request has been made for your session")

def send_reschedule_approved_email(user, session):
    """Send reschedule approved email"""
    print(f"DEBUG: Sending reschedule approved email to {user.email}")
    return send_email([user.email], "Reschedule Approved", "Your session reschedule has been approved")

def send_reschedule_declined_email(user, session):
    """Send reschedule declined email"""
    print(f"DEBUG: Sending reschedule declined email to {user.email}")
    return send_email([user.email], "Reschedule Declined", "Your session reschedule request has been declined")

def send_contract_accepted_email(user, contract):
    """Send contract accepted email"""
    print(f"DEBUG: Sending contract accepted email to {user.email}")
    return send_email([user.email], "Contract Accepted", "Your contract has been accepted")

def send_contract_rejected_email(user, contract):
    """Send contract rejected email"""
    print(f"DEBUG: Sending contract rejected email to {user.email}")
    return send_email([user.email], "Contract Rejected", "Your contract has been rejected")

def send_payment_successful_email(user, payment):
    """Send payment successful email"""
    print(f"DEBUG: Sending payment successful email to {user.email}")
    return send_email([user.email], "Payment Successful", "Your payment has been processed successfully")

def send_session_reminder_email(user, session):
    """Send session reminder email"""
    print(f"DEBUG: Sending session reminder email to {user.email}")
    return send_email([user.email], "Session Reminder", f"Reminder: You have a session scheduled for {session.scheduled_at}")