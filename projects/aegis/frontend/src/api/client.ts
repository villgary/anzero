const API_BASE = '/api/v1'

export const api = {
  get: async (path: string) => {
    try {
      const res = await fetch(`${API_BASE}${path}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      return { data: await res.json() }
    } catch (err) {
      console.error('API error:', err)
      throw err
    }
  }
}