import { PolicyEditor } from '@/components/policy-editor/PolicyEditor';
import styles from './page.module.css';

export default function PoliciesPage() {
  return (
    <div className={styles.page}>
      <h1>Policy Editor</h1>
      <PolicyEditor />
    </div>
  );
}