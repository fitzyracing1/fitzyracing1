chrome.runtime.onInstalled.addListener(details => {
  if (details.reason === "install") {
    chrome.storage.local.set({ firstRun: true });
    chrome.tabs.create({ url: chrome.runtime.getURL("welcome.html") });
  }
});

// Handle keyboard command shortcuts (Alt+S / Alt+K by default)
chrome.commands.onCommand.addListener(command => {
  if (command !== "save_step" && command !== "open_paths") return;
  chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
    const tab = tabs[0];
    if (!tab || !tab.id) return;
    chrome.tabs.sendMessage(tab.id, { type: command });
  });
});
