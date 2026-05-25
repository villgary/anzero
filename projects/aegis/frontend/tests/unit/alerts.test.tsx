import { render, screen } from '@testing-library/react'
import { AlertList } from '../../src/components/alerts/AlertList'

const mockAlerts = [
  { id: '1', priority: 'P0', confidence: 0.87, tool: 'PentestGPT', time: '14:32:15' }
]

test('renders alert list', () => {
  render(<AlertList alerts={mockAlerts} />)
  expect(screen.getByText(/PentestGPT/)).toBeInTheDocument()
})