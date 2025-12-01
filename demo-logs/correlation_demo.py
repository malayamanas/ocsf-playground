#!/usr/bin/env python3
"""
OCSF Event Correlation Demo
Demonstrates how OCSF standardized fields enable simple event correlation

Usage:
    python3 correlation_demo.py
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict


# Sample OCSF events from Scenario 6 (Zero-Day)
SAMPLE_EVENTS = [
    {
        "event_id": 1,
        "time": "2025-12-01T03:12:43.567Z",
        "class_name": "System Activity",
        "activity_name": "Application Crash",
        "device": {"hostname": "PENTAGON-LOGISTICS-12.defense.mil"},
        "process": {
            "pid": 4628,
            "file": {"name": "DefenseTrack.exe", "path": "C:\\Program Files\\DefenseTrack\\DefenseTrack.exe"}
        },
        "actor": {"user": {"name": "DEFENSE\\logistics.admin"}},
        "error": {"code": "0xc0000374", "message": "Heap corruption"}
    },
    {
        "event_id": 2,
        "time": "2025-12-01T03:12:44.890Z",
        "class_name": "File Activity",
        "activity_name": "File Created",
        "device": {"hostname": "PENTAGON-LOGISTICS-12.defense.mil"},
        "process": {"pid": 4628, "file": {"name": "DefenseTrack.exe"}},
        "file": {
            "name": "msvcr120_compat.dll",
            "path": "C:\\Windows\\Temp\\msvcr120_compat.dll",
            "hash": {"sha256": "A9B8C7D6E5F4A3B2C1D0E9F8A7B6C5D4E3F2A1B0C9D8E7F6A5B4C3D2E1F0A9B8"}
        },
        "actor": {"user": {"name": "DEFENSE\\logistics.admin"}}
    },
    {
        "event_id": 3,
        "time": "2025-12-01T03:12:45.123Z",
        "class_name": "Process Activity",
        "activity_name": "DLL Loaded",
        "device": {"hostname": "PENTAGON-LOGISTICS-12.defense.mil"},
        "process": {"pid": 4628, "file": {"name": "DefenseTrack.exe"}},
        "file": {
            "name": "msvcr120_compat.dll",
            "hash": {"sha256": "A9B8C7D6E5F4A3B2C1D0E9F8A7B6C5D4E3F2A1B0C9D8E7F6A5B4C3D2E1F0A9B8"}
        },
        "actor": {"user": {"name": "DEFENSE\\logistics.admin"}}
    },
    {
        "event_id": 4,
        "time": "2025-12-01T03:12:45.234Z",
        "class_name": "Process Activity",
        "activity_name": "Process Tampering",
        "device": {"hostname": "PENTAGON-LOGISTICS-12.defense.mil"},
        "process": {"pid": 4628, "file": {"name": "DefenseTrack.exe"}},
        "actor": {"user": {"name": "DEFENSE\\logistics.admin"}}
    },
    {
        "event_id": 5,
        "time": "2025-12-01T03:12:45.456Z",
        "class_name": "Process Activity",
        "activity_name": "Remote Thread Created",
        "device": {"hostname": "PENTAGON-LOGISTICS-12.defense.mil"},
        "process": {
            "pid": 4628,
            "file": {"name": "DefenseTrack.exe"},
            "target_process": {"pid": 1892, "file": {"name": "svchost.exe"}}
        },
        "actor": {"user": {"name": "DEFENSE\\logistics.admin"}}
    },
    {
        "event_id": 6,
        "time": "2025-12-01T03:12:45.567Z",
        "class_name": "Security Finding",
        "activity_name": "Malware Detected",
        "device": {"hostname": "PENTAGON-LOGISTICS-12.defense.mil"},
        "process": {"file": {"name": "DefenseTrack.exe"}},
        "malware": {
            "name": "Exploit:Win64/CVE-2025-XXXXX.A!dha",
            "classification": "Exploit"
        },
        "file": {
            "path": "C:\\Windows\\Temp\\msvcr120_compat.dll",
            "hash": {"sha256": "A9B8C7D6E5F4A3B2C1D0E9F8A7B6C5D4E3F2A1B0C9D8E7F6A5B4C3D2E1F0A9B8"}
        },
        "actor": {"user": {"name": "DEFENSE\\logistics.admin"}}
    },
    {
        "event_id": 7,
        "time": "2025-12-01T03:12:46.789Z",
        "class_name": "Process Activity",
        "activity_name": "Process Created",
        "device": {"hostname": "PENTAGON-LOGISTICS-12.defense.mil"},
        "process": {
            "pid": 7824,
            "file": {"name": "cmd.exe", "path": "C:\\Windows\\System32\\cmd.exe"},
            "cmd_line": 'cmd.exe /c "whoami /priv && net localgroup administrators DEFENSE\\logistics.admin /add"',
            "parent_process": {"pid": 1892, "file": {"name": "svchost.exe"}}
        },
        "actor": {"user": {"name": "NT AUTHORITY\\SYSTEM"}}
    },
    {
        "event_id": 8,
        "time": "2025-12-01T03:12:47.123Z",
        "class_name": "Group Management",
        "activity_name": "User Added to Group",
        "device": {"hostname": "PENTAGON-LOGISTICS-12.defense.mil"},
        "group": {"name": "Administrators"},
        "user": {"name": "DEFENSE\\logistics.admin"},
        "actor": {"user": {"name": "NT AUTHORITY\\SYSTEM"}}
    },
    {
        "event_id": 9,
        "time": "2025-12-01T03:13:00.456Z",
        "class_name": "Network Activity",
        "activity_name": "Network Connection",
        "device": {"hostname": "PENTAGON-LOGISTICS-12.defense.mil"},
        "src_endpoint": {"ip": "10.45.67.12", "port": 53892},
        "dst_endpoint": {
            "ip": "45.141.215.89",
            "port": 443,
            "hostname": "cdn.windowsupdates-verification.com"
        },
        "process": {"pid": 7824, "file": {"name": "rundll32.exe"}},
        "actor": {"user": {"name": "NT AUTHORITY\\SYSTEM"}}
    },
    {
        "event_id": 10,
        "time": "2025-12-01T03:12:48.123Z",
        "class_name": "System Activity",
        "activity_name": "Registry Modified",
        "device": {"hostname": "PENTAGON-LOGISTICS-12.defense.mil"},
        "process": {"pid": 5124, "file": {"name": "reg.exe"}},
        "registry": {
            "key": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\WindowsUpdateService"
        },
        "actor": {"user": {"name": "DEFENSE\\logistics.admin"}}
    }
]


def get_nested_field(obj: Dict, field_path: str) -> Any:
    """Get nested field value using dot notation (e.g., 'actor.user.name')"""
    parts = field_path.split('.')
    value = obj
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return None
    return value


def correlate_by_field(events: List[Dict], field_path: str) -> Dict[Any, List[Dict]]:
    """
    Group events by a specific OCSF field value

    Args:
        events: List of OCSF events
        field_path: Dot-notation path to field (e.g., 'process.pid')

    Returns:
        Dict mapping field values to lists of events
    """
    groups = defaultdict(list)

    for event in events:
        value = get_nested_field(event, field_path)
        if value:
            groups[value].append(event)

    return dict(groups)


def correlate_by_time_window(events: List[Dict], window_seconds: int = 300) -> List[List[Dict]]:
    """
    Group events within time windows

    Args:
        events: List of OCSF events
        window_seconds: Time window in seconds (default: 5 minutes)

    Returns:
        List of event groups (each group is a list of events)
    """
    events_sorted = sorted(events, key=lambda e: e['time'])

    groups = []
    current_group = []
    window_start = None

    for event in events_sorted:
        event_time = datetime.fromisoformat(event['time'].replace('Z', '+00:00'))

        if not window_start:
            window_start = event_time
            current_group = [event]
        elif event_time <= window_start + timedelta(seconds=window_seconds):
            current_group.append(event)
        else:
            groups.append(current_group)
            window_start = event_time
            current_group = [event]

    if current_group:
        groups.append(current_group)

    return groups


def build_process_tree(events: List[Dict]) -> Dict[int, Dict]:
    """
    Build process tree from OCSF Process Activity events

    Returns:
        Dict mapping PIDs to process info with children
    """
    processes = {}

    for event in events:
        if event.get('class_name') == 'Process Activity' and 'process' in event:
            proc = event['process']
            if 'pid' not in proc:
                continue

            pid = proc['pid']
            parent_pid = get_nested_field(proc, 'parent_process.pid')

            processes[pid] = {
                'pid': pid,
                'name': proc.get('file', {}).get('name', 'Unknown'),
                'cmd_line': proc.get('cmd_line', ''),
                'user': get_nested_field(event, 'actor.user.name') or '',
                'time': event['time'],
                'parent_pid': parent_pid,
                'children': [],
                'event': event
            }

    # Link children to parents
    for pid, proc in processes.items():
        if proc['parent_pid'] and proc['parent_pid'] in processes:
            processes[proc['parent_pid']]['children'].append(pid)

    return processes


def render_process_tree(processes: Dict, root_pid: int, indent: int = 0) -> str:
    """Render process tree as ASCII art"""
    if root_pid not in processes:
        return ""

    proc = processes[root_pid]
    output = f"{'  ' * indent}└─ [PID {proc['pid']}] {proc['name']} (User: {proc['user']})\n"

    if proc['cmd_line']:
        cmd_preview = proc['cmd_line'][:70] + ('...' if len(proc['cmd_line']) > 70 else '')
        output += f"{'  ' * indent}   Command: {cmd_preview}\n"

    for child_pid in proc['children']:
        output += render_process_tree(processes, child_pid, indent + 1)

    return output


def print_section(title: str):
    """Print section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def main():
    print("\n" + "=" * 80)
    print("  OCSF EVENT CORRELATION DEMONSTRATION")
    print("  Scenario 6: Zero-Day Memory Corruption Attack")
    print("=" * 80)

    print(f"\nTotal Events: {len(SAMPLE_EVENTS)}")
    print(f"Time Range: {SAMPLE_EVENTS[0]['time']} to {SAMPLE_EVENTS[-1]['time']}")
    print(f"Device: {SAMPLE_EVENTS[0]['device']['hostname']}")

    # =========================================================================
    # Correlation 1: By Process ID
    # =========================================================================
    print_section("Correlation #1: Events by Process ID")

    pid_groups = correlate_by_field(SAMPLE_EVENTS, 'process.pid')

    for pid, events in sorted(pid_groups.items()):
        print(f"\n  Process PID {pid}: {len(events)} events")
        for event in events:
            print(f"    └─ {event['time']}: {event['activity_name']} ({event['class_name']})")

    # =========================================================================
    # Correlation 2: By User
    # =========================================================================
    print_section("Correlation #2: Events by User")

    user_groups = correlate_by_field(SAMPLE_EVENTS, 'actor.user.name')

    for user, events in user_groups.items():
        print(f"\n  User: {user} ({len(events)} events)")
        for event in events:
            activity_desc = event['activity_name']
            if 'file' in event and 'name' in event['file']:
                activity_desc += f" → {event['file']['name']}"
            print(f"    └─ {event['time']}: {activity_desc}")

    # =========================================================================
    # Correlation 3: By File Hash (IOC)
    # =========================================================================
    print_section("Correlation #3: Events by File Hash (IOC)")

    hash_groups = correlate_by_field(SAMPLE_EVENTS, 'file.hash.sha256')

    for file_hash, events in hash_groups.items():
        if file_hash:
            print(f"\n  File Hash: {file_hash[:16]}... ({len(events)} events)")
            for event in events:
                file_name = get_nested_field(event, 'file.name') or 'Unknown'
                print(f"    └─ {event['time']}: {event['activity_name']} ({file_name})")

    # =========================================================================
    # Correlation 4: By Network IOC (C2 IP)
    # =========================================================================
    print_section("Correlation #4: Events by Network IOC (C2 IP)")

    c2_events = [e for e in SAMPLE_EVENTS if get_nested_field(e, 'dst_endpoint.ip')]

    if c2_events:
        for event in c2_events:
            c2_ip = get_nested_field(event, 'dst_endpoint.ip')
            c2_hostname = get_nested_field(event, 'dst_endpoint.hostname')
            print(f"\n  Connection to C2: {c2_ip} ({c2_hostname})")
            print(f"    └─ Time: {event['time']}")
            print(f"    └─ Process: {get_nested_field(event, 'process.file.name')}")
            print(f"    └─ User: {get_nested_field(event, 'actor.user.name')}")
    else:
        print("  No network connections found")

    # =========================================================================
    # Correlation 5: Process Tree Reconstruction
    # =========================================================================
    print_section("Correlation #5: Process Tree Reconstruction")

    processes = build_process_tree(SAMPLE_EVENTS)

    # Find root processes (no parent or parent not in tree)
    root_pids = [
        pid for pid, proc in processes.items()
        if not proc['parent_pid'] or proc['parent_pid'] not in processes
    ]

    print("  Process Execution Tree:\n")
    for root_pid in root_pids:
        print(render_process_tree(processes, root_pid))

    # =========================================================================
    # Correlation 6: Time Window Analysis
    # =========================================================================
    print_section("Correlation #6: Time Window Analysis (5-minute windows)")

    time_groups = correlate_by_time_window(SAMPLE_EVENTS, window_seconds=300)

    for i, group in enumerate(time_groups, 1):
        start_time = group[0]['time']
        end_time = group[-1]['time']
        print(f"\n  Window #{i}: {start_time} to {end_time}")
        print(f"  Events: {len(group)}")
        for event in group:
            print(f"    └─ {event['time']}: {event['activity_name']}")

    # =========================================================================
    # Attack Summary
    # =========================================================================
    print_section("Attack Chain Summary")

    print("  Timeline of Attack Events:\n")
    for event in sorted(SAMPLE_EVENTS, key=lambda e: e['time']):
        print(f"  {event['time']} - {event['activity_name']}")

        # Add context
        if 'error' in event:
            print(f"    └─ Error: {event['error']['message']}")
        if 'file' in event and 'name' in event['file']:
            print(f"    └─ File: {event['file']['name']}")
        if 'malware' in event:
            print(f"    └─ Malware: {event['malware']['name']}")
        if 'dst_endpoint' in event:
            print(f"    └─ C2: {event['dst_endpoint']['ip']}")
        if 'group' in event:
            print(f"    └─ Group: {event['group']['name']}")

    # =========================================================================
    # Key Findings
    # =========================================================================
    print_section("Key Correlation Findings")

    print("  ✓ All events correlated by:")
    print(f"    • Device: PENTAGON-LOGISTICS-12.defense.mil")
    print(f"    • Primary User: DEFENSE\\logistics.admin")
    print(f"    • Primary Process: PID 4628 (DefenseTrack.exe)")
    print(f"    • Malicious IOC: msvcr120_compat.dll (SHA256: A9B8C7D6...)")
    print(f"    • C2 Server: 45.141.215.89 (cdn.windowsupdates-verification.com)")
    print(f"    • Attack Duration: ~17 seconds (03:12:43 - 03:13:00)")

    print("\n  ✓ Attack Chain:")
    print("    1. Application crash (heap corruption)")
    print("    2. Malicious DLL created and loaded")
    print("    3. Process injection into svchost.exe")
    print("    4. Privilege escalation (cmd.exe as SYSTEM)")
    print("    5. User added to Administrators group")
    print("    6. C2 beacon established")
    print("    7. Persistence via registry modification")

    print("\n  ✓ OCSF Enabled Correlation:")
    print("    • Standard field names across all events")
    print("    • Process tree reconstruction (parent-child relationships)")
    print("    • Time-based grouping (all within 17 seconds)")
    print("    • IOC tracking (file hash, C2 IP)")
    print("    • User activity tracking (compromised account)")

    print("\n" + "=" * 80)
    print("  Correlation Complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
