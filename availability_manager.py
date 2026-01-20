"""
Availability Manager for preventing double-booking and managing coach schedules
Handles real-time availability checking, conflict detection, and scheduling patterns
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from models import Session, ScheduledCall, User, db
from timezone_utils import get_timezone_manager, convert_to_user_timezone

logger = logging.getLogger(__name__)

class AvailabilityManager:
    """Manages coach availability and prevents double-booking"""
    
    def __init__(self):
        self.timezone_manager = get_timezone_manager()
    
    def check_coach_availability(self, coach_id: int, start_time: datetime, 
                               end_time: datetime, exclude_session_id: int = None) -> Dict[str, Any]:
        """
        Check if a coach is available for a specific time slot
        
        Args:
            coach_id: ID of the coach
            start_time: Start time of the requested slot (UTC)
            end_time: End time of the requested slot (UTC)
            exclude_session_id: Session ID to exclude from conflict checking
            
        Returns:
            Dict with availability status and conflicts
        """
        try:
            # Get all sessions for this coach
            sessions = Session.query.join(Session.proposal).filter(
                Session.proposal.has(coach_id=coach_id),
                Session.status.in_(['scheduled', 'active']),
                Session.scheduled_at.isnot(None)
            ).all()
            
            # Get all scheduled calls for this coach
            calls = ScheduledCall.query.filter_by(
                coach_id=coach_id,
                status='scheduled'
            ).filter(
                ScheduledCall.scheduled_at.isnot(None)
            ).all()
            
            conflicts = []
            
            # Check session conflicts
            for session in sessions:
                if exclude_session_id and session.id == exclude_session_id:
                    continue
                    
                if self._times_overlap(start_time, end_time, session.scheduled_at, 
                                     session.scheduled_at + timedelta(minutes=session.duration_minutes or 60)):
                    conflicts.append({
                        'type': 'session',
                        'id': session.id,
                        'title': session.proposal.learning_request.title if session.proposal else 'Unknown Session',
                        'start_time': session.scheduled_at,
                        'end_time': session.scheduled_at + timedelta(minutes=session.duration_minutes or 60),
                        'duration': session.duration_minutes or 60
                    })
            
            # Check call conflicts
            for call in calls:
                if self._times_overlap(start_time, end_time, call.scheduled_at,
                                     call.scheduled_at + timedelta(minutes=call.duration_minutes or 60)):
                    conflicts.append({
                        'type': 'call',
                        'id': call.id,
                        'title': f'Scheduled Call with {call.student.user.first_name} {call.student.user.last_name}',
                        'start_time': call.scheduled_at,
                        'end_time': call.scheduled_at + timedelta(minutes=call.duration_minutes or 60),
                        'duration': call.duration_minutes or 60
                    })
            
            # Check if requested time is in the past
            if start_time < datetime.utcnow():
                return {
                    'available': False,
                    'reason': 'past_time',
                    'message': 'Cannot schedule meetings in the past',
                    'conflicts': conflicts
                }
            
            # Check if time slot is too far in the future (e.g., 1 year)
            if start_time > datetime.utcnow() + timedelta(days=365):
                return {
                    'available': False,
                    'reason': 'too_far_future',
                    'message': 'Cannot schedule meetings more than 1 year in advance',
                    'conflicts': conflicts
                }
            
            # Check for conflicts
            if conflicts:
                return {
                    'available': False,
                    'reason': 'conflicts',
                    'message': f'Coach has {len(conflicts)} conflicting appointment(s)',
                    'conflicts': conflicts
                }
            
            return {
                'available': True,
                'reason': 'available',
                'message': 'Time slot is available',
                'conflicts': []
            }
            
        except Exception as e:
            logger.error(f"Error checking coach availability: {e}")
            return {
                'available': False,
                'reason': 'error',
                'message': 'Error checking availability',
                'conflicts': []
            }
    
    def get_coach_availability_slots(self, coach_id: int, date: datetime, 
                                   duration_minutes: int = 60) -> List[Dict[str, Any]]:
        """
        Get available time slots for a coach on a specific date
        
        Args:
            coach_id: ID of the coach
            date: Date to check (UTC)
            duration_minutes: Duration of requested slot
            
        Returns:
            List of available time slots
        """
        try:
            # Get coach's working hours (you can extend this to be configurable)
            working_hours = self._get_coach_working_hours(coach_id)
            
            # Get all sessions and calls for this date
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            sessions = Session.query.join(Session.proposal).filter(
                Session.proposal.has(coach_id=coach_id),
                Session.status.in_(['scheduled', 'active']),
                Session.scheduled_at >= start_of_day,
                Session.scheduled_at < end_of_day
            ).all()
            
            calls = ScheduledCall.query.filter_by(
                coach_id=coach_id,
                status='scheduled'
            ).filter(
                ScheduledCall.scheduled_at >= start_of_day,
                ScheduledCall.scheduled_at < end_of_day
            ).all()
            
            # Combine all booked times
            booked_times = []
            
            for session in sessions:
                booked_times.append({
                    'start': session.scheduled_at,
                    'end': session.scheduled_at + timedelta(minutes=session.duration_minutes or 60)
                })
            
            for call in calls:
                booked_times.append({
                    'start': call.scheduled_at,
                    'end': call.scheduled_at + timedelta(minutes=call.duration_minutes or 60)
                })
            
            # Generate available slots
            available_slots = self._generate_available_slots(
                working_hours, booked_times, duration_minutes, date
            )
            
            return available_slots
            
        except Exception as e:
            logger.error(f"Error getting coach availability slots: {e}")
            return []
    
    def suggest_alternative_times(self, coach_id: int, requested_start: datetime,
                                requested_end: datetime, duration_minutes: int = 60) -> List[Dict[str, Any]]:
        """
        Suggest alternative times when requested slot is not available
        
        Args:
            coach_id: ID of the coach
            requested_start: Requested start time
            requested_end: Requested end time
            duration_minutes: Duration of meeting
            
        Returns:
            List of alternative time suggestions
        """
        try:
            suggestions = []
            
            # Check same day alternatives
            same_day_slots = self.get_coach_availability_slots(
                coach_id, requested_start.date(), duration_minutes
            )
            
            # Filter slots that are close to requested time
            for slot in same_day_slots:
                slot_start = slot['start_time']
                time_diff = abs((slot_start - requested_start).total_seconds() / 3600)  # hours
                
                if time_diff <= 4:  # Within 4 hours
                    suggestions.append({
                        'start_time': slot_start,
                        'end_time': slot_start + timedelta(minutes=duration_minutes),
                        'type': 'same_day',
                        'time_diff_hours': time_diff
                    })
            
            # Check next few days
            for days_ahead in [1, 2, 3, 7]:
                check_date = requested_start.date() + timedelta(days=days_ahead)
                future_slots = self.get_coach_availability_slots(
                    coach_id, check_date, duration_minutes
                )
                
                if future_slots:
                    # Take the first available slot of the day
                    suggestions.append({
                        'start_time': future_slots[0]['start_time'],
                        'end_time': future_slots[0]['start_time'] + timedelta(minutes=duration_minutes),
                        'type': f'{days_ahead}_days_ahead',
                        'days_ahead': days_ahead
                    })
                    break
            
            # Sort suggestions by preference (same day first, then by time difference)
            suggestions.sort(key=lambda x: (
                0 if x['type'] == 'same_day' else 1,
                x.get('time_diff_hours', 0)
            ))
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting alternative times: {e}")
            return []
    
    def _times_overlap(self, start1: datetime, end1: datetime, 
                      start2: datetime, end2: datetime) -> bool:
        """Check if two time ranges overlap"""
        return start1 < end2 and start2 < end1
    
    def _get_coach_working_hours(self, coach_id: int) -> Dict[str, Any]:
        """Get coach's working hours (default implementation)"""
        # You can extend this to be configurable per coach
        return {
            'monday': {'start': '09:00', 'end': '17:00'},
            'tuesday': {'start': '09:00', 'end': '17:00'},
            'wednesday': {'start': '09:00', 'end': '17:00'},
            'thursday': {'start': '09:00', 'end': '17:00'},
            'friday': {'start': '09:00', 'end': '17:00'},
            'saturday': {'start': '10:00', 'end': '15:00'},
            'sunday': {'start': '10:00', 'end': '15:00'}
        }
    
    def _generate_available_slots(self, working_hours: Dict[str, Any], 
                                booked_times: List[Dict[str, datetime]], 
                                duration_minutes: int, date: datetime) -> List[Dict[str, Any]]:
        """Generate available time slots based on working hours and booked times"""
        try:
            day_name = date.strftime('%A').lower()
            day_hours = working_hours.get(day_name)
            
            if not day_hours:
                return []  # Coach doesn't work on this day
            
            # Parse working hours
            start_hour, start_minute = map(int, day_hours['start'].split(':'))
            end_hour, end_minute = map(int, day_hours['end'].split(':'))
            
            # Create working hours range
            work_start = date.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            work_end = date.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
            
            # Generate slots every 30 minutes
            slot_interval = 30  # minutes
            available_slots = []
            
            current_slot = work_start
            while current_slot + timedelta(minutes=duration_minutes) <= work_end:
                slot_end = current_slot + timedelta(minutes=duration_minutes)
                
                # Check if this slot conflicts with any booked time
                slot_conflicts = False
                for booked in booked_times:
                    if self._times_overlap(current_slot, slot_end, booked['start'], booked['end']):
                        slot_conflicts = True
                        break
                
                if not slot_conflicts:
                    available_slots.append({
                        'start_time': current_slot,
                        'end_time': slot_end,
                        'duration_minutes': duration_minutes,
                        'available': True
                    })
                
                current_slot += timedelta(minutes=slot_interval)
            
            return available_slots
            
        except Exception as e:
            logger.error(f"Error generating available slots: {e}")
            return []

# Global availability manager instance
availability_manager = AvailabilityManager()

def get_availability_manager() -> AvailabilityManager:
    """Get the global availability manager instance"""
    return availability_manager

def check_coach_availability(coach_id: int, start_time: datetime, 
                           end_time: datetime, exclude_session_id: int = None) -> Dict[str, Any]:
    """Check if a coach is available for a specific time slot"""
    return availability_manager.check_coach_availability(coach_id, start_time, end_time, exclude_session_id)

def get_coach_availability_slots(coach_id: int, date: datetime, 
                               duration_minutes: int = 60) -> List[Dict[str, Any]]:
    """Get available time slots for a coach on a specific date"""
    return availability_manager.get_coach_availability_slots(coach_id, date, duration_minutes)

def get_coach_calendar_days(coach_id: int, year: int, month: int) -> List[Dict[str, Any]]:
    """
    Get calendar days for a coach for a specific month
    
    Args:
        coach_id: ID of the coach
        year: Year to get calendar for
        month: Month to get calendar for (1-12)
        
    Returns:
        List of calendar days with availability information
    """
    try:
        import calendar
        from datetime import date
        
        # Get the calendar for the month
        cal = calendar.monthcalendar(year, month)
        today = date.today()
        
        calendar_days = []
        
        for week in cal:
            for day in week:
                if day == 0:  # Empty day
                    continue
                
                # Create date object
                day_date = date(year, month, day)
                
                # Check if this day is available
                day_dt = datetime.combine(day_date, datetime.min.time())
                available_slots = get_coach_availability_slots(coach_id, day_dt, 60)
                
                # Determine availability status
                is_available = len(available_slots) > 0
                is_today = day_date == today
                is_past = day_date < today
                
                # Build classes list
                classes = []
                if is_today:
                    classes.append('today')
                if is_available and not is_past:
                    classes.append('available')
                elif is_past or not is_available:
                    classes.append('unavailable')
                
                calendar_days.append({
                    'date': day_date.isoformat(),
                    'day_number': day,
                    'is_today': is_today,
                    'is_available': is_available and not is_past,
                    'is_past': is_past,
                    'available_slots': len(available_slots),
                    'classes': classes
                })
        
        return calendar_days
        
    except Exception as e:
        logger.error(f"Error getting coach calendar days: {e}")
        return []

def suggest_alternative_times(coach_id: int, requested_start: datetime,
                            requested_end: datetime, duration_minutes: int = 60) -> List[Dict[str, Any]]:
    """Suggest alternative times when requested slot is not available"""
    return availability_manager.suggest_alternative_times(coach_id, requested_start, requested_end, duration_minutes)
