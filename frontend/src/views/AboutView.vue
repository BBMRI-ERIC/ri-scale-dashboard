<template>
  <v-layout class="dashboard-layout">
    <AppSidebar v-model:rail="sidebarRail" @toggle-rail="sidebarRail = !sidebarRail" />
    
    <v-main class="main-content">
      <AppHeader />
      
      <div class="page-container">
        <!-- Hero Section -->
        <div class="hero-section">
          <div class="hero-content">
            <h1 class="hero-title">
              <span class="gradient-text">RI-SCALE</span> Dashboard
            </h1>
            <p class="hero-subtitle">
              Unlocking Research Infrastructure potential with Scalable AI and Data
            </p>
          </div>
        </div>

        <!-- Logos Section -->
        <div class="logos-section">
          <h2 class="section-title">Partners & Institutions</h2>
          
          <div class="logos-grid">
            <!-- BBMRI-ERIC Logo -->
            <div class="logo-card glass">
              <div class="logo-wrapper bbmri">
                <svg viewBox="0 0 200 80" class="logo-svg">
                  <defs>
                    <linearGradient id="bbmriGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stop-color="#0077B6"/>
                      <stop offset="100%" stop-color="#00B4D8"/>
                    </linearGradient>
                  </defs>
                  <rect x="10" y="20" width="12" height="40" rx="2" fill="url(#bbmriGrad)"/>
                  <rect x="28" y="20" width="12" height="40" rx="2" fill="url(#bbmriGrad)"/>
                  <rect x="46" y="20" width="12" height="40" rx="2" fill="url(#bbmriGrad)"/>
                  <rect x="64" y="25" width="12" height="30" rx="2" fill="url(#bbmriGrad)"/>
                  <rect x="82" y="30" width="12" height="20" rx="2" fill="url(#bbmriGrad)"/>
                  <text x="105" y="45" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#0077B6">BBMRI</text>
                  <text x="105" y="60" font-family="Arial, sans-serif" font-size="10" fill="#64748b">ERIC</text>
                </svg>
              </div>
              <div class="logo-info">
                <h3>BBMRI-ERIC</h3>
                <p>Biobanking and BioMolecular Resources Research Infrastructure</p>
                <a href="https://www.bbmri-eric.eu" target="_blank" class="logo-link">
                  <v-icon size="14">mdi-open-in-new</v-icon>
                  bbmri-eric.eu
                </a>
              </div>
            </div>

            <!-- RI-SCALE Logo -->
            <div class="logo-card glass">
              <div class="logo-wrapper ri-scale">
                <img src="/logo.png" alt="RI-SCALE" class="logo-img" />
              </div>
              <div class="logo-info">
                <h3>RI-SCALE</h3>
                <p>Horizon Europe project delivering Data Exploitation Platforms for scalable AI workflows</p>
                <a href="https://ri-scale.eu" target="_blank" class="logo-link">
                  <v-icon size="14">mdi-open-in-new</v-icon>
                  ri-scale.eu
                </a>
              </div>
            </div>

            <!-- Medical University of Graz Logo -->
            <div class="logo-card glass">
              <div class="logo-wrapper mug">
                <svg viewBox="0 0 120 120" class="logo-svg square">
                  <defs>
                    <linearGradient id="mugGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stop-color="#DC2626"/>
                      <stop offset="100%" stop-color="#B91C1C"/>
                    </linearGradient>
                  </defs>
                  <!-- Shield shape -->
                  <path d="M60 10 L100 25 L100 65 Q100 95 60 110 Q20 95 20 65 L20 25 Z" 
                        fill="none" stroke="url(#mugGrad)" stroke-width="3"/>
                  <!-- Cross -->
                  <rect x="55" y="30" width="10" height="50" fill="url(#mugGrad)"/>
                  <rect x="40" y="45" width="40" height="10" fill="url(#mugGrad)"/>
                </svg>
              </div>
              <div class="logo-info">
                <h3>Medical University of Graz</h3>
                <p>Leading the biomedical use cases focusing on digital pathology and sensitive health data</p>
                <a href="https://www.medunigraz.at" target="_blank" class="logo-link">
                  <v-icon size="14">mdi-open-in-new</v-icon>
                  medunigraz.at
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- About Section -->
        <div class="about-section">
          <div class="info-card glass mission-card">
            <div class="info-icon">
              <v-icon size="32">mdi-target</v-icon>
            </div>
            <h3>Project Mission</h3>
            <p>
              RI-SCALE delivers Data Exploitation Platforms (DEPs) that co-host scientific data and AI frameworks, 
              integrating secure data access, identity, and trust mechanisms to enable scalable AI workflows on 
              national and European e-infrastructures.
            </p>
          </div>
        </div>

        <!-- Features Section -->
        <div class="features-section">
          <h2 class="section-title">Platform Capabilities</h2>
          <v-row>
            <v-col cols="12" sm="6" md="3" v-for="feature in features" :key="feature.title">
              <div class="feature-card">
                <div class="feature-icon" :style="{ background: feature.gradient }">
                  <v-icon size="24" color="white">{{ feature.icon }}</v-icon>
                </div>
                <h4>{{ feature.title }}</h4>
                <p>{{ feature.description }}</p>
              </div>
            </v-col>
          </v-row>
        </div>

        <!-- Footer -->
        <div class="about-footer">
          <div class="funding-info">
            <v-icon size="20" class="mr-2">mdi-star-circle</v-icon>
            <span>
              Funded by the European Union's Horizon Europe research and innovation programme
            </span>
          </div>
          <div class="version-info">
            <span class="version-label">Dashboard Version</span>
            <span class="version-number font-mono">v1.0.0-alpha</span>
          </div>
        </div>
      </div>
    </v-main>
  </v-layout>
</template>

<script setup>
import { ref } from 'vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const sidebarRail = ref(false)

const features = [
  {
    icon: 'mdi-database-search',
    title: 'Dataset Discovery',
    description: 'Browse and search BBMRI-ERIC biobank datasets',
    gradient: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)'
  },
  {
    icon: 'mdi-handshake',
    title: 'Access Negotiation',
    description: 'Streamlined data access request workflow',
    gradient: 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)'
  },
  {
    icon: 'mdi-server',
    title: 'Secure Computing',
    description: 'Run analyses on HPC secure processing environments',
    gradient: 'linear-gradient(135deg, #E69830 0%, #D18A28 100%)'
  },
  {
    icon: 'mdi-brain',
    title: 'AI Model Hub',
    description: 'Deploy pre-trained models for pathology analysis',
    gradient: 'linear-gradient(135deg, #EC4899 0%, #DB2777 100%)'
  }
]
</script>

<style scoped lang="scss">
// View-specific override for About page
.page-container {
  max-width: 1200px;
}

// Hero Section
.hero-section {
  text-align: center;
  padding: 3rem 0;
  margin-bottom: 2rem;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 1rem;
  
  @media (max-width: 768px) {
    font-size: 2rem;
  }
}

.gradient-text {
  background: linear-gradient(135deg, #E69830 0%, #F59E0B 50%, #E69830 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: #94a3b8;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
}

// Section Title
.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #f1f5f9;
  text-align: center;
  margin-bottom: 2rem;
}

// Logos Section
.logos-section {
  margin-bottom: 3rem;
}

.logos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}

.logo-card {
  background: rgba(30, 41, 59, 0.5) !important;
  border: 1px solid rgba(51, 65, 85, 0.5);
  border-radius: 16px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-4px);
    border-color: rgba(230, 152, 48, 0.3);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
  }
}

.logo-wrapper {
  width: 100%;
  max-width: 200px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.logo-svg {
  width: 100%;
  height: 100%;
  
  &.square {
    width: 80px;
    height: 80px;
  }
}

.logo-img {
  width: 80px;
  height: 80px;
  object-fit: contain;
}

.logo-info {
  h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 0.5rem;
  }
  
  p {
    font-size: 0.875rem;
    color: #94a3b8;
    line-height: 1.5;
    margin-bottom: 1rem;
  }
}

.logo-link {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  color: #E69830;
  text-decoration: none;
  transition: color 0.2s;
  
  &:hover {
    color: #F59E0B;
  }
}

// About Section
.about-section {
  margin-bottom: 3rem;
}

.info-card {
  background: rgba(30, 41, 59, 0.5) !important;
  border: 1px solid rgba(51, 65, 85, 0.5);
  border-radius: 16px;
  padding: 1.5rem;
  height: 100%;
  
  &.mission-card {
    max-width: 700px;
    margin: 0 auto;
    text-align: center;
    padding: 2rem;
  }
}

.info-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: rgba(230, 152, 48, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  
  .v-icon {
    color: #E69830;
  }
}

.info-card {
  h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 0.75rem;
  }
  
  p {
    font-size: 0.875rem;
    color: #94a3b8;
    line-height: 1.6;
  }
}

// Features Section
.features-section {
  margin-bottom: 3rem;
}

.feature-card {
  text-align: center;
  padding: 1.5rem;
}

.feature-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
}

.feature-card {
  h4 {
    font-size: 1rem;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 0.5rem;
  }
  
  p {
    font-size: 0.8125rem;
    color: #94a3b8;
    line-height: 1.5;
  }
}

// Footer
.about-footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem 0;
  border-top: 1px solid rgba(51, 65, 85, 0.3);
}

.funding-info {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  color: #64748b;
  text-align: center;
  
  .v-icon {
    color: #E69830;
  }
}

.version-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.version-label {
  font-size: 0.6875rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.version-number {
  font-size: 0.875rem;
  color: #94a3b8;
}

</style>
