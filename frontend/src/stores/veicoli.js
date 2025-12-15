/**
 * Store Pinia - Veicoli
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useVeicoliStore = defineStore('veicoli', () => {
  // State
  const veicoli = ref([])
  const currentVeicolo = ref(null)
  const stats = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Actions
  const fetchVeicoli = async (filters = {}) => {
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams(filters).toString()
      const response = await api.get(`/veicoli${params ? '?' + params : ''}`)

      if (response.data.success) {
        veicoli.value = response.data.data
        return { success: true, data: response.data.data }
      }
    } catch (err) {
      const message = err.response?.data?.message || 'Errore nel caricamento veicoli'
      error.value = message
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  const fetchVeicolo = async (id) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/veicoli/${id}`)

      if (response.data.success) {
        currentVeicolo.value = response.data.data
        return { success: true, data: response.data.data }
      }
    } catch (err) {
      const message = err.response?.data?.message || 'Errore nel caricamento veicolo'
      error.value = message
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  const createVeicolo = async (data) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post('/veicoli', data)

      if (response.data.success) {
        // Ricarica lista
        await fetchVeicoli()
        return { success: true, data: response.data.data }
      }
    } catch (err) {
      const message = err.response?.data?.message || 'Errore nella creazione veicolo'
      error.value = message
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  const updateVeicolo = async (id, data) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.put(`/veicoli/${id}`, data)

      if (response.data.success) {
        // Aggiorna lista
        await fetchVeicoli()
        return { success: true, data: response.data.data }
      }
    } catch (err) {
      const message = err.response?.data?.message || 'Errore nell\'aggiornamento veicolo'
      error.value = message
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  const deleteVeicolo = async (id) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.delete(`/veicoli/${id}`)

      if (response.data.success) {
        // Ricarica lista
        await fetchVeicoli()
        return { success: true }
      }
    } catch (err) {
      const message = err.response?.data?.message || 'Errore nell\'eliminazione veicolo'
      error.value = message
      return { success: false, message }
    } finally {
      loading.value = false
    }
  }

  const fetchStats = async () => {
    try {
      const response = await api.get('/veicoli/stats')

      if (response.data.success) {
        stats.value = response.data.data
        return { success: true, data: response.data.data }
      }
    } catch (err) {
      console.error('Errore nel caricamento statistiche:', err)
    }
  }

  return {
    // State
    veicoli,
    currentVeicolo,
    stats,
    loading,
    error,
    // Actions
    fetchVeicoli,
    fetchVeicolo,
    createVeicolo,
    updateVeicolo,
    deleteVeicolo,
    fetchStats
  }
})
