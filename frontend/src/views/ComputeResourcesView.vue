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
              <v-icon class="title-icon">mdi-server</v-icon>
              Compute Quotas
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
              Monitor storage and GPU hour quotas for your projects
            </p>
          </div>
        </div>

        <!-- Project Resource Quotas -->
        <v-card class="resources-card glass">
          <v-card-title class="card-title">
            <v-icon class="mr-2">mdi-folder-multiple</v-icon>
            Project Resource Quotas
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-0">
            <v-data-table
              :headers="resourceHeaders"
              :items="filteredProjectResources"
              class="resources-table"
              :items-per-page="-1"
              hide-default-footer
            >
              <template v-slot:item.projectName="{ item }">
                <div class="project-cell">
                  <span class="project-badge" :class="item.useCase.toLowerCase()">{{ item.useCase }}</span>
                  <span class="project-name">{{ item.projectName }}</span>
                </div>
              </template>
              
              <template v-slot:item.storageUsed="{ item }">
                <div class="quota-cell">
                  <div class="quota-bar-container">
                    <div 
                      class="quota-bar" 
                      :style="{ width: `${(item.storageUsed / item.storageQuota) * 100}%` }"
                    ></div>
                  </div>
                  <span class="quota-text">{{ item.storageUsed }} / {{ item.storageQuota }} TB</span>
                </div>
              </template>
              
              <template v-slot:item.gpuUsed="{ item }">
                <div class="quota-cell">
                  <div class="quota-bar-container">
                    <div 
                      class="quota-bar" 
                      :style="{ width: `${(item.gpuUsed / item.gpuQuota) * 100}%` }"
                    ></div>
                  </div>
                  <span class="quota-text">{{ item.gpuUsed.toLocaleString() }} / {{ item.gpuQuota.toLocaleString() }} hrs</span>
                </div>
              </template>

              <template v-slot:item.storagePercent="{ item }">
                <v-chip 
                  size="small" 
                  :color="getPercentColor(item.storageUsed / item.storageQuota)"
                  variant="tonal"
                >
                  {{ Math.round((item.storageUsed / item.storageQuota) * 100) }}%
                </v-chip>
              </template>

              <template v-slot:item.gpuPercent="{ item }">
                <v-chip 
                  size="small" 
                  :color="getPercentColor(item.gpuUsed / item.gpuQuota)"
                  variant="tonal"
                >
                  {{ Math.round((item.gpuUsed / item.gpuQuota) * 100) }}%
                </v-chip>
              </template>

              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon="mdi-chart-line"
                  size="small"
                  variant="text"
                  @click="viewDetails(item)"
                />
                <v-btn
                  icon="mdi-arrow-up-circle"
                  size="small"
                  variant="text"
                  color="primary"
                  @click="requestIncrease(item)"
                />
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </div>
    </v-main>

    <!-- Request Increase Dialog -->
    <v-dialog v-model="showRequestDialog" max-width="500">
      <v-card class="glass">
        <v-card-title>Request Quota Increase</v-card-title>
        <v-divider />
        <v-card-text>
          <p class="mb-4" v-if="selectedProject">
            Request additional resources for <strong>{{ selectedProject.projectName }}</strong>
          </p>
          <v-select
            v-model="requestType"
            :items="['Storage (TB)', 'GPU Hours']"
            label="Resource Type"
            variant="outlined"
            class="mb-4"
          />
          <v-text-field
            v-model="requestAmount"
            label="Additional Amount"
            variant="outlined"
            type="number"
            class="mb-4"
          />
          <v-textarea
            v-model="requestJustification"
            label="Justification"
            variant="outlined"
            rows="3"
            placeholder="Please explain why you need additional resources..."
          />
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showRequestDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="submitRequest">Submit Request</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar -->
    <v-snackbar v-model="showSnackbar" :color="snackbarColor" :timeout="3000">
      {{ snackbarMessage }}
    </v-snackbar>
  </v-layout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useProjectsStore } from '@/stores/projects'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const projectsStore = useProjectsStore()
const sidebarRail = ref(false)

// Dialog state
const showRequestDialog = ref(false)
const selectedProject = ref(null)
const requestType = ref('Storage (TB)')
const requestAmount = ref('')
const requestJustification = ref('')

// Snackbar
const showSnackbar = ref(false)
const snackbarMessage = ref('')
const snackbarColor = ref('success')

// Mock resource data per project
const projectResources = ref([
  {
    projectId: 'proj-uc7-001',
    projectName: 'UC7 - CRC Prediction',
    useCase: 'UC7',
    storageUsed: 12.5,
    storageQuota: 20,
    gpuUsed: 4520,
    gpuQuota: 10000,
  },
  {
    projectId: 'proj-uc8-001',
    projectName: 'UC8 - Synthetic Data',
    useCase: 'UC8',
    storageUsed: 8.2,
    storageQuota: 15,
    gpuUsed: 2100,
    gpuQuota: 5000,
  },
  {
    projectId: 'proj-uc7-002',
    projectName: 'UC7 - XAI Validation',
    useCase: 'UC7',
    storageUsed: 0,
    storageQuota: 10,
    gpuUsed: 0,
    gpuQuota: 3000,
  },
  {
    projectId: 'proj-uc8-002',
    projectName: 'UC8 - MR Benchmark',
    useCase: 'UC8',
    storageUsed: 18.7,
    storageQuota: 25,
    gpuUsed: 8900,
    gpuQuota: 10000,
  },
])

// Table headers
const resourceHeaders = [
  { title: 'Project', key: 'projectName', sortable: true },
  { title: 'Storage Usage', key: 'storageUsed', sortable: true },
  { title: 'Storage %', key: 'storagePercent', sortable: true, align: 'center' },
  { title: 'GPU Hours Usage', key: 'gpuUsed', sortable: true },
  { title: 'GPU %', key: 'gpuPercent', sortable: true, align: 'center' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
]

// Computed values - add percentage fields for sorting
const filteredProjectResources = computed(() => {
  let resources = projectResources.value
  
  if (projectsStore.selectedProjectId) {
    resources = resources.filter(r => r.projectId === projectsStore.selectedProjectId)
  }
  
  // Add computed percentage fields for sorting
  return resources.map(r => ({
    ...r,
    storagePercent: Math.round((r.storageUsed / r.storageQuota) * 100),
    gpuPercent: Math.round((r.gpuUsed / r.gpuQuota) * 100),
  }))
})

// Methods
function getPercentColor(ratio) {
  if (ratio >= 0.9) return 'error'
  if (ratio >= 0.7) return 'warning'
  return 'success'
}

function viewDetails(project) {
  snackbarMessage.value = `Viewing details for ${project.projectName}`
  snackbarColor.value = 'info'
  showSnackbar.value = true
}

function requestIncrease(project) {
  selectedProject.value = project
  requestType.value = 'Storage (TB)'
  requestAmount.value = ''
  requestJustification.value = ''
  showRequestDialog.value = true
}

function submitRequest() {
  showRequestDialog.value = false
  snackbarMessage.value = 'Quota increase request submitted successfully'
  snackbarColor.value = 'success'
  showSnackbar.value = true
}
</script>

<style scoped lang="scss">
// View-specific styles

.resources-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: #f1f5f9;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  
  .v-icon {
    color: #94a3b8;
  }
}

// Table styles
.resources-table {
  background: transparent !important;
  
  :deep(.v-data-table__thead) {
    background: rgba(15, 23, 42, 0.5);
    
    th {
      color: #94a3b8 !important;
      font-weight: 600;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      border-bottom: 1px solid rgba(51, 65, 85, 0.5) !important;
    }
  }
  
  :deep(.v-data-table__tbody) {
    tr {
      &:hover {
        background: rgba(51, 65, 85, 0.2) !important;
      }
      
      td {
        border-bottom: 1px solid rgba(51, 65, 85, 0.3) !important;
        color: #e2e8f0;
      }
    }
  }
}

.project-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.project-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.625rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  
  &.uc7 {
    background: rgba(230, 152, 48, 0.15);
    color: #E69830;
  }
  
  &.uc8 {
    background: rgba(139, 92, 246, 0.15);
    color: #a78bfa;
  }
}

.project-name {
  font-weight: 500;
  color: #f1f5f9;
}

.quota-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 150px;
}

.quota-bar-container {
  height: 6px;
  background: rgba(51, 65, 85, 0.5);
  border-radius: 3px;
  overflow: hidden;
}

.quota-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
  background: #E69830;
}

.quota-text {
  font-size: 0.75rem;
  color: #94a3b8;
  font-family: 'JetBrains Mono', monospace;
}
</style>
