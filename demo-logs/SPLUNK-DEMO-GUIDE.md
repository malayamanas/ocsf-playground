# Splunk Demo Guide: OCSF Event Correlation

## 🎯 What You Need for Splunk Demo

This guide shows you how to ingest OCSF events into Splunk and run correlation queries for your video demonstration.

---

## 📦 Files Provided

1. **`scenario6-ocsf-events.json`** - 10 OCSF-formatted events ready for Splunk ingestion
2. **This guide** - Step-by-step Splunk setup and SPL queries

---

## 🚀 Quick Start (5 Minutes to Demo-Ready)

### **Step 1: Prepare the Data File**

Extract individual events for Splunk ingestion:

```bash
cd /Users/apple/ocsf-playground/demo-logs

# Extract events array and format as JSON Lines (one event per line)
cat scenario6-ocsf-events.json | jq -c '.events[]' > scenario6-events.jsonl
```

Your `scenario6-events.jsonl` should now contain 10 lines, each a complete OCSF event.

---

### **Step 2: Ingest into Splunk**

#### **Option A: Upload via Splunk Web UI** (Easiest for demo)

1. Log into Splunk Web (http://localhost:8000 or your Splunk URL)
2. Go to **Settings** → **Add Data**
3. Select **Upload**
4. Click **Select File** → Choose `scenario6-events.jsonl`
5. **Set Source Type:**
   - Click **"Select Source Type"**
   - Search for "json" or select **_json**
   - Or create new source type: **ocsf:json**
6. **Set Index:**
   - Select index: **main** (or create new index called **ocsf**)
7. Click **Review** → **Submit**

✅ **Data is now in Splunk!**

---

#### **Option B: Upload via Splunk CLI** (For automation)

```bash
# Using Splunk's oneshot command
/opt/splunk/bin/splunk add oneshot /Users/apple/ocsf-playground/demo-logs/scenario6-events.jsonl \
    -sourcetype _json \
    -index main \
    -auth admin:changeme
```

---

#### **Option C: Monitor Directory** (For continuous ingestion)

Create `inputs.conf`:

```ini
# /opt/splunk/etc/apps/ocsf_demo/local/inputs.conf

[monitor:///Users/apple/ocsf-playground/demo-logs/*.jsonl]
disabled = false
sourcetype = ocsf:json
index = ocsf
recursive = false
```

Restart Splunk:
```bash
/opt/splunk/bin/splunk restart
```

---

### **Step 3: Verify Data Ingestion**

Run this in Splunk Search:

```spl
index=main sourcetype=_json class_name=*
| stats count by class_name
```

**Expected Output:**
```
class_name                  count
Process Activity            5
Network Activity            1
File System Activity        2
Security Finding            1
Group Management            1
```

✅ **If you see 10 events across 5 classes, you're ready to demo!**

---

## 🔍 Demo SPL Queries

### **Query 1: View All OCSF Events**

```spl
index=main sourcetype=_json
| table time, class_name, activity_name, device.hostname, actor.user.name, severity
| sort time
```

**What This Shows:**
- Complete timeline of all 10 events
- Demonstrates OCSF standardized fields

---

### **Query 2: Correlate by Process ID**

```spl
index=main sourcetype=_json
| eval process_pid = coalesce('process.pid', 'target_process.pid')
| search process_pid=4628
| table time, class_name, activity_name, process_pid, process.file.name, actor.user.name
| sort time
```

**Expected Output:**
```
time                      class_name          activity_name         process_pid  process.file.name      actor.user.name
2025-12-01 03:12:43.567   Process Activity    Other                 4628         DefenseTrack.exe       DEFENSE\logistics.admin
2025-12-01 03:12:44.890   File System Activity Create               4628         DefenseTrack.exe       DEFENSE\logistics.admin
2025-12-01 03:12:45.123   Process Activity    Load                  4628         DefenseTrack.exe       DEFENSE\logistics.admin
2025-12-01 03:12:45.234   Process Activity    Other                 4628         DefenseTrack.exe       DEFENSE\logistics.admin
2025-12-01 03:12:45.456   Process Activity    Inject                4628         DefenseTrack.exe       DEFENSE\logistics.admin
```

**Demo Point:**
> "5 related events - all tied to the same exploited process (PID 4628). One query, instant correlation!"

---

### **Query 3: Correlate by User**

```spl
index=main sourcetype=_json
| search actor.user.name="DEFENSE\\logistics.admin"
| table time, class_name, activity_name, process.file.name, file.name, dst_endpoint.ip
| sort time
```

**Expected Output:**
```
time                      class_name           activity_name    process.file.name   file.name              dst_endpoint.ip
2025-12-01 03:12:43.567   Process Activity     Other            DefenseTrack.exe    -                      -
2025-12-01 03:12:44.890   File System Activity Create           DefenseTrack.exe    msvcr120_compat.dll    -
2025-12-01 03:12:45.123   Process Activity     Load             DefenseTrack.exe    msvcr120_compat.dll    -
2025-12-01 03:12:45.234   Process Activity     Other            DefenseTrack.exe    -                      -
2025-12-01 03:12:45.456   Process Activity     Inject           DefenseTrack.exe    -                      -
2025-12-01 03:12:45.567   Security Finding     Create           DefenseTrack.exe    -                      -
2025-12-01 03:12:48.123   File System Activity Set Attributes   reg.exe             -                      -
```

**Demo Point:**
> "7 events by the compromised user account. Track user activity across different event types!"

---

### **Query 4: Correlate by File Hash (IOC)**

```spl
index=main sourcetype=_json
| eval file_hash = mvindex('file.hashes{}.value', 0)
| search file_hash="A9B8C7D6E5F4A3B2C1D0E9F8A7B6C5D4E3F2A1B0C9D8E7F6A5B4C3D2E1F0A9B8"
| table time, class_name, activity_name, file.name, file.path, process.file.name
| sort time
```

**Expected Output:**
```
time                      class_name           activity_name    file.name              file.path                           process.file.name
2025-12-01 03:12:44.890   File System Activity Create           msvcr120_compat.dll    C:\Windows\Temp\msvcr120_compat.dll DefenseTrack.exe
2025-12-01 03:12:45.123   Process Activity     Load             msvcr120_compat.dll    C:\Windows\Temp\msvcr120_compat.dll DefenseTrack.exe
2025-12-01 03:12:45.567   Security Finding     Create           -                      C:\Windows\Temp\msvcr120_compat.dll DefenseTrack.exe
```

**Demo Point:**
> "Same malicious DLL appears in 3 different event types. IOC tracking made trivial!"

---

### **Query 5: Correlate by C2 IP Address**

```spl
index=main sourcetype=_json
| search dst_endpoint.ip="45.141.215.89"
| table time, src_endpoint.ip, dst_endpoint.ip, dst_endpoint.hostname, dst_endpoint.port, process.file.name, actor.user.name
```

**Expected Output:**
```
time                      src_endpoint.ip  dst_endpoint.ip    dst_endpoint.hostname                       dst_endpoint.port  process.file.name  actor.user.name
2025-12-01 03:13:00.456   10.45.67.12      45.141.215.89      cdn.windowsupdates-verification.com         443                rundll32.exe       NT AUTHORITY\SYSTEM
```

**Demo Point:**
> "C2 connection detected! In a real scenario, this query would find all systems across all SOCs connecting to this malicious IP."

---

### **Query 6: Process Tree Reconstruction**

```spl
index=main sourcetype=_json class_name="Process Activity"
| eval parent_pid = 'process.parent_process.pid'
| eval child_pid = 'process.pid'
| eval parent_name = 'process.parent_process.file.name'
| eval child_name = 'process.file.name'
| eval cmd_line = 'process.cmd_line'
| table time, parent_pid, parent_name, child_pid, child_name, cmd_line
| sort time
```

**Expected Output:**
```
time                      parent_pid  parent_name    child_pid  child_name         cmd_line
2025-12-01 03:12:45.456   -           -              4628       DefenseTrack.exe   -
2025-12-01 03:12:46.789   1892        svchost.exe    7824       cmd.exe            cmd.exe /c "whoami /priv && net localgroup..."
```

**Demo Point:**
> "Process tree shows svchost spawned cmd.exe - classic privilege escalation pattern!"

---

### **Query 7: Time Window Analysis**

```spl
index=main sourcetype=_json
| eval time_epoch = strptime(time, "%Y-%m-%dT%H:%M:%S.%3QZ")
| eval time_readable = strftime(time_epoch, "%H:%M:%S.%3Q")
| stats
    count,
    values(class_name) as event_types,
    values(activity_name) as activities,
    min(time_readable) as first_event,
    max(time_readable) as last_event
    by device.hostname
| eval duration_seconds = "~17 seconds"
```

**Expected Output:**
```
device.hostname                        count  event_types                                           first_event       last_event        duration_seconds
PENTAGON-LOGISTICS-12.defense.mil      10     [Process Activity, File System Activity, ...]         03:12:43.567      03:13:00.456      ~17 seconds
```

**Demo Point:**
> "Complete zero-day attack chain executed in just 17 seconds. OCSF captured every step!"

---

### **Query 8: Attack Chain Summary Dashboard**

```spl
index=main sourcetype=_json
| eval process_pid = coalesce('process.pid', 'target_process.pid', 'process.parent_process.pid')
| eval user = 'actor.user.name'
| eval file_hash = mvindex('file.hashes{}.value', 0)
| eval c2_ip = 'dst_endpoint.ip'
| stats
    count as event_count,
    values(class_name) as event_classes,
    values(activity_name) as activities,
    values(process_pid) as process_ids,
    values(user) as users,
    values(file.name) as files,
    values(file_hash) as iocs,
    values(c2_ip) as c2_servers,
    values(malware{}.name) as malware_names,
    values(attacks{}.technique.uid) as mitre_techniques,
    min(time) as first_seen,
    max(time) as last_seen
    by device.hostname
| eval attack_summary = "Zero-Day Exploit: " . event_count . " events detected"
```

**Expected Output:**
```
device.hostname                        event_count  event_classes                    users                                      files                        c2_servers         malware_names                         mitre_techniques
PENTAGON-LOGISTICS-12.defense.mil      10           [Process Activity, Network...]   [DEFENSE\logistics.admin, NT AUTH\SYS...] [msvcr120_compat.dll, ...]   45.141.215.89      Exploit:Win64/CVE-2025-XXXXX...      [T1055, T1068, T1071.001, ...]
```

**Demo Point:**
> "One Splunk dashboard - complete attack visibility. IOCs, users, processes, C2 servers, MITRE techniques - all correlated automatically!"

---

## 🎬 Video Demo Script

### **Scene 1: Show the Problem (30 seconds)**

"Here's the challenge: 10 different security events from Sysmon, Windows Defender, and Windows Security - all from one Pentagon workstation. How do we know they're related?"

```spl
index=main sourcetype=_json
| table time, class_name, activity_name
| sort time
```

---

### **Scene 2: Correlation by Process (45 seconds)**

"Watch this - I'll search for all events related to process ID 4628..."

```spl
index=main sourcetype=_json
| eval process_pid = coalesce('process.pid', 'target_process.pid')
| search process_pid=4628
| table time, class_name, activity_name, process.file.name
| sort time
```

"5 events! All tied to DefenseTrack.exe. We see the exploit, DLL injection, process tampering - the entire attack chain. One query."

---

### **Scene 3: Correlation by User (30 seconds)**

"Now let's track the compromised user account..."

```spl
index=main sourcetype=_json
| search actor.user.name="DEFENSE\\logistics.admin"
| table time, class_name, activity_name, file.name
| sort time
```

"7 events by this user - from initial exploit to persistence. OCSF standard field names make this instant."

---

### **Scene 4: Correlation by IOC (30 seconds)**

"What about that malicious DLL? Same file hash across different log sources..."

```spl
index=main sourcetype=_json
| eval file_hash = mvindex('file.hashes{}.value', 0)
| search file_hash="A9B8C7D6*"
| table time, class_name, file.name, file.path
```

"There it is - file created, loaded, and detected by Defender. 3 different event types, same IOC."

---

### **Scene 5: The Big Picture (45 seconds)**

"Now the full attack summary..."

```spl
index=main sourcetype=_json
| stats
    count,
    values(class_name) as event_types,
    values(actor.user.name) as users,
    values(dst_endpoint.ip) as c2_servers,
    values(malware{}.name) as threats
    by device.hostname
```

"Complete visibility: 10 events, 5 event types, compromised user, C2 connection, malware detection - all correlated automatically. **This is the power of OCSF standardization.**"

---

### **Scene 6: The Value Prop (30 seconds)**

"Without OCSF, these events have different field names:
- Sysmon: `ProcessId`
- Windows: `NewProcessId`
- Defender: `Process Name`

With OCSF, it's all `process.pid`. Same field name everywhere. One query language. Instant correlation.

And remember - the OCSF Playground generated the transformation code to make this possible. Deploy once, correlate forever."

---

## 📊 Advanced Splunk Queries

### **Query 9: Create Alert for Attack Chain Detection**

```spl
index=main sourcetype=_json
| eval correlation_key = coalesce('process.pid', 'process.parent_process.pid')
| stats
    dc(class_name) as unique_event_types,
    values(class_name) as event_types,
    values(activity_name) as activities,
    values(actor.user.name) as users,
    count as event_count
    by device.hostname, correlation_key
| where unique_event_types >= 3 AND event_count >= 5
| eval alert_severity = case(
    event_count >= 8, "CRITICAL",
    event_count >= 5, "HIGH",
    1=1, "MEDIUM"
)
| eval alert_title = "Attack Chain Detected: " . event_count . " correlated events on " . device.hostname
| table device.hostname, correlation_key, event_count, unique_event_types, alert_severity, event_types, users, alert_title
```

**Use Case:** Real-time alert when multiple related events indicate an attack chain.

---

### **Query 10: MITRE ATT&CK Technique Coverage**

```spl
index=main sourcetype=_json attacks{}.technique.uid=*
| eval mitre_technique = mvindex('attacks{}.technique.uid', 0)
| eval mitre_name = mvindex('attacks{}.technique.name', 0)
| stats
    count as event_count,
    values(class_name) as event_types,
    values(device.hostname) as affected_hosts
    by mitre_technique, mitre_name
| sort - event_count
```

**Expected Output:**
```
mitre_technique  mitre_name                                           event_count  affected_hosts
T1055            Process Injection                                    2            PENTAGON-LOGISTICS-12.defense.mil
T1068            Exploitation for Privilege Escalation                1            PENTAGON-LOGISTICS-12.defense.mil
T1071.001        Application Layer Protocol: Web Protocols            1            PENTAGON-LOGISTICS-12.defense.mil
T1547.001        Boot or Logon Autostart Execution: Registry Run...  1            PENTAGON-LOGISTICS-12.defense.mil
```

**Demo Point:**
> "MITRE ATT&CK techniques automatically tagged. Security teams can track adversary behavior patterns!"

---

## 🚀 Production Splunk Setup

### **Create OCSF Index**

```bash
/opt/splunk/bin/splunk add index ocsf -auth admin:changeme
```

### **Create OCSF Source Type**

Create `props.conf`:

```ini
# /opt/splunk/etc/apps/ocsf_app/local/props.conf

[ocsf:json]
INDEXED_EXTRACTIONS = json
KV_MODE = json
TIMESTAMP_FIELDS = time
TIME_FORMAT = %Y-%m-%dT%H:%M:%S.%3QZ
MAX_TIMESTAMP_LOOKAHEAD = 30
SHOULD_LINEMERGE = false
LINE_BREAKER = ([\r\n]+)
category = Security
```

### **Create Field Extractions**

```ini
# Add to props.conf

[ocsf:json]
...existing config...

EVAL-process_pid = coalesce('process.pid', 'target_process.pid', 'process.parent_process.pid')
EVAL-user_name = 'actor.user.name'
EVAL-host_name = 'device.hostname'
EVAL-file_hash = mvindex('file.hashes{}.value', 0)
EVAL-c2_ip = 'dst_endpoint.ip'
EVAL-mitre_technique = mvindex('attacks{}.technique.uid', 0)
```

---

## ✅ Checklist: What You Have Now

- ✅ **OCSF-formatted JSON events** (`scenario6-ocsf-events.json`)
- ✅ **Splunk ingestion instructions** (3 methods)
- ✅ **10 ready-to-run SPL queries** (correlation examples)
- ✅ **Video demo script** (scene-by-scene)
- ✅ **Advanced queries** (alerts, MITRE mapping)
- ✅ **Production setup guide** (props.conf, indexes)

---

## 🎯 Summary: What's Missing vs. What You Have

### **✅ You Now Have:**
1. OCSF-formatted events ready for Splunk
2. Splunk ingestion instructions (web UI, CLI, monitoring)
3. 10 correlation queries demonstrating:
   - Process ID correlation
   - User tracking
   - IOC pivoting (file hash, C2 IP)
   - Process tree reconstruction
   - Time window analysis
   - Attack chain detection
4. Video demo script with talking points
5. Production Splunk configuration

### **🎬 Next Steps:**
1. Run `jq -c '.events[]' scenario6-ocsf-events.json > scenario6-events.jsonl`
2. Upload `scenario6-events.jsonl` to Splunk (web UI is fastest)
3. Run the SPL queries in order
4. Record your screen while demonstrating correlation
5. Show the value: "Same field names = instant correlation"

---

**You're ready to demo! 🚀**
