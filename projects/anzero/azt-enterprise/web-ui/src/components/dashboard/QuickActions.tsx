'use client';

import Link from 'next/link';
import { useLocale } from 'next-intl';
import styles from './QuickActions.module.css';

export function QuickActions() {
  const locale = useLocale();

  return (
    <div className={styles.actions}>
      <h3>Quick Actions</h3>
      <Link href={`/${locale}/alerts`} className={styles.btnPrimary}>View All Alerts</Link>
      <Link href={`/${locale}/approvals`} className={styles.btnSuccess}>Pending Approvals</Link>
      <Link href={`/${locale}/policies`} className={styles.btnSecondary}>Manage Policies</Link>
    </div>
  );
}