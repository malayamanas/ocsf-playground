import React, { useState } from 'react';
import { FormField, Textarea, RadioGroup, RadioGroupProps } from '@cloudscape-design/components';
import ModalDialog from '../common/ModalDialog';

export interface ImportDialogProps {
  visible: boolean;
  onClose: () => void;
  onImport: (logEntries: string[]) => void;
}

const ImportDialog: React.FC<ImportDialogProps> = ({
  visible,
  onClose,
  onImport
}) => {
  const [importText, setImportText] = useState('');
  const [parseMode, setParseMode] = useState('single');

  const handleImport = () => {
    if (importText.trim()) {
      let logEntries: string[];

      if (parseMode === 'single') {
        // Treat entire input as a single log entry (for multi-line logs like XML)
        logEntries = [importText.trim()];
      } else if (parseMode === 'xml-events') {
        // Split by XML Event tags for Windows Event Logs
        const eventMatches = importText.match(/<Event[^>]*>[\s\S]*?<\/Event>/g);
        logEntries = eventMatches ? eventMatches.map(e => e.trim()) : [importText.trim()];
      } else if (parseMode === 'json-array') {
        // Parse JSON array of log entries
        try {
          const parsed = JSON.parse(importText);
          if (Array.isArray(parsed)) {
            logEntries = parsed.map(item =>
              typeof item === 'string' ? item : JSON.stringify(item, null, 2)
            );
          } else {
            logEntries = [JSON.stringify(parsed, null, 2)];
          }
        } catch (e) {
          logEntries = [importText.trim()];
        }
      } else if (parseMode === 'blank-line') {
        // Split by blank lines (double newline)
        logEntries = importText
          .split(/\n\s*\n/)
          .map(entry => entry.trim())
          .filter(entry => entry.length > 0);
      } else {
        // Default: split by new line (one per line)
        logEntries = importText
          .split('\n')
          .filter(entry => entry.trim().length > 0);
      }

      onImport(logEntries);
      setImportText(''); // Clear the input after import
    }
  };

  const parseModeOptions: RadioGroupProps.RadioButtonDefinition[] = [
    {
      value: 'single',
      label: 'Single Entry',
      description: 'Treat entire input as one log entry (e.g., multi-line XML, JSON)'
    },
    {
      value: 'xml-events',
      label: 'Windows Event Log XML',
      description: 'Split by <Event>...</Event> tags (multiple Windows Event Logs)'
    },
    {
      value: 'json-array',
      label: 'JSON Array',
      description: 'Parse as JSON array of log entries'
    },
    {
      value: 'blank-line',
      label: 'Blank Line Separated',
      description: 'Split by blank lines (common for syslog, application logs)'
    },
    {
      value: 'newline',
      label: 'One Per Line',
      description: 'Each line is a separate log entry (e.g., Apache, Nginx)'
    }
  ];

  return (
    <ModalDialog
      title="Import Log Entries"
      visible={visible}
      onClose={onClose}
      onConfirm={handleImport}
      confirmLabel="Import"
    >
      <FormField
        label="Parse Mode"
        description="How should the input be split into log entries?"
      >
        <RadioGroup
          value={parseMode}
          onChange={({ detail }) => setParseMode(detail.value)}
          items={parseModeOptions}
        />
      </FormField>

      <FormField
        label="Paste your log entries below"
        description={
          parseMode === 'single'
            ? 'Entire input will be treated as one log entry'
            : parseMode === 'xml-events'
            ? 'Multiple <Event>...</Event> blocks will be split automatically'
            : parseMode === 'json-array'
            ? 'Paste a JSON array like: [{"field": "value"}, ...]'
            : parseMode === 'blank-line'
            ? 'Log entries separated by blank lines'
            : 'One log entry per line'
        }
      >
        <Textarea
          value={importText}
          onChange={({ detail }) => setImportText(detail.value)}
          placeholder="Paste your log entries here..."
          rows={20}
        />
      </FormField>
    </ModalDialog>
  );
};

export default ImportDialog;
