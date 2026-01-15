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

    <!-- Global Navigation -->
    <v-list density="comfortable" nav class="sidebar-nav">
      <v-list-item
        v-for="item in globalNavItems"
        :key="item.title"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="item.title"
        rounded="lg"
        class="nav-item"
      />
    </v-list>

    <!-- Project Context Section -->
    <div class="section-divider" v-if="!rail">
      <span class="section-label">{{ selectedProjectLabel }}</span>
    </div>
    <v-divider v-else class="mx-3 my-2" />

    <v-list density="comfortable" nav class="sidebar-nav project-nav">
      <v-list-item
        v-for="item in projectNavItems"
        :key="item.title"
        :to="item.to"
        :prepend-icon="item.icon"
        :title="item.title"
        rounded="lg"
        class="nav-item"
      />
    </v-list>

    <!-- BBMRI-ERIC External Links -->
    <div class="section-divider" v-if="!rail">
      <span class="section-label">BBMRI-ERIC</span>
    </div>
    <v-divider v-else class="mx-3 my-2" />

    <v-list density="comfortable" nav class="sidebar-nav external-nav">
      <v-list-item
        v-for="item in externalNavItems"
        :key="item.title"
        :href="item.href"
        target="_blank"
        :prepend-icon="item.icon"
        :title="item.title"
        rounded="lg"
        class="nav-item"
      >
        <template v-slot:append v-if="!rail">
          <v-icon size="14" class="external-icon">mdi-open-in-new</v-icon>
        </template>
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

// Global navigation (project-independent)
const globalNavItems = [
  { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/dashboard' },
  { title: 'Model Hub', icon: 'mdi-brain', to: '/models' },
]

// Project-dependent navigation
const projectNavItems = [
  { title: 'Datasets', icon: 'mdi-database', to: '/datasets' },
  { title: 'Data Transfers', icon: 'mdi-swap-horizontal', to: '/transfers' },
  { title: 'HPC Jobs', icon: 'mdi-chip', to: '/computations' },
  { title: 'Compute Quotas', icon: 'mdi-server', to: '/resources' },
]

// External BBMRI-ERIC links
const externalNavItems = [
  { title: 'Directory', icon: 'mdi-database-search', href: 'https://directory.bbmri-eric.eu/ERIC/directory/#/catalogue' },
  { title: 'Negotiator', icon: 'mdi-handshake', href: 'https://negotiator.bbmri-eric.eu/' },
]

// Selected project label
const selectedProjectLabel = computed(() => {
  if (!projectsStore.selectedProjectId) {
    return 'Project: All'
  }
  const project = projectsStore.activeProjects.find(p => p.id === projectsStore.selectedProjectId)
  return project ? `Project: ${project.shortTitle}` : 'Project: All'
})

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

.external-icon {
  color: #64748b;
  opacity: 0.7;
}

// Section dividers
.section-divider {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem 0.375rem;
  gap: 0.5rem;
  
  &::before,
  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(51, 65, 85, 0.5);
  }
  
  &::before {
    flex: 0;
    width: 0;
  }
}

.section-label {
  font-size: 0.625rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  white-space: nowrap;
}

.project-nav,
.external-nav {
  padding-top: 0.25rem !important;
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
