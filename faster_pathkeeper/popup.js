import { encryptData, decryptData } from "./crypto.js";

const passphrase = "your‑chosen‑passphrase"; // prompt user on first run

async function savePaths(paths) {
  const encrypted = await encryptData(passphrase, paths);
  chrome.storage.sync.set({ paths: encrypted });
}

async function loadPaths() {
  return new Promise(resolve => {
    chrome.storage.sync.get("paths", async data => {
      if (!data.paths) return resolve({});
      try {
        const decrypted = await decryptData(passphrase, data.paths);
        resolve(decrypted);
      } catch (e) {
        console.error("Decryption failed", e);
        resolve({});
      }
    });
  });
}

// UI wiring and keyboard shortcuts (Alt+S, Alt+K)
document.addEventListener("DOMContentLoaded", async () => {
  const input = document.getElementById("pathInput");
  const addBtn = document.getElementById("addPath");
  const listEl = document.getElementById("pathsList");
  const clearBtn = document.getElementById("clearAll");

  let paths = await loadPaths();

  function render() {
    listEl.innerHTML = "";
    const entries = Object.entries(paths);
    if (entries.length === 0) {
      listEl.textContent = "No saved paths yet.";
      return;
    }
    entries.forEach(([key, value]) => {
      const item = document.createElement("div");
      item.className = "path-item";
      const text = document.createElement("span");
      text.textContent = value;
      const copyBtn = document.createElement("button");
      copyBtn.textContent = "Copy";
      copyBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(value).catch(() => {});
      });
      item.appendChild(text);
      item.appendChild(copyBtn);
      listEl.appendChild(item);
    });
  }

  function addPathFromInput() {
    const val = (input.value || "").trim();
    if (!val) return;
    const id = Date.now().toString();
    paths[id] = val;
    savePaths(paths);
    input.value = "";
    render();
  }

  addBtn.addEventListener("click", addPathFromInput);
  clearBtn.addEventListener("click", () => {
    paths = {};
    savePaths(paths);
    render();
  });

  // Shortcut: Alt+S -> add current input as path
  // Shortcut: Alt+K -> copy most recent saved path
  window.addEventListener("keydown", e => {
    if (!e.altKey) return;
    if (e.code === "KeyS") {
      e.preventDefault();
      addPathFromInput();
    } else if (e.code === "KeyK") {
      e.preventDefault();
      const latestKey = Object.keys(paths).sort().pop();
      if (latestKey) {
        const latest = paths[latestKey];
        navigator.clipboard.writeText(latest).catch(() => {});
      }
    }
  });

  render();
});