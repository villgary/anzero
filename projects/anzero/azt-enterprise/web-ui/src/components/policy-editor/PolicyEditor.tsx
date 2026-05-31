'use client';

import { useState } from 'react';
import { YAMLEditor } from './YAMLEditor';
import styles from './PolicyEditor.module.css';

const defaultPolicy = `agent: email-agent-prod
version: 1
rules:
  - name: allow-read-tools
    effect: allow
    tools:
      - search
      - lookup
      - read
  - name: deny-external-write
    effect: deny
    tools:
      - send_email
      - post_message
    conditions:
      - trust_score_below: 70
`;

export function PolicyEditor() {
  const [yaml, setYaml] = useState(defaultPolicy);
  const [mode, setMode] = useState<'yaml' | 'visual'>('yaml');
  const [validationResult, setValidationResult] = useState<string>('');

  const handleValidate = () => {
    try {
      // Simple YAML validation - check basic structure
      if (yaml.includes('agent:') && yaml.includes('rules:')) {
        setValidationResult('✓ Policy is valid');
      } else {
        setValidationResult('✗ Policy missing required fields (agent, rules)');
      }
    } catch {
      setValidationResult('✗ YAML syntax error');
    }
  };

  return (
    <div className={styles.editor}>
      <div className={styles.toolbar}>
        <div className={styles.tabs}>
          <button
            onClick={() => setMode('yaml')}
            className={mode === 'yaml' ? styles.activeTab : ''}
          >
            YAML
          </button>
          <button
            onClick={() => setMode('visual')}
            className={mode === 'visual' ? styles.activeTab : ''}
          >
            Visual
          </button>
        </div>
        <button onClick={handleValidate} className={styles.validateBtn}>
          Validate
        </button>
      </div>
      {mode === 'yaml' && (
        <YAMLEditor value={yaml} onChange={setYaml} />
      )}
      {mode === 'visual' && (
        <div className={styles.visualPlaceholder}>
          <p>Visual editor coming soon</p>
          <p className={styles.hint}>Use YAML mode to edit policies directly</p>
        </div>
      )}
      {validationResult && (
        <div className={styles.validation}>{validationResult}</div>
      )}
    </div>
  );
}