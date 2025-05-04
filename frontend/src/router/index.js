import { createRouter, createWebHistory } from 'vue-router'
import { h } from 'vue'
import { useAuthStore } from '@/store/auth.store'

import DefaultLayout from '../layouts/DefaultLayout.vue'
import Login from '../layouts/LoginLayout.vue'

// Import your view components
import Dashboard from '../views/Dashboard.vue'
import SymbolsExplorer from '../views/SymbolsExplorer.vue'
import SymbolDetail from '../views/SymbolDetail.vue'
import Predictions from '../views/Predictions.vue'
import ModelPerformance from '../views/ModelPerformance.vue'
import Settings from '../views/Settings.vue'

// Layout wrapper component
const DefaultLayoutWrapper = (Component) => {
  return {
    render() {
      return h(DefaultLayout, null, {
        default: () => h(Component)
      })
    }
  }
}

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true, title: 'Login | Finexia' }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DefaultLayoutWrapper(Dashboard),
    meta: { requiresAuth: true, title: 'Dashboard | Finexia' }
  },
  {
    path: '/symbols',
    name: 'SymbolsExplorer',
    component: DefaultLayoutWrapper(SymbolsExplorer),
    meta: { requiresAuth: true, title: 'Symbols | Finexia' }
  },
  {
    path: '/symbols/:symbol',
    name: 'SymbolDetail',
    component: DefaultLayoutWrapper(SymbolDetail),
    props: true,
    meta: { requiresAuth: true, title: 'Symbol Details | Finexia' }
  },
  {
    path: '/predictions',
    name: 'Predictions',
    component: DefaultLayoutWrapper(Predictions),
    meta: { requiresAuth: true, title: 'Predictions | Finexia' }
  },
  {
    path: '/models',
    name: 'ModelPerformance',
    component: DefaultLayoutWrapper(ModelPerformance),
    meta: { requiresAuth: true, title: 'Models | Finexia' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: DefaultLayoutWrapper(Settings),
    meta: { requiresAuth: true, title: 'Settings | Finexia' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Update page title based on route meta
router.beforeEach(async (to, from, next) => {
  // Set page title
  document.title = to.meta.title || 'Finexia | Stock Market Intelligence'

  // Check if route requires authentication
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isPublic = to.matched.some(record => record.meta.public)

  if (!requiresAuth && isPublic) {
    // Public route, proceed
    return next()
  }

  // Get auth store (initialized by Pinia)
  const authStore = useAuthStore()

  // Check if user is logged in
  const isLoggedIn = authStore.isLoggedIn

  if (requiresAuth && !isLoggedIn) {
    // Not logged in, redirect to login
    return next('/login')
  }

  // User is logged in, verify token validity
  if (isLoggedIn) {
    try {
      // Verify token with backend
      const isValid = await authStore.verifyToken()
      if (isValid) {
        next() // Token is valid, proceed
      } else {
        // Token verification failed, redirect to login
        next('/login')
      }
    } catch (error) {
      // Token is invalid, logout and redirect to login
      authStore.logout()
      next('/login')
    }
  } else {
    next() // Proceed normally
  }
})

export default router