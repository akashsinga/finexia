<template>
  <div class="settings-page">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">Settings</h1>
      <div class="page-subtitle">Manage your account and application preferences</div>
    </div>

    <!-- Main Settings Container -->
    <div class="settings-card">
      <!-- Sidebar -->
      <div class="settings-sidebar">
        <div v-for="(section, index) in settingsSections" :key="index" @click="settingsStore.setActiveSection(section.id)" class="sidebar-item" :class="{ 'active': settingsStore.activeSection === section.id }">
          <v-icon size="small" class="sidebar-icon">{{ section.icon }}</v-icon>
          <span class="sidebar-text">{{ section.title }}</span>
        </div>
      </div>

      <!-- Content Area -->
      <div class="settings-content">
        <!-- Account Settings -->
        <div v-if="settingsStore.activeSection === 'account'" class="settings-section">
          <div class="section-header">
            <h2 class="section-title">Account Settings</h2>
            <div class="last-updated">Last updated: {{ settingsStore.formatDate(new Date()) }}</div>
          </div>

          <!-- Profile Card -->
          <div class="profile-card">
            <div class="profile-avatar">{{ authStore.userInitials }}</div>
            <div class="profile-details">
              <h3 class="profile-name">{{ authStore.username || 'User' }}</h3>
              <p class="profile-email">{{ authStore.user?.email || 'email@example.com' }}</p>
              <span class="profile-badge" :class="authStore.user?.is_admin ? 'badge-admin' : 'badge-user'">
                {{ authStore.user?.is_admin ? 'Administrator' : 'User' }}
              </span>
            </div>
          </div>

          <!-- Personal Information Form -->
          <div class="settings-block">
            <h3 class="block-title">Personal Information</h3>
            <div class="form-grid">
              <div class="form-group">
                <label>Full Name</label>
                <input v-model="settingsStore.account.fullName" type="text" placeholder="Enter your full name">
              </div>
              <div class="form-group">
                <label>Email Address</label>
                <input v-model="settingsStore.account.email" type="email" placeholder="Enter your email address">
              </div>
            </div>
            <button @click="saveAccountSettings" class="save-button" :disabled="settingsStore.loading.account">
              <v-icon v-if="settingsStore.loading.account" size="small">mdi-loading mdi-spin</v-icon>
              <span v-else>Save Changes</span>
            </button>
          </div>

          <!-- Password Form -->
          <div class="settings-block">
            <h3 class="block-title">Change Password</h3>
            <div class="form-grid">
              <div class="form-group">
                <label>Current Password</label>
                <input v-model="settingsStore.account.currentPassword" type="password" placeholder="Enter current password">
              </div>
              <div class="form-group">
                <label>New Password</label>
                <input v-model="settingsStore.account.newPassword" type="password" placeholder="Enter new password">
              </div>
              <div class="form-group">
                <label>Confirm Password</label>
                <input v-model="settingsStore.account.confirmPassword" type="password" placeholder="Confirm new password">
                <div v-if="!settingsStore.passwordsMatch" class="form-error">Passwords do not match</div>
              </div>
            </div>
            <div class="password-requirements">
              <div v-for="(met, req) in settingsStore.passwordRequirements" :key="req" class="requirement" :class="{ 'met': met }">
                <v-icon size="x-small">{{ met ? 'mdi-check-circle' : 'mdi-circle-outline' }}</v-icon>
                <span>{{ passwordRequirementLabels[req] }}</span>
              </div>
            </div>
            <button @click="changePassword" class="save-button" :disabled="settingsStore.loading.password">
              <v-icon v-if="settingsStore.loading.password" size="small">mdi-loading mdi-spin</v-icon>
              <span v-else>Update Password</span>
            </button>
          </div>
        </div>

        <!-- Appearance Settings -->
        <div v-if="settingsStore.activeSection === 'appearance'" class="settings-section">
          <div class="section-header">
            <h2 class="section-title">Appearance</h2>
            <div class="section-subtitle">Customize the look and feel of the application</div>
          </div>

          <!-- Theme Selection -->
          <div class="settings-block">
            <h3 class="block-title">Theme</h3>
            <div class="theme-grid">
              <div v-for="theme in settingsStore.options.themes" :key="theme.value" class="theme-card" :class="{ 'selected': settingsStore.appearance.theme === theme.value }" @click="settingsStore.appearance.theme = theme.value">
                <div class="theme-preview" :class="theme.preview"></div>
                <div class="theme-name">{{ theme.label }}</div>
              </div>
            </div>
          </div>

          <!-- Layout Preferences -->
          <div class="settings-block">
            <h3 class="block-title">Layout</h3>
            <div class="toggle-group">
              <div class="toggle-item">
                <div class="toggle-details">
                  <div class="toggle-label">Expanded Sidebar</div>
                  <div class="toggle-desc">Show expanded sidebar by default</div>
                </div>
                <div class="toggle-switch">
                  <input type="checkbox" id="sidebar-toggle" v-model="settingsStore.appearance.expandedSidebar">
                  <label for="sidebar-toggle" class="toggle-switch-label"></label>
                </div>
              </div>

              <div class="toggle-item">
                <div class="toggle-details">
                  <div class="toggle-label">Compact Tables</div>
                  <div class="toggle-desc">Use compact density for data tables</div>
                </div>
                <div class="toggle-switch">
                  <input type="checkbox" id="table-toggle" v-model="settingsStore.appearance.compactTables">
                  <label for="table-toggle" class="toggle-switch-label"></label>
                </div>
              </div>

              <div class="toggle-item">
                <div class="toggle-details">
                  <div class="toggle-label">Show Tooltips</div>
                  <div class="toggle-desc">Display helpful tooltips on hover</div>
                </div>
                <div class="toggle-switch">
                  <input type="checkbox" id="tooltip-toggle" v-model="settingsStore.appearance.showTooltips">
                  <label for="tooltip-toggle" class="toggle-switch-label"></label>
                </div>
              </div>
            </div>
            <button @click="saveAppearanceSettings" class="save-button" :disabled="settingsStore.loading.appearance">
              <v-icon v-if="settingsStore.loading.appearance" size="small">mdi-loading mdi-spin</v-icon>
              <span v-else>Save Changes</span>
            </button>
          </div>
        </div>

        <!-- Notifications Settings -->
        <div v-if="settingsStore.activeSection === 'notifications'" class="settings-section">
          <div class="section-header">
            <h2 class="section-title">Notifications</h2>
            <div class="section-subtitle">Manage notification preferences</div>
          </div>

          <!-- Email Notifications -->
          <div class="settings-block">
            <h3 class="block-title">Email Notifications</h3>
            <div class="toggle-group">
              <div class="toggle-item">
                <div class="toggle-details">
                  <div class="toggle-label">Pipeline Completion</div>
                  <div class="toggle-desc">Get notified when a pipeline run completes</div>
                </div>
                <div class="toggle-switch">
                  <input type="checkbox" id="pipeline-toggle" v-model="settingsStore.notifications.pipelineCompletion">
                  <label for="pipeline-toggle" class="toggle-switch-label"></label>
                </div>
              </div>

              <div class="toggle-item">
                <div class="toggle-details">
                  <div class="toggle-label">Model Training</div>
                  <div class="toggle-desc">Get notified when model training completes</div>
                </div>
                <div class="toggle-switch">
                  <input type="checkbox" id="training-toggle" v-model="settingsStore.notifications.modelTraining">
                  <label for="training-toggle" class="toggle-switch-label"></label>
                </div>
              </div>

              <div class="toggle-item">
                <div class="toggle-details">
                  <div class="toggle-label">High-Confidence Predictions</div>
                  <div class="toggle-desc">Get notified for high confidence predictions</div>
                </div>
                <div class="toggle-switch">
                  <input type="checkbox" id="confidence-toggle" v-model="settingsStore.notifications.highConfidence">
                  <label for="confidence-toggle" class="toggle-switch-label"></label>
                </div>
              </div>

              <div class="toggle-item">
                <div class="toggle-details">
                  <div class="toggle-label">System Alerts</div>
                  <div class="toggle-desc">Get notified for important system events</div>
                </div>
                <div class="toggle-switch">
                  <input type="checkbox" id="alerts-toggle" v-model="settingsStore.notifications.systemAlerts">
                  <label for="alerts-toggle" class="toggle-switch-label"></label>
                </div>
              </div>
            </div>
          </div>

          <!-- App Notifications -->
          <div class="settings-block">
            <h3 class="block-title">In-App Notifications</h3>
            <div class="toggle-group">
              <div class="toggle-item">
                <div class="toggle-details">
                  <div class="toggle-label">Notification Badge</div>
                  <div class="toggle-desc">Show notification count badge</div>
                </div>
                <div class="toggle-switch">
                  <input type="checkbox" id="badge-toggle" v-model="settingsStore.notifications.showBadge">
                  <label for="badge-toggle" class="toggle-switch-label"></label>
                </div>
              </div>

              <div class="toggle-item">
                <div class="toggle-details">
                  <div class="toggle-label">Desktop Notifications</div>
                  <div class="toggle-desc">Show desktop notifications</div>
                </div>
                <div class="toggle-switch">
                  <input type="checkbox" id="desktop-toggle" v-model="settingsStore.notifications.desktop">
                  <label for="desktop-toggle" class="toggle-switch-label"></label>
                </div>
              </div>

              <div class="toggle-item">
                <div class="toggle-details">
                  <div class="toggle-label">Sound Alerts</div>
                  <div class="toggle-desc">Play sound for new notifications</div>
                </div>
                <div class="toggle-switch">
                  <input type="checkbox" id="sound-toggle" v-model="settingsStore.notifications.sound">
                  <label for="sound-toggle" class="toggle-switch-label"></label>
                </div>
              </div>
            </div>
            <button @click="saveNotificationSettings" class="save-button" :disabled="settingsStore.loading.notifications">
              <v-icon v-if="settingsStore.loading.notifications" size="small">mdi-loading mdi-spin</v-icon>
              <span v-else>Save Changes</span>
            </button>
          </div>
        </div>

        <!-- API Settings -->
        <div v-if="settingsStore.activeSection === 'api'" class="settings-section">
          <div class="section-header">
            <h2 class="section-title">API Settings</h2>
            <div class="section-subtitle">Manage API keys and access</div>
          </div>

          <!-- API Keys -->
          <div class="settings-block">
            <div class="block-header">
              <h3 class="block-title">API Keys</h3>
              <button class="create-btn" @click="settingsStore.toggleNewKeyForm()">
                <v-icon size="small" class="mr-1">{{ settingsStore.showNewKeyForm ? 'mdi-minus' : 'mdi-plus' }}</v-icon>
                {{ settingsStore.showNewKeyForm ? 'Cancel' : 'New Key' }}
              </button>
            </div>

            <!-- New API Key Form -->
            <div class="new-key-form" v-if="settingsStore.showNewKeyForm">
              <div class="form-group">
                <label>Key Name</label>
                <div class="form-with-button">
                  <input v-model="settingsStore.newApiKey.name" type="text" placeholder="Enter a name for this API key">
                  <button class="create-key-btn" @click="generateApiKey" :disabled="!settingsStore.newApiKey.name || settingsStore.loading.apiKey">
                    <v-icon v-if="settingsStore.loading.apiKey" size="small">mdi-loading mdi-spin</v-icon>
                    <span v-else>Generate</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- API Keys List -->
            <div class="api-keys-container">
              <div v-if="settingsStore.api.keys.length === 0" class="empty-keys">
                <v-icon size="large" color="gray-400">mdi-key-outline</v-icon>
                <p>No API keys found</p>
                <button class="create-empty-btn" @click="settingsStore.toggleNewKeyForm()">
                  <v-icon size="small" class="mr-1">mdi-plus</v-icon>
                  Create API Key
                </button>
              </div>

              <div v-else class="api-key-list">
                <div v-for="(key, index) in settingsStore.api.keys" :key="index" class="api-key-item">
                  <div class="key-header">
                    <div class="key-name">{{ key.name }}</div>
                    <div class="key-created">Created {{ settingsStore.formatDate(key.created_at) }}</div>
                  </div>

                  <div class="key-value">
                    <div class="key-masked" v-if="!key.visible">{{ settingsStore.maskApiKey(key.key) }}</div>
                    <div class="key-full" v-else>{{ key.key }}</div>
                    <div class="key-actions">
                      <button class="key-action-btn" @click="settingsStore.toggleKeyVisibility(key.id)">
                        <v-icon size="small">{{ key.visible ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                      </button>
                      <button class="key-action-btn" @click="copyApiKey(key.key)">
                        <v-icon size="small">mdi-content-copy</v-icon>
                      </button>
                      <button class="key-action-btn error" @click="revokeApiKey(key.id)">
                        <v-icon size="small">mdi-delete</v-icon>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Rate Limiting -->
          <div class="settings-block">
            <h3 class="block-title">Rate Limiting</h3>
            <div class="rate-limit-container">
              <div class="rate-limit-label">Requests per minute</div>
              <div class="rate-limit-selector">
                <select v-model="settingsStore.api.rateLimit">
                  <option v-for="option in settingsStore.options.rateLimits" :key="option.value" :value="option.value">
                    {{ option.title }}
                  </option>
                </select>
              </div>
            </div>
            <div class="rate-limit-info">
              <v-icon size="small" color="blue-500" class="mr-1">mdi-information</v-icon>
              <span>Rate limiting applies to all API keys generated for your account.</span>
            </div>
            <button @click="saveApiSettings" class="save-button" :disabled="settingsStore.loading.api">
              <v-icon v-if="settingsStore.loading.api" size="small">mdi-loading mdi-spin</v-icon>
              <span v-else>Save Changes</span>
            </button>
          </div>
        </div>

        <!-- System Settings -->
        <div v-if="settingsStore.activeSection === 'system'" class="settings-section">
          <div class="section-header">
            <h2 class="section-title">System Settings</h2>
            <div class="section-subtitle">Configure advanced system parameters</div>
          </div>

          <!-- Pipeline Settings -->
          <div class="settings-block">
            <h3 class="block-title">Pipeline Configuration</h3>

            <div class="form-row">
              <div class="form-group">
                <label>Pipeline Schedule</label>
                <select v-model="settingsStore.system.pipelineSchedule">
                  <option v-for="option in settingsStore.options.scheduleTimes" :key="option.value" :value="option.value">
                    {{ option.title }}
                  </option>
                </select>
                <div class="form-hint">Daily run time in 24-hour format</div>
              </div>

              <div class="form-group">
                <label>Maximum Symbols</label>
                <input v-model="settingsStore.system.maxSymbols" type="number" min="1" max="500">
                <div class="form-hint">Maximum number of symbols to process</div>
              </div>
            </div>
          </div>

          <!-- Model Training Settings -->
          <div class="settings-block">
            <h3 class="block-title">Model Training</h3>

            <div class="form-row">
              <div class="form-group">
                <label>Default Classifier</label>
                <select v-model="settingsStore.system.defaultClassifier">
                  <option v-for="option in settingsStore.options.classifiers" :key="option.value" :value="option.value">
                    {{ option.title }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>Maximum Days to Look Ahead</label>
                <select v-model="settingsStore.system.maxDays">
                  <option v-for="option in settingsStore.options.days" :key="option.value" :value="option.value">
                    {{ option.title }}
                  </option>
                </select>
              </div>
            </div>

            <div class="threshold-slider">
              <label>Strong Move Threshold: {{ settingsStore.system.strongMoveThreshold }}%</label>
              <input type="range" v-model.number="settingsStore.system.strongMoveThreshold" min="0.5" max="10" step="0.5" class="range">
              <div class="range-markers">
                <span>0.5%</span>
                <span>5%</span>
                <span>10%</span>
              </div>
            </div>
          </div>

          <!-- Advanced Settings -->
          <div class="settings-block">
            <h3 class="block-title">Advanced Settings</h3>

            <div class="toggle-group">
              <div class="toggle-item">
                <div class="toggle-details">
                  <div class="toggle-label">Enable Logging</div>
                  <div class="toggle-desc">Log system activity for troubleshooting</div>
                </div>
                <div class="toggle-switch">
                  <input type="checkbox" id="logging-toggle" v-model="settingsStore.system.enableLogging">
                  <label for="logging-toggle" class="toggle-switch-label"></label>
                </div>
              </div>

              <div class="form-group" v-if="settingsStore.system.enableLogging">
                <label>Log Level</label>
                <select v-model="settingsStore.system.logLevel" :disabled="!settingsStore.system.enableLogging">
                  <option v-for="option in settingsStore.options.logLevels" :key="option.value" :value="option.value">
                    {{ option.title }}
                  </option>
                </select>
              </div>

              <div class="toggle-item">
                <div class="toggle-details">
                  <div class="toggle-label">Database Connection Pooling</div>
                  <div class="toggle-desc">Optimize database performance</div>
                </div>
                <div class="toggle-switch">
                  <input type="checkbox" id="pooling-toggle" v-model="settingsStore.system.connectionPooling">
                  <label for="pooling-toggle" class="toggle-switch-label"></label>
                </div>
              </div>
            </div>

            <button @click="saveSystemSettings" class="save-button" :disabled="settingsStore.loading.system">
              <v-icon v-if="settingsStore.loading.system" size="small">mdi-loading mdi-spin</v-icon>
              <span v-else>Save Changes</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/store/auth.store';
import { useSettingsStore } from '@/store/settings.store';

export default {
  name: 'Settings',
  data() {
    return {
      authStore: useAuthStore(),
      settingsStore: useSettingsStore(),

      // Settings sections
      settingsSections: [
        { id: 'account', title: 'Account', icon: 'mdi-account-circle' },
        { id: 'appearance', title: 'Appearance', icon: 'mdi-palette' },
        { id: 'notifications', title: 'Notifications', icon: 'mdi-bell' },
        { id: 'api', title: 'API Keys', icon: 'mdi-api' },
        { id: 'system', title: 'System', icon: 'mdi-cog' }
      ],

      // Password requirement labels
      passwordRequirementLabels: {
        length: 'At least 8 characters',
        uppercase: '1 uppercase letter',
        number: '1 number',
        special: '1 special character'
      }
    };
  },

  methods: {
    async saveAccountSettings() {
      try {
        await this.settingsStore.saveAccountSettings();
        this.$toast.success('Account settings updated successfully');
      } catch (error) {
        this.$toast.error('Failed to update account settings');
      }
    },

    async changePassword() {
      try {
        await this.settingsStore.changePassword();
        this.$toast.success('Password updated successfully');
      } catch (error) {
        this.$toast.error(error.message || 'Failed to update password');
      }
    },

    async saveAppearanceSettings() {
      try {
        await this.settingsStore.saveAppearanceSettings();
        this.$toast.success('Appearance settings saved');
      } catch (error) {
        this.$toast.error('Failed to save appearance settings');
      }
    },

    async saveNotificationSettings() {
      try {
        await this.settingsStore.saveNotificationSettings();
        this.$toast.success('Notification settings saved');
      } catch (error) {
        this.$toast.error('Failed to save notification settings');
      }
    },

    async saveApiSettings() {
      try {
        await this.settingsStore.saveApiSettings();
        this.$toast.success('API settings saved');
      } catch (error) {
        this.$toast.error('Failed to save API settings');
      }
    },

    async saveSystemSettings() {
      try {
        await this.settingsStore.saveSystemSettings();
        this.$toast.success('System settings saved');
      } catch (error) {
        this.$toast.error('Failed to save system settings');
      }
    },

    async generateApiKey() {
      try {
        await this.settingsStore.generateApiKey();
        this.$toast.success('API key generated successfully');
      } catch (error) {
        this.$toast.error(error.message || 'Failed to generate API key');
      }
    },

    async revokeApiKey(keyId) {
      try {
        await this.settingsStore.revokeApiKey(keyId);
        this.$toast.success('API key revoked successfully');
      } catch (error) {
        this.$toast.error('Failed to revoke API key');
      }
    },

    async copyApiKey(key) {
      try {
        await this.settingsStore.copyToClipboard(key);
        this.$toast.success('API key copied to clipboard');
      } catch (error) {
        this.$toast.error('Failed to copy API key');
      }
    }
  },

  mounted() {
    this.settingsStore.loadUserData(this.authStore.user);
    this.settingsStore.loadApiKeys();
  }
};
</script>

<style lang="postcss" scoped>
.settings-page {
  @apply w-full flex flex-col gap-6;
}

/* Page Header */
.page-header {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 p-5;
}

.page-title {
  @apply text-xl font-bold text-gray-800;
}

.page-subtitle {
  @apply text-sm text-gray-500 mt-1;
}

/* Settings card with sidebar */
.settings-card {
  @apply bg-gray-50 rounded-lg shadow-sm border border-gray-200 flex flex-col md:flex-row overflow-hidden;
}

/* Sidebar */
.settings-sidebar {
  @apply w-full md:w-64 bg-white border-b md:border-r md:border-b-0 border-gray-200 py-2 flex flex-row md:flex-col overflow-x-auto md:overflow-x-visible flex-nowrap;
}

.sidebar-item {
  @apply flex items-center gap-3 px-4 py-3 text-gray-600 hover:bg-gray-100 cursor-pointer transition-colors whitespace-nowrap md:whitespace-normal;
}

.sidebar-item.active {
  @apply bg-primary bg-opacity-5 text-primary border-b-2 md:border-b-0 md:border-l-2 border-primary;
}

.sidebar-icon {
  @apply text-current;
}

.sidebar-text {
  @apply text-sm font-medium;
}

/* Content area */
.settings-content {
  @apply flex-1 overflow-y-auto overflow-x-hidden;
}

.settings-section {
  @apply p-4 md:p-6 max-w-full;
}

.section-header {
  @apply mb-6;
}

.section-title {
  @apply text-lg font-bold text-gray-800;
}

.section-subtitle {
  @apply text-sm text-gray-500 mt-1;
}

.last-updated {
  @apply text-xs text-gray-500 mt-1;
}

/* Profile card */
.profile-card {
  @apply flex items-center gap-4 bg-gray-50 p-4 rounded-lg mb-6;
}

.profile-avatar {
  @apply w-16 h-16 rounded-full bg-primary text-white flex items-center justify-center text-xl font-bold;
}

.profile-details {
  @apply flex-1;
}

.profile-name {
  @apply text-base font-medium;
}

.profile-email {
  @apply text-sm text-gray-500;
}

.profile-badge {
  @apply inline-flex mt-1 px-2 py-0.5 rounded-full text-xs font-medium;
}

.badge-admin {
  @apply bg-primary bg-opacity-10 text-primary;
}

.badge-user {
  @apply bg-gray-200 text-gray-700;
}

/* Settings blocks */
.settings-block {
  @apply mb-6 bg-white rounded-lg border border-gray-200 p-3 md:p-4 w-full max-w-full overflow-hidden;
}

.block-header {
  @apply flex justify-between items-center mb-3;
}

.block-title {
  @apply text-sm font-medium text-gray-700 mb-3;
}

/* Form elements */
.form-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-4 mb-4;
}

.form-row {
  @apply flex flex-wrap gap-4 mb-4;
}

.form-group {
  @apply flex-1 min-w-[200px];
}

.form-group label {
  @apply block text-xs font-medium text-gray-700 mb-1;
}

.form-group input,
.form-group select {
  @apply w-full px-3 py-1.5 bg-white border border-gray-300 rounded-md focus:ring-1 focus:ring-primary focus:border-primary text-sm shadow-sm;
  transition: all 0.2s ease-in-out;
}

.form-group input:focus,
.form-group select:focus {
  @apply outline-none ring-2 ring-primary ring-opacity-50;
  box-shadow: 0 0 0 1px rgba(30, 58, 138, 0.2);
}

.form-hint {
  @apply text-xs text-gray-500 mt-1;
}

.form-error {
  @apply text-xs text-red-500 mt-1;
}

.form-with-button {
  @apply flex gap-2;
}

/* Password requirements */
.password-requirements {
  @apply grid grid-cols-1 sm:grid-cols-2 gap-2 my-3;
}

.requirement {
  @apply flex items-center gap-1 text-xs text-gray-500;
}

.requirement.met {
  @apply text-green-600;
}

/* Theme cards */
.theme-grid {
  @apply grid grid-cols-3 gap-4;
}

.theme-card {
  @apply border border-gray-200 rounded-lg p-2 cursor-pointer transition-all hover:border-primary;
}

.theme-card.selected {
  @apply border-primary bg-primary bg-opacity-5;
}

.theme-preview {
  @apply w-full h-20 rounded-lg mb-1;
}

.preview-light {
  @apply bg-gradient-to-br from-white to-gray-100 border border-gray-200;
}

.preview-dark {
  @apply bg-gradient-to-br from-gray-800 to-gray-900;
}

.preview-system {
  @apply bg-gradient-to-br from-blue-50 to-indigo-100 border border-gray-200;
}

.theme-name {
  @apply text-center text-sm mt-1;
}

/* Toggle switches */
.toggle-group {
  @apply space-y-4;
}

.toggle-item {
  @apply flex justify-between items-center;
}

.toggle-details {
  @apply flex-1;
}

.toggle-label {
  @apply text-sm font-medium text-gray-700;
}

.toggle-desc {
  @apply text-xs text-gray-500 mt-0.5;
}

/* Custom switch */
.toggle-switch {
  @apply relative inline-flex items-center cursor-pointer;
}

.toggle-switch input {
  @apply opacity-0 w-0 h-0;
}

.toggle-switch-label {
  @apply relative inline-block w-11 h-6 bg-gray-300 rounded-full transition-colors duration-200 ease-in-out cursor-pointer;
}

.toggle-switch-label:before {
  @apply absolute content-[''] h-4 w-4 left-1 bottom-1 bg-white rounded-full transition-transform duration-200 ease-in-out;
}

input:checked+.toggle-switch-label {
  @apply bg-primary;
}

input:focus+.toggle-switch-label {
  @apply ring-2 ring-primary ring-opacity-50;
}

input:checked+.toggle-switch-label:before {
  @apply transform translate-x-5;
}

/* API keys */
.create-btn {
  @apply flex items-center text-xs font-medium text-primary px-2 py-1 rounded-md bg-primary bg-opacity-10 hover:bg-opacity-20 transition-colors;
}

.new-key-form {
  @apply bg-gray-50 p-3 rounded-lg mb-4;
}

.create-key-btn {
  @apply px-3 py-1 bg-primary text-white rounded-md text-xs font-medium hover:bg-primary-dark transition-colors;
}

.empty-keys {
  @apply flex flex-col items-center justify-center py-8 space-y-2 text-gray-500;
}

.create-empty-btn {
  @apply flex items-center text-xs font-medium text-primary mt-2;
}

.api-key-list {
  @apply space-y-3;
}

.api-key-item {
  @apply border border-gray-200 rounded-lg p-3;
}

.key-header {
  @apply flex justify-between items-center mb-2;
}

.key-name {
  @apply font-medium;
}

.key-created {
  @apply text-xs text-gray-500;
}

.key-value {
  @apply flex justify-between flex-wrap gap-2;
}

.key-masked,
.key-full {
  @apply font-mono text-sm bg-gray-100 px-3 py-1.5 rounded flex-grow;
}

.key-full {
  @apply break-all;
}

.key-actions {
  @apply flex items-center;
}

.key-action-btn {
  @apply p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors;
}

.key-action-btn.error {
  @apply hover:text-red-500;
}

.rate-limit-container {
  @apply flex justify-between items-center mb-2;
}

.rate-limit-label {
  @apply text-sm font-medium text-gray-700;
}

.rate-limit-selector {
  @apply w-48;
}

.rate-limit-info {
  @apply flex items-start text-xs text-blue-600 bg-blue-50 p-2 rounded-lg mb-4;
}

/* Range slider */
.threshold-slider {
  @apply mb-4;
}

.threshold-slider label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.range {
  @apply w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary;
}

.range-markers {
  @apply flex justify-between text-xs text-gray-500 mt-1;
}

/* Save button */
.save-button {
  @apply w-full sm:w-auto mt-4 px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark transition-colors flex items-center justify-center gap-2 font-medium disabled:opacity-60 disabled:cursor-not-allowed;
}
</style>
