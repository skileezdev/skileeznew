# Meeting Link Button Fix

## Problem Description

The user reported that after setting up a meeting and pressing the "Save Meeting Link" button, the sessions list still showed "Setup Meeting" instead of "Join Meeting". Additionally, students still saw "Meeting Setup Pending" even though the meeting was set up.

## Root Cause Analysis

The issue was caused by a **data model mismatch**:

1. **`Session` model** - Used by the `sessions_list` route to display session information
2. **`ScheduledSession` model** - Used by the `save_meeting_link` route to store meeting link data

When a coach saved a meeting link, it was stored in the `ScheduledSession` model, but the sessions list was reading from the `Session` model, which didn't have access to the meeting link information.

## Solution Implemented

### 1. Updated Template Logic

Modified the templates to check for meeting links through the contract relationship instead of directly on the session object:

**Before:**
```html
{% if session.google_meet_url %}
    <!-- Show Join Meeting button -->
{% else %}
    <!-- Show Setup Meeting or Pending -->
{% endif %}
```

**After:**
```html
{% set contract = session.get_contract() %}
{% set has_meeting_link = false %}
{% if contract %}
    {% set scheduled_session = contract.get_scheduled_session(session.session_number) %}
    {% if scheduled_session and scheduled_session.google_meet_url %}
        {% set has_meeting_link = true %}
    {% endif %}
{% endif %}

{% if has_meeting_link %}
    <!-- Show Join Meeting button -->
{% else %}
    <!-- Show Setup Meeting or Pending -->
{% endif %}
```

### 2. Added Contract Method

Added a `get_scheduled_session()` method to the `Contract` model to retrieve the corresponding `ScheduledSession`:

```python
def get_scheduled_session(self, session_number):
    """Get the ScheduledSession for a specific session number"""
    from models import ScheduledSession
    return ScheduledSession.query.filter_by(
        session_id=self.proposal.sessions.filter_by(session_number=session_number).first().id
    ).first() if self.proposal else None
```

### 3. Updated Redirect

Changed the `save_meeting_link` route to redirect back to the sessions list instead of the meeting setup page, so users can immediately see the updated button state:

**Before:**
```python
return redirect(url_for('meeting_setup', session_id=session_id))
```

**After:**
```python
return redirect(url_for('sessions_list'))
```

## Files Modified

1. **`templates/sessions/sessions_list_enhanced.html`** - Updated button logic
2. **`templates/sessions/join_session.html`** - Updated button logic  
3. **`models.py`** - Added `get_scheduled_session` method to Contract class
4. **`routes.py`** - Updated redirect in `save_meeting_link` route

## How It Works Now

1. **Coach sets up meeting** → Meeting link is saved to `ScheduledSession` model
2. **Template checks for meeting link** → Uses `contract.get_scheduled_session()` to find the `ScheduledSession`
3. **Button state updates** → Shows "Join Meeting" if link exists, "Setup Meeting" if coach, "Pending" if student
4. **User is redirected** → Back to sessions list to see the updated button state

## Testing

Created `test_meeting_link_fix.py` to verify:
- Contract relationships work correctly
- `get_scheduled_session` method functions properly
- Meeting link data is accessible through the contract

## Result

✅ **Setup Meeting Button**: Only visible to coaches  
✅ **Button State Change**: Automatically changes from "Setup Meeting" to "Join Meeting" when meeting is set up  
✅ **Student View**: Shows "Join Meeting" button once meeting is set up  
✅ **Immediate Feedback**: Users see updated button state after saving meeting link  

The meeting link system now works correctly with proper button state management for both coaches and students.
