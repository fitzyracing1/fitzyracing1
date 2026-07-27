// Background service worker for Pathkeeper
chrome.runtime.onInstalled.addListener(() => {
  console.log('Pathkeeper extension installed');
});

// Store paths unencrypted in sync for global commands to keep simple
function getPaths() {
  return new Promise(resolve => {
    chrome.storage.sync.get("paths", data => {
      resolve(data.paths || {});
    });
  });
}

function setPaths(paths) {
  return new Promise(resolve => {
    chrome.storage.sync.set({ paths }, resolve);
  });
}

async function saveCurrentTabUrl() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.url) return;
  const paths = await getPaths();
  const id = Date.now().toString();
  paths[id] = tab.url;
  await setPaths(paths);
}

async function copyLatestPath() {
  const paths = await getPaths();
  const latestKey = Object.keys(paths).sort().pop();
  if (!latestKey) return;
  const latest = paths[latestKey];
  try {
    await navigator.clipboard.writeText(latest);
  } catch (e) {
    // Fallback: write via a temporary offscreen document
    try {
      await chrome.offscreen.createDocument({
        url: chrome.runtime.getURL("popup.html"),
        reasons: ["CLIPBOARD"],
        justification: "Copy latest path via offscreen document"
      });
    } catch (_) {}
    chrome.runtime.sendMessage({ type: "COPY_TO_CLIPBOARD", text: latest });
  }
}

chrome.commands.onCommand.addListener(async command => {
  if (command === "save-current-path") {
    await saveCurrentTabUrl();
  } else if (command === "copy-latest-path") {
    await copyLatestPath();
  }
});
