<template>
  <div class="source-column-selector">
    <!-- Source Selection -->
    <v-select
      :model-value="selectedSource"
      @update:model-value="handleSourceChange"
      :label="sourceLabel"
      :hint="sourceHint"
      :items="sourceItems"
      item-title="label"
      item-value="value"
      :placeholder="sourcePlaceholder || 'Select a source...'"
      variant="outlined"
      density="compact"
      persistent-hint
      :disabled="disabled || sourceItems.length === 0"
      prepend-inner-icon="mdi-database"
      clearable
      class="mb-3"
    >
      <template v-slot:no-data>
        <v-list-item>
          <v-list-item-title class="text-caption text-medium-emphasis">
            No sources available yet. Add a Data Loader step first.
          </v-list-item-title>
        </v-list-item>
      </template>
    </v-select>

    <!-- Column Selection (only shown when source is selected) -->
    <v-select
      v-if="selectedSource"
      :model-value="selectedColumn"
      @update:model-value="handleColumnChange"
      :label="columnLabel"
      :hint="columnHint"
      :items="availableColumns"
      :placeholder="columnPlaceholder || 'Select a column...'"
      variant="outlined"
      density="compact"
      persistent-hint
      :disabled="disabled || availableColumns.length === 0"
      prepend-inner-icon="mdi-table-column"
      clearable
    >
      <template v-slot:prepend-item v-if="currentSourceInfo">
        <v-list-subheader class="text-caption">
          Columns from: {{ currentSourceInfo.step_name }}
        </v-list-subheader>
        <v-divider class="mb-2" />
      </template>
      <template v-slot:no-data>
        <v-list-item>
          <v-list-item-title class="text-caption text-medium-emphasis">
            No columns detected for this source
          </v-list-item-title>
        </v-list-item>
      </template>
    </v-select>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getColumnsForSource } from '@/utils/sourceTracker'

const props = defineProps({
  sourceValue: {
    type: String,
    default: ''
  },
  columnValue: {
    type: String,
    default: ''
  },
  sourceLabel: {
    type: String,
    default: 'Source'
  },
  columnLabel: {
    type: String,
    default: 'Column'
  },
  sourceHint: {
    type: String,
    default: ''
  },
  columnHint: {
    type: String,
    default: ''
  },
  sourcePlaceholder: {
    type: String,
    default: ''
  },
  columnPlaceholder: {
    type: String,
    default: ''
  },
  availableSources: {
    type: Array,
    default: () => []
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:sourceValue', 'update:columnValue'])

const selectedSource = computed(() => props.sourceValue)
const selectedColumn = computed(() => props.columnValue)

const sourceItems = computed(() => {
  return props.availableSources.map(source => ({
    label: `${source.source_name} (from step: ${source.step_name})`,
    value: source.source_name
  }))
})

const currentSourceInfo = computed(() => {
  if (!selectedSource.value) return null
  return props.availableSources.find(s => s.source_name === selectedSource.value)
})

const availableColumns = computed(() => {
  if (!selectedSource.value) return []
  return getColumnsForSource(props.availableSources, selectedSource.value)
})

function handleSourceChange(value) {
  emit('update:sourceValue', value)
  // Clear column selection when source changes
  if (selectedColumn.value) {
    emit('update:columnValue', '')
  }
}

function handleColumnChange(value) {
  emit('update:columnValue', value)
}
</script>

<style scoped>
.source-column-selector {
  width: 100%;
}
</style>
