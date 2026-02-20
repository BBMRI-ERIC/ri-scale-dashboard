/**
 * Step Types Configuration for DPS Pipeline Builder
 * 
 * This module loads the shared step_types_config.yaml used by both frontend and backend
 * to ensure consistency and avoid configuration mismatches.
 * 
 * The YAML file is the single source of truth for step type definitions.
 */

import stepTypesConfigYaml from '../../../configs/step_types_config.yaml?raw'
import yaml from 'js-yaml'

// Parse the YAML configuration
const parsedConfig = yaml.load(stepTypesConfigYaml)

export const STEP_TYPES_CONFIG = parsedConfig

/**
 * Helper function to get config for a specific step type
 * @param {string} stepType - The step type (load, custom_command, join)
 * @returns {object} The configuration object for the step type
 */
export function getStepTypeConfig(stepType) {

  if (STEP_TYPES_CONFIG.step_types?.[stepType]) {
    return STEP_TYPES_CONFIG.step_types[stepType]
  }
  
  // Try finding by backend_type match
  const types = STEP_TYPES_CONFIG.step_types || {}
  for (const key in types) {
    if (types[key].backend_type === stepType) {
      return types[key]
    }
  }
  
  return undefined
}

/**
 * Helper function to get parameter config for a specific step type and param
 * @param {string} stepType - The step type
 * @param {string} paramName - The parameter name
 * @returns {object} The parameter configuration
 */
export function getParamConfig(stepType, paramName) {
  const typeConfig = getStepTypeConfig(stepType)
  return typeConfig?.params?.[paramName]
}

/**
 * Helper function to check if a parameter is required given current form state
 * @param {string} stepType - The step type
 * @param {string} paramName - The parameter name
 * @param {object} formState - Current form values
 * @returns {boolean} True if the parameter is required
 */
export function isParamRequired(stepType, paramName, formState = {}) {
  const paramConfig = getParamConfig(stepType, paramName)
  if (!paramConfig) return false

  if (paramConfig.required === true) return true

  if (paramConfig.requiredWhen) {
    // Simple evaluation of requiredWhen condition
    // Example: "mode === 'discovery'" or "execution_mode === 'per_row'"
    try {
      const condition = paramConfig.requiredWhen.replace(/(\w+)/g, (match) => {
        const value = formState[match]
        return typeof value === 'string' ? `'${value}'` : value
      })
      return eval(condition)
    } catch (e) {
      console.warn(`Failed to evaluate requiredWhen for ${paramName}:`, e)
      return false
    }
  }

  return false
}

/**
 * Get all parameter keys for a step type
 * @param {string} stepType - The step type
 * @returns {string[]} Array of parameter names
 */
export function getStepTypeParams(stepType) {
  const typeConfig = getStepTypeConfig(stepType)
  return typeConfig ? Object.keys(typeConfig.params) : []
}
