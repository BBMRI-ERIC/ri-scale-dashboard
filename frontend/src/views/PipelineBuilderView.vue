<template>
  <v-layout class="dashboard-layout">
    <AppSidebar 
      v-model:rail="sidebarRail"
      @toggle-rail="sidebarRail = !sidebarRail"
    />

    <v-main class="dashboard-main">
      <AppHeader />

      <div class="dashboard-content pipeline-builder">
        <div class="section-header">
          <div>
            <h1 class="section-title">Pipeline Builder</h1>
            <p class="section-subtitle">Design your data processing pipeline by arranging stages visually</p>
          </div>
          <div class="actions">
            <v-btn 
              color="primary" 
              prepend-icon="mdi-plus" 
              @click="addStage()"
            >
              Add Stage
            </v-btn>
            <v-btn 
              variant="tonal" 
              prepend-icon="mdi-content-save-outline"
              @click="savePipeline"
            >
              Save Pipeline
            </v-btn>
          </div>
        </div>

        <v-row>
          <!-- Stage Library Panel -->
          <v-col cols="12" md="3">
            <v-card class="glass" :elevation="0">
              <v-card-title class="text-subtitle-1">Stage Library</v-card-title>
              <v-divider />
              <v-list density="comfortable">
                <v-list-item
                  v-for="block in stageLibrary"
                  :key="block.name"
                  :title="block.name"
                  :subtitle="block.description"
                  :prepend-icon="block.icon"
                  @click="addStage(block)"
                  class="library-item"
                />
              </v-list>
            </v-card>
          </v-col>

          <!-- Pipeline Canvas -->
          <v-col cols="12" md="6">
            <v-card class="glass" :elevation="0">
              <v-card-title class="text-subtitle-1">Pipeline Canvas</v-card-title>
              <v-divider />
              <div class="canvas">
                <div v-if="stages.length === 0" class="empty-state">
                  <v-icon size="64" color="primary" class="mb-3">mdi-flow-chart</v-icon>
                  <h3>No stages yet</h3>
                  <p>Add stages from the library to start building your pipeline</p>
                </div>
                <v-timeline 
                  v-else
                  dense 
                  align="start"
                  class="pipeline-timeline"
                >
                  <v-timeline-item
                    v-for="(stage, idx) in stages"
                    :key="stage.id"
                    dot-color="primary"
                    fill-dot
                    size="small"
                  >
                    <div 
                      class="stage-card"
                      :class="{ 'selected': selectedStageId === stage.id }"
                      @click="selectStage(stage.id)"
                    >
                      <div class="stage-header">
                        <div class="stage-title">
                          <v-icon size="18" class="mr-2">{{ getStageIcon(stage) }}</v-icon>
                          {{ stage.config?.name || stage.name }}
                        </div>
                        <div class="stage-actions">
                          <v-btn 
                            icon 
                            size="small" 
                            variant="text" 
                            @click.stop="moveStage(idx, -1)" 
                            :disabled="idx === 0"
                          >
                            <v-icon>mdi-arrow-up</v-icon>
                          </v-btn>
                          <v-btn 
                            icon 
                            size="small" 
                            variant="text" 
                            @click.stop="moveStage(idx, 1)" 
                            :disabled="idx === stages.length - 1"
                          >
                            <v-icon>mdi-arrow-down</v-icon>
                          </v-btn>
                          <v-btn 
                            icon 
                            size="small" 
                            variant="text" 
                            color="error" 
                            @click.stop="removeStage(stage.id)"
                          >
                            <v-icon>mdi-close</v-icon>
                          </v-btn>
                        </div>
                      </div>
                      <p class="stage-note">Click to configure this stage</p>
                    </div>
                  </v-timeline-item>
                </v-timeline>
              </div>
            </v-card>
          </v-col>

          <!-- Stage Details + YAML Panel -->
          <v-col cols="12" md="3">
            <v-card class="glass" :elevation="0">
              <v-card-title class="text-subtitle-1">Stage Details</v-card-title>
              <v-divider />
              <v-tabs v-model="rightPanelTab" density="comfortable">
                <v-tab value="details" prepend-icon="mdi-cog-outline">Details</v-tab>
                <v-tab value="yaml" prepend-icon="mdi-code-tags">YAML</v-tab>
              </v-tabs>
              <v-divider />

              <div class="details-panel" v-if="rightPanelTab === 'details'">
                <div v-if="!selectedStage" class="empty-details">
                  <v-icon size="48" color="grey" class="mb-3">mdi-cog-outline</v-icon>
                  <p class="text-medium-emphasis">Select a stage from the canvas to configure it</p>
                </div>
                <div v-else class="stage-form">
                  <div class="text-subtitle-2 mb-2">{{ selectedStage.name }}</div>
                  <div class="text-caption text-medium-emphasis mb-4">Type: {{ selectedStage.type }}</div>
                  
                  <!-- Display Name -->
                  <v-text-field
                    v-model="selectedStage.config.name"
                    label="Display Name"
                    variant="outlined"
                    density="compact"
                    hide-details
                    class="mb-3"
                  />
                  
                  <!-- Enable Toggle -->
                  <v-switch
                    v-model="selectedStage.config.enabled"
                    color="primary"
                    label="Enable stage"
                    hide-details
                    class="mb-4"
                  />
                  
                  <v-divider class="mb-4" />
                  
                  <!-- Dynamic Step Parameters -->
                  <div v-if="selectedStageConfig" class="step-params">
                    <div class="text-subtitle-2 mb-3">Configuration</div>
                    
                    <template v-for="(paramConfig, paramKey) in selectedStageConfig.params" :key="paramKey">
                      <div v-if="shouldShowParam(paramKey, paramConfig)" class="param-field mb-3">
                        <!-- String fields -->
                        <v-text-field
                          v-if="paramConfig.type === 'string'"
                          v-model="selectedStage.config[paramKey]"
                          :label="paramConfig.label"
                          :hint="paramConfig.helpText"
                          :placeholder="getParamPlaceholder(paramConfig)"
                          :required="isParamRequiredForStage(paramKey, paramConfig)"
                          variant="outlined"
                          density="compact"
                          persistent-hint
                        />
                        
                        <!-- Boolean fields -->
                        <v-switch
                          v-else-if="paramConfig.type === 'boolean'"
                          v-model="selectedStage.config[paramKey]"
                          :label="paramConfig.label"
                          :hint="paramConfig.helpText"
                          color="primary"
                          persistent-hint
                          hide-details="auto"
                        />
                        
                        <!-- Enum/Select fields -->
                        <v-select
                          v-else-if="paramConfig.type === 'enum'"
                          v-model="selectedStage.config[paramKey]"
                          :label="paramConfig.label"
                          :hint="paramConfig.helpText"
                          :items="paramConfig.enumValues"
                          item-title="label"
                          item-value="value"
                          :required="isParamRequiredForStage(paramKey, paramConfig)"
                          variant="outlined"
                          density="compact"
                          persistent-hint
                        />
                        
                        <!-- Object fields (nested) -->
                        <v-expansion-panels v-else-if="paramConfig.type === 'object'" variant="accordion">
                          <v-expansion-panel>
                            <v-expansion-panel-title>
                              {{ paramConfig.label }}
                              <template v-if="paramConfig.helpText">
                                <v-tooltip location="top">
                                  <template v-slot:activator="{ props }">
                                    <v-icon v-bind="props" size="small" class="ml-2">mdi-help-circle-outline</v-icon>
                                  </template>
                                  {{ paramConfig.helpText }}
                                </v-tooltip>
                              </template>
                            </v-expansion-panel-title>
                            <v-expansion-panel-text>
                              <template v-for="(subParamConfig, subParamKey) in getObjectSubParams(paramConfig)" :key="subParamKey">
                                <div v-if="shouldShowParam(subParamKey, subParamConfig)" class="mb-3">
                                  <!-- String sub-fields -->
                                  <v-text-field
                                    v-if="subParamConfig.type === 'string'"
                                    v-model="getOrCreateNestedParam(paramKey)[subParamKey]"
                                    :label="subParamConfig.label"
                                    :hint="subParamConfig.helpText"
                                    :placeholder="getParamPlaceholder(subParamConfig)"
                                    variant="outlined"
                                    density="compact"
                                    persistent-hint
                                  />
                                  
                                  <!-- Boolean sub-fields -->
                                  <v-switch
                                    v-else-if="subParamConfig.type === 'boolean'"
                                    v-model="getOrCreateNestedParam(paramKey)[subParamKey]"
                                    :label="subParamConfig.label"
                                    :hint="subParamConfig.helpText"
                                    color="primary"
                                    persistent-hint
                                    hide-details="auto"
                                  />
                                </div>
                              </template>
                            </v-expansion-panel-text>
                          </v-expansion-panel>
                        </v-expansion-panels>
                      </div>
                    </template>
                  </div>
                  
                  <v-divider class="my-4" />
                  <div class="text-caption text-medium-emphasis mb-1">Stage ID</div>
                  <div class="text-body-2 font-mono">{{ selectedStage.id }}</div>
                </div>
              </div>

              <div class="yaml-panel" v-else>
                <div class="yaml-actions">
                  <v-btn
                    size="small"
                    variant="tonal"
                    prepend-icon="mdi-refresh"
                    @click="resetYamlFromStages"
                  >
                    Reset
                  </v-btn>
                  <v-btn
                    size="small"
                    color="primary"
                    prepend-icon="mdi-check"
                    @click="applyYamlToStages"
                  >
                    Apply YAML
                  </v-btn>
                </div>

                <v-textarea
                  v-model="yamlText"
                  label="Pipeline manifest (YAML)"
                  variant="outlined"
                  density="comfortable"
                  rows="18"
                  class="yaml-textarea"
                />

                <div v-if="yamlError" class="yaml-error">
                  {{ yamlError }}
                </div>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </v-main>
  </v-layout>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import yaml from 'js-yaml'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import { STEP_TYPES_CONFIG, getStepTypeConfig } from '@/configs/step_types_config.js'

const sidebarRail = ref(false)
const rightPanelTab = ref('details')

const yamlText = ref('')
const yamlError = ref('')
const yamlDirty = ref(false)
const isSyncingFromStages = ref(false)
const isSyncingFromYaml = ref(false)
let yamlParseTimer = null

// Build stage library from shared config
const stageLibrary = computed(() => {
  const stepTypes = STEP_TYPES_CONFIG.stepTypes || {}
  return Object.keys(stepTypes).map(key => ({
    name: stepTypes[key].displayName,
    type: stepTypes[key].backendType || key,
    icon: stepTypes[key].icon,
    description: `Type: ${stepTypes[key].backendType || key} - ${stepTypes[key].description}`,
  }))
})

// Pipeline stages
const stages = ref([])

// Selected stage for configuration
const selectedStageId = ref(null)
const selectedStage = computed(() => {
  return stages.value.find(s => s.id === selectedStageId.value)
})

// Get config for the selected stage
const selectedStageConfig = computed(() => {
  if (!selectedStage.value) return null
  return getStepTypeConfig(selectedStage.value.type)
})

// Generate unique ID for stages
function generateId() {
  return `stage_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// Get icon for stage type or name
function getStageIcon(stageOrName) {
  const type = typeof stageOrName === 'object' ? stageOrName.type : undefined
  if (type) {
    const matchByType = stageLibrary.value.find(s => s.type === type)
    if (matchByType) return matchByType.icon
  }

  const name = typeof stageOrName === 'object' ? stageOrName.name : stageOrName
  const matchByName = stageLibrary.value.find(s => s.name === name)
  return matchByName ? matchByName.icon : 'mdi-cube-outline'
}

// Add a new stage to the pipeline
function addStage(stageDefinition) {
  const definition = (stageDefinition && typeof stageDefinition === 'object')
    ? stageDefinition
    : stageLibrary.value.find(s => s.name === stageDefinition)
      //|| stageLibrary.value.find(s => s.type === 'custom_command')
      //|| { name: 'Run Command', type: 'custom_command', icon: 'mdi-console' }

  const id = generateId()
  const stageName = definition.name || 'Custom Stage'

  stages.value.push({
    id,
    name: stageName,
    type: definition.type, //|| guessStepType(stageName),
    config: {
      name: stageName,
      enabled: true,
    },
  })
  selectedStageId.value = id
}

// Remove a stage from the pipeline
function removeStage(id) {
  const index = stages.value.findIndex(s => s.id === id)
  if (index !== -1) {
    stages.value.splice(index, 1)
    if (selectedStageId.value === id) {
      selectedStageId.value = null
    }
  }
}

// Select a stage for configuration
function selectStage(id) {
  selectedStageId.value = id
}

// Move a stage up or down in the pipeline
function moveStage(index, delta) {
  const target = index + delta
  if (target < 0 || target >= stages.value.length) return
  
  const newStages = [...stages.value]
  const [item] = newStages.splice(index, 1)
  newStages.splice(target, 0, item)
  stages.value = newStages
}

// Helper: Check if a parameter should be shown based on conditional logic
function shouldShowParam(paramKey, paramConfig) {
  if (!paramConfig.conditionalOn) return true
  
  const conditionalValue = selectedStage.value?.config?.[paramConfig.conditionalOn]
  return conditionalValue === paramConfig.conditionalValue
}

// Helper: Check if a parameter is required
function isParamRequiredForStage(paramKey, paramConfig) {
  if (paramConfig.required === true) return true
  
  if (paramConfig.requiredWhen) {
    // Simple evaluation for common cases
    const condition = paramConfig.requiredWhen
    const formState = selectedStage.value?.config || {}
    
    // Parse conditions like "mode == 'discovery'" or "execution_mode == 'per_row'"
    const matches = condition.match(/(\w+)\s*===?\s*['"]([^'"]+)['"]/)
    if (matches) {
      const [, fieldName, expectedValue] = matches
      return formState[fieldName] === expectedValue
    }
  }
  
  return false
}

// Helper: Get placeholder text for a parameter
function getParamPlaceholder(paramConfig) {
  if (paramConfig.examples && paramConfig.examples.length > 0) {
    return `e.g., ${paramConfig.examples[0]}`
  }
  if (paramConfig.default !== null && paramConfig.default !== undefined) {
    return String(paramConfig.default)
  }
  return ''
}

// Helper: Get sub-parameters for object type fields
function getObjectSubParams(paramConfig) {
  const subParams = {}
  for (const key in paramConfig) {
    if (key !== 'label' && key !== 'type' && key !== 'required' && 
        key !== 'required_when' && key !== 'help_text' && key !== 'helpText' &&
        typeof paramConfig[key] === 'object' && paramConfig[key].type) {
      subParams[key] = paramConfig[key]
    }
  }
  return subParams
}

// Helper: Get or create nested parameter object
function getOrCreateNestedParam(paramKey) {
  if (!selectedStage.value.config[paramKey]) {
    selectedStage.value.config[paramKey] = {}
  }
  return selectedStage.value.config[paramKey]
}

// Save pipeline (placeholder for future implementation)
function savePipeline() {
  console.log('Saving pipeline:', stages.value)
  // TODO: Implement actual save functionality
  alert('Pipeline save functionality will be implemented soon!')
}

function buildManifestFromStages() {
  return {
    manifest_id: `id${new Date().toISOString().slice(0, 10)}`,
    created_by: 'ui@ri-scale',
    created_at: new Date().toISOString(),
    simulated: true,
    job_steps: stages.value.map((s) => {
      // map UI stage -> DPS manifest step
      const displayName = (s.config && s.config.name) || s.name || 'Unnamed step'
      // do not duplicate the display name inside params.name
      const { enabled, name, ...params } = (s.config || {})
      return {
        step_name: displayName,
        type: s.type || guessStepType(s.name),
        enabled: enabled !== false,
        params: params,
      }
    }),
  }
}

function guessStepType(stageName) {
  const normalized = (stageName || '').toLowerCase()
  if (normalized.includes('ingest')) return 'load'
  if (normalized.includes('join')) return 'join'
  return 'custom'
}

function resetYamlFromStages() {
  yamlError.value = ''
  const manifest = buildManifestFromStages()
  isSyncingFromStages.value = true
  yamlText.value = yaml.dump(manifest, { lineWidth: 120, noRefs: true })
  yamlDirty.value = false
  // allow watchers to observe the change first
  queueMicrotask(() => {
    isSyncingFromStages.value = false
  })
}

function applyYamlToStages({ preserveSelection = false } = {}) {
  yamlError.value = ''
  try {
    const parsed = yaml.load(yamlText.value)
    if (!parsed || typeof parsed !== 'object') {
      throw new Error('YAML root must be a mapping/object.')
    }
    if (!Array.isArray(parsed.job_steps)) {
      throw new Error('Missing required field: job_steps (must be a list).')
    }

    const newStages = parsed.job_steps.map((step) => {
      const id = generateId()
      const stepName = step.step_name || step.name || 'Unnamed step'
      const allParams = step.params && typeof step.params === 'object' ? step.params : {}
      // remove any legacy name field from params; step_name is the canonical display name
      const { name: _ignoredName, ...params } = allParams
      return {
        id,
        name: stepName,
        type: step.type || guessStepType(stepName),
        config: {
          ...params,
          enabled: step.enabled !== false,
          // display name always mirrors step_name
          name: stepName,
          description: params.description || '',
          notes: params.notes || '',
        },
      }
    })

    // avoid feedback loop: YAML -> stages should not immediately regenerate YAML while user is editing
    isSyncingFromYaml.value = true
    const previousSelectedName = selectedStage.value?.name
    stages.value = newStages

    if (preserveSelection && previousSelectedName) {
      const match = stages.value.find(s => s.name === previousSelectedName)
      selectedStageId.value = match?.id ?? stages.value[0]?.id ?? null
    } else {
      selectedStageId.value = stages.value[0]?.id ?? null
    }

    // If the user explicitly clicked "Apply", consider YAML clean.
    yamlDirty.value = false
    queueMicrotask(() => {
      isSyncingFromYaml.value = false
    })
  } catch (err) {
    yamlError.value = err?.message ? String(err.message) : 'Invalid YAML.'
  }
}

watch(
  stages,
  () => {
    // Keep YAML preview in sync unless user is actively editing it or YAML is the source of truth.
    if (isSyncingFromYaml.value) return
    if (!yamlDirty.value && rightPanelTab.value !== 'yaml') resetYamlFromStages()
  },
  { deep: true, immediate: true }
)

watch(
  yamlText,
  () => {
    if (isSyncingFromStages.value) return
    yamlDirty.value = true

    // Live update: while on YAML tab, debounce-parse and update stages as the user types.
    if (rightPanelTab.value !== 'yaml') return
    if (yamlParseTimer) clearTimeout(yamlParseTimer)
    yamlParseTimer = setTimeout(() => {
      // keep selection if possible while editing
      applyYamlToStages({ preserveSelection: true })
    }, 300)
  },
  { flush: 'post' }
)

watch(
  rightPanelTab,
  (tab) => {
    // When entering YAML tab, ensure YAML is up-to-date and treat YAML as the editable source.
    if (tab === 'yaml') {
      if (!yamlDirty.value) {
        resetYamlFromStages()
      }
    } else {
      // When leaving YAML tab, switch the source of truth back to the stages model:
      // clear YAML error state, mark YAML as clean, and regenerate YAML from stages.
      yamlError.value = ''
      yamlDirty.value = false
      resetYamlFromStages()
    }
  }
)

// Keep internal stage.name in sync with the display name used in the UI/YAML (config.name)
watch(
  () => selectedStage.value && selectedStage.value.config && selectedStage.value.config.name,
  (newName) => {
    if (!selectedStage.value || !newName) return
    selectedStage.value.name = newName
  }
)
</script>

<style scoped lang="scss">
.pipeline-builder {
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  gap: 16px;
  flex-wrap: wrap;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
}

.section-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #f1f5f9;
}

.section-subtitle {
  font-size: 0.875rem;
  color: #94a3b8;
  margin: 0;
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.library-item {
  cursor: pointer;
  transition: background 0.2s;
  
  &:hover {
    background: rgba(230, 152, 48, 0.08);
  }
}

.canvas {
  padding: 24px;
  min-height: 500px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
  color: #94a3b8;
  
  h3 {
    margin: 8px 0;
    color: #cbd5e1;
  }
  
  p {
    margin: 0;
    font-size: 0.875rem;
  }
}

.pipeline-timeline {
  padding: 16px 0;
}

.stage-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 8px;
  
  &:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(230, 152, 48, 0.4);
  }
  
  &.selected {
    background: rgba(230, 152, 48, 0.1);
    border-color: #E69830;
  }
}

.stage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.stage-title {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #f1f5f9;
  flex: 1;
  min-width: 0;
}

.stage-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.stage-note {
  color: #94a3b8;
  margin: 0;
  font-size: 0.75rem;
}

.details-panel {
  padding: 16px;
  min-height: 400px;
  max-height: 600px;
  overflow-y: auto;
}

.stage-form {
  .step-params {
    .param-field {
      margin-bottom: 16px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

.empty-details {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
  
  p {
    margin: 0;
    font-size: 0.875rem;
  }
}

.font-mono {
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  color: #64748b;
}

.yaml-panel {
  padding: 16px;
}

.yaml-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-bottom: 8px;
}

.yaml-textarea :deep(textarea) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 12px;
  line-height: 1.4;
}

.yaml-error {
  margin-top: 8px;
  color: #ef4444;
  font-size: 0.875rem;
}
</style>
