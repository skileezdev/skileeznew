# MVP Contract System Form Extensions
# Enhanced forms for job posting, proposals, contracts, and scheduling

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, IntegerField, FloatField, 
    SelectField, DateField, DateTimeField, BooleanField, 
    FieldList, FormField, HiddenField
)
from wtforms.validators import DataRequired, Optional, NumberRange, Length, Email
from datetime import datetime, timedelta

# Timezone choices for forms
TIMEZONE_CHOICES = [
    ('UTC', 'UTC (Coordinated Universal Time)'),
    ('America/New_York', 'Eastern Time (ET)'),
    ('America/Chicago', 'Central Time (CT)'),
    ('America/Denver', 'Mountain Time (MT)'),
    ('America/Los_Angeles', 'Pacific Time (PT)'),
    ('Europe/London', 'London (GMT/BST)'),
    ('Europe/Paris', 'Paris (CET/CEST)'),
    ('Asia/Tokyo', 'Tokyo (JST)'),
    ('Asia/Shanghai', 'Shanghai (CST)'),
    ('Asia/Kolkata', 'Mumbai (IST)'),
    ('Australia/Sydney', 'Sydney (AEST/AEDT)'),
]

# Common time preferences for job posts
TIME_PREFERENCE_CHOICES = [
    ('weekday_morning', 'Weekday Mornings (9 AM - 12 PM)'),
    ('weekday_afternoon', 'Weekday Afternoons (12 PM - 5 PM)'),
    ('weekday_evening', 'Weekday Evenings (5 PM - 9 PM)'),
    ('weekend_morning', 'Weekend Mornings (9 AM - 12 PM)'),
    ('weekend_afternoon', 'Weekend Afternoons (12 PM - 5 PM)'),
    ('weekend_evening', 'Weekend Evenings (5 PM - 9 PM)'),
    ('flexible', 'Flexible - Any time works'),
]

class EnhancedLearningRequestForm(FlaskForm):
    """Enhanced job posting form with new fields"""
    
    # Existing fields (from current LearningRequestForm)
    title = StringField('Job Title', validators=[
        DataRequired(message='Please enter a job title'),
        Length(min=10, max=200, message='Title must be between 10 and 200 characters')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(message='Please describe what you want to learn'),
        Length(min=50, max=2000, message='Description must be between 50 and 2000 characters')
    ])
    skills_needed = StringField('Skills Needed', validators=[
        DataRequired(message='Please specify the skills you want to learn')
    ])
    duration = StringField('Duration', validators=[
        DataRequired(message='Please specify how long you expect this to take')
    ])
    budget = FloatField('Budget (per hour)', validators=[
        DataRequired(message='Please specify your budget'),
        NumberRange(min=5, max=500, message='Budget must be between $5 and $500 per hour')
    ])
    experience_level = SelectField('Experience Level', choices=[
        ('', 'Select experience level'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert')
    ], validators=[DataRequired(message='Please select your experience level')])
    skill_type = SelectField('Skill Type', choices=[
        ('short_term', 'Short-term project'),
        ('long_term', 'Long-term learning')
    ], validators=[DataRequired(message='Please select the skill type')])
    
    # New fields for enhanced job posting
    skill_tags = StringField('Skill Tags', validators=[
        Optional()
    ])
    sessions_needed = IntegerField('Number of Sessions (Optional)', validators=[
        Optional(),
        NumberRange(min=1, max=100, message='Sessions must be between 1 and 100')
    ])
    timezone = SelectField('Your Timezone', choices=TIMEZONE_CHOICES, validators=[
        DataRequired(message='Please select your timezone')
    ])
    
    # Time preferences (multiple choice)
    preferred_times = SelectField('Preferred Learning Times', choices=TIME_PREFERENCE_CHOICES, validators=[
        DataRequired(message='Please select your preferred learning times')
    ])
    
    # Screening questions (existing fields)
    screening_question_1 = StringField('Screening Question 1 (Optional)', validators=[
        Optional(),
        Length(max=200, message='Question must be 200 characters or less')
    ])
    screening_question_2 = StringField('Screening Question 2 (Optional)', validators=[
        Optional(),
        Length(max=200, message='Question must be 200 characters or less')
    ])
    screening_question_3 = StringField('Screening Question 3 (Optional)', validators=[
        Optional(),
        Length(max=200, message='Question must be 200 characters or less')
    ])
    screening_question_4 = StringField('Screening Question 4 (Optional)', validators=[
        Optional(),
        Length(max=200, message='Question must be 200 characters or less')
    ])
    screening_question_5 = StringField('Screening Question 5 (Optional)', validators=[
        Optional(),
        Length(max=200, message='Question must be 200 characters or less')
    ])

class EnhancedProposalForm(FlaskForm):
    """Enhanced proposal form with new fields"""
    
    # Existing fields
    cover_letter = TextAreaField('Cover Letter', validators=[
        DataRequired(message='Please write a cover letter'),
        Length(min=50, max=2000, message='Cover letter must be between 50 and 2000 characters')
    ])
    session_count = IntegerField('Number of Sessions', validators=[
        DataRequired(message='Please specify the number of sessions'),
        NumberRange(min=1, max=100, message='Sessions must be between 1 and 100')
    ])
    price_per_session = FloatField('Price per Session ($)', validators=[
        DataRequired(message='Please specify the price per session'),
        NumberRange(min=5, max=500, message='Price must be between $5 and $500')
    ])
    session_duration = IntegerField('Session Duration (minutes)', validators=[
        DataRequired(message='Please specify session duration'),
        NumberRange(min=15, max=480, message='Duration must be between 15 and 480 minutes')
    ])
    
    # New fields for enhanced proposals
    approach_summary = TextAreaField('Teaching Approach', validators=[
        DataRequired(message='Please describe your teaching approach for this specific job'),
        Length(min=50, max=1000, message='Approach summary must be between 50 and 1000 characters')
    ])
    availability_match = BooleanField('I confirm my availability matches the student\'s preferred times')
    payment_model = SelectField('Payment Model', choices=[
        ('per_session', 'Per Session'),
        ('per_hour', 'Per Hour')
    ], validators=[DataRequired(message='Please select payment model')])
    hourly_rate = FloatField('Hourly Rate ($)', validators=[
        Optional(),
        NumberRange(min=5, max=500, message='Hourly rate must be between $5 and $500')
    ])
    
    # Hidden fields for dynamic screening questions
    screening_answers = HiddenField('Screening Answers')

class ContractForm(FlaskForm):
    """Contract creation form"""
    
    start_date = DateField('Start Date', validators=[
        DataRequired(message='Please select a start date')
    ])
    end_date = DateField('End Date (Optional)', validators=[
        Optional()
    ])
    timezone = SelectField('Contract Timezone', choices=TIMEZONE_CHOICES, validators=[
        DataRequired(message='Please select the contract timezone')
    ])
    cancellation_policy = TextAreaField('Cancellation Policy', validators=[
        Optional(),
        Length(max=500, message='Cancellation policy must be 500 characters or less')
    ])
    learning_outcomes = TextAreaField('Expected Learning Outcomes', validators=[
        Optional(),
        Length(max=1000, message='Learning outcomes must be 1000 characters or less')
    ])
    
    def validate_start_date(self, field):
        """Validate start date is not in the past"""
        if field.data and field.data < datetime.now().date():
            raise ValueError('Start date cannot be in the past')
    
    def validate_end_date(self, field):
        """Validate end date is after start date"""
        if field.data and self.start_date.data and field.data <= self.start_date.data:
            raise ValueError('End date must be after start date')

class SessionScheduleForm(FlaskForm):
    """Session scheduling form"""
    
    scheduled_at = DateTimeField('Scheduled Date/Time', validators=[
        DataRequired(message='Please select a date and time')
    ])
    duration_minutes = IntegerField('Duration (minutes)', validators=[
        DataRequired(message='Please specify duration'),
        NumberRange(min=15, max=480, message='Duration must be between 15 and 480 minutes')
    ])
    timezone = SelectField('Session Timezone', choices=TIMEZONE_CHOICES, validators=[
        DataRequired(message='Please select the session timezone')
    ])
    notes = TextAreaField('Session Notes (Optional)', validators=[
        Optional(),
        Length(max=500, message='Notes must be 500 characters or less')
    ])
    
    def validate_scheduled_at(self, field):
        """Validate scheduled time is in the future"""
        if field.data and field.data <= datetime.now():
            raise ValueError('Session must be scheduled for a future date and time')

class RescheduleRequestForm(FlaskForm):
    """Reschedule request form"""
    
    new_scheduled_at = DateTimeField('New Date/Time', validators=[
        DataRequired(message='Please select a new date and time')
    ])
    reason = TextAreaField('Reason for Reschedule', validators=[
        DataRequired(message='Please provide a reason for the reschedule'),
        Length(min=10, max=500, message='Reason must be between 10 and 500 characters')
    ])
    
    def validate_new_scheduled_at(self, field):
        """Validate new scheduled time is in the future"""
        if field.data and field.data <= datetime.now():
            raise ValueError('New session time must be in the future')

class SessionCompletionForm(FlaskForm):
    """Session completion form"""
    
    notes = TextAreaField('Session Notes', validators=[
        Optional(),
        Length(max=1000, message='Notes must be 1000 characters or less')
    ])
    completed_by = SelectField('Completed By', choices=[
        ('coach', 'Coach'),
        ('student', 'Student')
    ], validators=[DataRequired(message='Please specify who completed the session')])

class DirectContractForm(FlaskForm):
    """Direct contract creation form (for direct hire without job post)"""
    
    job_title = StringField('Learning Goal', validators=[
        DataRequired(message='Please describe what you want to learn'),
        Length(min=10, max=200, message='Title must be between 10 and 200 characters')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(message='Please describe your learning needs'),
        Length(min=50, max=2000, message='Description must be between 50 and 2000 characters')
    ])
    session_count = IntegerField('Number of Sessions', validators=[
        DataRequired(message='Please specify the number of sessions'),
        NumberRange(min=1, max=100, message='Sessions must be between 1 and 100')
    ])
    price_per_session = FloatField('Price per Session ($)', validators=[
        DataRequired(message='Please specify the price per session'),
        NumberRange(min=5, max=500, message='Price must be between $5 and $500')
    ])
    session_duration = IntegerField('Session Duration (minutes)', validators=[
        DataRequired(message='Please specify session duration'),
        NumberRange(min=15, max=480, message='Duration must be between 15 and 480 minutes')
    ])
    start_date = DateField('Start Date', validators=[
        DataRequired(message='Please select a start date')
    ])
    timezone = SelectField('Timezone', choices=TIMEZONE_CHOICES, validators=[
        DataRequired(message='Please select your timezone')
    ])
    learning_outcomes = TextAreaField('Expected Learning Outcomes', validators=[
        Optional(),
        Length(max=1000, message='Learning outcomes must be 1000 characters or less')
    ])

# Form helper functions

def create_dynamic_proposal_form(learning_request):
    """Create a dynamic proposal form based on learning request screening questions"""
    class DynamicProposalForm(EnhancedProposalForm):
        pass
    
    # Add dynamic screening question fields
    screening_questions = learning_request.screening_questions
    for i, question in enumerate(screening_questions):
        field_name = f'screening_answer_{i+1}'
        setattr(DynamicProposalForm, field_name, TextAreaField(
            f'Answer: {question.question_text}',
            validators=[DataRequired(message='Please answer this question')]
        ))
    
    return DynamicProposalForm()

def get_timezone_choices():
    """Get timezone choices for forms"""
    return TIMEZONE_CHOICES

def get_time_preference_choices():
    """Get time preference choices for job posts"""
    return TIME_PREFERENCE_CHOICES

# Form validation helpers

def validate_proposal_data(form, learning_request):
    """Validate proposal data against learning request"""
    errors = []
    
    # Check if sessions needed matches (if specified)
    if learning_request.sessions_needed and form.session_count.data != learning_request.sessions_needed:
        errors.append(f"Job requires {learning_request.sessions_needed} sessions, but you proposed {form.session_count.data}")
    
    # Check if price is within budget
    if form.price_per_session.data > learning_request.budget:
        errors.append(f"Your price (${form.price_per_session.data}) exceeds the student's budget (${learning_request.budget})")
    
    # Check if payment model is appropriate
    if form.payment_model.data == 'per_hour' and not form.hourly_rate.data:
        errors.append("Hourly rate is required when using per-hour payment model")
    
    return errors

def validate_contract_data(form, proposal):
    """Validate contract data against proposal"""
    errors = []
    
    # Check if start date is reasonable
    if form.start_date.data:
        min_start_date = datetime.now().date() + timedelta(days=1)
        if form.start_date.data < min_start_date:
            errors.append("Contract start date should be at least 1 day in the future")
    
    # Check if end date is reasonable (if provided)
    if form.end_date.data and form.start_date.data:
        max_duration = timedelta(days=365)  # 1 year max
        if form.end_date.data - form.start_date.data > max_duration:
            errors.append("Contract duration cannot exceed 1 year")
    
    return errors

def validate_session_schedule(form, contract):
    """Validate session schedule against contract"""
    errors = []
    
    # Check if session is within contract period
    if form.scheduled_at.data:
        session_date = form.scheduled_at.data.date()
        if session_date < contract.start_date:
            errors.append("Session cannot be scheduled before contract start date")
        
        if contract.end_date and session_date > contract.end_date:
            errors.append("Session cannot be scheduled after contract end date")
    
    # Check if duration is reasonable
    if form.duration_minutes.data:
        if form.duration_minutes.data < 15:
            errors.append("Session duration must be at least 15 minutes")
        if form.duration_minutes.data > 480:  # 8 hours
            errors.append("Session duration cannot exceed 8 hours")
    
    return errors
