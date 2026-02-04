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

/**
 * List all saved pipelines for a project
 * @param {string} projectId - The project ID
 * @returns {Promise<object>} Response with pipelines array
 */
export async function listPipelines(projectId) {
  if (!projectId) {
    throw new Error('Project ID is required')
  }

  try {
    const response = await fetch(`${API_BASE_URL}/pipeline/list?project_id=${encodeURIComponent(projectId)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to list pipelines: ${response.statusText}`)
    }

    return await response.json()
  } catch (err) {
    console.error('Pipeline list error:', err)
    throw err
  }
}

/**
 * Load a saved pipeline manifest
 * @param {string} projectId - The project ID
 * @param {string} pipelineId - The pipeline file ID
 * @returns {Promise<object>} Response with manifest
 */
export async function loadPipeline(projectId, pipelineId) {
  if (!projectId) {
    throw new Error('Project ID is required')
  }
  if (!pipelineId) {
    throw new Error('Pipeline ID is required')
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}/pipeline/load?project_id=${encodeURIComponent(projectId)}&pipeline_id=${encodeURIComponent(pipelineId)}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      }
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to load pipeline: ${response.statusText}`)
    }

    return await response.json()
  } catch (err) {
    console.error('Pipeline load error:', err)
    throw err
  }
}

/**
 * Update an existing pipeline manifest
 * @param {string} projectId - The project ID
 * @param {string} pipelineId - The pipeline file ID
 * @param {object} manifest - The updated pipeline manifest object
 * @returns {Promise<object>} Response with updated pipeline info
 */
export async function updatePipeline(projectId, pipelineId, manifest) {
  if (!projectId) {
    throw new Error('Project ID is required')
  }
  if (!pipelineId) {
    throw new Error('Pipeline ID is required')
  }
  if (!manifest || typeof manifest !== 'object') {
    throw new Error('Manifest must be a valid object')
  }

  try {
    const response = await fetch(`${API_BASE_URL}/pipeline/save`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        project_id: projectId,
        pipeline_id: pipelineId,
        manifest: manifest
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to update pipeline: ${response.statusText}`)
    }

    return await response.json()
  } catch (err) {
    console.error('Pipeline update error:', err)
    throw err
  }
}

/**
 * Retrieve source columns for a manifest
 * @param {object} manifest - The pipeline manifest object
 * @param {string} sourceName - Optional source name to fetch columns for
 * @returns {Promise<object>} Response with sources map
 */
export async function getSourceColumns(manifest, sourceName = null) {
  if (!manifest || typeof manifest !== 'object') {
    throw new Error('Manifest must be a valid object')
  }

  try {
    const response = await fetch(`${API_BASE_URL}/pipeline/source-columns`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        manifest,
        source_name: sourceName
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to retrieve source columns: ${response.statusText}`)
    }

    return await response.json()
  } catch (err) {
    console.error('Source columns error:', err)
    throw err
  }
}
