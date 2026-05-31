import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { Sidebar } from '@/components/ui/Sidebar';
import styles from './layout.module.css';

export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'zh' }, { locale: 'ja' }, { locale: 'fr' }, { locale: 'ar' }];
}

export default async function LocaleLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  let messages;
  try {
    messages = await getMessages();
  } catch {
    notFound();
  }

  return (
    <html dir={locale === 'ar' ? 'rtl' : 'ltr'}>
      <body>
        <NextIntlClientProvider locale={locale} messages={messages}>
          <div className={styles.layout}>
            <Sidebar />
            <main className={styles.main}>{children}</main>
          </div>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}