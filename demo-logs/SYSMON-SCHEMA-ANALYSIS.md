# Sysmon XML Event Schema Analysis

## 🎯 Key Finding: Is Sysmon XML Schema Consistent?

**Answer:** **YES and NO**

- ✅ **YES**: All Sysmon events use the **same base XML structure** (System section)
- ❌ **NO**: The **EventData section** is **unique per event type** (different fields)

---

## 📐 Universal XML Structure

### **All Sysmon Events Share This Structure:**

```xml
<Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
  <System>
    <!-- CONSISTENT across ALL event types -->
    <Provider Name="Microsoft-Windows-Sysmon" Guid="{...}" />
    <EventID>X</EventID>                    <!-- The ONLY difference -->
    <Version>X</Version>
    <Level>4</Level>
    <Task>X</Task>
    <Opcode>0</Opcode>
    <Keywords>0x8000000000000000</Keywords>
    <TimeCreated SystemTime="..." />
    <EventRecordID>...</EventRecordID>
    <Correlation />
    <Execution ProcessID="..." ThreadID="..." />
    <Channel>Microsoft-Windows-Sysmon/Operational</Channel>
    <Computer>HOSTNAME</Computer>
    <Security UserID="..." />
  </System>

  <EventData>
    <!-- UNIQUE per event type -->
    <Data Name="Field1">Value1</Data>
    <Data Name="Field2">Value2</Data>
    <!-- Number and names of fields vary by event type -->
  </EventData>
</Event>
```

---

## 🔍 What's Consistent (System Section)

These fields appear in **ALL** Sysmon events:

| Field | Always Present? | Same Format? | Notes |
|-------|----------------|--------------|-------|
| `Provider/@Name` | ✅ Yes | ✅ Yes | Always "Microsoft-Windows-Sysmon" |
| `Provider/@Guid` | ✅ Yes | ✅ Yes | Always "{5770385F-C22A-43E0-BF4C-06F5698FFBD9}" |
| `EventID` | ✅ Yes | ✅ Yes | 1-29 (identifies event type) |
| `Version` | ✅ Yes | ⚠️ Varies | Depends on Sysmon version |
| `Level` | ✅ Yes | ✅ Yes | Always "4" (Informational) |
| `TimeCreated/@SystemTime` | ✅ Yes | ✅ Yes | ISO 8601 format |
| `EventRecordID` | ✅ Yes | ✅ Yes | Incremental integer |
| `Channel` | ✅ Yes | ✅ Yes | Always "Microsoft-Windows-Sysmon/Operational" |
| `Computer` | ✅ Yes | ✅ Yes | Hostname |
| `Security/@UserID` | ✅ Yes | ✅ Yes | SID |

✅ **Conclusion: The System section is 100% consistent across all event types.**

---

## ⚠️ What's Different (EventData Section)

The `<EventData>` section contains **event-specific fields** using `<Data Name="...">` elements.

### **Common Fields (Appear in MANY Events)**

These fields appear across **multiple** (but not all) event types:

| Field Name | Event Types | Purpose |
|------------|-------------|---------|
| `UtcTime` | Most events | Timestamp (duplicate of System/TimeCreated) |
| `ProcessGuid` | 1, 3, 5, 7, 8, 10, 11 | Unique process identifier |
| `ProcessId` | 1, 3, 5, 7, 8, 10, 11 | Process PID |
| `Image` | 1, 3, 5, 7, 8, 10, 11 | Executable path |
| `User` | 1, 3, 7, 8, 10, 11 | Domain\Username |
| `RuleName` | All events (if configured) | Sysmon rule that matched |

### **Event-Specific Fields**

Each event type has **unique fields**:

#### **Event ID 1: Process Creation**
```xml
<Data Name="ProcessGuid">{...}</Data>
<Data Name="ProcessId">1234</Data>
<Data Name="Image">C:\Windows\System32\cmd.exe</Data>
<Data Name="FileVersion">10.0.19041.1</Data>
<Data Name="Description">Windows Command Processor</Data>
<Data Name="Product">Microsoft Windows Operating System</Data>
<Data Name="Company">Microsoft Corporation</Data>
<Data Name="OriginalFileName">Cmd.Exe</Data>
<Data Name="CommandLine">cmd.exe /c whoami</Data>
<Data Name="CurrentDirectory">C:\Windows\system32\</Data>
<Data Name="User">DOMAIN\username</Data>
<Data Name="LogonGuid">{...}</Data>
<Data Name="LogonId">0x3e7</Data>
<Data Name="TerminalSessionId">1</Data>
<Data Name="IntegrityLevel">High</Data>
<Data Name="Hashes">SHA256=...,MD5=...,IMPHASH=...</Data>
<Data Name="ParentProcessGuid">{...}</Data>
<Data Name="ParentProcessId">4892</Data>
<Data Name="ParentImage">C:\Windows\explorer.exe</Data>
<Data Name="ParentCommandLine">C:\Windows\Explorer.EXE</Data>
<Data Name="ParentUser">DOMAIN\username</Data>
```

#### **Event ID 3: Network Connection**
```xml
<Data Name="ProcessGuid">{...}</Data>
<Data Name="ProcessId">7832</Data>
<Data Name="Image">C:\Windows\System32\rundll32.exe</Data>
<Data Name="User">NT AUTHORITY\SYSTEM</Data>
<Data Name="Protocol">tcp</Data>
<Data Name="Initiated">true</Data>
<Data Name="SourceIsIpv6">false</Data>
<Data Name="SourceIp">10.23.45.142</Data>
<Data Name="SourceHostname">WORKSTATION-142</Data>
<Data Name="SourcePort">52341</Data>
<Data Name="SourcePortName">-</Data>
<Data Name="DestinationIsIpv6">false</Data>
<Data Name="DestinationIp">185.220.101.47</Data>
<Data Name="DestinationHostname">cdn-services-update.com</Data>
<Data Name="DestinationPort">443</Data>
<Data Name="DestinationPortName">https</Data>
```

#### **Event ID 7: Image/DLL Loaded**
```xml
<Data Name="ProcessGuid">{...}</Data>
<Data Name="ProcessId">4628</Data>
<Data Name="Image">C:\Program Files\DefenseTrack\DefenseTrack.exe</Data>
<Data Name="ImageLoaded">C:\Windows\Temp\msvcr120_compat.dll</Data>
<Data Name="FileVersion">-</Data>
<Data Name="Description">-</Data>
<Data Name="Product">-</Data>
<Data Name="Company">-</Data>
<Data Name="OriginalFileName">-</Data>
<Data Name="Hashes">SHA256=...,MD5=...,IMPHASH=...</Data>
<Data Name="Signed">false</Data>
<Data Name="Signature">-</Data>
<Data Name="SignatureStatus">Unsigned</Data>
<Data Name="User">DOMAIN\username</Data>
```

#### **Event ID 8: CreateRemoteThread**
```xml
<Data Name="SourceProcessGuid">{...}</Data>
<Data Name="SourceProcessId">4628</Data>
<Data Name="SourceImage">C:\Program Files\DefenseTrack\DefenseTrack.exe</Data>
<Data Name="TargetProcessGuid">{...}</Data>
<Data Name="TargetProcessId">1892</Data>
<Data Name="TargetImage">C:\Windows\System32\svchost.exe</Data>
<Data Name="NewThreadId">6248</Data>
<Data Name="StartAddress">0x00007FF8B2A40000</Data>
<Data Name="StartModule">C:\Windows\Temp\msvcr120_compat.dll</Data>
<Data Name="StartFunction">-</Data>
<Data Name="SourceUser">DOMAIN\username</Data>
<Data Name="TargetUser">NT AUTHORITY\SYSTEM</Data>
```

#### **Event ID 10: ProcessAccess**
```xml
<Data Name="SourceProcessGuid">{...}</Data>
<Data Name="SourceProcessId">8756</Data>
<Data Name="SourceImage">C:\Users\Public\Downloads\mim.exe</Data>
<Data Name="TargetProcessGuid">{...}</Data>
<Data Name="TargetProcessId">676</Data>
<Data Name="TargetImage">C:\Windows\System32\lsass.exe</Data>
<Data Name="GrantedAccess">0x1FFFFF</Data>
<Data Name="CallTrace">C:\Windows\SYSTEM32\ntdll.dll+9d4c4|...</Data>
<Data Name="SourceUser">DOMAIN\username</Data>
<Data Name="TargetUser">NT AUTHORITY\SYSTEM</Data>
```

#### **Event ID 11: FileCreate**
```xml
<Data Name="ProcessGuid">{...}</Data>
<Data Name="ProcessId">8924</Data>
<Data Name="Image">C:\Windows\System32\xcopy.exe</Data>
<Data Name="TargetFilename">E:\backup\Nuclear_Sites_2025.xlsx</Data>
<Data Name="CreationUtcTime">2025-12-01 14:24:15.789</Data>
<Data Name="User">DOMAIN\username</Data>
```

#### **Event ID 22: DNSQuery**
```xml
<Data Name="ProcessGuid">{...}</Data>
<Data Name="ProcessId">3948</Data>
<Data Name="QueryName">4E5353414C41535349464945442D52455041E4.exfil-data.tk</Data>
<Data Name="QueryStatus">0</Data>
<Data Name="QueryResults">type: 1 TXT exfil-chunk-received-ack</Data>
<Data Name="Image">C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe</Data>
<Data Name="User">DOMAIN\username</Data>
```

---

## 📊 All 29 Sysmon Event Types

| Event ID | Event Name | Key Unique Fields |
|----------|------------|-------------------|
| **1** | ProcessCreate | CommandLine, ParentProcessId, ParentImage, Hashes |
| **2** | FileCreateTime | TargetFilename, CreationUtcTime, PreviousCreationUtcTime |
| **3** | NetworkConnect | SourceIp, SourcePort, DestinationIp, DestinationPort, Protocol |
| **5** | ProcessTerminate | (No unique fields beyond process info) |
| **6** | DriverLoad | ImageLoaded, Signed, Signature, SignatureStatus |
| **7** | ImageLoad | ImageLoaded, Signed, Signature, SignatureStatus |
| **8** | CreateRemoteThread | SourceProcessId, TargetProcessId, NewThreadId, StartAddress |
| **9** | RawAccessRead | Device |
| **10** | ProcessAccess | SourceProcessId, TargetProcessId, GrantedAccess, CallTrace |
| **11** | FileCreate | TargetFilename, CreationUtcTime |
| **12** | RegistryEvent (Create) | TargetObject, EventType |
| **13** | RegistryEvent (SetValue) | TargetObject, Details, EventType |
| **14** | RegistryEvent (Rename) | TargetObject, NewName, EventType |
| **15** | FileCreateStreamHash | TargetFilename, Contents, Hash |
| **17** | PipeEvent (Created) | PipeName |
| **18** | PipeEvent (Connected) | PipeName |
| **19** | WmiEvent (Filter) | EventNamespace, Name, Query |
| **20** | WmiEvent (Consumer) | Type, Destination |
| **21** | WmiEvent (Binding) | Consumer, Filter |
| **22** | DNSQuery | QueryName, QueryStatus, QueryResults |
| **23** | FileDelete | TargetFilename, Hashes, IsExecutable |
| **24** | ClipboardChange | ClientInfo, Hashes, Archived |
| **25** | ProcessTampering | Type (indicates tampering type) |
| **26** | FileDeleteDetected | TargetFilename, Hashes, IsExecutable |
| **27** | FileBlockExecutable | TargetFilename, Hashes |
| **28** | FileBlockShredding | TargetFilename |
| **29** | FileExecutableDetected | TargetFilename, Hashes |

---

## 🎯 Implications for OCSF Transformation

### **What This Means:**

1. **System Section Parsing**: Can use **one parser** for all Sysmon events
   - `TimeCreated/@SystemTime` → `time`
   - `Computer` → `device.hostname`
   - `EventID` → determines OCSF class mapping

2. **EventData Section Parsing**: Requires **event-type-specific logic**
   - Event ID 1: Extract `CommandLine`, `ParentProcessId`, etc.
   - Event ID 3: Extract `SourceIp`, `DestinationIp`, etc.
   - Event ID 7: Extract `ImageLoaded`, `Signed`, etc.

3. **Field Name Consistency Within Event Type**:
   - ✅ Field names are **consistent** for the same Event ID
   - ✅ Event ID 1 always has `CommandLine`, `ParentProcessId`, etc.
   - ✅ Event ID 3 always has `SourceIp`, `DestinationIp`, etc.

### **OCSF Playground Handles This:**

The AI understands:
- **Common structure** (System section) is the same
- **Event-specific fields** (EventData) vary by Event ID
- **Generates appropriate parsing logic** based on event type

Example:
```python
def transform_sysmon_event(xml_string: str) -> dict:
    root = ET.fromstring(xml_string)

    # Parse System (same for all events)
    system = root.find('.//System', namespaces)
    event_id = int(system.find('EventID').text)

    # Parse EventData (event-specific)
    event_data = {}
    for data in root.findall('.//EventData/Data', namespaces):
        field_name = data.get('Name')
        event_data[field_name] = data.text

    # Map to OCSF based on event_id
    if event_id == 1:  # Process Creation
        return map_process_creation(event_data)
    elif event_id == 3:  # Network Connection
        return map_network_connection(event_data)
    # ... etc
```

---

## ✅ Summary: Schema Consistency

| Component | Consistent? | Details |
|-----------|-------------|---------|
| **XML Namespace** | ✅ Yes | Always `http://schemas.microsoft.com/win/2004/08/events/event` |
| **Root Element** | ✅ Yes | Always `<Event>` |
| **System Section** | ✅ Yes | Same structure, same fields |
| **System/Provider** | ✅ Yes | Always "Microsoft-Windows-Sysmon" |
| **System/Channel** | ✅ Yes | Always "Microsoft-Windows-Sysmon/Operational" |
| **System/EventID** | ⚠️ Varies | 1-29 (determines event type) |
| **EventData Section** | ❌ No | Unique per event type |
| **EventData Fields** | ❌ No | Different fields per Event ID |
| **Field Naming** | ✅ Yes | Uses `<Data Name="...">` format |

---

## 🔧 Practical Impact for Your Demo

### **Good News:**
✅ One transformation pipeline handles all Sysmon event types
✅ System section parsing is universal
✅ Field names within each event type are consistent
✅ OCSF Playground AI understands event-specific fields

### **What You Need:**
- One transformer **per Sysmon Event ID** you care about
- Or one **intelligent transformer** that dispatches based on Event ID

### **Example Multi-Event Transformer:**

```python
def transform_sysmon_to_ocsf(xml_string: str) -> dict:
    """
    Universal Sysmon → OCSF transformer
    Handles all Sysmon event types
    """
    root = ET.fromstring(xml_string)
    event_id = int(root.find('.//EventID', namespaces).text)

    # Dispatch to event-specific handler
    handlers = {
        1: transform_process_creation,      # → OCSF Process Activity (1007)
        3: transform_network_connection,    # → OCSF Network Activity (4001)
        7: transform_image_load,            # → OCSF Process Activity (1007)
        8: transform_remote_thread,         # → OCSF Process Activity (1007)
        10: transform_process_access,       # → OCSF Process Activity (1007)
        11: transform_file_create,          # → OCSF File System Activity (4010)
        22: transform_dns_query,            # → OCSF Network Activity (4001)
    }

    handler = handlers.get(event_id)
    if handler:
        return handler(root)
    else:
        return transform_generic(root)
```

---

## 🎯 Bottom Line

**Question:** "Is Sysmon XML event schema the same for all types of events?"

**Answer:**
- **System section**: ✅ YES - 100% consistent
- **EventData section**: ❌ NO - Unique per event type
- **Overall**: ⚠️ **Partially consistent** - same structure, different content

**For OCSF transformation:**
- You can parse the System section with **one parser**
- You need **event-specific logic** for EventData fields
- The OCSF Playground handles this automatically via AI

**For your Splunk demo:**
- All events will have standard OCSF fields (`time`, `device.hostname`, etc.)
- Event-specific fields map correctly (`process.pid`, `dst_endpoint.ip`, etc.)
- Correlation works perfectly because OCSF normalizes the differences
