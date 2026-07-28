// Popup UI. On each click it creates a BRAND-NEW Worker (a fresh sandbox),
// mines a marev1 block inside it via the bundled WASM, shows the result, then
// terminates the Worker so no state survives to the next run.

const runBtn = document.getElementById('run');
const out = document.getElementById('out');
const logEl = document.getElementById('log');
let runCount = 0;

// Default the timestamp field to the current unix time (like marev1's Block::new).
const tsInput = document.getElementById('timestamp');
if (!Number(tsInput.value)) tsInput.value = Math.floor(Date.now() / 1000);

runBtn.addEventListener('click', () => {
  const index = int('index');
  const timestamp = int('timestamp');
  const prevSeed = int('prevSeed');
  const difficulty = int('difficulty');
  const maxIters = int('maxIters');
  const id = ++runCount;

  out.textContent = 'mining…';
  appendLog(`> run #${id}: spawning fresh sandbox, difficulty ${difficulty}…`);

  // A new Worker per run = a clean, isolated execution context every time.
  const worker = new Worker('worker.js');

  worker.onmessage = (e) => {
    const d = e.data;
    if (d.error) {
      out.textContent = 'Error: ' + d.error;
      appendLog(`x run #${id}: ${d.error}`);
    } else if (!d.found) {
      out.textContent = `No nonce found within ${maxIters} iterations.`;
      appendLog(`- run #${id}: not found (${d.elapsed} ms)`);
    } else {
      out.innerHTML =
        `<span class="k">nonce:</span> ${d.nonce}<br>` +
        `<span class="k">hash:</span> ${d.hash}<br>` +
        `<span class="k">time:</span> ${d.elapsed} ms`;
      appendLog(`ok run #${id}: nonce ${d.nonce} in ${d.elapsed} ms, sandbox destroyed`);
    }
    worker.terminate(); // tear down the sandbox — nothing persists
  };

  worker.onerror = (err) => {
    out.textContent = 'Worker error: ' + err.message;
    appendLog(`x run #${id}: worker error`);
    worker.terminate();
  };

  worker.postMessage({ index, timestamp, prevSeed, difficulty, maxIters });
});

function int(id) {
  return parseInt(document.getElementById(id).value, 10) || 0;
}

function appendLog(msg) {
  const line = document.createElement('div');
  line.textContent = msg;
  logEl.prepend(line);
}
