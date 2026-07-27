#!/usr/bin/env python3
"""
Batch Item Viewer - Open multiple items at once
Usage: python batch_view.py cycle 1  (view all items in cycle 1)
       python batch_view.py value 500-800  (view items in value range)
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


def view_cycle(cycle_num: int):
    """View all items in a cycle"""
    items = load_items()
    cycle_items = [item for item in items if item['cycle'] == cycle_num]
    
    if not cycle_items:
        print(f"No items in cycle {cycle_num}")
        return
    
    print(f"\n[CYCLE {cycle_num}] - {len(cycle_items)} items")
    print("=" * 80)
    
    for item in cycle_items:
        print(f"ID: {item['item_id']} | Item #{item['item_number']:2d} | Value: {item['value']:4d} | {item['source']} | {item['timestamp']}")
    
    print("=" * 80)
    
    # Summary stats for cycle
    values = [item['value'] for item in cycle_items]
    print(f"\nCycle Statistics:")
    print(f"  Total Items: {len(cycle_items)}")
    print(f"  Min Value: {min(values)}")
    print(f"  Max Value: {max(values)}")
    print(f"  Avg Value: {sum(values) / len(values):.2f}\n")


def view_value_range(min_val: int, max_val: int):
    """View items in value range"""
    items = load_items()
    matching = [item for item in items if min_val <= item['value'] <= max_val]
    
    if not matching:
        print(f"No items found with value {min_val}-{max_val}")
        return
    
    print(f"\n[VALUE RANGE] {min_val}-{max_val} - {len(matching)} items")
    print("=" * 80)
    
    for item in matching:
        print(f"ID: {item['item_id']} | Cycle: {item['cycle']:2d} | Item #{item['item_number']:2d} | Value: {item['value']:4d} | {item['source']}")
    
    print("=" * 80 + "\n")


def view_source(source_name: str):
    """View items from specific source"""
    items = load_items()
    matching = [item for item in items if item['source'] == source_name]
    
    if not matching:
        print(f"No items from source {source_name}")
        return
    
    print(f"\n[SOURCE: {source_name}] - {len(matching)} items")
    print("=" * 80)
    
    for item in matching:
        print(f"ID: {item['item_id']} | Cycle: {item['cycle']:2d} | Value: {item['value']:4d} | {item['timestamp'][:19]}")
    
    print("=" * 80 + "\n")


def main():
    if len(sys.argv) < 2:
        print("[BATCH ITEM VIEWER]")
        print("\nUsage:")
        print("  python batch_view.py cycle <num>      - View all items in cycle")
        print("  python batch_view.py value <min-max>  - View items in value range")
        print("  python batch_view.py source <name>    - View items from source")
        print("\nExamples:")
        print("  python batch_view.py cycle 1")
        print("  python batch_view.py value 500-800")
        print("  python batch_view.py source source_1\n")
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == "cycle" and len(sys.argv) > 2:
        try:
            cycle_num = int(sys.argv[2])
            view_cycle(cycle_num)
        except ValueError:
            print("Invalid cycle number")
    
    elif cmd == "value" and len(sys.argv) > 2:
        try:
            min_v, max_v = map(int, sys.argv[2].split("-"))
            view_value_range(min_v, max_v)
        except:
            print("Usage: python batch_view.py value 100-500")
    
    elif cmd == "source" and len(sys.argv) > 2:
        source = sys.argv[2]
        view_source(source)
    
    else:
        print("Invalid command")


if __name__ == "__main__":
    main()
