"""
Enhanced Crawl Bot - Generates detailed item data for each crawl cycle
Each item is tracked individually with metadata
"""

import time
import random
import json
import uuid
from datetime import datetime
from pathlib import Path


class EnhancedCrawlBot:
    """Enhanced bot that crawls and generates detailed item data"""
    
    def __init__(self, cycles: int = 20):
        self.cycles = cycles
        self.cycle_count = 0
        self.all_items = []  # Individual items
        self.cycle_summaries = []  # Cycle summaries
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.detailed_items_file = self.data_dir / "detailed_items.json"
        self.collected_items_file = self.data_dir / "collected_items.json"
    
    def generate_items(self, count: int, cycle: int) -> list:
        """Generate individual items for a cycle"""
        items = []
        for i in range(count):
            item = {
                "item_id": str(uuid.uuid4())[:8],
                "cycle": cycle,
                "item_number": i + 1,
                "timestamp": datetime.now().isoformat(),
                "value": random.randint(10, 1000),
                "status": "collected",
                "source": f"source_{random.randint(1, 5)}"
            }
            items.append(item)
        return items
    
    def crawl(self):
        """Execute a single crawl cycle and generate items"""
        self.cycle_count += 1
        
        # Generate random number of items for this cycle
        items_count = random.randint(1, 100)
        
        # Create individual items
        items = self.generate_items(items_count, self.cycle_count)
        self.all_items.extend(items)
        
        # Create cycle summary
        cycle_summary = {
            'cycle': self.cycle_count,
            'timestamp': datetime.now().isoformat(),
            'status': 'crawled',
            'items_found': items_count,
            'items_list': [item['item_id'] for item in items]
        }
        self.cycle_summaries.append(cycle_summary)
        
        print(f"[Cycle {self.cycle_count}] Generated {items_count} items")
        
        return items
    
    def run(self):
        """Run the bot for the specified number of cycles"""
        print(f"\n🤖 ENHANCED CRAWL BOT - Detailed Item Collection")
        print("=" * 60)
        
        for i in range(self.cycles):
            self.crawl()
            time.sleep(0.05)
        
        print("=" * 60)
        print(f"✓ Bot completed {self.cycle_count} cycles")
        print(f"✓ Total individual items collected: {len(self.all_items)}")
        
        # Save detailed items
        self.save_results()
        
        return self.all_items
    
    def save_results(self):
        """Save all results to files"""
        # Save detailed individual items
        with open(self.detailed_items_file, 'w') as f:
            json.dump(self.all_items, f, indent=2)
        
        # Save cycle summaries
        with open(self.collected_items_file, 'w') as f:
            json.dump(self.cycle_summaries, f, indent=2)
        
        print(f"\n💾 Data saved:")
        print(f"   - {len(self.all_items)} individual items → detailed_items.json")
        print(f"   - {len(self.cycle_summaries)} cycle summaries → collected_items.json\n")


def main():
    """Main entry point"""
    bot = EnhancedCrawlBot(cycles=20)
    bot.run()


if __name__ == "__main__":
    main()
