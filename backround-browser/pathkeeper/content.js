(function () {
  const getPathMeta = () => ({
    url: location.href,
    title: document.title,
    h1: (document.querySelector("h1") || {}).innerText || "",
    ts: Date.now()
  });

  const KEY_SAVE = e => e.altKey && e.key.toLowerCase() === "s";
  const KEY_OPEN = e => e.altKey && e.key.toLowerCase() === "k";

  chrome.storage.local.get(["paths"], data => {
    const paths = data.paths || {};
    const domain = location.hostname;

    if (paths[domain]) {
      const banner = document.createElement("div");
      banner.textContent = "Pathkeeper: Alt+K to open saved paths";
      Object.assign(banner.style, {
        position: "fixed", bottom: "16px", right: "16px",
        background: "#111", color: "#fff", padding: "8px 12px",
        borderRadius: "8px", font: "14px system-ui", zIndex: 999999
      });
      document.body.appendChild(banner);
      setTimeout(() => banner.remove(), 3000);
    }

    const toast = (text) => {
      try {
        const t = document.createElement("div");
        t.textContent = text;
        Object.assign(t.style, {
          position: "fixed", bottom: "16px", right: "16px",
          background: "#111", color: "#fff", padding: "8px 12px",
          borderRadius: "8px", font: "12px system-ui", zIndex: 2147483647,
          boxShadow: "0 2px 8px rgba(0,0,0,.3)", opacity: "0.95"
        });
        document.body.appendChild(t);
        setTimeout(() => t.remove(), 1500);
      } catch (e) {}
    };

    toast("Pathkeeper active: Alt+S save, Alt+K open");

    const saveStep = () => {
      const note = prompt("Label this step:");
      if (!note) return;
      const entry = { ...getPathMeta(), note };
      const list = paths[domain] || [];
      list.push(entry);
      paths[domain] = list.slice(-50);
      chrome.storage.local.set({ paths }, () => alert("Step saved"));
    };

    const openPaths = () => {
      const list = paths[domain] || [];
      if (!list.length) return alert("No saved paths here yet.");
      const menu = list.map((p, i) => `${i + 1}. ${p.note || p.title}`).join("\n");
      const idx = parseInt(prompt("Open which path?\n" + menu)) - 1;
      if (idx >= 0 && idx < list.length) location.href = list[idx].url;
    };

    // Page-level key listener (Alt+S / Alt+K) with capture for reliability
    const keyHandler = (e) => {
      if (KEY_SAVE(e)) { toast("Alt+S detected"); saveStep(); }
      if (KEY_OPEN(e)) { toast("Alt+K detected"); openPaths(); }
    };
    window.addEventListener("keydown", keyHandler, true);
    document.addEventListener("keydown", keyHandler, true);

    // Command messages from the background service worker
    chrome.runtime.onMessage.addListener((msg) => {
      if (msg && msg.type === "save_step") { toast("Command: save"); saveStep(); }
      if (msg && msg.type === "open_paths") { toast("Command: open"); openPaths(); }
    });
  });
})();
