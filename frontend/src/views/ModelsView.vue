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
              <v-icon class="title-icon">mdi-brain</v-icon>
              Model Hub
            </h1>
            <p class="page-subtitle">
              Browse and deploy AI models for computational pathology analysis
            </p>
          </div>
          <div class="header-actions">
            <v-btn-toggle v-model="viewMode" mandatory density="comfortable" class="view-toggle">
              <v-btn value="grid" icon="mdi-view-grid" size="small" />
              <v-btn value="list" icon="mdi-view-list" size="small" />
            </v-btn-toggle>
          </div>
        </div>

        <!-- Filters -->
        <v-card class="filters-card glass mb-6">
          <v-card-text>
            <v-row align="center">
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="searchQuery"
                  placeholder="Search models..."
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  clearable
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="categoryFilter"
                  :items="categories"
                  label="Category"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  clearable
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Models grid view -->
        <section v-if="viewMode === 'grid'" class="models-grid slide-up delay-3">
          <v-row>
            <v-col 
              cols="12" 
              sm="6" 
              lg="4" 
              xl="3"
              v-for="model in filteredModels" 
              :key="model.id"
            >
              <v-card class="model-card glass card-hover" :elevation="0" @click="viewModel(model)">
                <!-- Model header -->
                <div class="model-header">
                  <div class="model-icon" :style="{ background: model.gradient }">
                    <v-icon :icon="model.icon" size="28" color="white" />
                  </div>
                  <v-chip 
                    :color="model.status === 'available' ? 'success' : 'warning'" 
                    size="x-small" 
                    variant="tonal"
                  >
                    {{ model.status }}
                  </v-chip>
                </div>

                <!-- Model content -->
                <v-card-text class="model-content">
                  <h3 class="model-name">{{ model.name }}</h3>
                  <p class="model-description">{{ model.shortDescription }}</p>

                  <!-- Tags -->
                  <div class="model-tags">
                    <v-chip 
                      v-for="tag in model.tags.slice(0, 3)" 
                      :key="tag" 
                      size="x-small"
                      variant="outlined"
                      class="tag-chip"
                    >
                      {{ tag }}
                    </v-chip>
                  </div>

                  <!-- Stats -->
                  <div class="model-stats">
                    <div class="stat-item">
                      <v-icon size="14">mdi-play-circle</v-icon>
                      <span>{{ model.runs }} runs</span>
                    </div>
                    <div class="stat-item">
                      <v-icon size="14">mdi-clock-outline</v-icon>
                      <span>{{ model.avgRuntime }}</span>
                    </div>
                  </div>
                </v-card-text>

                <!-- Model footer -->
                <div class="model-footer">
                  <v-btn 
                    color="primary" 
                    size="small" 
                    variant="tonal"
                    @click.stop="deployModel(model)"
                  >
                    Deploy
                  </v-btn>
                </div>
              </v-card>
            </v-col>
          </v-row>

          <!-- Empty state -->
          <div v-if="filteredModels.length === 0" class="empty-state">
            <v-icon size="64" color="primary" class="mb-4">mdi-brain</v-icon>
            <h3>No models found</h3>
            <p>Try adjusting your filters or search query.</p>
          </div>
        </section>

        <!-- Models list view -->
        <section v-else class="models-list slide-up delay-3">
          <v-card class="models-table-card glass" :elevation="0">
            <v-data-table
              :headers="tableHeaders"
              :items="filteredModels"
              class="models-table"
              item-key="id"
              hover
            >
              <!-- Name column -->
              <template v-slot:item.name="{ item }">
                <div class="name-cell" @click="viewModel(item)">
                  <div class="model-icon-small" :style="{ background: item.gradient }">
                    <v-icon :icon="item.icon" size="18" color="white" />
                  </div>
                  <div class="name-info">
                    <span class="model-name-text">{{ item.name }}</span>
                    <span class="model-version">{{ item.version }}</span>
                  </div>
                </div>
              </template>

              <!-- Category column -->
              <template v-slot:item.category="{ item }">
                <v-chip size="small" variant="tonal">{{ item.category }}</v-chip>
              </template>

              <!-- Stats column -->
              <template v-slot:item.stats="{ item }">
                <div class="stats-cell">
                  <span class="font-mono">{{ item.runs }} runs</span>
                  <span class="separator">•</span>
                  <span class="font-mono">{{ item.avgRuntime }}</span>
                </div>
              </template>

              <!-- Status column -->
              <template v-slot:item.status="{ item }">
                <v-chip 
                  :color="item.status === 'available' ? 'success' : 'warning'" 
                  size="small" 
                  variant="tonal"
                >
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
                    @click="viewModel(item)"
                  />
                  <v-btn
                    icon="mdi-play"
                    size="small"
                    variant="text"
                    color="primary"
                    @click="deployModel(item)"
                  />
                </div>
              </template>
            </v-data-table>
          </v-card>
        </section>
      </div>
    </v-main>

    <!-- Model Details Dialog -->
    <v-dialog v-model="showDetailsDialog" max-width="800">
      <v-card class="details-dialog glass" v-if="selectedModel">
        <div class="dialog-header">
          <div class="dialog-title-section">
            <div class="model-icon-large" :style="{ background: selectedModel.gradient }">
              <v-icon :icon="selectedModel.icon" size="32" color="white" />
            </div>
            <div>
              <h2>{{ selectedModel.name }}</h2>
              <span class="model-version-text">{{ selectedModel.version }}</span>
            </div>
          </div>
          <v-btn icon="mdi-close" variant="text" size="small" @click="showDetailsDialog = false" />
        </div>
        <v-divider />
        <v-card-text class="dialog-content">
          <!-- Description -->
          <div class="detail-section">
            <h4>Description</h4>
            <p class="description-text">{{ selectedModel.description }}</p>
          </div>

          <!-- Info grid -->
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">Category</span>
              <v-chip size="small" variant="tonal">{{ selectedModel.category }}</v-chip>
            </div>
            <div class="detail-item">
              <span class="detail-label">Status</span>
              <v-chip 
                :color="selectedModel.status === 'available' ? 'success' : 'warning'" 
                size="small" 
                variant="tonal"
              >
                {{ selectedModel.status }}
              </v-chip>
            </div>
            <div class="detail-item">
              <span class="detail-label">Architecture</span>
              <span class="detail-value">{{ selectedModel.architecture }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Input</span>
              <span class="detail-value">{{ selectedModel.inputFormat }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Output</span>
              <span class="detail-value">{{ selectedModel.outputFormat }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Total Runs</span>
              <span class="detail-value font-mono">{{ selectedModel.runs }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Avg. Runtime</span>
              <span class="detail-value font-mono">{{ selectedModel.avgRuntime }}</span>
            </div>
          </div>

          <!-- Requirements -->
          <div class="detail-section">
            <h4>Requirements</h4>
            <div class="requirements-grid">
              <div class="requirement-item">
                <v-icon size="20">mdi-server</v-icon>
                <div>
                  <span class="req-label">Nodes</span>
                  <span class="req-value">{{ selectedModel.requirements.nodes }}</span>
                </div>
              </div>
              <div class="requirement-item">
                <v-icon size="20">mdi-expansion-card</v-icon>
                <div>
                  <span class="req-label">GPU</span>
                  <span class="req-value">{{ selectedModel.requirements.gpu }}</span>
                </div>
              </div>
              <div class="requirement-item">
                <v-icon size="20">mdi-memory</v-icon>
                <div>
                  <span class="req-label">Memory</span>
                  <span class="req-value">{{ selectedModel.requirements.memory }}</span>
                </div>
              </div>
              <div class="requirement-item">
                <v-icon size="20">mdi-harddisk</v-icon>
                <div>
                  <span class="req-label">Storage</span>
                  <span class="req-value">{{ selectedModel.requirements.storage }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Tags -->
          <div class="detail-section">
            <h4>Tags</h4>
            <div class="tags-list">
              <v-chip 
                v-for="tag in selectedModel.tags" 
                :key="tag" 
                size="small"
                variant="outlined"
              >
                {{ tag }}
              </v-chip>
            </div>
          </div>
        </v-card-text>
        <v-divider />
        <div class="dialog-footer">
          <v-btn variant="outlined" prepend-icon="mdi-file-document">Documentation</v-btn>
          <v-btn color="primary" prepend-icon="mdi-play" @click="deployModel(selectedModel)">
            Deploy Model
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <!-- Deploy Model Dialog -->
    <v-dialog v-model="showDeployDialog" max-width="560">
      <v-card class="deploy-dialog glass" v-if="modelToDeploy">
        <div class="dialog-header">
          <h2>Deploy Model</h2>
          <v-btn icon="mdi-close" variant="text" size="small" @click="showDeployDialog = false" />
        </div>
        <v-divider />
        <v-card-text class="dialog-content">
          <div class="deploy-model-info">
            <div class="model-icon-small" :style="{ background: modelToDeploy.gradient }">
              <v-icon :icon="modelToDeploy.icon" size="18" color="white" />
            </div>
            <div>
              <span class="deploy-model-name">{{ modelToDeploy.name }}</span>
              <span class="deploy-model-version">{{ modelToDeploy.version }}</span>
            </div>
          </div>

          <v-form ref="deployFormRef" class="deploy-form">
            <v-select
              v-model="deployConfig.projectId"
              :items="projectsStore.activeProjects"
              item-title="shortTitle"
              item-value="id"
              label="Project"
              :rules="[v => !!v || 'Project is required']"
              class="mb-4"
            />
            <v-select
              v-model="deployConfig.datasetId"
              :items="availableDatasets"
              item-title="name"
              item-value="id"
              label="Dataset"
              :rules="[v => !!v || 'Dataset is required']"
              class="mb-4"
            />
            <v-select
              v-model="deployConfig.hpcSite"
              :items="hpcSites"
              label="HPC Site"
              :rules="[v => !!v || 'HPC site is required']"
              class="mb-4"
            />
          </v-form>
        </v-card-text>
        <v-divider />
        <div class="dialog-footer">
          <v-btn variant="text" @click="showDeployDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="confirmDeploy" :loading="isDeploying">
            Deploy
          </v-btn>
        </div>
      </v-card>
    </v-dialog>
  </v-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const router = useRouter()
const projectsStore = useProjectsStore()

const sidebarRail = ref(false)
const viewMode = ref('grid')
const searchQuery = ref('')
const categoryFilter = ref(null)
const showDetailsDialog = ref(false)
const showDeployDialog = ref(false)
const selectedModel = ref(null)
const modelToDeploy = ref(null)
const isDeploying = ref(false)
const deployFormRef = ref(null)

const deployConfig = ref({
  projectId: null,
  datasetId: null,
  hpcSite: null
})

// Mock models data
const models = ref([
  {
    id: 'model-virchow2',
    name: 'Virchow2 Feature Computation',
    version: 'v2.1.0',
    shortDescription: 'Foundation model for extracting rich feature representations from whole-slide images.',
    description: 'Virchow2 is a state-of-the-art foundation model for computational pathology. It extracts high-dimensional feature representations from whole-slide images that can be used for downstream tasks such as classification, segmentation, and survival prediction. Pre-trained on millions of pathology images, it provides robust and generalizable features.',
    category: 'Feature Extraction',
    icon: 'mdi-vector-combine',
    gradient: 'linear-gradient(135deg, #E69830 0%, #D18A28 100%)',
    status: 'available',
    useCases: ['UC7', 'UC8'],
    tags: ['foundation model', 'feature extraction', 'WSI', 'self-supervised', 'transformer'],
    runs: 1247,
    avgRuntime: '~45 min/WSI',
    architecture: 'Vision Transformer (ViT-H/14)',
    inputFormat: 'WSI (SVS, NDPI, TIFF)',
    outputFormat: 'Feature vectors (2048-dim)',
    requirements: {
      nodes: 1,
      gpu: '1x A100 40GB',
      memory: '64 GB',
      storage: '50 GB'
    }
  },
  {
    id: 'model-tissue-seg',
    name: 'Tissue Segmentation',
    version: 'v1.4.2',
    shortDescription: 'Multi-class tissue segmentation for identifying tumor, stroma, necrosis, and normal tissue regions.',
    description: 'Advanced deep learning model for pixel-level tissue segmentation in H&E stained whole-slide images. Accurately identifies and delineates multiple tissue types including tumor epithelium, stroma, necrosis, lymphocyte aggregates, and normal tissue. Essential for quantitative pathology analysis and region-of-interest extraction.',
    category: 'Segmentation',
    icon: 'mdi-vector-polygon',
    gradient: 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)',
    status: 'available',
    useCases: ['UC7'],
    tags: ['segmentation', 'tissue classification', 'H&E', 'U-Net', 'multi-class'],
    runs: 892,
    avgRuntime: '~30 min/WSI',
    architecture: 'U-Net with EfficientNet encoder',
    inputFormat: 'WSI patches (256x256)',
    outputFormat: 'Segmentation masks (6 classes)',
    requirements: {
      nodes: 1,
      gpu: '1x V100 32GB',
      memory: '32 GB',
      storage: '20 GB'
    }
  },
  {
    id: 'model-synth-gen',
    name: 'Synthetic Image Generation',
    version: 'v3.0.0',
    shortDescription: 'Generate high-resolution synthetic pathology images for training data augmentation and privacy-preserving sharing.',
    description: 'Cutting-edge generative model for creating photorealistic synthetic whole-slide images. Uses diffusion-based architecture to generate high-resolution pathology images that preserve diagnostic features while ensuring patient privacy. Ideal for data augmentation, federated learning, and creating shareable training datasets.',
    category: 'Generation',
    icon: 'mdi-creation',
    gradient: 'linear-gradient(135deg, #EC4899 0%, #DB2777 100%)',
    status: 'available',
    useCases: ['UC8'],
    tags: ['generative AI', 'diffusion model', 'synthetic data', 'privacy-preserving', 'data augmentation'],
    runs: 423,
    avgRuntime: '~2 hrs/batch',
    architecture: 'Latent Diffusion Model',
    inputFormat: 'Conditioning parameters + noise',
    outputFormat: 'Synthetic WSI tiles (1024x1024)',
    requirements: {
      nodes: 4,
      gpu: '4x A100 80GB',
      memory: '256 GB',
      storage: '200 GB'
    }
  },
  {
    id: 'model-ln-survival',
    name: 'Lymph Node Survival Prediction',
    version: 'v2.0.1',
    shortDescription: 'Predict patient survival outcomes from lymph node metastasis patterns in colorectal cancer.',
    description: 'Specialized survival prediction model trained on lymph node whole-slide images from colorectal cancer patients. Uses weakly supervised learning with multiple instance learning (MIL) to identify prognostic features and predict survival outcomes. Incorporates attention mechanisms to highlight regions contributing to predictions, enabling explainable AI analysis.',
    category: 'Prediction',
    icon: 'mdi-chart-timeline-variant',
    gradient: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
    status: 'available',
    useCases: ['UC7'],
    tags: ['survival analysis', 'MIL', 'attention', 'explainable AI', 'colorectal cancer', 'lymph node'],
    runs: 567,
    avgRuntime: '~15 min/case',
    architecture: 'CLAM with Attention MIL',
    inputFormat: 'WSI feature vectors',
    outputFormat: 'Survival probability, attention heatmaps',
    requirements: {
      nodes: 1,
      gpu: '1x V100 32GB',
      memory: '64 GB',
      storage: '30 GB'
    }
  }
])

const tableHeaders = [
  { title: 'Model', key: 'name', width: '280px' },
  { title: 'Category', key: 'category', width: '150px' },
  { title: 'Stats', key: 'stats', width: '180px' },
  { title: 'Status', key: 'status', width: '120px' },
  { title: 'Actions', key: 'actions', width: '100px', sortable: false }
]

const categories = ['Feature Extraction', 'Segmentation', 'Generation', 'Prediction']
const hpcSites = ['MUSICA', 'MUG-SX']

const availableDatasets = computed(() => [
  { id: 'ds-001', name: 'Lymph Node WSI Collection A' },
  { id: 'ds-002', name: 'Lymph Node WSI Collection B' },
  { id: 'ds-003', name: 'Training Set Alpha' },
  { id: 'ds-004', name: 'Validation Set Beta' },
])

const filteredModels = computed(() => {
  let result = models.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(m => 
      m.name.toLowerCase().includes(query) ||
      m.description.toLowerCase().includes(query) ||
      m.tags.some(t => t.toLowerCase().includes(query))
    )
  }

  if (categoryFilter.value) {
    result = result.filter(m => m.category === categoryFilter.value)
  }

  return result
})

function viewModel(model) {
  selectedModel.value = model
  showDetailsDialog.value = true
}

function deployModel(model) {
  modelToDeploy.value = model
  showDetailsDialog.value = false
  showDeployDialog.value = true
}

async function confirmDeploy() {
  const { valid } = await deployFormRef.value.validate()
  if (!valid) return

  isDeploying.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  isDeploying.value = false
  showDeployDialog.value = false
  
  // Navigate to computations page
  router.push('/computations')
}

onMounted(async () => {
  if (projectsStore.projects.length === 0) {
    await projectsStore.fetchProjects()
  }
})
</script>

<style scoped lang="scss">
// View-specific styles

// Model cards grid
.models-grid {
  margin-bottom: 2rem;
}

.model-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;
  
  &:hover {
    border-color: rgba(230, 152, 48, 0.3);
  }
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.25rem 1.25rem 0;
}

.model-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.model-content {
  flex: 1;
  padding: 1rem 1.25rem !important;
}

.model-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 0.5rem;
}

.model-description {
  font-size: 0.8125rem;
  color: #94a3b8;
  line-height: 1.5;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.model-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  margin-bottom: 1rem;
}

.tag-chip {
  font-size: 0.6875rem;
  border-color: rgba(51, 65, 85, 0.5);
}

.model-stats {
  display: flex;
  gap: 1.25rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: #64748b;
  
  .v-icon {
    color: #64748b;
  }
}

.model-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-top: 1px solid rgba(51, 65, 85, 0.3);
  background: rgba(30, 41, 59, 0.3);
}

.use-cases {
  display: flex;
  gap: 0.375rem;
}

.use-case-badge {
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

// List view
.models-table-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
  overflow: hidden;
}

.models-table {
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

.name-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.model-icon-small {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.name-info {
  display: flex;
  flex-direction: column;
}

.model-name-text {
  font-size: 0.875rem;
  font-weight: 500;
  color: #f1f5f9;
}

.model-version {
  font-size: 0.75rem;
  color: #64748b;
  font-family: 'JetBrains Mono', monospace;
}

.use-cases-cell {
  display: flex;
  gap: 0.375rem;
}

.stats-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: #94a3b8;
  
  .separator {
    color: #475569;
  }
}

.actions-cell {
  display: flex;
  gap: 0.25rem;
}

// Empty state
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  
  h3 {
    font-size: 1.25rem;
    color: #f1f5f9;
    margin-bottom: 0.5rem;
  }
  
  p {
    color: #64748b;
  }
}

// Dialogs
.details-dialog,
.deploy-dialog {
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem;
  
  h2 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #f1f5f9;
  }
}

.dialog-title-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.model-icon-large {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.model-version-text {
  font-size: 0.875rem;
  color: #64748b;
  font-family: 'JetBrains Mono', monospace;
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

// Detail sections
.detail-section {
  margin-bottom: 1.5rem;
  
  h4 {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.75rem;
  }
}

.description-text {
  font-size: 0.9375rem;
  color: #e2e8f0;
  line-height: 1.6;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.detail-label {
  font-size: 0.6875rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  font-size: 0.875rem;
  color: #e2e8f0;
}

.use-cases-detail {
  display: flex;
  gap: 0.375rem;
}

.requirements-grid {
  display: flex;
  gap: 1rem;
}

.requirement-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 10px;
  
  .v-icon {
    color: #E69830;
  }
  
  div {
    display: flex;
    flex-direction: column;
  }
}

.req-label {
  font-size: 0.6875rem;
  color: #64748b;
  text-transform: uppercase;
}

.req-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: #f1f5f9;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

// Deploy dialog
.deploy-model-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 10px;
  margin-bottom: 1.5rem;
}

.deploy-model-name {
  font-size: 1rem;
  font-weight: 500;
  color: #f1f5f9;
  display: block;
}

.deploy-model-version {
  font-size: 0.75rem;
  color: #64748b;
  font-family: 'JetBrains Mono', monospace;
}

.deploy-form {
  margin-top: 1rem;
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
  
  .requirements-grid {
    flex-direction: column;
  }
}
</style>
