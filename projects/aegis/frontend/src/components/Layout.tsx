import { useState } from 'react'
import { Layout, Menu } from 'antd'
import {
  DashboardOutlined,
  AlertOutlined,
  SearchOutlined,
  SettingOutlined,
  DatabaseOutlined,
  ShopOutlined
} from '@ant-design/icons'
import type { MenuProps } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'

const { Sider, Content } = Layout

interface LayoutProps {
  children: React.ReactNode
}

export function AppLayout({ children }: LayoutProps) {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems: MenuProps['items'] = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard'
    },
    {
      key: '/alerts',
      icon: <AlertOutlined />,
      label: 'Alert Center'
    },
    {
      key: '/investigation',
      icon: <SearchOutlined />,
      label: 'Investigation'
    },
    {
      key: '/config',
      icon: <SettingOutlined />,
      label: 'Configuration'
    },
    {
      key: '/intel',
      icon: <DatabaseOutlined />,
      label: 'Intelligence'
    },
    {
      key: '/museum',
      icon: <ShopOutlined />,
      label: 'Museum'
    }
  ]

  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    navigate(key)
  }

  return (
    <Layout className="min-h-screen">
      <Sider
        theme="dark"
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        className="bg-gray-900"
        width={220}
      >
        <div className="h-16 flex items-center justify-center border-b border-gray-800">
          {!collapsed && (
            <span className="text-xl font-bold text-white">AegisAI</span>
          )}
          {collapsed && (
            <span className="text-xl font-bold text-red-500">A</span>
          )}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          onClick={handleMenuClick}
          items={menuItems}
          className="bg-gray-900 border-r-0"
        />
      </Sider>
      <Layout>
        <Content className="bg-gray-900">
          {children}
        </Content>
      </Layout>
    </Layout>
  )
}
