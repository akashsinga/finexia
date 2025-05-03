<template>
  <div class="flex min-h-screen">
    <!-- Left sidebar/navbar -->
    <div class="fixed z-10 h-full text-white transition-all duration-300 bg-blue-900" :class="{ 'w-16': collapsed, 'w-64': !collapsed }">
      <div class="flex items-center justify-between h-16 p-4 border-b border-blue-800">
        <router-link to="/" class="flex items-center">
          <!-- <img src="@" alt="Finexia Logo" class="w-8 h-8" /> -->
          <span v-if="!collapsed" class="ml-2 text-xl font-bold">Finexia</span>
        </router-link>
        <button @click="toggleSidebar" class="text-white">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      </div>

      <div class="mt-6">
        <ul>
          <li class="mb-2">
            <router-link to="/" class="flex items-center px-4 py-3 transition-colors hover:bg-blue-800" active-class="bg-blue-800">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              <span v-if="!collapsed" class="ml-3">Dashboard</span>
            </router-link>
          </li>
          <li class="mb-2">
            <router-link to="/symbols" class="flex items-center px-4 py-3 transition-colors hover:bg-blue-800" active-class="bg-blue-800">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              </svg>
              <span v-if="!collapsed" class="ml-3">Symbols</span>
            </router-link>
          </li>
          <li class="mb-2">
            <router-link to="/predictions" class="flex items-center px-4 py-3 transition-colors hover:bg-blue-800" active-class="bg-blue-800">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span v-if="!collapsed" class="ml-3">Predictions</span>
            </router-link>
          </li>
          <li class="mb-2">
            <router-link to="/models" class="flex items-center px-4 py-3 transition-colors hover:bg-blue-800" active-class="bg-blue-800">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span v-if="!collapsed" class="ml-3">Models</span>
            </router-link>
          </li>
          <li class="mb-2">
            <router-link to="/settings" class="flex items-center px-4 py-3 transition-colors hover:bg-blue-800" active-class="bg-blue-800">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span v-if="!collapsed" class="ml-3">Settings</span>
            </router-link>
          </li>
        </ul>
      </div>
    </div>

    <!-- Main content area -->
    <div class="flex flex-col flex-1 transition-all duration-300" :class="{ 'ml-16': collapsed, 'ml-64': !collapsed }">
      <!-- Top navbar -->
      <header class="sticky top-0 flex items-center justify-between h-16 px-6 bg-white border-b border-gray-200 z-5">
        <div class="flex items-center">
          <!-- Page title - could be dynamic based on route -->
          <h1 class="text-xl font-semibold text-gray-800">{{ currentRouteName }}</h1>
        </div>

        <div class="flex items-center space-x-4">
          <!-- Search bar -->
          <div class="relative">
            <input type="text" placeholder="Search..." class="w-64 px-4 py-2 bg-gray-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 absolute right-3 top-2.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>

          <!-- Notifications -->
          <button class="text-gray-500 hover:text-gray-700">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </button>

          <!-- User menu -->
          <div class="relative">
            <button class="flex items-center space-x-2">
              <div class="flex items-center justify-center w-8 h-8 font-semibold text-white bg-blue-500 rounded-full">
                A
              </div>
              <span class="text-gray-700">Admin</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Main content with scrolling -->
      <main class="flex-1 p-6 overflow-auto">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DefaultLayout',
  data() {
    return {
      collapsed: false
    }
  },
  computed: {
    currentRouteName() {
      return this.$route.name || 'Dashboard'
    }
  },
  methods: {
    toggleSidebar() {
      this.collapsed = !this.collapsed
    }
  }
}
</script>