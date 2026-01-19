<template>
  <v-layout class="dashboard-layout">
    <!-- Sidebar -->
    <AppSidebar 
      v-model:rail="sidebarRail"
      @toggle-rail="sidebarRail = !sidebarRail"
    />

    <!-- Main content area -->
    <v-main class="dashboard-main">
      <!-- Top header bar -->
      <AppHeader />

      <!-- Dashboard content -->
      <div class="dashboard-content">
        <!-- Welcome section -->
        <section class="welcome-section slide-up delay-1">
          <div class="welcome-text">
            <h1 class="welcome-title">
              Welcome back, <span class="gradient-text">{{ authStore.user?.firstName }}</span>
            </h1>
            <p class="welcome-subtitle">
              Here's an overview about your research projects.
            </p>
          </div>
        </section>

        <!-- Quick stats -->
        <section class="stats-section slide-up delay-2">
          <v-row>
            <v-col cols="12" sm="6" lg="3" v-for="stat in quickStats" :key="stat.label">
              <div class="stat-card glass card-hover">
                <div class="stat-icon" :style="{ background: stat.gradient }">
                  <v-icon :icon="stat.icon" size="24" />
                </div>
                <div class="stat-content">
                  <span class="stat-value font-mono">{{ stat.value }}</span>
                  <span class="stat-label">{{ stat.label }}</span>
                </div>
              </div>
            </v-col>
          </v-row>
        </section>

        <!-- Active projects section -->
        <section class="projects-section slide-up delay-3">
          <div class="section-header">
            <h2 class="section-title">Active Projects</h2>
            <v-btn-toggle v-model="projectsViewMode" mandatory density="compact" class="view-toggle">
              <v-btn value="grid" icon="mdi-view-grid" size="small" />
              <v-btn value="list" icon="mdi-view-list" size="small" />
            </v-btn-toggle>
          </div>

          <!-- Grid View -->
          <v-row v-if="projectsViewMode === 'grid'">
            <v-col 
              cols="12" 
              md="6" 
              v-for="project in projectsStore.activeProjects" 
              :key="project.id"
            >
              <ProjectCard 
                :project="project" 
                @click="navigateToProject(project.id)"
              />
            </v-col>
          </v-row>

          <!-- List View (Table) -->
          <v-card v-else class="projects-table-card glass" :elevation="0">
            <v-data-table
              :headers="projectTableHeaders"
              :items="projectsStore.activeProjects"
              class="projects-table"
              :items-per-page="-1"
              hide-default-footer
              @click:row="(event, { item }) => navigateToProject(item.id)"
            >
              <template v-slot:item.shortTitle="{ item }">
                <div class="project-name-cell">
                  <span class="project-badge" :class="item.useCase.toLowerCase()">{{ item.useCase }}</span>
                  <span class="project-name">{{ item.shortTitle }}</span>
                </div>
              </template>
              <template v-slot:item.wsiCount="{ item }">
                <span class="table-value">{{ item.wsiCount.toLocaleString() }}</span>
              </template>
              <template v-slot:item.datasetCount="{ item }">
                <span class="table-value">{{ item.datasetCount }}</span>
              </template>
              <template v-slot:item.sites="{ item }">
                <span class="table-value">{{ item.sites.length }}</span>
              </template>
              <template v-slot:item.owner="{ item }">
                <span class="table-admin">{{ item.owner }}</span>
              </template>
              <template v-slot:item.status="{ item }">
                <v-chip 
                  size="x-small" 
                  :color="item.status === 'active' ? 'success' : 'warning'" 
                  variant="tonal"
                >
                  {{ item.status }}
                </v-chip>
              </template>
            </v-data-table>
          </v-card>

          <!-- Empty state -->
          <div v-if="projectsStore.activeProjects.length === 0" class="empty-state">
            <v-icon size="64" color="primary" class="mb-4">mdi-folder-open-outline</v-icon>
            <h3>No active projects</h3>
            <p>Start by requesting access to datasets through the Directory.</p>
            <v-btn color="primary" class="mt-4">
              Browse Directory
            </v-btn>
          </div>
        </section>

        <!-- Recent activity section -->
        <section class="activity-section slide-up delay-4">
          <div class="section-header">
            <h2 class="section-title">Recent Activity</h2>
          </div>

          <v-card class="activity-card glass" :elevation="0">
            <v-list bg-color="transparent" class="activity-list">
              <v-list-item
                v-for="activity in recentActivities"
                :key="activity.id"
                :prepend-icon="activity.icon"
                class="activity-item"
              >
                <v-list-item-title>{{ activity.title }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ activity.project }} · {{ activity.time }}
                </v-list-item-subtitle>

                <template v-slot:append>
                  <v-chip 
                    :color="getStatusColor(activity.status)" 
                    size="small"
                    variant="tonal"
                  >
                    {{ activity.status }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card>
        </section>
      </div>
    </v-main>
  </v-layout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProjectsStore } from '@/stores/projects'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import ProjectCard from '@/components/dashboard/ProjectCard.vue'

const router = useRouter()
const authStore = useAuthStore()
const projectsStore = useProjectsStore()

const sidebarRail = ref(false)
const projectsViewMode = ref('grid')

// Project table headers
const projectTableHeaders = [
  { title: 'Project', key: 'shortTitle', sortable: true },
  { title: 'WSIs', key: 'wsiCount', sortable: true, align: 'end' },
  { title: 'Datasets', key: 'datasetCount', sortable: true, align: 'end' },
  { title: 'Sites', key: 'sites', sortable: true, align: 'end' },
  { title: 'Project Admin', key: 'owner', sortable: true },
  { title: 'Status', key: 'status', sortable: true, align: 'center' },
]

// Quick stats data
const quickStats = computed(() => [
  {
    label: 'Active Projects',
    value: projectsStore.activeProjects.length,
    icon: 'mdi-folder-multiple',
    gradient: 'linear-gradient(135deg, #E69830 0%, #D18A28 100%)',
    trend: 12
  },
  {
    label: 'Data Transfers',
    value: '15',
    icon: 'mdi-swap-horizontal',
    gradient: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
    trend: 8
  },
  {
    label: 'Computations',
    value: '23',
    icon: 'mdi-chip',
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
    trend: 0
  },
  {
    label: 'WSI Processed',
    value: '12.4K',
    icon: 'mdi-image-multiple',
    gradient: 'linear-gradient(135deg, #f472b6 0%, #ec4899 100%)',
    trend: 24
  }
])

// Recent activities mock data
const recentActivities = ref([
  {
    id: 1,
    title: 'Data transfer completed',
    project: 'UC7 - CRC Prediction',
    time: '2 hours ago',
    status: 'completed',
    icon: 'mdi-check-circle'
  },
  {
    id: 2,
    title: 'Computation job started',
    project: 'UC8 - Synthetic Data',
    time: '4 hours ago',
    status: 'running',
    icon: 'mdi-play-circle'
  },
  {
    id: 3,
    title: 'Model applied to dataset',
    project: 'UC7 - CRC Prediction',
    time: '1 day ago',
    status: 'completed',
    icon: 'mdi-brain'
  },
  {
    id: 4,
    title: 'New access request submitted',
    project: 'UC7 - XAI Validation',
    time: '2 days ago',
    status: 'pending',
    icon: 'mdi-file-document-edit'
  }
])

function getStatusColor(status) {
  const colors = {
    completed: 'success',
    running: 'info',
    pending: 'warning',
    failed: 'error'
  }
  return colors[status] || 'default'
}

function navigateToProject(projectId) {
  router.push({ name: 'project-detail', params: { id: projectId } })
}

onMounted(async () => {
  await projectsStore.fetchProjects()
})
</script>

<style scoped lang="scss">
// View-specific styles

// Welcome section
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
}

.welcome-title {
  font-size: 2rem;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 0.5rem;
}

.welcome-subtitle {
  font-size: 1rem;
  color: #94a3b8;
}

// Stats section
.stats-section {
  margin-bottom: 2.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  border-radius: 16px;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    padding: 1px;
    background: linear-gradient(135deg, rgba(51, 65, 85, 0.5), transparent);
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
  }
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  .v-icon {
    color: white;
  }
}

.stat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f1f5f9;
}

.stat-label {
  font-size: 0.8125rem;
  color: #94a3b8;
}

// Section headers
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f1f5f9;
}

.view-toggle {
  border: 1px solid rgba(51, 65, 85, 0.5);
  border-radius: 8px;
}

// Projects section
.projects-section {
  margin-bottom: 2.5rem;
}

// Projects table view
.projects-table-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
  overflow: hidden;
}

.projects-table {
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
      cursor: pointer;
      
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

.project-name-cell {
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

.table-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  color: #e2e8f0;
}

.table-admin {
  font-size: 0.875rem;
  color: #94a3b8;
}

// Activity section
.activity-section {
  margin-bottom: 2rem;
}

.activity-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.activity-list {
  padding: 0.5rem;
}

.activity-item {
  border-radius: 12px;
  margin-bottom: 0.25rem;
  
  &:hover {
    background: rgba(51, 65, 85, 0.3);
  }
  
  :deep(.v-list-item__prepend) {
    .v-icon {
      color: #E69830;
    }
  }
}

// Empty state
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(17, 24, 39, 0.5);
  border-radius: 16px;
  border: 1px dashed rgba(51, 65, 85, 0.5);
  
  h3 {
    font-size: 1.25rem;
    color: #f1f5f9;
    margin-bottom: 0.5rem;
  }
  
  p {
    color: #94a3b8;
  }
}

// Responsive
@media (max-width: 960px) {
  .dashboard-content {
    padding: 1.5rem;
  }
  
  .welcome-title {
    font-size: 1.5rem;
  }
}
</style>
