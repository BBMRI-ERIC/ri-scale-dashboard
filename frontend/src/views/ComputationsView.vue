<template>
  <v-layout class="dashboard-layout">
    <AppSidebar v-model:rail="sidebarRail" @toggle-rail="sidebarRail = !sidebarRail" />

    <v-main class="main-content">
      <AppHeader />

      <div class="page-container">
        <!-- Page Header -->
        <div class="page-header">
          <div class="header-content">
            <h1 class="page-title">
              <v-icon class="title-icon">mdi-chip</v-icon>
              HPC Jobs
              <v-chip 
                v-if="projectsStore.selectedProject" 
                size="small" 
                variant="tonal"
                color="primary"
                class="ml-3"
              >
                {{ projectsStore.selectedProject.shortTitle }}
              </v-chip>
            </h1>
            <p class="page-subtitle">
              Monitor and manage jobs running on HPC sites
            </p>
          </div>
          <div class="header-actions">
            <v-btn 
              variant="outlined" 
              prepend-icon="mdi-refresh"
              @click="refreshJobs"
              :loading="isRefreshing"
            >
              Refresh
            </v-btn>
            <v-btn 
              color="primary" 
              prepend-icon="mdi-play"
              @click="showNewJobDialog = true"
            >
              New Job
            </v-btn>
          </div>
        </div>

        <!-- Stats cards -->
        <section class="stats-section mb-6">
          <v-row>
            <v-col cols="6" sm="3" v-for="stat in jobStats" :key="stat.label">
              <div class="stat-card glass">
                <div class="stat-icon" :class="stat.status">
                  <v-icon :icon="stat.icon" size="20" />
                </div>
                <div class="stat-info">
                  <span class="stat-value font-mono">{{ stat.value }}</span>
                  <span class="stat-label">{{ stat.label }}</span>
                </div>
              </div>
            </v-col>
          </v-row>
        </section>

        <!-- Filters -->
        <section class="filters-section slide-up delay-3">
          <div class="filters-row">
            <v-text-field
              v-model="searchQuery"
              placeholder="Search jobs..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              hide-details
              class="search-field"
              clearable
            />
            <v-select
              v-model="statusFilter"
              :items="statusOptions"
              label="Status"
              variant="outlined"
              density="compact"
              hide-details
              class="filter-select"
              clearable
            />
            <v-select
              v-model="hpcFilter"
              :items="hpcSites"
              label="HPC Site"
              variant="outlined"
              density="compact"
              hide-details
              class="filter-select"
              clearable
            />
          </div>
        </section>

        <!-- Jobs table -->
        <section class="table-section slide-up delay-4">
          <v-card class="jobs-table-card glass" :elevation="0">
            <v-data-table
              :headers="tableHeaders"
              :items="filteredJobs"
              :loading="isLoading"
              class="jobs-table"
              item-key="id"
              hover
            >
              <!-- ID column -->
              <template v-slot:item.id="{ item }">
                <span class="job-id font-mono">{{ item.id.slice(0, 8) }}...</span>
              </template>

              <!-- Project column -->
              <template v-slot:item.project="{ item }">
                <div class="project-cell">
                  <div class="project-badge" :class="item.useCase?.toLowerCase()">
                    {{ item.useCase }}
                  </div>
                  <span class="project-name">{{ item.projectName }}</span>
                </div>
              </template>

              <!-- Job Type column -->
              <template v-slot:item.jobType="{ item }">
                <div class="job-type-cell">
                  <v-icon size="16" class="job-type-icon">{{ getJobTypeIcon(item.jobType) }}</v-icon>
                  <span>{{ item.jobType }}</span>
                </div>
              </template>

              <!-- HPC Site column -->
              <template v-slot:item.hpcSite="{ item }">
                <v-chip size="small" variant="outlined" class="hpc-chip">
                  <v-icon start size="14">mdi-server</v-icon>
                  {{ item.hpcSite }}
                </v-chip>
              </template>

              <!-- Resources column -->
              <template v-slot:item.resources="{ item }">
                <div class="resources-cell">
                  <span class="resource-item" title="Nodes">
                    <v-icon size="14">mdi-server</v-icon>
                    {{ item.nodes }}
                  </span>
                  <span class="resource-item" title="GPUs">
                    <v-icon size="14">mdi-expansion-card</v-icon>
                    {{ item.gpus }}
                  </span>
                  <span class="resource-item" title="Memory">
                    <v-icon size="14">mdi-memory</v-icon>
                    {{ item.memory }}
                  </span>
                </div>
              </template>

              <!-- Runtime column -->
              <template v-slot:item.runtime="{ item }">
                <span class="font-mono">{{ item.runtime || '—' }}</span>
              </template>

              <!-- Status column -->
              <template v-slot:item.status="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  size="small"
                  variant="tonal"
                  class="status-chip"
                >
                  <v-icon start size="12">{{ getStatusIcon(item.status) }}</v-icon>
                  {{ item.status }}
                </v-chip>
              </template>

              <!-- Actions column -->
              <template v-slot:item.actions="{ item }">
                <div class="actions-cell">
                  <v-btn
                    icon="mdi-eye"
                    size="small"
                    variant="text"
                    @click="viewJob(item)"
                  />
                  <v-btn
                    v-if="item.status === 'running'"
                    icon="mdi-stop"
                    size="small"
                    variant="text"
                    color="warning"
                    @click="stopJob(item)"
                  />
                  <v-btn
                    v-if="item.status === 'queued'"
                    icon="mdi-close"
                    size="small"
                    variant="text"
                    color="error"
                    @click="cancelJob(item)"
                  />
                  <v-btn
                    v-if="item.status === 'failed'"
                    icon="mdi-refresh"
                    size="small"
                    variant="text"
                    color="warning"
                    @click="retryJob(item)"
                  />
                  <v-btn
                    v-if="item.status === 'completed'"
                    icon="mdi-download"
                    size="small"
                    variant="text"
                    color="primary"
                    @click="downloadResults(item)"
                  />
                </div>
              </template>

              <!-- Empty state -->
              <template v-slot:no-data>
                <div class="empty-state">
                  <v-icon size="48" color="primary" class="mb-3">mdi-chip</v-icon>
                  <h3>No computation jobs found</h3>
                  <p>Submit a new job to see it here.</p>
                </div>
              </template>
            </v-data-table>
          </v-card>
        </section>
      </div>
    </v-main>

    <!-- New Job Dialog -->
    <v-dialog v-model="showNewJobDialog" max-width="600">
      <v-card class="new-job-dialog glass">
        <div class="dialog-header">
          <h2>Submit New Job</h2>
          <v-btn icon="mdi-close" variant="text" size="small" @click="showNewJobDialog = false" />
        </div>
        <v-divider />
        <v-card-text class="dialog-content">
          <v-form ref="jobFormRef">
            <v-select
              v-model="newJob.projectId"
              :items="projectsStore.activeProjects"
              item-title="shortTitle"
              item-value="id"
              label="Project"
              :rules="[v => !!v || 'Project is required']"
              class="mb-4"
            />
            <v-select
              v-model="newJob.jobType"
              :items="jobTypes"
              label="Job Type"
              :rules="[v => !!v || 'Job type is required']"
              class="mb-4"
            />
            <v-select
              v-model="newJob.modelId"
              :items="availableModels"
              item-title="name"
              item-value="id"
              label="Model"
              :rules="[v => !!v || 'Model is required']"
              class="mb-4"
            />
            <v-select
              v-model="newJob.datasetId"
              :items="availableDatasets"
              item-title="name"
              item-value="id"
              label="Dataset"
              :rules="[v => !!v || 'Dataset is required']"
              class="mb-4"
            />
            <v-select
              v-model="newJob.hpcSite"
              :items="hpcSites"
              label="HPC Site"
              :rules="[v => !!v || 'HPC site is required']"
              class="mb-4"
            />
            
            <h4 class="resource-title">Resources</h4>
            <v-row>
              <v-col cols="4">
                <v-select
                  v-model="newJob.nodes"
                  :items="[1, 2, 4, 8, 16]"
                  label="Nodes"
                  :rules="[v => !!v || 'Required']"
                />
              </v-col>
              <v-col cols="4">
                <v-select
                  v-model="newJob.gpus"
                  :items="[1, 2, 4, 8]"
                  label="GPUs/Node"
                  :rules="[v => !!v || 'Required']"
                />
              </v-col>
              <v-col cols="4">
                <v-select
                  v-model="newJob.memory"
                  :items="['32 GB', '64 GB', '128 GB', '256 GB', '512 GB']"
                  label="Memory"
                  :rules="[v => !!v || 'Required']"
                />
              </v-col>
            </v-row>

            <v-textarea
              v-model="newJob.notes"
              label="Notes (optional)"
              rows="2"
            />
          </v-form>
        </v-card-text>
        <v-divider />
        <div class="dialog-footer">
          <v-btn variant="text" @click="showNewJobDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="submitJob" :loading="isSubmitting">
            Submit Job
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- Job Details Dialog -->
    <v-dialog v-model="showDetailsDialog" max-width="700">
      <v-card class="details-dialog glass" v-if="selectedJob">
        <div class="dialog-header">
          <h2>Job Details</h2>
          <v-btn icon="mdi-close" variant="text" size="small" @click="showDetailsDialog = false" />
        </div>
        <v-divider />
        <v-card-text class="dialog-content">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">Job ID</span>
              <span class="detail-value font-mono">{{ selectedJob.id }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Status</span>
              <v-chip :color="getStatusColor(selectedJob.status)" size="small" variant="tonal">
                {{ selectedJob.status }}
              </v-chip>
            </div>
            <div class="detail-item">
              <span class="detail-label">Project</span>
              <span class="detail-value">{{ selectedJob.projectName }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Job Type</span>
              <span class="detail-value">{{ selectedJob.jobType }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Model</span>
              <span class="detail-value">{{ selectedJob.modelName }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Dataset</span>
              <span class="detail-value">{{ selectedJob.datasetName }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">HPC Site</span>
              <span class="detail-value">{{ selectedJob.hpcSite }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Nodes</span>
              <span class="detail-value font-mono">{{ selectedJob.nodes }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">GPUs/Node</span>
              <span class="detail-value font-mono">{{ selectedJob.gpus }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Memory</span>
              <span class="detail-value font-mono">{{ selectedJob.memory }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Submitted</span>
              <span class="detail-value">{{ formatDate(selectedJob.submittedAt) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Started</span>
              <span class="detail-value">{{ selectedJob.startedAt ? formatDate(selectedJob.startedAt) : '—' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Runtime</span>
              <span class="detail-value font-mono">{{ selectedJob.runtime || '—' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Completed</span>
              <span class="detail-value">{{ selectedJob.completedAt ? formatDate(selectedJob.completedAt) : '—' }}</span>
            </div>
            <div class="detail-item full-width" v-if="selectedJob.error">
              <span class="detail-label">Error</span>
              <span class="detail-value error-text">{{ selectedJob.error }}</span>
            </div>
          </div>

          <!-- Running job progress -->
          <div class="progress-section" v-if="selectedJob.status === 'running'">
            <h4>Job Progress</h4>
            <div class="job-metrics">
              <div class="metric-card">
                <span class="metric-label">Epoch</span>
                <span class="metric-value font-mono">{{ selectedJob.currentEpoch }}/{{ selectedJob.totalEpochs }}</span>
              </div>
              <div class="metric-card">
                <span class="metric-label">GPU Utilization</span>
                <span class="metric-value font-mono">{{ selectedJob.gpuUtil }}%</span>
              </div>
              <div class="metric-card">
                <span class="metric-label">Memory Used</span>
                <span class="metric-value font-mono">{{ selectedJob.memoryUsed }}</span>
              </div>
            </div>
            <v-progress-linear
              :model-value="(selectedJob.currentEpoch / selectedJob.totalEpochs) * 100"
              color="primary"
              height="12"
              rounded
              striped
              class="mt-4"
            />
          </div>

          <!-- Completed job results -->
          <div class="results-section" v-if="selectedJob.status === 'completed' && selectedJob.results">
            <h4>Results</h4>
            <div class="results-grid">
              <div class="result-item" v-for="(value, key) in selectedJob.results" :key="key">
                <span class="result-label">{{ formatResultKey(key) }}</span>
                <span class="result-value font-mono">{{ value }}</span>
              </div>
            </div>
            <v-btn color="primary" variant="tonal" prepend-icon="mdi-download" class="mt-4">
              Download Full Results
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProjectsStore } from '@/stores/projects'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const projectsStore = useProjectsStore()

const sidebarRail = ref(false)
const isLoading = ref(false)
const isRefreshing = ref(false)
const isSubmitting = ref(false)
const searchQuery = ref('')
const statusFilter = ref(null)
const hpcFilter = ref(null)
const showNewJobDialog = ref(false)
const showDetailsDialog = ref(false)
const selectedJob = ref(null)
const jobFormRef = ref(null)

// New job form
const newJob = ref({
  projectId: null,
  jobType: null,
  modelId: null,
  datasetId: null,
  hpcSite: null,
  nodes: 1,
  gpus: 4,
  memory: '64 GB',
  notes: ''
})

// Mock data
const jobs = ref([
  {
    id: 'job-a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    projectId: 'proj-uc7-001',
    projectName: 'UC7 - CRC Prediction',
    useCase: 'UC7',
    jobType: 'Training',
    modelName: 'ResNet-WSI-v2',
    datasetName: 'Lymph Node WSI Collection A',
    hpcSite: 'MUSICA',
    nodes: 2,
    gpus: 4,
    memory: '128 GB',
    status: 'completed',
    submittedAt: '2024-12-14T08:00:00Z',
    startedAt: '2024-12-14T08:05:00Z',
    completedAt: '2024-12-15T02:30:00Z',
    runtime: '18h 25m',
    results: {
      accuracy: '94.2%',
      auc: '0.967',
      f1Score: '0.923',
      loss: '0.0234'
    }
  },
  {
    id: 'job-b2c3d4e5-f6a7-8901-bcde-f23456789012',
    projectId: 'proj-uc7-001',
    projectName: 'UC7 - CRC Prediction',
    useCase: 'UC7',
    jobType: 'Inference',
    modelName: 'ResNet-WSI-v2',
    datasetName: 'Lymph Node WSI Collection B',
    hpcSite: 'MUG-SX',
    nodes: 1,
    gpus: 2,
    memory: '64 GB',
    status: 'running',
    submittedAt: '2024-12-18T06:00:00Z',
    startedAt: '2024-12-18T06:12:00Z',
    completedAt: null,
    runtime: '5h 48m',
    currentEpoch: 156,
    totalEpochs: 250,
    gpuUtil: 94,
    memoryUsed: '58 GB'
  },
  {
    id: 'job-c3d4e5f6-a7b8-9012-cdef-345678901234',
    projectId: 'proj-uc8-001',
    projectName: 'UC8 - Synthetic Data',
    useCase: 'UC8',
    jobType: 'Generation',
    modelName: 'PathGAN-XL',
    datasetName: 'Training Set Alpha',
    hpcSite: 'MUSICA',
    nodes: 4,
    gpus: 8,
    memory: '256 GB',
    status: 'queued',
    submittedAt: '2024-12-18T10:30:00Z',
    startedAt: null,
    completedAt: null,
    runtime: null
  },
  {
    id: 'job-d4e5f6a7-b8c9-0123-defa-456789012345',
    projectId: 'proj-uc8-001',
    projectName: 'UC8 - Synthetic Data',
    useCase: 'UC8',
    jobType: 'Training',
    modelName: 'DiffuPath-v1',
    datasetName: 'Validation Set Beta',
    hpcSite: 'MUG-SX',
    nodes: 2,
    gpus: 4,
    memory: '128 GB',
    status: 'running',
    submittedAt: '2024-12-17T14:00:00Z',
    startedAt: '2024-12-17T14:30:00Z',
    completedAt: null,
    runtime: '21h 30m',
    currentEpoch: 89,
    totalEpochs: 100,
    gpuUtil: 87,
    memoryUsed: '112 GB'
  },
  {
    id: 'job-e5f6a7b8-c9d0-1234-efab-567890123456',
    projectId: 'proj-uc7-001',
    projectName: 'UC7 - CRC Prediction',
    useCase: 'UC7',
    jobType: 'Evaluation',
    modelName: 'XAI-Explainer',
    datasetName: 'Annotations Dataset',
    hpcSite: 'MUSICA',
    nodes: 1,
    gpus: 2,
    memory: '64 GB',
    status: 'failed',
    submittedAt: '2024-12-16T11:00:00Z',
    startedAt: '2024-12-16T11:15:00Z',
    completedAt: null,
    runtime: '2h 45m',
    error: 'CUDA out of memory. Tried to allocate 8.5 GB'
  }
])

const tableHeaders = [
  { title: 'ID', key: 'id', width: '120px' },
  { title: 'Project', key: 'project', width: '180px' },
  { title: 'Job Type', key: 'jobType', width: '120px' },
  { title: 'HPC Site', key: 'hpcSite', width: '120px' },
  { title: 'Resources', key: 'resources', width: '150px' },
  { title: 'Runtime', key: 'runtime', width: '100px' },
  { title: 'Status', key: 'status', width: '120px' },
  { title: 'Actions', key: 'actions', width: '140px', sortable: false }
]

const statusOptions = ['queued', 'running', 'completed', 'failed']
const hpcSites = ['MUSICA', 'MUG-SX']
const jobTypes = ['Training', 'Inference', 'Evaluation', 'Generation']

const availableModels = computed(() => [
  { id: 'model-001', name: 'ResNet-WSI-v2' },
  { id: 'model-002', name: 'PathGAN-XL' },
  { id: 'model-003', name: 'DiffuPath-v1' },
  { id: 'model-004', name: 'XAI-Explainer' },
  { id: 'model-005', name: 'ViT-Path-Large' },
])

const availableDatasets = computed(() => [
  { id: 'ds-001', name: 'Lymph Node WSI Collection A' },
  { id: 'ds-002', name: 'Lymph Node WSI Collection B' },
  { id: 'ds-003', name: 'Training Set Alpha' },
  { id: 'ds-004', name: 'Validation Set Beta' },
])

// Base jobs filtered by selected project
const projectFilteredJobs = computed(() => {
  if (projectsStore.selectedProjectId) {
    return jobs.value.filter(j => j.projectId === projectsStore.selectedProjectId)
  }
  return jobs.value
})

const jobStats = computed(() => [
  {
    label: 'Completed',
    value: projectFilteredJobs.value.filter(j => j.status === 'completed').length,
    icon: 'mdi-check-circle',
    status: 'completed'
  },
  {
    label: 'Running',
    value: projectFilteredJobs.value.filter(j => j.status === 'running').length,
    icon: 'mdi-play-circle',
    status: 'running'
  },
  {
    label: 'Queued',
    value: projectFilteredJobs.value.filter(j => j.status === 'queued').length,
    icon: 'mdi-clock-outline',
    status: 'queued'
  },
  {
    label: 'Failed',
    value: projectFilteredJobs.value.filter(j => j.status === 'failed').length,
    icon: 'mdi-alert-circle',
    status: 'failed'
  }
])

const filteredJobs = computed(() => {
  let result = jobs.value

  // Filter by selected project from sidebar
  if (projectsStore.selectedProjectId) {
    result = result.filter(j => j.projectId === projectsStore.selectedProjectId)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(j => 
      j.projectName.toLowerCase().includes(query) ||
      j.modelName.toLowerCase().includes(query) ||
      j.datasetName.toLowerCase().includes(query) ||
      j.jobType.toLowerCase().includes(query) ||
      j.id.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    result = result.filter(j => j.status === statusFilter.value)
  }

  if (hpcFilter.value) {
    result = result.filter(j => j.hpcSite === hpcFilter.value)
  }

  return result
})

function getStatusColor(status) {
  const colors = {
    completed: 'success',
    running: 'info',
    queued: 'warning',
    failed: 'error'
  }
  return colors[status] || 'default'
}

function getStatusIcon(status) {
  const icons = {
    completed: 'mdi-check-circle',
    running: 'mdi-play-circle',
    queued: 'mdi-clock-outline',
    failed: 'mdi-alert-circle'
  }
  return icons[status] || 'mdi-circle'
}

function getJobTypeIcon(jobType) {
  const icons = {
    Training: 'mdi-school',
    Inference: 'mdi-brain',
    Evaluation: 'mdi-chart-box',
    Generation: 'mdi-creation'
  }
  return icons[jobType] || 'mdi-cog'
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString()
}

function formatResultKey(key) {
  return key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())
}

async function refreshJobs() {
  isRefreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  isRefreshing.value = false
}

function viewJob(job) {
  selectedJob.value = job
  showDetailsDialog.value = true
}

function stopJob(job) {
  job.status = 'failed'
  job.error = 'Job stopped by user'
}

function cancelJob(job) {
  const index = jobs.value.findIndex(j => j.id === job.id)
  if (index > -1) {
    jobs.value.splice(index, 1)
  }
}

function retryJob(job) {
  job.status = 'queued'
  job.error = null
  job.startedAt = null
  job.runtime = null
}

function downloadResults(job) {
  console.log('Downloading results for job:', job.id)
}

async function submitJob() {
  const { valid } = await jobFormRef.value.validate()
  if (!valid) return

  isSubmitting.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))

  const project = projectsStore.getProjectById(newJob.value.projectId)
  const model = availableModels.value.find(m => m.id === newJob.value.modelId)
  const dataset = availableDatasets.value.find(d => d.id === newJob.value.datasetId)

  jobs.value.unshift({
    id: `job-${Math.random().toString(36).substr(2, 9)}`,
    projectId: newJob.value.projectId,
    projectName: project?.shortTitle || 'Unknown',
    useCase: project?.useCase || 'UC7',
    jobType: newJob.value.jobType,
    modelName: model?.name || 'Unknown Model',
    datasetName: dataset?.name || 'Unknown Dataset',
    hpcSite: newJob.value.hpcSite,
    nodes: newJob.value.nodes,
    gpus: newJob.value.gpus,
    memory: newJob.value.memory,
    status: 'queued',
    submittedAt: new Date().toISOString(),
    startedAt: null,
    completedAt: null,
    runtime: null
  })

  isSubmitting.value = false
  showNewJobDialog.value = false
  newJob.value = {
    projectId: null,
    jobType: null,
    modelId: null,
    datasetId: null,
    hpcSite: null,
    nodes: 1,
    gpus: 4,
    memory: '64 GB',
    notes: ''
  }
}

onMounted(async () => {
  if (projectsStore.projects.length === 0) {
    await projectsStore.fetchProjects()
  }
})
</script>

<style scoped lang="scss">
// View-specific styles

// Filters
.filters-section {
  margin-bottom: 1.5rem;
}

.filters-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-field {
  flex: 1;
  min-width: 200px;
  max-width: 320px;
}

.filter-select {
  width: 150px;
}

// Table
.jobs-table-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
  overflow: hidden;
}

.jobs-table {
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
  
  :deep(.v-data-table__tr:hover) {
    background: rgba(51, 65, 85, 0.2) !important;
  }
}

.job-id {
  color: #64748b;
  font-size: 0.8125rem;
}

.project-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.project-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  
  &.uc7 {
    background: rgba(230, 152, 48, 0.2);
    color: #E69830;
  }
  &.uc8 {
    background: rgba(139, 92, 246, 0.2);
    color: #a78bfa;
  }
}

.project-name {
  font-size: 0.875rem;
  color: #e2e8f0;
}

.job-type-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  .job-type-icon {
    color: #64748b;
  }
}

.hpc-chip {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
}

.resources-cell {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.75rem;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #94a3b8;
  
  .v-icon {
    color: #64748b;
  }
}

.status-chip {
  text-transform: capitalize;
}

.actions-cell {
  display: flex;
  gap: 0.25rem;
}

// Empty state
.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  
  h3 {
    font-size: 1.125rem;
    color: #f1f5f9;
    margin-bottom: 0.5rem;
  }
  
  p {
    color: #64748b;
  }
}

// Dialogs
.new-job-dialog,
.details-dialog {
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  
  h2 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #f1f5f9;
  }
}

.dialog-content {
  padding: 1.5rem !important;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
}

.resource-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 0.75rem;
  margin-top: 0.5rem;
}

// Details dialog
.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  
  &.full-width {
    grid-column: span 2;
  }
}

.detail-label {
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 0.9375rem;
  color: #e2e8f0;
  
  &.error-text {
    color: #ef4444;
  }
}

.progress-section,
.results-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(51, 65, 85, 0.5);
  
  h4 {
    font-size: 0.875rem;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 1rem;
  }
}

.job-metrics {
  display: flex;
  gap: 1rem;
}

.metric-card {
  flex: 1;
  padding: 0.75rem;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric-label {
  font-size: 0.6875rem;
  color: #64748b;
  text-transform: uppercase;
}

.metric-value {
  font-size: 1.125rem;
  font-weight: 600;
  color: #E69830;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.result-item {
  padding: 0.75rem;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-label {
  font-size: 0.8125rem;
  color: #94a3b8;
}

.result-value {
  font-size: 1rem;
  font-weight: 600;
  color: #10b981;
}

// Responsive
@media (max-width: 960px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .filters-row {
    flex-direction: column;
  }
  
  .search-field,
  .filter-select {
    max-width: none;
    width: 100%;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-item.full-width {
    grid-column: span 1;
  }
  
  .job-metrics {
    flex-direction: column;
  }
  
  .results-grid {
    grid-template-columns: 1fr;
  }
}
</style>
