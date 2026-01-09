<template>
  <v-dialog 
    v-model="isOpen" 
    max-width="640"
    :scrim="true"
    scrim-class="settings-scrim"
  >
    <v-card class="settings-dialog glass">
      <!-- Dialog header -->
      <div class="dialog-header">
        <h2 class="dialog-title">Settings</h2>
        <v-btn 
          icon="mdi-close" 
          variant="text" 
          size="small"
          @click="close"
        />
      </div>

      <!-- Tabs navigation -->
      <v-tabs 
        v-model="activeTab" 
        bg-color="transparent"
        color="primary"
        class="settings-tabs"
      >
        <v-tab value="profile">
          <v-icon start size="18">mdi-account</v-icon>
          Profile
        </v-tab>
        <v-tab value="preferences">
          <v-icon start size="18">mdi-palette</v-icon>
          Preferences
        </v-tab>
        <v-tab value="notifications">
          <v-icon start size="18">mdi-bell</v-icon>
          Notifications
        </v-tab>
      </v-tabs>

      <v-divider />

      <!-- Tab content -->
      <v-card-text class="dialog-content">
        <v-tabs-window v-model="activeTab">
          <!-- Profile Tab -->
          <v-tabs-window-item value="profile">
            <div class="tab-section">
              <!-- Avatar section -->
              <div class="avatar-section">
                <v-avatar size="80" class="user-avatar-large">
                  <span class="avatar-text">{{ authStore.userInitials }}</span>
                </v-avatar>
                <div class="avatar-actions">
                  <v-btn variant="tonal" size="small" prepend-icon="mdi-upload">
                    Upload Photo
                  </v-btn>
                  <v-btn variant="text" size="small" color="error">
                    Remove
                  </v-btn>
                </div>
              </div>

              <!-- Profile form -->
              <v-form ref="profileFormRef" class="profile-form">
                <v-row>
                  <v-col cols="12" sm="6">
                    <v-text-field
                      v-model="profileForm.firstName"
                      label="First Name"
                      :rules="[rules.required]"
                    />
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-text-field
                      v-model="profileForm.lastName"
                      label="Last Name"
                      :rules="[rules.required]"
                    />
                  </v-col>
                  <v-col cols="12">
                    <v-text-field
                      v-model="profileForm.email"
                      label="Email"
                      type="email"
                      :rules="[rules.required, rules.email]"
                      prepend-inner-icon="mdi-email-outline"
                    />
                  </v-col>
                  <v-col cols="12">
                    <v-text-field
                      v-model="profileForm.organization"
                      label="Organization"
                      prepend-inner-icon="mdi-domain"
                    />
                  </v-col>
                  <v-col cols="12">
                    <v-text-field
                      v-model="profileForm.department"
                      label="Department"
                      prepend-inner-icon="mdi-account-group"
                    />
                  </v-col>
                </v-row>
              </v-form>
            </div>
          </v-tabs-window-item>

          <!-- Preferences Tab -->
          <v-tabs-window-item value="preferences">
            <div class="tab-section">
              <h3 class="section-title">Appearance</h3>
              
              <div class="preference-item">
                <div class="preference-info">
                  <span class="preference-label">Theme</span>
                  <span class="preference-description">Choose your preferred color theme</span>
                </div>
                <v-btn-toggle
                  v-model="preferences.theme"
                  mandatory
                  rounded="lg"
                  density="compact"
                  class="theme-toggle"
                >
                  <v-btn value="dark" size="small">
                    <v-icon start size="16">mdi-weather-night</v-icon>
                    Dark
                  </v-btn>
                  <v-btn value="light" size="small" disabled>
                    <v-icon start size="16">mdi-weather-sunny</v-icon>
                    Light
                  </v-btn>
                  <v-btn value="system" size="small" disabled>
                    <v-icon start size="16">mdi-laptop</v-icon>
                    System
                  </v-btn>
                </v-btn-toggle>
              </div>

              <v-divider class="my-4" />

              <h3 class="section-title">Dashboard</h3>

              <div class="preference-item">
                <div class="preference-info">
                  <span class="preference-label">Compact Sidebar</span>
                  <span class="preference-description">Show sidebar in collapsed mode by default</span>
                </div>
                <v-switch
                  v-model="preferences.compactSidebar"
                  color="primary"
                  hide-details
                  inset
                />
              </div>

              <div class="preference-item">
                <div class="preference-info">
                  <span class="preference-label">Show Quick Stats</span>
                  <span class="preference-description">Display statistics cards on dashboard</span>
                </div>
                <v-switch
                  v-model="preferences.showQuickStats"
                  color="primary"
                  hide-details
                  inset
                />
              </div>

              <div class="preference-item">
                <div class="preference-info">
                  <span class="preference-label">Default Project View</span>
                  <span class="preference-description">How to display projects on dashboard</span>
                </div>
                <v-select
                  v-model="preferences.projectView"
                  :items="projectViewOptions"
                  density="compact"
                  hide-details
                  style="max-width: 140px"
                />
              </div>

            </div>
          </v-tabs-window-item>

          <!-- Notifications Tab -->
          <v-tabs-window-item value="notifications">
            <div class="tab-section">
              <h3 class="section-title">Email Notifications</h3>

              <div class="preference-item">
                <div class="preference-info">
                  <span class="preference-label">Project Updates</span>
                  <span class="preference-description">Receive emails about project status changes</span>
                </div>
                <v-switch
                  v-model="notifications.projectUpdates"
                  color="primary"
                  hide-details
                  inset
                />
              </div>

              <div class="preference-item">
                <div class="preference-info">
                  <span class="preference-label">Data Transfers</span>
                  <span class="preference-description">Get notified when transfers complete or fail</span>
                </div>
                <v-switch
                  v-model="notifications.dataTransfers"
                  color="primary"
                  hide-details
                  inset
                />
              </div>

              <div class="preference-item">
                <div class="preference-info">
                  <span class="preference-label">Computation Jobs</span>
                  <span class="preference-description">Receive updates about job status</span>
                </div>
                <v-switch
                  v-model="notifications.computationJobs"
                  color="primary"
                  hide-details
                  inset
                />
              </div>

            </div>
          </v-tabs-window-item>
        </v-tabs-window>
      </v-card-text>

      <!-- Dialog footer -->
      <v-divider />
      <div class="dialog-footer">
        <v-btn variant="text" @click="close">Cancel</v-btn>
        <v-btn 
          color="primary" 
          @click="saveSettings"
          :loading="isSaving"
        >
          Save Changes
        </v-btn>
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useSettingsStore } from '@/stores/settings'

const authStore = useAuthStore()
const settingsStore = useSettingsStore()

// Dialog state
const isOpen = defineModel({ type: Boolean, default: false })
const activeTab = ref('profile')
const isSaving = ref(false)
const profileFormRef = ref(null)

// Form data
const profileForm = reactive({
  firstName: '',
  lastName: '',
  email: '',
  organization: '',
  department: ''
})

const preferences = reactive({
  theme: 'dark',
  compactSidebar: false,
  showQuickStats: true,
  projectView: 'grid'
})

const notifications = reactive({
  projectUpdates: true,
  dataTransfers: true,
  computationJobs: true
})

const projectViewOptions = ['grid', 'list', 'compact']

// Validation rules
const rules = {
  required: v => !!v || 'This field is required',
  email: v => /.+@.+\..+/.test(v) || 'Invalid email address'
}

// Load user data when dialog opens
watch(isOpen, (open) => {
  if (open) {
    loadUserData()
    loadSettings()
  }
})

function loadUserData() {
  const user = authStore.user
  if (user) {
    profileForm.firstName = user.firstName || ''
    profileForm.lastName = user.lastName || ''
    profileForm.email = user.email || ''
    profileForm.organization = user.organization || ''
    profileForm.department = user.department || ''
  }
}

function loadSettings() {
  const saved = settingsStore.settings
  preferences.theme = saved.theme || 'dark'
  preferences.compactSidebar = saved.compactSidebar || false
  preferences.showQuickStats = saved.showQuickStats ?? true
  preferences.projectView = saved.projectView || 'grid'
  
  notifications.projectUpdates = saved.notifications?.projectUpdates ?? true
  notifications.dataTransfers = saved.notifications?.dataTransfers ?? true
  notifications.computationJobs = saved.notifications?.computationJobs ?? true
}

async function saveSettings() {
  // Validate profile form if on profile tab
  if (activeTab.value === 'profile') {
    const { valid } = await profileFormRef.value.validate()
    if (!valid) return
  }

  isSaving.value = true
  
  try {
    // Save settings to store
    await settingsStore.updateSettings({
      theme: preferences.theme,
      compactSidebar: preferences.compactSidebar,
      showQuickStats: preferences.showQuickStats,
      projectView: preferences.projectView,
      notifications: {
        projectUpdates: notifications.projectUpdates,
        dataTransfers: notifications.dataTransfers,
        computationJobs: notifications.computationJobs
      }
    })

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    close()
  } finally {
    isSaving.value = false
  }
}

function close() {
  isOpen.value = false
}
</script>

<style scoped lang="scss">
.settings-dialog {
  border: 1px solid rgba(51, 65, 85, 0.5);
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
}

.dialog-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f1f5f9;
}

.settings-tabs {
  :deep(.v-tab) {
    text-transform: none;
    font-weight: 500;
    letter-spacing: 0;
  }
}

.dialog-content {
  padding: 1.5rem !important;
  min-height: 400px;
  max-height: 60vh;
  overflow-y: auto;
}

.tab-section {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

// Avatar section
.avatar-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 1.25rem;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 12px;
}

.user-avatar-large {
  background: linear-gradient(135deg, #E69830 0%, #D18A28 100%);
  flex-shrink: 0;
  
  .avatar-text {
    font-size: 1.5rem;
    font-weight: 600;
    color: #0a0f1a;
  }
}

.avatar-actions {
  display: flex;
  gap: 0.5rem;
}

// Profile form
.profile-form {
  :deep(.v-field) {
    background: rgba(30, 41, 59, 0.3);
  }
}

// Section title
.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
}

// Preference items
.preference-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  gap: 1rem;
}

.preference-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.preference-label {
  font-size: 0.9375rem;
  font-weight: 500;
  color: #f1f5f9;
}

.preference-description {
  font-size: 0.8125rem;
  color: #64748b;
}

.theme-toggle {
  border: 1px solid rgba(51, 65, 85, 0.5);
  
  :deep(.v-btn) {
    text-transform: none;
  }
}

// Footer
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
}
</style>
