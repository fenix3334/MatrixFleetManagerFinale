<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navbar -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-4">
            <router-link
              to="/"
              class="text-gray-600 hover:text-gray-800"
            >
              ← Dashboard
            </router-link>
            <h1 class="text-xl font-bold text-gray-800">Gestione Veicoli</h1>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-600">{{ authStore.user?.username }}</span>
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
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <div>
          <h2 class="text-2xl font-bold text-gray-800">Veicoli</h2>
          <p class="text-gray-600">{{ veicoli.length }} veicoli totali</p>
        </div>
        <button
          @click="showModal = true"
          class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg font-medium"
        >
          + Nuovo Veicolo
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-600">Caricamento...</p>
      </div>

      <!-- Errore -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
        {{ error }}
      </div>

      <!-- Lista Veicoli -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="veicolo in veicoli"
          :key="veicolo.id"
          class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition"
        >
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="text-lg font-bold text-gray-800">{{ veicolo.targa }}</h3>
              <p class="text-sm text-gray-600">{{ veicolo.marca }} {{ veicolo.modello }}</p>
            </div>
            <span
              :class="{
                'bg-green-100 text-green-800': veicolo.stato === 'Attivo',
                'bg-orange-100 text-orange-800': veicolo.stato === 'In Manutenzione',
                'bg-gray-100 text-gray-800': veicolo.stato === 'Dismesso'
              }"
              class="px-2 py-1 rounded text-xs font-medium"
            >
              {{ veicolo.stato }}
            </span>
          </div>

          <div class="space-y-2 text-sm mb-4">
            <div class="flex justify-between">
              <span class="text-gray-600">Anno:</span>
              <span class="font-medium">{{ veicolo.anno_immatricolazione }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Km:</span>
              <span class="font-medium">{{ formatNumber(veicolo.km_attuali) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Carburante:</span>
              <span class="font-medium">{{ veicolo.carburante }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Nucleo:</span>
              <span class="font-medium">{{ veicolo.nucleo }}</span>
            </div>
          </div>

          <div class="flex space-x-2">
            <button
              class="flex-1 bg-blue-50 hover:bg-blue-100 text-blue-600 px-3 py-2 rounded text-sm font-medium transition"
            >
              Dettagli
            </button>
            <button
              v-if="authStore.isAdmin"
              @click="deleteVeicolo(veicolo.id)"
              class="bg-red-50 hover:bg-red-100 text-red-600 px-3 py-2 rounded text-sm font-medium transition"
            >
              Elimina
            </button>
          </div>
        </div>
      </div>

      <!-- Nessun veicolo -->
      <div v-if="!loading && veicoli.length === 0" class="text-center py-12">
        <p class="text-gray-600 mb-4">Nessun veicolo trovato</p>
        <button
          @click="showModal = true"
          class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg font-medium"
        >
          + Aggiungi il primo veicolo
        </button>
      </div>
    </div>

    <!-- Modal Nuovo Veicolo (placeholder) -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-xl font-bold mb-4">Nuovo Veicolo</h3>
        <p class="text-gray-600 mb-4">Funzionalità in sviluppo...</p>
        <button
          @click="showModal = false"
          class="w-full bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg"
        >
          Chiudi
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useVeicoliStore } from '../stores/veicoli'

const router = useRouter()
const authStore = useAuthStore()
const veicoliStore = useVeicoliStore()

const showModal = ref(false)

const veicoli = computed(() => veicoliStore.veicoli)
const loading = computed(() => veicoliStore.loading)
const error = computed(() => veicoliStore.error)

const formatNumber = (value) => {
  return new Intl.NumberFormat('it-IT').format(value)
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const deleteVeicolo = async (id) => {
  if (confirm('Sei sicuro di voler eliminare questo veicolo?')) {
    await veicoliStore.deleteVeicolo(id)
  }
}

onMounted(async () => {
  await veicoliStore.fetchVeicoli()
})
</script>
