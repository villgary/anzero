import { useState } from 'react'
import { Layout, Menu, theme, Dropdown, Button, Avatar } from 'antd'
import {
  DashboardOutlined,
  ScanOutlined,
  FileTextOutlined,
  BarChartOutlined,
  SettingOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  GlobalOutlined,
} from '@ant-design/icons'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../store/auth'

const { Header, Sider, Content } = Layout

export default function MainLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { t, i18n } = useTranslation()
  const { user, logout } = useAuthStore()
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken()

  const changeLanguage = () => {
    i18n.changeLanguage(i18n.language === 'en' ? 'zh' : 'en')
  }

  const menuItems = [
    { key: '/dashboard', icon: <DashboardOutlined />, label: t('common.dashboard') },
    { key: '/scans', icon: <ScanOutlined />, label: t('common.scans') },
    { key: '/reports', icon: <FileTextOutlined />, label: t('common.reports') },
    { key: '/statistics', icon: <BarChartOutlined />, label: t('common.statistics') },
    { key: '/settings', icon: <SettingOutlined />, label: t('common.settings') },
  ]

  const userMenu = {
    items: [
      { key: 'logout', icon: <LogoutOutlined />, label: t('common.logout'), danger: true },
    ],
    onClick: ({ key }: { key: string }) => {
      if (key === 'logout') {
        logout()
        navigate('/login')
      }
    },
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: collapsed ? 16 : 18,
          fontWeight: 'bold'
        }}>
          {collapsed ? 'AP' : 'AppScan Pro'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 16px', background: colorBgContainer, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <Button
              type="text"
              icon={<GlobalOutlined />}
              onClick={changeLanguage}
            >
              {i18n.language === 'en' ? '中文' : 'EN'}
            </Button>
            <Dropdown menu={userMenu} placement="bottomRight">
              <Avatar style={{ cursor: 'pointer' }}>{user?.username?.[0]?.toUpperCase()}</Avatar>
            </Dropdown>
          </div>
        </Header>
        <Content style={{ margin: 24, padding: 24, background: colorBgContainer, borderRadius: borderRadiusLG }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
