#!/usr/bin/env python3
"""Test regex expert with CLI client"""
import sys
sys.path.insert(0, '/Users/apple/ocsf-playground/playground')

from backend.regex_expert.expert_def import get_regex_expert, invoke_regex_expert
from backend.regex_expert.task_def import RegexTask
from backend.regex_expert.parameters import RegexFlavor

print("=" * 70)
print("Testing Regex Expert with Claude CLI")
print("=" * 70)

# Test input
test_log = '192.168.1.1 - - [01/Jan/2024:12:00:00 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"'

print(f"\nInput log:\n{test_log}")
print("\n" + "-" * 70)

try:
    # Create regex expert
    expert = get_regex_expert(RegexFlavor.JAVASCRIPT)
    print("✓ Created regex expert")

    # Create task
    task = RegexTask(
        input_entry=test_log,
        existing_heuristic="",
        user_guidance=""
    )
    print("✓ Created task")

    # Invoke expert
    print("\nCalling Claude CLI...")
    result = invoke_regex_expert(expert, task)

    print("\n" + "=" * 70)
    print("SUCCESS!")
    print("=" * 70)
    print(f"\nGenerated Regex:\n{result.new_heuristic}")
    print(f"\nRationale:\n{result.rationale[:200]}...")

except Exception as e:
    print(f"\n✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
