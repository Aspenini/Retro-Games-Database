#!/usr/bin/env python3
"""
Gaming Database Progress Tracker & Site Generator
Analyzes completion progress across all dead gaming consoles
and generates a beautiful static website
"""

import json
import os
from typing import Dict, List, Tuple
from datetime import datetime
import shutil

class ProgressTracker:
    def __init__(self):
        self.dead_consoles = self.load_dead_consoles()
        self.console_databases = self.find_console_databases()
        
    def load_dead_consoles(self) -> Dict:
        """Load the dead consoles database"""
        try:
            with open('dead_consoles.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ dead_consoles.json not found!")
            return {}
    
    def find_console_databases(self) -> Dict[str, Dict]:
        """Find all existing console game databases"""
        databases = {}
        
        # Look for JSON files that match console patterns
        for filename in os.listdir('.'):
            if filename.endswith('_games.json') and filename != 'dead_consoles.json':
                console_name = filename.replace('_games.json', '').replace('_', ' ').title()
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'games' in data:
                            databases[console_name] = {
                                'filename': filename,
                                'data': data,
                                'game_count': len(data['games']),
                                'last_updated': data.get('last_updated', 'Unknown')
                            }
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"⚠️  Error reading {filename}: {e}")
        
        return databases
    
    def get_console_info(self, console_name: str) -> Dict:
        """Get console info from dead consoles database"""
        for console in self.dead_consoles.get('consoles', []):
            if console_name.lower() in console['console'].lower():
                return console
        return {}
    
    def calculate_progress(self) -> List[Dict]:
        """Calculate progress for each console"""
        progress_data = []
        
        for db_name, db_info in self.console_databases.items():
            # Try to match with dead consoles database
            console_info = self.get_console_info(db_name)
            
            if console_info:
                total_games = console_info['total_official_games']
                current_games = db_info['game_count']
                percentage = (current_games / total_games) * 100 if total_games > 0 else 0
                
                progress_data.append({
                    'console': console_info['console'],
                    'manufacturer': console_info['manufacturer'],
                    'generation': console_info['generation'],
                    'release_year': console_info['release_year'],
                    'discontinuation_year': console_info['discontinuation_year'],
                    'total_official_games': total_games,
                    'current_games': current_games,
                    'percentage_complete': round(percentage, 2),
                    'filename': db_info['filename'],
                    'last_updated': db_info['last_updated'],
                    'status': self.get_status(percentage)
                })
        
        return sorted(progress_data, key=lambda x: x['percentage_complete'], reverse=True)
    
    def get_status(self, percentage: float) -> str:
        """Get status emoji based on completion percentage"""
        if percentage >= 100:
            return "✅ Complete"
        elif percentage >= 75:
            return "🟢 Nearly Done"
        elif percentage >= 50:
            return "🟡 In Progress"
        elif percentage >= 25:
            return "🟠 Started"
        elif percentage > 0:
            return "🔴 Minimal"
        else:
            return "⚫ Not Started"
    
    def print_summary(self):
        """Print overall summary"""
        progress_data = self.calculate_progress()
        total_consoles = len(self.dead_consoles.get('consoles', []))
        databases_created = len(progress_data)
        
        print("🎮 GAMING DATABASE PROGRESS TRACKER")
        print("=" * 50)
        print(f"📊 Total Dead Consoles: {total_consoles}")
        print(f"🗃️  Databases Created: {databases_created}")
        print(f"📈 Coverage: {round((databases_created/total_consoles)*100, 1)}% of consoles")
        print()
        
        if progress_data:
            total_games_target = sum(p['total_official_games'] for p in progress_data)
            total_games_current = sum(p['current_games'] for p in progress_data)
            overall_percentage = (total_games_current / total_games_target) * 100 if total_games_target > 0 else 0
            
            print(f"🎯 Overall Game Progress: {total_games_current:,} / {total_games_target:,} games ({overall_percentage:.1f}%)")
            print()
    
    def print_detailed_progress(self):
        """Print detailed progress for each console"""
        progress_data = self.calculate_progress()
        
        if not progress_data:
            print("❌ No console databases found!")
            return
        
        print("📋 DETAILED PROGRESS BY CONSOLE")
        print("=" * 80)
        
        for console in progress_data:
            print(f"\n🎮 {console['console']}")
            print(f"   Manufacturer: {console['manufacturer']}")
            print(f"   Generation: {console['generation']} ({console['release_year']}-{console['discontinuation_year']})")
            print(f"   Progress: {console['current_games']:,} / {console['total_official_games']:,} games ({console['percentage_complete']}%)")
            print(f"   Status: {console['status']}")
            print(f"   File: {console['filename']}")
            print(f"   Last Updated: {console['last_updated']}")
            
            # Progress bar
            bar_length = 30
            filled_length = int(bar_length * console['percentage_complete'] / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            print(f"   [{bar}] {console['percentage_complete']}%")
    
    def print_missing_consoles(self):
        """Print consoles that don't have databases yet"""
        existing_consoles = set()
        for db_name in self.console_databases.keys():
            for console in self.dead_consoles.get('consoles', []):
                if db_name.lower() in console['console'].lower():
                    existing_consoles.add(console['console'])
        
        missing_consoles = []
        for console in self.dead_consoles.get('consoles', []):
            if console['console'] not in existing_consoles:
                missing_consoles.append(console)
        
        if missing_consoles:
            print("\n🔍 MISSING CONSOLE DATABASES")
            print("=" * 50)
            
            # Sort by total games (most games first)
            missing_consoles.sort(key=lambda x: x['total_official_games'], reverse=True)
            
            for console in missing_consoles:
                print(f"⚫ {console['console']} ({console['manufacturer']})")
                print(f"   {console['total_official_games']:,} games | Gen {console['generation']} | {console['release_year']}-{console['discontinuation_year']}")
    
    def generate_report(self):
        """Generate complete progress report"""
        print()
        self.print_summary()
        self.print_detailed_progress()
        self.print_missing_consoles()
        
        print(f"\n📅 Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🚀 Keep up the great work building this open source gaming database!")
    
    def ensure_site_assets(self):
        """Ensure CSS and JS files exist in docs folder, create if missing"""
        site_dir = 'docs'
        if not os.path.exists(site_dir):
            os.makedirs(site_dir)
            print(f"📁 Created {site_dir} directory")
        
        # Create CSS file if missing
        css_path = os.path.join(site_dir, 'style.css')
        if not os.path.exists(css_path):
            print("🎨 Generating style.css...")
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(self.get_css_content())
        
        # Create JS file if missing
        js_path = os.path.join(site_dir, 'script.js')
        if not os.path.exists(js_path):
            print("⚡ Generating script.js...")
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(self.get_js_content())
    
    def get_css_content(self):
        """Return the complete CSS content"""
        return '''/* Retro Games Database - Modern Design */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    --primary-color: #2563eb;
    --secondary-color: #7c3aed;
    --accent-color: #f59e0b;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --bg-color: #0f172a;
    --card-bg: #1e293b;
    --text-primary: #f8fafc;
    --text-secondary: #cbd5e1;
    --border-color: #334155;
    --gradient: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-color);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
}

/* Header */
.header {
    text-align: center;
    margin-bottom: 3rem;
    padding: 2rem 0;
    background: var(--gradient);
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(37, 99, 235, 0.3);
}

.header h1 {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    background: linear-gradient(45deg, #fff, #e2e8f0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.header p {
    font-size: 1.2rem;
    opacity: 0.9;
    margin-bottom: 1rem;
}

.last-updated {
    font-size: 0.9rem;
    opacity: 0.8;
    background: rgba(255, 255, 255, 0.1);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    display: inline-block;
}

/* Stats Grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 3rem;
}

.stat-card {
    background: var(--card-bg);
    padding: 2rem;
    border-radius: 15px;
    border: 1px solid var(--border-color);
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.stat-number {
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
}

.stat-label {
    color: var(--text-secondary);
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Console Cards */
.console-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
    margin-bottom: 3rem;
}

.console-card {
    background: var(--card-bg);
    border-radius: 15px;
    border: 1px solid var(--border-color);
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.console-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
}

.console-header {
    padding: 1.5rem;
    background: var(--gradient);
    position: relative;
}

.console-name {
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.console-meta {
    font-size: 0.9rem;
    opacity: 0.9;
}

.console-body {
    padding: 1.5rem;
}

.progress-section {
    margin-bottom: 1.5rem;
}

.progress-bar {
    width: 100%;
    height: 12px;
    background: #374151;
    border-radius: 6px;
    overflow: hidden;
    margin: 0.5rem 0;
}

.progress-fill {
    height: 100%;
    background: var(--gradient);
    border-radius: 6px;
    transition: width 0.8s ease;
    position: relative;
}

.progress-fill::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.progress-text {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 0.5rem;
}

.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}

.status-complete { background: var(--success-color); color: white; }
.status-nearly { background: var(--warning-color); color: white; }
.status-progress { background: var(--primary-color); color: white; }
.status-started { background: var(--danger-color); color: white; }
.status-minimal { background: #6b7280; color: white; }
.status-none { background: #374151; color: white; }

/* Games Section */
.games-section {
    margin-top: 3rem;
}

.section-title {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    text-align: center;
}

.search-controls {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
    justify-content: center;
}

.search-input {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 0.75rem 1rem;
    border-radius: 10px;
    font-size: 1rem;
    min-width: 300px;
}

.search-input:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.filter-select {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 0.75rem 1rem;
    border-radius: 10px;
    font-size: 1rem;
}

/* Games Grid */
.games-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
    margin-top: 2rem;
}

.game-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 1rem;
    transition: all 0.3s ease;
}

.game-card:hover {
    border-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
}

.game-title {
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--text-primary);
}

.game-meta {
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.4;
}

.game-meta strong {
    color: var(--text-primary);
}

/* Missing Consoles */
.missing-consoles {
    background: var(--card-bg);
    border-radius: 15px;
    border: 1px solid var(--border-color);
    padding: 2rem;
    margin-top: 3rem;
}

.missing-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.missing-item {
    padding: 1rem;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 8px;
}

.missing-name {
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.missing-info {
    font-size: 0.85rem;
    color: var(--text-secondary);
}

/* Responsive Design */
@media (max-width: 768px) {
    .container {
        padding: 1rem;
    }
    
    .header h1 {
        font-size: 2rem;
    }
    
    .stats-grid {
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    }
    
    .console-grid {
        grid-template-columns: 1fr;
    }
    
    .search-controls {
        flex-direction: column;
        align-items: stretch;
    }
    
    .search-input {
        min-width: unset;
    }
}

/* Loading Animation */
.loading {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid var(--border-color);
    border-radius: 50%;
    border-top-color: var(--primary-color);
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Utilities */
.text-center { text-align: center; }
.mb-1 { margin-bottom: 0.5rem; }
.mb-2 { margin-bottom: 1rem; }
.mb-3 { margin-bottom: 1.5rem; }
.mt-1 { margin-top: 0.5rem; }
.mt-2 { margin-top: 1rem; }
.mt-3 { margin-top: 1.5rem; }

.hidden { display: none !important; }
.fade-in { animation: fadeIn 0.5s ease-in; }

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Footer */
.footer {
    text-align: center;
    margin-top: 4rem;
    padding: 2rem;
    border-top: 1px solid var(--border-color);
    color: var(--text-secondary);
}

.footer a {
    color: var(--primary-color);
    text-decoration: none;
}

.footer a:hover {
    text-decoration: underline;
}'''
    
    def get_js_content(self):
        """Return the complete JavaScript content"""
        return '''// Retro Games Database - Interactive Features
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
});'''
    
    def generate_html_site(self):
        """Generate complete HTML site with all data embedded"""
        self.ensure_site_assets()
        progress_data = self.calculate_progress()
        
        # Calculate overall stats
        total_consoles = len(self.dead_consoles.get('consoles', []))
        databases_created = len(progress_data)
        
        if progress_data:
            total_games_target = sum(p['total_official_games'] for p in progress_data)
            total_games_current = sum(p['current_games'] for p in progress_data)
            overall_percentage = (total_games_current / total_games_target) * 100 if total_games_target > 0 else 0
        else:
            total_games_target = total_games_current = overall_percentage = 0
        
        # Get missing consoles
        missing_consoles = self.get_missing_consoles()
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Retro Games Database - Open Source Gaming Data</title>
    <meta name="description" content="Comprehensive open source database of retro gaming consoles and their complete game libraries">
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <h1>🎮 Retro Games Database</h1>
            <p>The most comprehensive open source database of dead gaming consoles and their complete game libraries</p>
            <div class="last-updated">Last Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
        </header>

        <!-- Overall Statistics -->
        <section class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" style="color: var(--primary-color)">{total_consoles}</div>
                <div class="stat-label">Dead Consoles Tracked</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: var(--success-color)">{databases_created}</div>
                <div class="stat-label">Databases Created</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: var(--accent-color)">{total_games_current:,}</div>
                <div class="stat-label">Games Catalogued</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: var(--secondary-color)">{overall_percentage:.1f}%</div>
                <div class="stat-label">Overall Progress</div>
            </div>
        </section>

        <!-- Console Progress -->
        <section>
            <h2 class="section-title">📊 Console Database Progress</h2>
            <div class="console-grid">
{self.generate_console_cards(progress_data)}
            </div>
        </section>

        <!-- Missing Consoles -->
        {self.generate_missing_consoles_section(missing_consoles)}

        <!-- Games Section -->
        <section class="games-section" id="games">
            <h2 class="section-title">🎮 Complete Games Database</h2>
            
            <div class="search-controls">
                <input type="text" id="gameSearch" class="search-input" placeholder="🔍 Search games, developers, publishers..." />
                <select id="consoleFilter" class="filter-select">
                    <option value="all">All Consoles</option>
{self.generate_console_filter_options(progress_data)}
                </select>
                <select id="sortSelect" class="filter-select">
                    <option value="title">Sort by Title</option>
                    <option value="developer">Sort by Developer</option>
                    <option value="publisher">Sort by Publisher</option>
                    <option value="year">Sort by Year (Old to New)</option>
                    <option value="year-desc">Sort by Year (New to Old)</option>
                </select>
            </div>
            
            <div id="resultsCount" class="text-center mb-2" style="color: var(--text-secondary)"></div>
            
            <div class="games-grid">
{self.generate_all_games_html()}
            </div>
        </section>
    </div>

    <!-- Footer -->
    <footer class="footer">
        <p>🌟 Open Source Gaming Database Project</p>
        <p>Built with ❤️ for the gaming community • <a href="https://github.com">View on GitHub</a></p>
        <p>Data sourced from multiple gaming databases • Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </footer>

    <script src="script.js"></script>
</body>
</html>"""

        # Write HTML file
        html_path = os.path.join('docs', 'index.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n🌐 Website generated successfully!")
        print(f"📁 Location: {os.path.abspath(html_path)}")
        print(f"🚀 Open in browser to view the complete database!")
    
    def generate_console_cards(self, progress_data):
        """Generate HTML for console progress cards"""
        cards_html = ""
        
        for console in progress_data:
            status_class = self.get_status_class(console['percentage_complete'])
            
            cards_html += f"""
                <div class="console-card">
                    <div class="console-header">
                        <div class="console-name">{console['console']}</div>
                        <div class="console-meta">
                            {console['manufacturer']} • Gen {console['generation']} • 
                            {console['release_year']}-{console['discontinuation_year']}
                        </div>
                    </div>
                    <div class="console-body">
                        <div class="progress-section">
                            <div class="progress-bar">
                                <div class="progress-fill" data-percentage="{console['percentage_complete']}" style="width: 0%"></div>
                            </div>
                            <div class="progress-text">
                                <span>{console['current_games']:,} / {console['total_official_games']:,} games</span>
                                <span class="status-badge {status_class}">{console['percentage_complete']}%</span>
                            </div>
                        </div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">
                            <strong>File:</strong> {console['filename']}<br>
                            <strong>Updated:</strong> {console['last_updated']}
                        </div>
                    </div>
                </div>"""
        
        return cards_html
    
    def generate_missing_consoles_section(self, missing_consoles):
        """Generate HTML for missing consoles section"""
        if not missing_consoles:
            return ""
        
        missing_html = f"""
        <section class="missing-consoles">
            <h2 class="section-title">🔍 Consoles Awaiting Databases</h2>
            <div class="missing-grid">
"""
        
        for console in missing_consoles[:12]:  # Show top 12 missing
            missing_html += f"""
                <div class="missing-item">
                    <div class="missing-name">{console['console']}</div>
                    <div class="missing-info">
                        {console['manufacturer']} • {console['total_official_games']:,} games<br>
                        Gen {console['generation']} • {console['release_year']}-{console['discontinuation_year']}
                    </div>
                </div>"""
        
        missing_html += """
            </div>
        </section>"""
        
        return missing_html
    
    def generate_console_filter_options(self, progress_data):
        """Generate filter options for console dropdown"""
        options = ""
        for console in progress_data:
            console_key = console['console'].lower().replace(' ', '-')
            options += f'                    <option value="{console_key}">{console["console"]}</option>\n'
        return options
    
    def generate_all_games_html(self):
        """Generate HTML for all games from all databases"""
        games_html = ""
        
        for db_name, db_info in self.console_databases.items():
            console_info = self.get_console_info(db_name)
            console_name = console_info.get('console', db_name)
            console_key = console_name.lower().replace(' ', '-')
            
            for game in db_info['data'].get('games', []):
                release_year = game.get('release_date', '')[:4] if game.get('release_date') else 'Unknown'
                
                games_html += f"""
                <div class="game-card" 
                     data-title="{game.get('title', 'Unknown')}"
                     data-developer="{game.get('developer', 'Unknown')}" 
                     data-publisher="{game.get('publisher', 'Unknown')}"
                     data-console="{console_key}"
                     data-year="{release_year}"
                     data-release-date="{game.get('release_date', '')}">
                    <div class="game-title">{game.get('title', 'Unknown')}</div>
                    <div class="game-meta">
                        <strong>Developer:</strong> {game.get('developer', 'Unknown')}<br>
                        <strong>Publisher:</strong> {game.get('publisher', 'Unknown')}<br>
                        <strong>Console:</strong> {console_name}<br>
                        <strong>Released:</strong> {self.format_date(game.get('release_date', 'Unknown'))}
                    </div>
                </div>"""
        
        return games_html
    
    def get_status_class(self, percentage):
        """Get CSS class for status badge"""
        if percentage >= 100:
            return "status-complete"
        elif percentage >= 75:
            return "status-nearly"
        elif percentage >= 50:
            return "status-progress"
        elif percentage >= 25:
            return "status-started"
        elif percentage > 0:
            return "status-minimal"
        else:
            return "status-none"
    
    def get_missing_consoles(self):
        """Get list of consoles without databases"""
        existing_consoles = set()
        for db_name in self.console_databases.keys():
            for console in self.dead_consoles.get('consoles', []):
                if db_name.lower() in console['console'].lower():
                    existing_consoles.add(console['console'])
        
        missing_consoles = []
        for console in self.dead_consoles.get('consoles', []):
            if console['console'] not in existing_consoles:
                missing_consoles.append(console)
        
        # Sort by total games (most games first)
        return sorted(missing_consoles, key=lambda x: x['total_official_games'], reverse=True)
    
    def format_date(self, date_string):
        """Format date string for display"""
        if not date_string or date_string == 'Unknown':
            return 'Unknown'
        
        try:
            if len(date_string) == 4:  # Just year
                return date_string
            elif len(date_string) >= 10:  # Full date
                date_obj = datetime.strptime(date_string[:10], '%Y-%m-%d')
                return date_obj.strftime('%b %d, %Y')
            else:
                return date_string
        except:
            return date_string

def main():
    tracker = ProgressTracker()
    
    # Generate console report
    tracker.generate_report()
    
    # Generate website
    print("\n🌐 Generating website...")
    tracker.generate_html_site()

if __name__ == "__main__":
    main()
