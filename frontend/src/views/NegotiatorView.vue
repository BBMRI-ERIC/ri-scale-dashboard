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
              <v-icon class="title-icon">mdi-handshake</v-icon>
              BBMRI-ERIC Negotiator
            </h1>
            <p class="page-subtitle">
              Request and manage access to biobank datasets
            </p>
          </div>
          <v-btn color="primary" @click="openNewRequest">
            <v-icon class="mr-2">mdi-plus</v-icon>
            New Request
          </v-btn>
        </div>

        <!-- Stats Cards -->
        <v-row class="mb-6">
          <v-col cols="12" sm="6" md="3">
            <v-card class="stat-card glass">
              <v-card-text>
                <div class="stat-icon pending">
                  <v-icon>mdi-clock-outline</v-icon>
                </div>
                <div class="stat-info">
                  <span class="stat-value">{{ pendingCount }}</span>
                  <span class="stat-label">Pending</span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card class="stat-card glass">
              <v-card-text>
                <div class="stat-icon review">
                  <v-icon>mdi-file-search</v-icon>
                </div>
                <div class="stat-info">
                  <span class="stat-value">{{ inReviewCount }}</span>
                  <span class="stat-label">In Review</span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card class="stat-card glass">
              <v-card-text>
                <div class="stat-icon approved">
                  <v-icon>mdi-check-circle</v-icon>
                </div>
                <div class="stat-info">
                  <span class="stat-value">{{ approvedCount }}</span>
                  <span class="stat-label">Approved</span>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card class="stat-card glass">
              <v-card-text>
                <div class="stat-icon rejected">
                  <v-icon>mdi-close-circle</v-icon>
                </div>
                <div class="stat-info">
                  <span class="stat-value">{{ rejectedCount }}</span>
                  <span class="stat-label">Rejected</span>
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
                  placeholder="Search requests..."
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
              <v-col cols="12" md="3">
                <v-select
                  v-model="typeFilter"
                  :items="requestTypes"
                  label="Request Type"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  clearable
                />
              </v-col>
              <v-col cols="12" md="2" class="text-right">
                <v-btn-toggle v-model="viewMode" mandatory density="comfortable">
                  <v-btn value="cards" icon="mdi-view-grid" size="small" />
                  <v-btn value="table" icon="mdi-view-list" size="small" />
                </v-btn-toggle>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Requests Cards View -->
        <div v-if="viewMode === 'cards'" class="requests-grid">
          <v-card
            v-for="request in filteredRequests"
            :key="request.id"
            class="request-card glass"
            @click="openRequestDetails(request)"
          >
            <div class="card-status-bar" :class="request.status" />
            
            <v-card-text class="card-content">
              <div class="card-header">
                <v-chip
                  :color="getStatusColor(request.status)"
                  size="small"
                  variant="tonal"
                >
                  {{ formatStatus(request.status) }}
                </v-chip>
                <span class="request-id font-mono">{{ request.id }}</span>
              </div>

              <h3 class="request-title">{{ request.projectTitle }}</h3>
              <p class="request-description">{{ request.description }}</p>

              <div class="request-meta">
                <div class="meta-item">
                  <v-icon size="14">mdi-database</v-icon>
                  <span>{{ request.datasets.length }} dataset(s)</span>
                </div>
                <div class="meta-item">
                  <v-icon size="14">mdi-calendar</v-icon>
                  <span>{{ formatDate(request.submittedAt) }}</span>
                </div>
              </div>

              <div class="datasets-preview">
                <v-chip
                  v-for="dataset in request.datasets.slice(0, 2)"
                  :key="dataset"
                  size="x-small"
                  variant="outlined"
                  class="mr-1 mb-1"
                >
                  {{ dataset }}
                </v-chip>
                <v-chip
                  v-if="request.datasets.length > 2"
                  size="x-small"
                  variant="tonal"
                >
                  +{{ request.datasets.length - 2 }} more
                </v-chip>
              </div>

              <!-- Progress Steps -->
              <div class="progress-steps" v-if="request.status !== 'draft'">
                <div 
                  v-for="(step, index) in progressSteps" 
                  :key="step.key"
                  class="step"
                  :class="{ 
                    completed: isStepCompleted(request, step.key),
                    current: isStepCurrent(request, step.key)
                  }"
                >
                  <div class="step-indicator">
                    <v-icon v-if="isStepCompleted(request, step.key)" size="12">mdi-check</v-icon>
                    <span v-else>{{ index + 1 }}</span>
                  </div>
                  <span class="step-label">{{ step.label }}</span>
                </div>
              </div>
            </v-card-text>

            <v-divider />

            <v-card-actions class="card-actions">
              <v-btn variant="text" size="small" @click.stop="openRequestDetails(request)">
                View Details
              </v-btn>
              <v-spacer />
              <v-btn
                v-if="request.status === 'draft'"
                color="primary"
                variant="tonal"
                size="small"
                @click.stop="submitRequest(request)"
              >
                Submit
              </v-btn>
              <v-btn
                v-if="request.status === 'approved'"
                color="primary"
                variant="tonal"
                size="small"
                @click.stop="goToProject(request)"
              >
                Open Project
              </v-btn>
            </v-card-actions>
          </v-card>
        </div>

        <!-- Requests Table View -->
        <v-card v-else class="table-card glass">
          <v-data-table
            :headers="tableHeaders"
            :items="filteredRequests"
            :items-per-page="10"
            class="requests-table"
            hover
            @click:row="(e, { item }) => openRequestDetails(item)"
          >
            <template v-slot:item.id="{ item }">
              <span class="font-mono request-id-cell">{{ item.id }}</span>
            </template>

            <template v-slot:item.projectTitle="{ item }">
              <div class="title-cell">
                <span class="title-text">{{ item.projectTitle }}</span>
                <span class="type-text">{{ item.requestType }}</span>
              </div>
            </template>

            <template v-slot:item.datasets="{ item }">
              <span>{{ item.datasets.length }} dataset(s)</span>
            </template>

            <template v-slot:item.status="{ item }">
              <v-chip
                :color="getStatusColor(item.status)"
                size="small"
                variant="tonal"
              >
                {{ formatStatus(item.status) }}
              </v-chip>
            </template>

            <template v-slot:item.submittedAt="{ item }">
              <span>{{ formatDate(item.submittedAt) }}</span>
            </template>

            <template v-slot:item.actions="{ item }">
              <v-btn
                icon="mdi-eye"
                variant="text"
                size="small"
                @click.stop="openRequestDetails(item)"
              />
              <v-btn
                v-if="item.status === 'approved'"
                icon="mdi-arrow-right"
                variant="text"
                size="small"
                color="primary"
                @click.stop="goToProject(item)"
              />
            </template>
          </v-data-table>
        </v-card>
      </div>
    </v-main>

    <!-- Request Details Dialog -->
    <v-dialog v-model="showDetailsDialog" max-width="900">
      <v-card class="details-dialog glass" v-if="selectedRequest">
        <div class="dialog-header">
          <div class="header-info">
            <v-chip
              :color="getStatusColor(selectedRequest.status)"
              variant="tonal"
              class="mr-3"
            >
              {{ formatStatus(selectedRequest.status) }}
            </v-chip>
            <div>
              <h2>{{ selectedRequest.projectTitle }}</h2>
              <span class="request-id-label font-mono">{{ selectedRequest.id }}</span>
            </div>
          </div>
          <v-btn icon="mdi-close" variant="text" size="small" @click="showDetailsDialog = false" />
        </div>
        
        <v-divider />
        
        <v-card-text class="dialog-content">
          <!-- Progress Timeline -->
          <div class="timeline-section" v-if="selectedRequest.status !== 'draft'">
            <h4 class="section-title">Request Progress</h4>
            <div class="timeline">
              <div 
                v-for="(step, index) in progressSteps" 
                :key="step.key"
                class="timeline-step"
                :class="{ 
                  completed: isStepCompleted(selectedRequest, step.key),
                  current: isStepCurrent(selectedRequest, step.key),
                  rejected: selectedRequest.status === 'rejected' && step.key === selectedRequest.currentStep
                }"
              >
                <div class="timeline-marker">
                  <v-icon v-if="isStepCompleted(selectedRequest, step.key)" size="16">mdi-check</v-icon>
                  <v-icon v-else-if="selectedRequest.status === 'rejected' && step.key === selectedRequest.currentStep" size="16">mdi-close</v-icon>
                  <span v-else>{{ index + 1 }}</span>
                </div>
                <div class="timeline-content">
                  <span class="timeline-label">{{ step.label }}</span>
                  <span class="timeline-date" v-if="selectedRequest.stepDates?.[step.key]">
                    {{ formatDate(selectedRequest.stepDates[step.key]) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Project Details -->
          <div class="detail-section">
            <h4 class="section-title">Project Details</h4>
            <div class="detail-grid">
              <div class="detail-item full">
                <span class="detail-label">Description</span>
                <p class="detail-value description">{{ selectedRequest.description }}</p>
              </div>
              <div class="detail-item">
                <span class="detail-label">Request Type</span>
                <span class="detail-value">{{ selectedRequest.requestType }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Requested Duration</span>
                <span class="detail-value">{{ selectedRequest.duration }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Submitted</span>
                <span class="detail-value">{{ formatDate(selectedRequest.submittedAt) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Last Updated</span>
                <span class="detail-value">{{ formatDate(selectedRequest.updatedAt) }}</span>
              </div>
            </div>
          </div>

          <!-- Datasets -->
          <div class="detail-section">
            <h4 class="section-title">Requested Datasets</h4>
            <div class="datasets-list">
              <div v-for="dataset in selectedRequest.datasetDetails" :key="dataset.id" class="dataset-item">
                <v-icon size="20" color="primary" class="mr-3">mdi-database</v-icon>
                <div class="dataset-info">
                  <span class="dataset-name">{{ dataset.name }}</span>
                  <span class="dataset-biobank">{{ dataset.biobank }}</span>
                </div>
                <v-chip size="x-small" variant="tonal">{{ dataset.samples }} samples</v-chip>
              </div>
            </div>
          </div>

          <!-- HPC Site -->
          <div class="detail-section" v-if="selectedRequest.hpcSite">
            <h4 class="section-title">Compute Resources</h4>
            <div class="hpc-info">
              <v-icon size="20" color="primary" class="mr-3">mdi-server</v-icon>
              <div>
                <span class="hpc-site">{{ selectedRequest.hpcSite }}</span>
                <span class="hpc-label">Selected HPC Site</span>
              </div>
            </div>
          </div>

          <!-- Documents -->
          <div class="detail-section">
            <h4 class="section-title">Documents</h4>
            <div class="documents-list">
              <div 
                v-for="doc in selectedRequest.documents" 
                :key="doc.name"
                class="document-item"
                :class="{ uploaded: doc.uploaded }"
              >
                <v-icon size="20" :color="doc.uploaded ? 'primary' : 'grey'">
                  {{ doc.uploaded ? 'mdi-file-check' : 'mdi-file-outline' }}
                </v-icon>
                <span class="doc-name">{{ doc.name }}</span>
                <v-chip 
                  size="x-small" 
                  :color="doc.uploaded ? 'success' : 'warning'"
                  variant="tonal"
                >
                  {{ doc.uploaded ? 'Uploaded' : 'Required' }}
                </v-chip>
              </div>
            </div>
          </div>

          <!-- Comments/Notes -->
          <div class="detail-section" v-if="selectedRequest.comments?.length">
            <h4 class="section-title">Comments</h4>
            <div class="comments-list">
              <div v-for="comment in selectedRequest.comments" :key="comment.id" class="comment-item">
                <div class="comment-header">
                  <span class="comment-author">{{ comment.author }}</span>
                  <span class="comment-date">{{ formatDate(comment.date) }}</span>
                </div>
                <p class="comment-text">{{ comment.text }}</p>
              </div>
            </div>
          </div>
        </v-card-text>

        <v-divider />

        <div class="dialog-footer">
          <v-btn variant="text" @click="showDetailsDialog = false">Close</v-btn>
          <v-btn
            v-if="selectedRequest.status === 'approved'"
            color="primary"
            @click="goToProject(selectedRequest)"
          >
            <v-icon class="mr-1">mdi-arrow-right</v-icon>
            Go to Project
          </v-btn>
          <v-btn
            v-if="selectedRequest.status === 'draft'"
            color="primary"
            @click="submitRequest(selectedRequest)"
          >
            Submit Request
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- New Request Dialog -->
    <v-dialog v-model="showNewRequestDialog" max-width="700" persistent>
      <v-card class="new-request-dialog glass">
        <div class="dialog-header">
          <h2>New Access Request</h2>
          <v-btn icon="mdi-close" variant="text" size="small" @click="showNewRequestDialog = false" />
        </div>
        <v-divider />
        
        <v-card-text class="dialog-content">
          <v-stepper v-model="requestStep" :items="stepperItems" alt-labels>
            <template v-slot:item.1>
              <v-card flat class="step-content">
                <h4 class="step-title">Project Information</h4>
                <v-text-field
                  v-model="newRequest.projectTitle"
                  label="Project Title"
                  placeholder="e.g., Colorectal Cancer Biomarker Discovery"
                  variant="outlined"
                  :rules="[v => !!v || 'Required']"
                  class="mb-4"
                />
                <v-textarea
                  v-model="newRequest.description"
                  label="Project Description"
                  placeholder="Describe your research objectives and methodology..."
                  variant="outlined"
                  rows="3"
                  :rules="[v => !!v || 'Required']"
                  class="mb-4"
                />
                <v-select
                  v-model="newRequest.requestType"
                  :items="requestTypes"
                  label="Request Type"
                  variant="outlined"
                  :rules="[v => !!v || 'Required']"
                  class="mb-4"
                />
                <v-select
                  v-model="newRequest.duration"
                  :items="durationOptions"
                  label="Requested Access Duration"
                  variant="outlined"
                  :rules="[v => !!v || 'Required']"
                />
              </v-card>
            </template>

            <template v-slot:item.2>
              <v-card flat class="step-content">
                <h4 class="step-title">Select Datasets</h4>
                <v-text-field
                  v-model="datasetSearch"
                  prepend-inner-icon="mdi-magnify"
                  placeholder="Search datasets..."
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  class="mb-4"
                />
                <div class="dataset-selection">
                  <v-checkbox
                    v-for="dataset in availableDatasets"
                    :key="dataset.id"
                    v-model="newRequest.selectedDatasets"
                    :value="dataset.id"
                    hide-details
                    class="dataset-checkbox"
                  >
                    <template v-slot:label>
                      <div class="dataset-option">
                        <span class="dataset-option-name">{{ dataset.name }}</span>
                        <span class="dataset-option-biobank">{{ dataset.biobank }}</span>
                      </div>
                    </template>
                  </v-checkbox>
                </div>
              </v-card>
            </template>

            <template v-slot:item.3>
              <v-card flat class="step-content">
                <h4 class="step-title">Compute Resources</h4>
                <v-select
                  v-model="newRequest.hpcSite"
                  :items="hpcSites"
                  label="Preferred HPC Site"
                  variant="outlined"
                  class="mb-4"
                />
                <v-alert type="info" variant="tonal" class="mb-4">
                  Select an HPC site if you need to run computations on the data. Leave empty for data access only.
                </v-alert>
              </v-card>
            </template>

            <template v-slot:item.4>
              <v-card flat class="step-content">
                <h4 class="step-title">Documentation</h4>
                <v-checkbox
                  v-model="newRequest.ethicsApproval"
                  label="I confirm ethics committee approval has been obtained"
                  color="primary"
                  class="mb-2"
                />
                <v-checkbox
                  v-model="newRequest.dpiaCompleted"
                  label="Data Protection Impact Assessment (DPIA) has been completed"
                  color="primary"
                  class="mb-4"
                />
                <v-file-input
                  v-model="newRequest.ethicsDocument"
                  label="Upload Ethics Approval (optional)"
                  variant="outlined"
                  prepend-icon=""
                  prepend-inner-icon="mdi-paperclip"
                  class="mb-4"
                />
                <v-textarea
                  v-model="newRequest.additionalNotes"
                  label="Additional Notes"
                  placeholder="Any additional information for the review committee..."
                  variant="outlined"
                  rows="2"
                />
              </v-card>
            </template>
          </v-stepper>
        </v-card-text>

        <v-divider />

        <div class="dialog-footer">
          <v-btn variant="text" @click="showNewRequestDialog = false">Cancel</v-btn>
          <v-btn
            v-if="requestStep > 1"
            variant="outlined"
            @click="requestStep--"
          >
            Back
          </v-btn>
          <v-btn
            v-if="requestStep < 4"
            color="primary"
            @click="requestStep++"
          >
            Continue
          </v-btn>
          <v-btn
            v-if="requestStep === 4"
            color="primary"
            @click="createRequest"
            :loading="isCreating"
          >
            Submit Request
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- Success Snackbar -->
    <v-snackbar v-model="showSnackbar" :color="snackbarColor" :timeout="4000">
      {{ snackbarMessage }}
      <template v-slot:actions>
        <v-btn variant="text" @click="showSnackbar = false">Close</v-btn>
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
const viewMode = ref('cards')
const searchQuery = ref('')
const statusFilter = ref(null)
const typeFilter = ref(null)
const showDetailsDialog = ref(false)
const showNewRequestDialog = ref(false)
const selectedRequest = ref(null)
const requestStep = ref(1)
const isCreating = ref(false)
const datasetSearch = ref('')
const showSnackbar = ref(false)
const snackbarMessage = ref('')
const snackbarColor = ref('success')

const statusOptions = ['draft', 'pending', 'in_review', 'approved', 'rejected']
const requestTypes = ['Compute Access', 'Data Access', 'Data + Compute Access']
const durationOptions = ['3 months', '6 months', '12 months', '24 months']
const hpcSites = ['MUSICA', 'MUG-SX']

const stepperItems = ['Project', 'Datasets', 'Compute', 'Documentation']

const progressSteps = [
  { key: 'submitted', label: 'Submitted' },
  { key: 'biobank_review', label: 'Biobank Review' },
  { key: 'ethics_review', label: 'Ethics Review' },
  { key: 'final_approval', label: 'Final Approval' }
]

const newRequest = ref({
  projectTitle: '',
  description: '',
  requestType: null,
  duration: null,
  selectedDatasets: [],
  hpcSite: null,
  ethicsApproval: false,
  dpiaCompleted: false,
  ethicsDocument: null,
  additionalNotes: ''
})

const availableDatasets = [
  { id: 'ds-1', name: 'Austrian CRC Lymph Node Collection', biobank: 'BBMRI-AT / MUG' },
  { id: 'ds-2', name: 'MUG Synthetic Pathology Training Set', biobank: 'Medical University of Graz' },
  { id: 'ds-3', name: 'German Breast Cancer Genomics Cohort', biobank: 'BBMRI-DE / Charité' },
  { id: 'ds-4', name: 'Dutch Prostate Cancer Clinical Registry', biobank: 'BBMRI-NL / Erasmus MC' },
  { id: 'ds-5', name: 'Czech Lung Cancer Screening Dataset', biobank: 'BBMRI-CZ / MMCI' }
]

// Mock requests data
const requests = ref([
  {
    id: 'REQ-2024-001',
    projectTitle: 'CRC Biomarker Discovery using Explainable AI',
    description: 'This project aims to identify novel digital biomarkers for colorectal cancer prognosis using weakly supervised learning on whole-slide images of lymph node tissue.',
    requestType: 'Compute Access',
    datasets: ['Austrian CRC Lymph Node Collection'],
    datasetDetails: [
      { id: 'ds-1', name: 'Austrian CRC Lymph Node Collection', biobank: 'BBMRI-AT / MUG', samples: '3,200' }
    ],
    hpcSite: 'MUSICA',
    duration: '12 months',
    status: 'approved',
    currentStep: 'final_approval',
    submittedAt: '2024-10-15T09:00:00Z',
    updatedAt: '2024-11-20T14:30:00Z',
    stepDates: {
      submitted: '2024-10-15T09:00:00Z',
      biobank_review: '2024-10-28T11:00:00Z',
      ethics_review: '2024-11-10T16:00:00Z',
      final_approval: '2024-11-20T14:30:00Z'
    },
    documents: [
      { name: 'Ethics Approval', uploaded: true },
      { name: 'DPIA', uploaded: true },
      { name: 'Data Transfer Agreement', uploaded: true }
    ],
    comments: [
      { id: 1, author: 'Dr. Maria Weber (Biobank)', date: '2024-10-28T11:00:00Z', text: 'Dataset access approved. Please ensure compliance with the data handling guidelines.' },
      { id: 2, author: 'Ethics Committee', date: '2024-11-10T16:00:00Z', text: 'Ethics review completed. No concerns raised.' }
    ],
    projectId: 'proj-uc7-001'
  },
  {
    id: 'REQ-2024-002',
    projectTitle: 'Synthetic WSI Generation for Privacy-Preserving Research',
    description: 'Development and validation of synthetic whole-slide image generation methods to enable data sharing while preserving patient privacy.',
    requestType: 'Data + Compute Access',
    datasets: ['MUG Synthetic Pathology Training Set', 'Austrian CRC Lymph Node Collection'],
    datasetDetails: [
      { id: 'ds-2', name: 'MUG Synthetic Pathology Training Set', biobank: 'MUG', samples: '5,000' },
      { id: 'ds-1', name: 'Austrian CRC Lymph Node Collection', biobank: 'BBMRI-AT / MUG', samples: '3,200' }
    ],
    hpcSite: 'MUSICA',
    duration: '24 months',
    status: 'in_review',
    currentStep: 'ethics_review',
    submittedAt: '2024-11-01T10:30:00Z',
    updatedAt: '2024-12-05T09:15:00Z',
    stepDates: {
      submitted: '2024-11-01T10:30:00Z',
      biobank_review: '2024-11-18T14:00:00Z'
    },
    documents: [
      { name: 'Ethics Approval', uploaded: true },
      { name: 'DPIA', uploaded: true },
      { name: 'Data Transfer Agreement', uploaded: false }
    ],
    comments: [
      { id: 1, author: 'Dr. Thomas Müller (Biobank)', date: '2024-11-18T14:00:00Z', text: 'Initial review complete. Awaiting ethics committee decision.' }
    ]
  },
  {
    id: 'REQ-2024-003',
    projectTitle: 'Multi-center Breast Cancer Genomics Analysis',
    description: 'Federated analysis of breast cancer genomic data across multiple European biobanks to identify treatment response markers.',
    requestType: 'Compute Access',
    datasets: ['German Breast Cancer Genomics Cohort'],
    datasetDetails: [
      { id: 'ds-3', name: 'German Breast Cancer Genomics Cohort', biobank: 'BBMRI-DE / Charité', samples: '1,500' }
    ],
    hpcSite: 'MUG-SX',
    duration: '12 months',
    status: 'pending',
    currentStep: 'submitted',
    submittedAt: '2024-12-10T08:45:00Z',
    updatedAt: '2024-12-10T08:45:00Z',
    stepDates: {
      submitted: '2024-12-10T08:45:00Z'
    },
    documents: [
      { name: 'Ethics Approval', uploaded: true },
      { name: 'DPIA', uploaded: false },
      { name: 'Data Transfer Agreement', uploaded: false }
    ],
    comments: []
  },
  {
    id: 'REQ-2024-004',
    projectTitle: 'Lung Cancer Screening AI Development',
    description: 'Training deep learning models for automated lung nodule detection using CT screening data.',
    requestType: 'Data + Compute Access',
    datasets: ['Czech Lung Cancer Screening Dataset'],
    datasetDetails: [
      { id: 'ds-5', name: 'Czech Lung Cancer Screening Dataset', biobank: 'BBMRI-CZ / MMCI', samples: '12,000' }
    ],
    hpcSite: 'MUSICA',
    duration: '12 months',
    status: 'rejected',
    currentStep: 'ethics_review',
    submittedAt: '2024-09-20T11:00:00Z',
    updatedAt: '2024-10-15T16:30:00Z',
    stepDates: {
      submitted: '2024-09-20T11:00:00Z',
      biobank_review: '2024-10-01T10:00:00Z'
    },
    documents: [
      { name: 'Ethics Approval', uploaded: false },
      { name: 'DPIA', uploaded: true },
      { name: 'Data Transfer Agreement', uploaded: false }
    ],
    comments: [
      { id: 1, author: 'Ethics Committee', date: '2024-10-15T16:30:00Z', text: 'Request rejected: Ethics approval documentation not provided. Please resubmit with valid ethics committee approval.' }
    ]
  },
  {
    id: 'REQ-2024-005',
    projectTitle: 'Prostate Cancer Outcome Prediction',
    description: 'Machine learning analysis of clinical registry data to predict treatment outcomes in prostate cancer patients.',
    requestType: 'Compute Access',
    datasets: ['Dutch Prostate Cancer Clinical Registry'],
    datasetDetails: [
      { id: 'ds-4', name: 'Dutch Prostate Cancer Clinical Registry', biobank: 'BBMRI-NL / Erasmus MC', samples: '8,500' }
    ],
    hpcSite: 'MUSICA',
    duration: '6 months',
    status: 'approved',
    currentStep: 'final_approval',
    submittedAt: '2024-08-05T14:20:00Z',
    updatedAt: '2024-09-12T11:00:00Z',
    stepDates: {
      submitted: '2024-08-05T14:20:00Z',
      biobank_review: '2024-08-20T09:00:00Z',
      ethics_review: '2024-09-01T15:00:00Z',
      final_approval: '2024-09-12T11:00:00Z'
    },
    documents: [
      { name: 'Ethics Approval', uploaded: true },
      { name: 'DPIA', uploaded: true },
      { name: 'Data Transfer Agreement', uploaded: true }
    ],
    comments: [],
    projectId: 'proj-uc8-001'
  }
])

const tableHeaders = [
  { title: 'Request ID', key: 'id', width: '140px' },
  { title: 'Project', key: 'projectTitle', width: '280px' },
  { title: 'Datasets', key: 'datasets', width: '120px' },
  { title: 'Status', key: 'status', width: '130px' },
  { title: 'Submitted', key: 'submittedAt', width: '120px' },
  { title: 'Actions', key: 'actions', width: '100px', sortable: false }
]

// Computed
const pendingCount = computed(() => requests.value.filter(r => r.status === 'pending').length)
const inReviewCount = computed(() => requests.value.filter(r => r.status === 'in_review').length)
const approvedCount = computed(() => requests.value.filter(r => r.status === 'approved').length)
const rejectedCount = computed(() => requests.value.filter(r => r.status === 'rejected').length)

const filteredRequests = computed(() => {
  return requests.value.filter(request => {
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      const matches = 
        request.projectTitle.toLowerCase().includes(query) ||
        request.id.toLowerCase().includes(query) ||
        request.description.toLowerCase().includes(query)
      if (!matches) return false
    }
    if (statusFilter.value && request.status !== statusFilter.value) return false
    if (typeFilter.value && request.requestType !== typeFilter.value) return false
    return true
  })
})

// Methods
function getStatusColor(status) {
  const colors = {
    draft: 'grey',
    pending: 'warning',
    in_review: 'info',
    approved: 'success',
    rejected: 'error'
  }
  return colors[status] || 'grey'
}

function formatStatus(status) {
  const labels = {
    draft: 'Draft',
    pending: 'Pending',
    in_review: 'In Review',
    approved: 'Approved',
    rejected: 'Rejected'
  }
  return labels[status] || status
}

function formatDate(dateString) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function isStepCompleted(request, stepKey) {
  const stepOrder = ['submitted', 'biobank_review', 'ethics_review', 'final_approval']
  const currentIndex = stepOrder.indexOf(request.currentStep)
  const stepIndex = stepOrder.indexOf(stepKey)
  
  if (request.status === 'approved') return true
  if (request.status === 'rejected') return stepIndex < currentIndex
  return stepIndex < currentIndex
}

function isStepCurrent(request, stepKey) {
  return request.currentStep === stepKey && request.status !== 'approved'
}

function openNewRequest() {
  requestStep.value = 1
  newRequest.value = {
    projectTitle: '',
    description: '',
    requestType: null,
    duration: null,
    selectedDatasets: [],
    hpcSite: null,
    ethicsApproval: false,
    dpiaCompleted: false,
    ethicsDocument: null,
    additionalNotes: ''
  }
  showNewRequestDialog.value = true
}

function openRequestDetails(request) {
  selectedRequest.value = request
  showDetailsDialog.value = true
}

function submitRequest(request) {
  request.status = 'pending'
  request.currentStep = 'submitted'
  request.submittedAt = new Date().toISOString()
  showSnackbar.value = true
  snackbarMessage.value = 'Request submitted successfully'
  snackbarColor.value = 'success'
}

function goToProject(request) {
  showDetailsDialog.value = false
  if (request.projectId) {
    router.push(`/projects/${request.projectId}`)
  } else {
    router.push('/dashboard')
  }
}

async function createRequest() {
  isCreating.value = true
  
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  const newReq = {
    id: `REQ-2024-${String(requests.value.length + 1).padStart(3, '0')}`,
    projectTitle: newRequest.value.projectTitle,
    description: newRequest.value.description,
    requestType: newRequest.value.requestType,
    datasets: newRequest.value.selectedDatasets.map(id => 
      availableDatasets.find(d => d.id === id)?.name || id
    ),
    datasetDetails: newRequest.value.selectedDatasets.map(id => {
      const ds = availableDatasets.find(d => d.id === id)
      return { id, name: ds?.name, biobank: ds?.biobank, samples: 'N/A' }
    }),
    hpcSite: newRequest.value.hpcSite,
    duration: newRequest.value.duration,
    status: 'pending',
    currentStep: 'submitted',
    submittedAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    stepDates: {
      submitted: new Date().toISOString()
    },
    documents: [
      { name: 'Ethics Approval', uploaded: newRequest.value.ethicsApproval },
      { name: 'DPIA', uploaded: newRequest.value.dpiaCompleted },
      { name: 'Data Transfer Agreement', uploaded: false }
    ],
    comments: []
  }
  
  requests.value.unshift(newReq)
  
  isCreating.value = false
  showNewRequestDialog.value = false
  showSnackbar.value = true
  snackbarMessage.value = 'Access request created and submitted successfully'
  snackbarColor.value = 'success'
}
</script>

<style scoped lang="scss">
// View-specific styles
.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #f1f5f9;
  line-height: 1;
}

.stat-label {
  font-size: 0.8125rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

// Filters
.filters-card {
  background: rgba(30, 41, 59, 0.5) !important;
  border: 1px solid rgba(51, 65, 85, 0.5);
}

// Requests Grid
.requests-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 1.25rem;
}

.request-card {
  background: rgba(30, 41, 59, 0.5) !important;
  border: 1px solid rgba(51, 65, 85, 0.5);
  cursor: pointer;
  transition: all 0.2s ease;
  overflow: hidden;
  
  &:hover {
    transform: translateY(-2px);
    border-color: rgba(230, 152, 48, 0.3);
  }
}

.card-status-bar {
  height: 3px;
  
  &.draft { background: #64748b; }
  &.pending { background: #fbbf24; }
  &.in_review { background: #3b82f6; }
  &.approved { background: #22c55e; }
  &.rejected { background: #ef4444; }
}

.card-content {
  padding: 1.25rem !important;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.request-id {
  font-size: 0.75rem;
  color: #64748b;
}

.request-title {
  font-size: 1rem;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.request-description {
  font-size: 0.8125rem;
  color: #94a3b8;
  line-height: 1.5;
  margin-bottom: 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.request-meta {
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
}

.datasets-preview {
  margin-bottom: 1rem;
}

// Progress Steps
.progress-steps {
  display: flex;
  gap: 0.5rem;
}

.step {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  
  .step-indicator {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: rgba(100, 116, 139, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.625rem;
    font-weight: 600;
    color: #64748b;
  }
  
  .step-label {
    font-size: 0.6875rem;
    color: #64748b;
  }
  
  &.completed {
    .step-indicator {
      background: rgba(34, 197, 94, 0.2);
      color: #22c55e;
    }
    .step-label {
      color: #22c55e;
    }
  }
  
  &.current {
    .step-indicator {
      background: rgba(230, 152, 48, 0.2);
      color: #E69830;
    }
    .step-label {
      color: #E69830;
      font-weight: 500;
    }
  }
}

.card-actions {
  padding: 0.75rem 1rem !important;
}

// Table
.table-card {
  background: rgba(30, 41, 59, 0.5) !important;
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.requests-table {
  background: transparent !important;
  
  :deep(.v-data-table__tr) {
    cursor: pointer;
    
    &:hover {
      background: rgba(230, 152, 48, 0.05) !important;
    }
  }
}

.request-id-cell {
  font-size: 0.8125rem;
  color: #94a3b8;
}

.title-cell {
  .title-text {
    display: block;
    font-weight: 500;
    color: #f1f5f9;
  }
  .type-text {
    display: block;
    font-size: 0.75rem;
    color: #64748b;
  }
}

// Details Dialog
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

.request-id-label {
  font-size: 0.8125rem;
  color: #64748b;
  display: block;
}

.dialog-content {
  padding: 1.25rem !important;
  max-height: 65vh;
  overflow-y: auto;
}

// Timeline
.timeline-section {
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.timeline {
  display: flex;
  gap: 0.5rem;
}

.timeline-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: relative;
  
  &:not(:last-child)::after {
    content: '';
    position: absolute;
    top: 14px;
    left: calc(50% + 16px);
    width: calc(100% - 32px);
    height: 2px;
    background: rgba(100, 116, 139, 0.3);
  }
  
  &.completed:not(:last-child)::after {
    background: rgba(34, 197, 94, 0.5);
  }
}

.timeline-marker {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(100, 116, 139, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 0.5rem;
  z-index: 1;
  
  .completed & {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
  }
  
  .current & {
    background: rgba(230, 152, 48, 0.2);
    color: #E69830;
  }
  
  .rejected & {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
  }
}

.timeline-content {
  .timeline-label {
    display: block;
    font-size: 0.75rem;
    color: #94a3b8;
    
    .completed & {
      color: #22c55e;
    }
    
    .current & {
      color: #E69830;
      font-weight: 500;
    }
    
    .rejected & {
      color: #ef4444;
    }
  }
  
  .timeline-date {
    display: block;
    font-size: 0.6875rem;
    color: #64748b;
    margin-top: 0.25rem;
  }
}

// Detail sections
.detail-section {
  margin-bottom: 1.5rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.detail-item {
  &.full {
    grid-column: 1 / -1;
  }
  
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
    
    &.description {
      font-size: 0.875rem;
      line-height: 1.6;
      color: #94a3b8;
    }
  }
}

.datasets-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.dataset-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
}

.dataset-info {
  flex: 1;
  
  .dataset-name {
    display: block;
    font-weight: 500;
    color: #f1f5f9;
  }
  
  .dataset-biobank {
    display: block;
    font-size: 0.75rem;
    color: #64748b;
  }
}

.hpc-info {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  background: rgba(230, 152, 48, 0.1);
  border-radius: 8px;
  
  .hpc-site {
    display: block;
    font-weight: 500;
    color: #E69830;
  }
  
  .hpc-label {
    display: block;
    font-size: 0.75rem;
    color: #94a3b8;
  }
}

.documents-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.document-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 6px;
  
  .doc-name {
    flex: 1;
    color: #e2e8f0;
    font-size: 0.875rem;
  }
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.comment-item {
  padding: 0.75rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
  border-left: 3px solid #E69830;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  
  .comment-author {
    font-weight: 500;
    color: #E69830;
    font-size: 0.8125rem;
  }
  
  .comment-date {
    font-size: 0.75rem;
    color: #64748b;
  }
}

.comment-text {
  color: #94a3b8;
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
}

// New Request Dialog
.new-request-dialog {
  .dialog-content {
    padding: 0 !important;
  }
}

.step-content {
  padding: 1.5rem;
  background: transparent !important;
}

.step-title {
  font-size: 1rem;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 1.25rem;
}

.dataset-selection {
  max-height: 300px;
  overflow-y: auto;
}

.dataset-checkbox {
  margin-bottom: 0.5rem;
  
  :deep(.v-label) {
    opacity: 1 !important;
  }
}

.dataset-option {
  .dataset-option-name {
    display: block;
    color: #f1f5f9;
    font-weight: 500;
  }
  
  .dataset-option-biobank {
    display: block;
    font-size: 0.75rem;
    color: #64748b;
  }
}

</style>
