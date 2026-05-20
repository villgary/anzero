import { Card, Typography } from 'antd'

const { Title } = Typography

function DashboardPage() {
  return (
    <div>
      <Title level={2}>Dashboard</Title>
      <Card title="Welcome to AppScan Pro">
        <p>Mobile App Security Scanner Platform</p>
      </Card>
    </div>
  )
}

export default DashboardPage