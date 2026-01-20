import urllib.parse
from datetime import datetime, timedelta

def create_google_meet_url(title, start_time, duration_minutes):
    """Generate Google Meet creation URL with pre-filled details"""
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    # Format for Google Meet
    start_str = start_time.strftime('%Y%m%dT%H%M%S')
    end_str = end_time.strftime('%Y%m%dT%H%M%S')
    
    # Google Meet creation URL with pre-filled details
    meet_url = f"https://meet.google.com/new?title={urllib.parse.quote(title)}&start={start_str}&end={end_str}"
    
    return meet_url

def validate_google_meet_url(url):
    """Validate if a URL is a valid Google Meet link"""
    if not url:
        return False
    
    # Check if it's a Google Meet URL
    valid_patterns = [
        'meet.google.com',
        'hangouts.google.com',
        'meet.google.com/new'
    ]
    
    return any(pattern in url.lower() for pattern in valid_patterns)

def format_meeting_title(session_or_call):
    """Format meeting title for Google Meet - handles both Session and ScheduledCall objects"""
    try:
        # Check if it's a ScheduledCall object
        if hasattr(session_or_call, 'call_type'):
            if session_or_call.call_type == 'free_consultation':
                return f"Free Consultation - {session_or_call.coach.first_name} & {session_or_call.student.first_name}"
            else:
                return f"Coaching Session - {session_or_call.coach.first_name} & {session_or_call.student.first_name}"
        # Check if it's a Session object
        elif hasattr(session_or_call, 'session_type'):
            if session_or_call.session_type == 'consultation':
                return f"Free Consultation - {session_or_call.coach.first_name} & {session_or_call.student.first_name}"
            else:
                return f"Coaching Session - {session_or_call.coach.first_name} & {session_or_call.student.first_name}"
        # Fallback for unknown objects
        else:
            return f"Meeting - {getattr(session_or_call, 'coach', {}).get('first_name', 'Coach')} & {getattr(session_or_call, 'student', {}).get('first_name', 'Student')}"
    except Exception:
        # Fallback if any error occurs
        return "Coaching Session"

def get_meeting_reminder_text(session_or_call):
    """Generate reminder text for meetings - handles both Session and ScheduledCall objects"""
    try:
        if hasattr(session_or_call, 'call_type'):
            session_type = 'consultation' if session_or_call.call_type == 'free_consultation' else 'coaching'
            coach_name = session_or_call.coach.first_name
        elif hasattr(session_or_call, 'session_type'):
            session_type = session_or_call.session_type
            coach_name = session_or_call.coach.first_name
        else:
            session_type = 'coaching'
            coach_name = getattr(session_or_call, 'coach', {}).get('first_name', 'Coach')
        
        return f"Your {session_type} session with {coach_name} starts in 1 hour. Click the meeting link to join!"
    except Exception:
        return "Your coaching session starts in 1 hour. Click the meeting link to join!"
