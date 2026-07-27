#!/usr/bin/env python3
"""
Quick Item Viewer - Open specific items by ID
Usage: python view_item.py <item_id>
"""

import json
import sys
from pathlib import Path


def load_items():
    """Load all items"""
    data_dir = Path(__file__).parent.parent / "data"
    items_file = data_dir / "detailed_items.json"
    
    if items_file.exists():
        with open(items_file, 'r') as f:
            return json.load(f)
    return []


def view_item(item_id: str):
    """View a specific item"""
    items = load_items()
    
    for item in items:
        if item['item_id'] == item_id:
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
            return
    
    print(f"Item not found: {item_id}")


def list_all_items():
    """List all item IDs"""
    items = load_items()
    print(f"\nFound {len(items)} items:\n")
    
    for i, item in enumerate(items):
        print(f"{i+1:4d}. ID: {item['item_id']} - Cycle: {item['cycle']:2d} - Value: {item['value']:4d}")
        
        if (i + 1) % 10 == 0:
            print()


def main():
    if len(sys.argv) > 1:
        item_id = sys.argv[1]
        view_item(item_id)
    else:
        print("[ITEM VIEWER]")
        print("Usage: python view_item.py <item_id>")
        print("\nExample: python view_item.py a41d9558")
        list_all_items()


if __name__ == "__main__":
    main()
