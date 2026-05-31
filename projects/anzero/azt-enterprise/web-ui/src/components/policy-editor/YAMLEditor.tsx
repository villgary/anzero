'use client';

import Editor from '@monaco-editor/react';
import styles from './YAMLEditor.module.css';

interface YAMLEditorProps {
  value: string;
  onChange: (value: string) => void;
}

export function YAMLEditor({ value, onChange }: YAMLEditorProps) {
  return (
    <div className={styles.editor}>
      <Editor
        height="400px"
        defaultLanguage="yaml"
        value={value}
        onChange={(v) => onChange(v || '')}
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
        }}
      />
    </div>
  );
}