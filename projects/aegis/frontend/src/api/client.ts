const API_BASE = '/api/v1'

export const api = {
  get: async (path: string) => {
    const res = await fetch(`${API_BASE}${path}`)
    return { data: await res.json() }
  }
}