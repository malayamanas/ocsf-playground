# Single-System Event Correlation with OCSF

## 🎯 The Real Requirement

**Problem:** On a single endpoint, Sysmon generates thousands of events. You need to:
- ✅ Correlate events by **same username**
- ✅ Correlate events by **same IP address**
- ✅ Correlate events by **same hostname**
- ✅ Correlate events by **parent/child/sibling process IDs**
- ✅ Correlate events by **specific IOC** (file hash, domain, etc.)
- ✅ Within a **short time window** (e.g., 5 minutes)

**Solution:** OCSF provides standardized fields that make this trivial.

---

## 🏗️ How OCSF Enables This

### **The Problem Without OCSF**

**Scenario 6 (Zero-Day) has 10 events. Let's try to correlate them manually:**

```xml
<!-- Event 1: DLL Load -->
<Data Name="ProcessId">4628</Data>
<Data Name="User">DEFENSE\logistics.admin</Data>

<!-- Event 2: Remote Thread -->
<Data Name="SourceProcessId">4628</Data>
<Data Name="TargetProcessId">1892</Data>

<!-- Event 3: Defender Detection -->
<Data Name="Process Name">C:\Program Files\DefenseTrack\DefenseTrack.exe</Data>
<Data Name="Detection User">DEFENSE\logistics.admin</Data>

<!-- Event 4: Privilege Escalation -->
<Data Name="NewProcessId">0x1E88</Data>  <!-- HEX! -->
<Data Name="ParentProcessId">0x2234</Data>
```

❌ **Problems:**
- Different field names: `ProcessId` vs `SourceProcessId` vs `NewProcessId`
- Different formats: Decimal (4628) vs Hex (0x1E88)
- Need to manually map relationships

---

### **The Solution With OCSF**

All events transformed to OCSF have **standard fields**:

```json
{
  "process.pid": 4628,
  "process.parent_process.pid": 1892,
  "actor.user.name": "DEFENSE\\logistics.admin",
  "device.hostname": "PENTAGON-LOGISTICS-12.defense.mil",
  "src_endpoint.ip": "10.45.67.12",
  "file.hash.sha256": "A9B8C7D6E5F4...",
  "time": "2025-12-01T03:12:45.123Z"
}
```

✅ **Now correlation is simple:**
- Same process? Match `process.pid`
- Parent-child? Match `process.parent_process.pid` → `process.pid`
- Same user? Match `actor.user.name`
- Same IOC? Match `file.hash.sha256`
- Time window? Filter by `time`

---

## 📊 Practical Example: Correlating Scenario 6 Events

### **Attack Chain (Zero-Day Memory Corruption)**

Let's correlate the 10 events from `scenario6-zero-day-memory-corruption.xml`:

| Event | Type | Key OCSF Fields |
|-------|------|-----------------|
| **1** | Application Crash | `process.pid=4628`, `actor.user.name=logistics.admin` |
| **2** | Malicious DLL Created | `process.pid=4628`, `file.name=msvcr120_compat.dll` |
| **3** | DLL Loaded | `process.pid=4628`, `file.hash.sha256=A9B8C7D6...` |
| **4** | Process Tampering | `process.pid=4628` |
| **5** | Remote Thread Injection | `process.pid=4628`, `target_process.pid=1892` |
| **6** | Defender Alert | `process.file.path=DefenseTrack.exe`, `actor.user.name=logistics.admin` |
| **7** | Privilege Escalation | `process.parent_process.pid=1892`, `process.pid=7824` |
| **8** | Admin Group Add | `actor.user.name=logistics.admin` |
| **9** | C2 Connection | `process.pid=7824`, `dst_endpoint.ip=45.141.215.89` |
| **10** | Persistence (Registry) | `process.pid=5124`, `actor.user.name=logistics.admin` |

---

## 🔗 Correlation Techniques

### **1. Correlation by Process ID**

**Find all events related to malicious process (PID 4628):**

```sql
SELECT * FROM ocsf_events
WHERE
    device.hostname = 'PENTAGON-LOGISTICS-12.defense.mil'
    AND (
        process.pid = 4628
        OR process.parent_process.pid = 4628
        OR process.target_process.pid = 4628
    )
    AND time BETWEEN '2025-12-01 03:12:00' AND '2025-12-01 03:13:00'
ORDER BY time ASC
```

**Results:**
```
03:12:43.567 - Application Crash (process.pid=4628)
03:12:44.890 - File Created (process.pid=4628) → msvcr120_compat.dll
03:12:45.123 - DLL Loaded (process.pid=4628) → Unsigned DLL
03:12:45.234 - Process Tampering (process.pid=4628)
03:12:45.456 - Remote Thread (process.pid=4628 → target=1892)
```

**Insight:** All 5 events are part of the same exploit chain!

---

### **2. Correlation by User**

**Find all actions by compromised user:**

```sql
SELECT
    time,
    class_name,
    process.file.name,
    process.cmd_line,
    file.name
FROM ocsf_events
WHERE
    actor.user.name = 'DEFENSE\\logistics.admin'
    AND device.hostname = 'PENTAGON-LOGISTICS-12.defense.mil'
    AND time >= '2025-12-01 03:12:00'
ORDER BY time ASC
```

**Results:**
```
03:12:43 - Application Crash - DefenseTrack.exe
03:12:45 - DLL Load - DefenseTrack.exe → msvcr120_compat.dll
03:12:45 - Defender Alert - DefenseTrack.exe (User: logistics.admin)
03:12:47 - Admin Group Add - cmd.exe (Added logistics.admin to Administrators)
03:19:15 - Registry Persistence - reg.exe (User: logistics.admin)
```

**Insight:** The `logistics.admin` account was compromised and used throughout the attack!

---

### **3. Correlation by Parent-Child Process Tree**

**Reconstruct full process tree:**

```python
def build_process_tree(ocsf_events, root_pid):
    """
    Build hierarchical process tree from OCSF events
    """
    tree = {}

    # Index all processes
    for event in ocsf_events:
        if event.get('class_name') == 'Process Activity':
            pid = event['process']['pid']
            parent_pid = event['process'].get('parent_process', {}).get('pid')

            tree[pid] = {
                'process': event['process'],
                'parent_pid': parent_pid,
                'time': event['time'],
                'children': []
            }

    # Build parent-child relationships
    for pid, node in tree.items():
        if node['parent_pid'] and node['parent_pid'] in tree:
            tree[node['parent_pid']]['children'].append(pid)

    # Render tree
    def render_tree(pid, indent=0):
        if pid not in tree:
            return []

        node = tree[pid]
        result = [
            f"{'  ' * indent}└─ PID {pid}: {node['process']['file']['name']} "
            f"({node['time']}) - {node['process'].get('cmd_line', '')[:50]}"
        ]

        for child_pid in node['children']:
            result.extend(render_tree(child_pid, indent + 1))

        return result

    return '\n'.join(render_tree(root_pid))

# Example output:
"""
└─ PID 1892: svchost.exe (03:12:45.456) - C:\Windows\System32\svchost.exe -k netsvcs -p
  └─ PID 7824: cmd.exe (03:12:46.789) - cmd.exe /c "whoami /priv && net localgroup..."
    └─ PID 8912: rundll32.exe (03:13:00.456) - (C2 beacon)
"""
```

**Insight:** The attack escalated from svchost → cmd.exe → rundll32.exe!

---

### **4. Correlation by IOC (File Hash)**

**Find all events involving malicious DLL:**

```sql
SELECT
    time,
    class_name,
    device.hostname,
    process.file.name,
    file.path,
    file.hash.sha256
FROM ocsf_events
WHERE
    file.hash.sha256 = 'A9B8C7D6E5F4A3B2C1D0E9F8A7B6C5D4E3F2A1B0C9D8E7F6A5B4C3D2E1F0A9B8'
    AND time >= '2025-12-01 03:00:00'
ORDER BY time ASC
```

**Results:**
```
03:12:44.890 - File Activity - msvcr120_compat.dll created
03:12:45.123 - Process Activity - msvcr120_compat.dll loaded by DefenseTrack.exe
03:12:45.567 - Security Finding - Defender detected DLL (quarantine failed)
```

**Insight:** Same malicious DLL appears in 3 different event types!

---

### **5. Correlation by Network IOC (IP Address)**

**Find all network connections to C2 server:**

```sql
SELECT
    time,
    src_endpoint.ip,
    src_endpoint.port,
    dst_endpoint.ip,
    dst_endpoint.hostname,
    process.file.name,
    actor.user.name
FROM ocsf_events
WHERE
    class_name = 'Network Activity'
    AND dst_endpoint.ip = '45.141.215.89'
    AND device.hostname = 'PENTAGON-LOGISTICS-12.defense.mil'
ORDER BY time ASC
```

**Results:**
```
03:13:00.456 - rundll32.exe → 45.141.215.89:443 (User: SYSTEM)
03:15:23.789 - rundll32.exe → 45.141.215.89:443 (User: SYSTEM) [2nd beacon]
03:18:45.123 - rundll32.exe → 45.141.215.89:443 (User: SYSTEM) [3rd beacon]
```

**Insight:** Regular C2 beacons every ~3 minutes!

---

## 🎬 Real-World Correlation: Scenario 6 Attack Chain

### **Automated Correlation Rule**

Here's a **Splunk correlation rule** that automatically links all 10 events:

```spl
index=ocsf
device.hostname="PENTAGON-LOGISTICS-12.defense.mil"
earliest="2025-12-01T03:12:00" latest="2025-12-01T03:15:00"

| eval correlation_key = coalesce(
    process.pid,
    process.parent_process.pid,
    process.target_process.pid
)

| eval correlation_user = actor.user.name
| eval correlation_ioc = coalesce(
    file.hash.sha256,
    dst_endpoint.ip
)

| stats
    values(time) as event_times,
    values(class_name) as event_types,
    values(process.file.name) as processes,
    values(process.cmd_line) as commands,
    values(file.name) as files,
    values(dst_endpoint.ip) as c2_ips,
    count as event_count
    BY correlation_key, correlation_user, correlation_ioc, device.hostname

| where event_count >= 3

| eval alert_severity = case(
    event_count >= 5, "CRITICAL",
    event_count >= 3, "HIGH",
    1=1, "MEDIUM"
)

| eval attack_summary =
    "Detected " . event_count . " related events on " . device.hostname .
    " involving process PID " . correlation_key .
    " and user " . correlation_user

| table
    device.hostname,
    correlation_user,
    correlation_key,
    event_count,
    alert_severity,
    event_types,
    processes,
    files,
    c2_ips,
    attack_summary
```

**Output:**
```
device.hostname: PENTAGON-LOGISTICS-12.defense.mil
correlation_user: DEFENSE\logistics.admin
correlation_key: 4628
event_count: 10
alert_severity: CRITICAL
event_types: [Application Error, File Activity, Process Activity, Security Finding, Network Activity, Authentication]
processes: [DefenseTrack.exe, cmd.exe, rundll32.exe, reg.exe, vssadmin.exe]
files: [msvcr120_compat.dll, credentials.txt]
c2_ips: [45.141.215.89]
attack_summary: Detected 10 related events on PENTAGON-LOGISTICS-12.defense.mil involving process PID 4628 and user DEFENSE\logistics.admin
```

**🎯 Result:** All 10 events automatically correlated into a single alert!

---

## 🔑 Key OCSF Fields for Correlation

### **Process Correlation Fields**

```json
{
  "process": {
    "pid": 4628,                           // Current process ID
    "file": {
      "name": "DefenseTrack.exe",
      "path": "C:\\Program Files\\DefenseTrack\\DefenseTrack.exe",
      "hash": {
        "sha256": "...",
        "md5": "...",
        "imphash": "..."                   // Import hash (for correlation)
      }
    },
    "cmd_line": "...",
    "parent_process": {
      "pid": 1892,                         // Parent process ID
      "file": {
        "name": "explorer.exe",
        "path": "C:\\Windows\\explorer.exe"
      },
      "cmd_line": "..."
    },
    "target_process": {                    // For injection/access events
      "pid": 676,
      "file": {
        "name": "lsass.exe"
      }
    }
  }
}
```

### **User Correlation Fields**

```json
{
  "actor": {
    "user": {
      "name": "DEFENSE\\logistics.admin",  // Username (domain\\user)
      "uid": "S-1-5-21-...",                // SID (unique identifier)
      "account_type": "User"
    }
  }
}
```

### **Network Correlation Fields**

```json
{
  "src_endpoint": {
    "ip": "10.45.67.12",                   // Source IP
    "port": 53892,
    "hostname": "PENTAGON-LOGISTICS-12.defense.mil"
  },
  "dst_endpoint": {
    "ip": "45.141.215.89",                 // Destination IP (IOC)
    "port": 443,
    "hostname": "cdn.windowsupdates-verification.com"
  }
}
```

### **File Correlation Fields**

```json
{
  "file": {
    "name": "msvcr120_compat.dll",
    "path": "C:\\Windows\\Temp\\msvcr120_compat.dll",
    "hash": {
      "sha256": "A9B8C7D6E5F4A3B2C1D0E9F8A7B6C5D4E3F2A1B0C9D8E7F6A5B4C3D2E1F0A9B8",
      "md5": "F0E9D8C7B6A5948372615E4D3C2B1A09"
    },
    "size": 245760
  }
}
```

### **Device Correlation Fields**

```json
{
  "device": {
    "hostname": "PENTAGON-LOGISTICS-12.defense.mil",
    "ip": "10.45.67.12",
    "type": "Desktop",
    "os": {
      "name": "Windows",
      "version": "10.0.19041"
    }
  }
}
```

### **Time Correlation Fields**

```json
{
  "time": "2025-12-01T03:12:45.123Z",      // Event timestamp (ISO 8601)
  "start_time": "2025-12-01T03:12:43Z",    // Activity start
  "end_time": "2025-12-01T03:12:47Z"       // Activity end
}
```

---

## 💡 Correlation Strategies

### **Strategy 1: Time Window Grouping**

Group events within 5-minute window:

```python
from datetime import datetime, timedelta

def correlate_by_time_window(events, window_minutes=5):
    """
    Group events within time window
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
        elif event_time <= window_start + timedelta(minutes=window_minutes):
            current_group.append(event)
        else:
            groups.append(current_group)
            window_start = event_time
            current_group = [event]

    if current_group:
        groups.append(current_group)

    return groups
```

---

### **Strategy 2: Entity Linking**

Link events by common entities:

```python
def correlate_by_entity(events, entity_fields):
    """
    Group events sharing common entity values

    entity_fields = [
        'actor.user.name',
        'process.pid',
        'file.hash.sha256',
        'dst_endpoint.ip'
    ]
    """
    from collections import defaultdict

    entity_groups = defaultdict(list)

    for event in events:
        for field in entity_fields:
            value = get_nested_field(event, field)
            if value:
                entity_groups[f"{field}:{value}"].append(event)

    return entity_groups

def get_nested_field(obj, field_path):
    """
    Get nested field value (e.g., 'actor.user.name')
    """
    parts = field_path.split('.')
    value = obj
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return None
    return value
```

**Example:**
```python
events = load_ocsf_events('scenario6-zero-day-memory-corruption.xml')

groups = correlate_by_entity(events, [
    'actor.user.name',
    'process.pid',
    'file.hash.sha256'
])

# Output:
# actor.user.name:DEFENSE\logistics.admin → [Event1, Event3, Event6, Event8, Event10]
# process.pid:4628 → [Event1, Event2, Event3, Event4, Event5]
# file.hash.sha256:A9B8C7D6... → [Event2, Event3, Event6]
```

---

### **Strategy 3: Process Tree Reconstruction**

Build parent-child relationships:

```python
def build_process_tree_from_ocsf(events):
    """
    Build process tree from OCSF Process Activity events
    """
    processes = {}

    for event in events:
        if event.get('class_name') == 'Process Activity':
            proc = event['process']
            pid = proc['pid']
            parent_pid = proc.get('parent_process', {}).get('pid')

            processes[pid] = {
                'pid': pid,
                'name': proc['file']['name'],
                'cmd_line': proc.get('cmd_line', ''),
                'user': event.get('actor', {}).get('user', {}).get('name', ''),
                'time': event['time'],
                'parent_pid': parent_pid,
                'children': []
            }

    # Link children to parents
    for pid, proc in processes.items():
        if proc['parent_pid'] and proc['parent_pid'] in processes:
            processes[proc['parent_pid']]['children'].append(pid)

    return processes

# Render as ASCII tree
def render_process_tree(processes, root_pid, indent=0):
    if root_pid not in processes:
        return ""

    proc = processes[root_pid]
    output = f"{'  ' * indent}└─ [{proc['pid']}] {proc['name']} (User: {proc['user']})\n"
    output += f"{'  ' * indent}   {proc['cmd_line'][:80]}\n"

    for child_pid in proc['children']:
        output += render_process_tree(processes, child_pid, indent + 1)

    return output
```

**Example Output:**
```
└─ [1892] svchost.exe (User: NT AUTHORITY\SYSTEM)
   C:\Windows\System32\svchost.exe -k netsvcs -p
  └─ [7824] cmd.exe (User: NT AUTHORITY\SYSTEM)
     cmd.exe /c "whoami /priv && net localgroup administrators DEFENSE\logistics.admin /add"
    └─ [8912] rundll32.exe (User: NT AUTHORITY\SYSTEM)
       (C2 beacon to 45.141.215.89)
```

---

## 🎯 Demo Talking Points

### **For Your Video Demo:**

**"Let me show you how OCSF makes event correlation trivial..."**

1. **Show the raw Sysmon XML** (10 events, looks chaotic)
   - "Sysmon just generated 10 events in 30 seconds. How do we know they're related?"

2. **Transform to OCSF**
   - "We use the playground-generated code to transform them to OCSF..."

3. **Show the correlation**
   - "Now watch: One query finds all events with `process.pid = 4628`"
   - Pull up result: 5 related events
   - "Another query: `actor.user.name = 'logistics.admin'`"
   - Pull up result: 6 related events
   - "Another query: `file.hash.sha256 = 'A9B8C7...'`"
   - Pull up result: 3 related events

4. **The insight**
   - "Without OCSF: 10 isolated events, manual correlation required, takes hours"
   - "With OCSF: Automated correlation in seconds. Same field names = easy queries."

---

## 📊 Summary: Why OCSF Enables Correlation

| Correlation Type | Without OCSF | With OCSF |
|------------------|--------------|-----------|
| **By Process ID** | Different fields: `ProcessId`, `SourceProcessId`, `NewProcessId` | Standard: `process.pid` everywhere |
| **By User** | Different fields: `User`, `SubjectUserName`, `TargetUserName` | Standard: `actor.user.name` everywhere |
| **By Parent-Child** | Manual mapping required | `process.parent_process.pid` → `process.pid` |
| **By File Hash** | Different fields: `Hashes`, `SHA256`, `FileHash` | Standard: `file.hash.sha256` |
| **By IP Address** | Different fields: `SourceIp`, `src_ip`, `IpAddress` | Standard: `src_endpoint.ip`, `dst_endpoint.ip` |
| **Time Window** | Different formats: Unix timestamp, ISO, custom | Standard: ISO 8601 `time` field |

✅ **Result:** One query language, standardized fields, instant correlation!

---

**Bottom Line for Your Client:**

> "OCSF gives you standardized field names. Same process ID field. Same user field. Same IP field. Your SIEM can now correlate events trivially:
>
> - Same user across 10 events? One query.
> - Parent process spawned 5 children? One query.
> - Same malicious DLL in 3 events? One query.
> - All events within 5-minute attack window? One filter.
>
> **No OCSF = manual correlation nightmare. With OCSF = automated correlation in seconds.**"
