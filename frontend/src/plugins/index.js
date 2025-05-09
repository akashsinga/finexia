// src/plugins/index.js
import axios from 'axios'
import moment from 'moment'
import lodash from 'lodash-es'

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000
})

// Add axios interceptors
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')

      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// Export a single install function for all plugins
export default {
  install: (app) => {
    app.config.globalProperties.$lodash = lodash
    app.config.globalProperties.$axios = axios
    app.config.globalProperties.$http = api
    app.config.globalProperties.$moment = moment
    app.config.globalProperties.$filters = {
      formatDate(value, format = 'MMMM D, YYYY') {
        if (value) {
          return moment(String(value)).format(format)
        }
      },
      fromNow(value) {
        if (value) {
          return moment(String(value)).fromNow()
        }
      }
    }
  }
}

// Export individual instances in case they're needed separately
export { lodash, api, axios, moment }