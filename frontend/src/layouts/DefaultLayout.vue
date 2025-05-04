<template>
  <div class="app-container">
    <!-- Sidebar -->
    <div class="sidebar" :class="{ collapsed }">
      <!-- Header -->
      <div class="sidebar-header">
        <div class="brand">
          <img src="@/assets/images/favicon.svg" class="brand-image" />
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
            <div v-for="(item, i) in navItems" :key="i" class="nav-item" :class="{ active: $route.name === item.pathName }" @click="$router.push({ name: item.pathName })">
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
            <div class="user-info">
              <div class="user-name">{{ authStore.username }}</div>
              <div class="user-email">{{ authStore.user?.email || 'N/A' }}</div>
            </div>
          </div>
          <v-icon class="logout-icon text-lg" @click.stop="logout">mdi-logout</v-icon>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div :class="['main-content', { collapsed }]">
      <div class="header">
        <h1 class="page-title">{{ $route.meta.title }}</h1>
        <div class="market-status flex items-center space-x-2 text-sm">
          <span :class="['status-dot', marketStatus === 'LIVE' ? 'bg-green-500' : 'bg-red-500']"></span>
          <span class="font-medium">{{ marketStatus }}</span>
          <span class="text-gray-500">• {{ formattedTime }} IST</span>
        </div>
      </div>

      <div class="content-area">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/store/auth.store'

export default {
  data() {
    return {
      collapsed: false,
      marketOpenTime: '09:15',
      marketCloseTime: '15:30',
      currentTime: new Date(),
      navItems: [
        { title: 'Dashboard', icon: 'mdi-view-dashboard', pathName: 'Dashboard' },
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
      return this.currentTime.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
    }
  },
  methods: {
    toggleSidebar: function () {
      this.collapsed = !this.collapsed
    },
    logout: function () {
      this.authStore.logout()
      this.$router.push({ name: 'Login' })
    }
  },
  mounted() {
    this._clock = setInterval(() => {
      this.currentTime = new Date()
    }, 60000)
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

.status-dot {
  @apply w-2 h-2 rounded-full;
}

.sidebar {
  @apply fixed z-10 h-full transition-all duration-300 w-64 p-4 bg-white ring-1 ring-gray-300 shadow-md flex flex-col justify-between;

  .collapse-button {
    @apply absolute top-1/2 -right-3 w-6 h-6 ring-1 ring-gray-300 bg-white rounded-full flex items-center justify-center shadow-md;

    .v-icon {
      @apply text-xl;
    }
  }

  .sidebar-header {
    @apply flex pb-3 border-b border-gray-300;

    .brand {
      @apply flex items-center space-x-2;

      .brand-image {
        @apply w-10 h-10;
      }

      .brand-text {
        @apply flex flex-col;

        .brand-title {
          @apply text-lg font-medium;
        }

        .brand-subtitle {
          @apply text-xs;
        }
      }
    }
  }

  .sidebar-content {
    @apply flex flex-col justify-between flex-grow;

    .sidebar-nav {
      @apply mt-4;

      .nav-list {
        @apply flex flex-col space-y-3;

        .nav-item {
          @apply flex relative cursor-pointer transition-all duration-300;

          .nav-status-indicator {
            @apply w-1.5 absolute bg-transparent h-3/4 -left-4 top-1.5 rounded-r-full;
          }

          .nav-link {
            @apply flex items-center w-full px-2 py-2 space-x-3 relative rounded-lg;

            .nav-link-icon {
              @apply text-xl;
            }

            .nav-link-text {
              @apply text-sm;
            }

            .active-icon {
              @apply text-xl absolute right-1;
            }
          }

          &:hover {
            .nav-link {
              @apply bg-gray-100;

              .nav-link-text {
                @apply font-medium;
              }
            }
          }

          &.active {
            .nav-status-indicator {
              @apply bg-primary;
            }

            .nav-link {
              @apply bg-gray-100;

              .nav-link-icon {
                @apply text-primary;
              }

              .nav-link-text {
                @apply font-medium;
              }
            }
          }
        }
      }
    }

    .user-account {
      @apply relative pt-3 border-t border-gray-300 flex justify-between items-center;

      .user-wrapper {
        @apply flex items-center space-x-3 pr-3 py-1;

        .avatar {
          @apply w-8 aspect-square min-w-[2rem] flex-shrink-0 rounded-full bg-primary text-white flex items-center justify-center font-semibold text-base;
        }

        .user-info {
          @apply flex flex-col;

          .user-name {
            @apply text-sm font-medium capitalize;
          }

          .user-email {
            @apply text-xs text-gray-500 truncate max-w-[10rem];
          }
        }
      }

      .logout-icon {
        @apply ml-auto text-gray-500 hover:text-red-500 cursor-pointer;
      }
    }
  }

  &.collapsed {
    @apply w-16 p-3;

    .sidebar-header {
      @apply px-1;
    }

    .sidebar-content .sidebar-nav .nav-list .nav-item .nav-link {
      @apply justify-center;
    }

    .user-account {
      @apply hidden;
    }
  }
}

.main-content {
  @apply flex flex-col min-h-screen transition-all duration-300 w-full pl-64;

  &.collapsed {
    @apply pl-16;
  }

  .header {
    @apply sticky top-0 z-10 bg-white ring-1 ring-gray-300 ml-[1px] px-6 py-3 flex items-center justify-between;

    .page-title {
      @apply text-lg font-medium;
    }
  }

  .content-area {
    @apply flex-1 p-6 overflow-auto;
    background: radial-gradient(circle, rgba(30, 58, 138, 0.1) 2px, transparent 2px), radial-gradient(circle, rgba(14, 165, 233, 0.1) 2px, transparent 2px);
    background-size: 40px 40px;
    background-position: 0 0, 20px 20px;
  }
}
</style>
