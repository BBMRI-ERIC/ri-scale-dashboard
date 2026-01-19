<template>
  <div class="not-found-page">
    <div class="not-found-content slide-up">
      <div class="error-code gradient-text">404</div>
      <h1 class="error-title">Page Not Found</h1>
      <p class="error-message">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <div class="error-actions">
        <v-btn 
          color="primary" 
          size="large"
          prepend-icon="mdi-home"
          @click="$router.push('/dashboard')"
        >
          Go to Dashboard
        </v-btn>
        <v-btn 
          variant="outlined" 
          size="large"
          @click="$router.back()"
        >
          Go Back
        </v-btn>
      </div>
    </div>

    <!-- Background decoration -->
    <div class="bg-decoration">
      <div class="grid-bg"></div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped lang="scss">
.not-found-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 2rem;
}

.not-found-content {
  text-align: center;
  position: relative;
  z-index: 1;
}

.error-code {
  font-size: 8rem;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 1rem;
  font-family: 'JetBrains Mono', monospace;
}

.error-title {
  font-size: 2rem;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 1rem;
}

.error-message {
  font-size: 1.125rem;
  color: #94a3b8;
  margin-bottom: 2rem;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.bg-decoration {
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  
  .grid-bg {
    position: absolute;
    inset: 0;
    background-image: 
      linear-gradient(rgba(51, 65, 85, 0.08) 1px, transparent 1px),
      linear-gradient(90deg, rgba(51, 65, 85, 0.08) 1px, transparent 1px);
    background-size: 60px 60px;
  }
}

@media (max-width: 600px) {
  .error-code {
    font-size: 5rem;
  }
  
  .error-actions {
    flex-direction: column;
  }
}
</style>
