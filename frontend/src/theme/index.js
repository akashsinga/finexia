// src/theme/index.js - Create this file to define your theme colors once

export const themeColors = {
  primary: '#1E3A8A', // Deep blue from your favicon
  secondary: '#0EA5E9', // Sky blue
  accent: '#A78BFA', // Purple
  success: '#4ADE80', // Green from uptrend
  error: '#EF4444', // Red from downtrend
  info: '#60A5FA', // Light blue
  warning: '#FBBF24', // Amber
}

// Function to generate color shades (lighter/darker variants)
export const generateColorShades = (color, name) => {
  return {
    [name]: {
      DEFAULT: color,
      light: color, // You could use a color library to generate lighter shades
      dark: color,  // You could use a color library to generate darker shades
    }
  }
}

// Generate full color palette with shades
export const generateColorPalette = () => {
  const palette = {}

  Object.entries(themeColors).forEach(([name, color]) => {
    Object.assign(palette, generateColorShades(color, name))
  })

  return palette
}