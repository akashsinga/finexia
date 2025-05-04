<!-- src/views/Login.vue -->
<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Card with slight glassmorphism effect -->
      <div class="login-card">
        <!-- Brand header -->
        <div class="brand">
          <div class="logo-container">
            <img src="@/assets/images/favicon.svg" class="brand-image" />
          </div>
          <div class="brand-text">
            <h1 class="brand-title">Finexia</h1>
            <p class="brand-subtitle">Predictive Market Analytics</p>
          </div>
        </div>

        <!-- Form with refined spacing -->
        <form @submit.prevent="handleLogin" class="login-form">
          <h2 class="form-title">Welcome Back</h2>

          <!-- Error alert with icon -->
          <div v-if="error" class="error-alert">
            <v-icon size="small" class="mr-2">mdi-alert-circle</v-icon>
            <span>{{ error }}</span>
          </div>

          <!-- Username field -->
          <div class="form-group">
            <label for="username">Username</label>
            <div class="input-with-icon">
              <v-icon size="small" class="input-icon">mdi-account</v-icon>
              <input id="username" v-model="username" type="text" placeholder="Enter your username" required autocomplete="username" class="input-field" />
            </div>
          </div>

          <!-- Password field -->
          <div class="form-group">
            <div class="password-label">
              <label for="password">Password</label>
              <a href="#" class="forgot-link">Forgot password?</a>
            </div>
            <div class="input-with-icon">
              <v-icon size="small" class="input-icon">mdi-lock</v-icon>
              <input id="password" v-model="password" :type="showPassword ? 'text' : 'password'" placeholder="Enter your password" required autocomplete="current-password" class="input-field" />
              <v-icon size="small" class="toggle-password" @click="showPassword = !showPassword">
                {{ showPassword ? 'mdi-eye-off' : 'mdi-eye' }}
              </v-icon>
            </div>
          </div>

          <!-- Remember me with custom styled checkbox -->
          <div class="remember-me">
            <label class="checkbox-container">
              <input type="checkbox" v-model="rememberMe">
              <span class="custom-checkbox">
                <v-icon v-if="rememberMe" size="x-small" color="white">mdi-check</v-icon>
              </span>
              <span class="ml-2">Remember me</span>
            </label>
          </div>

          <!-- Submit button with hover effect -->
          <button type="submit" class="login-button" :disabled="loading">
            <v-progress-circular v-if="loading" indeterminate size="20" width="2" color="white"></v-progress-circular>
            <span v-else>Sign In</span>
          </button>
        </form>

        <!-- Footer with divider -->
        <div class="login-footer">
          <div class="divider">
            <span>OR</span>
          </div>
          <p>Don't have an account? <a href="#" @click.prevent="goToRegister" class="signup-link">Sign up</a></p>
        </div>
      </div>
    </div>

    <!-- Decorative background elements -->
    <div class="background-decoration decoration-1"></div>
    <div class="background-decoration decoration-2"></div>
  </div>
</template>

<script>
import { useAuthStore } from '@/store/auth.store'

export default {
  name: 'LoginView',

  data() {
    return {
      username: '',
      password: '',
      rememberMe: false,
      showPassword: false,
      loading: false,
      error: null
    }
  },

  computed: {
    authStore() {
      return useAuthStore()
    }
  },

  methods: {
    async handleLogin() {
      if (!this.username || !this.password) return

      this.loading = true
      this.error = null

      try {
        await this.authStore.login(this.username, this.password)
        this.$router.push('app/dashboard')
      } catch (err) {
        this.error = err.response?.data?.message || 'Invalid credentials. Please try again.'
      } finally {
        this.loading = false
      }
    },

    goToRegister() {
      this.$router.push('/register')
    }
  }
}
</script>

<style lang="postcss" scoped>
.login-page {
  @apply min-h-screen w-full flex items-center justify-center bg-gray-50 relative overflow-hidden;
  background-image:
    radial-gradient(circle, rgba(30, 58, 138, 0.1) 2px, transparent 2px),
    radial-gradient(circle, rgba(14, 165, 233, 0.1) 2px, transparent 2px);
  background-size: 40px 40px;
  background-position: 0 0, 20px 20px;
}

.login-container {
  @apply w-full max-w-md px-4 z-10;
}

.login-card {
  @apply bg-white rounded-xl shadow-xl p-8 ring-1 ring-gray-300;
  backdrop-filter: blur(10px);
}

.brand {
  @apply flex flex-col items-center justify-center mb-6;
}

.logo-container {
  @apply mb-3 bg-primary rounded-full p-3 flex items-center justify-center;
}

.brand-image {
  @apply w-12 h-12;
}

.brand-text {
  @apply flex flex-col items-center;
}

.brand-title {
  @apply text-2xl font-semibold text-gray-800 mb-1;
}

.brand-subtitle {
  @apply text-sm text-gray-500;
}

.login-form {
  @apply flex flex-col;
}

.form-title {
  @apply text-xl font-medium text-center mb-4 text-gray-800;
}

.error-alert {
  @apply flex items-center p-3 mb-4 text-sm text-error bg-red-50 rounded-md;
}

.form-group {
  @apply mb-4;
}

.form-group label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.password-label {
  @apply flex justify-between items-center;
}

.forgot-link {
  @apply text-xs text-primary hover:text-primary-dark transition-colors duration-200;
}

.input-with-icon {
  @apply relative;
}

.input-icon {
  @apply absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400;
}

.toggle-password {
  @apply absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 cursor-pointer;
}

.input-field {
  @apply w-full py-2 pl-10 pr-10 outline-none ring-1 ring-gray-200 rounded-lg focus:ring-1 focus:ring-blue-400 focus:border-blue-400 transition-all duration-300 text-sm;
}

.remember-me {
  @apply flex items-center mb-4;
}

.checkbox-container {
  @apply flex items-center text-sm text-gray-600 cursor-pointer;
}

.custom-checkbox {
  @apply inline-flex items-center justify-center w-5 h-5 border border-gray-300 rounded mr-2 bg-white;
}

input[type="checkbox"] {
  @apply hidden;
}

input[type="checkbox"]:checked+.custom-checkbox {
  @apply bg-primary border-primary flex items-center justify-center;
}

.login-button {
  @apply w-full py-2 px-4 bg-primary text-white rounded-lg hover:bg-primary-dark focus:outline-none focus:ring-1 focus:ring-primary focus:ring-offset-2 flex items-center justify-center h-10 font-medium transition-colors duration-200;
}

.login-button:disabled {
  @apply opacity-70 cursor-not-allowed;
}

.login-footer {
  @apply text-center mt-6 text-sm text-gray-600;
}

.divider {
  @apply flex items-center mb-4;
}

.divider::before,
.divider::after {
  @apply flex-grow border-t border-gray-200;
  content: "";
}

.divider span {
  @apply px-3 text-xs text-gray-500;
}

.signup-link {
  @apply text-primary font-medium hover:text-primary-dark transition-colors duration-200;
}

/* Decorative background elements */
.background-decoration {
  @apply absolute rounded-full blur-3xl opacity-20;
  z-index: 1;
}

.decoration-1 {
  @apply bg-primary;
  width: 400px;
  height: 400px;
  top: -100px;
  right: -100px;
}

.decoration-2 {
  @apply bg-info;
  width: 300px;
  height: 300px;
  bottom: -50px;
  left: -50px;
}
</style>