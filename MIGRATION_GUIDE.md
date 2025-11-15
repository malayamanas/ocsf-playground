# Claude API Migration Guide

This document explains the changes made to migrate from AWS Bedrock to Anthropic's Claude API.

## Overview

The OCSF Playground has been migrated from using AWS Bedrock to using the Anthropic Claude API. This allows you to use your existing Claude Code subscription instead of requiring AWS Bedrock credentials.

## What Changed

### 1. New Claude API Client Wrapper (`backend/core/claude_api_client.py`)

A new `ClaudeAPIRunnable` class wraps the Anthropic SDK and provides compatibility with LangChain's `Runnable` interface. This allows the rest of the codebase to continue working without major changes.

**Key features:**
- Implements LangChain's `Runnable` interface
- Supports tool binding via `bind_tools()`
- Handles message format conversion between LangChain and Anthropic formats
- Supports extended thinking mode (for entity analysis)
- Async support via `ainvoke()`

### 2. Updated Expert Definitions

All four expert modules were updated to use `ClaudeAPIRunnable` instead of `ChatBedrockConverse`:

**`backend/regex_expert/expert_def.py`**
- Uses `claude-3-5-sonnet-20241022`
- Temperature: 0 (deterministic regex generation)
- Extended thinking: disabled

**`backend/categorization_expert/expert_def.py`**
- Uses `claude-3-5-sonnet-20241022`
- Temperature: 0 (deterministic categorization)
- Extended thinking: disabled

**`backend/entities_expert/expert_def.py`**
- Analysis expert: `claude-3-7-sonnet-20250219` with extended thinking enabled
- Extraction expert: `claude-3-5-sonnet-20241022` without extended thinking
- Analysis temperature: 1 (required for extended thinking)
- Extraction temperature: 0

### 3. Dependency Changes

**Removed:**
- `boto3`
- `botocore`
- `langchain-aws`

**Added:**
- `anthropic`

**Kept:**
- `langchain` and `langchain-core` (for the `Runnable` interface and message types)

### 4. Configuration Changes

**AWS Configuration → Anthropic API Configuration**

Instead of AWS credentials, you now need an Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Get your API key from: https://console.anthropic.com

## Implementation Details

### Message Conversion

The `ClaudeAPIRunnable` converts between LangChain message formats and Anthropic API formats:

- `HumanMessage` → `{"role": "user", "content": "..."}`
- `AIMessage` → `{"role": "assistant", "content": "..."}`
- `SystemMessage` → Passed separately in the `system` parameter
- Tool calls are represented as content blocks with `type: "tool_use"`

### Tool Binding

Tools from the tool bundles are converted to Anthropic tool format:
```python
{
    "name": tool_name,
    "description": tool_description,
    "input_schema": tool_args_schema
}
```

### Extended Thinking

For the entity analysis expert, extended thinking is enabled:
- Budget: 30,000 tokens (configurable via `thinking_budget_tokens`)
- Used to improve accuracy of initial OCSF field mapping suggestions
- Temperature must be 1.0 when extended thinking is enabled (Anthropic requirement)

## Testing

To verify the migration works:

1. Set your API key:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key"
   ```

2. Test imports:
   ```bash
   cd playground
   pipenv run python3 -c "from backend.core.claude_api_client import ClaudeAPIRunnable; print('✓ Import successful')"
   ```

3. Start the backend:
   ```bash
   pipenv run python3 manage.py runserver
   ```

4. Test an endpoint:
   ```bash
   curl -X POST "http://127.0.0.1:8000/transformer/heuristic/create/" \
     -H "Content-Type: application/json" \
     -d '{"input_entry": "Failed password for invalid user from 192.168.1.1 port 22"}'
   ```

## Known Differences from Bedrock

1. **Model Names**: Anthropic model names are simpler (e.g., `claude-3-5-sonnet-20241022`) vs Bedrock's `us.anthropic.claude-3-7-sonnet-20250219-v1:0`

2. **Region Configuration**: No region selection needed. Anthropic API is globally available.

3. **Retry Configuration**: Handled by the Anthropic SDK automatically. The previous `DEFULT_BOTO_CONFIG` with boto retry configuration is no longer needed.

4. **Rate Limiting**: Anthropic API has its own rate limiting. Monitor your API usage at https://console.anthropic.com

5. **Extended Thinking**: Different parameter names and structure. Temperature must be 1.0 when enabled.

## Troubleshooting

### SSL Certificate Error

If you see SSL certificate verification errors during dependency installation:
```bash
PYTHONHTTPSVERIFY=0 pipenv install  # Not recommended for production
```

Or update Python's certificates:
```bash
/Applications/Python\ 3.13/Install\ Certificates.command
```

### API Key Not Found

If you get an error about missing ANTHROPIC_API_KEY:
```bash
export ANTHROPIC_API_KEY="your-key"
pipenv run python3 manage.py runserver
```

### Tool Use Errors

If tool calls aren't working, check the tool definitions in:
- `backend/regex_expert/tool_def.py`
- `backend/categorization_expert/tool_def.py`
- `backend/entities_expert/tool_def.py`

The tool schemas must have proper JSON schema format for Anthropic to parse them correctly.

## Future Improvements

1. **Error Handling**: Add better error handling for rate limits and authentication failures
2. **Token Counting**: Add token counting to track usage before hitting limits
3. **Streaming**: Implement streaming responses for long-running operations
4. **Model Configuration**: Make model selection configurable via environment variables
5. **Caching**: Consider caching OCSF schema requests to reduce latency

## References

- Anthropic API Documentation: https://docs.anthropic.com
- Claude Models: https://docs.anthropic.com/claude/reference/models-overview
- Extended Thinking: https://docs.anthropic.com/claude/guide/extended-thinking
