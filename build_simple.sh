#!/bin/bash

echo "🚀 Starting simplified build process..."

# Check if we're in a production environment
if [ -n "$DATABASE_URL" ]; then
    echo "🔌 Production environment detected"
    echo "Running deployment checks..."
    
    # Run the deployment fix script
    python deploy_fix.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Deployment checks completed successfully"
    else
        echo "💥 Deployment checks failed"
        echo "⚠️ Continuing with build anyway..."
    fi
else
    echo "⚠️ Local development environment - skipping checks"
fi

echo "✅ Build process completed"
