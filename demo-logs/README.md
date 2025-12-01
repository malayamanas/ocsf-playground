# National Security Demo Logs for OCSF Playground

This directory contains **realistic Windows Event Logs and Sysmon logs** specifically designed for demonstrating the OCSF Playground to **National Security SOC leadership**. Each scenario represents real-world threat patterns commonly encountered in government and defense networks.

---

## 📁 Scenario Files

### **Scenario 1: Insider Threat - USB Data Exfiltration**
**File:** `scenario1-insider-threat-usb-exfiltration.xml`

**Threat Summary:**
- Employee "john.miller" at NSA workstation inserts unauthorized USB drive
- Copies TOP SECRET/SCI classified document to external media
- Uses `xcopy` command to transfer "Nuclear_Sites_2025.xlsx"

**Attack Timeline:**
1. **14:23:45** - USB device inserted (Windows Event ID 4663)
2. **14:24:12** - Suspicious `xcopy.exe` process launched (Sysmon Event ID 1)
3. **14:24:15** - File written to USB drive E:\ (Sysmon Event ID 11)
4. **14:24:10** - Classified file accessed (Windows Event ID 4663)

**MITRE ATT&CK Techniques:**
- T1052: Exfiltration Over Physical Medium
- T1052.001: Exfiltration over USB

**Recommended OCSF Event Classes:**
- Device Activity (for USB insertion)
- Process Activity (for xcopy execution)
- File System Activity (for file creation/access)

**Key IOCs:**
- File: `Nuclear_Sites_2025.xlsx`
- User: `NATSEC\john.miller`
- Device: USB drive mounted as E:\
- Classification: TOP SECRET//SCI

---

### **Scenario 2: APT - Lateral Movement & C2 Communication**
**File:** `scenario2-apt-lateral-movement-c2.xml`

**Threat Summary:**
- Advanced Persistent Threat (APT29-style) compromises DOD workstation
- Establishes Command & Control using `rundll32.exe`
- Uses PowerShell with encoded commands for stealth
- Lateral movement via PsExec to Domain Controller
- Establishes persistence via Registry Run key

**Attack Timeline:**
1. **09:15:34** - C2 connection to `cdn-services-update.com` (185.220.101.47) - Sysmon Event ID 3
2. **09:16:02** - PowerShell with base64-encoded payload (Sysmon Event ID 1)
3. **09:18:45** - Network logon to DC01 via NTLM (Windows Event ID 4624)
4. **09:18:47** - PsExec service installed on Domain Controller (Sysmon Event ID 1)
5. **09:19:15** - Registry persistence established (Sysmon Event ID 13)

**MITRE ATT&CK Techniques:**
- T1071.001: Application Layer Protocol (Web Protocols)
- T1059.001: PowerShell
- T1021.002: Remote Services (SMB/Windows Admin Shares)
- T1547.001: Boot or Logon Autostart Execution (Registry Run Keys)

**Recommended OCSF Event Classes:**
- Network Activity (for C2 connections)
- Process Activity (for PowerShell/PsExec)
- Authentication (for lateral movement)
- System Activity (for registry modifications)

**Key IOCs:**
- C2 Domain: `cdn-services-update.com`
- C2 IP: `185.220.101.47`
- Tool: PsExec (Sysinternals)
- User: `DEFENSE\Administrator`
- Source: `DOD-WORKSTATION-142`

---

### **Scenario 3: Data Exfiltration via DNS Tunneling**
**File:** `scenario3-data-exfiltration-dns-tunneling.xml`

**Threat Summary:**
- CIA analyst workstation compromised
- Exfiltrates "Agent_List_2025.pdf" via DNS tunneling
- Uses PowerShell script `dns_exfil.ps1` to encode data in DNS queries
- Attacker-controlled domain: `exfil-data.tk`

**Attack Timeline:**
1. **16:44:55** - Suspicious PowerShell script created in Temp folder (Sysmon Event ID 11)
2. **16:45:00** - PowerShell executes DNS exfiltration script (Sysmon Event ID 1)
3. **16:45:12** - First DNS query with encoded data "4E5353414C41..." (Sysmon Event ID 22)
4. **16:45:13** - Second DNS query with encoded data "544F505345..." (Sysmon Event ID 22)
5. **16:45:12** - Firewall allows DNS connection to 198.51.100.47 (Windows Event ID 5156)

**MITRE ATT&CK Techniques:**
- T1071.004: Application Layer Protocol (DNS)
- T1048.003: Exfiltration Over Alternative Protocol
- T1059.001: PowerShell

**Recommended OCSF Event Classes:**
- Network Activity (DNS queries)
- Process Activity (PowerShell script)
- File System Activity (script creation)

**Key IOCs:**
- Exfil Domain: `exfil-data.tk`
- DNS Server: `198.51.100.47`
- Script: `C:\Users\sarah.chen\AppData\Local\Temp\dns_exfil.ps1`
- Exfiltrated File: `Agent_List_2025.pdf`
- User: `INTELLIGENCE\sarah.chen`

**Decoded DNS Query (Hex to ASCII):**
- Query 1: "NSACLASSIFIED-REPA..."
- Query 2: "TOPSECRET-AGENT-LIS..."

---

### **Scenario 4: Credential Theft using Mimikatz**
**File:** `scenario4-credential-theft-mimikatz.xml`

**Threat Summary:**
- Attacker runs Mimikatz on FBI field office workstation
- Dumps credentials from LSASS process memory
- Uses SeDebugPrivilege to access protected process
- Outputs credentials to `credentials.txt`

**Attack Timeline:**
1. **11:30:15** - Mimikatz process launched with LSASS dumping arguments (Sysmon Event ID 1)
2. **11:30:15** - SeDebugPrivilege used (Windows Event ID 4673)
3. **11:30:16** - LSASS memory accessed with full permissions (Sysmon Event ID 10)
4. **11:30:16** - Remote thread created in LSASS process (Sysmon Event ID 8)
5. **11:30:18** - Credentials written to text file (Sysmon Event ID 11)

**MITRE ATT&CK Techniques:**
- T1003.001: OS Credential Dumping (LSASS Memory)
- T1055: Process Injection

**Recommended OCSF Event Classes:**
- Process Activity (Mimikatz execution, LSASS access)
- Security Finding (credential theft detection)
- File System Activity (credential file creation)

**Key IOCs:**
- Binary: `C:\Users\Public\Downloads\mim.exe`
- SHA256: `B4C5D6E7F8A9B0C1D2E3F4A5B6C7D8E9F0A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5`
- IMPHASH: `F1E2D3C4B5A6978809F0E1D2C3B4A596`
- Target Process: `lsass.exe` (PID 676)
- User: `FBI\admin.local`
- Output File: `credentials.txt`

---

### **Scenario 5: Ransomware Attack Chain**
**File:** `scenario5-ransomware-attack-chain.xml`

**Threat Summary:**
- BlackCat/ALPHV ransomware deployed via phishing email
- Excel macro executes PowerShell downloader
- Downloads ransomware payload from `malicious-cdn.xyz`
- Encrypts files with `.blackcat` extension
- Deletes shadow copies to prevent recovery
- Drops ransom note `RECOVER-FILES-README.txt`

**Attack Timeline:**
1. **08:15:23** - Malicious macro executes PowerShell (Sysmon Event ID 1)
2. **08:15:24** - Downloads stage 2 payload (Sysmon Event ID 3)
3. **08:15:26** - Ransomware binary written to disk (Sysmon Event ID 11)
4. **08:15:30** - Ransomware executes with access token (Sysmon Event ID 1)
5. **08:15:45** - Files encrypted with `.blackcat` extension (Sysmon Event ID 11)
6. **08:15:46** - Original files deleted (Sysmon Event ID 23)
7. **08:15:55** - Shadow copies deleted via `vssadmin` (Windows Event ID 4688)
8. **08:16:00** - Ransom note created on desktop (Sysmon Event ID 11)

**MITRE ATT&CK Techniques:**
- T1204.002: User Execution (Malicious File)
- T1105: Ingress Tool Transfer
- T1486: Data Encrypted for Impact
- T1485: Data Destruction
- T1491.001: Defacement (Internal Defacement)

**Recommended OCSF Event Classes:**
- Process Activity (PowerShell, ransomware execution)
- Network Activity (payload download)
- File System Activity (encryption, deletion, ransom note)
- System Activity (shadow copy deletion)

**Key IOCs:**
- C2/Download: `malicious-cdn.xyz` (203.0.113.89)
- Binary: `C:\ProgramData\Microsoft\Windows\SystemData\encrypt.exe`
- SHA256: `D8E9F0A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6E7F8A9B0C1D2E3F4A5B6C7D8E9`
- File Extension: `.blackcat`
- Ransom Note: `RECOVER-FILES-README.txt`
- User: `TREASURY\robert.smith`

---

## 🎬 Using These Logs in Video Demo

### **Recommended Demo Flow:**

1. **Start with Scenario 2 (APT)** - Shows sophisticated attack with multiple stages
2. **Follow with Scenario 3 (DNS Tunneling)** - Demonstrates covert channel detection
3. **Conclude with Scenario 5 (Ransomware)** - High-impact, easy to explain to executives

### **For Each Scenario:**

1. **Import Log** (use "Single Entry" parse mode)
2. **Select OCSF Version** (recommend v1.7.0 for latest features)
3. **AI Categorization** → Show recommendation
4. **Entity Analysis** → Highlight extracted IOCs
5. **Pattern Extraction** → Show Python code
6. **Transformer Creation** → Test with sample
7. **Show OCSF Output** → Standardized JSON with IOCs clearly mapped

### **Key Points to Emphasize:**

✅ **Speed**: "From raw XML to OCSF JSON in under 2 minutes"
✅ **Accuracy**: "AI correctly identifies threat indicators automatically"
✅ **Deployment**: "Copy this code to all 30 SOCs - instant standardization"
✅ **IOC Correlation**: "Now all SOCs use same field names - instant correlation"

---

## 🔍 IOC Summary Across All Scenarios

### **Malicious Domains/IPs:**
- `cdn-services-update.com` (185.220.101.47) - APT C2
- `exfil-data.tk` (198.51.100.47) - DNS exfiltration
- `malicious-cdn.xyz` (203.0.113.89) - Ransomware payload

### **Malicious Files:**
- `mim.exe` - Mimikatz (SHA256: B4C5D6E7...)
- `encrypt.exe` - BlackCat ransomware (SHA256: D8E9F0A1...)
- `dns_exfil.ps1` - DNS tunneling script
- `PSEXESVC.exe` - Lateral movement tool

### **Compromised Users:**
- `NATSEC\john.miller` - Insider threat
- `DEFENSE\Administrator` - APT lateral movement
- `INTELLIGENCE\sarah.chen` - DNS exfiltration
- `FBI\admin.local` - Credential theft
- `TREASURY\robert.smith` - Ransomware victim

### **Classified Data at Risk:**
- `Nuclear_Sites_2025.xlsx` - TOP SECRET//SCI
- `Agent_List_2025.pdf` - TOP SECRET
- `Financial_Report_2025.xlsx` - Ransomware encrypted

---

## 📊 OCSF Field Mapping Examples

### **Common Fields Across Scenarios:**

| Raw Field | OCSF Path | Example Value |
|-----------|-----------|---------------|
| `User` | `actor.user.name` | `NATSEC\john.miller` |
| `SourceIp` | `src_endpoint.ip` | `10.23.45.142` |
| `DestinationIp` | `dst_endpoint.ip` | `185.220.101.47` |
| `ProcessId` | `process.pid` | `8756` |
| `Image` | `process.file.path` | `C:\Windows\System32\cmd.exe` |
| `CommandLine` | `process.cmd_line` | `powershell.exe -NoP -NonI...` |
| `TimeCreated` | `time` | `2025-12-01T11:30:15.678Z` |
| `Computer` | `device.hostname` | `NSA-WORKSTATION-057.natsec.gov` |

---

## 🛠️ Technical Notes

### **Event Log Sources:**
- **Windows Security Events**: 4624, 4663, 4673, 4688, 5156
- **Sysmon Events**: 1, 3, 8, 10, 11, 13, 22, 23

### **XML Structure:**
All logs follow Windows Event Log XML schema with:
- `<System>` section: Event metadata (ID, time, computer)
- `<EventData>` section: Event-specific details
- `RuleName` attribute: MITRE ATT&CK technique mapping

### **Parse Mode:**
Use **"Single Entry"** mode when importing these logs to treat each XML event as one log entry.

### **OCSF Version Recommendation:**
Use **v1.7.0** for demos - it has the most comprehensive field coverage and demonstrates the multi-version capability.

---

## 📝 Attribution Notice

These logs are **synthetic/fabricated** for demonstration purposes. They represent realistic threat scenarios based on publicly documented TTPs but do not contain real operational data. All organizations, users, and data references are fictional.

**Organizations referenced:**
- NSA (National Security Agency)
- DOD (Department of Defense)
- CIA (Central Intelligence Agency)
- FBI (Federal Bureau of Investigation)
- US Treasury Department

All domain names, IP addresses, and file hashes are either reserved for documentation (RFC 5737) or randomly generated.

---

## 🎯 Success Metrics for Demo

After showing these scenarios, the audience should understand:

1. ✅ **Format-agnostic** - Handles any Windows/Sysmon log format
2. ✅ **AI-powered** - No manual mapping required
3. ✅ **Multi-version** - Supports OCSF v1.0.0 through v1.7.0
4. ✅ **Production-ready** - Generated code deploys to all SOCs
5. ✅ **IOC correlation** - Standardized fields enable cross-zone analysis

**Expected Outcome:** Client understands how OCSF normalization solves their 30-SOC fragmentation problem and enables centralized threat detection.
