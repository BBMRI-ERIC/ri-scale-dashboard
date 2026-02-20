import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Route definitions
const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { 
      requiresAuth: false,
      title: 'Login'
    }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Dashboard'
    }
  },
  {
    path: '/projects/:id',
    name: 'project-detail',
    component: () => import('@/views/ProjectDetailView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Project Details'
    }
  },
  {
    path: '/datasets',
    name: 'datasets',
    component: () => import('@/views/DatasetsView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Datasets'
    }
  },
  {
    path: '/transfers',
    name: 'transfers',
    component: () => import('@/views/DataTransfersView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Data Transfers'
    }
  },
  {
    path: '/computations',
    name: 'computations',
    component: () => import('@/views/ComputationsView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'HPC Jobs'
    }
  },
  {
    path: '/models',
    name: 'models',
    component: () => import('@/views/ModelsView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Model Hub'
    }
  },
  {
    path: '/resources',
    name: 'resources',
    component: () => import('@/views/ComputeResourcesView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Compute Quotas'
    }
  },
  {
    path: '/pipelines',
    name: 'dps-pipelines',
    component: () => import('@/views/DPSPipelinesView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'DPS Pipelines'
    }
  },
  {
    path: '/pipelines/new',
    name: 'pipeline-builder-new',
    component: () => import('@/views/PipelineBuilderView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'New Pipeline'
    }
  },
  {
    path: '/pipelines/builder',
    name: 'pipeline-builder',
    component: () => import('@/views/PipelineBuilderView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'Pipeline Builder'
    }
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('@/views/AboutView.vue'),
    meta: { 
      requiresAuth: true,
      title: 'About'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: {
      title: 'Page Not Found'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Initialize auth state if needed
  if (!authStore.isInitialized) {
    await authStore.initialize()
  }

  // Update document title
  document.title = to.meta.title 
    ? `${to.meta.title} | RI-SCALE Dashboard`
    : 'RI-SCALE Dashboard'

  // Check authentication requirements
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Redirect to login with return URL
    next({ 
      name: 'login', 
      query: { redirect: to.fullPath } 
    })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    // Already logged in, redirect to dashboard
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
