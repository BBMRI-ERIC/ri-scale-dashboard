<template>
  <v-card class="sources-panel" variant="tonal" color="primary">
    <v-card-title class="text-subtitle-2 d-flex align-center">
      <v-icon size="18" class="mr-2">mdi-database-outline</v-icon>
      Available Sources
      <v-spacer />
      <v-chip size="x-small" variant="flat">{{ sources.length }}</v-chip>
    </v-card-title>
    <v-divider />
    <v-card-text class="pa-2">
      <div v-if="sources.length === 0" class="text-caption text-medium-emphasis text-center py-2">
        No sources yet
      </div>
      <v-list v-else density="compact" class="bg-transparent">
        <v-list-item
          v-for="source in sources"
          :key="source.source_name"
          :title="source.source_name"
          :subtitle="`${source.columns.length} column${source.columns.length !== 1 ? 's' : ''}`"
          density="compact"
          class="px-2"
        >
          <template v-slot:prepend>
            <v-icon size="16" color="primary">mdi-table</v-icon>
          </template>
          <v-tooltip location="right" activator="parent">
            <div class="text-caption">
              <div class="font-weight-bold mb-1">{{ source.source_name }}</div>
              <!-- <div class="text-caption mb-1">From: {{ source.step_name }}</div> -->
              <div class="text-caption">Columns:</div>
              <ul class="pl-4 mb-0">
                <li v-for="col in source.columns" :key="col">{{ col }}</li>
              </ul>
            </div>
          </v-tooltip>
        </v-list-item>
      </v-list>
    </v-card-text>
  </v-card>
</template>

<script setup>
defineProps({
  sources: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.sources-panel {
  position: sticky;
  top: 16px;
}
</style>
