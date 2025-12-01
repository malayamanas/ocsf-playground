#!/usr/bin/env python3
"""Test authentication configuration"""
import os
import sys

# Add the playground directory to the path
sys.path.insert(0, '/Users/apple/ocsf-playground/playground')

print("=" * 60)
print("Environment Variables Check")
print("=" * 60)

anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
claude_oauth = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")

print(f"ANTHROPIC_API_KEY: {anthropic_api_key[:20] + '...' if anthropic_api_key else 'NOT SET'}")
print(f"CLAUDE_CODE_OAUTH_TOKEN: {claude_oauth[:20] + '...' if claude_oauth else 'NOT SET'}")

print("\n" + "=" * 60)
print("Testing claude_auth.py")
print("=" * 60)

from backend.core.claude_auth import ClaudeAuthentication

try:
    api_key, auth_token = ClaudeAuthentication.get_credentials()
    print(f"\nReturned API Key: {api_key[:20] + '...' if api_key else 'None'}")
    print(f"Returned Auth Token: {auth_token[:20] + '...' if auth_token else 'None'}")

    if api_key:
        print(f"\n✓ Will use ANTHROPIC_API_KEY: {api_key[:30]}...")
    elif auth_token:
        print(f"\n✓ Will use CLAUDE_CODE_OAUTH_TOKEN: {auth_token[:30]}...")

except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "=" * 60)
print("Testing Anthropic Client")
print("=" * 60)

try:
    from anthropic import Anthropic

    if api_key:
        print(f"\nInitializing with api_key parameter...")
        client = Anthropic(api_key=api_key)
        print(f"✓ Client created with API key")
    elif auth_token:
        print(f"\nInitializing with auth_token parameter...")
        client = Anthropic(auth_token=auth_token)
        print(f"✓ Client created with OAuth token")
    else:
        print(f"\nInitializing with default (no params)...")
        client = Anthropic()
        print(f"✓ Client created with default auth")

    print(f"\n✓ Anthropic client initialized successfully")

except Exception as e:
    print(f"\n✗ Failed to initialize Anthropic client: {e}")

print("\n" + "=" * 60)
