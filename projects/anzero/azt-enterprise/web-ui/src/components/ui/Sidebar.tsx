'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Sidebar.module.css';

const navItems = [
  { href: '/', label: 'Dashboard' },
  { href: '/policies', label: 'Policies' },
  { href: '/agents', label: 'Agents' },
  { href: '/alerts', label: 'Alerts' },
  { href: '/approvals', label: 'Approvals' },
  { href: '/settings', label: 'Settings' },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>AZT Shield</div>
      <nav className={styles.nav}>
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`${styles.navLink} ${pathname === item.href ? styles.navLinkActive : ''}`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}