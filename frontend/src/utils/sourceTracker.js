/**
 * Source Tracker Utility
 * Extracts and tracks data sources created by pipeline steps
 * to provide column name suggestions in the UI
 */

/**
 * Extract named groups from a regex pattern
 * @param {string} pattern - Regex pattern with named groups
 * @returns {Array<string>} Array of group names
 */
function extractNamedGroupsFromRegex(pattern) {
  if (!pattern || typeof pattern !== 'string') return []
  
  const groups = []
  const regex = /\(\?P<(\w+)>/g
  let match
  
  while ((match = regex.exec(pattern)) !== null) {
    groups.push(match[1])
  }
  
  return groups
}

/**
 * Extract source metadata from a pipeline step
 * @param {object} step - The pipeline step object
 * @param {number} stepIndex - Index of the step in the pipeline
 * @returns {object|null} Source metadata or null if step doesn't create a source
 */
export function extractSourceFromStep(step, stepIndex) {
  if (!step || !step.config) return null
  
  // Only load steps create sources
  if (step.type === 'load') {
    const outputName = step.config.output_source_name
    if (!outputName) return null
    
    const columns = []
    const mode = step.config.mode || 'discovery'

    if (mode === 'discovery') {
      // Add the main column name
      const columnName = step.config.columns?.column_name
      if (columnName) {
        columns.push(columnName)
      }
      
      // Extract named groups from filename pattern
      const filenamePattern = step.config.columns?.filename_to_columnname
      if (filenamePattern) {
        const namedGroups = extractNamedGroupsFromRegex(filenamePattern)
        columns.push(...namedGroups)
      }
    }
    
    return {
      source_name: outputName,
      columns: columns.filter(Boolean), // Remove any null/undefined
      from_step: stepIndex,
      step_name: step.config.name || step.name
    }
  }
  
  return null
}

/**
 * Get all available sources up to a specific step in the pipeline
 * @param {Array<object>} steps - Array of pipeline steps
 * @param {number} currentStepIndex - Index of the current step
 * @returns {Array<object>} Array of source metadata objects
 */
export function getAvailableSourcesUpToStep(steps, currentStepIndex) {
  if (!Array.isArray(steps)) return []
  
  const sources = []
  
  // Only look at steps before the current one
  for (let i = 0; i < currentStepIndex; i++) {
    const source = extractSourceFromStep(steps[i], i)
    if (source) {
      sources.push(source)
    }
  }
  
  return sources
}

/**
 * Get all available sources from all steps in the pipeline
 * @param {Array<object>} steps - Array of pipeline steps
 * @returns {Array<object>} Array of source metadata objects
 */
export function getAllAvailableSources(steps) {
  if (!Array.isArray(steps)) return []
  
  return steps
    .map((step, index) => extractSourceFromStep(step, index))
    .filter(Boolean)
}

/**
 * Get columns for a specific source by name
 * @param {Array<object>} sources - Array of source metadata
 * @param {string} sourceName - Name of the source to find
 * @returns {Array<string>} Array of column names or empty array if not found
 */
export function getColumnsForSource(sources, sourceName) {
  if (!Array.isArray(sources) || !sourceName) return []
  
  const source = sources.find(s => s.source_name === sourceName)
  return source ? source.columns : []
}

/**
 * Check if a source exists in the available sources
 * @param {Array<object>} sources - Array of source metadata
 * @param {string} sourceName - Name of the source to check
 * @returns {boolean} True if source exists
 */
export function sourceExists(sources, sourceName) {
  if (!Array.isArray(sources) || !sourceName) return false
  return sources.some(s => s.source_name === sourceName)
}
