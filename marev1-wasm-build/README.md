# marev1-wasm-build

The `marev1` proof-of-work (from `marev1/src/block.rs`) ported to a WebAssembly
`cdylib`. Produces the `program.wasm` used by the extension on the
`wasm-extension` branch.

## Build

```
cargo build --release --target wasm32-unknown-unknown
# output: target/wasm32-unknown-unknown/release/marev1_wasm.wasm
```

Requires the wasm target once: `rustup target add wasm32-unknown-unknown`.

## Exports (numbers-only C ABI — no wasm-bindgen)

- `mine(index, timestamp, prev_hash_seed, difficulty, max_iters) -> nonce`
  (`u32::MAX` if no nonce found within `max_iters`)
- `hash_block(index, timestamp, prev_hash_seed, nonce) -> leading_zero_count`
- `hash_ptr() -> ptr` — address of the 32-byte result hash in linear memory

The hashing is `SHA256(index | timestamp | "" | prev_hash | nonce)`, identical to
marev1's native `Block::calculate_hash` for an empty transaction set.
