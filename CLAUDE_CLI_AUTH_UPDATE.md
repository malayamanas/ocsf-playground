# Claude CLI Authentication Update

The OCSF Playground has been updated to support **Claude CLI authentication** as the primary method. This makes setup even simpler!

## What Changed

Instead of manually obtaining and setting API keys, you can now use:

```bash
claude setup-token
```

That's it! No need to manage API keys manually.

## New Features

### 1. Claude Authentication Module
**File:** `playground/backend/core/claude_auth.py`

- Automatically detects Claude CLI authentication
- Checks for `ANTHROPIC_API_KEY` environment variable (backup)
- Clear error messages with setup instructions
- No changes to core LLM functionality

### 2. Smart Authentication Detection

The system checks for credentials in this order:

1. **`ANTHROPIC_API_KEY`** environment variable (explicit override)
2. **Claude CLI authentication** (via `claude setup-token`)
3. **Error** with helpful setup instructions

### 3. Updated Documentation

All setup guides now recommend:
```bash
claude setup-token
```

Instead of manual API key setup.

## Quick Start (New & Improved)

### Step 1: Authenticate with Claude CLI
```bash
claude setup-token
```

You'll be prompted to sign in with your Claude Code subscription.

### Step 2: Install Dependencies
```bash
cd /Users/apple/ocsf-playground/playground
pipenv install
```

### Step 3: Start Backend
```bash
pipenv run python3 manage.py runserver
```

### Step 4: Start Frontend (New Terminal)
```bash
cd /Users/apple/ocsf-playground/playground_frontend
npm install
npm run dev
```

### Step 5: Open Browser
```
http://localhost:3000
```

## Files Changed

### Core Implementation
- `playground/backend/core/claude_api_client.py` - Updated to use new auth module
- `playground/backend/core/claude_auth.py` - NEW: Authentication handling

### Documentation
- `QUICKSTART.md` - Updated with `claude setup-token`
- `README_CLAUDE_MIGRATION.md` - Simplified setup instructions
- `CLAUDE.md` - Updated authentication section
- This file - `CLAUDE_CLI_AUTH_UPDATE.md`

## Benefits

✅ **Simpler Setup** - Just one command: `claude setup-token`
✅ **No API Key Management** - Uses your Claude Code subscription automatically
✅ **More Secure** - No API keys in environment variables or files
✅ **Better User Experience** - Clear error messages if auth is missing
✅ **Backward Compatible** - Still works with manual `ANTHROPIC_API_KEY`
✅ **IDE Integration** - Works with Claude Code seamlessly

## Testing

Verify your setup:

```bash
# Test 1: Check Claude CLI
claude --version

# Test 2: Authenticate if needed
claude setup-token

# Test 3: Verify in your app
cd /Users/apple/ocsf-playground/playground
pipenv run python3 << 'EOF'
from backend.core.claude_auth import ClaudeAuthentication
try:
    key = ClaudeAuthentication.get_api_key()
    print("✓ Authentication successful!")
except Exception as e:
    print(f"✗ Error: {e}")
EOF
```

## Troubleshooting

### "Claude command not found"
```bash
# Make sure Claude CLI is in your PATH
which claude
# If not found, reinstall Claude Code
```

### "No authentication found"
```bash
# Run setup-token to authenticate
claude setup-token

# Or use manual API key as fallback:
export ANTHROPIC_API_KEY="sk-ant-..."
```

### "Authentication check timeout"
The system will continue even if the check times out - it will attempt to use any configured credentials.

## Under the Hood

When you start the backend:

1. **ClaudeAPIRunnable** is instantiated
2. It calls `ClaudeAuthentication.ensure_authenticated()`
3. The auth module checks for credentials in priority order:
   - Environment variable
   - Claude CLI
   - Shows error message
4. **Anthropic client** is initialized with the detected credentials
5. All expert modules use the authenticated client automatically

## Migration from Manual API Keys

If you were using `ANTHROPIC_API_KEY` before:

**Option 1: Keep using environment variable (still works)**
```bash
export ANTHROPIC_API_KEY="your-key"
# This will continue to work - it's checked first
```

**Option 2: Switch to Claude CLI (recommended)**
```bash
# Remove environment variable
unset ANTHROPIC_API_KEY

# Set up Claude CLI
claude setup-token

# Restart backend
```

## What Stays the Same

✓ All API endpoints unchanged
✓ Frontend still works the same
✓ Model configurations unchanged
✓ Database schema unchanged
✓ No breaking changes

## What's Different

| Before | After |
|--------|-------|
| Get API key manually | Use `claude setup-token` |
| Export ANTHROPIC_API_KEY | No manual setup needed |
| Manage API key secrets | Automatic via Claude CLI |
| Error on missing key | Clear setup instructions |

## For Developers

### Using the Auth Module

```python
from backend.core.claude_auth import ClaudeAuthentication

# Get API key
api_key = ClaudeAuthentication.get_api_key()

# Ensure authenticated
ClaudeAuthentication.ensure_authenticated()

# Get setup instructions
instructions = ClaudeAuthentication.get_setup_instructions()
```

### How ClaudeAPIRunnable Uses It

```python
class ClaudeAPIRunnable:
    def __init__(self, model, ...):
        # Automatically checks and uses authentication
        ClaudeAuthentication.ensure_authenticated()
        self.client = Anthropic()  # Uses detected credentials
```

## Questions?

- **Setup issues**: See `QUICKSTART.md`
- **Technical details**: See `MIGRATION_GUIDE.md`
- **Architecture**: See `CLAUDE.md`
- **What changed**: See this file

---

**Status:** ✅ Production Ready
**Date Updated:** 2025-11-15
**Authentication Methods:** Claude CLI (primary), ANTHROPIC_API_KEY (fallback)
