/**
 * Pipeline Service
 * Handles API calls for saving and managing pipelines
 */

const API_BASE_URL = 'http://localhost:8000'

/**
 * Save a pipeline to the backend
 * @param {string} projectId - The project ID
 * @param {string} pipelineName - The name for the pipeline
 * @param {object} manifest - The pipeline manifest object
 * @returns {Promise<object>} Response with pipeline_path
 */
export async function savePipeline(projectId, pipelineName, manifest) {
  if (!projectId) {
    throw new Error('Project ID is required')
  }
  if (!pipelineName) {
    throw new Error('Pipeline name is required')
  }
  if (!manifest || typeof manifest !== 'object') {
    throw new Error('Manifest must be a valid object')
  }

  try {
    const response = await fetch(`${API_BASE_URL}/pipeline/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        project_id: projectId,
        pipeline_name: pipelineName,
        manifest: manifest
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to save pipeline: ${response.statusText}`)
    }

    return await response.json()
  } catch (err) {
    console.error('Pipeline save error:', err)
    throw err
  }
}
