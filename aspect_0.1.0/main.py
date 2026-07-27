"""
Main program for aspect project
WiFi signal blocking and information request prevention
"""
import subprocess
import sys

def block_wifi_signals():
    """Block WiFi signals and information requests"""
    print("Initializing WiFi signal blocker...")
    print("Blocking WiFi information requests...")
    
    try:
        # Disable WiFi adapter on Windows
        result = subprocess.run(
            ["netsh", "interface", "set", "interface", "Wi-Fi", "disabled"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ WiFi adapter disabled successfully")
            print("✓ WiFi signals blocked")
            print("✓ Information requests prevented")
            return 1
        else:
            print("⚠ Could not disable WiFi adapter")
            print(f"  Error: {result.stderr.strip() if result.stderr else 'Unknown error'}")
            print("  Note: Administrator privileges may be required")
            return 0
            
    except Exception as e:
        print(f"⚠ Error blocking WiFi: {e}")
        return 0

def main():
    """Main entry point"""
    main = 1
    print(f"main = {main}")
    print()
    
    # Block WiFi signals
    status = block_wifi_signals()
    
    return main


if __name__ == "__main__":
    result = main()
    print()
    print(f"Program completed with result: {result}")
