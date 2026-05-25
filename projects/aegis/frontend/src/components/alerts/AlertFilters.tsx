import { useState } from 'react'
import { Select, DatePicker, Input } from 'antd'
import type { Dayjs } from 'dayjs'

const { RangePicker } = DatePicker

interface AlertFiltersProps {
  onFilterChange: (filters: AlertFilters) => void
}

export interface AlertFilters {
  priorities: string[]
  tools: string[]
  timeRange: [Dayjs, Dayjs] | null
  searchText: string
}

export function AlertFilters({ onFilterChange }: AlertFiltersProps) {
  const [filters, setFilters] = useState<AlertFilters>({
    priorities: [],
    tools: [],
    timeRange: null,
    searchText: ''
  })

  const handleChange = (key: keyof AlertFilters, value: any) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    onFilterChange(newFilters)
  }

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 mb-4">
      <div className="flex flex-wrap gap-4 items-center">
        {/* Search */}
        <div className="flex-1 min-w-[200px]">
          <Input.Search
            placeholder="Search alerts..."
            className="w-full"
            onSearch={(value) => handleChange('searchText', value)}
          />
        </div>

        {/* Priority Filter */}
        <div className="w-40">
          <Select
            mode="multiple"
            placeholder="Priority"
            className="w-full"
            options={[
              { label: 'P0 - Emergency', value: 'P0' },
              { label: 'P1 - High', value: 'P1' },
              { label: 'P2 - Medium', value: 'P2' },
              { label: 'P3 - Low', value: 'P3' },
            ]}
            onChange={(value) => handleChange('priorities', value)}
            allowClear
          />
        </div>

        {/* Tool Filter */}
        <div className="w-40">
          <Select
            mode="multiple"
            placeholder="Attack Tool"
            className="w-full"
            options={[
              { label: 'PentestGPT', value: 'PentestGPT' },
              { label: 'ReconAI', value: 'ReconAI' },
              { label: 'AttackGPT', value: 'AttackGPT' },
              { label: 'Other', value: 'Other' },
            ]}
            onChange={(value) => handleChange('tools', value)}
            allowClear
          />
        </div>

        {/* Time Range */}
        <div className="w-64">
          <RangePicker
            className="w-full"
            onChange={(dates) => handleChange('timeRange', dates)}
          />
        </div>
      </div>
    </div>
  )
}
