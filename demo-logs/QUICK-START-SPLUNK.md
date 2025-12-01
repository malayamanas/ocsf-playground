# 🚀 Quick Start: Splunk Demo in 5 Minutes

## 📋 What You Have

✅ **`scenario6-events.jsonl`** - 10 OCSF events ready for Splunk
✅ **`SPLUNK-DEMO-GUIDE.md`** - Complete guide with 10 SPL queries
✅ **Everything needed** for a live correlation demo

---

## ⚡ Fast Track (5 Minutes)

### **Step 1: Upload to Splunk** (2 minutes)

1. Open Splunk Web → **Settings** → **Add Data** → **Upload**
2. Select file: **`scenario6-events.jsonl`**
3. Source type: **`_json`**
4. Index: **`main`**
5. Click **Submit**

### **Step 2: Verify** (30 seconds)

```spl
index=main sourcetype=_json | stats count
```
Expected: **10 events**

### **Step 3: Run Demo Queries** (2 minutes)

Copy-paste these queries one by one:

#### **Query 1: Correlate by Process ID**
```spl
index=main sourcetype=_json
| eval process_pid = coalesce('process.pid', 'target_process.pid')
| search process_pid=4628
| table time, class_name, activity_name, process.file.name
| sort time
```
**Shows**: 5 events related to exploited process

#### **Query 2: Correlate by User**
```spl
index=main sourcetype=_json
| search actor.user.name="DEFENSE\\logistics.admin"
| table time, class_name, activity_name, file.name
| sort time
```
**Shows**: 7 events by compromised user

#### **Query 3: Correlate by File Hash (IOC)**
```spl
index=main sourcetype=_json
| eval file_hash = mvindex('file.hashes{}.value', 0)
| search file_hash="A9B8C7D6E5F4A3B2C1D0E9F8A7B6C5D4E3F2A1B0C9D8E7F6A5B4C3D2E1F0A9B8"
| table time, class_name, file.name, file.path
| sort time
```
**Shows**: 3 events with malicious DLL

#### **Query 4: Attack Summary**
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
**Shows**: Complete attack overview

---

## 🎬 Demo Script (30 seconds per query)

### **Opening:**
> "I have 10 security events from a Pentagon workstation - Sysmon, Windows Defender, Windows Security logs. Let me show you how OCSF enables instant correlation..."

### **Query 1:**
> "First, let's find all events related to process ID 4628... [Run query] ...5 events! All tied to DefenseTrack.exe. One field name - `process.pid` - works across all log sources."

### **Query 2:**
> "Now track the compromised user... [Run query] ...7 events showing everything this account did. Same field name everywhere: `actor.user.name`"

### **Query 3:**
> "What about that malicious DLL? [Run query] ...File created, loaded, detected - 3 different log sources, same file hash. Instant IOC pivoting."

### **Query 4:**
> "And here's the complete picture... [Run query] ...10 events, 5 event types, C2 connection, malware detected - all correlated automatically. **This is OCSF.**"

### **Closing:**
> "Without OCSF, these logs have different field names. With OCSF, it's all standardized. One query language. Instant correlation. The OCSF Playground generated the transformation code to make this possible."

---

## 📊 Expected Results Summary

| Query | Purpose | Events Found | Key Insight |
|-------|---------|--------------|-------------|
| Process ID | Correlate by PID 4628 | 5 events | Complete exploit chain |
| User | Track compromised account | 7 events | User activity timeline |
| File Hash | IOC pivoting | 3 events | Malicious DLL lifecycle |
| C2 IP | Network IOC | 1 event | Command & control |
| Summary | Full picture | 10 events | Attack chain complete |

---

## ✅ Checklist

Before recording your video:
- [ ] Splunk is running
- [ ] `scenario6-events.jsonl` uploaded
- [ ] Verify: `index=main sourcetype=_json | stats count` returns 10
- [ ] Test all 4 demo queries
- [ ] Practice talking points (30 sec per query = 2 min total)

---

## 🆘 Troubleshooting

**No events found?**
```spl
index=* | stats count by index, sourcetype
```
Check which index your data landed in.

**Field names not working?**
```spl
index=main sourcetype=_json | head 1 | table *
```
Verify JSON fields are extracted correctly.

**Want to start over?**
```spl
index=main sourcetype=_json | delete
```
Then re-upload the file.

---

## 🎯 Key Talking Points

1. **Standardized Fields**: Same field names across all log sources
   - `process.pid` (not ProcessId, SourceProcessId, NewProcessId)
   - `actor.user.name` (not User, SubjectUserName, TargetUserName)
   - `file.hashes{}.value` (not SHA256, FileHash, Hashes)

2. **Instant Correlation**: One query works everywhere
   - Find all events by process: `process.pid=4628`
   - Find all events by user: `actor.user.name="logistics.admin"`
   - Find all events by IOC: `file_hash="A9B8C7D6..."`

3. **The OCSF Value**: Playground generates transformation code once, correlation works forever
   - No manual field mapping
   - No custom parsers per SOC
   - Deploy transformers → instant standardization

---

**You're ready! 🚀 Record and impress your client!**
