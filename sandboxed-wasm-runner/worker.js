// The sandbox. Runs inside a Web Worker (no DOM, no page access).
// On every message it RE-LOADS the bundled marev1 WASM fresh (cache: 'no-store'),
// instantiates a new WASM sandbox, mines a block, and returns the result.
// The popup terminates this Worker after each run, so every run is a clean slate.

self.onmessage = async (e) => {
  const { index, timestamp, prevSeed, difficulty, maxIters } = e.data;
  try {
    // Re-read the bundled machine code on every run. 'no-store' guarantees a
    // genuine reload of the program each time (no cache reuse).
    const resp = await fetch('program.wasm', { cache: 'no-store' });
    const bytes = await resp.arrayBuffer();

    // Fresh WASM instance in this Worker's isolated memory. This is your
    // marev1 proof-of-work (src/block.rs) compiled to machine code.
    const { instance } = await WebAssembly.instantiate(bytes, {});
    const { mine, hash_ptr, memory } = instance.exports;

    const t0 = performance.now();
    const raw = mine(
      index >>> 0, timestamp >>> 0, prevSeed >>> 0, difficulty >>> 0, maxIters >>> 0
    );
    const elapsed = performance.now() - t0;

    const nonce = raw >>> 0;                 // treat as unsigned u32
    const found = nonce !== 0xFFFFFFFF;       // u32::MAX == not found

    // Read the 32-byte hash the wasm wrote into linear memory, hex-encode it.
    const mem = new Uint8Array(memory.buffer, hash_ptr(), 32);
    const hash = Array.from(mem).map((x) => x.toString(16).padStart(2, '0')).join('');

    self.postMessage({ found, nonce, hash, elapsed: Math.round(elapsed) });
  } catch (err) {
    self.postMessage({ error: String((err && err.message) || err) });
  }
};
