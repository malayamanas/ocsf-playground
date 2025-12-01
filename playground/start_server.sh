#!/bin/bash

# OCSF Playground Django Server Startup Script
# This script ensures the OAuth token is set before starting the server

echo "========================================="
echo "OCSF Playground Server Startup"
echo "========================================="

# Set the Claude Code OAuth token as ANTHROPIC_API_KEY
# The Anthropic SDK accepts OAuth tokens via this environment variable
export ANTHROPIC_API_KEY="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"

# Verify the token is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ERROR: ANTHROPIC_API_KEY is not set!"
    exit 1
else
    echo "✅ ANTHROPIC_API_KEY is set (OAuth token): ${ANTHROPIC_API_KEY:0:30}..."
fi

echo ""
echo "Killing any existing Django server processes..."
pkill -f "manage.py runserver" 2>/dev/null || true
sleep 1

echo ""
echo "Starting Django server..."
echo "========================================="

# Start the Django server
pipenv run python3 manage.py runserver
