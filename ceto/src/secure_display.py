"""
Secure Display Manager - Password-protected access to collected items
Without password: Display denied
With correct password: Show all collected items in detail
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any
import getpass


class SecureDisplayManager:
    """Manages password-protected access to collected items"""
    
    DEFAULT_PASSWORD_HASH = hashlib.sha256("ceto2026".encode()).hexdigest()
    
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        
        self.data_dir = Path(data_dir)
        self.items_file = self.data_dir / "detailed_items.json"
        self.cycle_file = self.data_dir / "collected_items.json"
        self.all_items = []
        self.cycles = []
        self.authenticated = False
        self.password_attempts = 0
        self.max_attempts = 3
    
    def load_items(self) -> List[Dict[str, Any]]:
        """Load all collected items"""
        if self.items_file.exists():
            with open(self.items_file, 'r') as f:
                self.all_items = json.load(f)
        
        if self.cycle_file.exists():
            with open(self.cycle_file, 'r') as f:
                self.cycles = json.load(f)
        
        return self.all_items
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return self.hash_password(password) == self.DEFAULT_PASSWORD_HASH
    
    def attempt_authentication(self) -> bool:
        """Attempt to authenticate user with password"""
        print("\n[SECURE ACCESS REQUIRED]")
        print("=" * 60)
        
        while self.password_attempts < self.max_attempts:
            password = getpass.getpass("Enter password to access items: ")
            self.password_attempts += 1
            
            if self.verify_password(password):
                print("[OK] Authentication successful!")
                self.authenticated = True
                return True
            else:
                remaining = self.max_attempts - self.password_attempts
                if remaining > 0:
                    print(f"[ERROR] Invalid password. {remaining} attempt(s) remaining.")
                else:
                    print("[ERROR] Maximum attempts exceeded. Access denied.")
        
        return False
    
    def display_denied(self):
        """Display access denied message"""
        print("\n" + "[ACCESS DENIED]".center(60, "="))
        print("=" * 60)
        print("NO PASSWORD PROVIDED")
        print("Cannot display collected items without authentication")
        print("=" * 60 + "\n")
    
    def display_all_items(self):
        """Display all collected items in detail"""
        print("\n" + "[ALL COLLECTED ITEMS - AUTHENTICATED ACCESS]".center(60, "="))
        print("=" * 60)
        
        if not self.all_items:
            print("No items found.")
            print("=" * 60 + "\n")
            return
        
        print(f"\n[CYCLE SUMMARY] ({len(self.cycles)} cycles):\n")
        for cycle in self.cycles:
            print(f"Cycle {cycle['cycle']:2d} │ Items: {cycle['items_found']:3d} │ {cycle['timestamp']}")
        
        print("\n" + "-" * 60)
        print(f"\n[DETAILED ITEMS] ({len(self.all_items)} total items):\n")
        
        items_by_cycle = {}
        for item in self.all_items:
            cycle = item['cycle']
            if cycle not in items_by_cycle:
                items_by_cycle[cycle] = []
            items_by_cycle[cycle].append(item)
        
        for cycle in sorted(items_by_cycle.keys()):
            items = items_by_cycle[cycle]
            print(f"\n  > CYCLE {cycle} ({len(items)} items):")
            for item in items:
                print(f"     • ID: {item['item_id']} │ Value: {item['value']:4d} │ Source: {item['source']}")
        
        print("\n" + "=" * 60)
        print(f"TOTAL ITEMS COLLECTED: {len(self.all_items)}")
        print(f"AVERAGE PER CYCLE: {len(self.all_items) / len(self.cycles):.2f}")
        print("=" * 60 + "\n")
    
    def display_summary(self):
        """Display summary only (no password needed)"""
        print("\n" + "[SUMMARY - PUBLIC]".center(60, "="))
        print("=" * 60)
        print(f"Total Crawl Cycles: {len(self.cycles)}")
        print(f"System Status: Operational")
        print(f"Detailed Items: LOCKED (requires authentication)")
        print("=" * 60 + "\n")
    
    def secure_display(self, require_password: bool = True):
        """Main secure display workflow"""
        print("\n" + "[SECURE DISPLAY MANAGER]".center(60, "="))
        
        items = self.load_items()
        print(f"\nLoaded {len(items)} items from {len(self.cycles)} cycles")
        
        self.display_summary()
        
        if not require_password:
            self.display_denied()
            return False
        
        if self.attempt_authentication():
            self.display_all_items()
            return True
        else:
            self.display_denied()
            return False


def main():
    """Main entry point"""
    manager = SecureDisplayManager()
    success = manager.secure_display(require_password=True)
    
    if success:
        print("✓ Session authenticated and items displayed")
    else:
        print("✗ Session denied - no items displayed")


if __name__ == "__main__":
    main()
