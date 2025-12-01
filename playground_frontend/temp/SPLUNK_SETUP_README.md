# Splunk - Apache OCSF Transformer Setup Guide
## Single-Node Splunk Configuration

This guide explains how to configure the Apache access log to OCSF transformer as a Splunk Scripted Input on a **single-node Splunk deployment** (all-in-one: search head + indexer).

## Overview

**What this does:**
- Reads Apache access logs (standard Combined Log Format)
- Transforms each log entry into OCSF (Open Cybersecurity Schema Framework) JSON
- Indexes OCSF events in Splunk for analysis and alerting
- Tracks processing checkpoints to avoid duplicate events
- Automatically handles log rotation

**Key Improvements (Production-Ready):**
- ✅ **Checkpoint tracking**: Prevents duplicate events by tracking file position and inode
- ✅ **Log rotation detection**: Automatically detects when logs are rotated
- ✅ **Security hardened**: Uses `start_by_shell = false` to prevent shell injection
- ✅ **Memory efficient**: Processes line-by-line instead of loading entire file
- ✅ **Search-time extraction**: Uses `KV_MODE = json` for flexible field extraction
- ✅ **Advanced routing**: Optional transforms.conf for data filtering and routing
- ✅ **Single-node optimized**: No outputs.conf needed, simpler architecture

**Components:**
1. `transform.py` - Core transformation logic (Apache log → OCSF JSON)
2. `splunk_transform_wrapper.py` - Splunk scripted input wrapper with checkpoint tracking
3. `inputs.conf.example` - Splunk input configuration
4. `props.conf.example` - Splunk field extraction configuration (search-time)
5. `transforms.conf.example` - Advanced routing, filtering, and field extraction (optional)

## Prerequisites

- **Single-node Splunk Enterprise** installed (search head + indexer on same machine)
- Python 3.6+ (comes with Splunk)
- Apache access logs in Combined Log Format
- Sufficient disk space for OCSF index

## Installation Steps

### Step 1: Copy Scripts to Splunk

```bash
# Set SPLUNK_HOME environment variable
export SPLUNK_HOME=/opt/splunkforwarder  # Adjust to your installation path

# Create scripts directory if it doesn't exist
mkdir -p $SPLUNK_HOME/bin/scripts

# Copy the transformer scripts
cp transform.py $SPLUNK_HOME/bin/scripts/
cp splunk_transform_wrapper.py $SPLUNK_HOME/bin/scripts/

# Make the wrapper executable
chmod +x $SPLUNK_HOME/bin/scripts/splunk_transform_wrapper.py
```

### Step 2: Create OCSF Index

```bash
# Create the OCSF index for storing transformed events
$SPLUNK_HOME/bin/splunk add index ocsf -auth admin:yourpassword

# Or via Splunk Web:
# Settings → Indexes → New Index → Name: "ocsf"
# Recommended settings:
#   - Max Size: 500GB+ (depending on log volume)
#   - Retention: 90 days (adjust as needed)
```

### Step 3: Configure inputs.conf

```bash
# Create app directory structure (recommended approach)
mkdir -p $SPLUNK_HOME/etc/apps/ocsf_apache_transform/local

# Copy and edit inputs.conf
cp inputs.conf.example $SPLUNK_HOME/etc/apps/ocsf_apache_transform/local/inputs.conf

# Edit the configuration
vi $SPLUNK_HOME/etc/apps/ocsf_apache_transform/local/inputs.conf
```

**Recommended production configuration:**

```ini
[script://$SPLUNK_HOME/bin/scripts/splunk_transform_wrapper.py /var/log/apache2/access.log]
disabled = 0
interval = 60
sourcetype = ocsf:http_activity
source = apache:ocsf_transform
index = ocsf
start_by_shell = false
```

**Key parameters to customize:**
- **Script path**: Update `/var/log/apache2/access.log` to your Apache log location
- **interval**: How often to run (in seconds). Default: 60 = every minute
- **index**: The Splunk index to send data to. Default: `ocsf`
- **sourcetype**: Must match props.conf configuration. Default: `ocsf:http_activity`
- **start_by_shell**: Set to `false` for security (Splunk best practice)

### Step 4: Configure props.conf

```bash
# Copy props.conf to your app directory
cp props.conf.example $SPLUNK_HOME/etc/apps/ocsf_apache_transform/local/props.conf

# Or to system/local:
cp props.conf.example $SPLUNK_HOME/etc/system/local/props.conf
```

**What this does:**
- Configures JSON parsing (search-time extraction with `KV_MODE = json`)
- Sets up timestamp extraction from OCSF "time" field (epoch milliseconds)
- Creates field aliases for nested OCSF fields (e.g., `src_endpoint.ip` → `src_ip`)
- Adds calculated fields (status_type, bytes_kb, etc.)

### Step 5: Configure transforms.conf (Optional)

For advanced use cases like data routing, filtering, or field extraction:

```bash
# Copy transforms.conf to your app directory
cp transforms.conf.example $SPLUNK_HOME/etc/apps/ocsf_apache_transform/local/transforms.conf
```

**Use cases:**
- Route server errors (5xx) to a separate security index
- Filter out health check or static asset requests
- Mask sensitive data in query strings or IPs
- Extract additional fields using regex

See `transforms.conf.example` for detailed examples.

### Step 6: Restart Splunk

```bash
$SPLUNK_HOME/bin/splunk restart
```

## Checkpoint Tracking

The wrapper script includes **automatic checkpoint tracking** to prevent duplicate events:

**How it works:**
- Tracks file inode and byte position for each log file
- Only processes new lines since last run
- Detects log rotation (inode changes) and resets automatically
- Saves checkpoints every 100 events for efficiency

**Checkpoint location:**
```bash
$SPLUNK_HOME/var/lib/splunk/modinputs/apache_ocsf_transform_*.checkpoint
```

**To reprocess logs from the beginning:**
```bash
# Stop Splunk
$SPLUNK_HOME/bin/splunk stop

# Remove checkpoint files
rm $SPLUNK_HOME/var/lib/splunk/modinputs/apache_ocsf_transform_*.checkpoint

# Restart Splunk
$SPLUNK_HOME/bin/splunk start
```

## Verification

### 1. Test the Script Manually

```bash
# Test with a sample Apache log line
echo '192.168.1.100 - - [22/Dec/2016:16:36:02 +0300] GET /index.html HTTP/1.1 200 512 - Mozilla/5.0' | \
  $SPLUNK_HOME/bin/splunk cmd python $SPLUNK_HOME/bin/scripts/splunk_transform_wrapper.py

# Expected output: JSON with OCSF fields
# {"src_endpoint": {"ip": "192.168.1.100"}, "time": "1482417362000", ...}
```

### 2. Check Splunk Internal Logs

```bash
# View scripted input execution logs
tail -f $SPLUNK_HOME/var/log/splunk/splunkd.log | grep ExecProcessor

# Or search in Splunk:
# index=_internal source=*splunkd.log* component=ExecProcessor
```

### 3. Search for OCSF Events

In Splunk Web search:

```spl
index=ocsf sourcetype=ocsf:http_activity
| head 10
```

### 4. Verify Field Extraction

```spl
index=ocsf sourcetype=ocsf:http_activity
| table _time src_ip http_method url status bytes
```

## Troubleshooting

### Issue: No data appearing in Splunk

**Check 1: Script execution**
```bash
# View script output manually (test mode)
$SPLUNK_HOME/bin/splunk cmd python $SPLUNK_HOME/bin/scripts/splunk_transform_wrapper.py /var/log/apache2/access.log

# Check for INFO messages about processed events
```

**Check 2: Script permissions**
```bash
ls -la $SPLUNK_HOME/bin/scripts/splunk_transform_wrapper.py
# Should be executable and readable by splunk user
chmod +x $SPLUNK_HOME/bin/scripts/splunk_transform_wrapper.py
chown splunk:splunk $SPLUNK_HOME/bin/scripts/*.py
```

**Check 3: Splunk internal logs**
```spl
index=_internal source=*splunkd.log* component=ExecProcessor
| search error OR fail OR exception OR "apache_ocsf"
```

**Check 4: Input configuration**
```bash
# List all configured inputs
$SPLUNK_HOME/bin/splunk list inputstatus

# Check if input is enabled
$SPLUNK_HOME/bin/splunk btool inputs list script
```

**Check 5: Checkpoint issues**
```bash
# Check if checkpoints exist and are being updated
ls -lh $SPLUNK_HOME/var/lib/splunk/modinputs/apache_ocsf_transform_*.checkpoint
cat $SPLUNK_HOME/var/lib/splunk/modinputs/apache_ocsf_transform_*.checkpoint
```

### Issue: Script runs but no events indexed

**Check 1: Index exists**
```bash
$SPLUNK_HOME/bin/splunk list index
# Should show "ocsf" in the list

# Create if missing:
$SPLUNK_HOME/bin/splunk add index ocsf -auth admin:password
```

**Check 2: Raw data in index**
```spl
index=ocsf
| head 100
| table _raw, _time, sourcetype
```

**Check 3: Check for parsing errors**
```spl
index=_internal source=*splunkd.log* "apache_ocsf" OR "transform.py"
| search ERROR OR WARNING
```

### Issue: Fields not extracting properly

**Check 1: props.conf deployed**
```bash
# Check effective props.conf configuration
$SPLUNK_HOME/bin/splunk btool props list ocsf:http_activity

# Should show:
# - KV_MODE = json
# - SHOULD_LINEMERGE = false
# - Field aliases (FIELDALIAS-*)
```

**Check 2: Test JSON extraction manually**
```spl
index=ocsf sourcetype=ocsf:http_activity
| head 1
| spath
| table src_endpoint.ip http_request.http_method http_response.code status src_ip
```

**Check 3: Restart Splunk after props.conf changes**
```bash
# props.conf changes require restart
$SPLUNK_HOME/bin/splunk restart
```

**Check 4: Verify field aliases**
```spl
index=ocsf sourcetype=ocsf:http_activity
| fieldsummary
| search field="src_ip" OR field="status" OR field="http_method"
```

### Issue: Duplicate events

**Cause:** Checkpoint tracking issue or script running multiple times

**Solution 1: Reset checkpoints**
```bash
$SPLUNK_HOME/bin/splunk stop
rm $SPLUNK_HOME/var/lib/splunk/modinputs/apache_ocsf_transform_*.checkpoint
$SPLUNK_HOME/bin/splunk start
```

**Solution 2: Check for duplicate inputs.conf stanzas**
```bash
# Search for duplicate configurations
$SPLUNK_HOME/bin/splunk btool inputs list script | grep -A10 "splunk_transform_wrapper"
```

### Issue: Processing large files takes too long

**Solution 1: Increase interval**
```ini
[script://...]
interval = 300  # Run every 5 minutes instead of every minute
```

**Solution 2: Use log rotation**
Ensure Apache logs are rotated regularly (daily/weekly) to keep file sizes manageable.

**Solution 3: Monitor checkpoint progress**
```bash
# Watch checkpoint updates in real-time
watch -n 5 'cat $SPLUNK_HOME/var/lib/splunk/modinputs/apache_ocsf_transform_*.checkpoint'
```

## Configuration Options

### Execution Frequency

**Interval-based (every N seconds):**
```ini
interval = 60   # Every minute
interval = 300  # Every 5 minutes
interval = 3600 # Every hour
```

**Cron-based (specific times):**
```ini
schedule = 0 2 * * *      # Daily at 2 AM
schedule = */15 * * * *   # Every 15 minutes
schedule = 0 */4 * * *    # Every 4 hours
schedule = 0 0 * * 0      # Weekly on Sunday midnight
```

### Multiple Log Files

Process multiple Apache instances:

```ini
[script://$SPLUNK_HOME/bin/scripts/splunk_transform_wrapper.py /var/log/apache2/access.log]
disabled = 0
interval = 60
sourcetype = ocsf:http_activity
source = apache:web1
index = ocsf

[script://$SPLUNK_HOME/bin/scripts/splunk_transform_wrapper.py /var/log/httpd/ssl_access.log]
disabled = 0
interval = 60
sourcetype = ocsf:http_activity:ssl
source = apache:web2:ssl
index = ocsf
```

## Architecture Overview (Single-Node)

**Data Flow:**
```
Apache Log File → Scripted Input (wrapper) → Transform → OCSF JSON → Splunk Index → Search Head
     ↓                    ↓                                  ↓
  Checkpoint         Regex Parser                      props.conf parsing
   Tracking          (transform.py)                    (KV_MODE = json)
```

**Key Components:**
1. **Scripted Input**: Runs every N seconds (configurable interval)
2. **Checkpoint Tracking**: Stores file position to avoid re-processing
3. **Log Rotation Detection**: Monitors file inode changes
4. **Transform Logic**: Regex-based Apache log parsing → OCSF JSON
5. **Search-time Parsing**: JSON field extraction using KV_MODE

**Advantages of Single-Node Setup:**
- ✅ No outputs.conf needed (data stays local)
- ✅ Simpler configuration (no indexer/search head split)
- ✅ Search-time field extraction (more flexible than index-time)
- ✅ No network overhead for forwarding

## Performance Considerations

### Memory Usage
- **Improved**: Wrapper script processes line-by-line (not loading entire file)
- **Checkpoint tracking**: Only reads new lines since last run
- **Memory per execution**: Minimal (~10-50MB depending on batch size)
- **Best practice**: Use log rotation to keep individual files under 1GB

### CPU Impact
- **Regex parsing**: Moderately CPU-intensive (~1-5% CPU for 1000 events/min)
- **Transform overhead**: ~1-2ms per log line
- **Adjust interval**: Balance freshness vs. CPU load (60s = good default)
- **Recommended**: Run on dedicated Splunk server, not production app server

### Disk I/O
- **Checkpoint writes**: Every 100 events (minimal overhead)
- **Index growth**: ~500-1000 bytes per event
- **Example**: 1000 req/min = ~43GB/month (uncompressed)
- **Splunk compression**: Typically 50-70% reduction in disk usage

### Throughput
- **Typical performance**: 10,000-50,000 events/minute on modern hardware
- **Network bandwidth**: Not applicable for single-node (local indexing)
- **Bottleneck**: Usually the regex parsing, not Splunk indexing

## Advanced: Streaming Mode

For real-time processing with `tail -f`:

**Modified wrapper script:**
```python
#!/usr/bin/env python3
import sys
import json
import subprocess
from transform import transformer

def main():
    # Use tail -f to stream new lines
    tail_process = subprocess.Popen(
        ['tail', '-F', '/var/log/apache2/access.log'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    for line in tail_process.stdout:
        line = line.strip()
        if line:
            try:
                ocsf_event = transformer(line)
                print(json.dumps(ocsf_event))
                sys.stdout.flush()
            except Exception as e:
                print(f"ERROR: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
```

**inputs.conf for streaming:**
```ini
[script://$SPLUNK_HOME/bin/scripts/splunk_transform_wrapper_stream.py]
disabled = 0
sourcetype = ocsf:http_activity
source = apache:streaming
index = ocsf
# No interval - runs continuously
```

## Security Considerations

### Script Security
1. **File permissions**: Ensure only splunk user can modify scripts
   ```bash
   chown splunk:splunk $SPLUNK_HOME/bin/scripts/*.py
   chmod 750 $SPLUNK_HOME/bin/scripts/*.py
   ```

2. **start_by_shell = false**: Prevents shell injection vulnerabilities (configured in inputs.conf)

3. **Input validation**: The wrapper script validates file paths and handles errors gracefully

### Log Access
4. **Apache log permissions**: Splunk user needs read access
   ```bash
   # Add splunk user to apache group
   usermod -a -G www-data splunk  # Ubuntu/Debian
   usermod -a -G apache splunk     # RHEL/CentOS

   # Or make logs readable
   chmod 644 /var/log/apache2/*.log
   ```

### Splunk Security
5. **Index permissions**: Configure role-based access control (RBAC)
   ```
   Settings → Access Controls → Roles → Create role "ocsf_analyst"
   Assign read permissions to "ocsf" index only
   ```

6. **TLS/SSL**: For single-node, not applicable (no network forwarding)

7. **Data sanitization**: Consider using transforms.conf to mask sensitive data
   - Query strings with authentication tokens
   - Source IPs (GDPR compliance)
   - User agents with identifying information

### Audit Trail
8. **Monitor script changes**: Enable file integrity monitoring on script files
9. **Track checkpoint modifications**: Alert on unexpected checkpoint deletions

## Next Steps

### 1. Create Dashboards
Build visualizations for OCSF HTTP activity:
```spl
# Top requesting IPs
index=ocsf sourcetype=ocsf:http_activity
| stats count by src_ip
| sort -count
| head 10

# HTTP status over time
index=ocsf sourcetype=ocsf:http_activity
| timechart count by status_type

# Top URLs
index=ocsf sourcetype=ocsf:http_activity
| stats count avg(bytes) by url
| sort -count
```

### 2. Set Up Alerts
Monitor for security events:
```spl
# Alert on 5xx errors
index=ocsf sourcetype=ocsf:http_activity status>=500
| stats count by src_ip, url
| where count > 10

# Alert on 4xx errors (potential attacks)
index=ocsf sourcetype=ocsf:http_activity status=404
| stats count by src_ip
| where count > 100
```

### 3. Integrate with Splunk Enterprise Security (ES)
- Map OCSF fields to CIM (Common Information Model)
- Create correlation searches
- Add to Web datamodel

### 4. Extend Transformer
- Support additional log formats (Nginx, IIS, etc.)
- Add enrichment (GeoIP, User-Agent parsing)
- Include performance metrics

### 5. Advanced Analytics
- Threat intel lookups (malicious IPs)
- Anomaly detection (ML Toolkit)
- User behavior analytics

## Support

For issues with:
- **Transform logic**: Check `transform.py` parsing regex
- **Splunk integration**: Review inputs.conf and props.conf
- **OCSF schema**: Reference OCSF documentation at https://schema.ocsf.io/

## References

- [Splunk Scripted Inputs Documentation](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Inputsconf)
- [OCSF Schema v1.1.0](https://schema.ocsf.io/1.1.0/)
- [Apache Combined Log Format](https://httpd.apache.org/docs/current/logs.html#combined)
