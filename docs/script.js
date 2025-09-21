// Retro Games Database - Interactive Features
class GamesDatabase {
    constructor() {
        this.games = [];
        this.filteredGames = [];
        this.currentConsole = 'all';
        this.searchTerm = '';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadGames();
        this.animateProgressBars();
        this.setupLazyLoading();
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('gameSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value.toLowerCase();
                this.filterGames();
            });
        }

        // Console filter
        const consoleFilter = document.getElementById('consoleFilter');
        if (consoleFilter) {
            consoleFilter.addEventListener('change', (e) => {
                this.currentConsole = e.target.value;
                this.filterGames();
            });
        }

        // Sort options
        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                this.sortGames(e.target.value);
            });
        }

        // Smooth scrolling for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    loadGames() {
        // Games are embedded in HTML by Python script
        const gameElements = document.querySelectorAll('.game-card');
        this.games = Array.from(gameElements).map(el => ({
            element: el,
            title: el.dataset.title?.toLowerCase() || '',
            developer: el.dataset.developer?.toLowerCase() || '',
            publisher: el.dataset.publisher?.toLowerCase() || '',
            console: el.dataset.console?.toLowerCase() || '',
            year: el.dataset.year || '',
            releaseDate: el.dataset.releaseDate || ''
        }));
        this.filteredGames = [...this.games];
        this.updateResultsCount();
    }

    filterGames() {
        this.filteredGames = this.games.filter(game => {
            const matchesSearch = !this.searchTerm || 
                game.title.includes(this.searchTerm) ||
                game.developer.includes(this.searchTerm) ||
                game.publisher.includes(this.searchTerm);
            
            const matchesConsole = this.currentConsole === 'all' || 
                game.console === this.currentConsole;

            return matchesSearch && matchesConsole;
        });

        this.displayGames();
        this.updateResultsCount();
    }

    displayGames() {
        this.games.forEach(game => {
            const isVisible = this.filteredGames.includes(game);
            game.element.style.display = isVisible ? 'block' : 'none';
            
            if (isVisible) {
                game.element.classList.add('fade-in');
            }
        });
    }

    sortGames(sortBy) {
        const gamesContainer = document.querySelector('.games-grid');
        if (!gamesContainer) return;

        const sortedElements = this.filteredGames.map(game => game.element).sort((a, b) => {
            switch (sortBy) {
                case 'title':
                    return a.dataset.title.localeCompare(b.dataset.title);
                case 'developer':
                    return a.dataset.developer.localeCompare(b.dataset.developer);
                case 'publisher':
                    return a.dataset.publisher.localeCompare(b.dataset.publisher);
                case 'year':
                    return new Date(a.dataset.releaseDate) - new Date(b.dataset.releaseDate);
                case 'year-desc':
                    return new Date(b.dataset.releaseDate) - new Date(a.dataset.releaseDate);
                default:
                    return 0;
            }
        });

        // Re-append elements in sorted order
        sortedElements.forEach(element => {
            gamesContainer.appendChild(element);
        });
    }

    updateResultsCount() {
        const counter = document.getElementById('resultsCount');
        if (counter) {
            const count = this.filteredGames.length;
            const total = this.games.length;
            counter.textContent = `Showing ${count.toLocaleString()} of ${total.toLocaleString()} games`;
        }
    }

    animateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-fill');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const bar = entry.target;
                    const percentage = bar.dataset.percentage;
                    
                    // Animate from 0 to target percentage
                    let current = 0;
                    const increment = percentage / 50; // 50 frames
                    
                    const animate = () => {
                        current += increment;
                        if (current <= percentage) {
                            bar.style.width = current + '%';
                            requestAnimationFrame(animate);
                        } else {
                            bar.style.width = percentage + '%';
                        }
                    };
                    
                    setTimeout(animate, 200); // Delay for stagger effect
                    observer.unobserve(bar);
                }
            });
        }, { threshold: 0.1 });

        progressBars.forEach(bar => observer.observe(bar));
    }

    setupLazyLoading() {
        // Lazy load game cards for performance
        const gameCards = document.querySelectorAll('.game-card');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        gameCards.forEach(card => observer.observe(card));
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.gamesDB = new GamesDatabase();
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'f':
                case 'F':
                    e.preventDefault();
                    document.getElementById('gameSearch')?.focus();
                    break;
            }
        }
    });
});