# Skileez Contract System Implementation

## Overview

This document describes the complete contract and payment system implementation for Skileez, a peer-to-peer learning marketplace. The system manages formal learning agreements between students and coaches, including session scheduling, payment tracking, and dispute resolution.

## 🏗️ Architecture

### Database Models

#### Core Models (Updated)

**LearningRequest** - Enhanced with contract-related fields:
- `preferred_times` (JSON) - Student's preferred time slots
- `sessions_needed` (Integer) - Number of sessions required
- `timeframe` (String) - Project timeline (e.g., "2 weeks")
- `skill_tags` (Text) - Comma-separated skill tags

**Proposal** - Enhanced with acceptance and payment fields:
- `accepted_at` (DateTime) - When proposal was accepted
- `accepted_terms` (JSON) - Accepted contract terms
- `availability_match` (Boolean) - Coach availability matches student preferences
- `approach_summary` (Text) - Coach's teaching approach
- `answers` (JSON) - Answers to screening questions
- `payment_model` (String) - 'per_session' or 'per_hour'
- `hourly_rate` (Float) - Hourly rate for per_hour model

**Session** - Enhanced with scheduling and reschedule fields:
- `scheduled_at` (DateTime) - Specific scheduling time
- `duration_minutes` (Integer) - Session duration
- `timezone` (String) - Session timezone
- `reschedule_requested` (Boolean) - Reschedule request status
- `reschedule_requested_by` (String) - Who requested reschedule
- `reschedule_reason` (Text) - Reason for reschedule
- `reschedule_deadline` (DateTime) - Response deadline
- `confirmed_by_coach` (Boolean) - Coach confirmation status

#### New Models

**Contract** - Formal learning agreement:
- `contract_number` (String) - Unique contract identifier
- `status` (String) - 'active', 'completed', 'cancelled', 'disputed'
- `start_date` (Date) - Contract start date
- `end_date` (Date) - Contract end date (optional)
- `total_sessions` (Integer) - Total sessions in contract
- `completed_sessions` (Integer) - Sessions completed
- `total_amount` (Numeric) - Total contract value
- `paid_amount` (Numeric) - Amount paid so far
- `payment_model` (String) - Payment structure
- `rate` (Numeric) - Per session or hourly rate
- `timezone` (String) - Contract timezone
- `cancellation_policy` (Text) - Cancellation terms
- `learning_outcomes` (Text) - Expected learning outcomes

**SessionPayment** - Payment tracking for Stripe integration:
- `amount` (Numeric) - Payment amount
- `status` (String) - 'pending', 'paid', 'failed', 'refunded'
- `stripe_payment_intent_id` (String) - Stripe payment intent
- `stripe_transfer_id` (String) - Stripe transfer ID
- `paid_at` (DateTime) - Payment timestamp

## 🔄 User Journey

### Student Journey
1. **Post Learning Request** - Create detailed learning request with preferences
2. **Review Proposals** - Evaluate coach proposals and approaches
3. **Accept Proposal** - Choose coach and accept proposal
4. **Create Contract** - Formalize learning agreement with terms
5. **Pay Upfront** - Pay entire contract amount via Stripe
6. **Schedule Sessions** - Coordinate session times with coach
7. **Attend Sessions** - Participate in video sessions
8. **Track Progress** - Monitor learning progress
9. **Complete Contract** - Rate and review coach

### Coach Journey
1. **Browse Requests** - Find matching learning opportunities
2. **Submit Proposal** - Create detailed proposal with approach
3. **Get Accepted** - Student accepts proposal
4. **Review Contract** - Accept or request contract modifications
5. **Receive Payment** - Get upfront payment via Stripe
6. **Sync Calendar** - Integrate with Google Calendar
7. **Conduct Sessions** - Lead video sessions with students
8. **Track Earnings** - Monitor contract payments
9. **Build Reputation** - Receive reviews and ratings

## 💰 Payment System

### Business Rules
- **Upfront Payment** - Students pay entire contract amount upfront
- **Escrow System** - Funds held securely until session completion
- **Platform Fee** - 15% fee (like Upwork)
- **Coach Payouts** - Automatic transfers after session completion

### Payment Flow
1. Student accepts proposal
2. Contract created with total amount
3. Student pays upfront via Stripe
4. Funds held in escrow
5. After each session completion, portion released to coach
6. Platform fee deducted from each payment

## 📅 Session Management

### Scheduling Rules
- **Reschedule Window** - 10 hours before session
- **Student Reschedule** - 24-hour notice required
- **Coach Reschedule** - 48-hour notice required
- **No-show Penalties** - Automatic penalties for missed sessions

### Session States
- `scheduled` - Session is scheduled
- `completed` - Session completed successfully
- `cancelled` - Session cancelled
- `missed` - Session missed without notice

## 📋 Contract Management

### Contract States
- `active` - Contract is active and sessions ongoing
- `completed` - All sessions completed
- `cancelled` - Contract cancelled
- `disputed` - Contract under dispute resolution

### Contract Features
- **Progress Tracking** - Visual progress indicators
- **Session Management** - Schedule and reschedule sessions
- **Payment Tracking** - Monitor payment status
- **Dispute Resolution** - Fair conflict resolution system

## 🛠️ Implementation Files

### Core Files
- `models.py` - Updated with all contract-related models and methods
- `migrations/versions/003_add_contract_system_fields.py` - Database migration
- `deploy_simple.py` - Enhanced deployment script
- `deploy_migrate_simple.py` - Simple migration runner
- `test_contract_system.py` - Comprehensive test suite

### Key Methods

#### Proposal Methods
```python
proposal.create_contract(**contract_data)  # Create contract from accepted proposal
proposal.get_contract()  # Get associated contract
proposal.get_upcoming_sessions()  # Get scheduled sessions
proposal.get_completed_sessions()  # Get completed sessions
```

#### Contract Methods
```python
contract.get_progress_percentage()  # Get completion percentage
contract.get_remaining_sessions()  # Get remaining sessions
contract.get_next_session()  # Get next scheduled session
contract.can_be_cancelled()  # Check if contract can be cancelled
contract.cancel()  # Cancel contract
```

#### Session Methods
```python
session.is_reschedule_allowed()  # Check reschedule eligibility
session.can_request_reschedule(user_role)  # Check user permissions
session.request_reschedule(requested_by, reason)  # Request reschedule
session.approve_reschedule(new_scheduled_at)  # Approve reschedule
session.mark_completed(notes, completed_by)  # Mark session complete
```

#### Utility Functions
```python
create_contract_from_proposal(proposal_id, **contract_data)  # Create contract
get_user_active_contracts(user_id, role)  # Get user's active contracts
get_user_upcoming_sessions(user_id, role)  # Get upcoming sessions
check_missed_sessions()  # Check for missed sessions (cron job)
```

## 🚀 Deployment

### Option 1: Simple Deployment
```bash
python deploy_simple.py
```

### Option 2: Migration-based Deployment
```bash
python deploy_migrate_simple.py
```

### Option 3: Alembic Migration
```bash
python -m alembic upgrade head
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_contract_system.py
```

The test suite verifies:
- User and profile creation
- Learning request and proposal creation
- Contract creation and management
- Session scheduling and operations
- Payment tracking
- Contract queries and utilities

## 📊 Database Schema

### New Tables
```sql
-- Contract table
CREATE TABLE contract (
    id SERIAL PRIMARY KEY,
    proposal_id INTEGER NOT NULL REFERENCES proposal(id),
    student_id INTEGER NOT NULL REFERENCES user(id),
    coach_id INTEGER NOT NULL REFERENCES user(id),
    contract_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    start_date DATE NOT NULL,
    end_date DATE,
    total_sessions INTEGER NOT NULL,
    completed_sessions INTEGER DEFAULT 0,
    total_amount NUMERIC(10,2) NOT NULL,
    paid_amount NUMERIC(10,2) DEFAULT 0.00,
    payment_model VARCHAR(20) NOT NULL,
    rate NUMERIC(10,2) NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC',
    cancellation_policy TEXT,
    learning_outcomes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Session payment table
CREATE TABLE session_payment (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES session(id),
    contract_id INTEGER NOT NULL REFERENCES contract(id),
    amount NUMERIC(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    stripe_payment_intent_id VARCHAR(255),
    stripe_transfer_id VARCHAR(255),
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### New Columns Added
- `learning_request`: preferred_times, sessions_needed, timeframe, skill_tags
- `proposal`: accepted_at, accepted_terms, availability_match, approach_summary, answers, payment_model, hourly_rate
- `session`: scheduled_at, duration_minutes, timezone, reschedule_requested, reschedule_requested_by, reschedule_reason, reschedule_deadline, confirmed_by_coach

## 🔐 Security Features

- **Contract Number Generation** - Unique, sequential contract numbers
- **Payment Security** - Stripe integration with escrow
- **Session Validation** - Reschedule rules and permissions
- **Data Integrity** - Foreign key constraints and validation

## 📈 Performance Optimizations

- **Database Indexes** - Optimized queries for contracts and payments
- **Efficient Queries** - Optimized relationship queries
- **Caching Ready** - Structure supports future caching implementation

## 🔮 Future Enhancements

### Phase 2 Features
- **Stripe Integration** - Complete payment processing
- **Google Calendar** - Calendar integration for scheduling
- **Video functionality has been removed from this application**
- **Dispute Resolution** - Automated dispute handling
- **Contract Extensions** - Ongoing learning relationships
- **Reviews & Ratings** - Quality assurance system

### Advanced Features
- **Automated Payouts** - Scheduled coach payments
- **Contract Templates** - Predefined contract terms
- **Analytics Dashboard** - Contract performance metrics
- **Mobile App** - Native mobile experience

## 📞 Support

For questions or issues with the contract system:
1. Check the test suite for examples
2. Review the model methods for usage patterns
3. Consult the database schema for structure
4. Run the deployment scripts for setup

The contract system provides a solid foundation for a professional learning marketplace with secure payments, flexible scheduling, and comprehensive tracking.
