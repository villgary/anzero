'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useLocale } from 'next-intl';
import styles from './Sidebar.module.css';

export function Sidebar() {
  const pathname = usePathname();
  const locale = useLocale();

  const navItems = [
    { href: `/${locale}`, label: 'Dashboard' },
    { href: `/${locale}/policies`, label: 'Policies' },
    { href: `/${locale}/agents`, label: 'Agents' },
    { href: `/${locale}/alerts`, label: 'Alerts' },
    { href: `/${locale}/approvals`, label: 'Approvals' },
    { href: `/${locale}/settings`, label: 'Settings' },
  ];

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