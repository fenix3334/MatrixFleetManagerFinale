/**
 * Vue Router Configuration
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/veicoli',
    name: 'Veicoli',
    component: () => import('../views/Veicoli.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // Carica auth da storage se non già caricato
  if (!authStore.isAuthenticated) {
    authStore.loadFromStorage()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Redirect a login se non autenticato
    next({ name: 'Login' })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    // Redirect a dashboard se già autenticato
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
