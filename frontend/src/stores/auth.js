/**
 * Store Pinia - Autenticazione
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const accessToken = ref(null)
  const refreshToken = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value)
  const isAdmin = computed(() => user.value?.ruolo === 'admin')

  // Actions
  const login = async (username, password) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post('/auth/login', {
        username,
        password
      })

      const data = response.data

      if (data.success) {
        // Salva token e user
        accessToken.value = data.access_token
        refreshToken.value = data.refresh_token
        user.value = data.user

        // Salva in localStorage
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        localStorage.setItem('user', JSON.stringify(data.user))

        return { success: true }
      } else {
        error.value = data.message
        return { success: false, message: data.message }
      }
    } catch (err) {
      const message = err.response?.data?.message || 'Errore durante il login'
      error.value = message
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  const register = async (username, password, nucleo = 'Via Capitel') => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post('/auth/register', {
        username,
        password,
        nucleo
      })

      const data = response.data

      if (data.success) {
        // Salva token e user
        accessToken.value = data.access_token
        refreshToken.value = data.refresh_token
        user.value = data.user

        // Salva in localStorage
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        localStorage.setItem('user', JSON.stringify(data.user))

        return { success: true }
      } else {
        error.value = data.message
        return { success: false, message: data.message }
      }
    } catch (err) {
      const message = err.response?.data?.message || 'Errore durante la registrazione'
      error.value = message
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    // Pulisci state
    user.value = null
    accessToken.value = null
    refreshToken.value = null

    // Pulisci localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  const loadFromStorage = () => {
    const storedToken = localStorage.getItem('access_token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      accessToken.value = storedToken
      refreshToken.value = storedRefreshToken
      user.value = JSON.parse(storedUser)
    }
  }

  const fetchCurrentUser = async () => {
    try {
      const response = await api.get('/auth/me')
      if (response.data.success) {
        user.value = response.data.user
        localStorage.setItem('user', JSON.stringify(response.data.user))
      }
    } catch (err) {
      console.error('Errore nel recupero utente:', err)
      logout()
    }
  }

  return {
    // State
    user,
    accessToken,
    loading,
    error,
    // Getters
    isAuthenticated,
    isAdmin,
    // Actions
    login,
    register,
    logout,
    loadFromStorage,
    fetchCurrentUser
  }
})
