"""
Meeting activation utilities for Calendly-like functionality
Handles automatic meeting activation, reminders, and lifecycle management
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from models import Session, ScheduledCall, User, db
from timezone_utils import get_timezone_manager, format_datetime_for_user
from email_utils import send_email
from notification_utils import create_system_notification

logger = logging.getLogger(__name__)

class MeetingActivationManager:
    """Manages automatic meeting activation and lifecycle"""
    
    def __init__(self):
        self.timezone_manager = get_timezone_manager()
    
    def get_meetings_to_activate(self) -> List[Dict[str, Any]]:
        """Get all meetings that should be auto-activated now"""
        meetings = []
        
        # Check Sessions
        sessions = Session.query.filter_by(
            status='scheduled',
            auto_activated=False
        ).filter(
            Session.scheduled_at.isnot(None)
        ).all()
        
        for session in sessions:
            if session.can_auto_activate():
                meetings.append({
                    'type': 'session',
                    'id': session.id,
                    'object': session,
                    'scheduled_at': session.scheduled_at,
                    'participants': self._get_session_participants(session)
                })
        
        # Check ScheduledCalls
        calls = ScheduledCall.query.filter_by(
            status='scheduled',
            auto_activated=False
        ).filter(
            ScheduledCall.scheduled_at.isnot(None)
        ).all()
        
        for call in calls:
            if call.can_auto_activate():
                meetings.append({
                    'type': 'call',
                    'id': call.id,
                    'object': call,
                    'scheduled_at': call.scheduled_at,
                    'participants': self._get_call_participants(call)
                })
        
        return meetings
    
    def get_meetings_for_reminders(self) -> List[Dict[str, Any]]:
        """Get all meetings that should receive reminders now"""
        meetings = []
        
        # Check Sessions
        sessions = Session.query.filter_by(
            status='scheduled',
            reminder_sent=False
        ).filter(
            Session.scheduled_at.isnot(None)
        ).all()
        
        for session in sessions:
            if session.should_send_reminder():
                meetings.append({
                    'type': 'session',
                    'id': session.id,
                    'object': session,
                    'scheduled_at': session.scheduled_at,
                    'participants': self._get_session_participants(session)
                })
        
        # Check ScheduledCalls
        calls = ScheduledCall.query.filter_by(
            status='scheduled',
            reminder_sent=False
        ).filter(
            ScheduledCall.scheduled_at.isnot(None)
        ).all()
        
        for call in calls:
            if call.should_send_reminder():
                meetings.append({
                    'type': 'call',
                    'id': call.id,
                    'object': call,
                    'scheduled_at': call.scheduled_at,
                    'participants': self._get_call_participants(call)
                })
        
        return meetings
    
    def get_meetings_for_early_join(self) -> List[Dict[str, Any]]:
        """Get all meetings that allow early join now"""
        meetings = []
        
        # Check Sessions
        sessions = Session.query.filter_by(status='scheduled').filter(
            Session.scheduled_at.isnot(None)
        ).all()
        
        for session in sessions:
            if session.can_join_early():
                meetings.append({
                    'type': 'session',
                    'id': session.id,
                    'object': session,
                    'scheduled_at': session.scheduled_at,
                    'participants': self._get_session_participants(session)
                })
        
        # Check ScheduledCalls
        calls = ScheduledCall.query.filter_by(status='scheduled').filter(
            ScheduledCall.scheduled_at.isnot(None)
        ).all()
        
        for call in calls:
            if call.can_join_early():
                meetings.append({
                    'type': 'call',
                    'id': call.id,
                    'object': call,
                    'scheduled_at': call.scheduled_at,
                    'participants': self._get_call_participants(call)
                })
        
        return meetings
    
    def activate_meeting(self, meeting_data: Dict[str, Any]) -> bool:
        """Activate a specific meeting"""
        try:
            meeting_obj = meeting_data['object']
            meeting_type = meeting_data['type']
            
            # Auto-activate the meeting
            if meeting_type == 'session':
                success = meeting_obj.auto_activate_meeting()
            else:  # call
                success = meeting_obj.auto_activate_meeting()
            
            if success:
                # Send notifications to participants
                self._send_meeting_activated_notifications(meeting_data)
                logger.info(f"Successfully activated {meeting_type} {meeting_obj.id}")
                return True
            else:
                logger.warning(f"Failed to activate {meeting_type} {meeting_obj.id}")
                return False
                
        except Exception as e:
            logger.error(f"Error activating meeting: {e}")
            return False
    
    def send_reminder(self, meeting_data: Dict[str, Any]) -> bool:
        """Send reminder for a specific meeting"""
        try:
            meeting_obj = meeting_data['object']
            meeting_type = meeting_data['type']
            participants = meeting_data['participants']
            
            # Send reminder emails
            for participant in participants:
                self._send_reminder_email(participant, meeting_data)
                self._send_reminder_notification(participant, meeting_data)
            
            # Mark reminder as sent
            meeting_obj.mark_reminder_sent()
            
            logger.info(f"Successfully sent reminder for {meeting_type} {meeting_obj.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
            return False
    
    def _get_session_participants(self, session: Session) -> List[Dict[str, Any]]:
        """Get participants for a session"""
        participants = []
        
        try:
            contract = session.get_contract()
            if contract:
                # Add coach
                coach_user = User.query.get(contract.coach_id)
                if coach_user:
                    participants.append({
                        'user': coach_user,
                        'role': 'coach',
                        'timezone': coach_user.timezone or 'UTC'
                    })
                
                # Add student
                student_user = User.query.get(contract.student_id)
                if student_user:
                    participants.append({
                        'user': student_user,
                        'role': 'student',
                        'timezone': student_user.timezone or 'UTC'
                    })
        except Exception as e:
            logger.error(f"Error getting session participants: {e}")
        
        return participants
    
    def _get_call_participants(self, call: ScheduledCall) -> List[Dict[str, Any]]:
        """Get participants for a scheduled call"""
        participants = []
        
        try:
            # Add coach
            coach_user = User.query.get(call.coach_id)
            if coach_user:
                participants.append({
                    'user': coach_user,
                    'role': 'coach',
                    'timezone': coach_user.timezone or 'UTC'
                })
            
            # Add student
            student_user = User.query.get(call.student_id)
            if student_user:
                participants.append({
                    'user': student_user,
                    'role': 'student',
                    'timezone': student_user.timezone or 'UTC'
                })
        except Exception as e:
            logger.error(f"Error getting call participants: {e}")
        
        return participants
    
    def _send_meeting_activated_notifications(self, meeting_data: Dict[str, Any]):
        """Send notifications when meeting is activated"""
        meeting_obj = meeting_data['object']
        meeting_type = meeting_data['type']
        participants = meeting_data['participants']
        
        for participant in participants:
            user = participant['user']
            role = participant['role']
            
            # Create in-app notification
            notification_title = f"Meeting Started - {meeting_type.title()}"
            notification_message = f"Your {meeting_type} has started. Click to join."
            
            create_system_notification(
                user_id=user.id,
                title=notification_title,
                message=notification_message,
                notification_type='meeting_started',
                related_id=meeting_obj.id,
                related_type=meeting_type
            )
            
            # Send email notification
            try:
                meeting_time = format_datetime_for_user(
                    meeting_obj.scheduled_at, 
                    participant['timezone']
                )
                
                subject = f"Your {meeting_type.title()} Has Started"
                body = f"""
                Hello {user.first_name},
                
                Your {meeting_type} has started. Please join the meeting now.
                
                Meeting Details:
                - Time: {meeting_time}
                - Duration: {getattr(meeting_obj, 'duration_minutes', 60)} minutes
                
                Click here to join: [Meeting Link]
                
                Best regards,
                Skileez Team
                """
                
                send_email(user.email, subject, body)
                
            except Exception as e:
                logger.error(f"Error sending meeting activated email: {e}")
    
    def _send_reminder_email(self, participant: Dict[str, Any], meeting_data: Dict[str, Any]):
        """Send reminder email to participant"""
        try:
            user = participant['user']
            meeting_obj = meeting_data['object']
            meeting_type = meeting_data['type']
            
            meeting_time = format_datetime_for_user(
                meeting_obj.scheduled_at, 
                participant['timezone']
            )
            
            subject = f"Reminder: Your {meeting_type.title()} in 15 minutes"
            body = f"""
            Hello {user.first_name},
            
            This is a reminder that your {meeting_type} starts in 15 minutes.
            
            Meeting Details:
            - Time: {meeting_time}
            - Duration: {getattr(meeting_obj, 'duration_minutes', 60)} minutes
            
            Please ensure you have:
            - A stable internet connection
            - Your camera and microphone ready
            - A quiet environment for the meeting
            
            Click here to join: [Meeting Link]
            
            Best regards,
            Skileez Team
            """
            
            send_email(user.email, subject, body)
            
        except Exception as e:
            logger.error(f"Error sending reminder email: {e}")
    
    def _send_reminder_notification(self, participant: Dict[str, Any], meeting_data: Dict[str, Any]):
        """Send reminder notification to participant"""
        try:
            user = participant['user']
            meeting_obj = meeting_data['object']
            meeting_type = meeting_data['type']
            
            notification_title = f"Meeting Reminder - {meeting_type.title()}"
            notification_message = f"Your {meeting_type} starts in 15 minutes. Get ready to join!"
            
            create_system_notification(
                user_id=user.id,
                title=notification_title,
                message=notification_message,
                notification_type='meeting_reminder',
                related_id=meeting_obj.id,
                related_type=meeting_type
            )
            
        except Exception as e:
            logger.error(f"Error sending reminder notification: {e}")

# Global meeting activation manager instance
meeting_activation_manager = MeetingActivationManager()

def get_meeting_activation_manager() -> MeetingActivationManager:
    """Get the global meeting activation manager instance"""
    return meeting_activation_manager

def activate_pending_meetings():
    """Activate all meetings that should be activated now"""
    manager = get_meeting_activation_manager()
    meetings = manager.get_meetings_to_activate()
    
    activated_count = 0
    for meeting in meetings:
        if manager.activate_meeting(meeting):
            activated_count += 1
    
    logger.info(f"Activated {activated_count} meetings")
    return activated_count

def send_pending_reminders():
    """Send reminders for all meetings that need them now"""
    manager = get_meeting_activation_manager()
    meetings = manager.get_meetings_for_reminders()
    
    reminder_count = 0
    for meeting in meetings:
        if manager.send_reminder(meeting):
            reminder_count += 1
    
    logger.info(f"Sent {reminder_count} reminders")
    return reminder_count
