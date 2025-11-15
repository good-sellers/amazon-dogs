/**
 * i18n Internationalization Library
 * Handles language switching and text translation
 */

class I18nManager {
  constructor() {
    this.currentLanguage = 'en';
    this.translations = {};
    this.observers = [];
  }

  /**
   * Initialize i18n manager
   * @param {string} defaultLanguage - Default language code
   */
  async init(defaultLanguage = 'en') {
    try {
      // Get saved language from storage
      const result = await chrome.storage.sync.get(['language']);
      this.currentLanguage = result.language || defaultLanguage;

      // Load translations
      await this.loadTranslations(this.currentLanguage);

      // Observe DOM changes for dynamic content
      this.observeDOM();

      return this.currentLanguage;
    } catch (error) {
      console.error('Error initializing i18n:', error);
      this.currentLanguage = defaultLanguage;
      return this.currentLanguage;
    }
  }

  /**
   * Load translations for a specific language
   * @param {string} language - Language code (e.g., 'en', 'zh_CN')
   */
  async loadTranslations(language) {
    try {
      // Get messages from Chrome's i18n API
      const messages = await chrome.i18n.getAcceptLanguages();

      // Try to get translation from messages.json
      const translation = await this.getTranslationFromFile(language);
      this.translations = translation;
      this.currentLanguage = language;
    } catch (error) {
      console.error('Error loading translations:', error);
    }
  }

  /**
   * Get translation from file (for options page)
   * @param {string} language - Language code
   */
  async getTranslationFromFile(language) {
    try {
      const response = await fetch(`./_locales/${language}/messages.json`);
      if (!response.ok) {
        throw new Error(`Failed to load translations for ${language}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching translation file:', error);
      return {};
    }
  }

  /**
   * Translate a key to current language
   * @param {string} key - Translation key
   * @param {Object} substitutions - Substitutions for placeholders
   * @returns {string} Translated text
   */
  t(key, substitutions = {}) {
    let message = this.translations[key] || key;

    // Handle message object (from Chrome i18n API)
    if (typeof message === 'object' && message.message) {
      message = message.message;
    }

    // Handle substitutions
    Object.keys(substitutions).forEach(placeholder => {
      const regex = new RegExp(`\\$${placeholder}\\$`, 'g');
      message = message.replace(regex, substitutions[placeholder]);
    });

    return message;
  }

  /**
   * Change current language
   * @param {string} language - New language code
   */
  async changeLanguage(language) {
    try {
      // Save to storage
      await chrome.storage.sync.set({ language });

      // Load new translations
      await this.loadTranslations(language);

      // Update all observers
      this.notifyObservers();

      // Trigger custom event for components to update
      window.dispatchEvent(new CustomEvent('languageChanged', {
        detail: { language: this.currentLanguage }
      }));

      return this.currentLanguage;
    } catch (error) {
      console.error('Error changing language:', error);
      throw error;
    }
  }

  /**
   * Get current language
   * @returns {string} Current language code
   */
  getCurrentLanguage() {
    return this.currentLanguage;
  }

  /**
   * Add observer for language changes
   * @param {Function} callback - Callback function
   */
  addObserver(callback) {
    this.observers.push(callback);
  }

  /**
   * Remove observer
   * @param {Function} callback - Callback function to remove
   */
  removeObserver(callback) {
    this.observers = this.observers.filter(obs => obs !== callback);
  }

  /**
   * Notify all observers of language change
   */
  notifyObservers() {
    this.observers.forEach(callback => {
      try {
        callback(this.currentLanguage);
      } catch (error) {
        console.error('Error in i18n observer:', error);
      }
    });
  }

  /**
   * Observe DOM for data-i18n attributes
   */
  observeDOM() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            this.updateElementTranslations(node);
          }
        });
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  /**
   * Update translations for a specific element
   * @param {Element} element - Element to update
   */
  updateElementTranslations(element) {
    // Check the element itself
    if (element.hasAttribute && element.hasAttribute('data-i18n')) {
      const key = element.getAttribute('data-i18n');
      const translation = this.t(key);
      this.applyTranslation(element, translation);
    }

    // Check all descendants
    const elements = element.querySelectorAll('[data-i18n]');
    elements.forEach((el) => {
      const key = el.getAttribute('data-i18n');
      const translation = this.t(key);
      this.applyTranslation(el, translation);
    });
  }

  /**
   * Apply translation to element
   * @param {Element} element - Target element
   * @param {string} text - Translated text
   */
  applyTranslation(element, text) {
    if (element.hasAttribute('data-i18n-attr')) {
      const attr = element.getAttribute('data-i18n-attr');
      element.setAttribute(attr, text);
    } else {
      element.textContent = text;
    }
  }

  /**
   * Initialize all elements with translations
   */
  initTranslations() {
    this.updateElementTranslations(document.body);
  }

  /**
   * Get available languages
   * @returns {Array} List of available languages
   */
  getAvailableLanguages() {
    return [
      { code: 'en', name: 'English' },
      { code: 'zh_CN', name: '简体中文' }
    ];
  }
}

// Create global instance
window.i18n = new I18nManager();
