"""
Crawl Bot - Autonomous bot that operates independently 20 times
Answers to no one, runs its own logic 20x
"""

import time
import random
import json
from datetime import datetime
from pathlib import Path


class CrawlBot:
    """A bot that crawls autonomously without external control"""
    
    def __init__(self, cycles: int = 20):
        self.cycles = cycles
        self.cycle_count = 0
        self.data_collected = []
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.items_file = self.data_dir / "collected_items.json"
        self.summary_file = self.data_dir / "crawl_summary.json"
        
    def crawl(self):
        """Execute a single crawl cycle"""
        self.cycle_count += 1
        
        # Simulate crawling activity
        timestamp = datetime.now().isoformat()
        data = {
            'cycle': self.cycle_count,
            'timestamp': timestamp,
            'status': 'crawled',
            'items_found': random.randint(1, 100)
        }
        
        self.data_collected.append(data)
    def save_results(self):
        """Save collected data to files"""
        # Save detailed items
        with open(self.items_file, 'w') as f:
            json.dump(self.data_collected, f, indent=2)
        
        # Save summary
        summary = {
            'total_cycles': self.cycle_count,
            'total_items': sum(d['items_found'] for d in self.data_collected),
            'average_items_per_cycle': sum(d['items_found'] for d in self.data_collected) / self.cycle_count if self.cycle_count > 0 else 0,
            'timestamp': datetime.now().isoformat(),
            'data_file': str(self.items_file)
        }
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    def display_all_items(self):
        """Display all collected items in detail"""
        print("\n" + "=" * 60)
        print("📊 ALL COLLECTED ITEMS SUMMARY")
        print("=" * 60)
        
        total_items = 0
        for cycle_data in self.data_collected:
            items_found = cycle_data['items_found']
            total_items += items_found
            print(f"  Cycle {cycle_data['cycle']:2d} | Items: {items_found:3d} | Time: {cycle_data['timestamp']}")
        
        print("=" * 60)
        print(f"Total Items Collected: {total_items}")
        print(f"Average per Cycle: {total_items / len(self.data_collected):.2f}")
        print("=" * 60 + "\n")
    
    def run(self):
        """Run the bot for the specified number of cycles"""
        print(f"🤖 Crawl Bot Starting - {self.cycles} cycles ahead")
        print("=" * 60)
        
        for i in range(self.cycles):
            self.crawl()
            # Small delay between cycles
            time.sleep(0.1)
        
        print("=" * 60)
        print(f"✓ Bot completed {self.cycle_count} cycles")
        print(f"✓ Total items collected: {sum(d['items_found'] for d in self.data_collected)}")
        
        # Display all items
        self.display_all_items()
        
        # Save results for future crawling
        summary = self.save_results()
        print(f"💾 Data saved to: {self.data_dir}")
        print(f"   - Items: {self.items_file.name}")
        print(f"   - Summary: {self.summary_file.name}\n")
        
        return self.data_collected
        print(f"✓ Bot completed {self.cycle_count} cycles")
        print(f"✓ Total items collected: {sum(d['items_found'] for d in self.data_collected)}")
        
        return self.data_collected


def main():
    """Main entry point - Bot answers to no one, just runs"""
    bot = CrawlBot(cycles=20)
    results = bot.run()


if __name__ == "__main__":
    main()
