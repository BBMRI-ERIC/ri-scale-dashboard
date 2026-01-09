import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// Custom dark theme inspired by scientific/biomedical aesthetics
const riScaleTheme = {
  dark: true,
  colors: {
    background: '#0a0f1a',
    surface: '#111827',
    'surface-bright': '#1e293b',
    'surface-light': '#1e293b',
    'surface-variant': '#1e293b',
    'on-surface-variant': '#94a3b8',
    primary: '#E69830',
    'primary-darken-1': '#D18A28',
    secondary: '#0891b2',
    'secondary-darken-1': '#0e7490',
    accent: '#f472b6',
    error: '#ef4444',
    info: '#3b82f6',
    success: '#10b981',
    warning: '#f59e0b',
    'on-background': '#f1f5f9',
    'on-surface': '#e2e8f0',
    'on-primary': '#0a0f1a',
    'on-secondary': '#ffffff',
  },
  variables: {
    'border-color': '#334155',
    'border-opacity': 0.12,
    'high-emphasis-opacity': 0.95,
    'medium-emphasis-opacity': 0.7,
    'disabled-opacity': 0.38,
    'idle-opacity': 0.04,
    'hover-opacity': 0.08,
    'focus-opacity': 0.12,
    'selected-opacity': 0.08,
    'activated-opacity': 0.12,
    'pressed-opacity': 0.12,
    'dragged-opacity': 0.08,
  }
}

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'riScaleTheme',
    themes: {
      riScaleTheme,
    },
  },
  defaults: {
    VBtn: {
      rounded: 'lg',
      elevation: 0,
    },
    VCard: {
      rounded: 'xl',
      elevation: 0,
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      rounded: 'lg',
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
      rounded: 'lg',
    },
  },
})
