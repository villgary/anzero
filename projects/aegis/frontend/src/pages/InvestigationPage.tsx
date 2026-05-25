import { useState } from 'react'
import { Tabs, Timeline, Card, Descriptions, Tag } from 'antd'

interface EventDetail {
  id: string
  timestamp: string
  sourceIp: string
  tool: string
  confidence: number
  priority: string
  attackChain: string[]
  indicators: string[]
}

const mockEvent: EventDetail = {
  id: 'INV-2026-05-25-001',
  timestamp: '2026-05-25 14:32:15',
  sourceIp: '203.0.113.42',
  tool: 'PentestGPT',
  confidence: 0.92,
  priority: 'P0',
  attackChain: ['Reconnaissance', 'Enumeration', 'Exploitation', 'Lateral Movement', 'Persistence'],
  indicators: [
    'TLS fingerprint matches known PentestGPT pattern',
    'Rapid directory enumeration detected',
    'Unusual API callback pattern',
    'Honeytoken triggered'
  ]
}

export function InvestigationPage() {
  const [selectedEvent] = useState<EventDetail>(mockEvent)

  const priorityColors: Record<string, string> = {
    P0: 'red',
    P1: 'orange',
    P2: 'yellow',
    P3: 'blue'
  }

  return (
    <div className="p-6 bg-gray-900 min-h-screen">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-2">
          Investigation Panel - Event {selectedEvent.id}
        </h1>
        <div className="flex items-center gap-4">
          <Tag color={priorityColors[selectedEvent.priority]}>
            {selectedEvent.priority}
          </Tag>
          <span className="text-gray-400">
            Confidence: {(selectedEvent.confidence * 100).toFixed(0)}%
          </span>
          <span className="text-gray-400">
            Source IP: {selectedEvent.sourceIp}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <Tabs
        className="text-white"
        items={[
          {
            key: 'timeline',
            label: 'Timeline',
            children: (
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
                <Timeline
                  items={selectedEvent.attackChain.map((stage, index) => ({
                    color: index === selectedEvent.attackChain.length - 1 ? 'red' : 'blue',
                    children: (
                      <div className="text-white">
                        <span className="font-medium">{stage}</span>
                        <div className="text-gray-400 text-sm mt-1">
                          Stage {index + 1} of {selectedEvent.attackChain.length}
                        </div>
                      </div>
                    )
                  }))}
                />
              </div>
            )
          },
          {
            key: 'comparison',
            label: 'Behavior Comparison',
            children: (
              <div className="grid grid-cols-2 gap-4">
                <Card title="Current Attacker Behavior" className="bg-gray-800 border-gray-700">
                  <ul className="space-y-2 text-white">
                    <li>• Rapid scanning pattern</li>
                    <li>• Automated tool signatures</li>
                    <li>• Honeytoken interaction</li>
                    <li>• API abuse detected</li>
                  </ul>
                </Card>
                <Card title="PentestGPT Template" className="bg-gray-800 border-gray-700">
                  <ul className="space-y-2 text-gray-400">
                    <li>• Tool-based reconnaissance</li>
                    <li>• Systematic enumeration</li>
                    <li>• Exploitation attempts</li>
                    <li>• C2 callback pattern</li>
                  </ul>
                </Card>
              </div>
            )
          },
          {
            key: 'network',
            label: 'Network Topology',
            children: (
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
                <div className="flex items-center justify-center h-64 text-gray-500">
                  Network topology visualization placeholder
                </div>
              </div>
            )
          },
          {
            key: 'logs',
            label: 'Raw Logs',
            children: (
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <pre className="text-green-400 text-sm overflow-auto max-h-96">
{`[2026-05-25 14:32:15] TLS connection established
  JA4: t13d5f8g9h2
  TLS fingerprint matches: PentestGPT

[2026-05-25 14:32:16] HTTP GET /admin/config
[2026-05-25 14:32:17] HTTP GET /api/users
[2026-05-25 14:32:18] Honeytoken triggered: decoy_api_key_xxxx
[2026-05-25 14:32:19] HTTP POST /api/login attempt

[2026-05-25 14:32:20] Alert: AI Agent attack detected (D-01 + D-21)`}
                </pre>
              </div>
            )
          },
          {
            key: 'evidence',
            label: 'Evidence',
            children: (
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
                <Descriptions bordered column={1} className="text-white">
                  <Descriptions.Item label="Source IP">{selectedEvent.sourceIp}</Descriptions.Item>
                  <Descriptions.Item label="Attack Tool">{selectedEvent.tool}</Descriptions.Item>
                  <Descriptions.Item label="Timestamp">{selectedEvent.timestamp}</Descriptions.Item>
                  <Descriptions.Item label="Confidence">
                    {(selectedEvent.confidence * 100).toFixed(0)}%
                  </Descriptions.Item>
                  <Descriptions.Item label="Indicators">
                    <ul className="space-y-1">
                      {selectedEvent.indicators.map((ind, i) => (
                        <li key={i} className="text-red-400">• {ind}</li>
                      ))}
                    </ul>
                  </Descriptions.Item>
                </Descriptions>
              </div>
            )
          }
        ]}
      />
    </div>
  )
}
