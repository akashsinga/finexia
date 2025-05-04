<template>
  <div class="app-container">
    <div class="sidebar" :class="{ 'collapsed': collapsed }">
      <div class="sidebar-header">
        <div class="brand">
          <img src="@/assets/images/favicon.svg" class="brand-image" />
          <div v-if="!collapsed" class="flex flex-col">
            <div class="brand-title">Finexia</div>
            <div class="brand-subtitle">Predictive Market Analytics</div>
          </div>
        </div>
      </div>
      <div class="collapse-button">
        <v-icon @click="collapsed = !collapsed">{{ collapsed ? 'mdi-chevron-right' : 'mdi-chevron-left' }}</v-icon>
      </div>
      <div class="sidebar-nav">
        <div class="nav-list">
          <div v-for="(item, i) in navItems" :key="i" class="nav-item" :class="{ 'active': $route.path.includes(item.to) }">
            <div v-if="!collapsed" class="nav-status-indicator"></div>
            <div class="nav-link">
              <v-icon class="nav-link-icon">{{ item.icon }}</v-icon>
              <div v-if="!collapsed" class="nav-link-text">{{ item.title }}</div>
              <v-icon class="active-icon" v-if="!collapsed && $route.path.includes(item.to)">mdi-chevron-right</v-icon>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      collapsed: false,
      navItems: [
        { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/dashboard' },
        { title: 'Symbols', icon: 'mdi-chart-line', to: '/symbols' },
        { title: 'Predictions', icon: 'mdi-chart-bar', to: '/predictions' },
        { title: 'Models', icon: 'mdi-brain', to: '/models' },
        { title: 'Settings', icon: 'mdi-cog', to: '/settings' },
      ]
    }
  }
}
</script>
<style lang="postcss" scoped>
.app-container {
  @apply flex min-h-screen;
}

.sidebar {
  @apply fixed z-10 h-full transition-all duration-300 w-64 p-4 bg-white ring-1 ring-gray-300 shadow-md;

  .collapse-button {
    @apply absolute top-1/2 -right-3 ring-1 ring-gray-300 bg-white rounded-full flex items-center justify-center shadow-md;
  }

  .sidebar-header {
    @apply flex pb-3 border-b border-gray-300;

    .brand {
      @apply flex items-center space-x-2;

      .brand-image {
        @apply w-10 h-10;
      }

      .brand-title {
        @apply text-lg font-medium;
      }

      .brand-subtitle {
        @apply text-xs;
      }
    }
  }

  .sidebar-nav {
    @apply mt-4;

    .nav-list {
      @apply flex flex-col space-y-3;

      .nav-item {
        @apply flex relative cursor-pointer;

        .nav-status-indicator {
          @apply w-1.5 absolute bg-transparent h-3/4 -left-4 top-1.5 rounded-r-full;
        }

        .nav-link {
          @apply flex items-center w-full px-2 py-2 space-x-3 relative rounded-lg;

          .nav-link-icon {
            @apply text-xl top-[1px];
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
            @apply bg-orange-500;
          }

          .nav-link {
            @apply bg-gray-100;

            .nav-link-icon {
              @apply text-orange-500;
            }

            .nav-link-text {
              @apply font-medium;
            }
          }
        }
      }
    }
  }

  &.collapsed {
    @apply w-16 p-3;

    .sidebar-header {
      @apply px-1;
    }

    .sidebar-nav {
      .nav-list .nav-item .nav-link {
        @apply justify-center;
      }
    }
  }
}
</style>