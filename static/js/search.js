/**
 * Advanced search functionality for TestLearn platform
 * Full-text search with filtering and highlighting
 */

const Search = {
    debounceTimer: null,
    minQueryLength: 2,
    maxResults: 20,
    currentResults: null,

    /**
     * Initialize search functionality
     */
    init() {
        const searchInput = document.getElementById('search-input');
        const searchForm = document.getElementById('search-form');
        
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.onInput(e));
            searchInput.addEventListener('focus', () => this.showRecentSearches());
        }

        if (searchForm) {
            searchForm.addEventListener('submit', (e) => this.onSubmit(e));
        }

        // Close search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                this.hideResults();
            }
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideResults();
            }
        });
    },

    /**
     * Handle input event with debounce
     */
    onInput(e) {
        const query = e.target.value.trim();
        
        clearTimeout(this.debounceTimer);

        if (query.length < this.minQueryLength) {
            this.hideResults();
            return;
        }

        this.debounceTimer = setTimeout(() => {
            this.search(query);
        }, 300);
    },

    /**
     * Handle form submission
     */
    onSubmit(e) {
        e.preventDefault();
        const searchInput = document.getElementById('search-input');
        const query = searchInput.value.trim();
        
        if (query.length >= this.minQueryLength) {
            this.performSearch(query, true);
        }
    },

    /**
     * Perform search and display results
     */
    async search(query) {
        try {
            const results = await API.get(`/api/search?q=${encodeURIComponent(query)}`);
            this.currentResults = results;
            this.displayResults(results, query);
            this.saveRecentSearch(query);
        } catch (error) {
            console.error('Search error:', error);
            this.displayError('Ошибка при поиске');
        }
    },

    /**
     * Perform search and redirect to results page
     */
    async performSearch(query, openInNewPage = false) {
        const url = `/theory?search=${encodeURIComponent(query)}`;
        
        if (openInNewPage) {
            window.location.href = url;
        } else {
            window.location.href = url;
        }
    },

    /**
     * Display search results in dropdown
     */
    displayResults(results, query) {
        let container = document.getElementById('search-results');
        
        if (!container) {
            container = document.createElement('div');
            container.id = 'search-results';
            container.className = 'search-results-container';
            
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.parentElement.appendChild(container);
            }
        }

        if (results.topics.length === 0 && results.glossary_terms.length === 0) {
            container.innerHTML = `
                <div class="p-4 text-center text-gray-500">
                    <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                    </svg>
                    <p>Ничего не найдено</p>
                    <p class="text-sm mt-1">Попробуйте изменить запрос</p>
                </div>
            `;
        } else {
            let html = '';

            // Topics section
            if (results.topics.length > 0) {
                html += `
                    <div class="search-section">
                        <div class="search-section-header">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                            </svg>
                            <span>Темы (${results.topics.length})</span>
                        </div>
                        ${results.topics.slice(0, 5).map(topic => this.renderTopicResult(topic, query)).join('')}
                    </div>
                `;
            }

            // Glossary section
            if (results.glossary_terms.length > 0) {
                html += `
                    <div class="search-section">
                        <div class="search-section-header">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
                            </svg>
                            <span>Глоссарий (${results.glossary_terms.length})</span>
                        </div>
                        ${results.glossary_terms.slice(0, 5).map(term => this.renderGlossaryResult(term, query)).join('')}
                    </div>
                `;
            }

            // View all link
            const totalResults = results.topics.length + results.glossary_terms.length;
            if (totalResults > 5) {
                html += `
                    <div class="search-footer">
                        <a href="/theory?search=${encodeURIComponent(query)}" class="text-blue-600 hover:text-blue-800 text-sm">
                            Показать все ${totalResults} результатов →
                        </a>
                    </div>
                `;
            }

            container.innerHTML = html;
        }

        container.classList.remove('hidden');
    },

    /**
     * Render individual topic result
     */
    renderTopicResult(topic, query) {
        const highlightedTitle = this.highlightText(topic.title, query);
        const highlightedSnippet = this.highlightText(this.truncate(topic.snippet, 150), query);

        return `
            <a href="/topic/${topic.id}" class="search-result-item">
                <div class="font-medium text-blue-600">${highlightedTitle}</div>
                <div class="text-sm text-gray-600">${highlightedSnippet}</div>
                <div class="text-xs text-gray-400 mt-1">${this.escapeHtml(topic.category)}</div>
            </a>
        `;
    },

    /**
     * Render individual glossary result
     */
    renderGlossaryResult(term, query) {
        const highlightedTerm = this.highlightText(term.term, query);
        const highlightedDef = this.highlightText(this.truncate(term.definition, 100), query);

        return `
            <div class="search-result-item">
                <div class="font-medium text-green-600">${highlightedTerm}</div>
                <div class="text-sm text-gray-600">${highlightedDef}</div>
            </div>
        `;
    },

    /**
     * Display error message
     */
    displayError(message) {
        let container = document.getElementById('search-results');
        if (!container) {
            container = document.createElement('div');
            container.id = 'search-results';
            container.className = 'search-results-container';
            
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.parentElement.appendChild(container);
            }
        }

        container.innerHTML = `
            <div class="p-4 text-center text-red-500">
                <p>${message}</p>
            </div>
        `;
        container.classList.remove('hidden');
    },

    /**
     * Hide search results
     */
    hideResults() {
        const container = document.getElementById('search-results');
        if (container) {
            container.classList.add('hidden');
        }
    },

    /**
     * Show recent searches
     */
    showRecentSearches() {
        const recent = Storage.get('recent_searches', []);
        
        if (recent.length === 0) return;

        let container = document.getElementById('search-results');
        if (!container) {
            container = document.createElement('div');
            container.id = 'search-results';
            container.className = 'search-results-container';
            
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.parentElement.appendChild(container);
            }
        }

        const html = `
            <div class="search-section">
                <div class="search-section-header">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span>Недавние поиски</span>
                </div>
                ${recent.map(query => `
                    <button onclick="Search.search('${this.escapeHtml(query)}')" class="search-result-item text-left">
                        <div class="font-medium text-gray-700">${this.escapeHtml(query)}</div>
                    </button>
                `).join('')}
                <div class="search-footer">
                    <button onclick="Search.clearRecentSearches()" class="text-red-600 hover:text-red-800 text-sm">
                        Очистить историю
                    </button>
                </div>
            </div>
        `;

        container.innerHTML = html;
        container.classList.remove('hidden');
    },

    /**
     * Save search to recent searches
     */
    saveRecentSearch(query) {
        let recent = Storage.get('recent_searches', []);
        
        // Remove if already exists
        recent = recent.filter(q => q !== query);
        
        // Add to beginning
        recent.unshift(query);
        
        // Limit to 10
        recent = recent.slice(0, 10);
        
        Storage.set('recent_searches', recent);
    },

    /**
     * Clear recent searches
     */
    clearRecentSearches() {
        Storage.remove('recent_searches');
        this.hideResults();
    },

    /**
     * Highlight search query in text
     */
    highlightText(text, query) {
        if (!query || !text) return this.escapeHtml(text);
        
        const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
        const highlighted = text.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
        return this.escapeHtml(highlighted);
    },

    /**
     * Truncate text with ellipsis
     */
    truncate(text, length) {
        if (!text || text.length <= length) return text;
        return text.substring(0, length) + '...';
    },

    /**
     * Escape regex special characters
     */
    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    },

    /**
     * Escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    Search.init();
});

// Export for use in other scripts
window.Search = Search;
