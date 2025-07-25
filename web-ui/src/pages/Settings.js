import React, { useState, useEffect } from 'react';
import { 
  CogIcon, 
  BellIcon, 
  ShieldCheckIcon,
  ServerIcon,
  UserIcon,
  KeyIcon,
  CloudIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({
    general: {
      siteName: 'FairClaimRCM',
      language: 'en',
      timezone: 'UTC-05:00',
      dateFormat: 'MM/DD/YYYY'
    },
    notifications: {
      emailNotifications: true,
      claimAlerts: true,
      systemUpdates: false,
      auditReminders: true
    },
    security: {
      twoFactorAuth: false,
      sessionTimeout: 60,
      passwordExpiry: 90,
      loginAttempts: 5
    },
    api: {
      rateLimit: 1000,
      timeout: 30,
      retryAttempts: 3,
      cacheTTL: 300
    }
  });

  const tabs = [
    { id: 'general', name: 'General', icon: CogIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
    { id: 'security', name: 'Security', icon: ShieldCheckIcon },
    { id: 'database', name: 'Database', icon: ServerIcon },
    { id: 'api', name: 'API', icon: CloudIcon },
    { id: 'audit', name: 'Audit', icon: DocumentTextIcon }
  ];

  const handleSettingChange = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  const handleSave = () => {
    // In a real app, this would save to the backend
    console.log('Saving settings:', settings);
    alert('Settings saved successfully!');
  };

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Site Name
        </label>
        <input
          type="text"
          value={settings.general.siteName}
          onChange={(e) => handleSettingChange('general', 'siteName', e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Language
        </label>
        <select
          value={settings.general.language}
          onChange={(e) => handleSettingChange('general', 'language', e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
        </select>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Timezone
        </label>
        <select
          value={settings.general.timezone}
          onChange={(e) => handleSettingChange('general', 'timezone', e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="UTC-05:00">Eastern Time (UTC-05:00)</option>
          <option value="UTC-06:00">Central Time (UTC-06:00)</option>
          <option value="UTC-07:00">Mountain Time (UTC-07:00)</option>
          <option value="UTC-08:00">Pacific Time (UTC-08:00)</option>
        </select>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Date Format
        </label>
        <select
          value={settings.general.dateFormat}
          onChange={(e) => handleSettingChange('general', 'dateFormat', e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="MM/DD/YYYY">MM/DD/YYYY</option>
          <option value="DD/MM/YYYY">DD/MM/YYYY</option>
          <option value="YYYY-MM-DD">YYYY-MM-DD</option>
        </select>
      </div>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-gray-900">Email Notifications</h3>
          <p className="text-sm text-gray-500">Receive notifications via email</p>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={settings.notifications.emailNotifications}
            onChange={(e) => handleSettingChange('notifications', 'emailNotifications', e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
        </label>
      </div>
      
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-gray-900">Claim Alerts</h3>
          <p className="text-sm text-gray-500">Get notified about claim status changes</p>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={settings.notifications.claimAlerts}
            onChange={(e) => handleSettingChange('notifications', 'claimAlerts', e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
        </label>
      </div>
      
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-gray-900">System Updates</h3>
          <p className="text-sm text-gray-500">Notifications about system updates and maintenance</p>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={settings.notifications.systemUpdates}
            onChange={(e) => handleSettingChange('notifications', 'systemUpdates', e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
        </label>
      </div>
      
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-gray-900">Audit Reminders</h3>
          <p className="text-sm text-gray-500">Reminders for scheduled audits and reviews</p>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={settings.notifications.auditReminders}
            onChange={(e) => handleSettingChange('notifications', 'auditReminders', e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
        </label>
      </div>
    </div>
  );

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-gray-900">Two-Factor Authentication</h3>
          <p className="text-sm text-gray-500">Add an extra layer of security to your account</p>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={settings.security.twoFactorAuth}
            onChange={(e) => handleSettingChange('security', 'twoFactorAuth', e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
        </label>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Session Timeout (minutes)
        </label>
        <input
          type="number"
          value={settings.security.sessionTimeout}
          onChange={(e) => handleSettingChange('security', 'sessionTimeout', parseInt(e.target.value))}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          min="15"
          max="480"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Password Expiry (days)
        </label>
        <input
          type="number"
          value={settings.security.passwordExpiry}
          onChange={(e) => handleSettingChange('security', 'passwordExpiry', parseInt(e.target.value))}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          min="30"
          max="365"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Maximum Login Attempts
        </label>
        <input
          type="number"
          value={settings.security.loginAttempts}
          onChange={(e) => handleSettingChange('security', 'loginAttempts', parseInt(e.target.value))}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          min="3"
          max="10"
        />
      </div>
    </div>
  );

  const renderApiSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Rate Limit (requests per minute)
        </label>
        <input
          type="number"
          value={settings.api.rateLimit}
          onChange={(e) => handleSettingChange('api', 'rateLimit', parseInt(e.target.value))}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          min="100"
          max="10000"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Request Timeout (seconds)
        </label>
        <input
          type="number"
          value={settings.api.timeout}
          onChange={(e) => handleSettingChange('api', 'timeout', parseInt(e.target.value))}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          min="5"
          max="300"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Retry Attempts
        </label>
        <input
          type="number"
          value={settings.api.retryAttempts}
          onChange={(e) => handleSettingChange('api', 'retryAttempts', parseInt(e.target.value))}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          min="1"
          max="10"
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Cache TTL (seconds)
        </label>
        <input
          type="number"
          value={settings.api.cacheTTL}
          onChange={(e) => handleSettingChange('api', 'cacheTTL', parseInt(e.target.value))}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          min="60"
          max="3600"
        />
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
        return renderGeneralSettings();
      case 'notifications':
        return renderNotificationSettings();
      case 'security':
        return renderSecuritySettings();
      case 'api':
        return renderApiSettings();
      case 'database':
        return (
          <div className="text-center py-8">
            <ServerIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Database settings coming soon...</p>
          </div>
        );
      case 'audit':
        return (
          <div className="text-center py-8">
            <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Audit settings coming soon...</p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Manage your application preferences and configuration</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar Navigation */}
        <div className="lg:w-64">
          <nav className="bg-white rounded-lg shadow">
            <div className="p-4">
              <ul className="space-y-1">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <li key={tab.id}>
                      <button
                        onClick={() => setActiveTab(tab.id)}
                        className={`w-full flex items-center gap-3 px-3 py-2 text-left rounded-lg transition-colors ${
                          activeTab === tab.id
                            ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                            : 'text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        <Icon className="h-5 w-5" />
                        {tab.name}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1">
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                {tabs.find(tab => tab.id === activeTab)?.name} Settings
              </h2>
            </div>
            
            <div className="p-6">
              {renderTabContent()}
            </div>
            
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 rounded-b-lg">
              <div className="flex justify-end gap-3">
                <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                  Reset
                </button>
                <button 
                  onClick={handleSave}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
