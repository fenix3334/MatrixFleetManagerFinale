<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navbar -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-800">Matrix Fleet Manager</h1>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-600">
              {{ authStore.user?.username }} ({{ authStore.user?.nucleo }})
            </span>
            <button
              @click="handleLogout"
              class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Benvenuto -->
      <div class="mb-8">
        <h2 class="text-3xl font-bold text-gray-800 mb-2">Dashboard</h2>
        <p class="text-gray-600">Benvenuto nel gestionale parco auto</p>
      </div>

      <!-- Statistiche -->
      <div v-if="stats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 mb-1">Totale Veicoli</p>
              <p class="text-3xl font-bold text-gray-800">{{ stats.totale_veicoli }}</p>
            </div>
            <div class="bg-primary-100 p-3 rounded-full">
              <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 mb-1">Veicoli Attivi</p>
              <p class="text-3xl font-bold text-green-600">{{ stats.veicoli_attivi }}</p>
            </div>
            <div class="bg-green-100 p-3 rounded-full">
              <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 mb-1">In Manutenzione</p>
              <p class="text-3xl font-bold text-orange-600">{{ stats.veicoli_manutenzione }}</p>
            </div>
            <div class="bg-orange-100 p-3 rounded-full">
              <svg class="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600 mb-1">Km Totali</p>
              <p class="text-3xl font-bold text-gray-800">{{ formatNumber(stats.km_totali) }}</p>
            </div>
            <div class="bg-blue-100 p-3 rounded-full">
              <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Azioni Rapide -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Azioni Rapide</h3>
          <div class="space-y-3">
            <router-link
              to="/veicoli"
              class="block w-full bg-primary-600 hover:bg-primary-700 text-white px-4 py-3 rounded-lg text-center font-medium transition"
            >
              Gestione Veicoli
            </router-link>
            <button
              class="block w-full bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-3 rounded-lg font-medium transition"
            >
              Manutenzioni (Coming Soon)
            </button>
            <button
              class="block w-full bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-3 rounded-lg font-medium transition"
            >
              Scadenze (Coming Soon)
            </button>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Informazioni Sistema</h3>
          <div class="space-y-2 text-sm">
            <p><span class="font-medium">Versione:</span> 1.0.0</p>
            <p><span class="font-medium">Utente:</span> {{ authStore.user?.username }}</p>
            <p><span class="font-medium">Ruolo:</span> {{ authStore.user?.ruolo }}</p>
            <p><span class="font-medium">Nucleo:</span> {{ authStore.user?.nucleo }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useVeicoliStore } from '../stores/veicoli'

const router = useRouter()
const authStore = useAuthStore()
const veicoliStore = useVeicoliStore()

const stats = ref(null)

const formatNumber = (value) => {
  return new Intl.NumberFormat('it-IT').format(value)
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

onMounted(async () => {
  // Carica statistiche
  const result = await veicoliStore.fetchStats()
  if (result.success) {
    stats.value = result.data
  }
})
</script>
