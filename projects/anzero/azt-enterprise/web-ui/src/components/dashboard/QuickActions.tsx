'use client';

import Link from 'next/link';
import styles from './QuickActions.module.css';

export function QuickActions() {
  return (
    <div className={styles.actions}>
      <h3>Quick Actions</h3>
      <Link href="/alerts" className={styles.btnPrimary}>View All Alerts</Link>
      <Link href="/approvals" className={styles.btnSuccess}>Pending Approvals</Link>
      <Link href="/policies" className={styles.btnSecondary}>Manage Policies</Link>
    </div>
  );
}