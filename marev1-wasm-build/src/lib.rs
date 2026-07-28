// marev1 proof-of-work, ported to WebAssembly.
//
// This is the exact hashing + mining scheme from marev1/src/block.rs:
//   hash = SHA256( index | timestamp | tx_string | previous_hash | nonce )   (hex)
//   mine by incrementing `nonce` until the hex hash has `difficulty` leading zeros.
//
// The only change from the native code is that `timestamp` is passed in as an
// argument instead of read from SystemTime (browsers/wasm have no wall clock
// on this target), and the demo mines a block with an empty transaction set
// (tx_string = ""), exactly as marev1 does for an empty mempool.
//
// Interface is numbers-only so it works with a plain WebAssembly.instantiate
// (no wasm-bindgen). The resulting 32-byte hash is written into linear memory;
// JS reads it back via hash_ptr().

use sha2::{Digest, Sha256};

static mut HASH_BUF: [u8; 32] = [0u8; 32];

// Faithful to Block::calculate_hash in marev1/src/block.rs (empty tx set).
fn calculate_hash(index: u32, timestamp: u32, prev_hash: &str, nonce: u32) -> [u8; 32] {
    let tx_string = ""; // empty mempool: Vec<Transaction>.join("|") == ""
    let input = format!("{}{}{}{}{}", index, timestamp, tx_string, prev_hash, nonce);

    let mut hasher = Sha256::new();
    hasher.update(input.as_bytes());
    let out = hasher.finalize();

    let mut arr = [0u8; 32];
    arr.copy_from_slice(&out);
    arr
}

// Count leading zero HEX digits (nibbles) — matches marev1's
// `hash.starts_with(&"0".repeat(difficulty))` on the hex string.
fn leading_zero_nibbles(hash: &[u8; 32]) -> u32 {
    let mut count = 0u32;
    for &b in hash.iter() {
        if (b >> 4) == 0 { count += 1; } else { break; }
        if (b & 0x0f) == 0 { count += 1; } else { break; }
    }
    count
}

/// Mine a marev1 block. Returns the winning nonce, or u32::MAX if not found
/// within `max_iters`. The 32-byte hash of the final attempt is stored for
/// hash_ptr(). `prev_hash_seed` becomes a 16-hex-char previous_hash string.
#[no_mangle]
pub extern "C" fn mine(
    index: u32,
    timestamp: u32,
    prev_hash_seed: u32,
    difficulty: u32,
    max_iters: u32,
) -> u32 {
    let prev_hash = format!("{:016x}", prev_hash_seed);
    let mut nonce: u32 = 0;
    loop {
        let h = calculate_hash(index, timestamp, &prev_hash, nonce);
        if leading_zero_nibbles(&h) >= difficulty {
            unsafe { HASH_BUF = h; }
            return nonce;
        }
        if nonce == max_iters {
            unsafe { HASH_BUF = h; }
            return u32::MAX; // not found within budget
        }
        nonce += 1;
    }
}

/// Just hash one block (no mining) — useful for verifying a nonce.
#[no_mangle]
pub extern "C" fn hash_block(index: u32, timestamp: u32, prev_hash_seed: u32, nonce: u32) -> u32 {
    let prev_hash = format!("{:016x}", prev_hash_seed);
    let h = calculate_hash(index, timestamp, &prev_hash, nonce);
    unsafe { HASH_BUF = h; }
    leading_zero_nibbles(&h)
}

/// Pointer to the 32-byte hash buffer in linear memory (JS reads it as hex).
#[no_mangle]
pub extern "C" fn hash_ptr() -> u32 {
    let p = &raw const HASH_BUF;
    p as u32
}
