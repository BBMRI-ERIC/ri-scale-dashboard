/**
 * HPC Jobs Service
 * Handles API calls for submitting and managing HPC jobs
 */

const API_BASE_URL = 'http://localhost:8000'

/**
 * Submit a new HPC job
 * @param {object} jobPayload - Job submission payload
 * @returns {Promise<object>} Response with job details
 */
export async function submitJob(jobPayload) {
  if (!jobPayload.projectId) {
    throw new Error('Project ID is required')
  }
  if (!jobPayload.jobType) {
    throw new Error('Job type is required')
  }
  if (!jobPayload.hpcSite) {
    throw new Error('HPC site is required')
  }

  // Validate job type specific requirements
  if (jobPayload.jobType === 'Data Preparation') {
    if (!jobPayload.manifestId) {
      throw new Error('Manifest file is required for Data Preparation jobs')
    }
  } else {
    if (!jobPayload.modelId) {
      throw new Error('Model is required')
    }
    if (!jobPayload.datasetId) {
      throw new Error('Dataset is required')
    }
  }

  try {
    const response = await fetch(`${API_BASE_URL}/jobs/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jobPayload)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to submit job: ${response.statusText}`)
    }

    return await response.json()
  } catch (err) {
    console.error('Job submission error:', err)
    throw err
  }
}

/**
 * Get all HPC jobs, optionally filtered by project
 * @param {string} projectId - Optional project ID filter
 * @returns {Promise<object>} Response with jobs array
 */
export async function getJobs(projectId = null) {
  try {
    const url = new URL(`${API_BASE_URL}/jobs`)
    if (projectId) {
      url.searchParams.append('project_id', projectId)
    }

    const response = await fetch(url.toString())

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to fetch jobs: ${response.statusText}`)
    }

    return await response.json()
  } catch (err) {
    console.error('Get jobs error:', err)
    throw err
  }
}

/**
 * Get details of a specific job
 * @param {string} jobId - The job ID
 * @returns {Promise<object>} Response with job details
 */
export async function getJob(jobId) {
  if (!jobId) {
    throw new Error('Job ID is required')
  }

  try {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to fetch job: ${response.statusText}`)
    }

    return await response.json()
  } catch (err) {
    console.error('Get job error:', err)
    throw err
  }
}

/**
 * Cancel a job
 * @param {string} jobId - The job ID
 * @returns {Promise<object>} Response with updated job
 */
export async function cancelJob(jobId) {
  if (!jobId) {
    throw new Error('Job ID is required')
  }

  try {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/cancel`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to cancel job: ${response.statusText}`)
    }

    return await response.json()
  } catch (err) {
    console.error('Cancel job error:', err)
    throw err
  }
}

/**
 * Retry a failed job
 * @param {string} jobId - The job ID
 * @returns {Promise<object>} Response with updated job
 */
export async function retryJob(jobId) {
  if (!jobId) {
    throw new Error('Job ID is required')
  }

  try {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/retry`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to retry job: ${response.statusText}`)
    }

    return await response.json()
  } catch (err) {
    console.error('Retry job error:', err)
    throw err
  }
}

/**
 * Get available manifests for a project (for Data Preparation jobs)
 * @param {string} projectId - The project ID
 * @returns {Promise<object>} Response with manifests array
 */
export async function getManifests(projectId) {
  if (!projectId) {
    throw new Error('Project ID is required')
  }

  try {
    const url = new URL(`${API_BASE_URL}/manifests`)
    url.searchParams.append('project_id', projectId)

    const response = await fetch(url.toString())

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to fetch manifests: ${response.statusText}`)
    }

    return await response.json()
  } catch (err) {
    console.error('Get manifests error:', err)
    throw err
  }
}

/**
 * Execute a Data Preparation job with specified mode
 * @param {string} jobId - The job ID
 * @param {boolean} simulated - Whether to run in simulated mode (default: false = production)
 * @returns {Promise<object>} Response with execution result
 */
export async function executeJob(jobId, simulated = false) {
  if (!jobId) {
    throw new Error('Job ID is required')
  }

  try {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ simulated })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `Failed to execute job: ${response.statusText}`)
    }

    return await response.json()
  } catch (err) {
    console.error('Execute job error:', err)
    throw err
  }
}
