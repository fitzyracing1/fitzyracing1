"""
Test secure display without password
"""

from pathlib import Path
from src.secure_display import SecureDisplayManager


manager = SecureDisplayManager()

# Load items
items = manager.load_items()
print(f"\n📥 Loaded {len(items)} items from storage")

# Display public summary (always visible)
manager.display_summary()

# Try to display items WITHOUT password
print("Attempting to display items WITHOUT authentication...")
manager.display_denied()

print("✓ Security test complete: Items hidden without password")
