<template>
  <header class="app-header">
    <div class="header-left">
      <!-- Breadcrumb -->
      <nav class="breadcrumb">
        <router-link to="/dashboard" class="breadcrumb-item">
          <v-icon size="small" class="mr-1">mdi-home</v-icon>
          Home
        </router-link>
        <v-icon size="x-small" class="breadcrumb-separator">mdi-chevron-right</v-icon>
        <span class="breadcrumb-item active">{{ currentPageTitle }}</span>
      </nav>
    </div>

    <div class="header-center">
      <!-- Project Selector -->
      <v-menu location="bottom" :close-on-content-click="true" offset="4">
        <template v-slot:activator="{ props }">
          <button class="project-selector" v-bind="props">
            <span class="selector-label">Project:</span>
            <span class="selector-value">{{ selectedProjectName }}</span>
            <v-icon size="14" class="selector-chevron">mdi-unfold-more-horizontal</v-icon>
          </button>
        </template>

        <v-card class="project-dropdown" min-width="240">
          <div class="dropdown-header">Select Project</div>
          <v-divider />
          <div class="dropdown-options">
            <button
              class="dropdown-option"
              :class="{ active: projectsStore.selectedProjectId === null }"
              @click="selectProject(null)"
            >
              <v-icon size="16" class="option-icon">mdi-view-grid-outline</v-icon>
              <span>All Projects</span>
              <v-icon v-if="projectsStore.selectedProjectId === null" size="16" class="check-icon">mdi-check</v-icon>
            </button>
            
            <button
              v-for="project in projectsStore.activeProjects"
              :key="project.id"
              class="dropdown-option"
              :class="{ active: project.id === projectsStore.selectedProjectId }"
              @click="selectProject(project.id)"
            >
              <span class="option-badge" :class="project.useCase.toLowerCase()">{{ project.useCase.replace('UC', '') }}</span>
              <span>{{ project.shortTitle }}</span>
              <v-icon v-if="project.id === projectsStore.selectedProjectId" size="16" class="check-icon">mdi-check</v-icon>
            </button>
          </div>
        </v-card>
      </v-menu>
    </div>

    <div class="header-right">
      <!-- Notifications -->
      <v-menu offset="8" :close-on-content-click="false">
        <template v-slot:activator="{ props }">
          <v-btn 
            icon 
            variant="text" 
            size="small"
            v-bind="props"
            class="header-icon-btn"
          >
            <v-badge
              :content="notificationCount"
              color="error"
              :model-value="notificationCount > 0"
            >
              <v-icon>mdi-bell-outline</v-icon>
            </v-badge>
          </v-btn>
        </template>

        <v-card class="notifications-menu glass" width="360">
          <div class="notifications-header">
            <span class="notifications-title">Notifications</span>
            <v-btn variant="text" size="small" color="primary">Mark all read</v-btn>
          </div>
          <v-divider />
          <v-list density="compact" bg-color="transparent" max-height="320">
            <v-list-item
              v-for="notification in notifications"
              :key="notification.id"
              class="notification-item"
            >
              <template v-slot:prepend>
                <v-avatar 
                  :color="notification.color" 
                  size="36"
                  class="notification-avatar"
                >
                  <v-icon size="18" color="white">{{ notification.icon }}</v-icon>
                </v-avatar>
              </template>
              <v-list-item-title class="notification-text">
                {{ notification.title }}
              </v-list-item-title>
              <v-list-item-subtitle>{{ notification.time }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
          <v-divider />
          <div class="notifications-footer">
            <v-btn variant="text" block>View All Notifications</v-btn>
          </div>
        </v-card>
      </v-menu>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'

const route = useRoute()
const projectsStore = useProjectsStore()
const notificationCount = ref(3)

// Ensure projects are loaded
onMounted(async () => {
  if (projectsStore.projects.length === 0) {
    await projectsStore.fetchProjects()
  }
})

const currentPageTitle = computed(() => {
  return route.meta.title || 'Dashboard'
})

// Project selector computed properties
const selectedProjectName = computed(() => {
  if (!projectsStore.selectedProjectId) return 'All Projects'
  const project = projectsStore.activeProjects.find(p => p.id === projectsStore.selectedProjectId)
  return project?.shortTitle || 'All Projects'
})

function selectProject(projectId) {
  projectsStore.selectProject(projectId)
}

const notifications = ref([
  {
    id: 1,
    title: 'Data transfer completed successfully',
    time: '5 minutes ago',
    icon: 'mdi-check',
    color: 'success'
  },
  {
    id: 2,
    title: 'New computation job queued',
    time: '1 hour ago',
    icon: 'mdi-clock-outline',
    color: 'warning'
  },
  {
    id: 3,
    title: 'Access request approved',
    time: '2 hours ago',
    icon: 'mdi-shield-check',
    color: 'primary'
  }
])

</script>

<style scoped lang="scss">
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  height: 48px;
  border-bottom: 1px solid rgba(51, 65, 85, 0.5);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(12px);
  background: rgba(17, 24, 39, 0.8);
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-center {
  display: flex;
  justify-content: center;
  flex: 1;
  margin: 0 2rem;
}

// Project Selector
.project-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.5rem;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
  
  &:hover {
    background: rgba(51, 65, 85, 0.3);
    
    .selector-value {
      color: #E69830;
    }
    
    .selector-chevron {
      color: #E69830;
    }
  }
}

.selector-label {
  font-size: 0.8125rem;
  color: #64748b;
  font-weight: 500;
}

.selector-value {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #f1f5f9;
  white-space: nowrap;
  transition: color 0.15s;
}

.selector-chevron {
  color: #64748b;
  flex-shrink: 0;
  transition: color 0.15s;
}

// Project dropdown
.project-dropdown {
  background: #0f172a !important;
  border: 1px solid rgba(51, 65, 85, 0.6);
  border-radius: 10px !important;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
}

.dropdown-header {
  padding: 0.625rem 0.875rem;
  font-size: 0.6875rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.dropdown-options {
  padding: 0.375rem;
}

.dropdown-option {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  width: 100%;
  padding: 0.5rem 0.625rem;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8125rem;
  color: #e2e8f0;
  text-align: left;
  transition: all 0.15s;
  
  &:hover {
    background: rgba(51, 65, 85, 0.4);
  }
  
  &.active {
    background: rgba(230, 152, 48, 0.1);
    color: #E69830;
  }
  
  span {
    flex: 1;
  }
}

.option-icon {
  color: #64748b;
  
  .active & {
    color: #E69830;
  }
}

.option-badge {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.625rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  flex-shrink: 0;
  
  &.uc7 {
    background: rgba(230, 152, 48, 0.2);
    color: #E69830;
  }
  
  &.uc8 {
    background: rgba(139, 92, 246, 0.2);
    color: #a78bfa;
  }
}

.check-icon {
  color: #E69830;
  flex-shrink: 0;
}

// Breadcrumb
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.breadcrumb-item {
  color: #64748b;
  display: flex;
  align-items: center;
  text-decoration: none;
  transition: color 0.2s;
  
  &:hover:not(.active) {
    color: #94a3b8;
  }
  
  &.active {
    color: #e2e8f0;
    font-weight: 500;
  }
}

.breadcrumb-separator {
  color: #475569;
}

// Search
.search-wrapper {
  width: 100%;
}

.search-input {
  :deep(.v-field) {
    background: rgba(51, 65, 85, 0.3);
    border: 1px solid rgba(51, 65, 85, 0.5);
    
    &:hover {
          border-color: rgba(230, 152, 48, 0.3);
    }
    
    &:focus-within {
      border-color: #E69830;
    }
  }
  
  :deep(.v-field__input) {
    font-size: 0.875rem;
    
    &::placeholder {
      color: #64748b;
    }
  }
}

.search-shortcut {
  display: flex;
  gap: 0.25rem;
  
  kbd {
    background: rgba(51, 65, 85, 0.5);
    border: 1px solid rgba(71, 85, 105, 0.5);
    border-radius: 4px;
    padding: 0.125rem 0.375rem;
    font-size: 0.6875rem;
    color: #94a3b8;
    font-family: inherit;
  }
}

// Header buttons
.header-icon-btn {
  color: #94a3b8;
  
  &:hover {
    color: #f1f5f9;
    background: rgba(51, 65, 85, 0.3);
  }
}

// Notifications menu
.notifications-menu {
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
}

.notifications-title {
  font-weight: 600;
  color: #f1f5f9;
}

.notification-item {
  &:hover {
    background: rgba(51, 65, 85, 0.3);
  }
}

.notification-avatar {
  opacity: 0.9;
}

.notification-text {
  font-size: 0.8125rem;
}

.notifications-footer {
  padding: 0.5rem;
}

// Responsive
@media (max-width: 960px) {
  .header-center {
    display: none;
  }
}
</style>
