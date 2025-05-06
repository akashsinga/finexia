<template>
  <div class="app-container">
    <!-- Sidebar -->
    <div class="sidebar" :class="{ collapsed }">
      <!-- Header -->
      <div class="sidebar-header">
        <div class="brand">
          <div class="logo-container">
            <img src="@/assets/images/favicon.svg" class="brand-image" />
          </div>
          <div v-if="!collapsed" class="brand-text">
            <div class="brand-title">Finexia</div>
            <div class="brand-subtitle">Predictive Market Analytics</div>
          </div>
        </div>
      </div>

      <!-- Collapse Button -->
      <button class="collapse-button" @click="toggleSidebar" aria-label="Toggle sidebar">
        <v-icon>{{ collapsed ? 'mdi-chevron-right' : 'mdi-chevron-left' }}</v-icon>
      </button>

      <!-- Sidebar Content -->
      <div class="sidebar-content">
        <!-- Navigation -->
        <div class="sidebar-nav">
          <div class="nav-list">
            <div v-for="(item, i) in navItems" :key="i" class="nav-item" :class="{ active: $route.name === item.pathName }" @click="navigateTo(item.pathName)">
              <div v-if="!collapsed" class="nav-status-indicator"></div>
              <div class="nav-link">
                <v-icon class="nav-link-icon">{{ item.icon }}</v-icon>
                <div v-if="!collapsed" class="nav-link-text">{{ item.title }}</div>
                <v-icon v-if="!collapsed && $route.name === item.pathName" class="active-icon">mdi-chevron-right</v-icon>
              </div>
            </div>
          </div>
        </div>

        <!-- User Info with Logout Icon -->
        <div v-if="authStore.isLoggedIn" class="user-account">
          <div class="user-wrapper">
            <div class="avatar">{{ authStore.userInitials }}</div>
            <div v-if="!collapsed" class="user-info">
              <div class="user-name">{{ authStore.username }}</div>
              <div class="user-email">{{ authStore.user?.email || 'N/A' }}</div>
            </div>
          </div>
          <v-tooltip v-if="!collapsed" location="top" text="Logout">
            <template #activator="{ props }">
              <v-icon v-bind="props" class="logout-icon" @click.stop="logout">mdi-logout</v-icon>
            </template>
          </v-tooltip>
        </div>

        <!-- Separate logout button when collapsed -->
        <div v-if="collapsed && authStore.isLoggedIn" class="collapsed-logout">
          <v-tooltip location="right" text="Logout">
            <template #activator="{ props }">
              <v-btn v-bind="props" icon="mdi-logout" variant="text" size="small" color="gray" @click.stop="logout" class="logout-btn"></v-btn>
            </template>
          </v-tooltip>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div :class="['main-content', { collapsed }]">
      <div class="header">
        <div class="header-left">
          <h1 class="page-title">{{ $route.meta.title }}</h1>
          <div v-if="breadcrumbs.length > 1" class="breadcrumbs">
            <div v-for="(crumb, index) in breadcrumbs" :key="index" class="breadcrumb-item">
              <span v-if="index < breadcrumbs.length - 1" class="breadcrumb-link" @click="navigateTo(crumb.name)">
                {{ crumb.title }}
              </span>
              <span v-else class="breadcrumb-current">{{ crumb.title }}</span>
              <v-icon v-if="index < breadcrumbs.length - 1" size="small" class="breadcrumb-separator">mdi-chevron-right</v-icon>
            </div>
          </div>
        </div>
        <div class="header-right">
          <div class="market-status">
            <span :class="['status-dot', marketStatus === 'LIVE' ? 'bg-green-500' : 'bg-red-500']"></span>
            <span class="market-status-text">{{ marketStatus }}</span>
            <span class="market-time">• {{ formattedTime }} IST</span>
          </div>
          <div class="header-actions">
            <v-tooltip location="bottom" text="Notifications">
              <template #activator="{ props }">
                <v-btn v-bind="props" icon="mdi-bell-outline" variant="text" size="small" class="action-button">
                  <div class="notification-badge" v-if="notificationCount > 0">{{ notificationCount }}</div>
                </v-btn>
              </template>
            </v-tooltip>
            <v-tooltip location="bottom" text="Help">
              <template #activator="{ props }">
                <v-btn v-bind="props" icon="mdi-help-circle-outline" variant="text" size="small" class="action-button"></v-btn>
              </template>
            </v-tooltip>
          </div>
        </div>
      </div>

      <div class="content-area">
        <!-- Add transition wrapper around router-view -->
        <transition name="fade-slide" mode="out-in">
          <router-view />
        </transition>
      </div>

      <div class="footer">
        <div class="footer-content">
          <div class="footer-copyright">© {{ currentYear }} Finexia - All rights reserved</div>
          <div class="footer-version">Version 1.0.0</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/store/auth.store'

export default {
  data() {
    return {
      collapsed: true,
      marketOpenTime: '09:15',
      marketCloseTime: '15:30',
      currentTime: null,
      notificationCount: 3,
      navItems: [
        { title: 'Dashboard', icon: 'mdi-view-dashboard', pathName: 'Dashboard' },
        { title: 'Pipeline', icon: 'mdi-ray-start-vertex-end', pathName: 'PipelineDashboard' },
        { title: 'Symbols', icon: 'mdi-chart-line', pathName: 'SymbolsExplorer' },
        { title: 'Predictions', icon: 'mdi-chart-bar', pathName: 'Predictions' },
        { title: 'Models', icon: 'mdi-brain', pathName: 'ModelPerformance' },
        { title: 'Settings', icon: 'mdi-cog', pathName: 'Settings' }
      ]
    }
  },
  computed: {
    authStore() {
      return useAuthStore()
    },
    marketStatus: function () {
      const now = this.currentTime
      const open = new Date(now)
      const close = new Date(now)

      const [openH, openM] = this.marketOpenTime.split(':')
      const [closeH, closeM] = this.marketCloseTime.split(':')

      open.setHours(openH, openM, 0)
      close.setHours(closeH, closeM, 0)

      return now >= open && now <= close ? 'LIVE' : 'CLOSED'
    },
    formattedTime: function () {
      return this.currentTime.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    },
    currentYear() {
      return new Date().getFullYear()
    },
    breadcrumbs() {
      // Generate breadcrumbs based on current route
      const crumbs = []

      // Always include home
      crumbs.push({
        title: 'Home',
        name: 'Dashboard'
      })

      // Add current page
      if (this.$route.name && this.$route.name !== 'Dashboard') {
        // Find the nav item with the matching pathName
        const navItem = this.navItems.find(item => item.pathName === this.$route.name)

        if (navItem) {
          crumbs.push({
            title: navItem.title,
            name: navItem.pathName
          })
        }

        // If we have a route param like symbol, add it as the final crumb
        if (this.$route.params.symbol) {
          crumbs.push({
            title: this.$route.params.symbol,
            name: null
          })
        }
      }

      return crumbs
    }
  },
  methods: {
    toggleSidebar: function () {
      this.collapsed = !this.collapsed
    },
    logout: function () {
      this.authStore.logout()
      this.$router.push({ name: 'Login' })
    },
    navigateTo: function (routeName) {
      if (routeName) {
        this.$router.push({ name: routeName })
      }
    }
  },
  created() {
    this.currentTime = new Date()
    this._clock = setInterval(() => {
      this.currentTime = new Date()
    }, 1000)
  },
  beforeUnmount() {
    clearInterval(this._clock)
  }
}
</script>

<style lang="postcss" scoped>
.app-container {
  @apply flex min-h-screen w-full;
}

/* Sidebar Styling */
.sidebar {
  @apply fixed z-10 h-full transition-all duration-300 w-64 bg-white border-r border-gray-300 flex flex-col;

  /* Collapse Button */
  .collapse-button {
    @apply absolute top-1/2 -right-3.5 w-7 h-7 bg-white rounded-full flex items-center justify-center ring-1 ring-gray-300 text-gray-600 hover:text-primary transition-colors duration-200;
  }

  /* Header with Brand */
  .sidebar-header {
    @apply py-5 px-4 border-b border-gray-200;

    .brand {
      @apply flex items-center gap-3;

      .logo-container {
        @apply w-10 h-10 bg-primary bg-opacity-10 rounded-lg flex items-center justify-center p-1;
      }

      .brand-image {
        @apply w-full h-full;
      }

      .brand-text {
        @apply flex flex-col;

        .brand-title {
          @apply text-lg font-bold text-gray-800;
        }

        .brand-subtitle {
          @apply text-xs text-gray-500;
        }
      }
    }
  }

  /* Sidebar Content */
  .sidebar-content {
    @apply flex flex-col justify-between flex-grow px-3 py-4;

    /* Navigation Area */
    .sidebar-nav {
      @apply mb-auto;

      .nav-list {
        @apply flex flex-col space-y-1;

        .nav-item {
          @apply flex relative cursor-pointer rounded-lg transition-all duration-200;

          .nav-status-indicator {
            @apply w-1 absolute bg-transparent h-6 -left-3 top-1/2 -translate-y-1/2 rounded-r-full transition-all duration-200;
          }

          .nav-link {
            @apply flex items-center w-full py-2.5 px-3 space-x-3 rounded-lg transition-all duration-200;

            .nav-link-icon {
              @apply text-lg text-gray-500 transition-colors duration-200;
            }

            .nav-link-text {
              @apply text-sm text-gray-600 font-medium transition-colors duration-200;
            }

            .active-icon {
              @apply text-sm absolute right-2 opacity-0 transition-all duration-200;
            }
          }

          &:hover {
            .nav-link {
              @apply bg-gray-100;

              .nav-link-icon {
                @apply text-gray-700;
              }

              .nav-link-text {
                @apply text-gray-800;
              }
            }
          }

          &.active {
            .nav-status-indicator {
              @apply bg-primary;
            }

            .nav-link {
              @apply bg-primary bg-opacity-5;

              .nav-link-icon {
                @apply text-primary;
              }

              .nav-link-text {
                @apply text-primary font-semibold;
              }

              .active-icon {
                @apply text-primary opacity-100;
              }
            }
          }
        }
      }
    }

    /* User Account Area */
    .user-account {
      @apply mt-4 pt-4 border-t border-gray-200 flex justify-between items-center;

      .user-wrapper {
        @apply flex items-center gap-3;

        .avatar {
          @apply w-9 h-9 rounded-full bg-primary text-white flex items-center justify-center font-semibold text-sm;
        }

        .user-info {
          @apply flex flex-col;

          .user-name {
            @apply text-sm font-medium text-gray-800;
          }

          .user-email {
            @apply text-xs text-gray-500 truncate max-w-[10rem];
          }
        }
      }

      .logout-icon {
        @apply text-gray-500 hover:text-error transition-colors duration-200 cursor-pointer;
      }
    }

    /* Collapsed Logout */
    .collapsed-logout {
      @apply mt-2 flex justify-center border-t border-gray-200 pt-2;

      .logout-btn {
        @apply text-gray-500 hover:text-error transition-colors duration-200;
      }
    }
  }

  /* Collapsed State */
  &.collapsed {
    @apply w-16;

    .sidebar-header {
      @apply justify-center px-0;

      .brand {
        @apply justify-center;
      }
    }

    .sidebar-content {
      @apply px-2;

      .nav-item .nav-link {
        @apply justify-center;
      }

      .user-account {
        @apply justify-center;
      }

      .user-account .user-wrapper {
        @apply justify-center;
      }
    }
  }
}

/* Main Content Area */
.main-content {
  @apply flex flex-col min-h-screen transition-all duration-300 w-full pl-64;

  &.collapsed {
    @apply pl-16;
  }

  /* Header Styling */
  .header {
    @apply sticky top-0 z-40 px-6 py-3 flex items-center justify-between bg-white/90 border-b border-gray-300 backdrop-blur;

    .header-left {
      @apply flex flex-col;

      .page-title {
        @apply text-lg font-semibold text-primary;
      }

      .breadcrumbs {
        @apply flex items-center text-xs text-gray-500 mt-1;

        .breadcrumb-item {
          @apply flex items-center;
        }

        .breadcrumb-link {
          @apply text-primary hover:text-primary-dark cursor-pointer;
        }

        .breadcrumb-current {
          @apply font-medium text-gray-600;
        }

        .breadcrumb-separator {
          @apply mx-1 text-gray-400;
        }
      }
    }

    .header-right {
      @apply flex items-center gap-4;

      .market-status {
        @apply flex items-center gap-2 px-3 py-1 rounded-full text-sm bg-gray-100 border border-gray-300;

        .status-dot {
          @apply w-2.5 h-2.5 rounded-full shadow-md;
        }

        .market-status-text {
          @apply text-gray-700;
        }

        .market-time {
          @apply text-gray-500 text-xs;
        }
      }

      .header-actions {
        @apply flex items-center gap-1;

        .action-button {
          @apply relative;

          .notification-badge {
            @apply absolute -top-1 -right-1 w-4 h-4 rounded-full bg-error text-white text-[10px] flex items-center justify-center;
          }
        }
      }
    }
  }

  /* Content Area */
  .content-area {
    @apply flex-1 p-6 overflow-auto relative bg-gray-50;
  }

  .content-area::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
      radial-gradient(circle, rgba(191, 219, 254, 0.4) 1px, transparent 1px),
      radial-gradient(circle, rgba(186, 230, 253, 0.3) 1px, transparent 1px);
    background-size: 40px 40px;
    background-position: 0 0, 20px 20px;
    opacity: 0.5;
    pointer-events: none;
    z-index: 0;
  }

  /* Footer Area */
  .footer {
    @apply py-3 px-6 text-xs text-gray-500 bg-white/90 border-t border-gray-300 backdrop-blur;

    .footer-content {
      @apply flex justify-between items-center;
    }
  }
}

/* Page transition animations */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>