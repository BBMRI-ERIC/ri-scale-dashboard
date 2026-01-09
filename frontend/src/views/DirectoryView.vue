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
              <v-icon class="title-icon">mdi-database-search</v-icon>
              BBMRI-ERIC Directory
            </h1>
            <p class="page-subtitle">
              Discover biomedical datasets and request compute access
            </p>
          </div>
        </div>

        <!-- Search & Filters -->
        <v-card class="search-card glass mb-6">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="searchQuery"
                  prepend-inner-icon="mdi-magnify"
                  placeholder="Search datasets, biobanks, or collections..."
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  clearable
                  class="search-field"
                />
              </v-col>
              <v-col cols="12" md="2">
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
              <v-col cols="12" md="2">
                <v-select
                  v-model="countryFilter"
                  :items="countries"
                  label="Country"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  clearable
                />
              </v-col>
              <v-col cols="12" md="2">
                <v-select
                  v-model="computeFilter"
                  :items="computeOptions"
                  label="Compute Access"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  clearable
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Results Summary -->
        <div class="results-summary mb-4">
          <span class="results-count">{{ filteredDatasets.length }} datasets found</span>
          <div class="view-toggle">
            <v-btn-toggle v-model="viewMode" mandatory density="comfortable">
              <v-btn value="grid" icon="mdi-view-grid" size="small" />
              <v-btn value="list" icon="mdi-view-list" size="small" />
            </v-btn-toggle>
          </div>
        </div>

        <!-- Dataset Grid View -->
        <div v-if="viewMode === 'grid'" class="datasets-grid">
          <v-card
            v-for="dataset in filteredDatasets"
            :key="dataset.id"
            class="dataset-card glass"
            @click="openDatasetDetails(dataset)"
          >
            <div class="card-header">
              <div class="biobank-logo">
                <v-icon size="32" :color="dataset.computeEnabled ? 'primary' : 'grey'">
                  {{ getDataTypeIcon(dataset.dataType) }}
                </v-icon>
              </div>
            </div>
            
            <v-card-text class="card-body">
              <h3 class="dataset-name">{{ dataset.name }}</h3>
              <p class="dataset-biobank">{{ dataset.biobank }}</p>
              <p class="dataset-description">{{ dataset.description }}</p>
              
              <div class="dataset-meta">
                <div class="meta-item">
                  <v-icon size="14">mdi-map-marker</v-icon>
                  <span>{{ dataset.country }}</span>
                </div>
                <div class="meta-item">
                  <v-icon size="14">mdi-database</v-icon>
                  <span>{{ dataset.sampleCount.toLocaleString() }} samples</span>
                </div>
              </div>

              <div class="dataset-tags">
                <v-chip
                  v-for="tag in dataset.tags.slice(0, 3)"
                  :key="tag"
                  size="x-small"
                  variant="tonal"
                  class="tag-chip"
                >
                  {{ tag }}
                </v-chip>
              </div>
            </v-card-text>

            <v-divider />

            <v-card-actions class="card-actions">
              <v-btn
                variant="text"
                size="small"
                @click.stop="openDatasetDetails(dataset)"
              >
                View Details
              </v-btn>
              <v-spacer />
              <v-btn
                v-if="dataset.computeEnabled"
                color="primary"
                variant="tonal"
                size="small"
                @click.stop="requestCompute(dataset)"
              >
                <v-icon size="16" class="mr-1">mdi-server</v-icon>
                Request Compute
              </v-btn>
              <v-btn
                v-else
                variant="tonal"
                size="small"
                @click.stop="requestAccess(dataset)"
              >
                <v-icon size="16" class="mr-1">mdi-file-document-edit</v-icon>
                Request Access
              </v-btn>
            </v-card-actions>
          </v-card>
        </div>

        <!-- Dataset List View -->
        <v-card v-else class="list-card glass">
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
                <v-icon size="20" :color="item.computeEnabled ? 'primary' : 'grey'" class="mr-2">
                  {{ getDataTypeIcon(item.dataType) }}
                </v-icon>
                <div>
                  <span class="dataset-name-text">{{ item.name }}</span>
                  <span class="dataset-biobank-text">{{ item.biobank }}</span>
                </div>
              </div>
            </template>

            <template v-slot:item.sampleCount="{ item }">
              <span class="font-mono">{{ item.sampleCount.toLocaleString() }}</span>
            </template>

            <template v-slot:item.computeEnabled="{ item }">
              <v-chip
                :color="item.computeEnabled ? 'primary' : 'grey'"
                size="small"
                variant="tonal"
              >
                {{ item.computeEnabled ? 'SPE Available' : 'Data Only' }}
              </v-chip>
            </template>

            <template v-slot:item.actions="{ item }">
              <v-btn
                v-if="item.computeEnabled"
                color="primary"
                variant="tonal"
                size="small"
                @click.stop="requestCompute(item)"
              >
                Request Compute
              </v-btn>
              <v-btn
                v-else
                variant="tonal"
                size="small"
                @click.stop="requestAccess(item)"
              >
                Request Access
              </v-btn>
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
            <v-icon size="28" :color="selectedDataset.computeEnabled ? 'primary' : 'grey'" class="mr-3">
              {{ getDataTypeIcon(selectedDataset.dataType) }}
            </v-icon>
            <div>
              <h2>{{ selectedDataset.name }}</h2>
              <span class="biobank-name">{{ selectedDataset.biobank }}</span>
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

          <v-row class="detail-grid">
            <v-col cols="6" md="3">
              <div class="detail-item">
                <span class="detail-label">Data Type</span>
                <span class="detail-value">{{ selectedDataset.dataType }}</span>
              </div>
            </v-col>
            <v-col cols="6" md="3">
              <div class="detail-item">
                <span class="detail-label">Country</span>
                <span class="detail-value">{{ selectedDataset.country }}</span>
              </div>
            </v-col>
            <v-col cols="6" md="3">
              <div class="detail-item">
                <span class="detail-label">Samples</span>
                <span class="detail-value font-mono">{{ selectedDataset.sampleCount.toLocaleString() }}</span>
              </div>
            </v-col>
            <v-col cols="6" md="3">
              <div class="detail-item">
                <span class="detail-label">Data Size</span>
                <span class="detail-value font-mono">{{ selectedDataset.dataSize }}</span>
              </div>
            </v-col>
          </v-row>

          <div class="detail-section">
            <h4 class="section-title">Compute Capabilities</h4>
            <div v-if="selectedDataset.computeEnabled" class="compute-info">
              <v-chip color="primary" variant="tonal" class="mr-2 mb-2">
                <v-icon size="16" class="mr-1">mdi-check-circle</v-icon>
                SPE Access Available
              </v-chip>
              <div class="hpc-sites mt-3">
                <span class="sites-label">Available HPC Sites:</span>
                <div class="sites-list">
                  <v-chip
                    v-for="site in selectedDataset.hpcSites"
                    :key="site"
                    size="small"
                    variant="outlined"
                    class="mr-2"
                  >
                    {{ site }}
                  </v-chip>
                </div>
              </div>
            </div>
            <div v-else class="no-compute">
              <v-icon color="grey" class="mr-2">mdi-server-off</v-icon>
              <span>This dataset does not currently offer SPE compute access. You can request data access only.</span>
            </div>
          </div>

          <div class="detail-section">
            <h4 class="section-title">Access Requirements</h4>
            <v-list density="compact" class="requirements-list">
              <v-list-item v-for="req in selectedDataset.accessRequirements" :key="req">
                <template v-slot:prepend>
                  <v-icon size="18" color="primary">mdi-check</v-icon>
                </template>
                <v-list-item-title>{{ req }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </div>

          <div class="detail-section">
            <h4 class="section-title">Tags</h4>
            <div class="tags-container">
              <v-chip
                v-for="tag in selectedDataset.tags"
                :key="tag"
                size="small"
                variant="tonal"
                class="mr-2 mb-2"
              >
                {{ tag }}
              </v-chip>
            </div>
          </div>
        </v-card-text>

        <v-divider />

        <div class="dialog-footer">
          <v-btn variant="text" @click="showDetailsDialog = false">Close</v-btn>
          <v-btn
            v-if="selectedDataset.computeEnabled"
            color="primary"
            @click="requestCompute(selectedDataset)"
          >
            <v-icon size="18" class="mr-1">mdi-server</v-icon>
            Request Compute Access
          </v-btn>
          <v-btn
            v-else
            color="primary"
            variant="tonal"
            @click="requestAccess(selectedDataset)"
          >
            <v-icon size="18" class="mr-1">mdi-file-document-edit</v-icon>
            Request Data Access
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- Request Compute Dialog -->
    <v-dialog v-model="showRequestDialog" max-width="600">
      <v-card class="request-dialog glass" v-if="datasetToRequest">
        <div class="dialog-header">
          <h2>Request Compute Access</h2>
          <v-btn icon="mdi-close" variant="text" size="small" @click="showRequestDialog = false" />
        </div>
        <v-divider />
        <v-card-text class="dialog-content">
          <v-alert type="info" variant="tonal" class="mb-4">
            You are requesting compute access to <strong>{{ datasetToRequest.name }}</strong> from {{ datasetToRequest.biobank }}.
            This will be processed through the BBMRI-ERIC Negotiator.
          </v-alert>

          <v-form ref="requestFormRef">
            <v-text-field
              v-model="requestForm.projectTitle"
              label="Project Title"
              placeholder="e.g., CRC Biomarker Analysis"
              variant="outlined"
              :rules="[v => !!v || 'Project title is required']"
              class="mb-4"
            />

            <v-textarea
              v-model="requestForm.description"
              label="Project Description"
              placeholder="Describe your research project and how you plan to use this data..."
              variant="outlined"
              rows="3"
              :rules="[v => !!v || 'Description is required']"
              class="mb-4"
            />

            <v-select
              v-model="requestForm.hpcSite"
              :items="datasetToRequest.hpcSites || []"
              label="Preferred HPC Site"
              variant="outlined"
              :rules="[v => !!v || 'HPC site is required']"
              class="mb-4"
            />

            <v-select
              v-model="requestForm.duration"
              :items="durationOptions"
              label="Requested Access Duration"
              variant="outlined"
              :rules="[v => !!v || 'Duration is required']"
              class="mb-4"
            />

            <v-checkbox
              v-model="requestForm.ethicsApproved"
              label="I confirm ethics approval has been obtained for this research"
              color="primary"
              :rules="[v => !!v || 'Ethics confirmation is required']"
            />
          </v-form>
        </v-card-text>
        <v-divider />
        <div class="dialog-footer">
          <v-btn variant="text" @click="showRequestDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="submitRequest" :loading="isSubmitting">
            Submit to Negotiator
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- Success Snackbar -->
    <v-snackbar v-model="showSuccessSnackbar" color="success" :timeout="4000">
      {{ successMessage }}
      <template v-slot:actions>
        <v-btn variant="text" @click="showSuccessSnackbar = false">Close</v-btn>
      </template>
    </v-snackbar>
  </v-layout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const router = useRouter()

const sidebarRail = ref(false)
const viewMode = ref('grid')
const searchQuery = ref('')
const typeFilter = ref(null)
const countryFilter = ref(null)
const computeFilter = ref(null)
const showDetailsDialog = ref(false)
const showRequestDialog = ref(false)
const selectedDataset = ref(null)
const datasetToRequest = ref(null)
const isSubmitting = ref(false)
const showSuccessSnackbar = ref(false)
const successMessage = ref('')
const requestFormRef = ref(null)

const requestForm = ref({
  projectTitle: '',
  description: '',
  hpcSite: null,
  duration: null,
  ethicsApproved: false
})

// Filter options
const dataTypes = ['Whole Slide Images', 'Genomic Data', 'Clinical Data', 'Tissue Samples', 'Imaging Data']
const countries = ['Austria', 'Germany', 'Italy', 'Netherlands', 'Finland', 'Czech Republic']
const computeOptions = [
  { title: 'SPE Available', value: true },
  { title: 'Data Only', value: false }
]
const durationOptions = ['3 months', '6 months', '12 months', '24 months']

// Mock datasets
const datasets = ref([
  {
    id: 'ds-bbmri-at-001',
    name: 'Austrian CRC Lymph Node Collection',
    biobank: 'BBMRI-AT / Medical University of Graz',
    description: 'Comprehensive collection of lymph node whole-slide images from colorectal cancer patients.',
    fullDescription: 'This collection contains over 3,000 digitized whole-slide images (WSIs) of lymph node tissue sections from colorectal cancer patients. The dataset includes associated clinical metadata such as TNM staging, survival outcomes, and treatment history. Images are scanned at 40x magnification with an average resolution of 100,000 x 100,000 pixels per slide.',
    dataType: 'Whole Slide Images',
    country: 'Austria',
    sampleCount: 3200,
    dataSize: '45 TB',
    computeEnabled: true,
    hpcSites: ['MUSICA', 'MUG-SX'],
    tags: ['Pathology', 'CRC', 'Lymph Nodes', 'WSI', 'AI-Ready'],
    accessRequirements: [
      'Ethics committee approval',
      'Data Transfer Agreement (DTA)',
      'Institutional affiliation verification',
      'Research project description'
    ]
  },
  {
    id: 'ds-bbmri-at-002',
    name: 'MUG Synthetic Pathology Training Set',
    biobank: 'Medical University of Graz',
    description: 'High-quality synthetic whole-slide images for AI model training and validation.',
    fullDescription: 'A curated collection of synthetically generated whole-slide images designed for training and benchmarking computational pathology algorithms. Generated using state-of-the-art diffusion models, these images maintain statistical properties of real tissue while being free from privacy constraints.',
    dataType: 'Whole Slide Images',
    country: 'Austria',
    sampleCount: 5000,
    dataSize: '12 TB',
    computeEnabled: true,
    hpcSites: ['MUSICA'],
    tags: ['Synthetic', 'AI Training', 'Pathology', 'Benchmark'],
    accessRequirements: [
      'Research project description',
      'Institutional affiliation verification'
    ]
  },
  {
    id: 'ds-bbmri-de-001',
    name: 'German Breast Cancer Genomics Cohort',
    biobank: 'BBMRI-DE / Charité Berlin',
    description: 'Multi-omics dataset including genomic, transcriptomic, and clinical data from breast cancer patients.',
    fullDescription: 'Comprehensive multi-omics dataset from a cohort of 1,500 breast cancer patients. Includes whole-genome sequencing, RNA-seq, and detailed clinical annotations including treatment response and long-term outcomes.',
    dataType: 'Genomic Data',
    country: 'Germany',
    sampleCount: 1500,
    dataSize: '8 TB',
    computeEnabled: true,
    hpcSites: ['MUSICA', 'MUG-SX'],
    tags: ['Genomics', 'Breast Cancer', 'Multi-omics', 'WGS'],
    accessRequirements: [
      'Ethics committee approval',
      'Data Transfer Agreement (DTA)',
      'Institutional affiliation verification',
      'Research project description',
      'Data protection impact assessment (DPIA)'
    ]
  },
  {
    id: 'ds-bbmri-it-001',
    name: 'Italian Melanoma Imaging Archive',
    biobank: 'BBMRI-IT / University of Milan',
    description: 'Dermoscopy and histopathology images from melanoma cases with expert annotations.',
    fullDescription: 'A comprehensive imaging archive containing paired dermoscopy and histopathology images from confirmed melanoma cases. All images include expert annotations marking regions of interest and diagnostic features.',
    dataType: 'Imaging Data',
    country: 'Italy',
    sampleCount: 2800,
    dataSize: '6 TB',
    computeEnabled: false,
    hpcSites: [],
    tags: ['Melanoma', 'Dermoscopy', 'Histopathology', 'Annotated'],
    accessRequirements: [
      'Ethics committee approval',
      'Data Transfer Agreement (DTA)',
      'Research project description'
    ]
  },
  {
    id: 'ds-bbmri-nl-001',
    name: 'Dutch Prostate Cancer Clinical Registry',
    biobank: 'BBMRI-NL / Erasmus MC',
    description: 'Longitudinal clinical data from prostate cancer patients including treatment outcomes.',
    fullDescription: 'A clinical registry containing detailed longitudinal data from over 8,000 prostate cancer patients. Includes diagnosis information, treatment protocols, PSA measurements over time, quality of life assessments, and survival outcomes.',
    dataType: 'Clinical Data',
    country: 'Netherlands',
    sampleCount: 8500,
    dataSize: '500 GB',
    computeEnabled: true,
    hpcSites: ['MUSICA'],
    tags: ['Prostate Cancer', 'Clinical', 'Longitudinal', 'Registry'],
    accessRequirements: [
      'Ethics committee approval',
      'Data Transfer Agreement (DTA)',
      'Institutional affiliation verification',
      'Research project description'
    ]
  },
  {
    id: 'ds-bbmri-fi-001',
    name: 'Finnish Biobank Tissue Collection',
    biobank: 'BBMRI-FI / Helsinki Biobank',
    description: 'FFPE tissue samples with linked genomic and clinical data from various cancer types.',
    fullDescription: 'A comprehensive tissue biobank containing FFPE samples from multiple cancer types. Each sample is linked to genomic profiling data and detailed clinical records from the Finnish healthcare system.',
    dataType: 'Tissue Samples',
    country: 'Finland',
    sampleCount: 15000,
    dataSize: 'Physical samples + 2 TB metadata',
    computeEnabled: false,
    hpcSites: [],
    tags: ['FFPE', 'Multi-cancer', 'Tissue Bank', 'Linked Data'],
    accessRequirements: [
      'Ethics committee approval',
      'Material Transfer Agreement (MTA)',
      'Data Transfer Agreement (DTA)',
      'Research project description',
      'Sample handling protocol'
    ]
  },
  {
    id: 'ds-bbmri-cz-001',
    name: 'Czech Lung Cancer Screening Dataset',
    biobank: 'BBMRI-CZ / Masaryk Memorial Cancer Institute',
    description: 'CT scans and clinical data from a national lung cancer screening program.',
    fullDescription: 'Low-dose CT scans from participants in the Czech national lung cancer screening program. Includes baseline and follow-up scans with radiologist annotations, smoking history, and outcome data.',
    dataType: 'Imaging Data',
    country: 'Czech Republic',
    sampleCount: 12000,
    dataSize: '25 TB',
    computeEnabled: true,
    hpcSites: ['MUSICA', 'MUG-SX'],
    tags: ['Lung Cancer', 'CT', 'Screening', 'Longitudinal'],
    accessRequirements: [
      'Ethics committee approval',
      'Data Transfer Agreement (DTA)',
      'Institutional affiliation verification',
      'Research project description'
    ]
  }
])

const tableHeaders = [
  { title: 'Dataset', key: 'name', width: '300px' },
  { title: 'Data Type', key: 'dataType', width: '150px' },
  { title: 'Country', key: 'country', width: '120px' },
  { title: 'Samples', key: 'sampleCount', width: '120px' },
  { title: 'Compute', key: 'computeEnabled', width: '140px' },
  { title: 'Actions', key: 'actions', width: '160px', sortable: false }
]

const filteredDatasets = computed(() => {
  return datasets.value.filter(dataset => {
    // Search filter
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      const matchesSearch = 
        dataset.name.toLowerCase().includes(query) ||
        dataset.biobank.toLowerCase().includes(query) ||
        dataset.description.toLowerCase().includes(query) ||
        dataset.tags.some(tag => tag.toLowerCase().includes(query))
      if (!matchesSearch) return false
    }

    // Type filter
    if (typeFilter.value && dataset.dataType !== typeFilter.value) return false

    // Country filter
    if (countryFilter.value && dataset.country !== countryFilter.value) return false

    // Compute filter
    if (computeFilter.value !== null && dataset.computeEnabled !== computeFilter.value) return false

    return true
  })
})

function getDataTypeIcon(type) {
  const icons = {
    'Whole Slide Images': 'mdi-image-area',
    'Genomic Data': 'mdi-dna',
    'Clinical Data': 'mdi-clipboard-text',
    'Tissue Samples': 'mdi-flask',
    'Imaging Data': 'mdi-radiobox-marked'
  }
  return icons[type] || 'mdi-database'
}

function openDatasetDetails(dataset) {
  selectedDataset.value = dataset
  showDetailsDialog.value = true
}

function requestCompute(dataset) {
  datasetToRequest.value = dataset
  showDetailsDialog.value = false
  showRequestDialog.value = true
}

function requestAccess(dataset) {
  // For non-compute datasets, redirect to Negotiator (placeholder)
  showSuccessSnackbar.value = true
  successMessage.value = `Redirecting to BBMRI-ERIC Negotiator for "${dataset.name}"...`
  showDetailsDialog.value = false
}

async function submitRequest() {
  const { valid } = await requestFormRef.value.validate()
  if (!valid) return

  isSubmitting.value = true
  
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  isSubmitting.value = false
  showRequestDialog.value = false
  showSuccessSnackbar.value = true
  successMessage.value = `Request submitted to BBMRI-ERIC Negotiator for "${datasetToRequest.value.name}"`
  
  // Reset form
  requestForm.value = {
    projectTitle: '',
    description: '',
    hpcSite: null,
    duration: null,
    ethicsApproved: false
  }
}
</script>

<style scoped lang="scss">
// View-specific styles
.search-field {
  :deep(.v-field) {
    background: rgba(15, 23, 42, 0.5);
  }
}

// Results summary
.results-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.results-count {
  color: #94a3b8;
  font-size: 0.875rem;
}

// Dataset Grid
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
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 1rem 0;
}

.biobank-logo {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.8);
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
  line-height: 1.3;
}

.dataset-biobank {
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

.dataset-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #64748b;
  
  .v-icon {
    color: #64748b;
  }
}

.dataset-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.tag-chip {
  font-size: 0.625rem !important;
  height: 20px !important;
}

.card-actions {
  padding: 0.75rem 1rem !important;
}

// List view
.list-card {
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

.dataset-biobank-text {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
}

// Dialogs
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
  
  .biobank-name {
    font-size: 0.875rem;
    color: #E69830;
  }
}

.dialog-content {
  padding: 1.25rem !important;
  max-height: 60vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 1.5rem;
  
  &:last-child {
    margin-bottom: 0;
  }
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

.detail-grid {
  margin-bottom: 1.5rem;
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

.compute-info {
  background: rgba(230, 152, 48, 0.05);
  border: 1px solid rgba(230, 152, 48, 0.2);
  border-radius: 8px;
  padding: 1rem;
}

.hpc-sites {
  .sites-label {
    font-size: 0.8125rem;
    color: #94a3b8;
    display: block;
    margin-bottom: 0.5rem;
  }
}

.no-compute {
  display: flex;
  align-items: center;
  color: #94a3b8;
  font-size: 0.875rem;
  background: rgba(100, 116, 139, 0.1);
  padding: 1rem;
  border-radius: 8px;
}

.requirements-list {
  background: transparent !important;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
}

</style>
