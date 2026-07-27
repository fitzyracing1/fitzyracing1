"""
Item Inspector - Open and view individual items in detail
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class ItemInspector:
    """Interactive tool to view and inspect individual items"""
    
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        
        self.data_dir = Path(data_dir)
        self.items_file = self.data_dir / "detailed_items.json"
        self.all_items = []
        self.load_items()
    
    def load_items(self):
        """Load all items"""
        if self.items_file.exists():
            with open(self.items_file, 'r') as f:
                self.all_items = json.load(f)
        print(f"Loaded {len(self.all_items)} items\n")
    
    def view_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """View a single item by item_id"""
        for item in self.all_items:
            if item['item_id'] == item_id:
                return item
        return None
    
    def display_item(self, item: Dict[str, Any]):
        """Display a single item with full details"""
        print("\n" + "=" * 60)
        print("[ITEM DETAILS]")
        print("=" * 60)
        print(f"Item ID:       {item['item_id']}")
        print(f"Cycle:         {item['cycle']}")
        print(f"Item Number:   {item['item_number']}")
        print(f"Timestamp:     {item['timestamp']}")
        print(f"Value:         {item['value']}")
        print(f"Status:        {item['status']}")
        print(f"Source:        {item['source']}")
        print("=" * 60 + "\n")
    
    def list_items_by_cycle(self, cycle: int):
        """List all items in a specific cycle"""
        cycle_items = [item for item in self.all_items if item['cycle'] == cycle]
        
        if not cycle_items:
            print(f"No items found in cycle {cycle}")
            return
        
        print(f"\n[CYCLE {cycle} ITEMS] ({len(cycle_items)} items)")
        print("=" * 60)
        for item in cycle_items:
            print(f"{item['item_number']:3d}. ID: {item['item_id']} │ Value: {item['value']:4d} │ {item['source']}")
        print("=" * 60 + "\n")
    
    def search_items_by_value(self, min_value: int = 0, max_value: int = 1000):
        """Search items by value range"""
        matching = [item for item in self.all_items 
                   if min_value <= item['value'] <= max_value]
        
        print(f"\n[SEARCH] Items with value {min_value}-{max_value}: {len(matching)} items")
        print("=" * 60)
        for item in matching[:50]:  # Show first 50
            print(f"ID: {item['item_id']} │ Cycle: {item['cycle']:2d} │ Value: {item['value']:4d} │ {item['source']}")
        
        if len(matching) > 50:
            print(f"... and {len(matching) - 50} more items")
        print("=" * 60 + "\n")
    
    def interactive_mode(self):
        """Interactive mode to open items"""
        print("\n" + "[ITEM INSPECTOR - INTERACTIVE MODE]".center(60, "="))
        print("=" * 60)
        print("Commands:")
        print("  view <item_id>    - View specific item (e.g., 'view a41d9558')")
        print("  cycle <num>       - List all items in cycle (e.g., 'cycle 1')")
        print("  search <min-max>  - Search by value (e.g., 'search 500-800')")
        print("  stats             - Show statistics")
        print("  quit              - Exit")
        print("=" * 60 + "\n")
        
        while True:
            try:
                cmd = input(">> ").strip().lower()
                
                if cmd == "quit":
                    print("Exiting...")
                    break
                
                elif cmd == "stats":
                    values = [item['value'] for item in self.all_items]
                    print(f"\n[STATISTICS]")
                    print(f"Total Items: {len(self.all_items)}")
                    print(f"Min Value: {min(values)}")
                    print(f"Max Value: {max(values)}")
                    print(f"Avg Value: {sum(values) / len(values):.2f}\n")
                
                elif cmd.startswith("view "):
                    item_id = cmd[5:].strip()
                    item = self.view_item(item_id)
                    if item:
                        self.display_item(item)
                    else:
                        print(f"Item not found: {item_id}\n")
                
                elif cmd.startswith("cycle "):
                    try:
                        cycle_num = int(cmd[6:].strip())
                        self.list_items_by_cycle(cycle_num)
                    except ValueError:
                        print("Invalid cycle number\n")
                
                elif cmd.startswith("search "):
                    try:
                        range_str = cmd[7:].strip()
                        min_v, max_v = map(int, range_str.split("-"))
                        self.search_items_by_value(min_v, max_v)
                    except:
                        print("Usage: search 100-500\n")
                
                else:
                    print("Unknown command. Type 'quit' to exit.\n")
            
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}\n")


def main():
    """Main entry point"""
    inspector = ItemInspector()
    
    # Example: Show first cycle items
    print("[QUICK VIEW] First 10 items from Cycle 1:")
    inspector.list_items_by_cycle(1)
    
    # Enter interactive mode
    inspector.interactive_mode()


if __name__ == "__main__":
    main()
