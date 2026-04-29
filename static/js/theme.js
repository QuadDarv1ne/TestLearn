/**
 * Theme management for TestLearn platform
 * Dark/Light mode switching and theme preferences
 */

const Theme = {
    STORAGE_KEY: 'testlearn_theme',
    DARK: 'dark',
    LIGHT: 'light',

    /**
     * Initialize theme on page load
     */
    init() {
        // Check for saved theme preference or respect OS preference
        const savedTheme = localStorage.getItem(this.STORAGE_KEY);
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme) {
            this.applyTheme(savedTheme);
        } else if (prefersDark) {
            this.applyTheme(this.DARK);
        }
    },

    /**
     * Apply theme to document
     */
    applyTheme(theme) {
        const html = document.documentElement;
        
        if (theme === this.DARK) {
            html.classList.add('dark');
            html.setAttribute('data-theme', 'dark');
        } else {
            html.classList.remove('dark');
            html.setAttribute('data-theme', 'light');
        }

        // Save preference
        localStorage.setItem(this.STORAGE_KEY, theme);
    },

    /**
     * Toggle between dark and light themes
     */
    toggle() {
        const html = document.documentElement;
        const isDark = html.classList.contains('dark');
        const newTheme = isDark ? this.LIGHT : this.DARK;
        this.applyTheme(newTheme);
        return newTheme;
    },

    /**
     * Get current theme
     */
    getCurrent() {
        const html = document.documentElement;
        return html.classList.contains('dark') ? this.DARK : this.LIGHT;
    },

    /**
     * Set specific theme
     */
    set(theme) {
        if (theme === this.DARK || theme === this.LIGHT) {
            this.applyTheme(theme);
        }
    },

    /**
     * Check if current theme is dark
     */
    isDark() {
        return this.getCurrent() === this.DARK;
    }
};

/**
 * Initialize theme toggle button
 */
function initThemeToggle() {
    const toggleButton = document.getElementById('theme-toggle');
    
    if (toggleButton) {
        // Set initial icon based on current theme
        updateThemeIcon(toggleButton);

        toggleButton.addEventListener('click', () => {
            const newTheme = Theme.toggle();
            updateThemeIcon(toggleButton);
            
            // Dispatch custom event for other scripts
            window.dispatchEvent(new CustomEvent('themeChanged', { 
                detail: { theme: newTheme } 
            }));
        });
    }
}

/**
 * Update theme toggle button icon
 */
function updateThemeIcon(button) {
    const isDark = Theme.isDark();
    
    // Remove existing icons
    const existingIcons = button.querySelectorAll('svg');
    existingIcons.forEach(icon => icon.remove());

    // Add appropriate icon
    if (isDark) {
        button.innerHTML = `
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
            </svg>
        `;
        button.title = 'Переключить на светлую тему';
    } else {
        button.innerHTML = `
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
            </svg>
        `;
        button.title = 'Переключить на тёмную тему';
    }
}

/**
 * Watch for OS theme changes
 */
function watchOSThemeChanges() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    mediaQuery.addEventListener('change', (e) => {
        // Only auto-switch if user hasn't set a preference
        if (!localStorage.getItem(Theme.STORAGE_KEY)) {
            Theme.applyTheme(e.matches ? Theme.DARK : Theme.LIGHT);
            const toggleButton = document.getElementById('theme-toggle');
            if (toggleButton) updateThemeIcon(toggleButton);
        }
    });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    Theme.init();
    initThemeToggle();
    watchOSThemeChanges();
});

// Export for use in other scripts
window.Theme = Theme;
