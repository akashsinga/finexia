// src/stores/auth.store.js
import { defineStore } from 'pinia'
import { api } from '@/plugins'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    userInitials: (state) => {
      if (!state.user || !state.user.username) return 'U'
      return state.user.username.charAt(0).toUpperCase()
    },
    username: (state) => state.user?.username || '',
    userRole: (state) => state.user?.role || 'user',
    isAdmin: (state) => state.user?.role === 'admin'
  },

  actions: {
    login: async function (username, password) {
      this.loading = true
      this.error = null

      try {
        const response = await api.post('/auth/token', { username, password }, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })

        this.token = response.data.access_token
        this.user = response.data.user

        // Save in localStorage
        localStorage.setItem('token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))

        return response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Authentication failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    logout: function () {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.token = null
      this.user = null
    },

    verifyToken: async function () {
      try {
        const response = await api.get('/auth/verify');
        // Update user data if needed
        if (response.data.user) {
          this.user = response.data.user;
          localStorage.setItem('user', JSON.stringify(this.user));
        }
        return true;
      } catch (error) {
        this.logout();
        return false;
      }
    }
  }
})