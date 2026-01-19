import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authService from '@/services/auth'

/**
 * Authentication Store
 * Manages user authentication state and actions
 */
export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  const isInitialized = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!user.value && !!token.value)
  const userName = computed(() => user.value?.name ?? '')
  const userInitials = computed(() => {
    if (!user.value) return ''
    const first = user.value.firstName?.[0] ?? ''
    const last = user.value.lastName?.[0] ?? ''
    return (first + last).toUpperCase()
  })
  const userRoles = computed(() => user.value?.roles ?? [])
  const isAdmin = computed(() => userRoles.value.includes('admin'))

  // Actions
  async function initialize() {
    if (isInitialized.value) return
    
    isLoading.value = true
    try {
      const session = await authService.getCurrentUser()
      if (session) {
        user.value = session.user
        token.value = session.token
      }
    } catch (e) {
      console.error('Failed to initialize auth:', e)
    } finally {
      isLoading.value = false
      isInitialized.value = true
    }
  }

  async function login(username, password) {
    isLoading.value = true
    error.value = null

    try {
      const result = await authService.login(username, password)
      
      if (result.success) {
        user.value = result.user
        token.value = result.token
        return { success: true }
      } else {
        error.value = result.error
        return { success: false, error: result.error }
      }
    } catch (e) {
      const message = e.message || 'An unexpected error occurred'
      error.value = message
      return { success: false, error: message }
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    isLoading.value = true
    try {
      await authService.logout()
      user.value = null
      token.value = null
    } finally {
      isLoading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  function hasRole(role) {
    return userRoles.value.includes(role)
  }

  return {
    // State
    user,
    token,
    isLoading,
    error,
    isInitialized,
    // Getters
    isAuthenticated,
    userName,
    userInitials,
    userRoles,
    isAdmin,
    // Actions
    initialize,
    login,
    logout,
    clearError,
    hasRole,
  }
})
