#!/usr/bin/env python3
"""
Gaming Database Progress Tracker
Analyzes completion progress across all dead gaming consoles
"""

import json
import os
from typing import Dict, List, Tuple
from datetime import datetime

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

def main():
    tracker = ProgressTracker()
    tracker.generate_report()

if __name__ == "__main__":
    main()
