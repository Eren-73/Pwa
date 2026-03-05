// d:\Freelance\Python_Dev\Pwa\static\js\theme.js
// Simple theme toggle manager
// RELEVANT FILES: static/css/theme.css, devis_app/templates/base.html

const ThemeManager = {
    STORAGE_KEY: 'theme-preference',
    THEME_DARK: 'dark',
    THEME_LIGHT: 'light',
    
    getTheme() {
        return localStorage.getItem(this.STORAGE_KEY) || 
            (window.matchMedia('(prefers-color-scheme: dark)').matches ? this.THEME_DARK : this.THEME_LIGHT);
    },
    
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(this.STORAGE_KEY, theme);
        this.updateIcon(theme);
    },
    
    updateIcon(theme) {
        const btn = document.getElementById('theme-toggle');
        const icon = btn?.querySelector('i');
        if (!icon) return;
        
        icon.className = theme === this.THEME_DARK ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
        btn.setAttribute('title', theme === this.THEME_DARK ? 'Thème clair' : 'Thème sombre');
    },
    
    toggle() {
        const current = document.documentElement.getAttribute('data-theme') || this.getTheme();
        const newTheme = current === this.THEME_DARK ? this.THEME_LIGHT : this.THEME_DARK;
        this.setTheme(newTheme);
    },
    
    init() {
        this.setTheme(this.getTheme());
        document.getElementById('theme-toggle')?.addEventListener('click', () => this.toggle());
    }
};

// Init when DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
} else {
    ThemeManager.init();
}
