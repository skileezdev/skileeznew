-- MVP Contract and Scheduling System Migration
-- Add new fields to support enhanced job posting, contract management, and scheduling

-- Add new fields to LearningRequest table
ALTER TABLE learning_request ADD COLUMN IF NOT EXISTS preferred_times TEXT;
ALTER TABLE learning_request ADD COLUMN IF NOT EXISTS sessions_needed INTEGER;
ALTER TABLE learning_request ADD COLUMN IF NOT EXISTS timeframe VARCHAR(100);
ALTER TABLE learning_request ADD COLUMN IF NOT EXISTS skill_tags VARCHAR(500);

-- Add new fields to Proposal table (contract management)
ALTER TABLE proposal ADD COLUMN IF NOT EXISTS accepted_at TIMESTAMP;
ALTER TABLE proposal ADD COLUMN IF NOT EXISTS accepted_terms TEXT;
ALTER TABLE proposal ADD COLUMN IF NOT EXISTS availability_match BOOLEAN DEFAULT FALSE;
ALTER TABLE proposal ADD COLUMN IF NOT EXISTS approach_summary TEXT;
ALTER TABLE proposal ADD COLUMN IF NOT EXISTS answers TEXT;
ALTER TABLE proposal ADD COLUMN IF NOT EXISTS payment_model VARCHAR(20) DEFAULT 'per_session';
ALTER TABLE proposal ADD COLUMN IF NOT EXISTS hourly_rate FLOAT;

-- Add new fields to Session table (enhanced scheduling)
ALTER TABLE session ADD COLUMN IF NOT EXISTS duration_minutes INTEGER;
ALTER TABLE session ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC';
ALTER TABLE session ADD COLUMN IF NOT EXISTS reschedule_requested BOOLEAN DEFAULT FALSE;
ALTER TABLE session ADD COLUMN IF NOT EXISTS reschedule_requested_by VARCHAR(20);
ALTER TABLE session ADD COLUMN IF NOT EXISTS reschedule_reason TEXT;
ALTER TABLE session ADD COLUMN IF NOT EXISTS confirmed_by_coach BOOLEAN DEFAULT FALSE;
ALTER TABLE session ADD COLUMN IF NOT EXISTS reschedule_deadline TIMESTAMP;

-- Update existing sessions to have duration_minutes if not set
UPDATE session SET duration_minutes = 60 WHERE duration_minutes IS NULL;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_proposal_accepted_at ON proposal(accepted_at);
CREATE INDEX IF NOT EXISTS idx_proposal_status ON proposal(status);
CREATE INDEX IF NOT EXISTS idx_session_scheduled_date ON session(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_session_status ON session(status);
CREATE INDEX IF NOT EXISTS idx_session_reschedule_deadline ON session(reschedule_deadline);

-- Add comments for documentation
COMMENT ON COLUMN learning_request.preferred_times IS 'JSON string of preferred learning times';
COMMENT ON COLUMN learning_request.sessions_needed IS 'Number of sessions needed for the learning request';
COMMENT ON COLUMN learning_request.timeframe IS 'Timeframe for learning (e.g., "Learn video editing in 1 month")';
COMMENT ON COLUMN learning_request.skill_tags IS 'Comma-separated skill tags';

COMMENT ON COLUMN proposal.accepted_at IS 'When proposal was accepted (becomes contract)';
COMMENT ON COLUMN proposal.accepted_terms IS 'JSON string of contract terms';
COMMENT ON COLUMN proposal.availability_match IS 'Coach confirms availability for the job';
COMMENT ON COLUMN proposal.approach_summary IS 'Teaching approach for this specific job';
COMMENT ON COLUMN proposal.answers IS 'JSON string of screening question answers';
COMMENT ON COLUMN proposal.payment_model IS 'Payment model: per_session or per_hour';
COMMENT ON COLUMN proposal.hourly_rate IS 'Optional hourly rate for per_hour payment model';

COMMENT ON COLUMN session.duration_minutes IS 'Session duration in minutes';
COMMENT ON COLUMN session.timezone IS 'Session timezone';
COMMENT ON COLUMN session.reschedule_requested IS 'Whether a reschedule has been requested';
COMMENT ON COLUMN session.reschedule_requested_by IS 'Who requested the reschedule: student or coach';
COMMENT ON COLUMN session.reschedule_reason IS 'Reason for reschedule request';
COMMENT ON COLUMN session.confirmed_by_coach IS 'Whether coach has confirmed the session';
COMMENT ON COLUMN session.reschedule_deadline IS 'Deadline for reschedule approval';
