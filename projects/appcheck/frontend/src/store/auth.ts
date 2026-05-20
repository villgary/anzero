import { create } from 'zustand'

interface AuthState {
  isAuthenticated: boolean
  user: null | { id: string; username: string }
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  login: async (username: string, password: string) => {
    // TODO: Implement actual API call
    set({ isAuthenticated: true, user: { id: '1', username } })
  },
  logout: () => {
    set({ isAuthenticated: false, user: null })
  },
}))