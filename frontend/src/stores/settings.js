import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * Settings Store
 * Manages user preferences and settings
 */

const STORAGE_KEY = 'ri_scale_settings'

// Default settings
const DEFAULT_SETTINGS = {
  theme: 'dark',
  compactSidebar: false,
  showQuickStats: true,
  projectView: 'grid',
  analytics: true,
  notifications: {
    projectUpdates: true,
    dataTransfers: true,
    computationJobs: true,
    desktop: false,
    sound: false
  }
}

export const useSettingsStore = defineStore('settings', () => {
  // State
  const settings = ref({ ...DEFAULT_SETTINGS })
  const isLoaded = ref(false)

  // Getters
  const theme = computed(() => settings.value.theme)
  const compactSidebar = computed(() => settings.value.compactSidebar)
  const showQuickStats = computed(() => settings.value.showQuickStats)
  const projectView = computed(() => settings.value.projectView)
  const notificationSettings = computed(() => settings.value.notifications)

  // Actions
  function loadSettings() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const parsed = JSON.parse(saved)
        settings.value = {
          ...DEFAULT_SETTINGS,
          ...parsed,
          notifications: {
            ...DEFAULT_SETTINGS.notifications,
            ...parsed.notifications
          }
        }
      }
    } catch (e) {
      console.error('Failed to load settings:', e)
      settings.value = { ...DEFAULT_SETTINGS }
    }
    isLoaded.value = true
  }

  async function updateSettings(newSettings) {
    settings.value = {
      ...settings.value,
      ...newSettings,
      notifications: {
        ...settings.value.notifications,
        ...(newSettings.notifications || {})
      }
    }
    
    // Persist to localStorage
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings.value))
    } catch (e) {
      console.error('Failed to save settings:', e)
    }
  }

  function resetSettings() {
    settings.value = { ...DEFAULT_SETTINGS }
    localStorage.removeItem(STORAGE_KEY)
  }

  function updateSingleSetting(key, value) {
    if (key.includes('.')) {
      const [parent, child] = key.split('.')
      settings.value[parent][child] = value
    } else {
      settings.value[key] = value
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings.value))
  }

  // Initialize settings on store creation
  loadSettings()

  return {
    // State
    settings,
    isLoaded,
    // Getters
    theme,
    compactSidebar,
    showQuickStats,
    projectView,
    notificationSettings,
    // Actions
    loadSettings,
    updateSettings,
    resetSettings,
    updateSingleSetting
  }
})
