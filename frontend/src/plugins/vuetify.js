// src/plugins/vuetify.js
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'
import { themeColors } from '@/theme' // Import our central theme colors

// Define your light theme using the centralized colors
const lightTheme = {
  dark: false,
  colors: {
    ...themeColors
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