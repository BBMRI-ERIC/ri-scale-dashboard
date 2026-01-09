<template>
  <div class="login-page">
    <!-- Animated background -->
    <div class="login-background">
      <div class="bg-grid"></div>
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>

    <!-- Login container -->
    <div class="login-container">
      <!-- Logo and branding -->
      <div class="login-header slide-up delay-1">
        <div class="logo-wrapper">
          <div class="logo-icon">
            <img src="/logo-48.png" alt="RI-SCALE" width="48" height="48" />
          </div>
          <div class="logo-text">
            <span class="logo-title gradient-text">RI-SCALE</span>
            <span class="logo-subtitle">Data Exploitation Platform</span>
          </div>
        </div>
      </div>

      <!-- Login card -->
      <v-card class="login-card glass slide-up delay-2" :elevation="0">
        <v-card-text class="pa-8">
          <h1 class="login-title mb-2">Welcome back</h1>
          <p class="login-subtitle mb-8">Sign in to access your research projects</p>

          <!-- Error alert -->
          <v-alert
            v-if="authStore.error"
            type="error"
            variant="tonal"
            class="mb-6"
            closable
            @click:close="authStore.clearError()"
          >
            {{ authStore.error }}
          </v-alert>

          <!-- Login form -->
          <v-form @submit.prevent="handleLogin" ref="formRef">
            <v-text-field
              v-model="username"
              label="Username"
              prepend-inner-icon="mdi-account-outline"
              :rules="[rules.required]"
              :disabled="authStore.isLoading"
              autocomplete="username"
              class="mb-4"
            />

            <v-text-field
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              label="Password"
              prepend-inner-icon="mdi-lock-outline"
              :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
              :rules="[rules.required]"
              :disabled="authStore.isLoading"
              autocomplete="current-password"
              class="mb-6"
              @click:append-inner="showPassword = !showPassword"
            />

            <v-btn
              type="submit"
              block
              size="large"
              :loading="authStore.isLoading"
              class="login-btn mb-4"
            >
              <span class="btn-text">Sign In</span>
              <v-icon end>mdi-arrow-right</v-icon>
            </v-btn>
          </v-form>

          <!-- Divider -->
          <div class="divider-wrapper my-6">
            <div class="divider-line"></div>
            <span class="divider-text">or continue with</span>
            <div class="divider-line"></div>
          </div>

          <!-- SSO Button -->
          <v-btn
            variant="outlined"
            block
            size="large"
            class="sso-btn"
            :disabled="authStore.isLoading"
          >
            <v-icon start>mdi-shield-account</v-icon>
            LifeScience AAI
          </v-btn>
        </v-card-text>
      </v-card>

      <!-- Footer info -->
      <div class="login-footer slide-up delay-3">
        <p class="hint-text">
          <v-icon size="small" class="mr-1">mdi-information-outline</v-icon>
          Test credentials: <code>test</code> / <code>test</code>
        </p>
        <p class="project-info">
          Part of the 
          <a href="https://ri-scale.eu" target="_blank" rel="noopener">
            RI-SCALE Horizon Europe Project
          </a>
        </p>
      </div>
    </div>

    <!-- Decorative elements -->
    <div class="side-decoration left">
      <div class="deco-line"></div>
      <div class="deco-dots">
        <span v-for="i in 5" :key="i" class="dot"></span>
      </div>
    </div>
    <div class="side-decoration right">
      <div class="deco-line"></div>
      <div class="deco-dots">
        <span v-for="i in 5" :key="i" class="dot"></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref(null)
const username = ref('')
const password = ref('')
const showPassword = ref(false)

const rules = {
  required: v => !!v || 'This field is required'
}

async function handleLogin() {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  const result = await authStore.login(username.value, password.value)
  
  if (result.success) {
    // Redirect to intended destination or dashboard
    const redirectPath = route.query.redirect || '/dashboard'
    router.push(redirectPath)
  }
}
</script>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 2rem;
}

.login-background {
  position: fixed;
  inset: 0;
  z-index: 0;
  
  .bg-grid {
    position: absolute;
    inset: 0;
    background-image: 
      linear-gradient(rgba(51, 65, 85, 0.08) 1px, transparent 1px),
      linear-gradient(90deg, rgba(51, 65, 85, 0.08) 1px, transparent 1px);
    background-size: 60px 60px;
  }
  
  .gradient-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.5;
    animation: float 20s ease-in-out infinite;
    
    &.orb-1 {
      width: 600px;
      height: 600px;
      background: radial-gradient(circle, rgba(230, 152, 48, 0.25) 0%, transparent 70%);
      top: -200px;
      right: -100px;
      animation-delay: 0s;
    }
    
    &.orb-2 {
      width: 500px;
      height: 500px;
      background: radial-gradient(circle, rgba(8, 145, 178, 0.25) 0%, transparent 70%);
      bottom: -150px;
      left: -100px;
      animation-delay: -7s;
    }
    
    &.orb-3 {
      width: 400px;
      height: 400px;
      background: radial-gradient(circle, rgba(244, 114, 182, 0.15) 0%, transparent 70%);
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      animation-delay: -14s;
    }
  }
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(30px, -30px) scale(1.05);
  }
  50% {
    transform: translate(-20px, 20px) scale(0.95);
  }
  75% {
    transform: translate(-30px, -20px) scale(1.02);
  }
}

.login-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 440px;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.logo-icon {
  width: 72px;
  height: 72px;
  
  svg {
    width: 100%;
    height: 100%;
  }
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.logo-subtitle {
  font-size: 0.875rem;
  color: rgba(148, 163, 184, 0.8);
  letter-spacing: 0.02em;
}

.login-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.login-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: #f1f5f9;
}

.login-subtitle {
  font-size: 0.9375rem;
  color: #94a3b8;
}

.login-btn {
  background: linear-gradient(135deg, #E69830 0%, #D18A28 100%) !important;
  color: #0a0f1a !important;
  font-weight: 600;
  letter-spacing: 0.02em;
  height: 52px !important;
  
  &:hover {
    box-shadow: 0 0 30px rgba(230, 152, 48, 0.4);
  }
  
  .btn-text {
    margin-right: 0.5rem;
  }
}

.divider-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: rgba(51, 65, 85, 0.5);
}

.divider-text {
  font-size: 0.8125rem;
  color: #64748b;
}

.sso-btn {
  height: 48px !important;
  border-color: rgba(51, 65, 85, 0.8);
  color: #94a3b8;
  
  &:hover {
    border-color: #E69830;
    color: #E69830;
  }
}

.login-footer {
  margin-top: 2rem;
  text-align: center;
}

.hint-text {
  font-size: 0.8125rem;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  
  code {
    background: rgba(230, 152, 48, 0.15);
    color: #E69830;
    padding: 0.125rem 0.5rem;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    margin: 0 0.25rem;
  }
}

.project-info {
  margin-top: 0.75rem;
  font-size: 0.75rem;
  color: #475569;
  
  a {
    color: #0891b2;
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

// Side decorations
.side-decoration {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 1rem;
  z-index: 0;
  
  &.left {
    left: 2rem;
    flex-direction: row;
  }
  
  &.right {
    right: 2rem;
    flex-direction: row-reverse;
  }
  
  .deco-line {
    width: 1px;
    height: 200px;
    background: linear-gradient(
      to bottom,
      transparent,
      rgba(230, 152, 48, 0.3),
      transparent
    );
  }
  
  .deco-dots {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    
    .dot {
      width: 4px;
      height: 4px;
      border-radius: 50%;
      background: rgba(230, 152, 48, 0.4);
    }
  }
}

// Responsive
@media (max-width: 600px) {
  .login-page {
    padding: 1rem;
  }
  
  .side-decoration {
    display: none;
  }
  
  .login-card :deep(.v-card-text) {
    padding: 1.5rem !important;
  }
}
</style>
