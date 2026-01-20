from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, IntegerField, FloatField, DateField, BooleanField, PasswordField, HiddenField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, URL, ValidationError
import re
from wtforms.widgets import TextArea
from wtforms.fields import TimeField
from datetime import date
from utils import get_available_timezones, get_common_timezones

def validate_password_strength(form, field):
    """Custom validator for password strength requirements"""
    password = field.data
    
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long and include uppercase, lowercase, number, and special character.')
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must be at least 8 characters long and include uppercase, lowercase, number, and special character.')
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must be at least 8 characters long and include uppercase, lowercase, number, and special character.')
    
    # Check for at least one number
    if not re.search(r'\d', password):
        raise ValidationError('Password must be at least 8 characters long and include uppercase, lowercase, number, and special character.')
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        raise ValidationError('Password must be at least 8 characters long and include uppercase, lowercase, number, and special character.')

# Role Switching Forms
class RoleSwitchForm(FlaskForm):
    """Form for role switching with CSRF protection"""
    role = SelectField('Switch to Role', choices=[
        ('student', 'Student'),
        ('coach', 'Coach')
    ], validators=[DataRequired()])

class UpgradeToCoachForm(FlaskForm):
    """Form for upgrading student to coach"""
    terms_accepted = BooleanField('I agree to the Coach Terms of Service', validators=[DataRequired()])
    ready_to_teach = BooleanField('I am ready to start teaching and coaching', validators=[DataRequired()])

class UpgradeToStudentForm(FlaskForm):
    """Form for upgrading coach to student"""
    terms_accepted = BooleanField('I agree to the Student Terms of Service', validators=[DataRequired()])
    ready_to_learn = BooleanField('I am ready to start learning', validators=[DataRequired()])

# Existing Forms (keeping all your original forms)
class SignupForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), validate_password_strength])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class AdminLoginForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])

class CoachStep1Form(FlaskForm):
    goal = SelectField('Goal', choices=[
        ('main_income', 'This is my main source of income'),
        ('side_income', 'This is for side income'),
        ('no_goal', 'I don\'t have a specific goal')
    ], validators=[DataRequired()])

class CoachStep3Form(FlaskForm):
    skills = StringField('Skills (comma-separated)', validators=[DataRequired()])

class CoachStep4Form(FlaskForm):
    title = StringField('Job Title', validators=[Optional(), Length(max=100)])
    company = StringField('Company', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    is_current = BooleanField('I currently work here')

class CoachStep5Form(FlaskForm):
    institution = StringField('Institution', validators=[Optional(), Length(max=100)])
    degree = StringField('Degree', validators=[Optional(), Length(max=100)])
    field_of_study = StringField('Field of Study', validators=[Optional(), Length(max=100)])
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[Optional()])
    is_current = BooleanField('I currently study here')

def validate_allowed_links(form, field):
    if not field.data or not field.data.strip():
        return

    allowed_domains = [
        'youtube.com', 'youtu.be', 'www.youtube.com',
        'drive.google.com', 'docs.google.com', 'sheets.google.com', 'slides.google.com',
        'dropbox.com', 'www.dropbox.com',
        'onedrive.live.com', 'onedrive.microsoft.com',
        'github.com', 'www.github.com', 'gitlab.com', 'www.gitlab.com',
        'vimeo.com', 'www.vimeo.com',
        'loom.com', 'www.loom.com'
    ]

    links = [link.strip() for link in field.data.split('\n') if link.strip()]
    for link in links:
        if not link.startswith(('http://', 'https://')):
            link = 'https://' + link

        # Extract domain from URL
        domain_match = re.match(r'https?://(?:www\.)?([^/]+)', link)
        if not domain_match:
            raise ValidationError(f'Invalid URL format: {link}')

        domain = domain_match.group(1).lower()
        if not any(allowed_domain in domain for allowed_domain in allowed_domains):
            raise ValidationError(f'Only YouTube, Google Drive, Dropbox, OneDrive, GitHub, GitLab, Vimeo, and Loom links are allowed. Found: {domain}')

# Portfolio form
class PortfolioForm(FlaskForm):
    category = SelectField('Portfolio Category', choices=[
        ('case_study', 'Case Study'),
        ('work_sample', 'Work Sample'),
        ('introduction', 'Introduction'),
        ('tutorial', 'Tutorial/Demo'),
        ('testimonial', 'Client Testimonial'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    title = StringField('Project Title', validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField('Project Description', validators=[DataRequired(), Length(min=50, max=2000)])
    project_links = TextAreaField('Project Links (one per line)', validators=[Optional(), validate_allowed_links])
    thumbnail_image = FileField('Thumbnail/Cover Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    skills = StringField('Skills Used (comma-separated)', validators=[Optional(), Length(max=255)])

# Portfolio form for onboarding (optional step)
class CoachStep5PortfolioForm(FlaskForm):
    title = StringField('Portfolio Item Title', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(min=50, max=2000)])
    project_links = TextAreaField('Project Links (one per line)', validators=[Optional(), Length(max=1000)])
    skills = StringField('Skills Used (comma-separated)', validators=[Optional(), Length(max=255)])
    thumbnail_image = FileField('Thumbnail/Cover Image', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])

class CoachStep6Form(FlaskForm):
    language = SelectField('Language', choices=[
        ('', 'Select a language'),
        ('English', 'English'),
        ('Spanish', 'Spanish'),
        ('French', 'French'),
        ('German', 'German'),
        ('Portuguese', 'Portuguese'),
        ('Italian', 'Italian'),
        ('Mandarin', 'Mandarin'),
        ('Japanese', 'Japanese'),
        ('Korean', 'Korean'),
        ('Arabic', 'Arabic'),
        ('Hindi', 'Hindi'),
        ('Russian', 'Russian'),
        ('Dutch', 'Dutch'),
        ('Swedish', 'Swedish'),
        ('Norwegian', 'Norwegian'),
        ('Danish', 'Danish'),
        ('Finnish', 'Finnish'),
        ('Polish', 'Polish'),
        ('Turkish', 'Turkish'),
        ('Hebrew', 'Hebrew'),
        ('Thai', 'Thai'),
        ('Vietnamese', 'Vietnamese'),
        ('Indonesian', 'Indonesian'),
        ('Malay', 'Malay'),
        ('Tagalog', 'Tagalog'),
        ('Swahili', 'Swahili'),
        ('Greek', 'Greek'),
        ('Czech', 'Czech'),
        ('Hungarian', 'Hungarian'),
        ('Romanian', 'Romanian'),
        ('Bulgarian', 'Bulgarian'),
        ('Croatian', 'Croatian'),
        ('Serbian', 'Serbian'),
        ('Slovak', 'Slovak'),
        ('Slovenian', 'Slovenian'),
        ('Lithuanian', 'Lithuanian'),
        ('Latvian', 'Latvian'),
        ('Estonian', 'Estonian'),
        ('Ukrainian', 'Ukrainian'),
        ('Belarusian', 'Belarusian'),
        ('Gujarati', 'Gujarati'),
        ('Bengali', 'Bengali'),
        ('Tamil', 'Tamil'),
        ('Telugu', 'Telugu'),
        ('Marathi', 'Marathi'),
        ('Urdu', 'Urdu'),
        ('Persian', 'Persian'),
        ('Amharic', 'Amharic'),
        ('Yoruba', 'Yoruba'),
        ('Zulu', 'Zulu'),
        ('Afrikaans', 'Afrikaans'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    proficiency = SelectField('Proficiency', choices=[
        ('', 'Select proficiency level'),
        ('basic', 'Basic'),
        ('conversational', 'Conversational'),
        ('fluent', 'Fluent'),
        ('native', 'Native')
    ], validators=[DataRequired()])

class CoachStep7Form(FlaskForm):
    coach_title = StringField('Coach Title', validators=[DataRequired(), Length(min=5, max=80)], 
                             render_kw={"placeholder": "e.g., Graphic Design Coach, Fluent English Tutor"})
    bio = TextAreaField('Bio', validators=[DataRequired(), Length(min=100, max=5000)],
                       widget=TextArea())

class CoachStep8Form(FlaskForm):
    country = SelectField('Country', choices=[
        ('', 'Select your country'),
        ('Afghanistan', 'Afghanistan'),
        ('Albania', 'Albania'),
        ('Algeria', 'Algeria'),
        ('Argentina', 'Argentina'),
        ('Armenia', 'Armenia'),
        ('Australia', 'Australia'),
        ('Austria', 'Austria'),
        ('Azerbaijan', 'Azerbaijan'),
        ('Bahrain', 'Bahrain'),
        ('Bangladesh', 'Bangladesh'),
        ('Belarus', 'Belarus'),
        ('Belgium', 'Belgium'),
        ('Bolivia', 'Bolivia'),
        ('Bosnia and Herzegovina', 'Bosnia and Herzegovina'),
        ('Brazil', 'Brazil'),
        ('Bulgaria', 'Bulgaria'),
        ('Cambodia', 'Cambodia'),
        ('Canada', 'Canada'),
        ('Chile', 'Chile'),
        ('China', 'China'),
        ('Colombia', 'Colombia'),
        ('Croatia', 'Croatia'),
        ('Czech Republic', 'Czech Republic'),
        ('Denmark', 'Denmark'),
        ('Ecuador', 'Ecuador'),
        ('Egypt', 'Egypt'),
        ('Estonia', 'Estonia'),
        ('Ethiopia', 'Ethiopia'),
        ('Finland', 'Finland'),
        ('France', 'France'),
        ('Georgia', 'Georgia'),
        ('Germany', 'Germany'),
        ('Ghana', 'Ghana'),
        ('Greece', 'Greece'),
        ('Hungary', 'Hungary'),
        ('Iceland', 'Iceland'),
        ('India', 'India'),
        ('Indonesia', 'Indonesia'),
        ('Iran', 'Iran'),
        ('Iraq', 'Iraq'),
        ('Ireland', 'Ireland'),
        ('Israel', 'Israel'),
        ('Italy', 'Italy'),
        ('Japan', 'Japan'),
        ('Jordan', 'Jordan'),
        ('Kazakhstan', 'Kazakhstan'),
        ('Kenya', 'Kenya'),
        ('South Korea', 'South Korea'),
        ('Kuwait', 'Kuwait'),
        ('Latvia', 'Latvia'),
        ('Lebanon', 'Lebanon'),
        ('Lithuania', 'Lithuania'),
        ('Luxembourg', 'Luxembourg'),
        ('Malaysia', 'Malaysia'),
        ('Mexico', 'Mexico'),
        ('Morocco', 'Morocco'),
        ('Netherlands', 'Netherlands'),
        ('New Zealand', 'New Zealand'),
        ('Nigeria', 'Nigeria'),
        ('Norway', 'Norway'),
        ('Pakistan', 'Pakistan'),
        ('Peru', 'Peru'),
        ('Philippines', 'Philippines'),
        ('Poland', 'Poland'),
        ('Portugal', 'Portugal'),
        ('Qatar', 'Qatar'),
        ('Romania', 'Romania'),
        ('Russia', 'Russia'),
        ('Saudi Arabia', 'Saudi Arabia'),
        ('Serbia', 'Serbia'),
        ('Singapore', 'Singapore'),
        ('Slovakia', 'Slovakia'),
        ('Slovenia', 'Slovenia'),
        ('South Africa', 'South Africa'),
        ('Spain', 'Spain'),
        ('Sri Lanka', 'Sri Lanka'),
        ('Sweden', 'Sweden'),
        ('Switzerland', 'Switzerland'),
        ('Thailand', 'Thailand'),
        ('Turkey', 'Turkey'),
        ('Ukraine', 'Ukraine'),
        ('United Arab Emirates', 'United Arab Emirates'),
        ('United Kingdom', 'United Kingdom'),
        ('United States', 'United States'),
        ('Uruguay', 'Uruguay'),
        ('Venezuela', 'Venezuela'),
        ('Vietnam', 'Vietnam'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    hourly_rate = FloatField('Hourly Rate ($)', validators=[DataRequired(), NumberRange(min=5, max=500)])
    profile_picture = FileField('Profile Picture', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])

class CoachStep9Form(FlaskForm):
    terms_accepted = BooleanField('I confirm that all information provided is accurate and I agree to the Terms of Service and Community Guidelines', 
                                 validators=[DataRequired(message='You must accept the terms to continue.')])

class StudentOnboardingForm(FlaskForm):
    bio = TextAreaField('Bio', validators=[DataRequired(), Length(min=50, max=1000)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=13, max=100)])
    country = SelectField('Country', choices=[
        ('', 'Select your country'),
        ('Afghanistan', 'Afghanistan'),
        ('Albania', 'Albania'),
        ('Algeria', 'Algeria'),
        ('Argentina', 'Argentina'),
        ('Armenia', 'Armenia'),
        ('Australia', 'Australia'),
        ('Austria', 'Austria'),
        ('Azerbaijan', 'Azerbaijan'),
        ('Bahrain', 'Bahrain'),
        ('Bangladesh', 'Bangladesh'),
        ('Belarus', 'Belarus'),
        ('Belgium', 'Belgium'),
        ('Bolivia', 'Bolivia'),
        ('Bosnia and Herzegovina', 'Bosnia and Herzegovina'),
        ('Brazil', 'Brazil'),
        ('Bulgaria', 'Bulgaria'),
        ('Cambodia', 'Cambodia'),
        ('Canada', 'Canada'),
        ('Chile', 'Chile'),
        ('China', 'China'),
        ('Colombia', 'Colombia'),
        ('Croatia', 'Croatia'),
        ('Czech Republic', 'Czech Republic'),
        ('Denmark', 'Denmark'),
        ('Ecuador', 'Ecuador'),
        ('Egypt', 'Egypt'),
        ('Estonia', 'Estonia'),
        ('Ethiopia', 'Ethiopia'),
        ('Finland', 'Finland'),
        ('France', 'France'),
        ('Georgia', 'Georgia'),
        ('Germany', 'Germany'),
        ('Ghana', 'Ghana'),
        ('Greece', 'Greece'),
        ('Hungary', 'Hungary'),
        ('Iceland', 'Iceland'),
        ('India', 'India'),
        ('Indonesia', 'Indonesia'),
        ('Iran', 'Iran'),
        ('Iraq', 'Iraq'),
        ('Ireland', 'Ireland'),
        ('Israel', 'Israel'),
        ('Italy', 'Italy'),
        ('Japan', 'Japan'),
        ('Jordan', 'Jordan'),
        ('Kazakhstan', 'Kazakhstan'),
        ('Kenya', 'Kenya'),
        ('South Korea', 'South Korea'),
        ('Kuwait', 'Kuwait'),
        ('Latvia', 'Latvia'),
        ('Lebanon', 'Lebanon'),
        ('Lithuania', 'Lithuania'),
        ('Luxembourg', 'Luxembourg'),
        ('Malaysia', 'Malaysia'),
        ('Mexico', 'Mexico'),
        ('Morocco', 'Morocco'),
        ('Netherlands', 'Netherlands'),
        ('New Zealand', 'New Zealand'),
        ('Nigeria', 'Nigeria'),
        ('Norway', 'Norway'),
        ('Pakistan', 'Pakistan'),
        ('Peru', 'Peru'),
        ('Philippines', 'Philippines'),
        ('Poland', 'Poland'),
        ('Portugal', 'Portugal'),
        ('Qatar', 'Qatar'),
        ('Romania', 'Romania'),
        ('Russia', 'Russia'),
        ('Saudi Arabia', 'Saudi Arabia'),
        ('Serbia', 'Serbia'),
        ('Singapore', 'Singapore'),
        ('Slovakia', 'Slovakia'),
        ('Slovenia', 'Slovenia'),
        ('South Africa', 'South Africa'),
        ('Spain', 'Spain'),
        ('Sri Lanka', 'Sri Lanka'),
        ('Sweden', 'Sweden'),
        ('Switzerland', 'Switzerland'),
        ('Thailand', 'Thailand'),
        ('Turkey', 'Turkey'),
        ('Ukraine', 'Ukraine'),
        ('United Arab Emirates', 'United Arab Emirates'),
        ('United Kingdom', 'United Kingdom'),
        ('United States', 'United States'),
        ('Uruguay', 'Uruguay'),
        ('Venezuela', 'Venezuela'),
        ('Vietnam', 'Vietnam'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    profile_picture = FileField('Profile Picture', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    # Languages will be handled separately

class LearningRequestForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=10, max=50)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=50, max=2000)])
    skills_needed = StringField('Skills Needed (comma-separated)', validators=[DataRequired()])
    duration = StringField('Expected Duration', validators=[DataRequired(), Length(max=50)])
    budget = FloatField('Budget ($)', validators=[DataRequired(), NumberRange(min=10)])
    experience_level = SelectField('Required Experience Level', choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert')
    ], validators=[DataRequired()])
    skill_type = SelectField('Skill Type', choices=[
        ('short_term', 'Quick Skill'),
        ('long_term', 'Deep Skill')
    ], validators=[DataRequired()])

    # Screening questions - optional fields with max 250 characters each
    screening_question_1 = StringField('Screening Question 1', validators=[Optional(), Length(max=250)])
    screening_question_2 = StringField('Screening Question 2', validators=[Optional(), Length(max=250)])
    screening_question_3 = StringField('Screening Question 3', validators=[Optional(), Length(max=250)])
    screening_question_4 = StringField('Screening Question 4', validators=[Optional(), Length(max=250)])
    screening_question_5 = StringField('Screening Question 5', validators=[Optional(), Length(max=250)])

class LanguageForm(FlaskForm):
    """Form for adding/editing individual languages"""
    language = SelectField('Language', choices=[
        ('', 'Select a language'),
        ('English', 'English'),
        ('Spanish', 'Spanish'),
        ('French', 'French'),
        ('German', 'German'),
        ('Portuguese', 'Portuguese'),
        ('Italian', 'Italian'),
        ('Mandarin', 'Mandarin'),
        ('Japanese', 'Japanese'),
        ('Korean', 'Korean'),
        ('Arabic', 'Arabic'),
        ('Hindi', 'Hindi'),
        ('Russian', 'Russian'),
        ('Dutch', 'Dutch'),
        ('Swedish', 'Swedish'),
        ('Norwegian', 'Norwegian'),
        ('Danish', 'Danish'),
        ('Finnish', 'Finnish'),
        ('Polish', 'Polish'),
        ('Turkish', 'Turkish'),
        ('Hebrew', 'Hebrew'),
        ('Thai', 'Thai'),
        ('Vietnamese', 'Vietnamese'),
        ('Indonesian', 'Indonesian'),
        ('Malay', 'Malay'),
        ('Tagalog', 'Tagalog'),
        ('Swahili', 'Swahili'),
        ('Greek', 'Greek'),
        ('Czech', 'Czech'),
        ('Hungarian', 'Hungarian'),
        ('Romanian', 'Romanian'),
        ('Bulgarian', 'Bulgarian'),
        ('Croatian', 'Croatian'),
        ('Serbian', 'Serbian'),
        ('Slovak', 'Slovak'),
        ('Slovenian', 'Slovenian'),
        ('Lithuanian', 'Lithuanian'),
        ('Latvian', 'Latvian'),
        ('Estonian', 'Estonian'),
        ('Ukrainian', 'Ukrainian'),
        ('Belarusian', 'Belarusian'),
        ('Gujarati', 'Gujarati'),
        ('Bengali', 'Bengali'),
        ('Tamil', 'Tamil'),
        ('Telugu', 'Telugu'),
        ('Marathi', 'Marathi'),
        ('Urdu', 'Urdu'),
        ('Persian', 'Persian'),
        ('Amharic', 'Amharic'),
        ('Yoruba', 'Yoruba'),
        ('Zulu', 'Zulu'),
        ('Afrikaans', 'Afrikaans'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    proficiency = SelectField('Proficiency', choices=[
        ('', 'Select proficiency level'),
        ('basic', 'Basic'),
        ('conversational', 'Conversational'),
        ('fluent', 'Fluent'),
        ('native', 'Native')
    ], validators=[DataRequired()])

class StudentLanguageForm(FlaskForm):
    """Form for adding/editing student languages"""
    language = SelectField('Language', choices=[
        ('', 'Select a language'),
        ('English', 'English'),
        ('Spanish', 'Spanish'),
        ('French', 'French'),
        ('German', 'German'),
        ('Portuguese', 'Portuguese'),
        ('Italian', 'Italian'),
        ('Mandarin', 'Mandarin'),
        ('Japanese', 'Japanese'),
        ('Korean', 'Korean'),
        ('Arabic', 'Arabic'),
        ('Hindi', 'Hindi'),
        ('Russian', 'Russian'),
        ('Dutch', 'Dutch'),
        ('Swedish', 'Swedish'),
        ('Norwegian', 'Norwegian'),
        ('Danish', 'Danish'),
        ('Finnish', 'Finnish'),
        ('Polish', 'Polish'),
        ('Turkish', 'Turkish'),
        ('Hebrew', 'Hebrew'),
        ('Thai', 'Thai'),
        ('Vietnamese', 'Vietnamese'),
        ('Indonesian', 'Indonesian'),
        ('Malay', 'Malay'),
        ('Tagalog', 'Tagalog'),
        ('Swahili', 'Swahili'),
        ('Greek', 'Greek'),
        ('Czech', 'Czech'),
        ('Hungarian', 'Hungarian'),
        ('Romanian', 'Romanian'),
        ('Bulgarian', 'Bulgarian'),
        ('Croatian', 'Croatian'),
        ('Serbian', 'Serbian'),
        ('Slovak', 'Slovak'),
        ('Slovenian', 'Slovenian'),
        ('Lithuanian', 'Lithuanian'),
        ('Latvian', 'Latvian'),
        ('Estonian', 'Estonian'),
        ('Ukrainian', 'Ukrainian'),
        ('Belarusian', 'Belarusian'),
        ('Gujarati', 'Gujarati'),
        ('Bengali', 'Bengali'),
        ('Tamil', 'Tamil'),
        ('Telugu', 'Telugu'),
        ('Marathi', 'Marathi'),
        ('Urdu', 'Urdu'),
        ('Persian', 'Persian'),
        ('Amharic', 'Amharic'),
        ('Yoruba', 'Yoruba'),
        ('Zulu', 'Zulu'),
        ('Afrikaans', 'Afrikaans'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    proficiency = SelectField('Proficiency', choices=[
        ('', 'Select proficiency level'),
        ('Basic', 'Basic'),
        ('Conversational', 'Conversational'),
        ('Fluent', 'Fluent'),
        ('Native', 'Native')
    ], validators=[DataRequired()])

class ProposalForm(FlaskForm):
    cover_letter = TextAreaField('Cover Letter', validators=[DataRequired(), Length(min=100, max=2000)])
    session_count = IntegerField('Number of Sessions', validators=[DataRequired(), NumberRange(min=1, max=50)])
    price_per_session = FloatField('Price per Session ($)', validators=[DataRequired(), NumberRange(min=10)])
    session_duration = SelectField('Session Duration (minutes)', choices=[
        (30, '30 minutes'),
        (45, '45 minutes'),
        (60, '1 hour'),
        (90, '1.5 hours'),
        (120, '2 hours')
    ], coerce=int, validators=[DataRequired()])

class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=1000)])

class ContractForm(FlaskForm):
    """Contract creation form"""
    start_date = DateField('Start Date', validators=[
        DataRequired(message='Please select a start date')
    ])
    end_date = DateField('End Date (Optional)', validators=[
        Optional()
    ])
    total_sessions = IntegerField('Number of Sessions', validators=[
        DataRequired(message='Please specify number of sessions'),
        NumberRange(min=1, max=100, message='Number of sessions must be between 1 and 100')
    ])
    duration_minutes = IntegerField('Session Duration (minutes)', validators=[
        DataRequired(message='Please specify session duration'),
        NumberRange(min=15, max=480, message='Duration must be between 15 and 480 minutes')
    ])
    rate = FloatField('Rate per Session ($)', validators=[
        DataRequired(message='Please specify rate per session'),
        NumberRange(min=0.01, message='Rate must be greater than 0')
    ])
    timezone = SelectField('Timezone', choices=get_common_timezones(), validators=[DataRequired(message='Please select a timezone')])
    cancellation_policy = TextAreaField('Cancellation Policy', validators=[
        Optional(),
        Length(max=1000, message='Cancellation policy must be 1000 characters or less')
    ])
    learning_outcomes = TextAreaField('Learning Outcomes', validators=[
        Optional(),
        Length(max=1000, message='Learning outcomes must be 1000 characters or less')
    ])

class SessionScheduleForm(FlaskForm):
    """Session scheduling form"""
    scheduled_at = StringField('Scheduled Date/Time', validators=[
        DataRequired(message='Please select a date and time')
    ])
    duration_minutes = IntegerField('Duration (minutes)', validators=[
        DataRequired(message='Please specify duration'),
        NumberRange(min=15, max=480, message='Duration must be between 15 and 480 minutes')
    ])
    timezone = SelectField('Timezone', choices=get_common_timezones(), validators=[DataRequired(message='Please select a timezone')])

class RescheduleRequestForm(FlaskForm):
    """Reschedule request form with 5-hour policy"""
    reason = TextAreaField('Reason for Reschedule', validators=[
        DataRequired(message='Please provide a reason'),
        Length(min=10, max=500, message='Reason must be between 10 and 500 characters')
    ])
    
    new_scheduled_at = DateTimeField('New Date/Time', validators=[
        DataRequired(message='Please select a new date and time for the reschedule')
    ], format='%Y-%m-%dT%H:%M')
    
    timezone = SelectField('Timezone', choices=get_common_timezones(), default='UTC')

class RescheduleApprovalForm(FlaskForm):
    """Reschedule approval form"""
    new_scheduled_at = StringField('New Date/Time', validators=[
        DataRequired(message='Please select a new date and time')
    ])

class SessionCompletionForm(FlaskForm):
    """Session completion form"""
    notes = TextAreaField('Session Notes', validators=[
        Optional(),
        Length(max=1000, message='Notes must be 1000 characters or less')
    ])

class SessionCancelForm(FlaskForm):
    """Session cancellation form"""
    reason = TextAreaField('Cancellation Reason (Optional)', validators=[
        Optional(),
        Length(max=500, message='Reason must be 500 characters or less')
    ])

class SessionMissedForm(FlaskForm):
    """Session missed form"""
    reason = TextAreaField('Reason for No-Show (Optional)', validators=[
        Optional(),
        Length(max=500, message='Reason must be 500 characters or less')
    ])

class PaymentForm(FlaskForm):
    """Payment form for contract payment"""
    submit = SubmitField('Pay Now')

# ============================================================================
# ENTERPRISE SCHEDULING SYSTEM FORMS
# ============================================================================

class SessionBookingForm(FlaskForm):
    """Form for booking sessions with coaches"""
    
    session_type = SelectField('Session Type', choices=[
        ('consultation', 'Free Consultation (15 min)'),
        ('paid', 'Paid Session')
    ], validators=[DataRequired()])
    
    scheduled_at = DateTimeField('Scheduled Time', validators=[
        DataRequired(message='Please select a time for your session')
    ], format='%Y-%m-%dT%H:%M')
    
    duration_minutes = IntegerField('Duration (minutes)', validators=[
        DataRequired(message='Please specify session duration'),
        NumberRange(min=15, max=480, message='Duration must be between 15 minutes and 8 hours')
    ])
    
    notes = TextAreaField('Notes (Optional)', validators=[
        Optional(),
        Length(max=500, message='Notes must be 500 characters or less')
    ])
    
    submit = SubmitField('Book Session')



class CoachAvailabilityForm(FlaskForm):
    """Form for coach availability settings"""
    
    is_available = BooleanField('Accepting Bookings')
    
    timezone = SelectField('Timezone', choices=get_common_timezones(), validators=[DataRequired()])
    
    # Working hours
    monday_start = TimeField('Monday Start Time')
    monday_end = TimeField('Monday End Time')
    tuesday_start = TimeField('Tuesday Start Time')
    tuesday_end = TimeField('Tuesday End Time')
    wednesday_start = TimeField('Wednesday Start Time')
    wednesday_end = TimeField('Wednesday End Time')
    thursday_start = TimeField('Thursday Start Time')
    thursday_end = TimeField('Thursday End Time')
    friday_start = TimeField('Friday Start Time')
    friday_end = TimeField('Friday End Time')
    saturday_start = TimeField('Saturday Start Time')
    saturday_end = TimeField('Saturday End Time')
    sunday_start = TimeField('Sunday Start Time')
    sunday_end = TimeField('Sunday End Time')
    
    # Session settings
    session_duration = IntegerField('Default Session Duration (minutes)', validators=[
        DataRequired(),
        NumberRange(min=15, max=480, message='Duration must be between 15 minutes and 8 hours')
    ])
    
    buffer_before = IntegerField('Buffer Before Sessions (minutes)', validators=[
        NumberRange(min=0, max=60, message='Buffer must be between 0 and 60 minutes')
    ])
    
    buffer_after = IntegerField('Buffer After Sessions (minutes)', validators=[
        NumberRange(min=0, max=60, message='Buffer must be between 0 and 60 minutes')
    ])
    
    # Booking settings
    advance_booking_days = IntegerField('Advance Booking Days', validators=[
        DataRequired(),
        NumberRange(min=1, max=365, message='Advance booking must be between 1 and 365 days')
    ])
    
    same_day_booking = BooleanField('Allow Same-Day Bookings')
    instant_confirmation = BooleanField('Auto-Confirm Bookings')
    
    # Consultation settings
    consultation_available = BooleanField('Offer Free Consultations')
    consultation_duration = IntegerField('Consultation Duration (minutes)', validators=[
        NumberRange(min=5, max=60, message='Consultation duration must be between 5 and 60 minutes')
    ])
    consultation_advance_hours = IntegerField('Consultation Advance Hours', validators=[
        NumberRange(min=1, max=72, message='Consultation advance notice must be between 1 and 72 hours')
    ])
    
    submit = SubmitField('Save Availability Settings')

class BookingRulesForm(FlaskForm):
    """Form for booking rules and policies"""
    
    # Cancellation and reschedule policies
    cancellation_hours = IntegerField('Cancellation Notice (hours)', validators=[
        DataRequired(),
        NumberRange(min=1, max=168, message='Cancellation notice must be between 1 and 168 hours')
    ])
    
    reschedule_hours = IntegerField('Reschedule Notice (hours)', validators=[
        DataRequired(),
        NumberRange(min=1, max=168, message='Reschedule notice must be between 1 and 168 hours')
    ])
    
    no_show_policy = SelectField('No-Show Policy', choices=[
        ('charge_full', 'Charge Full Amount'),
        ('charge_partial', 'Charge Partial Amount'),
        ('no_charge', 'No Charge')
    ], validators=[DataRequired()])
    
    # Payment policies
    require_payment_before = BooleanField('Require Payment Before Booking')
    allow_partial_payment = BooleanField('Allow Partial Payments')
    
    # Notification settings
    send_reminder_hours = IntegerField('Send Reminder (hours before)', validators=[
        DataRequired(),
        NumberRange(min=1, max=72, message='Reminder must be sent between 1 and 72 hours before')
    ])
    
    send_confirmation = BooleanField('Send Booking Confirmation')
    send_cancellation = BooleanField('Send Cancellation Notifications')
    
    submit = SubmitField('Save Booking Rules')

class AvailabilityExceptionForm(FlaskForm):
    """Form for adding availability exceptions"""
    
    date = DateField('Date', validators=[
        DataRequired(message='Please select a date')
    ])
    
    start_time = TimeField('Start Time (Optional - leave blank for whole day)')
    end_time = TimeField('End Time (Optional - leave blank for whole day)')
    
    is_blocked = BooleanField('Block This Time (uncheck to make available)')
    
    reason = StringField('Reason', validators=[
        DataRequired(message='Please provide a reason for this exception'),
        Length(max=255, message='Reason must be 255 characters or less')
    ])
    
    submit = SubmitField('Add Exception')

class FreeConsultationForm(FlaskForm):
    """Form for scheduling free 15-minute consultations"""
    scheduled_date = DateField('Date', validators=[DataRequired()])
    scheduled_time = TimeField('Time', validators=[DataRequired()])
    timezone = SelectField('Timezone', choices=get_common_timezones(), default='UTC')
    notes = TextAreaField('Notes (Optional)', validators=[Optional(), Length(max=500)])
    
    def validate_scheduled_date(self, field):
        """Ensure date is in the future"""
        if field.data < date.today():
            raise ValidationError('Date must be in the future')
    
    def validate_scheduled_time(self, field):
        """Ensure time is reasonable (between 6 AM and 10 PM)"""
        if field.data:
            hour = field.data.hour
            if hour < 6 or hour > 22:
                raise ValidationError('Time must be between 6:00 AM and 10:00 PM')

class PaidSessionForm(FlaskForm):
    """Form for scheduling paid sessions"""
    scheduled_date = DateField('Date', validators=[DataRequired()])
    scheduled_time = TimeField('Time', validators=[DataRequired()])
    timezone = SelectField('Timezone', choices=get_common_timezones(), default='UTC')
    duration_minutes = SelectField('Duration', choices=[
        (30, '30 minutes'),
        (45, '45 minutes'),
        (60, '1 hour'),
        (90, '1.5 hours'),
        (120, '2 hours')
    ], default=60)
    notes = TextAreaField('Session Notes (Optional)', validators=[Optional(), Length(max=1000)])
    
    def validate_scheduled_date(self, field):
        """Ensure date is in the future"""
        if field.data < date.today():
            raise ValidationError('Date must be in the future')
    
    def validate_scheduled_time(self, field):
        """Ensure time is reasonable (between 6 AM and 10 PM)"""
        if field.data:
            hour = field.data.hour
            if hour < 6 or hour > 22:
                raise ValidationError('Time must be between 6:00 AM and 10:00 PM')

class RescheduleCallForm(FlaskForm):
    """Form for rescheduling calls"""
    new_scheduled_date = DateField('New Date', validators=[DataRequired()])
    new_scheduled_time = TimeField('New Time', validators=[DataRequired()])
    timezone = SelectField('Timezone', choices=get_common_timezones(), default='UTC')
    reason = TextAreaField('Reason for Reschedule', validators=[DataRequired(), Length(min=10, max=500)])
    
    def validate_new_scheduled_date(self, field):
        """Ensure date is in the future"""
        if field.data < date.today():
            raise ValidationError('Date must be in the future')
    
    def validate_new_scheduled_time(self, field):
        """Ensure time is reasonable"""
        if field.data:
            hour = field.data.hour
            if hour < 6 or hour > 22:
                raise ValidationError('Time must be between 6:00 AM and 10:00 PM')