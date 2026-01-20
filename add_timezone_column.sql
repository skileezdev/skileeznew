-- Add timezone column to user table
-- Run this script manually in your database to add the timezone column

ALTER TABLE "user" ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';

-- Update existing users to have UTC timezone
UPDATE "user" SET timezone = 'UTC' WHERE timezone IS NULL;

-- Add a comment to the column
COMMENT ON COLUMN "user".timezone IS 'User timezone preference for displaying dates and times';
