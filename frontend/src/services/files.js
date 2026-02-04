/**
 * File browser service - provides API interactions for the file dialog system
 */

import { ref } from 'vue'

const API_BASE = '/api'

/**
 * Browse project data directory
 * @param {string} projectId - Project ID
 * @param {string} path - Current path to browse (relative to project data folder)
 * @returns {Promise} Directory contents and metadata
 */
export async function browseProjectData(projectId, path = '') {
  try {
    const query = path ? `?path=${encodeURIComponent(path)}` : ''
    const response = await fetch(
      `${API_BASE}/projects/${projectId}/data-browser${query}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `HTTP Error: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Error browsing directory:', error)
    throw error
  }
}

/**
 * Get file metadata
 * @param {string} projectId - Project ID
 * @param {string} path - File path relative to project data folder
 * @returns {Promise} File metadata
 */
export async function getFileMetadata(projectId, path) {
  try {
    const response = await fetch(
      `${API_BASE}/projects/${projectId}/data-browser?path=${encodeURIComponent(path)}`
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `HTTP Error: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Error getting file metadata:', error)
    throw error
  }
}
