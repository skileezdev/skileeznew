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

def send_verification_email(user):
    """Send verification email to user - SIMPLIFIED RELIABLE VERSION"""
    print(f"DEBUG: send_verification_email called for user {user.email}")
    
    try:
        # Generate verification token
        token = generate_verification_token()
        user.verification_token = token
        user.token_created_at = datetime.utcnow()
        
        # Get the base URL for verification links
        try:
            base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
        except:
            base_url = 'http://localhost:5000'
            
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        
        verification_url = f"{base_url}/verify-email/{token}"
        print(f"DEBUG: Verification URL: {verification_url}")
        
        # Create simple email message
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
            <hr style="margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">This email was sent from Skileez - Your Learning Platform</p>
        </body>
        </html>
        """
        
        # Send email
        mail = get_mail()
        if mail:
            msg = Message(subject, recipients=[user.email], html=html_content)
            mail.send(msg)
            print(f"DEBUG: Email sent successfully to {user.email}")
            
            # Save token to database
            try:
                from app import db
                db.session.commit()
                print(f"DEBUG: Token saved to database for user {user.email}")
            except Exception as e:
                print(f"DEBUG: Database commit error: {e}")
            
            return True
        else:
            print("DEBUG: Mail instance not available")
            return False
            
    except Exception as e:
        print(f"DEBUG: Error sending verification email: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
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
