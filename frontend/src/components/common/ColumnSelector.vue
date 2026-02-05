<template>
  <div class="column-selector">
    <v-select
      :model-value="modelValue"
      @update:model-value="handleChange"
      :label="label"
      :hint="hint"
      :items="availableColumns"
      :placeholder="placeholder || 'Select a column...'"
      variant="outlined"
      density="compact"
      persistent-hint
      :disabled="disabled || availableColumns.length === 0"
      :prepend-inner-icon="prependIcon"
      clearable
    >
      <template v-slot:prepend-item v-if="showSourceInfo && selectedSourceInfo">
        <v-list-subheader class="text-caption">
          From: {{ selectedSourceInfo.step_name }} ({{ selectedSourceInfo.source_name }})
        </v-list-subheader>
        <v-divider class="mb-2" />
      </template>
      <template v-slot:no-data>
        <v-list-item>
          <v-list-item-title class="text-caption text-medium-emphasis">
            {{ noDataMessage }}
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
  modelValue: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: 'Column'
  },
  hint: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  sourceName: {
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
  },
  prependIcon: {
    type: String,
    default: 'mdi-table-column'
  },
  showSourceInfo: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue'])

const selectedSourceInfo = computed(() => {
  if (!props.sourceName || !props.availableSources) return null
  return props.availableSources.find(s => s.source_name === props.sourceName)
})

const availableColumns = computed(() => {
  if (!props.sourceName) return []
  return getColumnsForSource(props.availableSources, props.sourceName)
})

const noDataMessage = computed(() => {
  if (!props.sourceName) {
    return 'Please select a source first'
  }
  return 'No columns available for this source'
})

function handleChange(value) {
  emit('update:modelValue', value)
}
</script>

<style scoped>
.column-selector {
  width: 100%;
}
</style>
