// src/plugins/vuetify.js
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

// Define your light and dark themes
const lightTheme = {
  dark: false,
  colors: {
    primary: '#1E3A8A', // Deep blue from your favicon
    secondary: '#0EA5E9', // Sky blue
    accent: '#A78BFA', // Purple
    success: '#4ADE80', // Green from uptrend
    error: '#EF4444', // Red from downtrend
    info: '#60A5FA', // Light blue
    warning: '#FBBF24', // Amber
  }
}

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'lightTheme',
    themes: {
      lightTheme,
    }
  },
  icons: {
    defaultSet: 'mdi', // This is already the default value - only for display purposes
  },
})