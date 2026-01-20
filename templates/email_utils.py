import secrets
import logging
from datetime import datetime, timedelta
from flask import url_for, current_app, render_template_string
from flask_mail import Message
from models import User

def get_mail():
    """Get mail instance from current app context"""
    from app import mail
    return mail

def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

def send_verification_email(user):
    """Send verification email to user"""
    # Check if email verification is enabled
    from utils import is_email_verification_enabled
    if not is_email_verification_enabled():
        logging.info(f"Email verification disabled - skipping email send to {user.email}")
        return True  # Return True to indicate "success" even though no email was sent
    
    try:
        # Generate verification token
        token = generate_verification_token()
        user.verification_token = token
        user.token_created_at = datetime.utcnow()
        
        # Get the base URL for verification links
        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        
        verification_url = f"{base_url}/verify-email/{token}"
        
        # Create email message
        msg = Message(
            subject="Verify Your Email - Skileez",
            recipients=[user.email],
            html=render_verification_email_html(user, verification_url)
        )
        
        # Send email
        get_mail().send(msg)
        
        # Save token to database
        from app import db
        db.session.commit()
        
        logging.info(f"Verification email sent to {user.email}")
        return True
        
    except Exception as e:
        logging.error(f"Error sending verification email to {user.email}: {e}")
        return False

def render_verification_email_html(user, verification_url):
    """Render HTML email template for verification"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verify Your Email - Skileez</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .welcome-text {{
                font-size: 18px;
                margin-bottom: 20px;
                color: #555;
            }}
            .verification-button {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                padding: 15px 30px;
                border-radius: 25px;
                font-size: 16px;
                font-weight: 600;
                margin: 20px 0;
                text-align: center;
                transition: transform 0.2s ease;
            }}
            .verification-button:hover {{
                transform: translateY(-2px);
            }}
            .footer {{
                background-color: #f8f9fa;
                padding: 20px 30px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
            .warning {{
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 4px;
                padding: 15px;
                margin: 20px 0;
                color: #856404;
            }}
            .link-text {{
                word-break: break-all;
                color: #667eea;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎓 Skileez</h1>
                <p>Your Learning Journey Starts Here</p>
            </div>
            
            <div class="content">
                <div class="welcome-text">
                    Hi {user.first_name}!
                </div>
                
                <p>Welcome to Skileez! We're excited to have you join our community of learners and coaches.</p>
                
                <p>To complete your registration and start your learning journey, please verify your email address by clicking the button below:</p>
                
                <div style="text-align: center;">
                    <a href="{verification_url}" class="verification-button">
                        ✅ Verify Email Address
                    </a>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Important:</strong> This verification link will expire in 24 hours. If you don't verify your email within this time, you'll need to request a new verification email.
                </div>
                
                <p>If the button above doesn't work, you can copy and paste this link into your browser:</p>
                <p><a href="{verification_url}" class="link-text">{verification_url}</a></p>
                
                <p>If you didn't create an account on Skileez, you can safely ignore this email.</p>
                
                <p>Best regards,<br>The Skileez Team</p>
            </div>
            
            <div class="footer">
                <p>© 2024 Skileez. All rights reserved.</p>
                <p>This email was sent to {user.email}</p>
            </div>
        </div>
    </body>
    </html>
    """

def verify_email_token(token):
    """Verify email token and mark user as verified"""
    try:
        # Find user by token
        user = User.query.filter_by(verification_token=token).first()
        
        if not user:
            return False, "Invalid verification token"
        
        # Check if token is expired (24 hours)
        if user.token_created_at:
            expiration_time = user.token_created_at + timedelta(hours=24)
            if datetime.utcnow() > expiration_time:
                return False, "Verification token has expired"
        
        # Mark user as verified
        user.email_verified = True
        user.verification_token = None
        user.token_created_at = None
        
        # Save changes
        from app import db
        db.session.commit()
        
        logging.info(f"Email verified for user {user.email}")
        return True, "Email verified successfully"
        
    except Exception as e:
        logging.error(f"Error verifying email token: {str(e)}")
        return False, "Error verifying email"

def resend_verification_email(user):
    """Resend verification email to user"""
    # Check if email verification is enabled
    from utils import is_email_verification_enabled
    if not is_email_verification_enabled():
        logging.info(f"Email verification disabled - skipping resend to {user.email}")
        return True  # Return True to indicate "success" even though no email was sent
    
    # Clear any existing token
    user.verification_token = None
    user.token_created_at = None
    
    # Send new verification email
    return send_verification_email(user)

def send_email_change_verification(user, new_email):
    """Send email change verification to new email address"""
    # Check if email verification is enabled
    from utils import is_email_verification_enabled
    if not is_email_verification_enabled():
        logging.info(f"Email verification disabled - skipping email change verification to {new_email}")
        return True  # Return True to indicate "success" even though no email was sent
    
    try:
        # Generate email change verification token
        token = generate_verification_token()
        user.email_change_token = token
        user.email_change_token_created_at = datetime.utcnow()
        user.new_email = new_email
        
        # Get the base URL for verification links
        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        
        verification_url = f"{base_url}/verify-email-change/{token}"
        
        # Create email message
        msg = Message(
            subject="Verify Your New Email Address - Skileez",
            recipients=[new_email],
            html=render_email_change_verification_html(user, verification_url, new_email)
        )
        
        # Send email
        get_mail().send(msg)
        
        # Save token to database
        from app import db
        db.session.commit()
        
        logging.info(f"Email change verification sent to {new_email}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send email change verification to {new_email}: {str(e)}")
        return False

def render_email_change_verification_html(user, verification_url, new_email):
    """Render HTML for email change verification email"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verify Your New Email - Skileez</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8fafc;
            }}
            .container {{
                background-color: white;
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo {{
                font-size: 28px;
                font-weight: bold;
                color: #6366f1;
                margin-bottom: 10px;
            }}
            .title {{
                font-size: 24px;
                font-weight: bold;
                color: #1f2937;
                margin-bottom: 20px;
            }}
            .content {{
                margin-bottom: 30px;
            }}
            .verification-button {{
                display: inline-block;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                margin: 20px 0;
                text-align: center;
            }}
            .warning {{
                background-color: #fef3c7;
                border: 1px solid #f59e0b;
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
                color: #92400e;
            }}
            .link-text {{
                color: #6366f1;
                text-decoration: none;
                word-break: break-all;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">Skileez</div>
                <div class="title">Verify Your New Email Address</div>
            </div>
            
            <div class="content">
                <p>Hello {user.first_name},</p>
                
                <p>You have requested to change your email address on Skileez from <strong>{user.email}</strong> to <strong>{new_email}</strong>.</p>
                
                <p>To complete this change, please click the button below to verify your new email address:</p>
                
                <div style="text-align: center;">
                    <a href="{verification_url}" class="verification-button">
                        ✅ Verify New Email Address
                    </a>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Important:</strong> This verification link will expire in 24 hours. If you don't verify your email within this time, you'll need to request a new email change.
                </div>
                
                <p>If the button above doesn't work, you can copy and paste this link into your browser:</p>
                <p><a href="{verification_url}" class="link-text">{verification_url}</a></p>
                
                <p>If you didn't request this email change, you can safely ignore this email and your current email address will remain unchanged.</p>
                
                <p>Best regards,<br>The Skileez Team</p>
            </div>
            
            <div class="footer">
                <p>© 2024 Skileez. All rights reserved.</p>
                <p>This email was sent to {new_email}</p>
            </div>
        </div>
    </body>
    </html>
    """

def verify_email_change_token(token):
    """Verify email change token and update user's email"""
    try:
        # Find user by email change token
        user = User.query.filter_by(email_change_token=token).first()
        
        if not user:
            return False, "Invalid email change verification token"
        
        # Check if token is expired (24 hours)
        if user.email_change_token_created_at:
            expiration_time = user.email_change_token_created_at + timedelta(hours=24)
            if datetime.utcnow() > expiration_time:
                return False, "Email change verification token has expired"
        
        # Check if new email is still available
        if user.new_email:
            existing_user = User.query.filter_by(email=user.new_email).first()
            if existing_user and existing_user.id != user.id:
                return False, "The new email address is already registered by another user"
        
        # Update user's email
        old_email = user.email
        user.email = user.new_email
        user.email_verified = True  # Mark as verified since they verified the new email
        user.new_email = None
        user.email_change_token = None
        user.email_change_token_created_at = None
        
        # Save changes
        from app import db
        db.session.commit()
        
        logging.info(f"Email changed for user from {old_email} to {user.email}")
        return True, "Email changed successfully"
        
    except Exception as e:
        logging.error(f"Error verifying email change token: {str(e)}")
        return False, "Error changing email"

def is_email_verification_required(user):
    """Check if email verification is required for login"""
    from utils import is_email_verification_enabled
    if not is_email_verification_enabled():
        return False  # Email verification not required if disabled
    return not user.email_verified 

def send_contract_accepted_email(contract):
    """Send email notification when contract is accepted"""
    try:
        # Check if email verification is enabled
        from utils import is_email_verification_enabled
        if not is_email_verification_enabled():
            logging.info(f"Email verification disabled - skipping contract accepted email to {contract.student.email}")
            return True
        
        # Create email message for student
        msg = Message(
            subject=f"Contract Accepted - {contract.proposal.learning_request.title}",
            recipients=[contract.student.email],
            html=render_contract_accepted_email_html(contract)
        )
        
        # Send email
        get_mail().send(msg)
        
        logging.info(f"Contract accepted email sent to {contract.student.email}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send contract accepted email to {contract.student.email}: {str(e)}")
        return False

def send_contract_rejected_email(contract):
    """Send email notification when contract is rejected"""
    try:
        # Check if email verification is enabled
        from utils import is_email_verification_enabled
        if not is_email_verification_enabled():
            logging.info(f"Email verification disabled - skipping contract rejected email to {contract.student.email}")
            return True
        
        # Create email message for student
        msg = Message(
            subject=f"Contract Rejected - {contract.proposal.learning_request.title}",
            recipients=[contract.student.email],
            html=render_contract_rejected_email_html(contract)
        )
        
        # Send email
        get_mail().send(msg)
        
        logging.info(f"Contract rejected email sent to {contract.student.email}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send contract rejected email to {contract.student.email}: {str(e)}")
        return False

def send_payment_successful_email(contract):
    """Send email notification when contract payment is completed"""
    try:
        # Check if email verification is enabled
        from utils import is_email_verification_enabled
        if not is_email_verification_enabled():
            logging.info(f"Email verification disabled - skipping payment completed emails")
            return True
        
        # Send email to student
        student_msg = Message(
            subject=f"Payment Completed - {contract.proposal.learning_request.title}",
            recipients=[contract.student.email],
            html=render_payment_successful_student_email_html(contract)
        )
        get_mail().send(student_msg)
        
        # Send email to coach
        coach_msg = Message(
            subject=f"Payment Received - {contract.proposal.learning_request.title}",
            recipients=[contract.coach.email],
            html=render_payment_successful_coach_email_html(contract)
        )
        get_mail().send(coach_msg)
        
        logging.info(f"Payment completed emails sent to {contract.student.email} and {contract.coach.email}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send payment completed emails: {str(e)}")
        return False

def render_contract_accepted_email_html(contract):
    """Render HTML email template for contract acceptance"""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    
    contract_url = f"{base_url}/contracts/{contract.id}"
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Contract Accepted - Skileez</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .success-icon {{
                text-align: center;
                font-size: 48px;
                margin-bottom: 20px;
            }}
            .contract-details {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .action-button {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ Contract Accepted!</h1>
            </div>
            
            <div class="content">
                <div class="success-icon">🎉</div>
                
                <p>Hello {contract.student.first_name},</p>
                
                <p>Great news! Your coach has accepted the contract for <strong>{contract.proposal.learning_request.title}</strong>.</p>
                
                <div class="contract-details">
                    <h3>Contract Details:</h3>
                    <p><strong>Project:</strong> {contract.proposal.learning_request.title}</p>
                    <p><strong>Coach:</strong> {contract.coach.first_name} {contract.coach.last_name}</p>
                    <p><strong>Total Sessions:</strong> {contract.total_sessions}</p>
                    <p><strong>Total Amount:</strong> ${contract.total_amount}</p>
                    <p><strong>Start Date:</strong> {contract.start_date.strftime('%B %d, %Y')}</p>
                </div>
                
                <p>To proceed with your learning journey, please complete the payment for this contract:</p>
                
                <div style="text-align: center;">
                    <a href="{contract_url}" class="action-button">
                        💳 Complete Payment
                    </a>
                </div>
                
                <p>Once payment is completed, your contract will be activated and you can start scheduling your sessions.</p>
                
                <p>Best regards,<br>The Skileez Team</p>
            </div>
            
            <div class="footer">
                <p>© 2024 Skileez. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

def render_contract_rejected_email_html(contract):
    """Render HTML email template for contract rejection"""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Contract Declined - Skileez</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .info-icon {{
                text-align: center;
                font-size: 48px;
                margin-bottom: 20px;
            }}
            .contract-details {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>❌ Contract Rejected</h1>
            </div>
            
            <div class="content">
                <div class="info-icon">📝</div>
                
                <p>Hello {contract.student.first_name},</p>
                
                <p>We wanted to let you know that the contract for <strong>{contract.proposal.learning_request.title}</strong> has been rejected by the coach.</p>
                
                <div class="contract-details">
                    <h3>Contract Details:</h3>
                    <p><strong>Project:</strong> {contract.proposal.learning_request.title}</p>
                    <p><strong>Coach:</strong> {contract.coach.first_name} {contract.coach.last_name}</p>
                    <p><strong>Total Sessions:</strong> {contract.total_sessions}</p>
                    <p><strong>Total Amount:</strong> ${contract.total_amount}</p>
                </div>
                
                <p>Don't worry! You can:</p>
                <ul>
                    <li>Create a new contract with different terms</li>
                    <li>Find another coach for this project</li>
                    <li>Modify your learning request</li>
                </ul>
                
                <p>We're here to help you find the perfect learning experience.</p>
                
                <p>Best regards,<br>The Skileez Team</p>
            </div>
            
            <div class="footer">
                <p>© 2024 Skileez. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

def render_payment_successful_student_email_html(contract):
    """Render HTML email template for payment completion (student)"""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    
    sessions_url = f"{base_url}/sessions"
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Payment Completed - Skileez</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .success-icon {{
                text-align: center;
                font-size: 48px;
                margin-bottom: 20px;
            }}
            .contract-details {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .action-button {{
                display: inline-block;
                background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💳 Payment Completed!</h1>
            </div>
            
            <div class="content">
                <div class="success-icon">🎉</div>
                
                <p>Hello {contract.student.first_name},</p>
                
                <p>Excellent! Your payment for <strong>{contract.proposal.learning_request.title}</strong> has been completed successfully.</p>
                
                <div class="contract-details">
                    <h3>Contract Details:</h3>
                    <p><strong>Project:</strong> {contract.proposal.learning_request.title}</p>
                    <p><strong>Coach:</strong> {contract.coach.first_name} {contract.coach.last_name}</p>
                    <p><strong>Total Sessions:</strong> {contract.total_sessions}</p>
                    <p><strong>Amount Paid:</strong> ${contract.total_amount}</p>
                    <p><strong>Status:</strong> <span style="color: #00b894; font-weight: bold;">Active</span></p>
                </div>
                
                <p>Your contract is now active and ready for your learning journey! You can now schedule your sessions.</p>
                
                <div style="text-align: center;">
                    <a href="{sessions_url}" class="action-button">
                        📅 View Sessions
                    </a>
                </div>
                
                <p>Your coach has been notified and is ready to help you achieve your learning goals.</p>
                
                <p>Best regards,<br>The Skileez Team</p>
            </div>
            
            <div class="footer">
                <p>© 2024 Skileez. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

def render_payment_successful_coach_email_html(contract):
    """Render HTML email template for payment completion (coach)"""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    
    sessions_url = f"{base_url}/sessions"
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Payment Received - Skileez</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .success-icon {{
                text-align: center;
                font-size: 48px;
                margin-bottom: 20px;
            }}
            .contract-details {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .action-button {{
                display: inline-block;
                background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💰 Payment Received!</h1>
            </div>
            
            <div class="content">
                <div class="success-icon">🎉</div>
                
                <p>Hello {contract.coach.first_name},</p>
                
                <p>Great news! Payment has been completed for the contract <strong>{contract.proposal.learning_request.title}</strong>.</p>
                
                <div class="contract-details">
                    <h3>Contract Details:</h3>
                    <p><strong>Project:</strong> {contract.proposal.learning_request.title}</p>
                    <p><strong>Student:</strong> {contract.student.first_name} {contract.student.last_name}</p>
                    <p><strong>Total Sessions:</strong> {contract.total_sessions}</p>
                    <p><strong>Amount Received:</strong> ${contract.total_amount}</p>
                    <p><strong>Status:</strong> <span style="color: #00b894; font-weight: bold;">Active</span></p>
                </div>
                
                <p>The contract is now active and ready for your coaching sessions. The student is ready to begin their learning journey!</p>
                
                <div style="text-align: center;">
                    <a href="{sessions_url}" class="action-button">
                        📅 View Sessions
                    </a>
                </div>
                
                <p>You can now schedule and conduct your coaching sessions with the student.</p>
                
                <p>Best regards,<br>The Skileez Team</p>
            </div>
            
            <div class="footer">
                <p>© 2024 Skileez. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """ 

def send_session_scheduled_email(session):
    """Send email notification when a session is scheduled"""
    try:
        from models import Session, Contract, Proposal, LearningRequest, User
        
        # Get session details
        session = Session.query.get(session.id)
        if not session:
            return False
        
        contract = session.get_contract()
        if not contract:
            return False
        
        # Get participants
        student = User.query.get(contract.student_id)
        coach = User.query.get(contract.coach_id)
        
        if not student or not coach:
            return False
        
        # Format session time
        session_time = session.scheduled_at.strftime('%B %d, %Y at %I:%M %p')
        
        # Send to student
        student_msg = Message(
            subject=f"Session Scheduled - {contract.proposal.learning_request.title}",
            recipients=[student.email],
            html=f"""
            <h2>Session Scheduled</h2>
            <p>Hello {student.first_name},</p>
            <p>Your session with {coach.first_name} {coach.last_name} has been scheduled for:</p>
            <p><strong>{session_time}</strong></p>
            <p>Duration: {session.duration_minutes or 60} minutes</p>
            <p>You will receive a reminder 1 hour before the session.</p>
            <p>Best regards,<br>Skileez Team</p>
            """
        )
        get_mail().send(student_msg)
        
        # Send to coach
        coach_msg = Message(
            subject=f"Session Scheduled - {contract.proposal.learning_request.title}",
            recipients=[coach.email],
            html=f"""
            <h2>Session Scheduled</h2>
            <p>Hello {coach.first_name},</p>
            <p>Your session with {student.first_name} {student.last_name} has been scheduled for:</p>
            <p><strong>{session_time}</strong></p>
            <p>Duration: {session.duration_minutes or 60} minutes</p>
            <p>You will receive a reminder 1 hour before the session.</p>
            <p>Best regards,<br>Skileez Team</p>
            """
        )
        get_mail().send(coach_msg)
        
        logging.info(f"Session scheduled emails sent for session {session.id}")
        return True
        
    except Exception as e:
        logging.error(f"Error sending session scheduled email: {e}")
        return False

def send_session_reminder_email(session, reminder_type='1h'):
    """Send session reminder email"""
    try:
        from models import Session, Contract, User
        
        # Get session details
        session = Session.query.get(session.id)
        if not session:
            return False
        
        contract = session.get_contract()
        if not contract:
            return False
        
        # Get participants
        student = User.query.get(contract.student_id)
        coach = User.query.get(contract.coach_id)
        
        if not student or not coach:
            return False
        
        # Format session time
        session_time = session.scheduled_at.strftime('%B %d, %Y at %I:%M %p')
        
        # Get base URL for join links
        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        
        join_url = f"{base_url}/sessions/{session.id}/join"
        
        # Determine reminder message
        if reminder_type == '1h':
            subject = f"Session Reminder - 1 hour until your session"
            time_text = "1 hour"
        elif reminder_type == '24h':
            subject = f"Session Reminder - 24 hours until your session"
            time_text = "24 hours"
        else:
            subject = f"Session Reminder - Your session is starting soon"
            time_text = "soon"
        
        # Send to student
        student_msg = Message(
            subject=subject,
            recipients=[student.email],
            html=f"""
            <h2>Session Reminder</h2>
            <p>Hello {student.first_name},</p>
            <p>This is a reminder that your session with {coach.first_name} {coach.last_name} is starting in {time_text}.</p>
            <p><strong>Session Time:</strong> {session_time}</p>
            <p><strong>Duration:</strong> {session.duration_minutes or 60} minutes</p>
            <p><a href="{join_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Join Session</a></p>
            <p>Best regards,<br>Skileez Team</p>
            """
        )
        get_mail().send(student_msg)
        
        # Send to coach
        coach_msg = Message(
            subject=subject,
            recipients=[coach.email],
            html=f"""
            <h2>Session Reminder</h2>
            <p>Hello {coach.first_name},</p>
            <p>This is a reminder that your session with {student.first_name} {student.last_name} is starting in {time_text}.</p>
            <p><strong>Session Time:</strong> {session_time}</p>
            <p><strong>Duration:</strong> {session.duration_minutes or 60} minutes</p>
            <p><a href="{join_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Join Session</a></p>
            <p>Best regards,<br>Skileez Team</p>
            """
        )
        get_mail().send(coach_msg)
        
        logging.info(f"Session reminder emails sent for session {session.id} ({reminder_type})")
        return True
        
    except Exception as e:
        logging.error(f"Error sending session reminder email: {e}")
        return False

def send_email(to_email, subject, template=None, html_content=None, **kwargs):
    """
    Generic email sending function for the scheduling system
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        template (str): Template name (optional)
        html_content (str): HTML content (optional)
        **kwargs: Additional context variables for template rendering
    """
    try:
        # Check if email is enabled
        from utils import is_email_verification_enabled
        if not is_email_verification_enabled():
            logging.info(f"Email disabled - skipping email send to {to_email}")
            return True
        
        # Create email message
        msg = Message(
            subject=subject,
            recipients=[to_email]
        )
        
        # Set HTML content
        if html_content:
            msg.html = html_content
        elif template:
            # For now, we'll create a simple template
            # In a full implementation, you'd load from actual template files
            msg.html = render_simple_email_template(template, **kwargs)
        else:
            logging.error("No content provided for email")
            return False
        
        # Send email
        get_mail().send(msg)
        
        logging.info(f"Email sent to {to_email}: {subject}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

def render_simple_email_template(template_name, **kwargs):
    """
    Render a simple email template for scheduling notifications
    """
    if 'call_scheduled' in template_name or 'consultation_scheduled' in template_name or 'session_scheduled' in template_name:
        call = kwargs.get('call')
        student = kwargs.get('student')
        coach = kwargs.get('coach')
        
        # Format the scheduled date
        scheduled_date = "TBD"
        if call and hasattr(call, 'scheduled_at') and call.scheduled_at:
            scheduled_date = call.scheduled_at.strftime('%B %d, %Y at %I:%M %p')
        
        duration = getattr(call, 'duration_minutes', 15) if call else 15
        student_name = getattr(student, 'first_name', 'there') if student else 'there'
        coach_name = getattr(coach, 'first_name', 'your coach') if coach else 'your coach'
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #667eea; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .button {{ background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📅 Call Scheduled</h1>
                </div>
                <div class="content">
                    <p>Hello {student_name},</p>
                    <p>Your call with {coach_name} has been scheduled.</p>
                    <p><strong>Date:</strong> {scheduled_date}</p>
                    <p><strong>Duration:</strong> {duration} minutes</p>
                    <p>You'll receive a notification when it's time to join the call.</p>
                    <p>Best regards,<br>The Skileez Team</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    elif 'reminder' in template_name:
        call = kwargs.get('call')
        student = kwargs.get('student')
        coach = kwargs.get('coach')
        
        # Format the scheduled date
        scheduled_date = "TBD"
        if call and hasattr(call, 'scheduled_at') and call.scheduled_at:
            scheduled_date = call.scheduled_at.strftime('%B %d, %Y at %I:%M %p')
        
        student_name = getattr(student, 'first_name', 'there') if student else 'there'
        coach_name = getattr(coach, 'first_name', 'your coach') if coach else 'your coach'
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #f39c12; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .button {{ background: #f39c12; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⏰ Call Reminder</h1>
                </div>
                <div class="content">
                    <p>Hello {student_name},</p>
                    <p>This is a reminder about your upcoming call with {coach_name}.</p>
                    <p><strong>Date:</strong> {scheduled_date}</p>
                    <p>Please be ready to join the call at the scheduled time.</p>
                    <p>Best regards,<br>The Skileez Team</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    else:
        # Default template
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #667eea; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Skileez Notification</h1>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>You have a new notification from Skileez.</p>
                    <p>Best regards,<br>The Skileez Team</p>
                </div>
            </div>
        </body>
        </html>
        """ 