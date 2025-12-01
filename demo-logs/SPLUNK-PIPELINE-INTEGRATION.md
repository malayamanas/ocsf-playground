# OCSF Transformer Integration in Splunk Architecture

## 🏗️ Your Splunk Pipeline

```
Windows Endpoints → Universal Forwarder → Heavy Forwarder (Optional) → Indexer → Search Head
     (Logs)              (UF)                   (HF)                    (Index)    (Query)
```

## 🎯 Question: Where to Integrate OCSF Transformer?

**Answer: Heavy Forwarder (Recommended) or Indexer (Alternative)**

---

## 📊 Integration Options Comparison

| Location | Pros | Cons | Recommended? |
|----------|------|------|--------------|
| **Universal Forwarder** | ❌ Not possible | UF cannot run Python/scripts | ❌ NO |
| **Heavy Forwarder** | ✅✅✅ BEST OPTION | Requires HF deployment | ✅ **YES** |
| **Indexer** | ✅ Possible | Performance impact, no scaling | ⚠️ Fallback |
| **Search-Time** | ✅ No pipeline changes | Slow, compute on every search | ❌ NO |

---

## ✅ RECOMMENDED: Heavy Forwarder Integration

### **Why Heavy Forwarder?**

1. **Purpose-built for transformation** - HF is designed for parsing, enrichment, and data manipulation
2. **Centralized processing** - Transform once for all endpoints
3. **Scales independently** - Add more HFs without touching indexers
4. **Reduces index load** - Indexers receive clean OCSF JSON
5. **No endpoint performance impact** - UFs stay lightweight

### **Architecture:**

```
┌─────────────────────────────────────────────────────────────────────┐
│  ENDPOINTS (30+ SOCs)                                                │
│  • Pentagon workstations                                             │
│  • Navy servers                                                      │
│  • Air Force systems                                                 │
│  • Sysmon + Windows Event Logs + Defender                           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Raw XML/JSON logs
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  UNIVERSAL FORWARDER (on each endpoint)                              │
│  • Lightweight agent                                                 │
│  • Reads logs from:                                                  │
│    - C:\Windows\System32\winevt\Logs\                               │
│    - Microsoft-Windows-Sysmon/Operational                           │
│  • Forwards raw logs (no transformation)                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Forward to Heavy Forwarder
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  HEAVY FORWARDER ← ← ← INTEGRATE OCSF TRANSFORMER HERE              │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  OCSF Transformation Layer (Python Scripts)                │    │
│  │                                                             │    │
│  │  • Receives raw Windows/Sysmon XML                         │    │
│  │  • Runs OCSF transformer scripts:                          │    │
│  │    - transform_sysmon_event1.py (Process Creation)         │    │
│  │    - transform_sysmon_event3.py (Network Connection)       │    │
│  │    - transform_windows_4624.py (Authentication)            │    │
│  │  • Outputs OCSF-compliant JSON                             │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  Configuration Files:                                                │
│  • props.conf - Field extraction                                    │
│  • transforms.conf - OCSF transformation logic                      │
│  • inputs.conf - Receiving from UFs                                 │
│  • outputs.conf - Forwarding to Indexers                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ OCSF JSON events
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  INDEXER (Splunk Enterprise)                                        │
│  • Receives pre-transformed OCSF events                             │
│  • Indexes as: index=ocsf sourcetype=ocsf:json                     │
│  • No additional parsing needed                                     │
│  • Fast indexing (already in JSON format)                           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Indexed data
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SEARCH HEAD                                                         │
│  • Analysts run correlation queries                                 │
│  • Standard OCSF field names work across all 30 SOCs                │
│  • Example: dst_endpoint.ip="45.141.215.89"                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementation: Heavy Forwarder Setup

### **Step 1: Install Splunk Heavy Forwarder**

```bash
# Download Splunk Enterprise (used as HF)
wget -O splunk.tgz 'https://download.splunk.com/products/splunk/releases/9.1.0/linux/splunk-9.1.0-linux-x64.tgz'

# Install
tar xvzf splunk.tgz -C /opt

# Enable Heavy Forwarder mode
/opt/splunk/bin/splunk enable app SplunkForwarder -auth admin:changeme

# Set as Heavy Forwarder (parsing enabled)
/opt/splunk/bin/splunk set deploy-poll deploymentserver.defense.mil:8089
```

---

### **Step 2: Deploy OCSF Transformer Scripts**

Create app structure:

```bash
/opt/splunk/etc/apps/ocsf_transformer/
├── bin/
│   ├── transform_sysmon_event1.py      # Process Creation
│   ├── transform_sysmon_event3.py      # Network Connection
│   ├── transform_sysmon_event7.py      # DLL Load
│   ├── transform_windows_4624.py       # Authentication
│   ├── ocsf_lib.py                     # Common OCSF utilities
│   └── requirements.txt                # Python dependencies
├── local/
│   ├── props.conf                      # Field extraction config
│   ├── transforms.conf                 # Transformation rules
│   ├── inputs.conf                     # Receive from UFs
│   └── outputs.conf                    # Forward to indexers
└── metadata/
    └── default.meta                    # App permissions
```

---

### **Step 3: Configure Transformation Pipeline**

#### **inputs.conf** (Receive from Universal Forwarders)

```ini
# /opt/splunk/etc/apps/ocsf_transformer/local/inputs.conf

[splunktcp://9997]
disabled = false
# Receive logs from Universal Forwarders
```

---

#### **props.conf** (Identify Log Types & Trigger Transforms)

```ini
# /opt/splunk/etc/apps/ocsf_transformer/local/props.conf

# Sysmon Event ID 1 (Process Creation)
[source::XmlWinEventLog:Microsoft-Windows-Sysmon/Operational]
TRANSFORMS-ocsf_sysmon_event1 = ocsf_transform_sysmon_1
TRANSFORMS-ocsf_sysmon_event3 = ocsf_transform_sysmon_3
TRANSFORMS-ocsf_sysmon_event7 = ocsf_transform_sysmon_7

# Windows Security Events
[source::WinEventLog:Security]
TRANSFORMS-ocsf_windows_4624 = ocsf_transform_windows_4624

# Set sourcetype for transformed events
EVAL-sourcetype = if(match(_raw, "class_name"), "ocsf:json", sourcetype)
```

---

#### **transforms.conf** (Call Python Transformers)

```ini
# /opt/splunk/etc/apps/ocsf_transformer/local/transforms.conf

# Sysmon Event ID 1 → OCSF Process Activity
[ocsf_transform_sysmon_1]
REGEX = <EventID>1</EventID>
DEST_KEY = _raw
FORMAT = ocsf::$1

# Call Python script to transform
LOOKUP-ocsf_sysmon_1 = ocsf_sysmon_1_script

# Python script transformation
[ocsf_sysmon_1_script]
filename = transform_sysmon_event1.py
python.version = python3

# Similar configs for other event types...

# Sysmon Event ID 3 → OCSF Network Activity
[ocsf_transform_sysmon_3]
REGEX = <EventID>3</EventID>
DEST_KEY = _raw
FORMAT = ocsf::$1

[ocsf_sysmon_3_script]
filename = transform_sysmon_event3.py
python.version = python3

# Windows Event ID 4624 → OCSF Authentication
[ocsf_transform_windows_4624]
REGEX = <EventID>4624</EventID>
DEST_KEY = _raw
FORMAT = ocsf::$1

[ocsf_transform_windows_4624_script]
filename = transform_windows_4624.py
python.version = python3
```

---

### **Step 4: Python Transformer Script Example**

#### **transform_sysmon_event1.py** (Sysmon Event ID 1 → OCSF)

```python
#!/opt/splunk/bin/python3
"""
OCSF Transformer: Sysmon Event ID 1 → OCSF Process Activity (1007)
Generated by OCSF Playground
"""

import sys
import json
import xml.etree.ElementTree as ET
from datetime import datetime


def transform_sysmon_event1(xml_string):
    """Transform Sysmon Event ID 1 to OCSF Process Activity"""

    try:
        root = ET.fromstring(xml_string)
        ns = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}

        # Extract System section
        system = root.find('.//ns:System', ns)
        time_created = system.find('ns:TimeCreated', ns).get('SystemTime')
        computer = system.find('ns:Computer', ns).text

        # Extract EventData
        event_data = {}
        for data in root.findall('.//ns:EventData/ns:Data', ns):
            field_name = data.get('Name')
            event_data[field_name] = data.text

        # Build OCSF Process Activity event
        ocsf_event = {
            "time": time_created,
            "class_uid": 1007,
            "class_name": "Process Activity",
            "category_uid": 1,
            "category_name": "System Activity",
            "activity_id": 1,
            "activity_name": "Launch",
            "severity_id": 1,
            "severity": "Informational",
            "type_uid": 100701,
            "metadata": {
                "version": "1.7.0",
                "product": {
                    "name": "Sysmon",
                    "vendor_name": "Microsoft",
                    "version": "Event ID 1"
                }
            },
            "device": {
                "hostname": computer,
                "type_id": 1
            },
            "process": {
                "pid": int(event_data.get('ProcessId', 0)),
                "file": {
                    "name": event_data.get('Image', '').split('\\')[-1],
                    "path": event_data.get('Image', '')
                },
                "cmd_line": event_data.get('CommandLine', ''),
                "integrity": event_data.get('IntegrityLevel', ''),
                "parent_process": {
                    "pid": int(event_data.get('ParentProcessId', 0)),
                    "file": {
                        "name": event_data.get('ParentImage', '').split('\\')[-1],
                        "path": event_data.get('ParentImage', '')
                    },
                    "cmd_line": event_data.get('ParentCommandLine', '')
                }
            },
            "actor": {
                "user": {
                    "name": event_data.get('User', ''),
                    "uid": event_data.get('LogonGuid', '')
                }
            }
        }

        # Add file hashes if present
        if 'Hashes' in event_data:
            hashes = []
            for hash_pair in event_data['Hashes'].split(','):
                if '=' in hash_pair:
                    alg, value = hash_pair.split('=', 1)
                    hashes.append({
                        "algorithm": alg,
                        "value": value
                    })
            ocsf_event['process']['file']['hashes'] = hashes

        return json.dumps(ocsf_event)

    except Exception as e:
        # Return original event if transformation fails
        return xml_string


def main():
    """Splunk scripted input handler"""
    # Read event from stdin (Splunk passes events this way)
    for line in sys.stdin:
        transformed = transform_sysmon_event1(line)
        sys.stdout.write(transformed + '\n')
        sys.stdout.flush()


if __name__ == '__main__':
    main()
```

---

### **Step 5: Configure Forwarding to Indexers**

#### **outputs.conf** (Forward OCSF Events to Indexers)

```ini
# /opt/splunk/etc/apps/ocsf_transformer/local/outputs.conf

[tcpout]
defaultGroup = ocsf_indexers

[tcpout:ocsf_indexers]
server = indexer1.defense.mil:9997, indexer2.defense.mil:9997, indexer3.defense.mil:9997
compressed = true

# Only forward OCSF-transformed events
[tcpout-server://indexer1.defense.mil:9997]
sendCookedData = true
```

---

### **Step 6: Deploy and Test**

```bash
# Restart Heavy Forwarder
/opt/splunk/bin/splunk restart

# Test transformation with sample event
echo '<Event>...</Event>' | /opt/splunk/etc/apps/ocsf_transformer/bin/transform_sysmon_event1.py

# Check logs
tail -f /opt/splunk/var/log/splunk/splunkd.log

# Verify on indexer
# Splunk Search: index=ocsf sourcetype=ocsf:json | head 10
```

---

## ⚠️ Alternative: Indexer Integration (Fallback)

### **If No Heavy Forwarder:**

Deploy transformers directly on **indexers**, but this has drawbacks:

**Indexer props.conf:**
```ini
# /opt/splunk/etc/system/local/props.conf

[source::XmlWinEventLog:Microsoft-Windows-Sysmon/Operational]
TRANSFORMS-ocsf = ocsf_transform_all
INDEXED_EXTRACTIONS = json
# ... same transforms.conf config ...
```

**Cons:**
- ❌ Indexer CPU usage increases
- ❌ No horizontal scaling (can't add more indexers easily)
- ❌ Transformation happens at index time (can't reprocess without re-indexing)

---

## 🚫 Why NOT Universal Forwarder?

**Universal Forwarder Limitations:**
1. ❌ **No Python execution** - UF is C++ only, no scripting
2. ❌ **No parsing** - UF cannot manipulate _raw data
3. ❌ **Lightweight by design** - Only reads & forwards files
4. ❌ **No transforms.conf** - Cannot apply TRANSFORMS- operations

**UF Role:** Collect and forward raw logs only.

---

## 🚫 Why NOT Search-Time Transformation?

**Search-Time Field Extraction:**

```ini
# props.conf (on Search Head)
[ocsf:json]
EXTRACT-process_pid = (?<process_pid>"process":\{"pid":(\d+))
EXTRACT-user_name = (?<user_name>"actor":\{"user":\{"name":"([^"]+)"))
# ... hundreds of field extractions ...
```

**Cons:**
- ❌ **Slow** - Computed on every search
- ❌ **Wasteful** - Re-extracts same fields repeatedly
- ❌ **Complex** - Requires regex for every OCSF field
- ❌ **No data normalization** - Still storing raw XML

**Use Case:** Only for temporary prototyping/testing

---

## 📊 Performance Comparison

| Metric | Heavy Forwarder | Indexer | Search-Time |
|--------|-----------------|---------|-------------|
| **Transform Cost** | ✅ Once (HF CPU) | ⚠️ Once (Indexer CPU) | ❌ Every search |
| **Index Size** | ✅ Small (JSON) | ✅ Small (JSON) | ❌ Large (raw XML) |
| **Search Speed** | ✅ Fast | ✅ Fast | ❌ Slow |
| **Scaling** | ✅ Easy (add HFs) | ⚠️ Hard | ❌ No scaling |
| **Reprocessing** | ✅ Re-run HF | ❌ Re-index | ✅ Change regex |
| **Indexer Load** | ✅ Low | ❌ High | ✅ Low (index) |

---

## 🎯 Recommended Architecture for 30 SOCs

```
30 SOCs
  └─ Each SOC: 100-1000 endpoints
       └─ Each endpoint: Universal Forwarder
            │
            │ Forward raw logs
            ▼
  ┌─────────────────────────────────┐
  │  3-5 Heavy Forwarders           │  ← DEPLOY OCSF TRANSFORMERS HERE
  │  (Load-balanced, HA cluster)    │
  │  • Pentagon-HF-01               │
  │  • Pentagon-HF-02               │
  │  • Pentagon-HF-03               │
  └─────────────────────────────────┘
            │
            │ Forward OCSF JSON
            ▼
  ┌─────────────────────────────────┐
  │  Indexer Cluster (10+ indexers) │
  │  • Fast indexing (JSON)         │
  │  • No transformation overhead   │
  └─────────────────────────────────┘
            │
            ▼
  ┌─────────────────────────────────┐
  │  Search Head Cluster            │
  │  • Analysts run SPL queries     │
  │  • OCSF field names work        │
  └─────────────────────────────────┘
```

**Benefits:**
- ✅ Centralized transformation (3-5 HFs vs. 30,000 endpoints)
- ✅ Easy to update (change transformer script on HFs only)
- ✅ Horizontally scalable (add more HFs as needed)
- ✅ Indexers stay fast (receive clean JSON)
- ✅ No endpoint performance impact

---

## ✅ Summary: Best Practices

| Question | Answer |
|----------|--------|
| **Where to integrate?** | Heavy Forwarder (primary) or Indexer (fallback) |
| **Universal Forwarder?** | ❌ No - Cannot run Python/scripts |
| **Heavy Forwarder?** | ✅ **YES** - Purpose-built for transformation |
| **Indexer?** | ⚠️ Possible but not recommended (performance) |
| **Search-Time?** | ❌ No - Too slow, wasteful |
| **How many HFs?** | 3-5 for 30 SOCs (load-balanced cluster) |
| **Deployment method?** | Splunk app with Python scripts in `bin/` |
| **Configuration files?** | `props.conf`, `transforms.conf`, `outputs.conf` |

---

## 🚀 Next Steps

1. **Deploy Heavy Forwarder** infrastructure (if not already present)
2. **Package OCSF transformers** as Splunk app
3. **Test with sample events** from each SOC
4. **Monitor performance** (HF CPU, throughput)
5. **Scale horizontally** by adding more HFs as needed

---

## 📝 Quick Decision Matrix

**Do you have Heavy Forwarders?**
- ✅ **YES** → Integrate OCSF transformers on HF (BEST)
- ❌ **NO** → Deploy HFs first, then integrate transformers

**Cannot deploy Heavy Forwarders?**
- ⚠️ Integrate on Indexers (monitor performance)
- Consider upgrading to HF architecture later

**Want quick prototype?**
- Use search-time field extraction temporarily
- Plan migration to HF-based transformation

---

**Recommended:** Heavy Forwarder integration for production-grade OCSF normalization at scale! 🚀
