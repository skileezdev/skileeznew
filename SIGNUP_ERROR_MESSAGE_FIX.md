# Signup Error Message Fix

## Problem
When users visited the signup pages (for coaches or students), they immediately saw the error message "Please correct the errors below." even before filling out any form fields. This created a poor user experience.

## Root Cause
In the `routes.py` file, three signup routes had a logic error:

```python
if form.validate_on_submit():
    # handle successful submission
else:
    flash('Please correct the errors below.', 'error')

return render_template(...)
```

The issue: `form.validate_on_submit()` returns `False` on GET requests (initial page load), which caused the `else` block to execute and flash the error message even when the page was first loaded.

## Solution
Changed the logic to only show the error message when a POST request fails validation:

```python
if form.validate_on_submit():
    # handle successful submission
elif request.method == 'POST':
    # Only show error message if form was submitted (POST) but validation failed
    flash('Please correct the errors below.', 'error')

return render_template(...)
```

## Files Modified
- `routes.py`
  - Fixed `/signup` route (line 751-755)
  - Fixed `/signup/student` route (line 833-835)
  - Fixed `/signup/coach` route (line 908-910)

## Impact
- Error messages now only appear after the user actually submits the form with errors
- GET requests (initial page loads) no longer display premature error messages
- Better user experience for new user signups

## Testing
To test the fix:
1. Visit `/signup/student` or `/signup/coach`
2. Verify no error message appears on initial page load
3. Try submitting the form with invalid data
4. Verify error message "Please correct the errors below." now appears after submission

