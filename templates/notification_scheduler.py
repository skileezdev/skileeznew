import os
import logging
import schedule
import time
from datetime import datetime, timedelta
from threading import Thread
from flask import current_app
from models import ScheduledCall, CallNotification, Session, Contract, db
from scheduling_utils import send_call_notifications
from email_utils import send_session_reminder_email

logger = logging.getLogger(__name__)

class NotificationScheduler:
    """Background scheduler for call notifications and session reminders"""
    
    def __init__(self, app=None):
        self.app = app
        self.running = False
        self.thread = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the scheduler with the Flask app"""
        self.app = app
        
        # Schedule jobs
        self.schedule_jobs()
        
        # Start the scheduler in a separate thread
        if not self.running:
            self.start()
    
    def schedule_jobs(self):
        """Schedule all notification jobs"""
        # Check for calls ready to join (every minute)
        schedule.every().minute.do(self.check_calls_ready)
        
        # Send 24-hour reminders (every hour)
        schedule.every().hour.do(self.send_24h_reminders)
        
        # Send 1-hour reminders (every 15 minutes)
        schedule.every(15).minutes.do(self.send_1h_reminders)
        
        # Send session reminders (every 15 minutes)
        schedule.every(15).minutes.do(self.send_session_reminders)
        
        # Clean up old notifications (daily at 2 AM)
        schedule.every().day.at("02:00").do(self.cleanup_old_notifications)
        
        # Mark overdue calls as missed (every 30 minutes)
        schedule.every(30).minutes.do(self.mark_overdue_calls)
    
    def start(self):
        """Start the scheduler in a background thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("Notification scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Notification scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in notification scheduler: {e}")
                time.sleep(60)  # Wait before retrying
    
    def check_calls_ready(self):
        """Check for calls that are ready to join (within 5 minutes)"""
        try:
            with self.app.app_context():
                # Check if required tables exist
                try:
                    # Simple check to see if ScheduledCall table exists
                    db.session.execute(db.text("SELECT 1 FROM scheduled_call LIMIT 1"))
                except Exception as e:
                    logger.warning(f"Database schema issue detected: {e}")
                    return  # Skip this job if tables don't exist yet
                
                now = datetime.utcnow()
                ready_window = now + timedelta(minutes=5)
                
                # Find calls that are ready to join
                ready_calls = ScheduledCall.query.filter(
                    ScheduledCall.status == 'scheduled',
                    ScheduledCall.scheduled_at <= ready_window,
                    ScheduledCall.scheduled_at > now
                ).all()
                
                notifications_sent = 0
                for call in ready_calls:
                    # Check if we already sent a ready notification
                    existing_notification = CallNotification.query.filter_by(
                        call_id=call.id,
                        notification_type='ready'
                    ).first()
                    
                    if not existing_notification:
                        logger.info(f"Sending ready notification for call {call.id}")
                        send_call_notifications(call, 'ready')
                        notifications_sent += 1
                
                return {
                    'calls_checked': len(ready_calls),
                    'notifications_sent': notifications_sent
                }
                
        except Exception as e:
            # Check if this is a missing column error
            if "auto_activated" in str(e) or "column" in str(e).lower():
                logger.warning(f"Database schema issue detected: {e}")
                logger.info("Skipping notification check until database is updated")
                return {'warning': 'Database schema needs update', 'calls_checked': 0, 'notifications_sent': 0}
            else:
                logger.error(f"Error checking calls ready: {e}")
                return {'error': str(e)}
    
    def send_24h_reminders(self):
        """Send 24-hour reminders for upcoming calls"""
        try:
            with self.app.app_context():
                # Check if required tables exist
                try:
                    db.session.execute(db.text("SELECT 1 FROM scheduled_call LIMIT 1"))
                except Exception as e:
                    logger.warning(f"Database schema issue detected: {e}")
                    return {'warning': 'Database schema needs update', 'calls_checked': 0, 'reminders_sent': 0}
                
                now = datetime.utcnow()
                reminder_window_start = now + timedelta(hours=24)
                reminder_window_end = now + timedelta(hours=25)
                
                # Find calls that need 24-hour reminders
                calls_for_reminder = ScheduledCall.query.filter(
                    ScheduledCall.status == 'scheduled',
                    ScheduledCall.scheduled_at >= reminder_window_start,
                    ScheduledCall.scheduled_at <= reminder_window_end
                ).all()
                
                reminders_sent = 0
                for call in calls_for_reminder:
                    # Check if we already sent a 24h reminder
                    existing_notification = CallNotification.query.filter_by(
                        call_id=call.id,
                        notification_type='reminder_24h'
                    ).first()
                    
                    if not existing_notification:
                        logger.info(f"Sending 24h reminder for call {call.id}")
                        send_call_notifications(call, 'reminder_24h')
                        reminders_sent += 1
                
                return {
                    'calls_checked': len(calls_for_reminder),
                    'reminders_sent': reminders_sent
                }
                
        except Exception as e:
            # Check if this is a missing column error
            if "auto_activated" in str(e) or "column" in str(e).lower():
                logger.warning(f"Database schema issue detected: {e}")
                logger.info("Skipping 24h reminder check until database is updated")
                return {'warning': 'Database schema needs update', 'calls_checked': 0, 'reminders_sent': 0}
            else:
                logger.error(f"Error sending 24h reminders: {e}")
                return {'error': str(e)}
    
    def send_1h_reminders(self):
        """Send 1-hour reminders for upcoming calls"""
        try:
            with self.app.app_context():
                # Check if required tables exist
                try:
                    db.session.execute(db.text("SELECT 1 FROM scheduled_call LIMIT 1"))
                except Exception as e:
                    logger.warning(f"Database schema issue detected: {e}")
                    return {'warning': 'Database schema needs update', 'calls_checked': 0, 'reminders_sent': 0}
                
                now = datetime.utcnow()
                reminder_window_start = now + timedelta(hours=1)
                reminder_window_end = now + timedelta(hours=1, minutes=15)
                
                # Find calls that need 1-hour reminders
                calls_for_reminder = ScheduledCall.query.filter(
                    ScheduledCall.status == 'scheduled',
                    ScheduledCall.scheduled_at >= reminder_window_start,
                    ScheduledCall.scheduled_at <= reminder_window_end
                ).all()
                
                reminders_sent = 0
                for call in calls_for_reminder:
                    # Check if we already sent a 1h reminder
                    existing_notification = CallNotification.query.filter_by(
                        call_id=call.id,
                        notification_type='reminder_1h'
                    ).first()
                    
                    if not existing_notification:
                        logger.info(f"Sending 1h reminder for call {call.id}")
                        send_call_notifications(call, 'reminder_1h')
                        reminders_sent += 1
                
                return {
                    'calls_checked': len(calls_for_reminder),
                    'reminders_sent': reminders_sent
                }
                
        except Exception as e:
            # Check if this is a missing column error
            if "auto_activated" in str(e) or "column" in str(e).lower():
                logger.warning(f"Database schema issue detected: {e}")
                logger.info("Skipping 1h reminder check until database is updated")
                return {'warning': 'Database schema needs update', 'calls_checked': 0, 'reminders_sent': 0}
            else:
                logger.error(f"Error sending 1h reminders: {e}")
                return {'error': str(e)}
    
    def send_session_reminders(self):
        """Send session reminders for upcoming sessions"""
        try:
            with self.app.app_context():
                # Check if required tables exist
                try:
                    db.session.execute(db.text("SELECT 1 FROM session LIMIT 1"))
                except Exception as e:
                    logger.warning(f"Database schema issue detected: {e}")
                    return {'warning': 'Database schema needs update', 'sessions_checked': 0, 'reminders_sent': 0}
                
                now = datetime.utcnow()
                reminder_window_start = now + timedelta(minutes=15) # 15 minutes before session
                reminder_window_end = now + timedelta(minutes=30) # 30 minutes before session
                
                # Find sessions that need reminders
                sessions_for_reminder = Session.query.filter(
                    Session.status == 'scheduled',
                    Session.scheduled_at >= reminder_window_start,
                    Session.scheduled_at <= reminder_window_end
                ).all()
                
                reminders_sent = 0
                for session in sessions_for_reminder:
                    # Check if we already sent a session reminder
                    existing_notification = CallNotification.query.filter_by(
                        call_id=session.id, # Assuming session ID is used for notification
                        notification_type='session_reminder'
                    ).first()
                    
                    if not existing_notification:
                        logger.info(f"Sending session reminder for session {session.id}")
                        send_session_reminder_email(session)
                        reminders_sent += 1
                
                return {
                    'sessions_checked': len(sessions_for_reminder),
                    'reminders_sent': reminders_sent
                }
                
        except Exception as e:
            # Check if this is a missing column error
            if "auto_activated" in str(e) or "column" in str(e).lower():
                logger.warning(f"Database schema issue detected: {e}")
                logger.info("Skipping session reminder check until database is updated")
                return {'warning': 'Database schema needs update', 'sessions_checked': 0, 'reminders_sent': 0}
            else:
                logger.error(f"Error sending session reminders: {e}")
                return {'error': str(e)}
    
    def mark_overdue_calls(self):
        """Mark calls that are overdue as missed"""
        try:
            with self.app.app_context():
                # Check if required tables exist
                try:
                    db.session.execute(db.text("SELECT 1 FROM scheduled_call LIMIT 1"))
                except Exception as e:
                    logger.warning(f"Database schema issue detected: {e}")
                    return {'warning': 'Database schema needs update', 'calls_checked': 0, 'calls_marked_missed': 0}
                
                now = datetime.utcnow()
                overdue_threshold = now - timedelta(minutes=15)  # 15 minutes after scheduled time
                
                # Find overdue calls
                overdue_calls = ScheduledCall.query.filter(
                    ScheduledCall.status == 'scheduled',
                    ScheduledCall.scheduled_at < overdue_threshold
                ).all()
                
                calls_marked = 0
                for call in overdue_calls:
                    logger.info(f"Marking call {call.id} as missed")
                    call.status = 'missed'
                    call.notes = f"Call missed - no participants joined within 15 minutes of scheduled time"
                    calls_marked += 1
                
                db.session.commit()
                
                return {
                    'calls_checked': len(overdue_calls),
                    'calls_marked_missed': calls_marked
                }
                
        except Exception as e:
            # Check if this is a missing column error
            if "auto_activated" in str(e) or "column" in str(e).lower():
                logger.warning(f"Database schema issue detected: {e}")
                logger.info("Skipping overdue call check until database is updated")
                return {'warning': 'Database schema needs update', 'calls_checked': 0, 'calls_marked_missed': 0}
            else:
                logger.error(f"Error marking overdue calls: {e}")
                return {'error': str(e)}
    
    def cleanup_old_notifications(self):
        """Clean up old notification records"""
        try:
            with self.app.app_context():
                # Check if required tables exist
                try:
                    db.session.execute(db.text("SELECT 1 FROM call_notification LIMIT 1"))
                except Exception as e:
                    logger.warning(f"Database schema issue detected: {e}")
                    return {'warning': 'Database schema needs update', 'notifications_deleted': 0}
                
                # Delete notifications older than 30 days
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                
                deleted_count = CallNotification.query.filter(
                    CallNotification.sent_at < cutoff_date
                ).delete()
                
                db.session.commit()
                logger.info(f"Cleaned up {deleted_count} old notifications")
                
                return {
                    'notifications_deleted': deleted_count
                }
                
        except Exception as e:
            logger.error(f"Error cleaning up old notifications: {e}")
            return {'error': str(e)}

# Global scheduler instance
notification_scheduler = NotificationScheduler()

def init_notification_scheduler(app):
    """Initialize the notification scheduler with the Flask app"""
    notification_scheduler.init_app(app)
    return notification_scheduler

# Standalone functions for webhook access
def check_calls_ready():
    """Standalone function to check for calls ready to join"""
    if notification_scheduler.app:
        return notification_scheduler.check_calls_ready()
    return {'error': 'Scheduler not initialized'}

def send_24h_reminders():
    """Standalone function to send 24-hour reminders"""
    if notification_scheduler.app:
        return notification_scheduler.send_24h_reminders()
    return {'error': 'Scheduler not initialized'}

def send_1h_reminders():
    """Standalone function to send 1-hour reminders"""
    if notification_scheduler.app:
        return notification_scheduler.send_1h_reminders()
    return {'error': 'Scheduler not initialized'}

def send_session_reminders():
    """Standalone function to send session reminders"""
    if notification_scheduler.app:
        return notification_scheduler.send_session_reminders()
    return {'error': 'Scheduler not initialized'}

def mark_overdue_calls():
    """Standalone function to mark overdue calls"""
    if notification_scheduler.app:
        return notification_scheduler.mark_overdue_calls()
    return {'error': 'Scheduler not initialized'}

def cleanup_old_notifications():
    """Standalone function to cleanup old notifications"""
    if notification_scheduler.app:
        return notification_scheduler.cleanup_old_notifications()
    return {'error': 'Scheduler not initialized'}
