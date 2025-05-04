// tailwind.config.js
import { generateColorPalette } from './src/theme'

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Import color palette from our centralized theme
        ...generateColorPalette()
      }
    },
  },
  plugins: [],
  safelist: [
    // Add common color classes to safelist to prevent purging
    'text-primary',
    'bg-primary',
    'border-primary',
    'text-secondary',
    'bg-secondary',
    'border-secondary',
    'text-success',
    'bg-success',
    'border-success',
    'text-error',
    'bg-error',
    'border-error',
    'text-warning',
    'bg-warning',
    'border-warning',
    'text-info',
    'bg-info',
    'border-info'
  ]
}