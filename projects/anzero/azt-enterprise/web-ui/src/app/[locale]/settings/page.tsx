import styles from './page.module.css';

export default function SettingsPage() {
  return (
    <div className={styles.page}>
      <h1>Settings</h1>
      <div className={styles.section}>
        <h2>General</h2>
        <div className={styles.field}>
          <label>Cluster Name</label>
          <input type="text" defaultValue="azt-production" />
        </div>
        <div className={styles.field}>
          <label>Timezone</label>
          <select defaultValue="UTC">
            <option value="UTC">UTC</option>
            <option value="America/New_York">America/New_York</option>
            <option value="Europe/London">Europe/London</option>
            <option value="Asia/Shanghai">Asia/Shanghai</option>
          </select>
        </div>
      </div>

      <div className={styles.section}>
        <h2>Notifications</h2>
        <div className={styles.checkbox}>
          <input type="checkbox" id="email" defaultChecked />
          <label htmlFor="email">Email notifications for critical alerts</label>
        </div>
        <div className={styles.checkbox}>
          <input type="checkbox" id="slack" />
          <label htmlFor="slack">Slack webhook notifications</label>
        </div>
      </div>

      <div className={styles.actions}>
        <button className={styles.saveBtn}>Save Settings</button>
      </div>
    </div>
  );
}
