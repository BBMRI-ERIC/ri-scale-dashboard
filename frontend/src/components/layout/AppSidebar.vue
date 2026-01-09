<template>
  <v-navigation-drawer
    :rail="rail"
    permanent
    class="app-sidebar"
  >
    <!-- Settings Dialog -->
    <SettingsDialog v-model="showSettings" />
    <!-- Logo section -->
    <div class="sidebar-header" @click="$emit('toggle-rail')">
      <div class="logo-icon">
        <img src="/logo-32.png" alt="RI-SCALE" width="24" height="24" />
      </div>
      <transition name="fade">
        <span v-if="!rail" class="logo-text gradient-text">RI-SCALE</span>
      </transition>
    </div>

    <!-- Main navigation -->
    <v-list density="comfortable" nav class="sidebar-nav">
      <v-list-item
        v-for="item in mainNavItems"
        :key="item.title"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="item.title"
        rounded="lg"
        class="nav-item"
      >
        <template v-slot:append v-if="item.badge && !rail">
          <v-badge
            :content="item.badge"
            color="primary"
            inline
          />
        </template>
      </v-list-item>
    </v-list>

    <!-- Projects section -->
    <template v-if="!rail">
      <div class="sidebar-section-title">
        <span>PROJECT SELECTION</span>
      </div>
    </template>

    <v-list density="comfortable" nav class="project-nav">
      <!-- All projects option -->
      <v-list-item
        :active="projectsStore.selectedProjectId === null"
        rounded="lg"
        class="project-item all-projects"
        @click="selectProject(null)"
      >
        <template v-slot:prepend>
          <div class="project-indicator all">
            <v-icon size="16">mdi-view-grid</v-icon>
          </div>
        </template>
        <v-list-item-title v-if="!rail" class="project-title">
          All Projects
        </v-list-item-title>
      </v-list-item>

      <!-- Divider between All and individual projects -->
      <v-divider class="my-2 mx-3" />

      <!-- Individual projects -->
      <v-list-item
        v-for="project in projectsStore.activeProjects.slice(0, 4)"
        :key="project.id"
        :active="project.id === projectsStore.selectedProjectId"
        rounded="lg"
        class="project-item"
        @click="selectProject(project.id)"
      >
        <template v-slot:prepend>
          <div 
            class="project-indicator" 
            :class="project.useCase.toLowerCase()"
          >
            {{ project.useCase.replace('UC', '') }}
          </div>
        </template>
        <v-list-item-title v-if="!rail" class="project-title">
          {{ project.shortTitle }}
        </v-list-item-title>
      </v-list-item>
    </v-list>

    <v-spacer />

    <!-- Bottom section -->
    <div class="sidebar-bottom">
      <v-divider class="my-2 mx-3" />
      
      <v-list density="comfortable" nav>
        <v-list-item
          v-for="item in bottomNavItems"
          :key="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          rounded="lg"
          class="nav-item"
        />
      </v-list>

      <!-- User section -->
      <div class="user-section" :class="{ 'rail-mode': rail }">
        <v-menu location="top" offset="8">
          <template v-slot:activator="{ props }">
            <div class="user-card" v-bind="props">
              <v-avatar 
                :size="rail ? 32 : 40" 
                class="user-avatar"
                color="primary"
              >
                <span class="avatar-text">{{ authStore.userInitials }}</span>
              </v-avatar>
              <transition name="fade">
                <div v-if="!rail" class="user-info">
                  <span class="user-name">{{ authStore.userName }}</span>
                  <span class="user-role">{{ primaryRole }}</span>
                </div>
              </transition>
              <v-icon v-if="!rail" size="small" class="menu-icon">
                mdi-chevron-up
              </v-icon>
            </div>
          </template>

          <v-card class="user-menu glass" min-width="200">
            <v-list density="compact" bg-color="transparent">
              <v-list-item 
                prepend-icon="mdi-cog" 
                title="Settings"
                @click="openSettings"
              />
              <v-divider class="my-1" />
              <v-list-item 
                prepend-icon="mdi-logout" 
                title="Sign Out"
                @click="handleLogout"
                class="logout-item"
              />
            </v-list>
          </v-card>
        </v-menu>
      </div>
    </div>
  </v-navigation-drawer>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProjectsStore } from '@/stores/projects'
import SettingsDialog from '@/components/settings/SettingsDialog.vue'

const props = defineProps({
  rail: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:rail', 'toggle-rail'])

const router = useRouter()
const authStore = useAuthStore()
const projectsStore = useProjectsStore()

// Settings dialog state
const showSettings = ref(false)

function openSettings() {
  showSettings.value = true
}

// Navigation items
const mainNavItems = [
  { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/dashboard' },
  { title: 'Directory', icon: 'mdi-database-search', to: '/directory' },
  { title: 'Negotiator', icon: 'mdi-handshake', to: '/negotiator' },
  { title: 'Datasets', icon: 'mdi-database', to: '/datasets' },
  { title: 'Data Transfers', icon: 'mdi-swap-horizontal', to: '/transfers' },
  { title: 'HPC Jobs', icon: 'mdi-chip', to: '/computations' },
  { title: 'Model Hub', icon: 'mdi-brain', to: '/models' },
  { title: 'Compute Quotas', icon: 'mdi-server', to: '/resources' },
]

const bottomNavItems = [
  { title: 'About', icon: 'mdi-information-outline', to: '/about' },
  { title: 'Settings', icon: 'mdi-cog', to: '/settings' },
]

const primaryRole = computed(() => {
  const roles = authStore.userRoles
  if (roles.includes('admin')) return 'Administrator'
  if (roles.includes('project_admin')) return 'Project Admin'
  if (roles.includes('researcher')) return 'Researcher'
  return 'User'
})

function selectProject(projectId) {
  projectsStore.selectProject(projectId)
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped lang="scss">
.app-sidebar {
  background: #111827 !important;
  border-right: 1px solid rgba(51, 65, 85, 0.5) !important;
}

// Logo
.sidebar-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: opacity 0.2s;
  height: 48px;
  box-sizing: border-box;
  border-bottom: 1px solid rgba(51, 65, 85, 0.5);
  margin-right: -1px; // Extend border under the vertical border
  
  &:hover {
    opacity: 0.8;
  }
}

.logo-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
  
  svg {
    width: 100%;
    height: 100%;
  }
}

.logo-text {
  font-size: 1.125rem;
  font-weight: 700;
  letter-spacing: 0.03em;
}

// Navigation
.sidebar-nav {
  padding: 0.75rem 0.5rem 0;
  
  :deep(.v-list-item__prepend) {
    width: 24px;
    margin-inline-end: 16px !important;
  }
}

.nav-item {
  margin-bottom: 0.25rem;
  
  &:hover {
    background: rgba(230, 152, 48, 0.08);
  }
  
  &.v-list-item--active {
    background: rgba(230, 152, 48, 0.15);
    
    :deep(.v-list-item__prepend .v-icon) {
      color: #E69830;
    }
    
    :deep(.v-list-item-title) {
      color: #E69830;
      font-weight: 500;
    }
  }
}

// Section title
.sidebar-section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1rem 0.5rem;
  font-size: 0.6875rem;
  font-weight: 600;
  color: #64748b;
  letter-spacing: 0.1em;
}

// Project nav
.project-nav {
  padding: 0 0.5rem;
  
  :deep(.v-list-item__prepend) {
    width: 24px;
    margin-inline-end: 16px !important;
  }
}

.project-item {
  margin-bottom: 0.25rem;
  
  &:hover {
    background: rgba(51, 65, 85, 0.3);
  }
  
  &.v-list-item--active {
    background: rgba(230, 152, 48, 0.1);
    border-left: 2px solid #E69830;
  }
}

.project-indicator {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  
  &.all {
    background: rgba(100, 116, 139, 0.2);
    color: #94a3b8;
  }
  
  &.uc7 {
    background: rgba(230, 152, 48, 0.2);
    color: #E69830;
  }
  
  &.uc8 {
    background: rgba(139, 92, 246, 0.2);
    color: #a78bfa;
  }
}

.project-title {
  font-size: 0.8125rem;
  color: #e2e8f0;
}

.progress-text {
  font-size: 0.5rem;
  font-family: 'JetBrains Mono', monospace;
}

// Bottom section
.sidebar-bottom {
  padding-bottom: 0.5rem;
  
  .v-list {
    padding: 0 0.5rem;
    
    :deep(.v-list-item__prepend) {
      width: 24px;
      margin-inline-end: 16px !important;
    }
  }
}

// User section
.user-section {
  padding: 0.5rem;
  
  &.rail-mode {
    padding: 0.5rem 0.25rem;
  }
}

.user-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
  
  &:hover {
    background: rgba(51, 65, 85, 0.3);
  }
}

.user-avatar {
  flex-shrink: 0;
  background: linear-gradient(135deg, #E69830 0%, #D18A28 100%);
  
  .avatar-text {
    font-size: 0.75rem;
    font-weight: 600;
    color: #0a0f1a;
  }
}

.user-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #f1f5f9;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 0.75rem;
  color: #64748b;
}

.menu-icon {
  color: #64748b;
}

// User menu
.user-menu {
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.logout-item {
  color: #ef4444;
  
  :deep(.v-list-item__prepend .v-icon) {
    color: #ef4444;
  }
}

// Transitions
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
