import { Layout, Menu, Button } from 'antd'
import { Outlet } from 'react-router-dom'
import { useAuthStore } from '../store/auth'

const { Header, Content } = Layout

function MainLayout() {
  const { logout } = useAuthStore()

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ color: 'white', fontSize: 18, fontWeight: 'bold' }}>AppScan Pro</div>
        <Button type="primary" danger onClick={logout}>
          Logout
        </Button>
      </Header>
      <Content style={{ padding: 24 }}>
        <Outlet />
      </Content>
    </Layout>
  )
}

export default MainLayout