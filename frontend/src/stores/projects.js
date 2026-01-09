import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * Projects Store
 * Manages project selection and project data
 */

// Mock projects data
const MOCK_PROJECTS = [
  {
    id: 'proj-uc7-001',
    title: 'Colorectal Cancer Prediction Study',
    shortTitle: 'UC7 - CRC Prediction',
    description: 'Weakly supervised learning on lymph node whole-slide images for survival-guided biomarker discovery',
    useCase: 'UC7',
    status: 'active',
    createdAt: '2024-08-15',
    validUntil: '2027-12-31',
    owner: 'Dr. Max Mustermann',
    datasetCount: 3,
    wsiCount: 45000,
    sites: ['BBMRI-AT', 'BBMRI-NL', 'BBMRI-DE'],
    progress: 45,
    lastActivity: '2 hours ago',
    stats: {
      dataTransfers: { completed: 12, pending: 3, total: 15 },
      computations: { completed: 8, running: 2, queued: 5 },
      models: { applied: 4, available: 12 }
    }
  },
  {
    id: 'proj-uc8-001',
    title: 'Synthetic WSI Generation Pipeline',
    shortTitle: 'UC8 - Synthetic Data',
    description: 'Generation of high-resolution synthetic whole-slide images for computational pathology training',
    useCase: 'UC8',
    status: 'active',
    createdAt: '2024-09-01',
    validUntil: '2027-06-30',
    owner: 'Dr. Max Mustermann',
    datasetCount: 2,
    wsiCount: 12000,
    sites: ['BBMRI-FI', 'BBMRI-CZ'],
    progress: 28,
    lastActivity: '1 day ago',
    stats: {
      dataTransfers: { completed: 5, pending: 1, total: 6 },
      computations: { completed: 3, running: 1, queued: 2 },
      models: { applied: 2, available: 8 }
    }
  },
  {
    id: 'proj-uc7-002',
    title: 'Explainable AI Biomarker Validation',
    shortTitle: 'UC7 - XAI Validation',
    description: 'Validation study for AI-discovered biomarkers in colorectal cancer lymph node metastasis',
    useCase: 'UC7',
    status: 'pending',
    createdAt: '2024-11-20',
    validUntil: '2027-03-31',
    owner: 'Dr. Max Mustermann',
    datasetCount: 1,
    wsiCount: 8500,
    sites: ['BBMRI-IT'],
    progress: 0,
    lastActivity: 'Awaiting approval',
    stats: {
      dataTransfers: { completed: 0, pending: 0, total: 0 },
      computations: { completed: 0, running: 0, queued: 0 },
      models: { applied: 0, available: 12 }
    }
  },
  {
    id: 'proj-uc8-002',
    title: 'Multi-Resolution Synthesis Benchmark',
    shortTitle: 'UC8 - MR Benchmark',
    description: 'Benchmarking synthetic data generation at multiple resolution scales (20x, 40x, 100k²)',
    useCase: 'UC8',
    status: 'completed',
    createdAt: '2024-03-10',
    validUntil: '2027-09-30',
    owner: 'Dr. Max Mustermann',
    datasetCount: 4,
    wsiCount: 25000,
    sites: ['BBMRI-SE', 'BBMRI-NO', 'BBMRI-DK'],
    progress: 100,
    lastActivity: 'Completed Oct 15',
    stats: {
      dataTransfers: { completed: 20, pending: 0, total: 20 },
      computations: { completed: 45, running: 0, queued: 0 },
      models: { applied: 6, available: 8 }
    }
  }
]

export const useProjectsStore = defineStore('projects', () => {
  // State
  const projects = ref([])
  const selectedProjectId = ref(null)
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const selectedProject = computed(() => 
    projects.value.find(p => p.id === selectedProjectId.value) ?? null
  )

  const activeProjects = computed(() => 
    projects.value.filter(p => p.status === 'active')
  )

  const pendingProjects = computed(() => 
    projects.value.filter(p => p.status === 'pending')
  )

  const completedProjects = computed(() => 
    projects.value.filter(p => p.status === 'completed')
  )

  const projectsByUseCase = computed(() => ({
    UC7: projects.value.filter(p => p.useCase === 'UC7'),
    UC8: projects.value.filter(p => p.useCase === 'UC8')
  }))

  // Actions
  async function fetchProjects() {
    isLoading.value = true
    error.value = null

    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500))
      projects.value = MOCK_PROJECTS
      // Default to "All" (null) - don't auto-select a project
    } catch (e) {
      error.value = e.message || 'Failed to fetch projects'
    } finally {
      isLoading.value = false
    }
  }

  function selectProject(projectId) {
    // Allow null for "All Projects"
    if (projectId === null) {
      selectedProjectId.value = null
      return
    }
    const project = projects.value.find(p => p.id === projectId)
    if (project) {
      selectedProjectId.value = projectId
    }
  }

  function clearSelection() {
    selectedProjectId.value = null
  }

  function getProjectById(id) {
    return projects.value.find(p => p.id === id) ?? null
  }

  return {
    // State
    projects,
    selectedProjectId,
    isLoading,
    error,
    // Getters
    selectedProject,
    activeProjects,
    pendingProjects,
    completedProjects,
    projectsByUseCase,
    // Actions
    fetchProjects,
    selectProject,
    clearSelection,
    getProjectById,
  }
})
