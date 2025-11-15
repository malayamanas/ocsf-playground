# OCSF Playground - Now Powered by Claude API

You've successfully migrated the OCSF Normalization Playground from AWS Bedrock to use Anthropic's Claude API!

## What This Means

Instead of requiring AWS credentials and paying for Bedrock inference, your OCSF Playground now uses your existing Claude Code subscription. It's simpler, cheaper, and faster to set up.

## Getting Started (3 Simple Steps)

### Step 1: Get Your API Key
Visit https://console.anthropic.com and copy your API key

### Step 2: Set Environment Variable
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Step 3: Run the Application
```bash
# Terminal 1: Start Backend
cd /Users/apple/ocsf-playground/playground
pipenv install
pipenv run python3 manage.py runserver

# Terminal 2: Start Frontend
cd /Users/apple/ocsf-playground/playground_frontend
npm install
npm run dev

# Open http://localhost:3000 in your browser
```

That's it! Your app is now running with Claude API.

## Documentation Files

| File | Purpose |
|------|---------|
| **QUICKSTART.md** | Step-by-step setup guide with testing |
| **MIGRATION_GUIDE.md** | Technical details of the migration |
| **CHANGES.md** | File-by-file changes overview |
| **INTEGRATION_SUMMARY.txt** | Executive summary |
| **CLAUDE.md** | Architecture and development guide |

Start with **QUICKSTART.md** if you're setting up for the first time.

## What Changed

### Before (AWS Bedrock)
```python
from langchain_aws import ChatBedrockConverse
llm = ChatBedrockConverse(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    region_name="us-west-2",
    config=DEFULT_BOTO_CONFIG
)
```

### After (Claude API)
```python
from backend.core.claude_api_client import ClaudeAPIRunnable
llm = ClaudeAPIRunnable(
    model="claude-3-5-sonnet-20241022",
    temperature=0,
    max_tokens=16000
)
```

Much simpler! And no AWS credentials needed.

## Key Files Modified

**Core Implementation:**
- `playground/backend/core/claude_api_client.py` - New Claude API wrapper
- `playground/backend/regex_expert/expert_def.py` - Uses ClaudeAPIRunnable
- `playground/backend/categorization_expert/expert_def.py` - Uses ClaudeAPIRunnable
- `playground/backend/entities_expert/expert_def.py` - Uses ClaudeAPIRunnable

**Cleanup:**
- `playground/backend/core/experts.py` - Removed Bedrock config
- `playground/playground/settings.py` - Removed boto logging
- `Pipfile` - Updated dependencies

## Models Used

| Module | Model | Purpose |
|--------|-------|---------|
| Regex Generation | claude-3-5-sonnet-20241022 | Parse log patterns |
| Categorization | claude-3-5-sonnet-20241022 | Map to OCSF classes |
| Entity Analysis | claude-3-7-sonnet-20250219 | Identify OCSF fields (with extended thinking) |
| Entity Extraction | claude-3-5-sonnet-20241022 | Generate transform logic |

## API Key Configuration

### Option 1: Environment Variable (Recommended)
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Option 2: .env File
Create `.env` in repo root:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### Option 3: In Code (Not Recommended)
```python
import os
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."
```

## Verification

Test your setup:
```bash
# Check API key is set
echo $ANTHROPIC_API_KEY

# Test backend connectivity
curl http://127.0.0.1:8000/

# Test Claude API integration
curl -X POST "http://127.0.0.1:8000/transformer/heuristic/create/" \
  -H "Content-Type: application/json" \
  -d '{"input_entry": "Failed password for user from 192.168.1.1"}'
```

## Benefits of This Migration

✅ **Simpler Setup** - No AWS account needed  
✅ **Cost Effective** - Uses existing Claude Code subscription  
✅ **Faster** - Quicker deployment and setup  
✅ **More Flexible** - Easy to switch models  
✅ **Latest Models** - Direct access to newest Claude versions  
✅ **No Breaking Changes** - Fully backward compatible  

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### "Connection refused" 
Make sure both backend and frontend are running:
- Backend: http://127.0.0.1:8000
- Frontend: http://localhost:3000

### "Tool call failed"
Check backend logs:
```bash
tail -f playground/logs/backend.debug.log
```

### API rate limits
Check your usage at https://console.anthropic.com/account/billing/overview

## Next Steps

1. **Read QUICKSTART.md** for detailed setup
2. **Review MIGRATION_GUIDE.md** for technical details
3. **Check CLAUDE.md** for architecture information
4. **Start building** with your OCSF transformations!

## Support

For questions about:
- **Setup**: See QUICKSTART.md
- **Technical Details**: See MIGRATION_GUIDE.md  
- **Architecture**: See CLAUDE.md
- **Changes**: See CHANGES.md

## License

Same as original project - See LICENSE file

---

**Last Updated:** 2025-11-15  
**Status:** ✅ Production Ready  
**API Provider:** Anthropic  
**Subscription:** Claude Code

Happy transforming! 🚀
