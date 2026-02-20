<template>
  <div class="file-input-wrapper">
    <div class="input-with-button">
      <v-text-field
        :model-value="modelValue"
        @update:model-value="emit('update:modelValue', $event)"
        :label="label"
        :placeholder="placeholder"
        :hint="hint"
        :required="required"
        variant="outlined"
        density="compact"
        persistent-hint
        class="file-input-field"
      />
      <v-btn
        icon
        size="small"
        variant="text"
        :loading="isResolvingRoot"
        @click="openFileDialog"
        title="Browse files"
        class="file-browse-btn"
      >
        <v-icon>mdi-folder-open-outline</v-icon>
      </v-btn>
    </div>

    <!-- File Dialog -->
    <FileDialog
      v-model="fileDialogOpen"
      :project-id="projectId"
      :mode="dialogMode"
      :initial-path="dataRoot"
      title="Select Data File or Directory"
      @select="onFileSelected"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import FileDialog from '@/components/common/FileDialog.vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: 'Path'
  },
  placeholder: {
    type: String,
    default: 'Enter path or browse...'
  },
  hint: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  projectId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const fileDialogOpen = ref(false)
const dataRoot = ref('')
const isResolvingRoot = ref(false)

// Module-level cache so we only fetch once across all FileInput instances
let _cachedDataRoot = null

async function resolveDataRoot() {
  if (_cachedDataRoot !== null) return _cachedDataRoot
  try {
    const resp = await fetch('/api/config/data-root')
    if (resp.ok) {
      const data = await resp.json()
      _cachedDataRoot = data.path || ''
    } else {
      _cachedDataRoot = ''
    }
  } catch {
    _cachedDataRoot = ''
  }
  return _cachedDataRoot
}

const dialogMode = computed(() => dataRoot.value ? 'filesystem' : 'project')

async function openFileDialog() {
  if (_cachedDataRoot === null) {
    isResolvingRoot.value = true
    dataRoot.value = await resolveDataRoot()
    isResolvingRoot.value = false
  } else {
    dataRoot.value = _cachedDataRoot
  }
  fileDialogOpen.value = true
}

function onFileSelected(filePath) {
  emit('update:modelValue', filePath)
}
</script>

<style scoped lang="scss">
.file-input-wrapper {
  width: 100%;

  .input-with-button {
    display: flex;
    gap: 8px;
    align-items: flex-start;

    .file-input-field {
      flex: 1;
    }

    .file-browse-btn {
      margin-top: 4px;
      color: var(--v-theme-primary);

      &:hover {
        background-color: rgba(var(--v-theme-primary), 0.08);
      }
    }
  }
}
</style>
