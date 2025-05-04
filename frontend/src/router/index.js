import { createRouter, createWebHistory } from 'vue-router'
import { h } from 'vue'
import DefaultLayout from '../layouts/DefaultLayout.vue'

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
    path: '/dashboard',
    name: 'Dashboard',
    component: DefaultLayoutWrapper(Dashboard),
    meta: { title: 'Dashboard | Finexia' }
  },
  {
    path: '/symbols',
    name: 'SymbolsExplorer',
    component: DefaultLayoutWrapper(SymbolsExplorer),
    meta: { title: 'Symbols | Finexia' }
  },
  {
    path: '/symbols/:symbol',
    name: 'SymbolDetail',
    component: DefaultLayoutWrapper(SymbolDetail),
    props: true,
    meta: { title: 'Symbol Details | Finexia' }
  },
  {
    path: '/predictions',
    name: 'Predictions',
    component: DefaultLayoutWrapper(Predictions),
    meta: { title: 'Predictions | Finexia' }
  },
  {
    path: '/models',
    name: 'ModelPerformance',
    component: DefaultLayoutWrapper(ModelPerformance),
    meta: { title: 'Models | Finexia' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: DefaultLayoutWrapper(Settings),
    meta: { title: 'Settings | Finexia' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Update page title based on route meta
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'Finexia | Predictive Stock Analytics'
  next()
})

export default router