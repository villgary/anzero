import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import axios from 'axios'

interface AuthState {
  token: string | null
  user: { id: string; username: string; email: string } | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const api = axios.create({
  baseURL: '/api/v1',
})

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      login: async (username: string, password: string) => {
        const formData = new FormData()
        formData.append('username', username)
        formData.append('password', password)
        const response = await api.post('/auth/login', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })
        const { access_token } = response.data
        localStorage.setItem('token', access_token)
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        const userResponse = await api.get('/auth/me')
        set({
          token: access_token,
          user: userResponse.data,
          isAuthenticated: true,
        })
      },
      logout: () => {
        localStorage.removeItem('token')
        delete api.defaults.headers.common['Authorization']
        set({ token: null, user: null, isAuthenticated: false })
      },
    }),
    {
      name: 'auth-storage',
      onRehydrateStorage: () => (state) => {
        const token = localStorage.getItem('token')
        if (token && state) {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`
          state.token = token
          state.isAuthenticated = true
        }
      },
    }
  )
)