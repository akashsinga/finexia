// src/store/settings.store.js
import { defineStore } from 'pinia';
import { api } from '@/plugins';

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    activeSection: 'account',

    account: {
      fullName: '',
      email: '',
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    },

    appearance: {
      theme: 'light',
      expandedSidebar: false,
      compactTables: true,
      showTooltips: true
    },

    notifications: {
      pipelineCompletion: true,
      modelTraining: true,
      highConfidence: false,
      systemAlerts: true,
      showBadge: true,
      desktop: false,
      sound: false
    },

    api: {
      keys: [],
      rateLimit: 100
    },

    system: {
      pipelineSchedule: '02:00',
      maxSymbols: 100,
      defaultClassifier: 'lightgbm',
      strongMoveThreshold: 3.0,
      maxDays: 5,
      enableLogging: true,
      logLevel: 'INFO',
      connectionPooling: true
    },

    loading: {
      account: false,
      password: false,
      appearance: false,
      notifications: false,
      api: false,
      apiKey: false,
      system: false
    },

    error: null,

    // UI state
    showNewKeyForm: false,
    newApiKey: {
      name: ''
    }
  }),

  getters: {
    // Check if passwords match
    passwordsMatch: (state) => {
      return !state.account.newPassword || !state.account.confirmPassword || state.account.newPassword === state.account.confirmPassword;
    },

    // Password requirements checks
    passwordRequirements: (state) => {
      const { newPassword } = state.account;
      return {
        length: newPassword.length >= 8,
        uppercase: !!newPassword.match(/[A-Z]/),
        number: !!newPassword.match(/[0-9]/),
        special: !!newPassword.match(/[^A-Za-z0-9]/)
      };
    },

    // Options for select inputs
    options: () => ({
      scheduleTimes: [
        { title: '00:00', value: '00:00' },
        { title: '02:00', value: '02:00' },
        { title: '04:00', value: '04:00' },
        { title: '06:00', value: '06:00' },
        { title: '08:00', value: '08:00' },
        { title: '10:00', value: '10:00' },
        { title: '12:00', value: '12:00' },
        { title: '14:00', value: '14:00' },
        { title: '16:00', value: '16:00' },
        { title: '18:00', value: '18:00' },
        { title: '20:00', value: '20:00' },
        { title: '22:00', value: '22:00' }
      ],
      themes: [
        { value: 'light', label: 'Light', preview: 'preview-light' },
        { value: 'dark', label: 'Dark', preview: 'preview-dark' },
        { value: 'system', label: 'System Default', preview: 'preview-system' }
      ],
      classifiers: [
        { title: 'LightGBM', value: 'lightgbm' },
        { title: 'XGBoost', value: 'xgboost' },
        { title: 'Random Forest', value: 'randomforest' }
      ],
      days: [
        { title: '1 day', value: 1 },
        { title: '3 days', value: 3 },
        { title: '5 days', value: 5 },
        { title: '7 days', value: 7 },
        { title: '10 days', value: 10 },
        { title: '14 days', value: 14 }
      ],
      logLevels: [
        { title: 'DEBUG', value: 'DEBUG' },
        { title: 'INFO', value: 'INFO' },
        { title: 'WARNING', value: 'WARNING' },
        { title: 'ERROR', value: 'ERROR' },
        { title: 'CRITICAL', value: 'CRITICAL' }
      ],
      rateLimits: [
        { title: '60 requests/minute', value: 60 },
        { title: '100 requests/minute', value: 100 },
        { title: '300 requests/minute', value: 300 },
        { title: '500 requests/minute', value: 500 },
        { title: '1000 requests/minute', value: 1000 }
      ]
    })
  },

  actions: {
    /**
     * Set active settings section
     */
    setActiveSection(section) {
      this.activeSection = section;
    },

    /**
     * Load all user settings from API
     */
    async loadUserData(userData) {
      // Initialize account data from user
      if (userData) {
        this.account.fullName = userData.full_name || '';
        this.account.email = userData.email || '';
      }

      // Load saved settings if available
      try {
        const response = await api.get('/users/settings');
        const settings = response.data;

        // Apply stored settings if available
        if (settings.appearance) this.appearance = { ...this.appearance, ...settings.appearance };
        if (settings.notifications) this.notifications = { ...this.notifications, ...settings.notifications };
        if (settings.api) this.api = { ...this.api, ...settings.api };
        if (settings.system) this.system = { ...this.system, ...settings.system };
      } catch (error) {
        console.error('Failed to load user settings:', error);
        this.error = error.message || 'Failed to load user settings';
        // Continue with defaults
      }
    },

    /**
     * Load API keys
     */
    async loadApiKeys() {
      try {
        const response = await api.get('/users/api-keys');
        this.api.keys = response.data.map(key => ({ ...key, visible: false }));
        return this.api.keys;
      } catch (error) {
        console.error('Failed to load API keys:', error);
        this.error = error.message || 'Failed to load API keys';
        this.api.keys = [];
        throw error;
      }
    },

    /**
     * Save account settings
     */
    async saveAccountSettings() {
      this.loading.account = true;
      this.error = null;

      try {
        const payload = { full_name: this.account.fullName, email: this.account.email };
        await api.put(`/users/account`, payload);
        return true;
      } catch (error) {
        console.error('Failed to update account settings:', error);
        this.error = error.message || 'Failed to update account settings';
        throw error;
      } finally {
        this.loading.account = false;
      }
    },

    /**
     * Change password
     */
    async changePassword() {
      if (!this.passwordsMatch) {
        throw new Error('Passwords do not match');
      }

      if (!this.account.currentPassword || !this.account.newPassword) {
        throw new Error('Current and new passwords are required');
      }

      this.loading.password = true;
      this.error = null;

      try {
        await api.put(`/users/password`, { current_password: this.account.currentPassword, password: this.account.newPassword });

        // Reset form
        this.account.currentPassword = '';
        this.account.newPassword = '';
        this.account.confirmPassword = '';

        return true;
      } catch (error) {
        console.error('Failed to update password:', error);
        this.error = error.message || 'Failed to update password';
        throw error;
      } finally {
        this.loading.password = false;
      }
    },

    /**
     * Save appearance settings
     */
    async saveAppearanceSettings() {
      this.loading.appearance = true;
      this.error = null;

      try {
        await api.post('/users/settings/appearance', this.appearance);
        return true;
      } catch (error) {
        console.error('Failed to save appearance settings:', error);
        this.error = error.message || 'Failed to save appearance settings';
        throw error;
      } finally {
        this.loading.appearance = false;
      }
    },

    /**
     * Save notification settings
     */
    async saveNotificationSettings() {
      this.loading.notifications = true;
      this.error = null;

      try {
        await api.post('/users/settings/notifications', this.notifications);
        return true;
      } catch (error) {
        console.error('Failed to save notification settings:', error);
        this.error = error.message || 'Failed to save notification settings';
        throw error;
      } finally {
        this.loading.notifications = false;
      }
    },

    /**
     * Save API settings
     */
    async saveApiSettings() {
      this.loading.api = true;
      this.error = null;

      try {
        await api.post('/users/settings/api', { rateLimit: this.api.rateLimit });
        return true;
      } catch (error) {
        console.error('Failed to save API settings:', error);
        this.error = error.message || 'Failed to save API settings';
        throw error;
      } finally {
        this.loading.api = false;
      }
    },

    /**
     * Save system settings
     */
    async saveSystemSettings() {
      this.loading.system = true;
      this.error = null;

      try {
        await api.post('/system/settings', this.system);
        return true;
      } catch (error) {
        console.error('Failed to save system settings:', error);
        this.error = error.message || 'Failed to save system settings';
        throw error;
      } finally {
        this.loading.system = false;
      }
    },

    /**
     * Generate API key
     */
    async generateApiKey() {
      if (!this.newApiKey.name) {
        throw new Error('Please enter a name for the API key');
      }

      this.loading.apiKey = true;
      this.error = null;

      try {
        const response = await api.post('/users/api-keys', {
          name: this.newApiKey.name
        });

        // Add new key to list
        this.api.keys.unshift({ ...response.data, visible: true });

        // Reset form
        this.newApiKey.name = '';
        this.showNewKeyForm = false;

        return response.data;
      } catch (error) {
        console.error('Failed to generate API key:', error);
        this.error = error.message || 'Failed to generate API key';
        throw error;
      } finally {
        this.loading.apiKey = false;
      }
    },

    /**
     * Revoke API key
     */
    async revokeApiKey(keyId) {
      try {
        await api.delete(`/users/api-keys/${keyId}`);

        // Remove key from list
        this.api.keys = this.api.keys.filter(key => key.id !== keyId);
        return true;
      } catch (error) {
        console.error('Failed to revoke API key:', error);
        this.error = error.message || 'Failed to revoke API key';
        throw error;
      }
    },

    /**
     * Toggle API key visibility
     */
    toggleKeyVisibility(keyId) {
      const keyIndex = this.api.keys.findIndex(key => key.id === keyId);

      if (keyIndex !== -1) {
        this.api.keys[keyIndex].visible = !this.api.keys[keyIndex].visible;
      }
    },

    /**
     * Toggle new key form visibility
     */
    toggleNewKeyForm() {
      this.showNewKeyForm = !this.showNewKeyForm;
      if (!this.showNewKeyForm) {
        this.newApiKey.name = '';
      }
    },

    /**
     * Format a date for display
     */
    formatDate(dateString, format = 'MMM D, YYYY') {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    },

    /**
     * Mask an API key for display
     */
    maskApiKey(key) {
      if (!key) return '';

      const firstChars = key.substring(0, 4);
      const lastChars = key.substring(key.length - 4);
      return `${firstChars}...${lastChars}`;
    },

    /**
     * Copy text to clipboard
     */
    async copyToClipboard(text) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (error) {
        console.error('Failed to copy to clipboard:', error);
        throw error;
      }
    }
  }
});