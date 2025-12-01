#!/usr/bin/env python3
"""Test different Anthropic authentication methods"""
import os
import sys

print("=" * 70)
print("Testing Anthropic SDK Authentication")
print("=" * 70)

# Test 1: Check current environment
print("\n1. Environment Variables:")
print("-" * 70)
anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
claude_oauth = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")

print(f"ANTHROPIC_API_KEY: {anthropic_key[:30] + '...' if anthropic_key else 'NOT SET'}")
print(f"CLAUDE_CODE_OAUTH_TOKEN: {claude_oauth[:30] + '...' if claude_oauth else 'NOT SET'}")

# Test 2: Try with no environment variables (rely on SDK default auth chain)
print("\n2. Test with SDK default authentication (no env vars):")
print("-" * 70)

# Temporarily clear the env vars
old_api_key = os.environ.pop("ANTHROPIC_API_KEY", None)
old_oauth = os.environ.pop("CLAUDE_CODE_OAUTH_TOKEN", None)

try:
    from anthropic import Anthropic

    print("Attempting to initialize Anthropic client with default auth chain...")
    client = Anthropic()

    # Try a simple API call
    print("Attempting a test API call...")
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=10,
        messages=[{"role": "user", "content": "Hi"}]
    )
    print("✅ SUCCESS! SDK default authentication works!")
    print(f"Response: {response.content[0].text}")

except Exception as e:
    print(f"❌ FAILED: {e}")

# Restore environment variables
if old_api_key:
    os.environ["ANTHROPIC_API_KEY"] = old_api_key
if old_oauth:
    os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = old_oauth

# Test 3: Try with CLAUDE_CODE_OAUTH_TOKEN as ANTHROPIC_API_KEY
if claude_oauth:
    print("\n3. Test with CLAUDE_CODE_OAUTH_TOKEN as ANTHROPIC_API_KEY:")
    print("-" * 70)

    try:
        os.environ["ANTHROPIC_API_KEY"] = claude_oauth
        from anthropic import Anthropic

        print("Attempting to initialize with OAuth token as API key...")
        client = Anthropic()

        print("Attempting a test API call...")
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print("✅ SUCCESS! OAuth token works as API key!")
        print(f"Response: {response.content[0].text}")

    except Exception as e:
        print(f"❌ FAILED: {e}")
        print("\nThis means CLAUDE_CODE_OAUTH_TOKEN is NOT a valid Anthropic API key.")

print("\n" + "=" * 70)
print("Conclusion:")
print("=" * 70)
print("""
You need ONE of the following:

Option 1: Get an Anthropic API key from https://console.anthropic.com
  - Sign up / login at console.anthropic.com
  - Create an API key
  - Set it: export ANTHROPIC_API_KEY="sk-ant-api03-..."

Option 2: Use Claude CLI authentication (if it has valid credentials)
  - The Anthropic SDK can use credentials from Claude CLI automatically
  - No need to set ANTHROPIC_API_KEY explicitly

Option 3: Contact Claude Code support to get a valid API key
  - The CLAUDE_CODE_OAUTH_TOKEN is for Claude Code CLI, not Anthropic API
""")
