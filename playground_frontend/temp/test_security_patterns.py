#!/usr/bin/env python3
"""
Security Pattern Detection and Severity Enhancement

This script processes acunetix.txt and detects:
- Local File Inclusion (LFI) patterns
- SQL Injection (SQLi) patterns

When detected, it elevates OCSF severity_id from 1 (Informational) to 4 (High)
"""
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Import the original transformer
sys.path.insert(0, str(Path(__file__).parent))
from trasform import transformer

# ============================================================================
# ATTACK PATTERN DEFINITIONS
# ============================================================================

LFI_PATTERNS = [
    '/etc/passwd',
    '/etc/shadow',
    '/proc/version',
    '/proc/self/environ',
    r'c:\\windows',
    'boot.ini',
    '../',
    '..%2f',
    '%2e%2e%2f',
    '%c0%af',
    'php://',
    'data://',
    'expect://',
    '%00',
    'null-byte'
]

SQLI_PATTERNS = [
    '1=1',
    '--',
    'or 1=1',
    'union select',
    'union all select',
    'waitfor delay',
    'pg_sleep(',
    'benchmark(',
    'sleep(',
    'into outfile',
    'load_file(',
    '@@version',
    'convert(',
    'cast(',
    '%27',
    '%22',
    "''",
    '""'
]

# ============================================================================
# OCSF SEVERITY LEVELS
# ============================================================================

SEVERITY_LEVELS = {
    'UNKNOWN': 0,
    'INFORMATIONAL': 1,
    'LOW': 2,
    'MEDIUM': 3,
    'HIGH': 4,
    'CRITICAL': 5,
    'FATAL': 6,
    'OTHER': 99
}

# ============================================================================
# PATTERN DETECTION FUNCTIONS
# ============================================================================

def detect_lfi(log_line: str) -> Tuple[bool, List[str]]:
    """
    Detect Local File Inclusion patterns in log line.

    Args:
        log_line: Raw log line to analyze

    Returns:
        Tuple of (detected: bool, matched_patterns: List[str])
    """
    matched = []
    log_lower = log_line.lower()

    for pattern in LFI_PATTERNS:
        # Case-insensitive search
        if pattern.lower() in log_lower:
            matched.append(pattern)

    return (len(matched) > 0, matched)


def detect_sqli(log_line: str) -> Tuple[bool, List[str]]:
    """
    Detect SQL Injection patterns in log line.

    Args:
        log_line: Raw log line to analyze

    Returns:
        Tuple of (detected: bool, matched_patterns: List[str])
    """
    matched = []
    log_lower = log_line.lower()

    for pattern in SQLI_PATTERNS:
        # Case-insensitive search
        if pattern.lower() in log_lower:
            matched.append(pattern)

    return (len(matched) > 0, matched)


def detect_attack_patterns(log_line: str) -> Dict[str, Any]:
    """
    Detect all attack patterns in a log line.

    Args:
        log_line: Raw log line to analyze

    Returns:
        Dictionary with detection results
    """
    lfi_detected, lfi_patterns = detect_lfi(log_line)
    sqli_detected, sqli_patterns = detect_sqli(log_line)

    attack_detected = lfi_detected or sqli_detected
    attack_types = []
    all_patterns = []

    if lfi_detected:
        attack_types.append('LFI')
        all_patterns.extend(lfi_patterns)

    if sqli_detected:
        attack_types.append('SQLi')
        all_patterns.extend(sqli_patterns)

    return {
        'attack_detected': attack_detected,
        'attack_types': attack_types,
        'matched_patterns': all_patterns,
        'lfi_detected': lfi_detected,
        'sqli_detected': sqli_detected
    }


# ============================================================================
# ENHANCED TRANSFORMER
# ============================================================================

def transform_with_security_detection(log_line: str) -> Dict[str, Any]:
    """
    Transform log line to OCSF format with security pattern detection.

    Elevates severity_id to 4 (HIGH) when attack patterns are detected.

    Args:
        log_line: Raw Apache/HTTP log line

    Returns:
        OCSF JSON dictionary with enhanced severity and attack metadata
    """
    # Get base OCSF transformation
    ocsf_event = transformer(log_line)

    # Detect attack patterns
    detection_result = detect_attack_patterns(log_line)

    # Enhance the OCSF event
    if detection_result['attack_detected']:
        # Elevate severity to HIGH
        ocsf_event['severity_id'] = SEVERITY_LEVELS['HIGH']

        # Add attack detection metadata
        if 'metadata' not in ocsf_event:
            ocsf_event['metadata'] = {}

        ocsf_event['metadata']['attack_detected'] = True
        ocsf_event['metadata']['attack_types'] = detection_result['attack_types']
        ocsf_event['metadata']['matched_patterns'] = detection_result['matched_patterns']

        # Add enrichment note
        ocsf_event['enrichments'] = [{
            'name': 'security_pattern_detection',
            'type': 'threat_intelligence',
            'value': f"Detected {', '.join(detection_result['attack_types'])} patterns"
        }]

    return ocsf_event, detection_result


# ============================================================================
# TEST HARNESS
# ============================================================================

def test_security_patterns():
    """
    Process acunetix.txt with security pattern detection.
    """
    input_file = Path(__file__).parent / 'acunetix.txt'
    output_file = Path(__file__).parent / 'output_with_security.json'
    report_file = Path(__file__).parent / 'security_detection_report.json'

    results = []
    statistics = {
        'total_lines': 0,
        'clean_lines': 0,
        'attack_lines': 0,
        'lfi_count': 0,
        'sqli_count': 0,
        'both_count': 0,
        'severity_elevated': 0,
        'attack_breakdown': {},
        'pattern_frequency': {}
    }

    print("=" * 80)
    print("Security Pattern Detection Test")
    print("=" * 80)
    print(f"\nScanning for:")
    print(f"  • LFI patterns: {len(LFI_PATTERNS)} signatures")
    print(f"  • SQLi patterns: {len(SQLI_PATTERNS)} signatures")
    print(f"\nProcessing {input_file.name}...")
    print("-" * 80)

    with open(input_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            statistics['total_lines'] += 1

            try:
                # Transform with security detection
                ocsf_event, detection = transform_with_security_detection(line)

                # Update statistics
                if detection['attack_detected']:
                    statistics['attack_lines'] += 1
                    statistics['severity_elevated'] += 1

                    if detection['lfi_detected'] and detection['sqli_detected']:
                        statistics['both_count'] += 1
                    elif detection['lfi_detected']:
                        statistics['lfi_count'] += 1
                    elif detection['sqli_detected']:
                        statistics['sqli_count'] += 1

                    # Track attack types
                    for attack_type in detection['attack_types']:
                        statistics['attack_breakdown'][attack_type] = \
                            statistics['attack_breakdown'].get(attack_type, 0) + 1

                    # Track pattern frequency
                    for pattern in detection['matched_patterns']:
                        statistics['pattern_frequency'][pattern] = \
                            statistics['pattern_frequency'].get(pattern, 0) + 1
                else:
                    statistics['clean_lines'] += 1

                # Store result
                results.append({
                    'line_number': line_num,
                    'input': line,
                    'output': ocsf_event,
                    'detection': detection
                })

                # Progress indicator
                if line_num % 100 == 0:
                    attacks = statistics['attack_lines']
                    clean = statistics['clean_lines']
                    print(f"  Line {line_num:5d}: {attacks:4d} attacks, {clean:4d} clean")

            except Exception as e:
                print(f"\n❌ ERROR on line {line_num}: {e}")
                continue

    # Calculate percentages
    total = statistics['total_lines']
    statistics['attack_percentage'] = (statistics['attack_lines'] / total * 100) if total > 0 else 0
    statistics['clean_percentage'] = (statistics['clean_lines'] / total * 100) if total > 0 else 0

    # Print Summary
    print("\n" + "=" * 80)
    print("DETECTION SUMMARY")
    print("=" * 80)
    print(f"\n📊 Overall Statistics:")
    print(f"  Total lines processed: {statistics['total_lines']:,}")
    print(f"  Clean lines: {statistics['clean_lines']:,} ({statistics['clean_percentage']:.1f}%)")
    print(f"  Attack lines: {statistics['attack_lines']:,} ({statistics['attack_percentage']:.1f}%)")
    print(f"  Severity elevated: {statistics['severity_elevated']:,}")

    print(f"\n🎯 Attack Type Breakdown:")
    print(f"  LFI only: {statistics['lfi_count']:,}")
    print(f"  SQLi only: {statistics['sqli_count']:,}")
    print(f"  Both LFI + SQLi: {statistics['both_count']:,}")

    if statistics['attack_breakdown']:
        print(f"\n🔍 Attack Category Distribution:")
        for attack_type, count in sorted(statistics['attack_breakdown'].items(),
                                        key=lambda x: x[1], reverse=True):
            percentage = (count / statistics['attack_lines'] * 100) if statistics['attack_lines'] > 0 else 0
            print(f"  {attack_type}: {count:,} ({percentage:.1f}%)")

    if statistics['pattern_frequency']:
        print(f"\n🔥 Top 10 Most Matched Patterns:")
        sorted_patterns = sorted(statistics['pattern_frequency'].items(),
                                key=lambda x: x[1], reverse=True)[:10]
        for pattern, count in sorted_patterns:
            print(f"  {count:4d}x  {pattern}")

    # Save outputs
    print(f"\n💾 Saving outputs...")

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  ✓ OCSF events: {output_file}")

    with open(report_file, 'w') as f:
        json.dump({
            'statistics': statistics,
            'top_patterns': sorted_patterns[:20] if statistics['pattern_frequency'] else [],
            'sample_attacks': [r for r in results if r['detection']['attack_detected']][:10]
        }, f, indent=2)
    print(f"  ✓ Detection report: {report_file}")

    # Show sample detections
    attack_samples = [r for r in results if r['detection']['attack_detected']][:3]
    if attack_samples:
        print("\n" + "=" * 80)
        print("SAMPLE ATTACK DETECTIONS")
        print("=" * 80)
        for idx, sample in enumerate(attack_samples, 1):
            print(f"\n[{idx}] Line {sample['line_number']}:")
            print(f"  Input: {sample['input'][:100]}...")
            print(f"  Attack Types: {', '.join(sample['detection']['attack_types'])}")
            print(f"  Patterns: {', '.join(sample['detection']['matched_patterns'][:5])}")
            print(f"  Original Severity: 1 (Informational)")
            print(f"  Elevated Severity: {sample['output']['severity_id']} (High)")

    print("\n" + "=" * 80)
    print("✅ COMPLETE")
    print("=" * 80)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    test_security_patterns()
