<template>
  <v-card class="project-card glass card-hover" :elevation="0" @click="$emit('click')">
    <!-- Card header -->
    <div class="card-header">
      <div class="project-badge" :class="project.useCase.toLowerCase()">
        {{ project.useCase }}
      </div>
      <v-chip 
        :color="statusColor" 
        size="small" 
        variant="tonal"
        class="status-chip"
      >
        <v-icon start size="12">{{ statusIcon }}</v-icon>
        {{ project.status }}
      </v-chip>
    </div>

    <!-- Card content -->
    <v-card-text class="card-content">
      <h3 class="project-title">{{ project.shortTitle }}</h3>
      <p class="project-description">{{ project.description }}</p>

      <!-- Project stats -->
      <div class="project-stats">
        <div class="stat-item">
          <v-icon size="16" class="stat-icon">mdi-database</v-icon>
          <span class="stat-value">{{ project.datasetCount }}</span>
          <span class="stat-label">Datasets</span>
        </div>
        <div class="stat-item">
          <v-icon size="16" class="stat-icon">mdi-image-multiple</v-icon>
          <span class="stat-value">{{ formatNumber(project.wsiCount) }}</span>
          <span class="stat-label">WSIs</span>
        </div>
        <div class="stat-item">
          <v-icon size="16" class="stat-icon">mdi-map-marker</v-icon>
          <span class="stat-value">{{ project.sites.length }}</span>
          <span class="stat-label">Sites</span>
        </div>
      </div>

      <!-- Project Duration Timeline -->
      <div class="duration-section">
        <div class="duration-header">
          <span class="duration-date start">{{ formatDate(project.createdAt) }}</span>
          <span class="duration-label">Project Duration</span>
          <span class="duration-date end">{{ formatDate(project.validUntil) }}</span>
        </div>
        <div class="duration-bar-container">
          <v-progress-linear
            :model-value="timeProgress"
            :color="timeProgressColor"
            height="8"
            rounded
            class="duration-bar"
          />
          <div 
            v-if="timeProgress > 5 && timeProgress < 95" 
            class="duration-marker" 
            :style="{ left: timeProgress + '%' }"
          >
            <span class="marker-label">Today</span>
          </div>
        </div>
        <div class="duration-info">
          <span class="time-remaining" :class="{ warning: daysRemaining < 30, danger: daysRemaining < 7 }">
            <v-icon size="12" class="mr-1">mdi-calendar-clock</v-icon>
            {{ daysRemainingText }}
          </span>
        </div>
      </div>

      <!-- Quick stats row -->
      <div class="quick-stats">
        <div class="quick-stat">
          <div class="quick-stat-icon transfers">
            <v-icon size="14">mdi-swap-horizontal</v-icon>
          </div>
          <div class="quick-stat-content">
            <span class="quick-stat-value">{{ project.stats.dataTransfers.total }}</span>
            <span class="quick-stat-label">Transfers</span>
          </div>
        </div>
        <div class="quick-stat">
          <div class="quick-stat-icon computations">
            <v-icon size="14">mdi-chip</v-icon>
          </div>
          <div class="quick-stat-content">
            <span class="quick-stat-value">{{ project.stats.computations.running }}</span>
            <span class="quick-stat-label">Running</span>
          </div>
        </div>
        <div class="quick-stat">
          <div class="quick-stat-icon models">
            <v-icon size="14">mdi-brain</v-icon>
          </div>
          <div class="quick-stat-content">
            <span class="quick-stat-value">{{ project.stats.models.applied }}</span>
            <span class="quick-stat-label">Models</span>
          </div>
        </div>
      </div>
    </v-card-text>

    <!-- Card footer -->
    <div class="card-footer">
      <span class="project-owner">
        <v-icon size="14" class="mr-1">mdi-account</v-icon>
        <span class="owner-label">Project Admin:</span>
        <span class="owner-name">{{ project.owner }}</span>
      </span>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  project: {
    type: Object,
    required: true
  }
})

defineEmits(['click'])

const statusColor = computed(() => {
  const colors = {
    active: 'success',
    pending: 'warning',
    completed: 'info',
    cancelled: 'error'
  }
  return colors[props.project.status] || 'default'
})

const statusIcon = computed(() => {
  const icons = {
    active: 'mdi-circle',
    pending: 'mdi-clock-outline',
    completed: 'mdi-check-circle',
    cancelled: 'mdi-close-circle'
  }
  return icons[props.project.status] || 'mdi-circle'
})

// Time-based progress calculation
const timeProgress = computed(() => {
  const start = new Date(props.project.createdAt)
  const end = new Date(props.project.validUntil)
  const now = new Date()
  
  const totalDuration = end - start
  const elapsed = now - start
  
  if (elapsed <= 0) return 0
  if (elapsed >= totalDuration) return 100
  
  return Math.round((elapsed / totalDuration) * 100)
})

const timeProgressColor = computed(() => {
  if (timeProgress.value >= 90) return 'error'
  if (timeProgress.value >= 75) return 'warning'
  return 'primary'
})

const daysRemaining = computed(() => {
  const end = new Date(props.project.validUntil)
  const now = new Date()
  const diff = end - now
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
})

const daysRemainingText = computed(() => {
  if (daysRemaining.value < 0) return 'Expired'
  if (daysRemaining.value === 0) return 'Expires today'
  if (daysRemaining.value === 1) return '1 day remaining'
  if (daysRemaining.value < 30) return `${daysRemaining.value} days remaining`
  const months = Math.round(daysRemaining.value / 30)
  if (months === 1) return '~1 month remaining'
  return `~${months} months remaining`
})

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    year: 'numeric'
  })
}

function formatNumber(num) {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}
</script>

<style scoped lang="scss">
.project-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;
  
  &:hover {
    border-color: rgba(230, 152, 48, 0.3);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1rem 0;
}

.project-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.05em;
  
  &.uc7 {
    background: rgba(230, 152, 48, 0.15);
    color: #E69830;
  }
  
  &.uc8 {
    background: rgba(139, 92, 246, 0.15);
    color: #a78bfa;
  }
}

.status-chip {
  text-transform: capitalize;
}

.card-content {
  flex: 1;
  padding: 1rem !important;
}

.project-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 0.5rem;
}

.project-description {
  font-size: 0.8125rem;
  color: #94a3b8;
  line-height: 1.5;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-stats {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 10px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.stat-icon {
  color: #64748b;
}

.stat-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #f1f5f9;
}

.stat-label {
  font-size: 0.75rem;
  color: #64748b;
}

// Duration Timeline
.duration-section {
  margin-bottom: 1rem;
}

.duration-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.duration-date {
  font-size: 0.6875rem;
  font-family: 'JetBrains Mono', monospace;
  color: #64748b;
  
  &.start {
    color: #94a3b8;
  }
  
  &.end {
    color: #94a3b8;
  }
}

.duration-label {
  font-size: 0.6875rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.duration-bar-container {
  position: relative;
  margin-bottom: 0.5rem;
}

.duration-bar {
  background: rgba(51, 65, 85, 0.5);
}

.duration-marker {
  position: absolute;
  top: -2px;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  
  &::before {
    content: '';
    width: 4px;
    height: 12px;
    background: #f1f5f9;
    border-radius: 2px;
  }
  
  .marker-label {
    font-size: 0.5625rem;
    color: #94a3b8;
    margin-top: 2px;
    white-space: nowrap;
  }
}

.duration-info {
  display: flex;
  justify-content: flex-end;
}

.time-remaining {
  font-size: 0.6875rem;
  color: #94a3b8;
  display: flex;
  align-items: center;
  
  &.warning {
    color: #fbbf24;
  }
  
  &.danger {
    color: #ef4444;
  }
}

.quick-stats {
  display: flex;
  gap: 0.75rem;
}

.quick-stat {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(30, 41, 59, 0.3);
  border-radius: 8px;
}

.quick-stat-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &.transfers {
    background: rgba(59, 130, 246, 0.2);
    color: #3b82f6;
  }
  
  &.computations {
    background: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
  }
  
  &.models {
    background: rgba(244, 114, 182, 0.2);
    color: #f472b6;
  }
}

.quick-stat-content {
  display: flex;
  flex-direction: column;
}

.quick-stat-value {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #f1f5f9;
}

.quick-stat-label {
  font-size: 0.625rem;
  color: #64748b;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-top: 1px solid rgba(51, 65, 85, 0.3);
  background: rgba(30, 41, 59, 0.3);
}

.project-owner {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  
  .owner-label {
    color: #64748b;
  }
  
  .owner-name {
    color: #e2e8f0;
  }
}

</style>
