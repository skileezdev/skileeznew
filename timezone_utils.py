"""
Enhanced timezone utilities for Calendly-like functionality
Handles timezone conversion, DST, and user timezone preferences
"""

import pytz
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class TimezoneManager:
    """Manages timezone conversions and user timezone preferences"""
    
    def __init__(self):
        self.common_timezones = {
            'UTC': 'UTC',
            'EST': 'America/New_York',
            'EDT': 'America/New_York',
            'CST': 'America/Chicago',
            'CDT': 'America/Chicago',
            'MST': 'America/Denver',
            'MDT': 'America/Denver',
            'PST': 'America/Los_Angeles',
            'PDT': 'America/Los_Angeles',
            'GMT': 'Europe/London',
            'BST': 'Europe/London',
            'CET': 'Europe/Paris',
            'CEST': 'Europe/Paris',
            'JST': 'Asia/Tokyo',
            'IST': 'Asia/Kolkata',
            'AEST': 'Australia/Sydney',
            'AEDT': 'Australia/Sydney'
        }
    
    def get_timezone_object(self, timezone_name: str) -> Optional[pytz.timezone]:
        """Get timezone object from timezone name"""
        try:
            # Handle common abbreviations
            if timezone_name in self.common_timezones:
                timezone_name = self.common_timezones[timezone_name]
            
            return pytz.timezone(timezone_name)
        except Exception as e:
            logger.error(f"Invalid timezone: {timezone_name}, error: {e}")
            return None
    
    def convert_datetime(self, dt: datetime, from_tz: str, to_tz: str) -> Optional[datetime]:
        """Convert datetime from one timezone to another"""
        try:
            from_tz_obj = self.get_timezone_object(from_tz)
            to_tz_obj = self.get_timezone_object(to_tz)
            
            if not from_tz_obj or not to_tz_obj:
                return None
            
            # If datetime is naive, assume it's in from_tz
            if dt.tzinfo is None:
                dt = from_tz_obj.localize(dt)
            
            # Convert to target timezone
            converted_dt = dt.astimezone(to_tz_obj)
            return converted_dt
            
        except Exception as e:
            logger.error(f"Error converting datetime: {e}")
            return None
    
    def convert_to_user_timezone(self, dt: datetime, user_timezone: str) -> Optional[datetime]:
        """Convert UTC datetime to user's timezone"""
        if not dt:
            return None
        
        return self.convert_datetime(dt, 'UTC', user_timezone)
    
    def convert_from_user_timezone(self, dt: datetime, user_timezone: str) -> Optional[datetime]:
        """Convert datetime from user's timezone to UTC"""
        if not dt:
            return None
        
        return self.convert_datetime(dt, user_timezone, 'UTC')
    
    def format_datetime_for_timezone(self, dt: datetime, timezone_name: str, 
                                   format_str: str = "%B %d, %Y at %I:%M %p") -> str:
        """Format datetime for specific timezone with timezone indicator"""
        try:
            tz_obj = self.get_timezone_object(timezone_name)
            if not tz_obj:
                return dt.strftime(format_str)
            
            # Convert to target timezone
            if dt.tzinfo is None:
                dt = pytz.UTC.localize(dt)
            
            local_dt = dt.astimezone(tz_obj)
            
            # Get timezone abbreviation
            tz_abbr = local_dt.strftime('%Z')
            
            # Format with timezone
            formatted = local_dt.strftime(format_str)
            return f"{formatted} {tz_abbr}"
            
        except Exception as e:
            logger.error(f"Error formatting datetime: {e}")
            return dt.strftime(format_str)
    
    def get_timezone_offset(self, timezone_name: str) -> Optional[str]:
        """Get timezone offset string (e.g., '+05:30', '-08:00')"""
        try:
            tz_obj = self.get_timezone_object(timezone_name)
            if not tz_obj:
                return None
            
            now = datetime.now(tz_obj)
            offset = now.strftime('%z')
            
            # Format as +/-HH:MM
            if len(offset) == 5:
                return f"{offset[:3]}:{offset[3:]}"
            return offset
            
        except Exception as e:
            logger.error(f"Error getting timezone offset: {e}")
            return None
    
    def is_dst_active(self, timezone_name: str) -> bool:
        """Check if daylight saving time is active in the timezone"""
        try:
            tz_obj = self.get_timezone_object(timezone_name)
            if not tz_obj:
                return False
            
            now = datetime.now(tz_obj)
            return bool(now.dst())
            
        except Exception as e:
            logger.error(f"Error checking DST: {e}")
            return False
    
    def get_available_timezones(self) -> List[Dict[str, str]]:
        """Get list of available timezones with their offsets"""
        timezones = []
        
        for tz_name in pytz.all_timezones:
            try:
                tz_obj = pytz.timezone(tz_name)
                now = datetime.now(tz_obj)
                offset = now.strftime('%z')
                
                # Format offset
                if len(offset) == 5:
                    formatted_offset = f"{offset[:3]}:{offset[3:]}"
                else:
                    formatted_offset = offset
                
                # Get timezone name parts
                parts = tz_name.split('/')
                if len(parts) >= 2:
                    region = parts[0]
                    city = parts[-1].replace('_', ' ')
                else:
                    region = "Other"
                    city = tz_name
                
                timezones.append({
                    'name': tz_name,
                    'region': region,
                    'city': city,
                    'offset': formatted_offset,
                    'display': f"{city} ({formatted_offset})"
                })
                
            except Exception as e:
                logger.error(f"Error processing timezone {tz_name}: {e}")
                continue
        
        # Sort by offset
        timezones.sort(key=lambda x: x['offset'])
        return timezones
    
    def get_working_hours_in_timezone(self, working_hours_utc: Dict[str, Any], 
                                    user_timezone: str) -> Dict[str, Any]:
        """Convert working hours from UTC to user's timezone"""
        try:
            tz_obj = self.get_timezone_object(user_timezone)
            if not tz_obj:
                return working_hours_utc
            
            converted_hours = {}
            
            for day, hours in working_hours_utc.items():
                if isinstance(hours, dict) and 'start' in hours and 'end' in hours:
                    # Convert start time
                    start_utc = datetime.strptime(hours['start'], '%H:%M')
                    start_local = self.convert_datetime(start_utc, 'UTC', user_timezone)
                    
                    # Convert end time
                    end_utc = datetime.strptime(hours['end'], '%H:%M')
                    end_local = self.convert_datetime(end_utc, 'UTC', user_timezone)
                    
                    converted_hours[day] = {
                        'start': start_local.strftime('%H:%M') if start_local else hours['start'],
                        'end': end_local.strftime('%H:%M') if end_local else hours['end']
                    }
                else:
                    converted_hours[day] = hours
            
            return converted_hours
            
        except Exception as e:
            logger.error(f"Error converting working hours: {e}")
            return working_hours_utc
    
    def calculate_meeting_time_in_timezones(self, meeting_time_utc: datetime, 
                                          timezones: List[str]) -> Dict[str, str]:
        """Calculate meeting time in multiple timezones"""
        result = {}
        
        for tz in timezones:
            converted = self.convert_datetime(meeting_time_utc, 'UTC', tz)
            if converted:
                result[tz] = converted.strftime("%B %d, %Y at %I:%M %p %Z")
        
        return result

# Global timezone manager instance
timezone_manager = TimezoneManager()

def get_timezone_manager() -> TimezoneManager:
    """Get the global timezone manager instance"""
    return timezone_manager

def format_datetime_for_user(dt: datetime, user_timezone: str = 'UTC') -> str:
    """Format datetime for user's timezone"""
    return timezone_manager.format_datetime_for_timezone(dt, user_timezone)

def convert_to_user_timezone(dt: datetime, user_timezone: str) -> Optional[datetime]:
    """Convert UTC datetime to user's timezone"""
    return timezone_manager.convert_to_user_timezone(dt, user_timezone)

def convert_from_user_timezone(dt: datetime, user_timezone: str) -> Optional[datetime]:
    """Convert datetime from user's timezone to UTC"""
    return timezone_manager.convert_from_user_timezone(dt, user_timezone)

def get_common_timezones() -> List[str]:
    """Get list of common timezones for dropdown"""
    return [
        'UTC',
        'America/New_York',
        'America/Chicago',
        'America/Denver',
        'America/Los_Angeles',
        'Europe/London',
        'Europe/Paris',
        'Europe/Berlin',
        'Asia/Tokyo',
        'Asia/Shanghai',
        'Asia/Kolkata',
        'Australia/Sydney',
        'Pacific/Auckland'
    ]
