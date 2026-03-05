// d:\Freelance\Python_Dev\Pwa\static\js\theme-toggle.js
// Theme toggle functionality with localStorage persistence
// Handles light/dark mode switching and system preference detection
// RELEVANT FILES: static/css/theme.css, devis_app/templates/base.html

(function() {
    'use strict';

    // Theme management class
    const ThemeManager = {
        STORAGE_KEY: 'theme-preference',
        THEME_DARK: 'dark',
        THEME_LIGHT: 'light',

        // Get current theme from localStorage or system preference
        getPreferredTheme() {
            const storedTheme = localStorage.getItem(this.STORAGE_KEY);
            if (storedTheme) {
                return storedTheme;
            }
            
            // Check system preference
            return window.matchMedia('(prefers-color-scheme: dark)').matches 
                ? this.THEME_DARK 
                : this.THEME_LIGHT;
        },

        // Set theme on document
        setTheme(theme) {
            if (theme === this.THEME_DARK) {
                document.documentElement.setAttribute('data-theme', 'dark');
            } else {
                document.documentElement.setAttribute('data-theme', 'light');
            }
            localStorage.setItem(this.STORAGE_KEY, theme);
            this.updateIcon(theme);
        },

        // Update toggle button icon
        updateIcon(theme) {
            const toggleBtn = document.getElementById('theme-toggle');
            if (!toggleBtn) return;

            const icon = toggleBtn.querySelector('i');
            if (!icon) return;

            if (theme === this.THEME_DARK) {
                icon.className = 'bi bi-sun-fill';
                toggleBtn.setAttribute('aria-label', 'Passer au thème clair');
                toggleBtn.setAttribute('title', 'Thème clair');
            } else {
                icon.className = 'bi bi-moon-fill';
                toggleBtn.setAttribute('aria-label', 'Passer au thème sombre');
                toggleBtn.setAttribute('title', 'Thème sombre');
            }
        },

        // Toggle between themes
        toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme') || this.getPreferredTheme();
            const newTheme = currentTheme === this.THEME_DARK 
                ? this.THEME_LIGHT 
                : this.THEME_DARK;
            this.setTheme(newTheme);
        },

        // Initialize theme on page load
        init() {
            const theme = this.getPreferredTheme();
            this.setTheme(theme);

            // Setup toggle button event listener
            const toggleBtn = document.getElementById('theme-toggle');
            if (toggleBtn) {
                toggleBtn.addEventListener('click', () => this.toggleTheme());
            }

            // Listen for system theme changes
            window.matchMedia('(prefers-color-scheme: dark)')
                .addEventListener('change', (e) => {
                    // Only update if user hasn't set a preference
                    if (!localStorage.getItem(this.STORAGE_KEY)) {
                        this.setTheme(e.matches ? this.THEME_DARK : this.THEME_LIGHT);
                    }
                });
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
    } else {
        ThemeManager.init();
    }

    // Apply theme immediately to avoid flash
    const initialTheme = ThemeManager.getPreferredTheme();
    document.documentElement.setAttribute('data-theme', initialTheme);
})();
