"""
Task Server - Onboard server that manages collected items
Reduces immediate workload by processing only 0.8% of tasks in memory
Stores remainder for intelligent batch thinking later
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import math


class TaskServer:
    """Server that manages crawled items with intelligent workload distribution"""
    
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        
        self.data_dir = Path(data_dir)
        self.items_file = self.data_dir / "collected_items.json"
        self.compute_tasks_file = self.data_dir / "compute_tasks.json"
        self.pending_tasks_file = self.data_dir / "pending_tasks.json"
        self.intelligence_tasks_file = self.data_dir / "intelligence_tasks.json"
        
        self.all_items = []
        self.compute_tasks = []  # 0.8% for immediate processing
        self.pending_tasks = []  # Rest stored for later
        self.intelligence_tasks = []  # For batch intelligent thinking
    
    def load_items(self) -> List[Dict[str, Any]]:
        """Load all collected items from file"""
        if self.items_file.exists():
            with open(self.items_file, 'r') as f:
                self.all_items = json.load(f)
            return self.all_items
        return []
    
    def distribute_workload(self):
        """Distribute items: 0.8% to compute, rest to pending/intelligence"""
        total_items = len(self.all_items)
        
        # Calculate 0.8% for immediate compute tasks
        compute_count = max(1, math.ceil(total_items * 0.008))
        
        print(f"\n📦 WORKLOAD DISTRIBUTION")
        print("=" * 60)
        print(f"Total Items: {total_items}")
        print(f"Compute Tasks (0.8%): {compute_count}")
        print(f"Pending Tasks (99.2%): {total_items - compute_count}")
        print("=" * 60)
        
        # Assign first 0.8% to compute tasks
        self.compute_tasks = self.all_items[:compute_count]
        
        # Rest go to pending for intelligent processing
        self.pending_tasks = self.all_items[compute_count:]
        
        # All pending tasks are intelligence candidates
        self.intelligence_tasks = [
            {
                "task_id": f"intel_{i}",
                "source_cycle": item['cycle'],
                "items_found": item['items_found'],
                "timestamp": item['timestamp'],
                "status": "pending_intelligence"
            }
            for i, item in enumerate(self.pending_tasks)
        ]
    
    def process_compute_tasks(self):
        """Process immediate compute tasks (0.8%)"""
        print(f"\n⚡ PROCESSING COMPUTE TASKS ({len(self.compute_tasks)} items)")
        print("=" * 60)
        
        results = []
        for task in self.compute_tasks:
            result = {
                "cycle": task['cycle'],
                "processed_items": task['items_found'],
                "action": "immediate_compute",
                "timestamp": task['timestamp']
            }
            results.append(result)
            print(f"  ✓ Cycle {task['cycle']}: Computed {task['items_found']} items")
        
        print("=" * 60)
        return results
    
    def store_for_intelligence(self):
        """Store pending tasks for intelligent batch thinking"""
        print(f"\n🧠 STORING FOR INTELLIGENT BATCH PROCESSING")
        print("=" * 60)
        print(f"Tasks in Storage: {len(self.intelligence_tasks)}")
        print(f"Ready for Batch Thinking: YES")
        print("=" * 60)
        
        # Save intelligence tasks
        with open(self.intelligence_tasks_file, 'w') as f:
            json.dump(self.intelligence_tasks, f, indent=2)
        
        # Save pending tasks
        with open(self.pending_tasks_file, 'w') as f:
            json.dump(self.pending_tasks, f, indent=2)
        
        return len(self.intelligence_tasks)
    
    def show_server_status(self):
        """Display current server status - items shown to no one"""
        print(f"\n🔐 SERVER STATUS (PRIVATE - SHOWN TO NO ONE)")
        print("=" * 60)
        print(f"Items in Memory: {len(self.all_items)}")
        print(f"Active Compute: {len(self.compute_tasks)}")
        print(f"Queued for Intelligence: {len(self.intelligence_tasks)}")
        print(f"Workload Reduction: 99.2% offloaded")
        print("=" * 60)
    
    def port_to_server(self):
        """Main workflow: load, distribute, process, and store"""
        print("\n" + "🌐 TASK SERVER INITIALIZATION".center(60, "="))
        
        # Load all items
        items = self.load_items()
        print(f"\n📥 Loaded {len(items)} items from storage")
        
        # Distribute workload
        self.distribute_workload()
        
        # Process compute tasks immediately
        compute_results = self.process_compute_tasks()
        
        # Store the rest for intelligent thinking
        intelligence_count = self.store_for_intelligence()
        
        # Show server status
        self.show_server_status()
        
        # Save compute results
        compute_file = self.data_dir / "compute_results.json"
        with open(compute_file, 'w') as f:
            json.dump(compute_results, f, indent=2)
        
        print(f"\n✅ SERVER SETUP COMPLETE")
        print(f"   - Compute results saved")
        print(f"   - Intelligence tasks queued: {intelligence_count}")
        print(f"   - Ready for batch thinking\n")
        
        return {
            "compute_tasks": len(self.compute_tasks),
            "intelligence_tasks": len(self.intelligence_tasks),
            "efficiency": "99.2% workload reduction"
        }


def main():
    """Initialize task server and port items"""
    server = TaskServer()
    server.port_to_server()


if __name__ == "__main__":
    main()
