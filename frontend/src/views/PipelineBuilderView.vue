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
              variant="tonal" 
              prepend-icon="mdi-folder-open-outline"
              @click="showLoadDialog"
            >
              Load Pipeline
            </v-btn>
            <v-btn 
              variant="tonal" 
              prepend-icon="mdi-content-save-outline"
              @click="showSaveDialog"
            >
              Save Pipeline
            </v-btn>
          </div>
        </div>

        <!-- Load Pipeline Dialog -->
        <v-dialog v-model="loadDialogOpen" max-width="500px">
          <v-card>
            <v-card-title>Load Pipeline</v-card-title>
            <v-divider />
            <v-card-text class="pt-6">
              <div class="text-subtitle-2 mb-2">Project</div>
              <div class="text-body-2 mb-4">{{ selectedProjectName }}</div>

              <div v-if="isLoadingPipelines" class="text-center py-4">
                <v-progress-circular indeterminate color="primary" />
              </div>
              <div v-else-if="savedPipelines.length === 0" class="text-center py-4 text-body-2">
                No saved pipelines found for this project
              </div>
              <v-list v-else density="comfortable" class="bg-transparent">
                <v-list-item
                  v-for="pipeline in savedPipelines"
                  :key="pipeline.id"
                  :title="pipeline.name"
                  :subtitle="`Saved ${new Date(pipeline.created_at * 1000).toLocaleDateString()}`"
                  @click="loadSelectedPipeline(pipeline.id)"
                  class="cursor-pointer"
                  style="border: 1px solid var(--v-border-color); border-radius: 4px; margin-bottom: 8px;"
                />
              </v-list>
              <div v-if="loadError" class="text-error text-caption mt-2 mb-4">{{ loadError }}</div>
            </v-card-text>
            <v-divider />
            <v-card-actions>
              <v-spacer />
              <v-btn variant="plain" @click="loadDialogOpen = false">Cancel</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Save Pipeline Dialog -->
        <v-dialog v-model="saveDialogOpen" max-width="600px">
          <v-card>
            <v-card-title>Save Pipeline</v-card-title>
            <v-divider />
            <v-card-text class="pt-6">
              <div class="text-subtitle-2 mb-2">Project</div>
              <div class="text-body-2 mb-4">{{ selectedProjectName }}</div>

              <v-text-field
                v-model="pipelineName"
                label="Pipeline Name"
                placeholder="Enter a descriptive name for your pipeline"
                variant="outlined"
                density="comfortable"
                clearable
                @keyup.enter="confirmSavePipeline"
              />
              
              <div class="text-subtitle-2 mt-6 mb-2">Existing Pipelines</div>
              <div v-if="isSavingDialogLoading" class="text-center py-4">
                <v-progress-circular indeterminate color="primary" size="24" />
              </div>
              <div v-else-if="savedPipelinesForSave.length === 0" class="text-body-2 text-medium-emphasis py-4">
                No existing pipelines in this project
              </div>
              <v-list v-else density="comfortable" class="bg-transparent" style="max-height: 250px; overflow-y: auto;">
                <v-list-item
                  v-for="pipeline in savedPipelinesForSave"
                  :key="pipeline.id"
                  :title="pipeline.name"
                  :subtitle="`Saved ${new Date(pipeline.created_at * 1000).toLocaleDateString()}`"
                  @click="selectExistingPipeline(pipeline.name)"
                  class="cursor-pointer"
                  :active="pipelineName === pipeline.name"
                  style="border-radius: 4px;"
                />
              </v-list>
              
              <div v-if="saveError" class="text-error text-caption mt-4 mb-4">{{ saveError }}</div>
            </v-card-text>
            <v-divider />
            <v-card-actions>
              <v-spacer />
              <v-btn variant="plain" @click="saveDialogOpen = false">Cancel</v-btn>
              <v-btn color="primary" :loading="isSaving" @click="confirmSavePipeline">Save</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Overwrite Pipeline Dialog -->
        <v-dialog v-model="overwriteDialogOpen" max-width="400px">
          <v-card>
            <v-card-title>Pipeline Already Exists</v-card-title>
            <v-divider />
            <v-card-text class="pt-6">
              <p>A pipeline named "<strong>{{ pipelineName }}</strong>" already exists.</p>
              <p class="mt-4">Do you want to overwrite it?</p>
            </v-card-text>
            <v-divider />
            <v-card-actions>
              <v-spacer />
              <v-btn variant="plain" @click="overwriteDialogOpen = false">Cancel</v-btn>
              <v-btn color="warning" :loading="isSaving" @click="performSavePipeline(true)">Overwrite</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <v-row>
          <!-- Stage Library Panel -->
          <v-col cols="12" md="3">
            <v-card class="glass" :elevation="0">
              <v-card-title class="text-subtitle-1">Stage Library</v-card-title>
              <v-divider />
              <v-list density="comfortable">
                <!-- Basic Steps Group -->
                <v-list-group value="Basic">
                  <template v-slot:activator="{ props }">
                    <v-list-item
                      v-bind="props"
                      title="Basic"
                      :prepend-icon="'mdi-toolbox'"
                    />
                  </template>
                  <v-list-item
                    v-for="block in stageLibrary.basic"
                    :key="block.name"
                    :title="block.name"
                    :subtitle="block.description"
                    :prepend-icon="block.icon"
                    @click="addStage(block)"
                    class="library-item"
                  />
                </v-list-group>

                <!-- Custom Chains by Category -->
                <v-list-group
                  v-for="(chains, category) in stageLibrary.custom"
                  :key="category"
                  :value="category"
                  v-if="Object.keys(stageLibrary.custom).length > 0"
                >
                  <template v-slot:activator="{ props }">
                    <v-list-item
                      v-bind="props"
                      :title="category"
                      :prepend-icon="'mdi-package-variant-closed'"
                    />
                  </template>
                  <v-list-item
                    v-for="block in chains"
                    :key="block.name"
                    :title="block.name"
                    :subtitle="block.description"
                    :prepend-icon="block.icon"
                    @click="addStage(block)"
                    class="library-item"
                  />
                </v-list-group>
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

                  <!-- Chain-specific form -->
                  <template v-if="isChainStage(selectedStage)">
                    <div class="text-body-2 text-medium-emphasis mb-2" style="margin-left: 12px;">Composite command chain</div>
                    <div class="text-caption text-medium-emphasis mb-4" v-if="selectedChainDefinition?.description" style="margin-left: 12px;">
                      {{ selectedChainDefinition.description }}
                    </div>

                    <v-text-field
                      v-model="selectedStage.config.name"
                      label="Display Name"
                      variant="outlined"
                      density="compact"
                      hide-details
                      class="mb-3"
                      style="margin-left: 12px;"
                    />

                    <v-switch
                      v-model="selectedStage.config.enabled"
                      color="primary"
                      label="Enable chain"
                      hide-details
                      class="mb-4"
                      style="margin-left: 12px;"
                    />

                    <v-divider class="mb-4" style="margin-left: 12px;" />

                    <div class="text-subtitle-2 mb-2" style="margin-left: 12px;">Inputs</div>
                    <div class="text-caption text-medium-emphasis mb-3" style="margin-left: 12px;">Values are substituted into the chain steps.</div>
                    <template v-for="sub in selectedChainFormInputs || []" :key="sub.name">
                      <!-- Use registry source as dropdown if specified -->
                      <v-select
                        v-if="sub.use_registry_source"
                        v-model="selectedStage.config.userInputs[sub.name]"
                        :label="sub.label || sub.name"
                        :placeholder="sub.default || ''"
                        :hint="sub.helpText"
                        :items="getRegisteredValues(sub.use_registry_source)"
                        variant="outlined"
                        density="compact"
                        class="mb-3"
                        style="margin-left: 12px;"
                      />
                      <!-- Regular text input for non-registry fields -->
                      <v-text-field
                        v-else
                        v-model="selectedStage.config.userInputs[sub.name]"
                        :label="sub.label || sub.name"
                        :placeholder="sub.default || ''"
                        :hint="sub.helpText"
                        variant="outlined"
                        density="compact"
                        class="mb-3"
                        style="margin-left: 12px;"
                      />
                    </template>

                    <div class="mb-3" style="margin-left: 12px;">
                      <div class="text-subtitle-2 mb-2">Chain Steps:</div>
                      <ul>
                        <li v-for="(step, idx) in selectedChainDefinition?.chain || []" :key="idx">
                          {{ getStepTypeConfig(step.type)?.display_name || step.type }}
                        </li>
                      </ul>
                    </div>
                  </template>

                  <!-- Regular step form -->
                  <template v-else>
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
                            :items="getEnumItemsForField(paramConfig)"
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
                  </template>
                  
                  <v-divider class="my-4" />
                  <div class="text-caption text-medium-emphasis mb-1">Stage ID</div>
                  <div class="text-body-2 font-mono">{{ selectedStage.id }}</div>
                </div>
              </div>

              <div class="yaml-panel" v-else>

                <v-textarea
                  v-model="yamlText"
                  label="Pipeline manifest (YAML)"
                  variant="outlined"
                  density="comfortable"
                  rows="20"
                  class="yaml-textarea"
                />

                <div v-if="yamlError" class="yaml-error">
                  <strong>Parse Error:</strong> {{ yamlError }}
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
import { useProjectsStore } from '@/stores/projects.js'
import { useAuthStore } from '@/stores/auth.js'
import { savePipeline, listPipelines, loadPipeline, updatePipeline } from '@/services/pipelines.js'

const projectsStore = useProjectsStore()
const authStore = useAuthStore()
const sidebarRail = ref(false)
const rightPanelTab = ref('details')

const yamlText = ref('')
const yamlError = ref('')
const yamlDirty = ref(false)
const isSyncingFromStages = ref(false)
const isSyncingFromYaml = ref(false)
let yamlParseTimer = null

// Save dialog state
const saveDialogOpen = ref(false)
const pipelineName = ref('')
const saveError = ref('')
const isSaving = ref(false)
const savedPipelinesForSave = ref([])
const isSavingDialogLoading = ref(false)

// Load dialog state
const loadDialogOpen = ref(false)
const savedPipelines = ref([])
const isLoadingPipelines = ref(false)
const loadError = ref('')

// Overwrite dialog state
const overwriteDialogOpen = ref(false)
const existingPipelineId = ref(null)

const selectedProjectName = computed(() => {
  const project = projectsStore.selectedProject
  return project?.title || project?.shortTitle || 'Unknown Project'
})

// Build stage library from shared config (step types + command chains)
const stageLibrary = computed(() => {
  const stepTypes = STEP_TYPES_CONFIG.step_types || {}
  const chains = STEP_TYPES_CONFIG.command_chains || {}

  const typeEntries = Object.keys(stepTypes).map(key => ({
    name: stepTypes[key].display_name,
    type: stepTypes[key].backend_type || key,
    icon: stepTypes[key].icon,
    description: `Type: ${stepTypes[key].backend_type || key} - ${stepTypes[key].description}`,
    isChain: false,
  }))

  const chainEntries = Object.keys(chains).map(key => {
    const chainDef = chains[key] || {}
    // Map substitutions to a userInputs object for form binding (include per_row column selectors)
    const userInputs = (chainDef.substitutions || [])
      .reduce((acc, s) => {
        acc[s.name] = { name: s.name, label: s.label, default: s.default, helpText: s.help_text, scope: s.scope }
        return acc
      }, {})

    return {
      name: chainDef.display_name || key,
      type: 'command_chain',
      icon: chainDef.icon || 'mdi-source-merge',
      description: chainDef.description || 'Composite command chain',
      isChain: true,
      chainKey: key,
      chain: chainDef.chain || [],
      userInputs,
      substitutions: chainDef.substitutions || [],
      category: chainDef.category || 'Uncategorized',
    }
  })

  // Group chains by category
  const chainsByCategory = chainEntries.reduce((acc, chain) => {
    const cat = chain.category
    if (!acc[cat]) {
      acc[cat] = []
    }
    acc[cat].push(chain)
    return acc
  }, {})

  return {
    basic: typeEntries,
    custom: chainsByCategory,
  }
})


// Pipeline stages
const stages = ref([])

// Field Registry: Maps registry IDs to arrays of registered values
// e.g., { "sources": ["source1", "wsi_source", "labels"] }
// Fields with register_id add their values here, fields with use_registry_source read from here
const fieldRegistry = ref({})

// Helper to add a value to the registry
function registerFieldValue(registryId, value) {
  if (!registryId || !value) return
  if (!fieldRegistry.value[registryId]) {
    fieldRegistry.value[registryId] = []
  }
  // Add value if not already present (avoid duplicates)
  if (!fieldRegistry.value[registryId].includes(value)) {
    fieldRegistry.value[registryId].push(value)
  }
}

// Helper to get registered values for a registry ID
function getRegisteredValues(registryId) {
  return fieldRegistry.value[registryId] || []
}

// Helper to clear the registry (useful when loading a new pipeline)
function clearRegistry() {
  fieldRegistry.value = {}
}

// Selected stage for configuration
const selectedStageId = ref(null)
const selectedStage = computed(() => {
  return stages.value.find(s => s.id === selectedStageId.value)
})

// Get config for the selected stage
const selectedStageConfig = computed(() => {
  if (!selectedStage.value) return null
  if (isChainStage(selectedStage.value)) return null
  return getStepTypeConfig(selectedStage.value.type)
})

const selectedChainDefinition = computed(() => {
  if (!selectedStage.value || !isChainStage(selectedStage.value)) return null
  return getChainDefinition(selectedStage.value.config.chainKey)
})

// Flatten form-scoped substitutions for the selected chain into an array the template can iterate
const selectedChainUserInputs = computed(() => {
  const def = selectedChainDefinition.value
  if (!def) return []
  const subs = def.substitutions || []
  // include all substitutions (form-scoped and per_row) so column name selectors are shown
  return subs.map(s => ({ name: s.name, label: s.label, default: s.default, helpText: s.help_text, scope: s.scope }))
})

// Expose step parameter exposures that are visible and resolved at form time
const selectedChainExposures = computed(() => {
  const def = selectedChainDefinition.value
  if (!def) return []
  const exposures = def.step_param_exposure || []
  return exposures
    .filter(e => e.visible === true && (e.resolve_timing === 'form' || !e.resolve_timing))
    .map(e => {
      const stepId = e.step_id || 'step'
      const param = e.param || e.param_name || 'param'
      const name = `${stepId}.${param.replace(/\./g, '_')}`
      return { 
        name, 
        label: e.label || `${stepId} ${param}`, 
        default: e.default, 
        helpText: e.help_text, 
        stepId, 
        param,
        use_registry_source: e.use_registry_source,
        register_id: e.register_id
      }
    })
})

const selectedChainFormInputs = computed(() => {
  const inputs = []
  
  // Add all substitutions
  selectedChainUserInputs.value.forEach(s => {
    inputs.push({ ...s, isSubstitution: true })
  })
  
  // Add visible exposures
  selectedChainExposures.value.forEach(e => {
    inputs.push({ ...e, isExposure: true })
  })
  
  return inputs
})

// Generate unique ID for stages
function generateId() {
  return `stage_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// Get icon for stage type or name
function getStageIcon(stageOrName) {
  const type = typeof stageOrName === 'object' ? stageOrName.type : undefined
  if (type) {
    // Flatten basic stages
    const basicStages = stageLibrary.value.basic
    const matchByType = basicStages.find(s => s.type === type)
    if (matchByType) return matchByType.icon
  }

  const name = typeof stageOrName === 'object' ? stageOrName.name : stageOrName
  // Flatten custom stages from all categories
  const basicStages = stageLibrary.value.basic
  const customStages = Object.values(stageLibrary.value.custom).flat()
  const allStages = [...basicStages, ...customStages]
  const matchByName = allStages.find(s => s.name === name)
  return matchByName ? matchByName.icon : 'mdi-cube-outline'
}

// Add a new stage to the pipeline
function addStage(stageDefinition) {
  const definition = (stageDefinition && typeof stageDefinition === 'object')
    ? stageDefinition
    : (() => {
        const basicStages = stageLibrary.value.basic
        const customStages = Object.values(stageLibrary.value.custom).flat()
        const allStages = [...basicStages, ...customStages]
        return allStages.find(s => s.name === stageDefinition)
      })()

  if (!definition) return

  // If this is a composite command chain, expand to concrete steps
  if (definition.isChain) {
    createChainStage(definition)
    return
  }

  const stageName = definition.name || 'Custom Stage'
  createStage(definition.type, stageName)
}

function createChainStage(definition) {
  const id = generateId()
  const chainDef = getChainDefinition(definition.chainKey)
  const defaults = {}

  // Initialize substitutions
  const subs = (chainDef?.substitutions || [])
  subs.forEach(s => { defaults[s.name] = s.default ?? '' })
  
  // Initialize visible exposures (these are direct form inputs)
  const exposures = chainDef?.step_param_exposure || []
  exposures.filter(e => e.visible === true).forEach(e => {
    const stepId = e.step_id
    const param = e.param || e.param_name || 'param'
    const key = `${stepId}.${param.replace(/\./g, '_')}`
    defaults[key] = e.default ?? ''
  })

  const stageName = definition.name || 'Command Chain'

  stages.value.push({
    id,
    name: stageName,
    type: 'command_chain',
    config: {
      name: stageName,
      enabled: true,
      command_chain_type: definition.chainKey,
      chain_command_name: stageName,
      chainKey: definition.chainKey,
        userInputs: defaults,
    },
  })
  selectedStageId.value = id
}

function createStage(stepType, stageName, paramOverrides = {}) {
  const id = generateId()
  const defaults = buildDefaultsFromConfig(stepType)
  const config = {
    name: stageName,
    enabled: true,
    ...defaults,
    ...paramOverrides,
  }

  stages.value.push({
    id,
    name: stageName,
    type: stepType,
    config,
  })
  selectedStageId.value = id
}

// Build initial config values using defaults from step type schema
function buildDefaultsFromConfig(stepType) {
  const typeConfig = getStepTypeConfig(stepType)
  if (!typeConfig || !typeConfig.params) return {}

  const config = {}
  for (const [key, param] of Object.entries(typeConfig.params)) {
    if (param.type === 'object') {
      config[key] = buildObjectDefaults(param)
    } else if (Object.prototype.hasOwnProperty.call(param, 'default')) {
      config[key] = param.default
    }
  }
  return config
}

function buildObjectDefaults(paramConfig) {
  const nested = {}
  for (const [subKey, subParam] of Object.entries(paramConfig)) {
    if (!subParam || typeof subParam !== 'object' || !subParam.type) continue
    if (subParam.type === 'object') {
      nested[subKey] = buildObjectDefaults(subParam)
    } else if (Object.prototype.hasOwnProperty.call(subParam, 'default')) {
      nested[subKey] = subParam.default
    }
  }
  return nested
}

function isChainStage(stage) {
  return stage?.type === 'command_chain'
}

function getChainDefinition(chainKey) {
  const chains = STEP_TYPES_CONFIG.command_chains || {}
  return chains[chainKey]
}

/**
 * Replace placeholder tokens in params using provided values.
 * Only replace {string}, but in {{string}} the inner {string} should be replaced, leaving the outer one intact.
 */
function resolvePlaceholders(value, replacements) {
  if (Array.isArray(value)) return value.map(v => resolvePlaceholders(v, replacements))
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, resolvePlaceholders(v, replacements)]))
  }
  if (typeof value === 'string') {
    // Replace only single braces, not double braces
    // For {{key}}, replace the inner {key} but keep the outer braces
    // e.g. "{{foo}}" with {foo: "bar"} => "{bar}"
    // e.g. "abc {foo} xyz" => "abc bar xyz"
    // e.g. "{{foo}}" with no foo => "{foo}"
    return value.replace(/{{([^{}]+)}}|{([^{}]+)}/g, (match, doubleKey, singleKey) => {
      if (doubleKey !== undefined) {
        // It's {{key}}, so replace inner {key} and keep outer braces
        const inner = replacements[doubleKey] ?? doubleKey
        return `{${inner}}`
      }
      if (singleKey !== undefined) {
        // It's {key}, so replace as usual
        return replacements[singleKey] ?? `{${singleKey}}`
      }
      return match
    })
  }
  return value
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

// Helper: Get enum items for a field, considering registry sources
function getEnumItemsForField(paramConfig) {
  // If this field uses a registry source, build items from registered values
  if (paramConfig.use_registry_source) {
    const registryId = paramConfig.use_registry_source
    const registeredValues = getRegisteredValues(registryId)
    return registeredValues.map(value => ({
      value: value,
      label: value
    }))
  }
  
  // Otherwise use predefined enum values
  return paramConfig.enumValues || []
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
        key !== 'required_when' && key !== 'help_text' &&
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

// Dialog management for pipeline save
function showSaveDialog() {
  const project = projectsStore.selectedProject
  if (!project) {
    alert('Please select a project first')
    return
  }
  
  pipelineName.value = ''
  saveError.value = ''
  isSavingDialogLoading.value = true
  saveDialogOpen.value = true

  // Load existing pipelines for the save dialog
  listPipelines(project.id)
    .then(result => {
      savedPipelinesForSave.value = result.pipelines || []
    })
    .catch(err => {
      console.error('Error listing pipelines:', err)
      savedPipelinesForSave.value = []
    })
    .finally(() => {
      isSavingDialogLoading.value = false
    })
}

function selectExistingPipeline(pipelineNameToSelect) {
  pipelineName.value = pipelineNameToSelect
}

async function confirmSavePipeline() {
  saveError.value = ''
  
  if (!pipelineName.value.trim()) {
    saveError.value = 'Please enter a pipeline name'
    return
  }

  const project = projectsStore.selectedProject
  if (!project) {
    saveError.value = 'No project selected'
    return
  }

  isSaving.value = true
  try {
    // Check if a pipeline with this name already exists
    const result = await listPipelines(project.id)
    const existingPipeline = result.pipelines?.find(p => p.name === pipelineName.value.trim())
    
    if (existingPipeline) {
      // Ask user if they want to overwrite
      existingPipelineId.value = existingPipeline.id
      overwriteDialogOpen.value = true
      isSaving.value = false
      return
    }

    // No existing pipeline, proceed with save
    await performSavePipeline(false)
  } catch (err) {
    console.error('Error checking for existing pipeline:', err)
    saveError.value = err.message || 'Failed to check existing pipelines'
    isSaving.value = false
  }
}

async function performSavePipeline(isOverwrite = false) {
  isSaving.value = true
  try {
    const manifest = buildManifestFromStages()
    const project = projectsStore.selectedProject
    
    let result
    if (isOverwrite && existingPipelineId.value) {
      // Update existing pipeline
      result = await updatePipeline(project.id, existingPipelineId.value, manifest)
    } else {
      // Save as new pipeline
      result = await savePipeline(project.id, pipelineName.value.trim(), manifest)
    }
    
    console.log('Pipeline saved:', result)
    saveDialogOpen.value = false
    overwriteDialogOpen.value = false
    
    // Show success message
    alert(`Pipeline "${pipelineName.value}" ${isOverwrite ? 'updated' : 'saved'} successfully!`)
  } catch (err) {
    console.error('Error saving pipeline:', err)
    saveError.value = err.message || 'Failed to save pipeline'
  } finally {
    isSaving.value = false
  }
}

async function showLoadDialog() {
  const project = projectsStore.selectedProject
  if (!project) {
    alert('Please select a project first')
    return
  }

  loadError.value = ''
  isLoadingPipelines.value = true
  loadDialogOpen.value = true

  try {
    const result = await listPipelines(project.id)
    savedPipelines.value = result.pipelines || []
  } catch (err) {
    console.error('Error listing pipelines:', err)
    loadError.value = err.message || 'Failed to load pipelines'
  } finally {
    isLoadingPipelines.value = false
  }
}

async function loadSelectedPipeline(pipelineId) {
  const project = projectsStore.selectedProject
  if (!project) {
    loadError.value = 'No project selected'
    return
  }

  try {
    const result = await loadPipeline(project.id, pipelineId)
    const manifest = result.manifest

    // Clear current stages and registry
    stages.value = []
    selectedStageId.value = null
    clearRegistry()

    // Convert manifest to YAML and set it, then apply to stages
    yamlText.value = yaml.dump(manifest)
    
    // Reset sync flags and apply YAML to stages
    isSyncingFromYaml.value = true
    applyYamlToStages({ preserveSelection: false })
    isSyncingFromYaml.value = false

    loadDialogOpen.value = false
    alert('Pipeline loaded successfully!')
  } catch (err) {
    console.error('Error loading pipeline:', err)
    loadError.value = err.message || 'Failed to load pipeline'
  }
}

function buildManifestFromStages() {
  const jobSteps = []

  stages.value.forEach((s) => {
    if (isChainStage(s)) {
      const chainDef = getChainDefinition(s.config.chainKey)
      if (!chainDef) return
      const inputs = s.config.userInputs || {}

      const exposures = chainDef.step_param_exposure || []

      const setNested = (obj, path, value) => {
        const parts = (path || '').split('.')
        let cur = obj
        for (let i = 0; i < parts.length; i++) {
          const p = parts[i]
          if (i === parts.length - 1) {
            cur[p] = value
          } else {
            if (!cur[p]) cur[p] = {}
            cur = cur[p]
          }
        }
      }

      ;(chainDef.chain || []).forEach((stepEntry, idx) => {
        const stepType = stepEntry.type
        const displayName = getStepTypeConfig(stepType)?.display_name || stepEntry.display_name || stepEntry.type || `Step ${idx + 1}`

        // Collect exposures for this step instance by step id
        const stepId = stepEntry.id || stepEntry.step_id || `step${idx}`
        const stepExposures = (exposures || []).filter(e => (e.step_id === stepId))

        // Build params from exposures
        const paramsObj = {}
        stepExposures.forEach(exp => {
          const paramPath = exp.param || exp.param_name || ''
          const expStepId = exp.step_id || exp.stepId
          const expKey = `${expStepId}.${paramPath.replace(/\./g, '_')}`
          
          let value
          if (exp.visible === true) {
            // For visible exposures, use the user-provided value directly
            value = inputs[expKey] ?? exp.default
          } else {
            // For hidden exposures, use default with substitutions applied
            value = resolvePlaceholders(exp.default, inputs)
          }
          
          if (paramPath) setNested(paramsObj, paramPath, value)
        })

        jobSteps.push({
          step_name: displayName,
          type: stepType,
          command_chain_type: s.config.command_chain_type || s.config.chainKey,
          chain_command_name: s.config.chain_command_name || s.config.name,
          enabled: s.config.enabled !== false,
          params: paramsObj,
        })
      })

      return
    }

    const displayName = (s.config && s.config.name) || s.name || 'Unnamed step'
    const { enabled, name, ...params } = (s.config || {})
    jobSteps.push({
      step_name: displayName,
      type: s.type,
      command_chain_type: s.config?.command_chain_type,
      chain_command_name: s.config?.chain_command_name,
      enabled: enabled !== false,
      params: params,
    })
  })

  return {
    manifest_id: `id${new Date().toISOString().slice(0, 10)}`,
    created_by: authStore.userName || authStore.user?.name || 'unknown',
    created_at: new Date().toISOString(),
    simulated: true,
    job_steps: jobSteps,
  }
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

    // Group steps by command_chain_type/chain_command_name to detect composite chains
    const groupedSteps = []
    let currentGroup = null

    parsed.job_steps.forEach((step) => {
      const chainType = step.command_chain_type
      const chainName = step.chain_command_name

      if (chainType && chainName) {
        // This step is part of a chain
        if (!currentGroup || currentGroup.chainType !== chainType || currentGroup.chainName !== chainName) {
          // Start a new chain group
          if (currentGroup) {
            groupedSteps.push(currentGroup)
          }
          currentGroup = { chainType, chainName, steps: [step] }
        } else {
          // Add to current chain group
          currentGroup.steps.push(step)
        }
      } else {
        // Regular step, not part of a chain
        if (currentGroup) {
          groupedSteps.push(currentGroup)
          currentGroup = null
        }
        groupedSteps.push({ steps: [step] })
      }
    })
    if (currentGroup) {
      groupedSteps.push(currentGroup)
    }

    // Convert grouped steps into stages
    const newStages = groupedSteps.map((group) => {
      if (group.chainType) {
        // This is a composite chain stage
        const id = generateId()
        const chainKey = group.chainType
        const chainDef = getChainDefinition(chainKey)
        
        if (!chainDef) {
          console.warn(`Chain definition not found for chainKey: "${chainKey}". Available chains:`, Object.keys(STEP_TYPES_CONFIG.command_chains || {}))
        }

        // Extract substitution and visible exposure values from step params
        const userInputs = {}
        const exposures = chainDef?.step_param_exposure || []
        const substitutions = chainDef?.substitutions || []

        // Helper to get nested values from params
        const getNested = (obj, path) => {
          const parts = (path || '').split('.')
          let cur = obj
          for (const p of parts) {
            if (!cur || typeof cur !== 'object') return undefined
            cur = cur[p]
          }
          return cur
        }

        const escapeRegex = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

        const extractSubstitutionsFromTemplate = (template, actual) => {
          if (typeof template !== 'string' || typeof actual !== 'string') return {}

          const tokenRegex = /{{([^{}]+)}}|{([^{}]+)}/g
          let lastIndex = 0
          let match
          let pattern = '^'
          const keys = []

          while ((match = tokenRegex.exec(template)) !== null) {
            const [full, doubleKey, singleKey] = match
            const key = doubleKey || singleKey
            pattern += escapeRegex(template.slice(lastIndex, match.index))
            if (doubleKey) {
              // {{key}} resolves to {value}, keep braces in actual
              pattern += '\\{(?<k' + keys.length + '>.+?)\\}'
            } else {
              // {key} resolves to value
              pattern += '(?<k' + keys.length + '>.+?)'
            }
            keys.push(key)
            lastIndex = match.index + full.length
          }

          pattern += escapeRegex(template.slice(lastIndex)) + '$'

          try {
            const regex = new RegExp(pattern)
            const m = actual.match(regex)
            if (!m || !m.groups) return {}
            const extracted = {}
            keys.forEach((k, i) => {
              const value = m.groups[`k${i}`]
              if (value !== undefined) extracted[k] = value
            })
            return extracted
          } catch (err) {
            return {}
          }
        }

        // Extract values for visible exposures and try to reverse-engineer substitutions
        group.steps.forEach((step, stepIdx) => {
          const chainStep = (chainDef?.chain || [])[stepIdx]
          if (!chainStep) return
          
          const stepId = chainStep.id || chainStep.step_id || `step${stepIdx}`
          const stepExposures = exposures.filter(e => e.step_id === stepId)
          
          stepExposures.forEach(exp => {
            const paramPath = exp.param || exp.param_name || ''
            const actualValue = getNested(step.params || {}, paramPath)
            
            if (exp.visible === true) {
              // For visible exposures, store the actual value directly
              const expKey = `${stepId}.${paramPath.replace(/\./g, '_')}`
              if (actualValue !== undefined) {
                userInputs[expKey] = actualValue
              }
            } else {
              // For hidden exposures, try to extract substitution values
              const defaultTemplate = exp.default || ''
              if (typeof actualValue === 'string' && typeof defaultTemplate === 'string') {
                // Check if default is a simple placeholder like "{output_dir}"
                const simpleMatch = defaultTemplate.match(/^{([^}]+)}$/)
                if (simpleMatch) {
                  const substName = simpleMatch[1]
                  if (!userInputs.hasOwnProperty(substName)) {
                    userInputs[substName] = actualValue
                  }
                } else if (defaultTemplate.includes('{')) {
                  // More complex template with placeholders
                  const extracted = extractSubstitutionsFromTemplate(defaultTemplate, actualValue)
                  Object.entries(extracted).forEach(([k, v]) => {
                    if (!userInputs.hasOwnProperty(k)) {
                      userInputs[k] = v
                    }
                  })
                }
              }
            }
          })
        })

        // Initialize any missing substitutions with defaults
        substitutions.forEach(s => {
          if (!userInputs.hasOwnProperty(s.name)) {
            userInputs[s.name] = s.default ?? ''
          }
        })
        
        // Initialize any missing visible exposures with defaults
        exposures.filter(e => e.visible === true).forEach(e => {
          const stepId = e.step_id
          const param = e.param || e.param_name || ''
          const expKey = `${stepId}.${param.replace(/\./g, '_')}`
          if (!userInputs.hasOwnProperty(expKey)) {
            userInputs[expKey] = e.default ?? ''
          }
        })

        return {
          id,
          name: group.chainName,
          type: 'command_chain',
          config: {
            name: group.chainName,
            enabled: true,
            command_chain_type: chainKey,
            chain_command_name: group.chainName,
            chainKey,
            userInputs,
          },
        }
      } else {
        // Regular step
        const step = group.steps[0]
        const id = generateId()
        const stepName = step.step_name || step.name || 'Unnamed step'
        const allParams = step.params && typeof step.params === 'object' ? step.params : {}
        const { name: _ignoredName, ...params } = allParams
        return {
          id,
          name: stepName,
          type: step.type,
          config: {
            ...params,
            enabled: step.enabled !== false,
            name: stepName,
            description: params.description || '',
            notes: params.notes || '',
          },
        }
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
    // Always keep YAML in sync with canvas changes, unless we are currently syncing FROM YAML to avoid feedback loops
    if (isSyncingFromYaml.value) return
    resetYamlFromStages()
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

// Watch for changes to stages and update registry for fields with register_id
watch(
  stages,
  () => {
    // Rebuild registry from all current stages
    // This ensures registry stays in sync whenever stages change
    rebuildRegistryFromStages()
  },
  { deep: true, immediate: false }
)

// Helper: Rebuild the registry from all stages
function rebuildRegistryFromStages() {
  const newRegistry = {}
  
  stages.value.forEach((stage) => {
    if (isChainStage(stage)) {
      // For chain stages, check step parameter exposures
      const chainDef = getChainDefinition(stage.config.chainKey)
      if (chainDef && chainDef.step_param_exposure) {
        chainDef.step_param_exposure.forEach((exposure) => {
          if (exposure.register_id) {
            const registryId = exposure.register_id
            // For exposures, use the computed key format
            const stepId = exposure.step_id
            const param = exposure.param || exposure.param_name || ''
            const expKey = `${stepId}.${param.replace(/\./g, '_')}`
            const value = stage.config.userInputs?.[expKey]
            
            if (value) {
              if (!newRegistry[registryId]) {
                newRegistry[registryId] = []
              }
              if (!newRegistry[registryId].includes(value)) {
                newRegistry[registryId].push(value)
              }
            }
          }
        })
      }
    } else {
      // For regular stages, check params
      const typeConfig = getStepTypeConfig(stage.type)
      if (!typeConfig || !typeConfig.params) return
      
      // Check all parameters in this step's config for register_id
      Object.entries(typeConfig.params).forEach(([paramKey, paramConfig]) => {
        if (paramConfig.register_id) {
          const registryId = paramConfig.register_id
          const value = stage.config[paramKey]
          
          if (value) {
            if (!newRegistry[registryId]) {
              newRegistry[registryId] = []
            }
            if (!newRegistry[registryId].includes(value)) {
              newRegistry[registryId].push(value)
            }
          }
        }
      })
    }
  })
  
  fieldRegistry.value = newRegistry
}
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
