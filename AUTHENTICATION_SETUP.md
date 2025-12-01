# Authentication Setup Guide

This guide shows you how to properly configure authentication for the OCSF Normalization Playground backend.

## Quick Start (Recommended)

The easiest way to set up authentication is to use a shell script that exports the environment variable before starting the server.

### Step 1: Create a startup script

```bash
# Navigate to the playground directory
cd /Users/apple/ocsf-playground/playground

# Create the startup script
cat > start_server.sh << 'EOF'
#!/bin/bash

# Export OAuth token for Claude Code
export CLAUDE_CODE_OAUTH_TOKEN="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"

# Verify the token is set
echo "✓ CLAUDE_CODE_OAUTH_TOKEN is set: ${CLAUDE_CODE_OAUTH_TOKEN:0:30}..."

# Start the Django server
echo "Starting Django server..."
pipenv run python3 manage.py runserver
EOF

# Make it executable
chmod +x start_server.sh
```

### Step 2: Run the startup script

```bash
# From the playground directory
./start_server.sh
```

You should see:
```
✓ CLAUDE_CODE_OAUTH_TOKEN is set: sk-ant-oat01-Hye9chwkivMJdfMSC...
Starting Django server...
```

---

## Alternative Methods

### Method 1: Export in Current Shell (Temporary)

This method sets the environment variable for the current terminal session only. You'll need to export it again if you close the terminal.

```bash
# Navigate to playground directory
cd /Users/apple/ocsf-playground/playground

# Export the OAuth token
export CLAUDE_CODE_OAUTH_TOKEN="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"

# Verify it's set
echo "Token set: ${CLAUDE_CODE_OAUTH_TOKEN:0:30}..."

# Start the server IN THE SAME TERMINAL
pipenv run python3 manage.py runserver
```

**Important:** The `export` command and `pipenv run` must be executed in the **same terminal session**.

---

### Method 2: Using .env File with python-dotenv

Create a `.env` file in the playground directory and configure Django to load it.

#### Step 1: Install python-dotenv

```bash
cd /Users/apple/ocsf-playground
pipenv install python-dotenv
```

#### Step 2: Create .env file

```bash
cd playground
cat > .env << 'EOF'
# Claude Code OAuth Token
CLAUDE_CODE_OAUTH_TOKEN=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
EOF

# Secure the file (important!)
chmod 600 .env
```

#### Step 3: Update Django settings

Add this to the top of `playground/settings.py` (after imports):

```python
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')
```

#### Step 4: Add .env to .gitignore

```bash
echo ".env" >> .gitignore
```

Now you can start the server normally:
```bash
cd playground
pipenv run python3 manage.py runserver
```

---

### Method 3: Using Shell Profile (Persistent)

This sets the environment variable permanently in your shell profile. **Note:** This exposes your token in your shell config file.

#### For Bash (~/.bash_profile or ~/.bashrc):

```bash
echo 'export CLAUDE_CODE_OAUTH_TOKEN="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"' >> ~/.bash_profile

# Reload the profile
source ~/.bash_profile
```

#### For Zsh (~/.zshrc):

```bash
echo 'export CLAUDE_CODE_OAUTH_TOKEN="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"' >> ~/.zshrc

# Reload the profile
source ~/.zshrc
```

Now the variable will be available in all new terminal sessions.

---

### Method 4: Inline Environment Variable

Run the server with the environment variable set inline (one-time, no persistence):

```bash
cd /Users/apple/ocsf-playground/playground

CLAUDE_CODE_OAUTH_TOKEN="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" pipenv run python3 manage.py runserver
```

---

## Verifying Authentication

After starting the server with any of the above methods, check the logs:

```bash
cd /Users/apple/ocsf-playground/playground
tail -f logs/*.log | grep -E "(CLAUDE_CODE|authentication|OAuth)"
```

You should see:
```
[INFO] backend: Using CLAUDE_CODE_OAUTH_TOKEN from environment variable
[INFO] backend: ✓ Claude authentication verified
[INFO] backend: Initialized Claude API client with OAuth token
```

If you see `ANTHROPIC_API_KEY` instead, it means that variable is set and taking precedence. Unset it:
```bash
unset ANTHROPIC_API_KEY
```

---

## Testing the Setup

Run the authentication test script:

```bash
cd /Users/apple/ocsf-playground/playground

# Make sure the environment variable is set first
export CLAUDE_CODE_OAUTH_TOKEN="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"

# Run the test
pipenv run python3 test_auth.py
```

Expected output:
```
============================================================
Environment Variables Check
============================================================
ANTHROPIC_API_KEY: NOT SET
CLAUDE_CODE_OAUTH_TOKEN: sk-ant-oat01-Hye9chw...

============================================================
Testing claude_auth.py
============================================================

✓ Will use CLAUDE_CODE_OAUTH_TOKEN: sk-ant-oat01-Hye9chwkivMJdfM...

✓ Anthropic client initialized successfully
```

---

## Troubleshooting

### Issue: "Environment variable not set" error

**Cause:** The environment variable was exported in a different terminal session.

**Solution:** Export the variable in the same terminal where you run `pipenv run python3 manage.py runserver`.

---

### Issue: "invalid x-api-key" 401 error

**Cause 1:** `ANTHROPIC_API_KEY` is set to an invalid value and taking precedence.

**Solution:**
```bash
unset ANTHROPIC_API_KEY
export CLAUDE_CODE_OAUTH_TOKEN="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"
```

**Cause 2:** Old server process still running with old code.

**Solution:** Kill all Django processes and restart:
```bash
# Find and kill Django processes
pkill -f "manage.py runserver"

# Wait a moment, then start fresh
./start_server.sh
```

---

### Issue: Backend logs show "ANTHROPIC_API_KEY from environment variable"

**Cause:** You have `ANTHROPIC_API_KEY` set, which takes precedence over `CLAUDE_CODE_OAUTH_TOKEN`.

**Solution:**
```bash
# Unset the ANTHROPIC_API_KEY
unset ANTHROPIC_API_KEY

# Verify it's unset
echo $ANTHROPIC_API_KEY  # Should print nothing

# Restart the server
./start_server.sh
```

---

### Issue: Changes not taking effect

**Cause:** Old Python processes still running with cached code.

**Solution:**
```bash
# Kill all Django/Python processes
pkill -f "manage.py runserver"
pkill -f "python3"

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Restart
./start_server.sh
```

---

## Security Best Practices

1. **Never commit tokens to Git:**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   echo "start_server.sh" >> .gitignore  # If it contains your token
   ```

2. **Secure .env file permissions:**
   ```bash
   chmod 600 .env
   ```

3. **Use environment-specific tokens:** Don't use production tokens in development.

4. **Rotate tokens regularly:** If a token is exposed, rotate it immediately.

---

## Recommended Setup for Development

**Use the startup script method (Method from Quick Start):**

Pros:
- ✅ Simple to use
- ✅ Token not in shell history (if you create the file with an editor)
- ✅ Easy to restart server
- ✅ Can be added to .gitignore

Cons:
- ❌ Token stored in plaintext file (secure with `chmod 600`)
- ❌ Need to remember to run the script

**Or use .env file method:**

Pros:
- ✅ Standard practice in Python/Django projects
- ✅ Works with multiple environment variables
- ✅ Can be templated (.env.example)

Cons:
- ❌ Requires python-dotenv dependency
- ❌ Must modify Django settings

Choose the method that fits your workflow best!
