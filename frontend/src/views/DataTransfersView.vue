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
              <v-icon class="title-icon">mdi-swap-horizontal</v-icon>
              Data Transfers
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
              Monitor and manage data transfers between storage locations and HPC sites
            </p>
          </div>
          <div class="header-actions">
            <v-btn 
              variant="outlined" 
              prepend-icon="mdi-refresh"
              @click="refreshTransfers"
              :loading="isRefreshing"
            >
              Refresh
            </v-btn>
            <v-btn 
              color="primary" 
              prepend-icon="mdi-plus"
              @click="showNewTransferDialog = true"
            >
              New Transfer
            </v-btn>
          </div>
        </div>

        <!-- Stats cards -->
        <section class="stats-section mb-6">
          <v-row>
            <v-col cols="6" sm="3" v-for="stat in transferStats" :key="stat.label">
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
              placeholder="Search transfers..."
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
          </div>
        </section>

        <!-- Transfers table -->
        <section class="table-section slide-up delay-4">
          <v-card class="transfers-table-card glass" :elevation="0">
            <v-data-table
              :headers="tableHeaders"
              :items="filteredTransfers"
              :loading="isLoading"
              class="transfers-table"
              item-key="id"
              hover
            >
              <!-- ID column -->
              <template v-slot:item.id="{ item }">
                <span class="transfer-id font-mono">{{ item.id.slice(0, 8) }}...</span>
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

              <!-- Source/Destination column -->
              <template v-slot:item.route="{ item }">
                <div class="route-cell">
                  <span class="location source">{{ item.source }}</span>
                  <v-icon size="16" class="route-arrow">mdi-arrow-right</v-icon>
                  <span class="location destination">{{ item.destination }}</span>
                </div>
              </template>

              <!-- Size column -->
              <template v-slot:item.size="{ item }">
                <span class="font-mono">{{ formatSize(item.size) }}</span>
              </template>

              <!-- Progress column -->
              <template v-slot:item.progress="{ item }">
                <div class="progress-cell">
                  <v-progress-linear
                    :model-value="item.progress"
                    :color="getProgressColor(item.status)"
                    height="6"
                    rounded
                    class="progress-bar"
                  />
                  <span class="progress-text font-mono">{{ item.progress }}%</span>
                </div>
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
                    @click="viewTransfer(item)"
                  />
                  <v-btn
                    v-if="item.status === 'in_progress' || item.status === 'pending'"
                    icon="mdi-pause"
                    size="small"
                    variant="text"
                    @click="pauseTransfer(item)"
                  />
                  <v-btn
                    v-if="item.status === 'paused'"
                    icon="mdi-play"
                    size="small"
                    variant="text"
                    color="primary"
                    @click="resumeTransfer(item)"
                  />
                  <v-btn
                    v-if="['pending', 'in_progress', 'paused'].includes(item.status)"
                    icon="mdi-close"
                    size="small"
                    variant="text"
                    color="error"
                    @click="cancelTransfer(item)"
                  />
                  <v-btn
                    v-if="item.status === 'failed'"
                    icon="mdi-refresh"
                    size="small"
                    variant="text"
                    color="warning"
                    @click="retryTransfer(item)"
                  />
                </div>
              </template>

              <!-- Empty state -->
              <template v-slot:no-data>
                <div class="empty-state">
                  <v-icon size="48" color="primary" class="mb-3">mdi-swap-horizontal</v-icon>
                  <h3>No transfers found</h3>
                  <p>Start a new data transfer to see it here.</p>
                </div>
              </template>
            </v-data-table>
          </v-card>
        </section>
      </div>
    </v-main>

    <!-- New Transfer Dialog -->
    <v-dialog v-model="showNewTransferDialog" max-width="560">
      <v-card class="new-transfer-dialog glass">
        <div class="dialog-header">
          <h2>New Data Transfer</h2>
          <v-btn icon="mdi-close" variant="text" size="small" @click="showNewTransferDialog = false" />
        </div>
        <v-divider />
        <v-card-text class="dialog-content">
          <v-form ref="transferFormRef">
            <v-select
              v-model="newTransfer.projectId"
              :items="projectsStore.activeProjects"
              item-title="shortTitle"
              item-value="id"
              label="Project"
              :rules="[v => !!v || 'Project is required']"
              class="mb-4"
            />
            <v-select
              v-model="newTransfer.datasetId"
              :items="availableDatasets"
              item-title="name"
              item-value="id"
              label="Dataset"
              :rules="[v => !!v || 'Dataset is required']"
              class="mb-4"
            />
            <v-select
              v-model="newTransfer.source"
              :items="sourceLocations"
              label="Source Location"
              :rules="[v => !!v || 'Source is required']"
              class="mb-4"
            />
            <v-select
              v-model="newTransfer.destination"
              :items="destinationLocations"
              label="Destination (HPC/SPE)"
              :rules="[v => !!v || 'Destination is required']"
              class="mb-4"
            />
            <v-textarea
              v-model="newTransfer.notes"
              label="Notes (optional)"
              rows="2"
            />
          </v-form>
        </v-card-text>
        <v-divider />
        <div class="dialog-footer">
          <v-btn variant="text" @click="showNewTransferDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="initiateTransfer" :loading="isInitiating">
            Start Transfer
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- Transfer Details Dialog -->
    <v-dialog v-model="showDetailsDialog" max-width="600">
      <v-card class="details-dialog glass" v-if="selectedTransfer">
        <div class="dialog-header">
          <h2>Transfer Details</h2>
          <v-btn icon="mdi-close" variant="text" size="small" @click="showDetailsDialog = false" />
        </div>
        <v-divider />
        <v-card-text class="dialog-content">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">Transfer ID</span>
              <span class="detail-value font-mono">{{ selectedTransfer.id }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Status</span>
              <v-chip :color="getStatusColor(selectedTransfer.status)" size="small" variant="tonal">
                {{ selectedTransfer.status }}
              </v-chip>
            </div>
            <div class="detail-item">
              <span class="detail-label">Project</span>
              <span class="detail-value">{{ selectedTransfer.projectName }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Dataset</span>
              <span class="detail-value">{{ selectedTransfer.datasetName }}</span>
            </div>
            <div class="detail-item full-width">
              <span class="detail-label">Route</span>
              <div class="route-display">
                <span class="location">{{ selectedTransfer.source }}</span>
                <v-icon size="20">mdi-arrow-right</v-icon>
                <span class="location">{{ selectedTransfer.destination }}</span>
              </div>
            </div>
            <div class="detail-item">
              <span class="detail-label">Size</span>
              <span class="detail-value font-mono">{{ formatSize(selectedTransfer.size) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Progress</span>
              <span class="detail-value font-mono">{{ selectedTransfer.progress }}%</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Started</span>
              <span class="detail-value">{{ formatDate(selectedTransfer.startedAt) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Completed</span>
              <span class="detail-value">{{ selectedTransfer.completedAt ? formatDate(selectedTransfer.completedAt) : '—' }}</span>
            </div>
            <div class="detail-item full-width" v-if="selectedTransfer.error">
              <span class="detail-label">Error</span>
              <span class="detail-value error-text">{{ selectedTransfer.error }}</span>
            </div>
          </div>

          <!-- Progress visualization -->
          <div class="progress-section" v-if="selectedTransfer.status === 'in_progress'">
            <h4>Transfer Progress</h4>
            <v-progress-linear
              :model-value="selectedTransfer.progress"
              color="primary"
              height="12"
              rounded
              striped
            />
            <div class="progress-stats">
              <span>{{ formatSize(selectedTransfer.size * selectedTransfer.progress / 100) }} transferred</span>
              <span>{{ selectedTransfer.speed || '—' }}</span>
              <span>{{ selectedTransfer.eta || '—' }} remaining</span>
            </div>
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
const isInitiating = ref(false)
const searchQuery = ref('')
const statusFilter = ref(null)
const showNewTransferDialog = ref(false)
const showDetailsDialog = ref(false)
const selectedTransfer = ref(null)
const transferFormRef = ref(null)

// New transfer form
const newTransfer = ref({
  projectId: null,
  datasetId: null,
  source: null,
  destination: null,
  notes: ''
})

// Mock data
const transfers = ref([
  {
    id: 'txf-a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    projectId: 'proj-uc7-001',
    projectName: 'UC7 - CRC Prediction',
    useCase: 'UC7',
    datasetName: 'Lymph Node WSI Collection A',
    source: 'BBMRI-AT Storage',
    destination: 'MUSICA',
    size: 12500000000000, // 12.5 TB
    progress: 100,
    status: 'completed',
    startedAt: '2024-12-15T10:30:00Z',
    completedAt: '2024-12-15T14:45:00Z',
  },
  {
    id: 'txf-b2c3d4e5-f6a7-8901-bcde-f23456789012',
    projectId: 'proj-uc7-001',
    projectName: 'UC7 - CRC Prediction',
    useCase: 'UC7',
    datasetName: 'Lymph Node WSI Collection B',
    source: 'BBMRI-AT Storage',
    destination: 'MUG-SX',
    size: 8900000000000, // 8.9 TB
    progress: 67,
    status: 'in_progress',
    startedAt: '2024-12-18T09:15:00Z',
    completedAt: null,
    speed: '1.2 GB/s',
    eta: '~4h 30m'
  },
  {
    id: 'txf-c3d4e5f6-a7b8-9012-cdef-345678901234',
    projectId: 'proj-uc8-001',
    projectName: 'UC8 - Synthetic Data',
    useCase: 'UC8',
    datasetName: 'Training Set Alpha',
    source: 'MUG Storage',
    destination: 'MUSICA',
    size: 4500000000000, // 4.5 TB
    progress: 0,
    status: 'pending',
    startedAt: null,
    completedAt: null,
  },
  {
    id: 'txf-d4e5f6a7-b8c9-0123-defa-456789012345',
    projectId: 'proj-uc8-001',
    projectName: 'UC8 - Synthetic Data',
    useCase: 'UC8',
    datasetName: 'Validation Set Beta',
    source: 'MUG Storage',
    destination: 'MUG-SX',
    size: 3200000000000, // 3.2 TB
    progress: 34,
    status: 'paused',
    startedAt: '2024-12-17T14:00:00Z',
    completedAt: null,
  },
  {
    id: 'txf-e5f6a7b8-c9d0-1234-efab-567890123456',
    projectId: 'proj-uc7-001',
    projectName: 'UC7 - CRC Prediction',
    useCase: 'UC7',
    datasetName: 'Annotations Dataset',
    source: 'BBMRI-AT Storage',
    destination: 'MUSICA',
    size: 1800000000000, // 1.8 TB
    progress: 100,
    status: 'failed',
    startedAt: '2024-12-16T08:00:00Z',
    completedAt: null,
    error: 'Connection timeout after 3 retries'
  }
])

const tableHeaders = [
  { title: 'ID', key: 'id', width: '120px' },
  { title: 'Project', key: 'project', width: '200px' },
  { title: 'Route', key: 'route', width: '280px' },
  { title: 'Size', key: 'size', width: '100px' },
  { title: 'Progress', key: 'progress', width: '150px' },
  { title: 'Status', key: 'status', width: '120px' },
  { title: 'Actions', key: 'actions', width: '140px', sortable: false }
]

const statusOptions = ['pending', 'in_progress', 'paused', 'completed', 'failed']

const sourceLocations = ['BBMRI-AT Storage', 'MUG Storage']
const destinationLocations = ['MUSICA', 'MUG-SX']

const availableDatasets = computed(() => [
  { id: 'ds-001', name: 'Lymph Node WSI Collection A' },
  { id: 'ds-002', name: 'Lymph Node WSI Collection B' },
  { id: 'ds-003', name: 'Training Set Alpha' },
  { id: 'ds-004', name: 'Validation Set Beta' },
])

// Base transfers filtered by selected project
const projectFilteredTransfers = computed(() => {
  if (projectsStore.selectedProjectId) {
    return transfers.value.filter(t => t.projectId === projectsStore.selectedProjectId)
  }
  return transfers.value
})

const transferStats = computed(() => [
  {
    label: 'Completed',
    value: projectFilteredTransfers.value.filter(t => t.status === 'completed').length,
    icon: 'mdi-check-circle',
    status: 'completed'
  },
  {
    label: 'In Progress',
    value: projectFilteredTransfers.value.filter(t => t.status === 'in_progress').length,
    icon: 'mdi-progress-clock',
    status: 'in_progress'
  },
  {
    label: 'Pending',
    value: projectFilteredTransfers.value.filter(t => t.status === 'pending').length,
    icon: 'mdi-clock-outline',
    status: 'pending'
  },
  {
    label: 'Failed',
    value: projectFilteredTransfers.value.filter(t => t.status === 'failed').length,
    icon: 'mdi-alert-circle',
    status: 'failed'
  }
])

const filteredTransfers = computed(() => {
  let result = transfers.value

  // Filter by selected project from sidebar
  if (projectsStore.selectedProjectId) {
    result = result.filter(t => t.projectId === projectsStore.selectedProjectId)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(t => 
      t.projectName.toLowerCase().includes(query) ||
      t.datasetName.toLowerCase().includes(query) ||
      t.source.toLowerCase().includes(query) ||
      t.destination.toLowerCase().includes(query) ||
      t.id.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    result = result.filter(t => t.status === statusFilter.value)
  }

  return result
})

function getStatusColor(status) {
  const colors = {
    completed: 'success',
    in_progress: 'info',
    pending: 'warning',
    paused: 'secondary',
    failed: 'error'
  }
  return colors[status] || 'default'
}

function getStatusIcon(status) {
  const icons = {
    completed: 'mdi-check-circle',
    in_progress: 'mdi-progress-clock',
    pending: 'mdi-clock-outline',
    paused: 'mdi-pause-circle',
    failed: 'mdi-alert-circle'
  }
  return icons[status] || 'mdi-circle'
}

function getProgressColor(status) {
  if (status === 'failed') return 'error'
  if (status === 'paused') return 'secondary'
  if (status === 'completed') return 'success'
  return 'primary'
}

function formatSize(bytes) {
  if (!bytes) return '—'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let unitIndex = 0
  let size = bytes
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString()
}

async function refreshTransfers() {
  isRefreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  isRefreshing.value = false
}

function viewTransfer(transfer) {
  selectedTransfer.value = transfer
  showDetailsDialog.value = true
}

function pauseTransfer(transfer) {
  transfer.status = 'paused'
}

function resumeTransfer(transfer) {
  transfer.status = 'in_progress'
}

function cancelTransfer(transfer) {
  const index = transfers.value.findIndex(t => t.id === transfer.id)
  if (index > -1) {
    transfers.value.splice(index, 1)
  }
}

function retryTransfer(transfer) {
  transfer.status = 'pending'
  transfer.progress = 0
  transfer.error = null
}

async function initiateTransfer() {
  const { valid } = await transferFormRef.value.validate()
  if (!valid) return

  isInitiating.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))

  const project = projectsStore.getProjectById(newTransfer.value.projectId)
  const dataset = availableDatasets.value.find(d => d.id === newTransfer.value.datasetId)

  transfers.value.unshift({
    id: `txf-${Math.random().toString(36).substr(2, 9)}`,
    projectId: newTransfer.value.projectId,
    projectName: project?.shortTitle || 'Unknown',
    useCase: project?.useCase || 'UC7',
    datasetName: dataset?.name || 'Unknown Dataset',
    source: newTransfer.value.source,
    destination: newTransfer.value.destination,
    size: Math.floor(Math.random() * 100000000000),
    progress: 0,
    status: 'pending',
    startedAt: null,
    completedAt: null,
  })

  isInitiating.value = false
  showNewTransferDialog.value = false
  newTransfer.value = { projectId: null, datasetId: null, source: null, destination: null, notes: '' }
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
  width: 160px;
}

// Table
.transfers-table-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
  overflow: hidden;
}

.transfers-table {
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

.transfer-id {
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

.route-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.location {
  font-size: 0.8125rem;
  color: #94a3b8;
  
  &.source {
    color: #e2e8f0;
  }
}

.route-arrow {
  color: #64748b;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.progress-bar {
  flex: 1;
  background: rgba(51, 65, 85, 0.5);
}

.progress-text {
  font-size: 0.75rem;
  color: #94a3b8;
  min-width: 36px;
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
.new-transfer-dialog,
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

.route-display {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  
  .location {
    padding: 0.5rem 0.75rem;
    background: rgba(30, 41, 59, 0.5);
    border-radius: 6px;
    font-size: 0.875rem;
    color: #e2e8f0;
  }
}

.progress-section {
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

.progress-stats {
  display: flex;
  justify-content: space-between;
  margin-top: 0.75rem;
  font-size: 0.75rem;
  color: #64748b;
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
}
</style>
