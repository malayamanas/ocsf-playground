# START HERE - OCSF Playground with Claude CLI

Welcome! Your OCSF Playground has been updated to use Claude CLI for authentication. This is the simplest way to get started.

## Quick Setup (4 Steps)

### Step 1: Authenticate with Claude CLI
```bash
claude setup-token
```
This uses your Claude Code subscription automatically.

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
cd ../playground_frontend
npm install && npm run dev
```

**Open:** http://localhost:3000

Done!

## Documentation Map

| Need | File | Time |
|------|------|------|
| **What is this?** | README_CLAUDE_MIGRATION.md | 5 min |
| **Setup help** | QUICKSTART.md | 15 min |
| **Claude CLI details** | CLAUDE_CLI_AUTH_UPDATE.md | 10 min |
| **Architecture** | CLAUDE.md | 15 min |
| **Technical details** | MIGRATION_GUIDE.md | 20 min |
| **What changed** | CHANGES.md | 10 min |
| **Navigation** | MIGRATION_INDEX.md | 5 min |

## Authentication

**No API keys to manage!**

Just run:
```bash
claude setup-token
```

That's it. The app automatically detects your Claude Code subscription.

## Verification

### Test 1: Claude CLI
```bash
claude --version
```

### Test 2: Backend
```bash
curl http://127.0.0.1:8000/
```

### Test 3: Authentication
```bash
cd playground && pipenv run python3 << 'EOF'
from backend.core.claude_auth import ClaudeAuthentication
api_key = ClaudeAuthentication.get_api_key()
print("✓ Authentication successful!")
EOF
```

## Common Questions

**Q: Do I need an API key?**
A: No! Just run `claude setup-token`

**Q: Is Claude CLI required?**
A: No, you can use `ANTHROPIC_API_KEY` env var as fallback

**Q: What if I have the old API key setup?**
A: It still works! Both methods work side-by-side

**Q: Where's the docs?**
A: See the table above for all documentation

## Troubleshooting

### "claude command not found"
```bash
# Check if Claude CLI is installed
which claude
```

### "No Claude API key found"
```bash
# Run setup
claude setup-token

# Or use manual API key:
export ANTHROPIC_API_KEY="sk-ant-..."
```

See full troubleshooting in QUICKSTART.md

## Next Steps

1. **Setup:** Follow the 4 steps above
2. **Learn:** Read README_CLAUDE_MIGRATION.md
3. **Use:** Visit http://localhost:3000
4. **Reference:** Check docs as needed

## What You Can Do

- Generate regex patterns from logs
- Map logs to OCSF event classes
- Identify OCSF schema fields
- Extract and transform log data
- Create OCSF-compliant transformers

## Support

- **Setup issues:** QUICKSTART.md
- **Understand changes:** CLAUDE_CLI_AUTH_UPDATE.md
- **Technical details:** MIGRATION_GUIDE.md
- **Full navigation:** MIGRATION_INDEX.md

---

**Ready?** Run `claude setup-token` and follow Step 2 above!
