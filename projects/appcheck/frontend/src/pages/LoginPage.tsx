import { Button, Form, Input } from 'antd'
import { useAuthStore } from '../store/auth'

function LoginPage() {
  const { login } = useAuthStore()

  const onFinish = async (values: { username: string; password: string }) => {
    await login(values.username, values.password)
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <Form onFinish={onFinish} style={{ width: 300 }}>
        <Form.Item name="username" rules={[{ required: true }]}>
          <Input placeholder="Username" />
        </Form.Item>
        <Form.Item name="password" rules={[{ required: true }]}>
          <Input.Password placeholder="Password" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" block>
            Login
          </Button>
        </Form.Item>
      </Form>
    </div>
  )
}

export default LoginPage