# Quick Start Guide - Using Your Claude Code Subscription

This guide shows you how to get the OCSF Playground running with your Claude Code subscription API key.

## Prerequisites

- Python 3.13+
- Node.js 20+ / npm 10+
- Anthropic API key from https://console.anthropic.com

## Step 1: Authenticate with Claude CLI

The easiest way is to use your Claude Code subscription via the Claude CLI:

```bash
# Set up Claude CLI authentication
claude setup-token
```

This will prompt you to authenticate with your Claude Code subscription.

**Alternative: Manual API Key (Optional)**

If you prefer to set the API key manually instead of using Claude CLI:

```bash
# Option A: Set environment variable
export ANTHROPIC_API_KEY="sk-ant-xxx..."

# Option B: Create .env file in repo root
echo "ANTHROPIC_API_KEY=sk-ant-xxx..." > /Users/apple/ocsf-playground/.env

# Option C: Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export ANTHROPIC_API_KEY="sk-ant-xxx..."' >> ~/.bashrc
source ~/.bashrc
```

## Step 2: Install Backend Dependencies

```bash
cd /Users/apple/ocsf-playground

# Install Python dependencies (one-time)
pipenv install

# Verify installation
pipenv run python3 -c "from anthropic import Anthropic; print('✓ Anthropic SDK installed')"
```

## Step 3: Start the Backend

```bash
cd /Users/apple/ocsf-playground/playground

# Start Django development server
pipenv run python3 manage.py runserver

# You should see: "Starting development server at http://127.0.0.1:8000/"
```

The backend is now running at http://127.0.0.1:8000

## Step 4: Install Frontend Dependencies (New Terminal)

```bash
cd /Users/apple/ocsf-playground/playground_frontend

npm install
```

## Step 5: Start the Frontend

```bash
cd /Users/apple/ocsf-playground/playground_frontend

npm run dev

# You should see: "Ready in X.XXs"
```

The frontend is now running at http://localhost:3000

## Step 6: Open the Application

Open your web browser and navigate to: **http://localhost:3000**

You should see the OCSF Normalization Playground interface!

## Testing Your Setup

### Test 1: Claude CLI Authentication
```bash
# Verify Claude CLI is set up
claude --version

# If not authenticated yet, run:
claude setup-token
```

### Test 2: Backend is Running
```bash
curl http://127.0.0.1:8000/schema.json
# Should return a 404 (that's OK, it means the server is running)
```

### Test 3: Authentication is Working
```bash
cd /Users/apple/ocsf-playground/playground
pipenv run python3 << 'EOF'
from backend.core.claude_auth import ClaudeAuthentication
try:
    api_key = ClaudeAuthentication.get_api_key()
    print("✓ Authentication configured!")
    print(f"  Using: {'Claude CLI' if api_key == 'claude-cli-authenticated' else 'Manual API key'}")
except Exception as e:
    print(f"✗ Authentication error: {e}")
EOF
```

### Test 4: Claude API Works
```bash
curl -X POST "http://127.0.0.1:8000/transformer/heuristic/create/" \
  -H "Content-Type: application/json" \
  -d '{
    "input_entry": "2025-11-15 10:30:45 Failed password for invalid user guest from 192.168.1.100 port 22"
  }'
```

You should get back a response with a generated regex pattern (may take a few seconds).

## Example Workflow

1. **Import Logs**: Click "Import Logs" and paste some sample logs:
   ```
   Thu Mar 12 2025 07:40:57 mailsv1 sshd[4351]: Failed password for invalid user guest from 86.212.199.60 port 3771 ssh2
   Thu Mar 12 2025 07:40:57 mailsv1 sshd[2716]: Failed password for invalid user postgres from 86.212.199.60 port 4093 ssh2
   ```

2. **Get Heuristic (Regex)**: Click the "Analyze Heuristic" button to generate a regex pattern

3. **Categorize**: Click "Analyze Category" to map to an OCSF Event Class (e.g., Authentication)

4. **Extract Entities**: Click "Analyze Entities" to identify OCSF fields

5. **Generate Transformer**: Click "Generate" to create the final transformation logic

## Monitoring

### Backend Logs
```bash
tail -f /Users/apple/ocsf-playground/playground/logs/backend.info.log
```

### Frontend Console
Open browser DevTools (F12) and check the Console tab for any errors

## Troubleshooting

### "No Claude API key found" or "Authentication error"
```bash
# First, authenticate with Claude CLI:
claude setup-token

# This will prompt you to sign in with your Claude Code subscription

# Verify it's working:
claude --version

# If you already have an API key, you can also set it manually:
export ANTHROPIC_API_KEY="your-api-key"

# Restart the backend
pipenv run python3 manage.py runserver
```

### "Connection refused" error
- Make sure backend is running on port 8000
- Make sure frontend is running on port 3000
- Check for port conflicts: `lsof -i :8000` and `lsof -i :3000`

### "Tool call failed" or LLM errors
- Check that your API key is valid
- Check your API usage at https://console.anthropic.com
- Check backend logs: `tail -f ./logs/backend.debug.log`

### Slow responses
- Extended thinking analysis is slow by design (provides better results)
- Check API rate limits at https://console.anthropic.com/account/billing/overview

## Stopping the Services

**Backend:**
```bash
# In the backend terminal, press Ctrl+C
```

**Frontend:**
```bash
# In the frontend terminal, press Ctrl+C
```

## Next Steps

- Read [CLAUDE.md](./CLAUDE.md) for architecture and development guidance
- Read [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for technical details on the Bedrock→Claude migration
- Check [README.md](./README.md) for original project documentation

## Useful Resources

- **Anthropic Console**: https://console.anthropic.com
- **API Documentation**: https://docs.anthropic.com
- **Model Information**: https://docs.anthropic.com/claude/reference/models-overview
- **Rate Limits**: Check your account at https://console.anthropic.com/account/billing/overview

---

**Questions?** Check the logs or review the migration guide for more details!
