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
              <v-icon class="title-icon">mdi-database</v-icon>
              Datasets
              <v-chip
                v-if="projectsStore.selectedProjectId"
                size="small"
                variant="tonal"
                color="primary"
                class="ml-3"
                closable
                @click:close="projectsStore.selectProject(null)"
              >
                {{ projectsStore.selectedProject?.shortTitle }}
              </v-chip>
            </h1>
            <p class="page-subtitle">
              Manage and monitor datasets across your projects
            </p>
          </div>
        </div>

        <!-- Stats Cards -->
        <v-row class="mb-6">
          <v-col cols="12" sm="6" md="3">
            <v-card class="stat-card glass">
              <v-card-text>
                <div class="stat-icon total">
                  <v-icon>mdi-database</v-icon>
                </div>
                <div class="stat-info">
                  <span class="stat-value">{{ filteredDatasets.length }}</span>
                  <span class="stat-label">Total Datasets</span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card class="stat-card glass">
              <v-card-text>
                <div class="stat-icon wsi">
                  <v-icon>mdi-image-multiple</v-icon>
                </div>
                <div class="stat-info">
                  <span class="stat-value">{{ totalWsiCount }}</span>
                  <span class="stat-label">Total WSIs</span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card class="stat-card glass">
              <v-card-text>
                <div class="stat-icon size">
                  <v-icon>mdi-harddisk</v-icon>
                </div>
                <div class="stat-info">
                  <span class="stat-value">{{ totalSize }}</span>
                  <span class="stat-label">Total Size</span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card class="stat-card glass">
              <v-card-text>
                <div class="stat-icon active">
                  <v-icon>mdi-check-circle</v-icon>
                </div>
                <div class="stat-info">
                  <span class="stat-value">{{ activeDatasets }}</span>
                  <span class="stat-label">Active</span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Filters -->
        <v-card class="filters-card glass mb-6">
          <v-card-text>
            <v-row align="center">
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="searchQuery"
                  prepend-inner-icon="mdi-magnify"
                  placeholder="Search datasets..."
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  clearable
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="typeFilter"
                  :items="dataTypes"
                  label="Data Type"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  clearable
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="statusFilter"
                  :items="statusOptions"
                  label="Status"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  clearable
                />
              </v-col>
              <v-col cols="12" md="2" class="text-right">
                <v-btn-toggle v-model="viewMode" mandatory density="comfortable">
                  <v-btn value="grid" icon="mdi-view-grid" size="small" />
                  <v-btn value="table" icon="mdi-view-list" size="small" />
                </v-btn-toggle>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Datasets Grid View -->
        <div v-if="viewMode === 'grid'" class="datasets-grid">
          <v-card
            v-for="dataset in filteredDatasets"
            :key="dataset.id"
            class="dataset-card glass"
            @click="openDatasetDetails(dataset)"
          >
            <div class="card-header">
              <div class="dataset-icon">
                <v-icon size="28" color="primary">{{ getTypeIcon(dataset.type) }}</v-icon>
              </div>
              <v-chip
                :color="getStatusColor(dataset.status)"
                size="small"
                variant="tonal"
              >
                {{ dataset.status }}
              </v-chip>
            </div>
            
            <v-card-text class="card-body">
              <h3 class="dataset-name">{{ dataset.name }}</h3>
              <p class="dataset-source">{{ dataset.source }}</p>
              <p class="dataset-description">{{ dataset.description }}</p>
              
              <div class="dataset-stats">
                <div class="stat-item">
                  <v-icon size="14">mdi-image-multiple</v-icon>
                  <span>{{ formatNumber(dataset.wsiCount) }} WSIs</span>
                </div>
                <div class="stat-item">
                  <v-icon size="14">mdi-harddisk</v-icon>
                  <span>{{ dataset.size }}</span>
                </div>
              </div>

              <div class="storage-badge">
                <v-icon size="12">mdi-server</v-icon>
                <span class="storage-label">Primary Storage:</span>
                <span class="storage-value">{{ dataset.primaryStorage }}</span>
              </div>

              <div class="projects-section">
                <span class="projects-label">Assigned to:</span>
                <div class="projects-chips">
                  <v-chip
                    v-for="project in dataset.projects"
                    :key="project.id"
                    size="x-small"
                    :color="project.useCase === 'UC7' ? 'primary' : 'purple'"
                    variant="tonal"
                    class="project-chip"
                  >
                    {{ project.shortName }}
                  </v-chip>
                </div>
              </div>
            </v-card-text>

            <v-divider />

            <v-card-actions class="card-actions">
              <v-btn variant="text" size="small" @click.stop="openDatasetDetails(dataset)">
                View Details
              </v-btn>
              <v-spacer />
              <v-btn
                icon="mdi-chart-line"
                size="small"
                variant="text"
                @click.stop="viewStats(dataset)"
                title="View Statistics"
              />
            </v-card-actions>
          </v-card>
        </div>

        <!-- Datasets Table View -->
        <v-card v-else class="table-card glass">
          <v-data-table
            :headers="tableHeaders"
            :items="filteredDatasets"
            :items-per-page="10"
            class="datasets-table"
            hover
            @click:row="(e, { item }) => openDatasetDetails(item)"
          >
            <template v-slot:item.name="{ item }">
              <div class="name-cell">
                <v-icon size="20" color="primary" class="mr-2">{{ getTypeIcon(item.type) }}</v-icon>
                <div>
                  <span class="dataset-name-text">{{ item.name }}</span>
                  <span class="dataset-source-text">{{ item.source }}</span>
                </div>
              </div>
            </template>

            <template v-slot:item.wsiCount="{ item }">
              <span class="font-mono">{{ formatNumber(item.wsiCount) }}</span>
            </template>

            <template v-slot:item.size="{ item }">
              <span class="font-mono">{{ item.size }}</span>
            </template>

            <template v-slot:item.projects="{ item }">
              <div class="projects-cell">
                <v-chip
                  v-for="project in item.projects.slice(0, 2)"
                  :key="project.id"
                  size="x-small"
                  :color="project.useCase === 'UC7' ? 'primary' : 'purple'"
                  variant="tonal"
                  class="mr-1"
                >
                  {{ project.shortName }}
                </v-chip>
                <v-chip
                  v-if="item.projects.length > 2"
                  size="x-small"
                  variant="tonal"
                >
                  +{{ item.projects.length - 2 }}
                </v-chip>
              </div>
            </template>

            <template v-slot:item.status="{ item }">
              <v-chip
                :color="getStatusColor(item.status)"
                size="small"
                variant="tonal"
              >
                {{ item.status }}
              </v-chip>
            </template>

            <template v-slot:item.actions="{ item }">
              <v-btn
                icon="mdi-eye"
                size="small"
                variant="text"
                @click.stop="openDatasetDetails(item)"
              />
              <v-btn
                icon="mdi-chart-line"
                size="small"
                variant="text"
                @click.stop="viewStats(item)"
              />
            </template>
          </v-data-table>
        </v-card>
      </div>
    </v-main>

    <!-- Dataset Details Dialog -->
    <v-dialog v-model="showDetailsDialog" max-width="800">
      <v-card class="details-dialog glass" v-if="selectedDataset">
        <div class="dialog-header">
          <div class="header-info">
            <v-icon size="28" color="primary" class="mr-3">{{ getTypeIcon(selectedDataset.type) }}</v-icon>
            <div>
              <h2>{{ selectedDataset.name }}</h2>
              <span class="source-text">{{ selectedDataset.source }}</span>
            </div>
          </div>
          <v-btn icon="mdi-close" variant="text" size="small" @click="showDetailsDialog = false" />
        </div>
        
        <v-divider />
        
        <v-card-text class="dialog-content">
          <div class="detail-section">
            <h4 class="section-title">Description</h4>
            <p class="description-text">{{ selectedDataset.fullDescription }}</p>
          </div>

          <v-row class="detail-grid mb-4">
            <v-col cols="6" md="3">
              <div class="detail-item">
                <span class="detail-label">Data Type</span>
                <span class="detail-value">{{ selectedDataset.type }}</span>
              </div>
            </v-col>
            <v-col cols="6" md="3">
              <div class="detail-item">
                <span class="detail-label">WSI Count</span>
                <span class="detail-value font-mono">{{ formatNumber(selectedDataset.wsiCount) }}</span>
              </div>
            </v-col>
            <v-col cols="6" md="3">
              <div class="detail-item">
                <span class="detail-label">Size</span>
                <span class="detail-value font-mono">{{ selectedDataset.size }}</span>
              </div>
            </v-col>
            <v-col cols="6" md="3">
              <div class="detail-item">
                <span class="detail-label">Status</span>
                <v-chip :color="getStatusColor(selectedDataset.status)" size="small" variant="tonal">
                  {{ selectedDataset.status }}
                </v-chip>
              </div>
            </v-col>
          </v-row>

          <div class="detail-section">
            <h4 class="section-title">Storage Location</h4>
            <div class="storage-info">
              <v-icon size="20" class="mr-2">mdi-server</v-icon>
              <span>{{ selectedDataset.storageLocation }}</span>
            </div>
          </div>

          <div class="detail-section">
            <h4 class="section-title">Assigned Projects</h4>
            <div class="projects-list">
              <div 
                v-for="project in selectedDataset.projects" 
                :key="project.id"
                class="project-item"
              >
                <div class="project-badge" :class="project.useCase.toLowerCase()">
                  {{ project.useCase }}
                </div>
                <div class="project-info">
                  <span class="project-name">{{ project.name }}</span>
                  <span class="project-role">{{ project.role }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="detail-section" v-if="selectedDataset.metadata">
            <h4 class="section-title">Metadata</h4>
            <v-row>
              <v-col cols="6" v-for="(value, key) in selectedDataset.metadata" :key="key">
                <div class="metadata-item">
                  <span class="metadata-label">{{ formatLabel(key) }}</span>
                  <span class="metadata-value">{{ value }}</span>
                </div>
              </v-col>
            </v-row>
          </div>
        </v-card-text>

        <v-divider />

        <div class="dialog-footer">
          <v-btn variant="text" @click="showDetailsDialog = false">Close</v-btn>
          <v-btn color="primary" variant="tonal" @click="viewStats(selectedDataset)">
            <v-icon class="mr-1">mdi-chart-line</v-icon>
            View Statistics
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- Stats Snackbar -->
    <v-snackbar v-model="showSnackbar" :timeout="3000">
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
const viewMode = ref('grid')
const searchQuery = ref('')
const typeFilter = ref(null)
const statusFilter = ref(null)
const showDetailsDialog = ref(false)
const selectedDataset = ref(null)
const showSnackbar = ref(false)
const snackbarMessage = ref('')

const dataTypes = ['Whole Slide Images', 'Feature Vectors', 'Annotations', 'Clinical Data', 'Synthetic']
const statusOptions = ['active', 'processing', 'archived', 'pending']

// Mock datasets data
const datasets = ref([
  {
    id: 'ds-001',
    name: 'Lymph Node WSI Collection A',
    source: 'BBMRI-AT / Medical University of Graz',
    description: 'Primary lymph node whole-slide images for colorectal cancer analysis.',
    fullDescription: 'Comprehensive collection of digitized lymph node tissue sections from colorectal cancer patients. Scanned at 40x magnification with Hamamatsu scanners. Includes H&E stained sections with associated clinical metadata including TNM staging and survival outcomes.',
    type: 'Whole Slide Images',
    wsiCount: 15000,
    size: '18.5 TB',
    status: 'active',
    primaryStorage: 'MUG',
    storageLocation: 'MUSICA HPC Storage',
    projects: [
      { id: 'proj-uc7-001', name: 'CRC Prediction Study', shortName: 'UC7-CRC', useCase: 'UC7', role: 'Training Data' },
      { id: 'proj-uc7-002', name: 'XAI Validation', shortName: 'UC7-XAI', useCase: 'UC7', role: 'Validation Data' }
    ],
    metadata: {
      scannerType: 'Hamamatsu NanoZoomer',
      magnification: '40x',
      fileFormat: 'NDPI',
      staining: 'H&E',
      acquisitionDate: '2022-2024'
    }
  },
  {
    id: 'ds-002',
    name: 'Lymph Node WSI Collection B',
    source: 'MMCI (Masaryk Memorial Cancer Institute)',
    description: 'Secondary lymph node collection for model validation and testing.',
    fullDescription: 'External validation cohort of lymph node whole-slide images from MMCI. Used for independent model validation and generalization testing across different scanners and staining protocols.',
    type: 'Whole Slide Images',
    wsiCount: 8500,
    size: '10.2 TB',
    status: 'active',
    primaryStorage: 'BBMRI-ERIC WSI Repository',
    storageLocation: 'MUG-SX Storage',
    projects: [
      { id: 'proj-uc7-001', name: 'CRC Prediction Study', shortName: 'UC7-CRC', useCase: 'UC7', role: 'Validation Data' }
    ],
    metadata: {
      scannerType: 'Aperio GT450',
      magnification: '40x',
      fileFormat: 'SVS',
      staining: 'H&E',
      acquisitionDate: '2021-2023'
    }
  },
  {
    id: 'ds-004',
    name: 'Training Set Alpha',
    source: 'Medical University of Graz',
    description: 'Curated training dataset for synthetic image generation models.',
    fullDescription: 'Carefully curated subset of high-quality WSIs selected for training generative models. Includes diverse tissue types and staining variations to ensure model robustness.',
    type: 'Whole Slide Images',
    wsiCount: 5000,
    size: '6.2 TB',
    status: 'active',
    primaryStorage: 'MUG',
    storageLocation: 'MUSICA HPC Storage',
    projects: [
      { id: 'proj-uc8-001', name: 'Synthetic WSI Pipeline', shortName: 'UC8-Synth', useCase: 'UC8', role: 'Training Data' }
    ],
    metadata: {
      scannerType: 'Mixed',
      magnification: '40x',
      fileFormat: 'TIFF',
      staining: 'H&E',
      curationStatus: 'Quality Verified'
    }
  },
  {
    id: 'ds-005',
    name: 'Synthetic WSI Output v1',
    source: 'Generated by PathGAN-XL',
    description: 'First generation of synthetic whole-slide images for validation.',
    fullDescription: 'Synthetic whole-slide images generated using the PathGAN-XL model. These images are designed to preserve diagnostic features while ensuring complete privacy. Used for model pre-training and data augmentation.',
    type: 'Synthetic',
    wsiCount: 10000,
    size: '12.8 TB',
    status: 'processing',
    primaryStorage: 'MUG',
    storageLocation: 'MUSICA HPC Storage',
    projects: [
      { id: 'proj-uc8-001', name: 'Synthetic WSI Pipeline', shortName: 'UC8-Synth', useCase: 'UC8', role: 'Generated Output' },
      { id: 'proj-uc7-001', name: 'CRC Prediction Study', shortName: 'UC7-CRC', useCase: 'UC7', role: 'Augmentation Data' }
    ],
    metadata: {
      generatorModel: 'PathGAN-XL v3.0',
      resolution: '1024x1024 tiles',
      generationDate: '2024-12',
      qualityScore: '0.92'
    }
  },
])

const tableHeaders = [
  { title: 'Dataset', key: 'name', width: '280px' },
  { title: 'Type', key: 'type', width: '150px' },
  { title: 'WSIs', key: 'wsiCount', width: '100px' },
  { title: 'Size', key: 'size', width: '100px' },
  { title: 'Projects', key: 'projects', width: '180px' },
  { title: 'Status', key: 'status', width: '110px' },
  { title: 'Actions', key: 'actions', width: '100px', sortable: false }
]

// Computed
const filteredDatasets = computed(() => {
  return datasets.value.filter(dataset => {
    // Project filter from sidebar
    if (projectsStore.selectedProjectId) {
      const hasProject = dataset.projects.some(p => p.id === projectsStore.selectedProjectId)
      if (!hasProject) return false
    }

    // Search filter
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      const matches = 
        dataset.name.toLowerCase().includes(query) ||
        dataset.source.toLowerCase().includes(query) ||
        dataset.description.toLowerCase().includes(query)
      if (!matches) return false
    }

    // Type filter
    if (typeFilter.value && dataset.type !== typeFilter.value) return false

    // Status filter
    if (statusFilter.value && dataset.status !== statusFilter.value) return false

    return true
  })
})

const totalWsiCount = computed(() => {
  const total = filteredDatasets.value.reduce((sum, ds) => sum + ds.wsiCount, 0)
  return formatNumber(total)
})

const totalSize = computed(() => {
  let totalTB = 0
  filteredDatasets.value.forEach(ds => {
    const match = ds.size.match(/([\d.]+)\s*(TB|GB)/)
    if (match) {
      const value = parseFloat(match[1])
      const unit = match[2]
      totalTB += unit === 'TB' ? value : value / 1024
    }
  })
  return totalTB >= 1 ? `${totalTB.toFixed(1)} TB` : `${(totalTB * 1024).toFixed(0)} GB`
})

const activeDatasets = computed(() => {
  return filteredDatasets.value.filter(ds => ds.status === 'active').length
})

// Methods
function getTypeIcon(type) {
  const icons = {
    'Whole Slide Images': 'mdi-image-area',
    'Feature Vectors': 'mdi-vector-polyline',
    'Annotations': 'mdi-draw',
    'Clinical Data': 'mdi-clipboard-text',
    'Synthetic': 'mdi-creation'
  }
  return icons[type] || 'mdi-database'
}

function getStatusColor(status) {
  const colors = {
    active: 'success',
    processing: 'info',
    archived: 'grey',
    pending: 'warning'
  }
  return colors[status] || 'default'
}

function formatNumber(num) {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

function formatLabel(key) {
  return key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())
}

function openDatasetDetails(dataset) {
  selectedDataset.value = dataset
  showDetailsDialog.value = true
}

function viewStats(dataset) {
  showSnackbar.value = true
  snackbarMessage.value = `Opening statistics for "${dataset.name}"...`
  showDetailsDialog.value = false
}
</script>

<style scoped lang="scss">
// View-specific stat card icons
.stat-icon {
  &.size {
    background: rgba(139, 92, 246, 0.15);
    color: #8b5cf6;
  }
}

.stat-label {
  font-size: 0.8125rem;
  color: #94a3b8;
}

// Filters
.filters-card {
  background: rgba(30, 41, 59, 0.5) !important;
  border: 1px solid rgba(51, 65, 85, 0.5);
}

// Datasets Grid
.datasets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.25rem;
}

.dataset-card {
  background: rgba(30, 41, 59, 0.5) !important;
  border: 1px solid rgba(51, 65, 85, 0.5);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    border-color: rgba(230, 152, 48, 0.3);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1rem 0;
}

.dataset-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(230, 152, 48, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-body {
  padding: 1rem !important;
}

.dataset-name {
  font-size: 1rem;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 0.25rem;
}

.dataset-source {
  font-size: 0.75rem;
  color: #E69830;
  margin-bottom: 0.5rem;
}

.dataset-description {
  font-size: 0.8125rem;
  color: #94a3b8;
  line-height: 1.5;
  margin-bottom: 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.dataset-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #64748b;
}

.storage-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.6875rem;
  background: rgba(100, 116, 139, 0.15);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  margin-bottom: 0.75rem;
  
  .v-icon {
    color: #64748b;
  }
  
  .storage-label {
    color: #64748b;
  }
  
  .storage-value {
    color: #e2e8f0;
    font-weight: 500;
  }
}

.projects-section {
  .projects-label {
    font-size: 0.6875rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: block;
    margin-bottom: 0.375rem;
  }
}

.projects-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.project-chip {
  font-size: 0.625rem !important;
}

.card-actions {
  padding: 0.75rem 1rem !important;
}

// Table
.table-card {
  background: rgba(30, 41, 59, 0.5) !important;
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.datasets-table {
  background: transparent !important;
  
  :deep(.v-data-table__tr) {
    cursor: pointer;
    
    &:hover {
      background: rgba(230, 152, 48, 0.05) !important;
    }
  }
}

.name-cell {
  display: flex;
  align-items: center;
}

.dataset-name-text {
  display: block;
  font-weight: 500;
  color: #f1f5f9;
}

.dataset-source-text {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
}

.projects-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

// Dialog
.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.25rem;
  
  h2 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #f1f5f9;
  }
}

.header-info {
  display: flex;
  align-items: center;
}

.source-text {
  font-size: 0.875rem;
  color: #E69830;
}

.dialog-content {
  padding: 1.25rem !important;
  max-height: 60vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.description-text {
  color: #94a3b8;
  line-height: 1.6;
}

.detail-item {
  .detail-label {
    display: block;
    font-size: 0.6875rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
  }
  
  .detail-value {
    color: #e2e8f0;
    font-size: 0.9375rem;
  }
}

.storage-info {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
  color: #94a3b8;
  
  .v-icon {
    color: #E69830;
  }
}

.projects-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.project-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
}

.project-badge {
  padding: 0.25rem 0.5rem;
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

.project-info {
  flex: 1;
  
  .project-name {
    display: block;
    font-weight: 500;
    color: #f1f5f9;
    font-size: 0.875rem;
  }
  
  .project-role {
    display: block;
    font-size: 0.75rem;
    color: #64748b;
  }
}

.metadata-item {
  padding: 0.5rem;
  background: rgba(15, 23, 42, 0.3);
  border-radius: 6px;
  
  .metadata-label {
    display: block;
    font-size: 0.6875rem;
    color: #64748b;
    margin-bottom: 0.25rem;
  }
  
  .metadata-value {
    color: #e2e8f0;
    font-size: 0.8125rem;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
}

</style>
