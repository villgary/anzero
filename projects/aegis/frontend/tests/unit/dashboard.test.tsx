import { render, screen, waitFor } from '@testing-library/react'
import { DashboardPage } from '../../src/pages/DashboardPage'

vi.mock('../../src/api/client', () => ({
  api: {
    get: vi.fn().mockResolvedValue({
      data: {
        attackCount: 128,
        mttd: '5m',
        counterRate: 85,
        threatLevel: '高'
      }
    })
  }
}))

test('renders metric cards', async () => {
  render(<DashboardPage />)
  await waitFor(() => {
    expect(screen.getByText('本月攻击')).toBeInTheDocument()
  })
  expect(screen.getByText('MTTD')).toBeInTheDocument()
})