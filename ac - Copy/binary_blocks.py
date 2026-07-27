"""
Binary Block Inclusion Project
Demonstrates binary patterns and block structures
"""

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

if __name__ == "__main__":
    print("=== Binary Patterns ===")
    binary_blocks()
    
    print("\n=== Block Inclusion Check ===")
    test_string = "0111010"
    print(f"Testing: {test_string}")
    inclusions = block_inclusion(test_string)
    for block, included in inclusions.items():
        print(f"Block '{block}': {included}")
