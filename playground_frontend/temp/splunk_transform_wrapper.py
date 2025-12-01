#!/usr/bin/env python3
"""
Splunk Scripted Input wrapper for Apache Log OCSF Transformer
This script reads Apache access logs and outputs OCSF-formatted JSON events to stdout

Features:
- Checkpoint tracking to avoid duplicate events
- Log rotation detection
- Graceful error handling
- Memory-efficient line-by-line processing
"""

import sys
import json
import os
import hashlib
from transform import transformer

# Checkpoint file location (will be created in Splunk's modinput directory)
CHECKPOINT_DIR = os.getenv('SPLUNK_HOME', '/opt/splunk') + '/var/lib/splunk/modinputs'
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

def get_checkpoint_file(log_file_path):
    """Generate checkpoint filename based on log file path"""
    # Create a unique checkpoint file name based on the log file path
    path_hash = hashlib.md5(log_file_path.encode()).hexdigest()
    return os.path.join(CHECKPOINT_DIR, f'apache_ocsf_transform_{path_hash}.checkpoint')

def load_checkpoint(checkpoint_file):
    """
    Load checkpoint data (file inode and last processed position)
    Returns: (inode, position) tuple
    """
    try:
        if os.path.exists(checkpoint_file):
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
                return data.get('inode'), data.get('position', 0)
    except Exception as e:
        print(f"WARNING: Could not load checkpoint: {e}", file=sys.stderr)
    return None, 0

def save_checkpoint(checkpoint_file, inode, position):
    """Save checkpoint data (file inode and last processed position)"""
    try:
        with open(checkpoint_file, 'w') as f:
            json.dump({'inode': inode, 'position': position}, f)
    except Exception as e:
        print(f"ERROR: Could not save checkpoint: {e}", file=sys.stderr)

def get_file_inode(file_path):
    """Get file inode to detect log rotation"""
    try:
        return os.stat(file_path).st_ino
    except Exception:
        return None

def process_log_file(log_file_path):
    """
    Process log file with checkpoint tracking
    Only processes new lines since last run
    Detects log rotation and resets checkpoint if needed
    """
    checkpoint_file = get_checkpoint_file(log_file_path)

    # Get current file inode
    current_inode = get_file_inode(log_file_path)
    if current_inode is None:
        print(f"ERROR: Cannot access file {log_file_path}", file=sys.stderr)
        return

    # Load checkpoint
    saved_inode, saved_position = load_checkpoint(checkpoint_file)

    # Detect log rotation (inode changed or file is smaller than last position)
    file_size = os.path.getsize(log_file_path)
    if saved_inode != current_inode or file_size < saved_position:
        # Log was rotated, start from beginning
        print(f"INFO: Log rotation detected for {log_file_path}, starting from beginning", file=sys.stderr)
        saved_position = 0

    # Process file from checkpoint position
    events_processed = 0
    current_position = saved_position

    try:
        with open(log_file_path, 'r') as f:
            # Seek to last position
            if saved_position > 0:
                f.seek(saved_position)

            for line in f:
                current_position = f.tell()
                line = line.strip()

                if line:  # Skip empty lines
                    try:
                        ocsf_event = transformer(line)
                        # Output JSON to stdout (Splunk will index this)
                        print(json.dumps(ocsf_event))
                        sys.stdout.flush()
                        events_processed += 1
                    except Exception as e:
                        # Log errors to stderr (Splunk will capture in _internal logs)
                        print(f"ERROR processing line at position {current_position}: {e}", file=sys.stderr)
                        sys.stderr.flush()

                # Save checkpoint every 100 events to avoid too many writes
                if events_processed % 100 == 0:
                    save_checkpoint(checkpoint_file, current_inode, current_position)

        # Save final checkpoint
        save_checkpoint(checkpoint_file, current_inode, current_position)

        if events_processed > 0:
            print(f"INFO: Processed {events_processed} new events from {log_file_path}", file=sys.stderr)

    except Exception as e:
        print(f"ERROR reading file {log_file_path}: {e}", file=sys.stderr)
        # Save checkpoint even on error to avoid re-processing same lines
        save_checkpoint(checkpoint_file, current_inode, current_position)
        sys.exit(1)

def process_stdin():
    """
    Process input from stdin (for piped input or continuous monitoring)
    No checkpoint tracking for stdin mode
    """
    for line in sys.stdin:
        line = line.strip()
        if line:
            try:
                ocsf_event = transformer(line)
                print(json.dumps(ocsf_event))
                sys.stdout.flush()
            except Exception as e:
                print(f"ERROR processing line: {e}", file=sys.stderr)
                sys.stderr.flush()

def main():
    """
    Main function for Splunk scripted input.
    Reads log entries from a file (with checkpoint tracking) or stdin.
    """
    if len(sys.argv) > 1:
        # File mode with checkpoint tracking
        log_file_path = sys.argv[1]

        # Validate file exists
        if not os.path.exists(log_file_path):
            print(f"ERROR: Log file does not exist: {log_file_path}", file=sys.stderr)
            sys.exit(1)

        process_log_file(log_file_path)
    else:
        # Stdin mode (no checkpoint tracking)
        print("INFO: Reading from stdin (no checkpoint tracking)", file=sys.stderr)
        process_stdin()

if __name__ == "__main__":
    main()
