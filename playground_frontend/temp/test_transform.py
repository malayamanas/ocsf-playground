#!/usr/bin/env python3
"""
Test script to process acunetix.txt through transform.py
Analyzes failures and reports issues
"""
import sys
import json
import traceback
from pathlib import Path

# Import the transformer
sys.path.insert(0, str(Path(__file__).parent))
from trasform import transformer

def test_transformation():
    """Process each line and collect results"""

    input_file = Path(__file__).parent / "acunetix.txt"
    output_file = Path(__file__).parent / "output.json"
    error_file = Path(__file__).parent / "errors.txt"

    results = []
    errors = []
    line_num = 0

    print("=" * 80)
    print("Testing transform.py against acunetix.txt")
    print("=" * 80)

    with open(input_file, 'r') as f:
        for line in f:
            line_num += 1
            line = line.strip()

            if not line:
                continue

            try:
                # Transform the line
                result = transformer(line)
                results.append({
                    "line_number": line_num,
                    "input": line,
                    "output": result
                })

                # Print progress every 100 lines
                if line_num % 100 == 0:
                    print(f"Processed {line_num} lines successfully...")

            except Exception as e:
                error_info = {
                    "line_number": line_num,
                    "input": line,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
                errors.append(error_info)
                print(f"\n❌ ERROR on line {line_num}:")
                print(f"   Input: {line[:100]}...")
                print(f"   Error: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total lines processed: {line_num}")
    print(f"Successful transformations: {len(results)}")
    print(f"Failed transformations: {len(errors)}")
    print(f"Success rate: {len(results)/line_num*100:.2f}%")

    # Save successful results
    if results:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Successful results saved to: {output_file}")

    # Save errors
    if errors:
        with open(error_file, 'w') as f:
            json.dump(errors, f, indent=2)
        print(f"✗ Error details saved to: {error_file}")

        # Analyze error patterns
        print("\n" + "=" * 80)
        print("ERROR ANALYSIS")
        print("=" * 80)

        error_types = {}
        for error in errors:
            error_msg = error["error"]
            if error_msg in error_types:
                error_types[error_msg] += 1
            else:
                error_types[error_msg] = 1

        print("\nError frequency by type:")
        for error_msg, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {count}x: {error_msg}")

        # Show first error in detail
        if errors:
            print("\n" + "=" * 80)
            print("FIRST ERROR DETAIL")
            print("=" * 80)
            first_error = errors[0]
            print(f"Line {first_error['line_number']}:")
            print(f"Input: {first_error['input']}")
            print(f"\n{first_error['traceback']}")

    return len(errors) == 0

if __name__ == "__main__":
    success = test_transformation()
    sys.exit(0 if success else 1)
