// src/store/settings.store.js
import { defineStore } from 'pinia';
import { api } from '@/plugins';

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    account: {
      fullName: '',
      email: ''
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
      appearance: false,
      notifications: false,
      api: false,
      system: false
    },
    error: null
  }),

  actions: {
    // Load all settings
    async loadSettings() {
      try {
        const response = await api.get('/users/settings');
        const settings = response.data;

        // Apply stored settings if available
        if (settings.account) this.account = { ...this.account, ...settings.account };
        if (settings.appearance) this.appearance = { ...this.appearance, ...settings.appearance };
        if (settings.notifications) this.notifications = { ...this.notifications, ...settings.notifications };
        if (settings.api) this.api = { ...this.api, ...settings.api };
        if (settings.system) this.system = { ...this.system, ...settings.system };

        return settings;
      } catch (error) {
        console.error('Failed to load settings:', error);
        this.error = error.message || 'Failed to load settings';
        throw error;
      }
    },

    // Account settings
    async saveAccountSettings(accountData) {
      this.loading.account = true;

      try {
        const response = await api.put(`/users/account`, accountData);
        this.account = { ...this.account, ...response.data };
        return response.data;
      } catch (error) {
        console.error('Failed to update account settings:', error);
        this.error = error.message || 'Failed to update account settings';
        throw error;
      } finally {
        this.loading.account = false;
      }
    },

    // Appearance settings
    async saveAppearanceSettings() {
      this.loading.appearance = true;

      try {
        await api.post('/users/settings/appearance', this.appearance);
        return this.appearance;
      } catch (error) {
        console.error('Failed to save appearance settings:', error);
        this.error = error.message || 'Failed to save appearance settings';
        throw error;
      } finally {
        this.loading.appearance = false;
      }
    },

    // Notification settings
    async saveNotificationSettings() {
      this.loading.notifications = true;

      try {
        await api.post('/users/settings/notifications', this.notifications);
        return this.notifications;
      } catch (error) {
        console.error('Failed to save notification settings:', error);
        this.error = error.message || 'Failed to save notification settings';
        throw error;
      } finally {
        this.loading.notifications = false;
      }
    },

    // API settings
    async saveApiSettings() {
      this.loading.api = true;

      try {
        await api.post('/users/settings/api', { rateLimit: this.api.rateLimit });
        return this.api;
      } catch (error) {
        console.error('Failed to save API settings:', error);
        this.error = error.message || 'Failed to save API settings';
        throw error;
      } finally {
        this.loading.api = false;
      }
    },

    // System settings
    async saveSystemSettings() {
      this.loading.system = true;

      try {
        await api.post('/system/settings', this.system);
        return this.system;
      } catch (error) {
        console.error('Failed to save system settings:', error);
        this.error = error.message || 'Failed to save system settings';
        throw error;
      } finally {
        this.loading.system = false;
      }
    },

    // API key management
    async loadApiKeys() {
      this.loading.api = true;

      try {
        const response = await api.get('/users/api-keys');
        this.api.keys = response.data.map(key => ({ ...key, visible: false }));
        return this.api.keys;
      } catch (error) {
        console.error('Failed to load API keys:', error);
        this.error = error.message || 'Failed to load API keys';
        throw error;
      } finally {
        this.loading.api = false;
      }
    },

    async generateApiKey(name) {
      this.loading.api = true;

      try {
        const response = await api.post('/users/api-keys', { name });

        // Add to the keys array with visibility flag
        const newKey = { ...response.data, visible: true };
        this.api.keys = [newKey, ...this.api.keys];

        return newKey;
      } catch (error) {
        console.error('Failed to generate API key:', error);
        this.error = error.message || 'Failed to generate API key';
        throw error;
      } finally {
        this.loading.api = false;
      }
    },

    async revokeApiKey(keyId) {
      try {
        await api.delete(`/users/api-keys/${keyId}`);

        // Remove from keys array
        this.api.keys = this.api.keys.filter(key => key.id !== keyId);

        return true;
      } catch (error) {
        console.error('Failed to revoke API key:', error);
        this.error = error.message || 'Failed to revoke API key';
        throw error;
      }
    },

    // Toggle API key visibility
    toggleKeyVisibility(keyId) {
      const keyIndex = this.api.keys.findIndex(key => key.id === keyId);

      if (keyIndex !== -1) {
        this.api.keys[keyIndex].visible = !this.api.keys[keyIndex].visible;
      }
    },

    // Change password
    async changePassword(currentPassword, newPassword) {
      this.loading.account = true;

      try {
        await api.put('/users/password', {
          current_password: currentPassword,
          password: newPassword
        });

        return true;
      } catch (error) {
        console.error('Failed to update password:', error);
        this.error = error.message || 'Failed to update password';
        throw error;
      } finally {
        this.loading.account = false;
      }
    }
  }
});