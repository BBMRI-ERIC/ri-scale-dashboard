<template>
  <v-layout class="dashboard-layout">
    <AppSidebar 
      v-model:rail="sidebarRail"
      @toggle-rail="sidebarRail = !sidebarRail"
    />

    <v-main class="main-content">
      <AppHeader />

      <div class="page-container">
        <div class="page-header">
          <div class="header-content">
            <h1 class="page-title">
              <v-icon class="title-icon">mdi-file-document-multiple</v-icon>
              DPS Pipelines
            </h1>
            <p class="page-subtitle">Manage your data processing pipeline manifests</p>
          </div>
          <div class="header-actions">
            <v-btn 
              color="primary"
              prepend-icon="mdi-plus"
              @click="createNewPipeline"
            >
              New Pipeline
            </v-btn>
          </div>
        </div>

        <!-- Project Filter -->
        <v-card class="filters-card glass mb-6" :elevation="0">
          <v-card-text>
            <v-row align="center">
              <v-col cols="12" md="4">
                <v-select
                  v-model="selectedProject"
                  :items="projectOptions"
                  item-title="label"
                  item-value="id"
                  label="Filter by Project"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  prepend-inner-icon="mdi-filter-variant"
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Pipelines table -->
        <section class="table-section mb-6">
          <v-card class="pipelines-table-card glass" :elevation="0">
            <v-data-table
              :headers="tableHeaders"
              :items="filteredPipelines"
              :loading="isLoading"
              class="pipelines-table"
              item-key="id"
              hover
              @click:row="(event, { item }) => openPipeline(item)"
            >
              <!-- Name column -->
              <template v-slot:item.name="{ item }">
                <div class="pipeline-name-cell">
                  <v-icon color="primary" size="18" class="mr-2">mdi-file-document</v-icon>
                  <span>{{ item.name }}</span>
                </div>
              </template>

              <!-- Project column -->
              <template v-slot:item.project="{ item }">
                <div class="project-cell">
                  <span class="project-name">{{ item.project_name || item.project_id }}</span>
                </div>
              </template>

              <!-- Actions column -->
              <template v-slot:item.actions="{ item }">
                <div class="actions-cell">
                  <v-btn
                    icon="mdi-pencil"
                    size="small"
                    variant="text"
                    color="primary"
                    @click.stop="openPipeline(item)"
                    title="Edit pipeline"
                  />
                  <v-btn
                    icon="mdi-delete"
                    size="small"
                    variant="text"
                    color="error"
                    @click.stop="deletePipeline(item)"
                    title="Delete pipeline"
                  />
                </div>
              </template>

              <!-- Empty state -->
              <template v-slot:no-data>
                <div class="empty-state">
                  <v-icon size="48" color="primary" class="mb-3">mdi-file-document-outline</v-icon>
                  <h3>No pipelines found</h3>
                  <p>{{ selectedProject === 'all' ? 'Create your first pipeline to get started' : 'No pipelines in this project yet' }}</p>
                  <v-btn
                    color="primary"
                    variant="tonal"
                    class="mt-3"
                    prepend-icon="mdi-plus"
                    @click="createNewPipeline"
                  >
                    Create New Pipeline
                  </v-btn>
                </div>
              </template>

              <!-- Loading state -->
              <template v-slot:loading>
                <div class="loading-state">
                  <v-progress-circular indeterminate color="primary" size="48" />
                  <p class="mt-3">Loading pipelines...</p>
                </div>
              </template>
            </v-data-table>
          </v-card>
        </section>

        <!-- Recent Runs -->
        <section class="table-section mt-6">
          <div class="section-label mb-3">
            <v-icon size="18" class="mr-2">mdi-play-circle-outline</v-icon>
            Recent Runs
            <v-btn icon size="x-small" variant="text" class="ml-2" @click="loadRuns" :loading="runsLoading" title="Refresh runs">
              <v-icon size="16">mdi-refresh</v-icon>
            </v-btn>
          </div>
          <v-card class="pipelines-table-card glass" :elevation="0">
            <v-data-table
              :headers="runsHeaders"
              :items="filteredRuns"
              :loading="runsLoading"
              class="pipelines-table"
              item-key="run_id"
              density="compact"
            >
              <template v-slot:item.pipeline_name="{ item }">
                <span class="pipeline-name-cell">{{ item.pipeline_name || '—' }}</span>
              </template>
              <template v-slot:item.status="{ item }">
                <v-chip :color="runStatusColor(item.status)" size="x-small" variant="tonal">{{ item.status }}</v-chip>
              </template>
              <template v-slot:item.simulated="{ item }">
                <v-chip size="x-small" variant="outlined" :color="item.simulated ? 'warning' : 'primary'">
                  {{ item.simulated ? 'Simulated' : 'Production' }}
                </v-chip>
              </template>
              <template v-slot:item.created_at="{ item }">
                <span class="text-caption">{{ formatDate(item.created_at) }}</span>
              </template>
              <template v-slot:item.runtime="{ item }">
                <span class="text-caption">{{ item.runtime || '—' }}</span>
              </template>
              <template v-slot:item.actions="{ item }">
                <div class="actions-cell">
                  <v-btn
                    icon="mdi-text-box-outline"
                    size="small"
                    variant="text"
                    color="primary"
                    @click.stop="viewRunLogs(item)"
                    title="View logs"
                  />
                  <v-btn
                    v-if="['starting','running','cancelling'].includes(item.status)"
                    icon="mdi-stop"
                    size="small"
                    variant="text"
                    color="error"
                    :loading="item.status === 'cancelling'"
                    @click.stop="stopRun(item.run_id)"
                    title="Stop run"
                  />
                </div>
              </template>
              <template v-slot:no-data>
                <div class="empty-state" style="padding: 2rem">
                  <p>No runs yet. Use the Pipeline Builder to run a pipeline.</p>
                </div>
              </template>
            </v-data-table>
          </v-card>
        </section>

        <!-- Log viewer dialog -->
        <v-dialog v-model="logDialogOpen" max-width="900px">
          <v-card>
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-console</v-icon>
              {{ selectedRun?.pipeline_name || 'Run' }}
              <v-chip :color="runStatusColor(selectedRun?.status)" size="x-small" variant="tonal" class="ml-2">
                {{ selectedRun?.status }}
              </v-chip>
              <v-spacer />
              <v-btn
                v-if="['starting','running','cancelling'].includes(selectedRun?.status)"
                size="small"
                variant="tonal"
                color="error"
                :loading="selectedRun?.status === 'cancelling'"
                @click="stopRun(selectedRun.run_id)"
              >Stop</v-btn>
            </v-card-title>
            <v-divider />
            <v-card-text style="padding: 0">
              <div class="log-output-dialog" ref="logDialogEl">
                <pre class="log-text-dialog">{{ selectedRunLogs || '(no output yet)' }}</pre>
              </div>
            </v-card-text>
            <v-divider />
            <v-card-actions>
              <v-spacer />
              <v-btn variant="plain" @click="logDialogOpen = false">Close</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </div>
    </v-main>
  </v-layout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import { listPipelines, deletePipeline as deletePipelineAPI, listRuns, getRun, cancelRun } from '@/services/pipelines'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const router = useRouter()
const projectsStore = useProjectsStore()

const sidebarRail = ref(false)
const selectedProject = ref('all')
const pipelines = ref([])
const isLoading = ref(false)
const error = ref(null)

// Runs state
const runs = ref([])
const runsLoading = ref(false)
const logDialogOpen = ref(false)
const selectedRun = ref(null)
const selectedRunLogs = ref('')
const logDialogEl = ref(null)
let runsRefreshTimer = null

const runsHeaders = [
  { title: 'Pipeline', key: 'pipeline_name' },
  { title: 'Status', key: 'status' },
  { title: 'Mode', key: 'simulated' },
  { title: 'Started', key: 'created_at' },
  { title: 'Runtime', key: 'runtime' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center', width: '100px' },
]

const filteredRuns = computed(() => {
  if (selectedProject.value === 'all') return runs.value
  return runs.value.filter(r => r.project_id === selectedProject.value)
})

const runStatusColor = (status) => {
  const map = { running: 'primary', completed: 'success', failed: 'error', cancelled: 'warning', cancelling: 'warning', starting: 'grey' }
  return map[status] || 'grey'
}

async function loadRuns() {
  runsLoading.value = true
  try {
    const projectId = selectedProject.value !== 'all' ? selectedProject.value : null
    const result = await listRuns(projectId)
    runs.value = result.runs || []
  } catch (err) {
    console.warn('Failed to load runs:', err)
  } finally {
    runsLoading.value = false
  }
}

async function viewRunLogs(run) {
  selectedRun.value = run
  selectedRunLogs.value = ''
  logDialogOpen.value = true
  try {
    const result = await getRun(run.run_id)
    selectedRun.value = result.run
    selectedRunLogs.value = result.run.logs || ''
    nextTick(() => {
      if (logDialogEl.value) logDialogEl.value.scrollTop = logDialogEl.value.scrollHeight
    })
  } catch (err) {
    selectedRunLogs.value = `Failed to load logs: ${err.message}`
  }
}

async function stopRun(runId) {
  try {
    await cancelRun(runId)
    await loadRuns()
    if (selectedRun.value?.run_id === runId) {
      selectedRun.value = { ...selectedRun.value, status: 'cancelling' }
    }
  } catch (err) {
    console.error('Failed to stop run:', err)
  }
}

function startRunsRefresh() {
  runsRefreshTimer = setInterval(async () => {
    const hasActive = runs.value.some(r => ['starting', 'running', 'cancelling'].includes(r.status))
    if (hasActive) {
      await loadRuns()
      // Refresh open dialog logs too
      if (logDialogOpen.value && selectedRun.value) {
        const active = ['starting', 'running', 'cancelling'].includes(selectedRun.value.status)
        if (active) {
          try {
            const result = await getRun(selectedRun.value.run_id)
            selectedRun.value = result.run
            selectedRunLogs.value = result.run.logs || ''
            nextTick(() => {
              if (logDialogEl.value) logDialogEl.value.scrollTop = logDialogEl.value.scrollHeight
            })
          } catch { /* ignore */ }
        }
      }
    }
  }, 2000)
}

// Table headers
const tableHeaders = [
  { title: 'Name', key: 'name' },
  { title: 'Project', key: 'project' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center', width: '120px' }
]

// Project options for filter
const projectOptions = computed(() => {
  const options = [{ id: 'all', label: 'All Projects' }]
  
  if (projectsStore.activeProjects && projectsStore.activeProjects.length > 0) {
    projectsStore.activeProjects.forEach(project => {
      options.push({
        id: project.id,
        label: project.shortTitle || project.id
      })
    })
  }
  
  return options
})

// Filtered pipelines based on selected project
const filteredPipelines = computed(() => {
  if (selectedProject.value === 'all') {
    return pipelines.value
  }
  return pipelines.value.filter(p => p.project_id === selectedProject.value)
})

// Load pipelines for all projects or selected project
async function loadPipelines() {
  isLoading.value = true
  error.value = null
  pipelines.value = []

  try {
    // If a specific project is selected, load only that project's pipelines
    if (selectedProject.value !== 'all') {
      const response = await listPipelines(selectedProject.value)
      if (response.pipelines && response.pipelines.length > 0) {
        pipelines.value = response.pipelines.map(p => ({
          ...p,
          project_id: selectedProject.value
        }))
      }
    } else {
      // Load pipelines from all projects
      const projects = projectsStore.activeProjects || []
      
      if (projects.length === 0) {
        // Try to use current selected project if no projects loaded
        if (projectsStore.selectedProjectId) {
          const response = await listPipelines(projectsStore.selectedProjectId)
          if (response.pipelines && response.pipelines.length > 0) {
            pipelines.value = response.pipelines.map(p => ({
              ...p,
              project_id: projectsStore.selectedProjectId
            }))
          }
        }
      } else {
        // Load from all projects
        const allPipelines = []
        for (const project of projects) {
          try {
            const response = await listPipelines(project.id)
            if (response.pipelines && response.pipelines.length > 0) {
              const projectPipelines = response.pipelines.map(p => ({
                ...p,
                project_id: project.id,
                project_name: project.shortTitle || project.id
              }))
              allPipelines.push(...projectPipelines)
            }
          } catch (err) {
            console.warn(`Failed to load pipelines for project ${project.id}:`, err)
          }
        }
        pipelines.value = allPipelines
      }
    }
  } catch (err) {
    console.error('Failed to load pipelines:', err)
    error.value = err.message || 'Failed to load pipelines'
  } finally {
    isLoading.value = false
  }
}

// Format date for display
function formatDate(dateString) {
  if (!dateString) return 'Unknown'
  try {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}
// Delete pipeline
async function deletePipeline(pipeline) {
  if (!pipeline || !pipeline.id || !pipeline.project_id) {
    console.error('Invalid pipeline object:', pipeline)
    alert('Invalid pipeline - missing required fields')
    return
  }

  if (confirm(`Are you sure you want to delete "${pipeline.name}"?`)) {
    try {
      // Store the original pipelines array in case we need to restore
      const originalPipelines = [...pipelines.value]
      
      // Optimistically remove from UI
      pipelines.value = pipelines.value.filter(p => p.id !== pipeline.id)
      
      // Call the API
      console.log('Deleting pipeline:', { projectId: pipeline.project_id, pipelineId: pipeline.id })
      await deletePipelineAPI(pipeline.project_id, pipeline.id)
      
      console.log('Pipeline deleted successfully:', pipeline.id)
    } catch (err) {
      console.error('Failed to delete pipeline:', err)
      // Restore the original list on error
      pipelines.value = originalPipelines
      alert(`Failed to delete pipeline: ${err.message}`)
    }
  }
}
// Create new pipeline
function createNewPipeline() {
  router.push('/pipelines/new')
}

// Open existing pipeline
function openPipeline(pipeline) {
  router.push({
    name: 'pipeline-builder',
    query: {
      project: pipeline.project_id,
      pipeline: pipeline.id
    }
  })
}

// Watch for project changes and reload
import { watch } from 'vue'
watch(selectedProject, () => {
  loadPipelines()
  loadRuns()
})

// When the store finishes loading projects (async, 500ms delay), sync the local filter
watch(() => projectsStore.selectedProjectId, (newId) => {
  if (newId && selectedProject.value === 'all') {
    selectedProject.value = newId
  }
})

onMounted(() => {
  if (projectsStore.selectedProjectId) {
    selectedProject.value = projectsStore.selectedProjectId
  }
  loadPipelines()
  loadRuns()
  startRunsRefresh()
})

onUnmounted(() => {
  if (runsRefreshTimer) clearInterval(runsRefreshTimer)
})
</script>

<style scoped lang="scss">
// Filters
.filters-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
}

// Table
.pipelines-table-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
  overflow: hidden;
}

.pipelines-table {
  background: transparent !important;
  
  :deep(.v-data-table__thead) {
    background: rgba(30, 41, 59, 0.5);
    
    th {
      color: #94a3b8 !important;
      font-weight: 600;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
  }
  
  :deep(.v-data-table__tr) {
    cursor: pointer;
    
    &:hover {
      background: rgba(230, 152, 48, 0.08) !important;
    }
  }
}

.pipeline-id {
  color: #64748b;
  font-size: 0.8125rem;
}

.pipeline-name-cell {
  display: flex;
  align-items: center;
  font-size: 0.9375rem;
  font-weight: 500;
  color: #f1f5f9;
}

.project-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.project-name {
  font-size: 0.875rem;
  color: #e2e8f0;
}

.steps-chip {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
}

.actions-cell {
  display: flex;
  gap: 0.25rem;
  justify-content: center;
}

// Loading state
.loading-state {
  text-align: center;
  padding: 4rem 2rem;
  
  p {
    color: #94a3b8;
    font-size: 0.875rem;
  }
}

// Empty state
.empty-state {
  text-align: center;
  padding: 4rem 2rem;

  h3 {
    font-size: 1.125rem;
    color: #f1f5f9;
    margin: 0;
  }

  p {
    color: #64748b;
    margin: 0.5rem 0 0;
  }
}

.section-label {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.log-output-dialog {
  height: 400px;
  overflow-y: auto;
  background: #0d1117;
  padding: 16px;
}

.log-text-dialog {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 12px;
  line-height: 1.5;
  color: #94a3b8;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}
</style>
