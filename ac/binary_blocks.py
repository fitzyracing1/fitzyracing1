"""
Binary Block Inclusion Project
Demonstrates binary patterns, block structures, and blockchain timestamps
"""

import time
import hashlib

def binary_blocks():
    """Generate binary patterns with block inclusion"""
    patterns = [
        "01",           # 1
        "0110",         # 6
        "0111010",      # 58
        "01111",        # 15
    ]
    
    for pattern in patterns:
        decimal = int(pattern, 2)
        print(f"{pattern} -> {decimal}")

def block_inclusion(binary_str):
    """Check if blocks are included in binary string"""
    blocks = ["01", "11", "10"]
    result = {}
    
    for block in blocks:
        result[block] = block in binary_str
    
    return result

def time_to_binary(timestamp=None):
    """Convert timestamp to binary representation"""
    if timestamp is None:
        timestamp = int(time.time())
    
    binary = bin(timestamp)[2:]  # Remove '0b' prefix
    return binary, timestamp

def create_blockchain_block(index, data, previous_hash="0"):
    """Create a blockchain block with binary timestamp"""
    binary_time, unix_time = time_to_binary()
    
    # Create block data
    block_data = f"{index}{data}{previous_hash}{binary_time}"
    block_hash = hashlib.sha256(block_data.encode()).hexdigest()
    binary_hash = bin(int(block_hash, 16))[2:].zfill(256)
    
    return {
        "index": index,
        "timestamp": unix_time,
        "timestamp_binary": binary_time,
        "data": data,
        "previous_hash": previous_hash,
        "hash": block_hash,
        "hash_binary": binary_hash[:64]  # First 64 bits
    }

def display_blockchain_block(block):
    """Display blockchain block information"""
    print(f"\n{'='*60}")
    print(f"Block #{block['index']}")
    print(f"{'='*60}")
    print(f"Unix Timestamp:        {block['timestamp']}")
    print(f"Binary Timestamp:      {block['timestamp_binary']}")
    print(f"Data:                  {block['data']}")
    print(f"Previous Hash:         {block['previous_hash']}")
    print(f"Block Hash:            {block['hash'][:32]}...")
    print(f"Binary Hash (64-bit):  {block['hash_binary']}")
    print(f"{'='*60}")

if __name__ == "__main__":
    print("=== Binary Patterns ===")
    binary_blocks()
    
    print("\n=== Block Inclusion Check ===")
    test_string = "0111010"
    print(f"Testing: {test_string}")
    inclusions = block_inclusion(test_string)
    for block, included in inclusions.items():
        print(f"Block '{block}': {included}")
    
    print("\n=== Blockchain with Binary Timestamps ===")
    
    # Create a simple blockchain
    blockchain = []
    previous_hash = "genesis"
    
    for i in range(3):
        block = create_blockchain_block(i, f"Transaction Block {i}", previous_hash)
        blockchain.append(block)
        display_blockchain_block(block)
        previous_hash = block['hash']
        
        if i < 2:
            time.sleep(1)  # Ensure different timestamps
