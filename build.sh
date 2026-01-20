#!/bin/bash

echo "🚀 Starting build process..."

# Check if we're in a production environment
if [ -n "$DATABASE_URL" ]; then
    echo "🔌 Production environment detected"
    echo "Running database migration..."
    
    # Run the Python migration script
    python build.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Database migration completed successfully"
    else
        echo "💥 Database migration failed"
        exit 1
    fi
else
    echo "⚠️ Local development environment - skipping migration"
fi

echo "✅ Build process completed"
