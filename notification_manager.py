"""
Advanced Notification Manager for Phase 5A
Handles smart reminders, professional email templates, and multi-channel notifications
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from models import Session, ScheduledCall, User, db
from email_utils import send_email
from timezone_utils import convert_to_user_timezone, format_datetime_for_user

logger = logging.getLogger(__name__)

class NotificationManager:
    """Manages advanced notifications with smart timing and professional templates"""
    
    def __init__(self):
        self.notification_templates = {
            'session_reminder': {
                'subject': 'Reminder: Your session starts in {time_until}',
                'template': 'notifications/session_reminder.html'
            },
            'session_confirmation': {
                'subject': 'Session Confirmed: {session_title}',
                'template': 'notifications/session_confirmation.html'
            },
            'session_cancelled': {
                'subject': 'Session Cancelled: {session_title}',
                'template': 'notifications/session_cancelled.html'
            },
            'session_rescheduled': {
                'subject': 'Session Rescheduled: {session_title}',
                'template': 'notifications/session_rescheduled.html'
            }
        }
    
    def get_notifications_to_send(self) -> List[Dict[str, Any]]:
        """Get all notifications that need to be sent"""
        try:
            notifications = []
            now = datetime.utcnow()
            
            # Get upcoming sessions that need reminders
            upcoming_sessions = Session.query.filter(
                Session.status == 'scheduled',
                Session.scheduled_at > now,
                Session.scheduled_at <= now + timedelta(days=7),
                Session.reminder_sent == False
            ).all()
            
            for session in upcoming_sessions:
                # Check if it's time to send reminder
                time_until = session.scheduled_at - now
                
                # Send reminder 24 hours before
                if timedelta(hours=23) <= time_until <= timedelta(hours=25):
                    notifications.append({
                        'type': 'session_reminder_24h',
                        'session': session,
                        'time_until': '24 hours'
                    })
                
                # Send reminder 1 hour before
                elif timedelta(minutes=55) <= time_until <= timedelta(minutes=65):
                    notifications.append({
                        'type': 'session_reminder_1h',
                        'session': session,
                        'time_until': '1 hour'
                    })
                
                # Send reminder 15 minutes before
                elif timedelta(minutes=10) <= time_until <= timedelta(minutes=20):
                    notifications.append({
                        'type': 'session_reminder_15m',
                        'session': session,
                        'time_until': '15 minutes'
                    })
            
            # Get scheduled calls that need reminders
            upcoming_calls = ScheduledCall.query.filter(
                ScheduledCall.status == 'scheduled',
                ScheduledCall.scheduled_at > now,
                ScheduledCall.scheduled_at <= now + timedelta(days=7),
                ScheduledCall.reminder_sent == False
            ).all()
            
            for call in upcoming_calls:
                time_until = call.scheduled_at - now
                
                # Send reminder 1 hour before
                if timedelta(minutes=55) <= time_until <= timedelta(minutes=65):
                    notifications.append({
                        'type': 'call_reminder_1h',
                        'call': call,
                        'time_until': '1 hour'
                    })
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error getting notifications to send: {e}")
            return []
    
    def send_notification(self, notification_data: Dict[str, Any]) -> bool:
        """Send a specific notification"""
        try:
            notification_type = notification_data['type']
            
            if 'session' in notification_type:
                session = notification_data['session']
                time_until = notification_data['time_until']
                
                # Send to student
                if session.proposal and session.proposal.student:
                    self._send_session_reminder_to_user(
                        session, session.proposal.student.user, time_until
                    )
                
                # Send to coach
                if session.proposal and session.proposal.coach:
                    self._send_session_reminder_to_user(
                        session, session.proposal.coach.user, time_until
                    )
                
                # Mark reminder as sent
                session.reminder_sent = True
                db.session.commit()
                
            elif 'call' in notification_type:
                call = notification_data['call']
                time_until = notification_data['time_until']
                
                # Send to student
                if call.student:
                    self._send_call_reminder_to_user(
                        call, call.student.user, time_until
                    )
                
                # Send to coach
                if call.coach:
                    self._send_call_reminder_to_user(
                        call, call.coach.user, time_until
                    )
                
                # Mark reminder as sent
                call.reminder_sent = True
                db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    def send_session_confirmation(self, session: Session) -> bool:
        """Send session confirmation email"""
        try:
            if not session.proposal:
                return False
            
            # Send to student
            if session.proposal.student:
                self._send_session_confirmation_to_user(session, session.proposal.student.user)
            
            # Send to coach
            if session.proposal.coach:
                self._send_session_confirmation_to_user(session, session.proposal.coach.user)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending session confirmation: {e}")
            return False
    
    def send_session_cancellation(self, session: Session, reason: str = None) -> bool:
        """Send session cancellation email"""
        try:
            if not session.proposal:
                return False
            
            # Send to student
            if session.proposal.student:
                self._send_session_cancellation_to_user(session, session.proposal.student.user, reason)
            
            # Send to coach
            if session.proposal.coach:
                self._send_session_cancellation_to_user(session, session.proposal.coach.user, reason)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending session cancellation: {e}")
            return False
    
    def _send_session_reminder_to_user(self, session: Session, user: User, time_until: str) -> bool:
        """Send session reminder to a specific user"""
        try:
            # Get session details
            session_title = session.proposal.learning_request.title if session.proposal else 'Session'
            session_time = format_datetime_for_user(session.scheduled_at, user.timezone or 'UTC')
            
            # Prepare email data
            email_data = {
                'user_name': user.first_name,
                'session_title': session_title,
                'session_time': session_time,
                'time_until': time_until,
                'session_duration': session.duration_minutes or 60,
                'join_url': f"/sessions/{session.id}/join",
                'reschedule_url': f"/sessions/{session.id}/reschedule"
            }
            
            # Send email
            subject = f"Reminder: Your session starts in {time_until}"
            return send_email(
                to_email=user.email,
                subject=subject,
                template='notifications/session_reminder.html',
                data=email_data
            )
            
        except Exception as e:
            logger.error(f"Error sending session reminder to user: {e}")
            return False
    
    def _send_call_reminder_to_user(self, call: ScheduledCall, user: User, time_until: str) -> bool:
        """Send call reminder to a specific user"""
        try:
            # Get call details
            call_time = format_datetime_for_user(call.scheduled_at, user.timezone or 'UTC')
            
            # Prepare email data
            email_data = {
                'user_name': user.first_name,
                'call_time': call_time,
                'time_until': time_until,
                'call_duration': call.duration_minutes or 60,
                'join_url': f"/calls/{call.id}/join"
            }
            
            # Send email
            subject = f"Reminder: Your call starts in {time_until}"
            return send_email(
                to_email=user.email,
                subject=subject,
                template='notifications/call_reminder.html',
                data=email_data
            )
            
        except Exception as e:
            logger.error(f"Error sending call reminder to user: {e}")
            return False
    
    def _send_session_confirmation_to_user(self, session: Session, user: User) -> bool:
        """Send session confirmation to a specific user"""
        try:
            # Get session details
            session_title = session.proposal.learning_request.title if session.proposal else 'Session'
            session_time = format_datetime_for_user(session.scheduled_at, user.timezone or 'UTC')
            
            # Prepare email data
            email_data = {
                'user_name': user.first_name,
                'session_title': session_title,
                'session_time': session_time,
                'session_duration': session.duration_minutes or 60,
                'join_url': f"/sessions/{session.id}/join"
            }
            
            # Send email
            subject = f"Session Confirmed: {session_title}"
            return send_email(
                to_email=user.email,
                subject=subject,
                template='notifications/session_confirmation.html',
                data=email_data
            )
            
        except Exception as e:
            logger.error(f"Error sending session confirmation to user: {e}")
            return False
    
    def _send_session_cancellation_to_user(self, session: Session, user: User, reason: str = None) -> bool:
        """Send session cancellation to a specific user"""
        try:
            # Get session details
            session_title = session.proposal.learning_request.title if session.proposal else 'Session'
            session_time = format_datetime_for_user(session.scheduled_at, user.timezone or 'UTC')
            
            # Prepare email data
            email_data = {
                'user_name': user.first_name,
                'session_title': session_title,
                'session_time': session_time,
                'reason': reason or 'No reason provided',
                'reschedule_url': f"/sessions/{session.id}/reschedule"
            }
            
            # Send email
            subject = f"Session Cancelled: {session_title}"
            return send_email(
                to_email=user.email,
                subject=subject,
                template='notifications/session_cancelled.html',
                data=email_data
            )
            
        except Exception as e:
            logger.error(f"Error sending session cancellation to user: {e}")
            return False

# Global notification manager instance
notification_manager = NotificationManager()

def get_notification_manager() -> NotificationManager:
    """Get the global notification manager instance"""
    return notification_manager

def send_pending_notifications() -> int:
    """Send all pending notifications and return count sent"""
    try:
        manager = get_notification_manager()
        notifications = manager.get_notifications_to_send()
        
        sent_count = 0
        for notification in notifications:
            if manager.send_notification(notification):
                sent_count += 1
        
        logger.info(f"Sent {sent_count} notifications")
        return sent_count
        
    except Exception as e:
        logger.error(f"Error sending pending notifications: {e}")
        return 0

def send_session_confirmation(session_id: int) -> bool:
    """Send confirmation for a specific session"""
    try:
        session = Session.query.get(session_id)
        if not session:
            return False
        
        manager = get_notification_manager()
        return manager.send_session_confirmation(session)
        
    except Exception as e:
        logger.error(f"Error sending session confirmation: {e}")
        return False

def send_session_cancellation(session_id: int, reason: str = None) -> bool:
    """Send cancellation for a specific session"""
    try:
        session = Session.query.get(session_id)
        if not session:
            return False
        
        manager = get_notification_manager()
        return manager.send_session_cancellation(session, reason)
        
    except Exception as e:
        logger.error(f"Error sending session cancellation: {e}")
        return False
