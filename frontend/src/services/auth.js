/**
 * Authentication Service
 * 
 * Handles authentication logic. Currently uses mock implementation
 * with a test user. Will be replaced with LifeScience AAI integration.
 */

// Mock users for development
const MOCK_USERS = [
  {
    id: 'user-001',
    username: 'test',
    password: 'test',
    email: 'test@ri-scale.eu',
    name: 'Test User',
    firstName: 'Test',
    lastName: 'User',
    avatar: null,
    roles: ['researcher', 'project_admin'],
    organization: 'BBMRI-ERIC',
    department: 'Digital Pathology',
    joinedAt: '2024-01-15',
  },
  {
    id: 'user-002',
    username: 'admin',
    password: 'admin',
    email: 'admin@ri-scale.eu',
    name: 'Admin User',
    firstName: 'Admin',
    lastName: 'User',
    avatar: null,
    roles: ['admin', 'researcher', 'project_admin'],
    organization: 'RI-SCALE Consortium',
    department: 'Platform Administration',
    joinedAt: '2023-06-01',
  }
]

// Simulated API delay
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * Authentication service interface
 * Abstracted to allow easy swap to real LifeScience AAI
 */
class AuthService {
  constructor() {
    this.storageKey = 'ri_scale_auth'
  }

  /**
   * Attempt to log in with credentials
   * @param {string} username 
   * @param {string} password 
   * @returns {Promise<{success: boolean, user?: object, error?: string}>}
   */
  async login(username, password) {
    // Simulate network delay
    await delay(800)

    const user = MOCK_USERS.find(
      u => u.username === username && u.password === password
    )

    if (!user) {
      return {
        success: false,
        error: 'Invalid username or password'
      }
    }

    // Create session token (mock)
    const token = this._generateToken()
    const session = {
      token,
      userId: user.id,
      expiresAt: Date.now() + (24 * 60 * 60 * 1000), // 24 hours
    }

    // Store session
    localStorage.setItem(this.storageKey, JSON.stringify(session))

    // Return user data (without password)
    const { password: _, ...userData } = user
    return {
      success: true,
      user: userData,
      token
    }
  }

  /**
   * Log out current user
   */
  async logout() {
    await delay(200)
    localStorage.removeItem(this.storageKey)
    return { success: true }
  }

  /**
   * Get current session if valid
   * @returns {Promise<{user: object} | null>}
   */
  async getCurrentUser() {
    const sessionData = localStorage.getItem(this.storageKey)
    
    if (!sessionData) {
      return null
    }

    try {
      const session = JSON.parse(sessionData)
      
      // Check if session expired
      if (session.expiresAt < Date.now()) {
        localStorage.removeItem(this.storageKey)
        return null
      }

      // Find user
      const user = MOCK_USERS.find(u => u.id === session.userId)
      if (!user) {
        return null
      }

      const { password: _, ...userData } = user
      return { user: userData, token: session.token }
    } catch {
      localStorage.removeItem(this.storageKey)
      return null
    }
  }

  /**
   * Check if user has specific role
   * @param {object} user 
   * @param {string} role 
   * @returns {boolean}
   */
  hasRole(user, role) {
    return user?.roles?.includes(role) ?? false
  }

  /**
   * Generate mock token
   * @private
   */
  _generateToken() {
    return 'mock_' + Math.random().toString(36).substring(2) + Date.now().toString(36)
  }
}

// Export singleton instance
export const authService = new AuthService()
export default authService
