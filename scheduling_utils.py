import os
import logging
from datetime import datetime, timedelta, timezone
from flask import current_app
from models import ScheduledCall, CallNotification, User, Contract, Message
from email_utils import send_email
from notification_utils import create_system_notification
import pytz

logger = logging.getLogger(__name__)

def get_db_session():
    """Get database session from current app context"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker(bind=engine)
    return Session()

def create_call_scheduled_message(call, session=None):
    """
    Create an interactive session card message in the chat between student and coach
    """
    try:
        import json
        from datetime import datetime
        
        # Get user information
        student = User.query.get(call.student_id)
        coach = User.query.get(call.coach_id)
        
        if call.call_type == 'free_consultation':
            # Create free consultation card message
            message_data = {
                "consultation_id": call.id,
                "scheduled_at": call.scheduled_at.strftime("%B %d, %Y at %I:%M %p"),
                "status": call.status,
                "coach_name": f"{coach.first_name} {coach.last_name}",
                "student_name": f"{student.first_name} {student.last_name}",
                "duration": "15"
            }
            
            message = Message(
                sender_id=call.student_id,
                recipient_id=call.coach_id,
                content=json.dumps(message_data),
                message_type='FREE_CONSULTATION',
                sender_role='student',
                recipient_role='coach',
                call_id=call.id
            )
            
        else:
            # Create paid session card message
            contract = Contract.query.get(call.contract_id) if call.contract_id else None
            
            # Get session number if it's part of a contract
            session_number = None
            if contract:
                # Count previous sessions for this contract
                previous_sessions = ScheduledCall.query.filter_by(
                    contract_id=call.contract_id,
                    call_type='paid_session'
                ).count()
                session_number = f"{previous_sessions + 1} of {contract.total_sessions}"
            
            message_data = {
                "session_id": call.id,
                "session_number": session_number,
                "scheduled_at": call.scheduled_at.strftime("%B %d, %Y at %I:%M %p"),
                "duration": str(call.duration_minutes),
                "status": call.status,
                "session_type": "paid",
                "contract_title": contract.title if contract else "Learning Session",
                "coach_name": f"{coach.first_name} {coach.last_name}",
                "student_name": f"{student.first_name} {student.last_name}"
            }
            
            message = Message(
                sender_id=call.student_id,
                recipient_id=call.coach_id,
                content=json.dumps(message_data),
                message_type='SESSION_SCHEDULED',
                sender_role='student',
                recipient_role='coach',
                call_id=call.id
            )
        
        if session is None:
            session = get_db_session()
            should_close = True
        else:
            should_close = False
            
        session.add(message)
        session.commit()
        
        if should_close:
            session.close()
        
        logger.info(f"Created interactive session card message for call {call.id}")
        
    except Exception as e:
        logger.error(f"Error creating interactive session card message: {e}")

def get_scheduling_options(student_id, coach_id):
    """
    Determine what scheduling options are available based on contract status
    Returns: 'free_consultation', 'paid_sessions', or 'both'
    """
    try:
        # Check if there's an active contract with payment
        contract = Contract.query.filter_by(
            student_id=student_id,
            coach_id=coach_id,
            status='active'
        ).first()
        
        if contract and contract.payment_status == 'paid':
            return 'paid_sessions'
        else:
            return 'free_consultation'
            
    except Exception as e:
        logger.error(f"Error checking scheduling options: {e}")
        return 'free_consultation'

def schedule_free_consultation(student_id, coach_id, scheduled_date, scheduled_time, timezone_name, notes=None):
    """
    Schedule a free 15-minute consultation call
    """
    try:
        # Convert to UTC
        user_tz = pytz.timezone(timezone_name)
        local_dt = user_tz.localize(datetime.combine(scheduled_date, scheduled_time))
        utc_dt = local_dt.astimezone(pytz.UTC)
        
        # Check if there's already a free consultation scheduled
        existing_call = ScheduledCall.query.filter_by(
            student_id=student_id,
            coach_id=coach_id,
            call_type='free_consultation',
            status='scheduled'
        ).first()
        
        if existing_call:
            raise ValueError("You already have a free consultation scheduled with this coach")
        
        # Create the scheduled call
        call = ScheduledCall(
            student_id=student_id,
            coach_id=coach_id,
            call_type='free_consultation',
            scheduled_at=utc_dt,
            duration_minutes=15,
            notes=notes
        )
        
        session = get_db_session()
        session.add(call)
        session.commit()
        
        # Create CALL_SCHEDULED message in chat
        create_call_scheduled_message(call, session)
        
        # Send notifications
        send_call_notifications(call, 'scheduled', session)
        
        session.close()
        return call
        
    except Exception as e:
        logger.error(f"Error scheduling free consultation: {e}")
        raise

def schedule_paid_session(student_id, coach_id, contract_id, scheduled_date, scheduled_time, 
                         timezone_name, duration_minutes=60, notes=None):
    """
    Schedule a paid session call
    """
    try:
        # Verify contract exists and is paid
        contract = Contract.query.get(contract_id)
        if not contract:
            raise ValueError("Contract not found")
        
        if contract.payment_status != 'paid':
            raise ValueError("Contract payment not completed")
        
        # Convert to UTC
        user_tz = pytz.timezone(timezone_name)
        local_dt = user_tz.localize(datetime.combine(scheduled_date, scheduled_time))
        utc_dt = local_dt.astimezone(pytz.UTC)
        
        # Create the scheduled call
        call = ScheduledCall(
            student_id=student_id,
            coach_id=coach_id,
            call_type='paid_session',
            scheduled_at=utc_dt,
            duration_minutes=duration_minutes,
            contract_id=contract_id,
            notes=notes
        )
        
        session = get_db_session()
        session.add(call)
        session.commit()
        
        # Create CALL_SCHEDULED message in chat
        create_call_scheduled_message(call, session)
        
        # Send notifications
        send_call_notifications(call, 'scheduled', session)
        
        session.close()
        return call
        
    except Exception as e:
        logger.error(f"Error scheduling paid session: {e}")
        raise

def send_call_notifications(call, notification_type, session=None):
    """
    Send notifications for call events
    """
    try:
        # Create notification record
        notification = CallNotification(
            call_id=call.id,
            notification_type=notification_type
        )
        
        if session is None:
            session = get_db_session()
            should_close = True
        else:
            should_close = False
            
        session.add(notification)
        session.commit()
        
        if should_close:
            session.close()
        
        # Send email notifications
        if notification_type == 'scheduled':
            send_call_scheduled_emails(call)
        elif notification_type == 'reminder_24h':
            send_call_reminder_emails(call, '24h')
        elif notification_type == 'reminder_1h':
            send_call_reminder_emails(call, '1h')
        elif notification_type == 'ready':
            send_call_ready_notifications(call)
        
        # Send in-app notifications
        send_in_app_call_notifications(call, notification_type)
        
    except Exception as e:
        logger.error(f"Error sending call notifications: {e}")

def send_call_scheduled_emails(call):
    """
    Send confirmation emails when call is scheduled
    """
    try:
        # Email to student
        student = User.query.get(call.student_id)
        coach = User.query.get(call.coach_id)
        
        if call.is_free_consultation:
            subject = f"Free Consultation Scheduled with {coach.first_name}"
            template = 'emails/free_consultation_scheduled.html'
        else:
            subject = f"Learning Session Scheduled with {coach.first_name}"
            template = 'emails/paid_session_scheduled.html'
        
        # Send to student
        send_email(
            to_email=student.email,
            subject=subject,
            template=template,
            call=call,
            student=student,
            coach=coach
        )
        
        # Send to coach
        send_email(
            to_email=coach.email,
            subject=f"New {call.call_type.replace('_', ' ').title()} Scheduled",
            template=template,
            call=call,
            student=student,
            coach=coach
        )
        
    except Exception as e:
        logger.error(f"Error sending call scheduled emails: {e}")

def send_call_reminder_emails(call, reminder_type):
    """
    Send reminder emails (24h or 1h before)
    """
    try:
        student = User.query.get(call.student_id)
        coach = User.query.get(call.coach_id)
        
        if reminder_type == '24h':
            subject = f"Reminder: Your call with {coach.first_name} is tomorrow"
            template = 'emails/call_reminder_24h.html'
        else:
            subject = f"Reminder: Your call with {coach.first_name} starts in 1 hour"
            template = 'emails/call_reminder_1h.html'
        
        # Send to student
        send_email(
            to_email=student.email,
            subject=subject,
            template=template,
            call=call,
            student=student,
            coach=coach
        )
        
        # Send to coach
        send_email(
            to_email=coach.email,
            subject=subject,
            template=template,
            call=call,
            student=student,
            coach=coach
        )
        
    except Exception as e:
        logger.error(f"Error sending call reminder emails: {e}")

def send_call_ready_notifications(call):
    """
    Send notifications when call is ready to join
    """
    try:
        student = User.query.get(call.student_id)
        coach = User.query.get(call.coach_id)
        
        # Create in-app notifications
        create_system_notification(
            student.id,
            "Your call is ready!",
            f"Join your {call.call_type.replace('_', ' ')} with {coach.first_name}",
            'call_ready'
        )
        
        create_system_notification(
            coach.id,
            "Call ready to start",
            f"Join your {call.call_type.replace('_', ' ')} with {student.first_name}",
            'call_ready'
        )
        
    except Exception as e:
        logger.error(f"Error sending call ready notifications: {e}")

def send_in_app_call_notifications(call, notification_type):
    """
    Send in-app notifications for call events
    """
    try:
        student = User.query.get(call.student_id)
        coach = User.query.get(call.coach_id)
        
        if notification_type == 'scheduled':
            # Notify both parties about scheduled call
            create_system_notification(
                student.id,
                "Call Scheduled",
                f"Your {call.call_type.replace('_', ' ')} with {coach.first_name} has been scheduled",
                'call_scheduled'
            )
            
            create_system_notification(
                coach.id,
                "Call Scheduled",
                f"Your {call.call_type.replace('_', ' ')} with {student.first_name} has been scheduled",
                'call_scheduled'
            )
            
    except Exception as e:
        logger.error(f"Error sending in-app call notifications: {e}")



def check_call_availability(coach_id, scheduled_date, scheduled_time, timezone_name, duration_minutes=15):
    """
    Check if coach is available at the specified time
    """
    try:
        # Convert to UTC
        user_tz = pytz.timezone(timezone_name)
        local_dt = user_tz.localize(datetime.combine(scheduled_date, scheduled_time))
        utc_dt = local_dt.astimezone(pytz.UTC)
        
        # Check for conflicts
        end_time = utc_dt + timedelta(minutes=duration_minutes)
        
        # Get all scheduled calls for the coach that might conflict
        conflicting_calls = ScheduledCall.query.filter(
            ScheduledCall.coach_id == coach_id,
            ScheduledCall.status == 'scheduled'
        ).all()
        
        # Check for time overlaps
        for call in conflicting_calls:
            # Ensure call.scheduled_at is timezone-aware (assume UTC if naive)
            call_scheduled_at = call.scheduled_at
            if call_scheduled_at.tzinfo is None:
                call_scheduled_at = pytz.UTC.localize(call_scheduled_at)
            
            call_end_time = call_scheduled_at + timedelta(minutes=call.duration_minutes)
            
            # Check if there's an overlap
            if (utc_dt < call_end_time and end_time > call_scheduled_at):
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking call availability: {e}")
        return False

def get_upcoming_calls(user_id, limit=10):
    """
    Get upcoming calls for a user
    """
    try:
        # Use a timezone-naive datetime for comparison since database stores naive datetimes
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        
        calls = ScheduledCall.query.filter(
            ScheduledCall.student_id == user_id,
            ScheduledCall.status == 'scheduled',
            ScheduledCall.scheduled_at > now_utc
        ).order_by(ScheduledCall.scheduled_at).limit(limit).all()
        
        return calls
        
    except Exception as e:
        logger.error(f"Error getting upcoming calls: {e}")
        return []

def get_coach_upcoming_calls(coach_id, limit=10):
    """
    Get upcoming calls for a coach
    """
    try:
        # Use a timezone-naive datetime for comparison since database stores naive datetimes
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        
        calls = ScheduledCall.query.filter(
            ScheduledCall.coach_id == coach_id,
            ScheduledCall.status == 'scheduled',
            ScheduledCall.scheduled_at > now_utc
        ).order_by(ScheduledCall.scheduled_at).limit(limit).all()
        
        return calls
        
    except Exception as e:
        logger.error(f"Error getting coach upcoming calls: {e}")
        return []
