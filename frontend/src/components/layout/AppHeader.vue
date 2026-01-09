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

      <!-- Status indicator -->
      <div class="status-indicator">
        <span class="status-dot online"></span>
        <span class="status-text">Connected</span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const notificationCount = ref(3)

const currentPageTitle = computed(() => {
  return route.meta.title || 'Dashboard'
})

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
  flex: 1;
  max-width: 480px;
  margin: 0 2rem;
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

// Status indicator
.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.status-text {
  font-size: 0.75rem;
  color: #10b981;
  font-weight: 500;
}

// Responsive
@media (max-width: 960px) {
  .header-center {
    display: none;
  }
  
  .status-indicator .status-text {
    display: none;
  }
}
</style>
