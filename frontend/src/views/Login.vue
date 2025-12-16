<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center px-4">
    <div class="max-w-md w-full bg-white rounded-lg shadow-xl p-8">
      <!-- Logo e Titolo -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">Matrix Fleet Manager</h1>
        <p class="text-gray-600">Gestione Parco Auto Aziendale</p>
      </div>

      <!-- Form Login -->
      <form @submit.prevent="handleLogin" class="space-y-6">
        <!-- Username -->
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
            Username
          </label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="Inserisci username"
          />
        </div>

        <!-- Password -->
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
            Password
          </label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="Inserisci password"
          />
        </div>

        <!-- Errore -->
        <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {{ error }}
        </div>

        <!-- Bottone Login -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-4 rounded-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="!loading">Accedi</span>
          <span v-else>Accesso in corso...</span>
        </button>
      </form>

      <!-- Link Registrazione -->
      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          Non hai un account?
          <button @click="showRegister = !showRegister" class="text-primary-600 hover:text-primary-700 font-medium">
            Registrati
          </button>
        </p>
      </div>

      <!-- Form Registrazione -->
      <div v-if="showRegister" class="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 class="text-lg font-semibold mb-4">Registrazione</h3>
        <form @submit.prevent="handleRegister" class="space-y-4">
          <input
            v-model="registerData.username"
            type="text"
            required
            placeholder="Username"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
          <input
            v-model="registerData.password"
            type="password"
            required
            placeholder="Password (min 6 caratteri)"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
          <select
            v-model="registerData.nucleo"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="Via Capitel">Via Capitel</option>
            <option value="Altro Nucleo">Altro Nucleo</option>
          </select>
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg"
          >
            Registrati
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const showRegister = ref(false)

const registerData = ref({
  username: '',
  password: '',
  nucleo: 'Via Capitel'
})

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  const result = await authStore.login(username.value, password.value)

  loading.value = false

  if (result.success) {
    router.push('/')
  } else {
    error.value = result.message || 'Errore durante il login'
  }
}

const handleRegister = async () => {
  error.value = ''
  loading.value = true

  const result = await authStore.register(
    registerData.value.username,
    registerData.value.password,
    registerData.value.nucleo
  )

  loading.value = false

  if (result.success) {
    router.push('/')
  } else {
    error.value = result.message || 'Errore durante la registrazione'
  }
}
</script>
