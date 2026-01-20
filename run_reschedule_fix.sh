#!/bin/bash

# Script to fix the reschedule_proposed_time column issue on production
# This script can be run on Render or any production environment

echo "🚀 Starting reschedule column fix for production..."
echo "=================================================="

# Check if we're in a production environment
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL environment variable not set"
    echo "This script should be run in a production environment"
    exit 1
fi

echo "✅ Production environment detected"

# Run the Python migration script
echo "🔄 Running database migration..."
python deploy_reschedule_fix.py

if [ $? -eq 0 ]; then
    echo "✅ Migration completed successfully!"
    echo "The reschedule system should now work properly."
else
    echo "❌ Migration failed!"
    exit 1
fi
