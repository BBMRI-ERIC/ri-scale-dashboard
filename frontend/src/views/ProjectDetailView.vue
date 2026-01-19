<template>
  <v-layout class="dashboard-layout">
    <!-- Sidebar -->
    <AppSidebar v-model:rail="sidebarRail" />

    <!-- Main content area -->
    <v-main class="dashboard-main">
      <!-- Top header bar -->
      <AppHeader />

      <!-- Project content -->
      <div class="project-content" v-if="project">
        <!-- Project header -->
        <section class="project-header slide-up delay-1">
          <div class="header-top">
            <v-btn 
              variant="text" 
              prepend-icon="mdi-arrow-left"
              @click="$router.push('/dashboard')"
              class="back-btn"
            >
              Back to Dashboard
            </v-btn>
            <div class="header-actions">
              <v-btn variant="outlined" prepend-icon="mdi-cog">Settings</v-btn>
              <v-btn color="primary" prepend-icon="mdi-play">Run Computation</v-btn>
            </div>
          </div>

          <div class="project-info">
            <div class="project-badge" :class="project.useCase.toLowerCase()">
              {{ project.useCase }}
            </div>
            <h1 class="project-title">{{ project.title }}</h1>
            <p class="project-description">{{ project.description }}</p>
            
            <div class="project-meta">
              <div class="meta-item">
                <v-icon size="16">mdi-calendar</v-icon>
                <span>Valid until {{ project.validUntil }}</span>
              </div>
              <div class="meta-item">
                <v-icon size="16">mdi-clock-outline</v-icon>
                <span>Last activity: {{ project.lastActivity }}</span>
              </div>
              <v-chip 
                :color="project.status === 'active' ? 'success' : 'warning'" 
                size="small"
                variant="tonal"
              >
                {{ project.status }}
              </v-chip>
            </div>
          </div>
        </section>

        <!-- Progress overview -->
        <section class="progress-overview slide-up delay-2">
          <v-card class="glass" :elevation="0">
            <v-card-text>
              <div class="progress-header">
                <h3>Overall Progress</h3>
                <span class="progress-percentage font-mono">{{ project.progress }}%</span>
              </div>
              <v-progress-linear
                :model-value="project.progress"
                color="primary"
                height="12"
                rounded
              />
              <div class="progress-stages">
                <div 
                  v-for="stage in progressStages" 
                  :key="stage.label"
                  class="stage-item"
                  :class="{ completed: stage.completed, active: stage.active }"
                >
                  <div class="stage-indicator">
                    <v-icon v-if="stage.completed" size="16">mdi-check</v-icon>
                    <span v-else>{{ stage.step }}</span>
                  </div>
                  <span class="stage-label">{{ stage.label }}</span>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </section>

        <!-- Stats and actions grid -->
        <section class="content-grid slide-up delay-3">
          <v-row>
            <!-- Data Transfers -->
            <v-col cols="12" md="4">
              <v-card class="stat-card glass" :elevation="0">
                <v-card-text>
                  <div class="stat-header">
                    <div class="stat-icon transfers">
                      <v-icon>mdi-swap-horizontal</v-icon>
                    </div>
                    <h4>Data Transfers</h4>
                  </div>
                  <div class="stat-numbers">
                    <div class="number-item">
                      <span class="number">{{ project.stats.dataTransfers.completed }}</span>
                      <span class="label">Completed</span>
                    </div>
                    <div class="number-item">
                      <span class="number">{{ project.stats.dataTransfers.pending }}</span>
                      <span class="label">Pending</span>
                    </div>
                  </div>
                  <v-btn block variant="tonal" color="primary" class="mt-4">
                    Manage Transfers
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Computations -->
            <v-col cols="12" md="4">
              <v-card class="stat-card glass" :elevation="0">
                <v-card-text>
                  <div class="stat-header">
                    <div class="stat-icon computations">
                      <v-icon>mdi-chip</v-icon>
                    </div>
                    <h4>Computations</h4>
                  </div>
                  <div class="stat-numbers">
                    <div class="number-item">
                      <span class="number">{{ project.stats.computations.running }}</span>
                      <span class="label">Running</span>
                    </div>
                    <div class="number-item">
                      <span class="number">{{ project.stats.computations.queued }}</span>
                      <span class="label">Queued</span>
                    </div>
                  </div>
                  <v-btn block variant="tonal" color="primary" class="mt-4">
                    View Jobs
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Models -->
            <v-col cols="12" md="4">
              <v-card class="stat-card glass" :elevation="0">
                <v-card-text>
                  <div class="stat-header">
                    <div class="stat-icon models">
                      <v-icon>mdi-brain</v-icon>
                    </div>
                    <h4>AI Models</h4>
                  </div>
                  <div class="stat-numbers">
                    <div class="number-item">
                      <span class="number">{{ project.stats.models.applied }}</span>
                      <span class="label">Applied</span>
                    </div>
                    <div class="number-item">
                      <span class="number">{{ project.stats.models.available }}</span>
                      <span class="label">Available</span>
                    </div>
                  </div>
                  <v-btn block variant="tonal" color="primary" class="mt-4">
                    Browse Models
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </section>

        <!-- Sites involved -->
        <section class="sites-section slide-up delay-4">
          <h3 class="section-title">Sites Involved</h3>
          <div class="sites-grid">
            <div v-for="site in project.sites" :key="site" class="site-card glass">
              <div class="site-avatar">
                {{ site.split('-')[1]?.[0] || site[0] }}
              </div>
              <div class="site-info">
                <span class="site-name">{{ site }}</span>
                <span class="site-status">
                  <span class="status-dot online"></span>
                  Connected
                </span>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- Loading state -->
      <div v-else class="loading-state">
        <v-progress-circular indeterminate color="primary" size="48" />
        <p>Loading project details...</p>
      </div>
    </v-main>
  </v-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const route = useRoute()
const projectsStore = useProjectsStore()

const sidebarRail = ref(false)

const project = computed(() => 
  projectsStore.getProjectById(route.params.id)
)

const progressStages = computed(() => {
  if (!project.value) return []
  const progress = project.value.progress
  return [
    { step: 1, label: 'Data Access', completed: progress >= 25, active: progress < 25 },
    { step: 2, label: 'Transfer', completed: progress >= 50, active: progress >= 25 && progress < 50 },
    { step: 3, label: 'Processing', completed: progress >= 75, active: progress >= 50 && progress < 75 },
    { step: 4, label: 'Results', completed: progress >= 100, active: progress >= 75 && progress < 100 },
  ]
})

onMounted(async () => {
  if (projectsStore.projects.length === 0) {
    await projectsStore.fetchProjects()
  }
})
</script>

<style scoped lang="scss">
// View-specific styles
.project-content {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

// Project header
.project-header {
  margin-bottom: 2rem;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.back-btn {
  color: #94a3b8;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.project-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
  
  &.uc7 {
    background: rgba(230, 152, 48, 0.15);
    color: #E69830;
  }
  
  &.uc8 {
    background: rgba(139, 92, 246, 0.15);
    color: #a78bfa;
  }
}

.project-title {
  font-size: 2rem;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 0.75rem;
}

.project-description {
  font-size: 1rem;
  color: #94a3b8;
  margin-bottom: 1rem;
  max-width: 800px;
}

.project-meta {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #64748b;
  
  .v-icon {
    color: #64748b;
  }
}

// Progress overview
.progress-overview {
  margin-bottom: 2rem;
  
  .v-card {
    border: 1px solid rgba(51, 65, 85, 0.5);
  }
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  
  h3 {
    font-size: 1rem;
    font-weight: 600;
    color: #f1f5f9;
  }
}

.progress-percentage {
  font-size: 1.5rem;
  font-weight: 700;
  color: #E69830;
}

.progress-stages {
  display: flex;
  justify-content: space-between;
  margin-top: 1.5rem;
}

.stage-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  
  &.completed {
    .stage-indicator {
      background: #E69830;
      color: #0a0f1a;
    }
    .stage-label {
      color: #E69830;
    }
  }
  
  &.active {
    .stage-indicator {
      background: rgba(230, 152, 48, 0.2);
      color: #E69830;
      animation: pulse 2s infinite;
    }
  }
}

.stage-indicator {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(51, 65, 85, 0.5);
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 600;
}

.stage-label {
  font-size: 0.75rem;
  color: #64748b;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(230, 152, 48, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(230, 152, 48, 0);
  }
}

// Stats cards
.content-grid {
  margin-bottom: 2rem;
}

.stat-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
  height: 100%;
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  
  h4 {
    font-size: 1rem;
    font-weight: 600;
    color: #f1f5f9;
  }
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &.transfers {
    background: rgba(59, 130, 246, 0.2);
    color: #3b82f6;
  }
  
  &.computations {
    background: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
  }
  
  &.models {
    background: rgba(244, 114, 182, 0.2);
    color: #f472b6;
  }
}

.stat-numbers {
  display: flex;
  gap: 2rem;
}

.number-item {
  display: flex;
  flex-direction: column;
  
  .number {
    font-size: 1.75rem;
    font-weight: 700;
    color: #f1f5f9;
    font-family: 'JetBrains Mono', monospace;
  }
  
  .label {
    font-size: 0.75rem;
    color: #64748b;
  }
}

// Sites section
.sites-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 1rem;
}

.sites-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.site-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.site-avatar {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #E69830, #D18A28);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  color: #0a0f1a;
}

.site-info {
  display: flex;
  flex-direction: column;
}

.site-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #f1f5f9;
}

.site-status {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: #10b981;
}

// Loading state
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  gap: 1rem;
  
  p {
    color: #94a3b8;
  }
}
</style>
