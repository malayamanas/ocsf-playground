#!/usr/bin/env python3
"""Test Claude CLI integration"""
import sys
sys.path.insert(0, '/Users/apple/ocsf-playground/playground')

from backend.core.claude_cli_client import ClaudeCLIRunnable
from langchain_core.messages import HumanMessage

print("=" * 70)
print("Testing Claude CLI Integration")
print("=" * 70)

# Test 1: Simple prompt
print("\n1. Testing simple prompt:")
print("-" * 70)

try:
    client = ClaudeCLIRunnable(model="claude-3-5-sonnet-20241022")

    response = client.invoke([
        HumanMessage(content="Say 'Hello from Claude CLI!' and nothing else.")
    ])

    print(f"✅ SUCCESS!")
    print(f"Response: {response.content}")

except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("If you see '✅ SUCCESS!' above, the CLI integration is working!")
print("=" * 70)
