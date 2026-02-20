<template>
  <v-dialog 
    :model-value="modelValue" 
    @update:model-value="emit('update:modelValue', $event)"
    :max-width="maxWidth"
    persistent
  >
    <v-card class="file-dialog glass">
      <!-- Header -->
      <div class="dialog-header">
        <h2 class="dialog-title">
          <v-icon class="mr-2">mdi-folder-open</v-icon>
          {{ title || 'Select File' }}
        </h2>
        <v-btn 
          icon 
          size="small" 
          @click="emit('update:modelValue', false)"
          variant="plain"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>

      <v-divider />

      <!-- Toolbar with actions -->
      <div class="toolbar-section">
        <v-btn
          size="small"
          variant="tonal"
          prepend-icon="mdi-folder-plus"
          @click="showCreateFolderDialog = true"
          class="mr-2"
        >
          New Folder
        </v-btn>
        </div>

      <v-divider />

      <!-- Breadcrumb Navigation -->
      <div class="breadcrumb-section">
        <div class="breadcrumb">
          <v-btn
            size="small"
            variant="text"
            prepend-icon="mdi-home"
            @click="navigateHome"
            :color="isAtRoot ? 'primary' : 'default'"
          >
            {{ mode === 'filesystem' ? (initialPathName || 'Root') : 'Root' }}
          </v-btn>
          <span v-if="currentPath" class="breadcrumb-separator">/</span>
          <template v-for="(part, index) in breadcrumbParts" :key="index">
            <v-btn 
              size="small" 
              variant="text"
              @click="navigateTo(breadcrumbPaths[index])"
              :color="index === breadcrumbParts.length - 1 ? 'primary' : 'default'"
            >
              {{ part }}
            </v-btn>
            <span v-if="index < breadcrumbParts.length - 1" class="breadcrumb-separator">/</span>
          </template>
        </div>
      </div>

      <v-divider />

      <!-- Content Area -->
      <v-card-text class="file-browser">
        <!-- Loading State -->
        <div v-if="isLoading" class="loading-container">
          <v-progress-circular 
            indeterminate 
            color="primary" 
            size="48"
          />
          <p class="mt-4 text-body-2">Loading directory...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="error-container">
          <v-icon color="error" size="48" class="mb-2">mdi-alert-circle</v-icon>
          <p class="text-error text-body-2">{{ error }}</p>
          <v-btn 
            size="small" 
            variant="tonal" 
            @click="refreshDirectory"
            class="mt-4"
          >
            Retry
          </v-btn>
        </div>

        <!-- Empty Directory -->
        <div v-else-if="entries.length === 0" class="empty-container">
          <v-icon color="medium-emphasis" size="48" class="mb-2">mdi-folder-open-outline</v-icon>
          <p class="text-medium-emphasis text-body-2">This directory is empty</p>
        </div>

        <!-- Directory Listing -->
        <div v-else class="entries-list">
          <!-- Parent Directory Link -->
          <div 
            v-if="parentPath !== null" 
            class="entry parent-entry"
            @click="navigateTo(parentPath)"
          >
            <v-icon class="entry-icon">mdi-arrow-up</v-icon>
            <span class="entry-name">..</span>
            <span class="entry-type">(Parent Directory)</span>
          </div>

          <!-- File/Folder Entries -->
          <div 
            v-for="entry in entries" 
            :key="entry.path"
            class="entry"
            :class="{ 
              'is-directory': entry.type === 'directory',
              'is-selected': selectedPath === entry.path
            }"
            @click="selectEntry(entry)"
            @dblclick="doubleClickEntry(entry)"
          >
            <v-icon class="entry-icon">
              {{ entry.type === 'directory' ? 'mdi-folder' : getFileIcon(entry.name) }}
            </v-icon>
            <div class="entry-content">
              <span class="entry-name">{{ entry.name }}</span>
              <span v-if="entry.type === 'file'" class="entry-size">
                {{ formatFileSize(entry.size) }}
              </span>
            </div>
            <v-icon 
              v-if="entry.type === 'directory'" 
              class="entry-chevron"
              size="small"
            >
              mdi-chevron-right
            </v-icon>
          </div>
        </div>
      </v-card-text>

      <v-divider />

      <!-- Selected File Display -->
      <div v-if="selectedPath" class="selected-path-section">
        <div class="selected-path">
          <span class="label">Selected:</span>
          <span class="path">{{ selectedPath }}</span>
        </div>
      </div>

      <!-- Footer -->
      <v-card-actions class="dialog-actions">
        <v-spacer />
        <v-btn 
          variant="plain" 
          @click="emit('update:modelValue', false)"
        >
          Cancel
        </v-btn>
        <v-btn 
          color="primary" 
          variant="tonal"
          @click="confirmSelection"
          :disabled="!selectedPath || isLoading"
        >
          Select
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Create Folder Dialog -->
    <v-dialog v-model="showCreateFolderDialog" max-width="400px">
      <v-card>
        <v-card-title>Create New Folder</v-card-title>
        <v-divider />
        <v-card-text class="pt-4">
          <v-text-field
            v-model="newFolderName"
            label="Folder Name"
            placeholder="Enter folder name"
            variant="outlined"
            density="comfortable"
            autofocus
            @keyup.enter="createFolder"
            :error-messages="createFolderError"
          />
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="plain" @click="showCreateFolderDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="createFolder" :loading="isCreatingFolder">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Folder Confirmation -->
    <v-dialog v-model="showDeleteFolderDialog" max-width="400px">
      <v-card>
        <v-card-title>Delete Folder?</v-card-title>
        <v-divider />
        <v-card-text class="pt-4">
          <p>Are you sure you want to delete this folder and all its contents?</p>
          <p class="text-error mt-2"><strong>This action cannot be undone.</strong></p>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="plain" @click="showDeleteFolderDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="deleteFolder" :loading="isDeletingFolder">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  projectId: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: 'Select File'
  },
  maxWidth: {
    type: String,
    default: '700px'
  },
  fileTypesFilter: {
    type: Array,
    default: () => []
  },
  /** 'project' browses the project upload dir; 'filesystem' browses the real FS */
  mode: {
    type: String,
    default: 'project'
  },
  /** Starting path for filesystem mode (e.g. resolved $DATA value) */
  initialPath: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'select'])

const currentPath = ref('')
const entries = ref([])
const selectedPath = ref('')
const selectedEntryType = ref('')
const isLoading = ref(false)
const error = ref('')
const serverParentPath = ref(null) // used in filesystem mode

// Create folder state
const showCreateFolderDialog = ref(false)
const newFolderName = ref('')
const isCreatingFolder = ref(false)
const createFolderError = ref('')

// Delete folder state
const showDeleteFolderDialog = ref(false)
const isDeletingFolder = ref(false)

// The last path segment of initialPath, used as the Home button label
const initialPathName = computed(() => {
  if (!props.initialPath) return ''
  return props.initialPath.split('/').filter(p => p).pop() || props.initialPath
})

const isAtRoot = computed(() => {
  if (props.mode === 'filesystem') return currentPath.value === props.initialPath
  return currentPath.value === ''
})

const breadcrumbParts = computed(() => {
  if (props.mode === 'filesystem') {
    if (!currentPath.value || !props.initialPath) return []
    // Show segments relative to the parent of initialPath
    const base = props.initialPath.split('/').slice(0, -1).join('/')
    const relative = base && currentPath.value.startsWith(base + '/')
      ? currentPath.value.slice(base.length + 1)
      : currentPath.value
    return relative.split('/').filter(p => p)
  }
  if (!currentPath.value) return []
  return currentPath.value.split('/').filter(p => p)
})

const breadcrumbPaths = computed(() => {
  if (props.mode === 'filesystem') {
    const base = props.initialPath ? props.initialPath.split('/').slice(0, -1).join('/') : ''
    return breadcrumbParts.value.map((_, i) =>
      base + '/' + breadcrumbParts.value.slice(0, i + 1).join('/')
    )
  }
  const paths = []
  const parts = currentPath.value.split('/').filter(p => p)
  for (let i = 0; i < parts.length; i++) {
    paths.push(parts.slice(0, i + 1).join('/'))
  }
  return paths
})

const parentPath = computed(() => {
  if (props.mode === 'filesystem') return serverParentPath.value
  if (!currentPath.value) return null
  const parts = currentPath.value.split('/').filter(p => p)
  if (parts.length === 0) return null
  return parts.slice(0, -1).join('/') || ''
})

function getFileIcon(filename) {
  const ext = filename.split('.').pop()?.toLowerCase()
  const iconMap = {
    'yaml': 'mdi-code-braces',
    'yml': 'mdi-code-braces',
    'json': 'mdi-code-braces',
    'csv': 'mdi-table',
    'txt': 'mdi-text-box',
    'svs': 'mdi-image',
    'dcm': 'mdi-hospital-box',
    'jpg': 'mdi-image',
    'png': 'mdi-image',
    'tiff': 'mdi-image',
  }
  return iconMap[ext] || 'mdi-file'
}

function formatFileSize(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

async function loadDirectory(path = '') {
  isLoading.value = true
  error.value = ''
  try {
    let url
    if (props.mode === 'filesystem') {
      url = path ? `/api/fs-browse?path=${encodeURIComponent(path)}` : '/api/fs-browse'
    } else {
      const query = path ? `?path=${encodeURIComponent(path)}` : ''
      url = `/api/projects/${props.projectId}/data-browser${query}`
    }
    const response = await fetch(url)
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Failed to load directory')
    }
    const data = await response.json()
    entries.value = data.entries
    currentPath.value = data.current_path
    if (props.mode === 'filesystem') {
      serverParentPath.value = data.parent_path ?? null
    }
  } catch (err) {
    error.value = err.message
    console.error('Error loading directory:', err)
  } finally {
    isLoading.value = false
  }
}

function navigateTo(path) {
  selectedPath.value = ''
  loadDirectory(path)
}

function navigateHome() {
  if (props.mode === 'filesystem' && props.initialPath) {
    navigateTo(props.initialPath)
  } else {
    navigateTo('')
  }
}

function selectEntry(entry) {
  selectedPath.value = entry.absolute_path
  selectedEntryType.value = entry.type
}

function doubleClickEntry(entry) {
  if (entry.type === 'directory') {
    navigateTo(entry.path)
  }
}

function refreshDirectory() {
  loadDirectory(currentPath.value)
}

function confirmSelection() {
  if (!selectedPath.value) return
  emit('select', selectedPath.value)
  emit('update:modelValue', false)
}

function confirmDeleteFolder() {
  if (!selectedPath.value || selectedEntryType.value !== 'directory') return
  showDeleteFolderDialog.value = true
}

async function createFolder() {
  if (!newFolderName.value || !newFolderName.value.trim()) {
    createFolderError.value = 'Folder name is required'
    return
  }

  isCreatingFolder.value = true
  createFolderError.value = ''

  try {
    let url, body
    if (props.mode === 'filesystem') {
      url = '/api/fs-create-folder'
      body = { parent_path: currentPath.value, folder_name: newFolderName.value.trim() }
    } else {
      url = `/api/projects/${props.projectId}/data-browser/create-folder`
      body = { path: currentPath.value, folder_name: newFolderName.value.trim() }
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Failed to create folder')
    }

    showCreateFolderDialog.value = false
    newFolderName.value = ''
    await loadDirectory(currentPath.value)
  } catch (err) {
    createFolderError.value = err.message
  } finally {
    isCreatingFolder.value = false
  }
}

async function deleteFolder() {
  if (!selectedPath.value) return
  
  isDeletingFolder.value = true
  
  try {
    // Get the relative path for the API
    const relativePath = selectedPath.value.replace(/^.*\/data\//, '')
    
    const response = await fetch(
      `/api/projects/${props.projectId}/data-browser/delete-folder?path=${encodeURIComponent(relativePath)}`,
      { method: 'DELETE' }
    )
    
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Failed to delete folder')
    }
    
    // Success - close dialog and refresh
    showDeleteFolderDialog.value = false
    selectedPath.value = ''
    selectedEntryType.value = ''
    await loadDirectory(currentPath.value)
  } catch (err) {
    error.value = err.message
  } finally {
    isDeletingFolder.value = false
  }
}

// Load directory when dialog opens
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    // On first open in filesystem mode, start at initialPath
    const startPath = (props.mode === 'filesystem' && !currentPath.value && props.initialPath)
      ? props.initialPath
      : currentPath.value
    loadDirectory(startPath)
  }
})
</script>

<style scoped lang="scss">
.file-dialog {
  display: flex;
  flex-direction: column;
  max-height: 90vh;

  .dialog-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;

    .dialog-title {
      display: flex;
      align-items: center;
      margin: 0;
      font-size: 1.25rem;
      font-weight: 600;
    }
  }

  .toolbar-section {
    padding: 12px 20px;
    display: flex;
    gap: 8px;
  }

  .breadcrumb-section {
    padding: 12px 20px;
    background-color: rgba(var(--v-theme-surface-variant), 0.3);

    .breadcrumb {
      display: flex;
      align-items: center;
      gap: 4px;
      overflow-x: auto;
      padding-bottom: 4px;

      &::-webkit-scrollbar {
        height: 4px;
      }

      &::-webkit-scrollbar-thumb {
        background-color: rgba(var(--v-theme-on-surface), 0.2);
        border-radius: 2px;

        &:hover {
          background-color: rgba(var(--v-theme-on-surface), 0.3);
        }
      }

      .breadcrumb-separator {
        color: var(--v-border-color);
        margin: 0 4px;
      }
    }
  }

  .file-browser {
    flex: 1;
    overflow-y: auto;
    padding: 0;
    min-height: 300px;

    .loading-container,
    .error-container,
    .empty-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 300px;
      padding: 40px 20px;
      text-align: center;
    }

    .entries-list {
      .entry {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 20px;
        cursor: pointer;
        transition: all 0.2s ease;
        border-left: 3px solid transparent;

        &:hover {
          background-color: rgba(var(--v-theme-primary), 0.08);
        }

        &.is-selected {
          background-color: rgba(var(--v-theme-primary), 0.12);
          border-left-color: var(--v-theme-primary);
        }

        &.parent-entry {
          font-weight: 500;
          opacity: 0.7;
          padding: 16px 20px;

          .entry-type {
            margin-left: auto;
            font-size: 0.75rem;
            opacity: 0.6;
          }
        }

        .entry-icon {
          flex-shrink: 0;
          color: var(--v-theme-primary);
        }

        .entry-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          min-width: 0;

          .entry-name {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-weight: 500;
          }

          .entry-size {
            font-size: 0.75rem;
            color: var(--v-theme-on-surface-variant);
          }
        }

        .entry-chevron {
          flex-shrink: 0;
          opacity: 0.4;
        }

        &.is-directory {
          &:hover {
            .entry-chevron {
              opacity: 1;
              transform: translateX(4px);
            }
          }
        }
      }
    }
  }

  .selected-path-section {
    padding: 12px 20px;
    background-color: rgba(var(--v-theme-surface-variant), 0.3);

    .selected-path {
      display: flex;
      align-items: center;
      gap: 8px;
      word-break: break-all;

      .label {
        font-weight: 600;
        flex-shrink: 0;
      }

      .path {
        font-family: 'Courier New', monospace;
        font-size: 0.875rem;
        color: var(--v-theme-primary);
      }
    }
  }

  .dialog-actions {
    padding: 12px 20px;
  }
}
</style>
