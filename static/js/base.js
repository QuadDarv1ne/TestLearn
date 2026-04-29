/**
 * Base JavaScript utilities for TestLearn platform
 * Common functionality used across all pages
 */

// Toast notification system
const Toast = {
    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white transform transition-all duration-300 z-50 ${
            type === 'success' ? 'bg-green-500' :
            type === 'error' ? 'bg-red-500' :
            type === 'warning' ? 'bg-yellow-500' :
            'bg-blue-500'
        }`;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-20px)';
        }, duration - 300);

        setTimeout(() => {
            toast.remove();
        }, duration);
    },

    success(message) {
        this.show(message, 'success');
    },

    error(message) {
        this.show(message, 'error');
    },

    warning(message) {
        this.show(message, 'warning');
    },

    info(message) {
        this.show(message, 'info');
    }
};

// Loading spinner
const Loading = {
    show(container = document.body) {
        const overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        overlay.innerHTML = `
            <div class="bg-white rounded-lg p-8 flex flex-col items-center">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <p class="mt-4 text-gray-700">Загрузка...</p>
            </div>
        `;
        container.appendChild(overlay);
    },

    hide() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
};

// LocalStorage helper
const Storage = {
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            return defaultValue;
        }
    },

    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('LocalStorage error:', e);
        }
    },

    remove(key) {
        localStorage.removeItem(key);
    },

    clear() {
        localStorage.clear();
    }
};

// API helper
const API = {
    async request(url, options = {}) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Request failed' }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request error:', error);
            throw error;
        }
    },

    get(url) {
        return this.request(url);
    },

    post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    delete(url) {
        return this.request(url, {
            method: 'DELETE'
        });
    }
};

// Mobile menu toggle
function initMobileMenu() {
    const menuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!menuButton.contains(e.target) && !mobileMenu.contains(e.target)) {
                mobileMenu.classList.add('hidden');
            }
        });
    }
}

// Search functionality
function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    if (searchInput && searchResults) {
        let debounceTimer;

        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            const query = e.target.value.trim();

            if (query.length < 2) {
                searchResults.classList.add('hidden');
                return;
            }

            debounceTimer = setTimeout(() => {
                performSearch(query);
            }, 300);
        });
    }
}

async function performSearch(query) {
    const searchResults = document.getElementById('search-results');
    if (!searchResults) return;

    try {
        const results = await API.get(`/api/search?q=${encodeURIComponent(query)}`);
        
        if (results.topics.length === 0 && results.glossary_terms.length === 0) {
            searchResults.innerHTML = '<p class="p-4 text-gray-500">Ничего не найдено</p>';
        } else {
            let html = '';
            
            if (results.topics.length > 0) {
                html += '<div class="p-2 bg-gray-50 font-semibold">Темы</div>';
                results.topics.forEach(topic => {
                    html += `
                        <a href="/topic/${topic.id}" class="block p-3 hover:bg-gray-50 border-b">
                            <div class="font-medium text-blue-600">${escapeHtml(topic.title)}</div>
                            <div class="text-sm text-gray-600">${escapeHtml(topic.snippet)}</div>
                            <div class="text-xs text-gray-400 mt-1">${escapeHtml(topic.category)}</div>
                        </a>
                    `;
                });
            }

            if (results.glossary_terms.length > 0) {
                html += '<div class="p-2 bg-gray-50 font-semibold">Глоссарий</div>';
                results.glossary_terms.forEach(term => {
                    html += `
                        <div class="block p-3 hover:bg-gray-50 border-b">
                            <div class="font-medium text-green-600">${escapeHtml(term.term)}</div>
                            <div class="text-sm text-gray-600">${escapeHtml(term.definition)}</div>
                        </div>
                    `;
                });
            }

            searchResults.innerHTML = html;
        }

        searchResults.classList.remove('hidden');
    } catch (error) {
        console.error('Search error:', error);
        searchResults.innerHTML = '<p class="p-4 text-red-500">Ошибка поиска</p>';
        searchResults.classList.remove('hidden');
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Confirm dialog
function confirm(message, callback) {
    if (window.confirm(message)) {
        callback();
    }
}

// Copy to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        Toast.success('Скопировано в буфер обмена');
    } catch (error) {
        Toast.error('Не удалось скопировать');
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    initMobileMenu();
    initSearch();
});

// Export for use in other scripts
window.Toast = Toast;
window.Loading = Loading;
window.Storage = Storage;
window.API = API;
window.copyToClipboard = copyToClipboard;
window.confirm = confirm;
window.escapeHtml = escapeHtml;
