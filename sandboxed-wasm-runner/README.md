# marev1 Miner — Sandboxed WASM (browser extension)

A Manifest V3 browser extension that runs **your marev1 proof-of-work** as
**WebAssembly**, in a **fresh, isolated sandbox on every run**, then destroys it.
No remote code, no network permissions, no storage.

## What it runs

`program.wasm` is your `marev1` blockchain's proof-of-work, ported from
`marev1/src/block.rs` (`Block::calculate_hash` + `Block::mine_block`):

```
hash  = SHA256( index | timestamp | tx_string | previous_hash | nonce )   // hex
mine  = increment nonce until the hex hash has `difficulty` leading zeros
```

The port is faithful to your native code. The only change: `timestamp` is passed
in as an argument instead of read from `SystemTime` (this wasm target has no wall
clock), and the demo mines with an empty transaction set (`tx_string = ""`), just
like marev1 with an empty mempool. Verified: the wasm hash is byte-for-byte
identical to a SHA-256 recomputation of marev1's exact input string.

## Delivery method, mapped to browser primitives

| Your phrasing | What it is here |
|---|---|
| "machine code" | **WebAssembly** compiled from your Rust (`cargo build --target wasm32-unknown-unknown`) |
| "runs in a sandbox" | **Web Worker** (no DOM/page access) + WASM's memory-safe sandbox |
| "clones / re-loads every run" | New Worker + re-fetched `program.wasm` (`cache: 'no-store'`) + fresh WASM instance, torn down each run |
| "in a browser extension" | **Manifest V3** extension |

## Load it (Chrome / Edge / Brave)

1. Go to `chrome://extensions`.
2. Enable **Developer mode** (top-right).
3. **Load unpacked** → select this folder (`sandboxed-wasm-runner`).
4. Click the icon, set a difficulty (start at 4), press **Mine block in fresh sandbox**.

The log shows each run mining in its own instance, which is then destroyed.

## Rebuild the WASM after changing the Rust

The crate source is on the `marev1-wasm` branch (folder `marev1-wasm-build`):

```
cd marev1-wasm-build
cargo build --release --target wasm32-unknown-unknown
copy target\wasm32-unknown-unknown\release\marev1_wasm.wasm ..\sandboxed-wasm-runner\program.wasm
```

Exports (all numbers-only, so no wasm-bindgen needed):
- `mine(index, timestamp, prev_hash_seed, difficulty, max_iters) -> nonce` (`u32::MAX` = not found)
- `hash_block(index, timestamp, prev_hash_seed, nonce) -> leading_zero_count`
- `hash_ptr() -> ptr` — the 32-byte result hash in linear memory (JS hex-encodes it)

To expose more of marev1 (e.g. order-book matching from `src/orderbook.rs`), add
`#[no_mangle] pub extern "C"` functions to `marev1-wasm-build/src/lib.rs` and call
them from `worker.js`.

## What this intentionally does NOT do

It never downloads or executes code from a remote server — that pattern is banned
by MV3 and is the classic unreviewable-payload vector. All executed code lives in
this folder and is inspectable.
