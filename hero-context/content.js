// ─── HERO CONTEXT ────────────────────────────────────────────────
// Linear divide: root ÷ position
// Root = 100
// Result 1: 100 ÷ 1 = 100
// Result 2: 100 ÷ 2 = 50
// Result 3: 100 ÷ 3 = 33.3 … and so on
// ─────────────────────────────────────────────────────────────────

const HERO_ROOT = 100;

function heroScore(position) {
  // Linear divide: root divided by position index
  return HERO_ROOT / position;
}

function applyHeroContext() {
  // Google search result containers
  const results = document.querySelectorAll("div.g, div[data-hveid]");

  let position = 1;

  results.forEach((result) => {
    // Skip if already labelled or not a real result block
    if (result.querySelector(".hero-badge")) return;
    if (!result.querySelector("h3")) return;

    const score = heroScore(position);

    // Build the hero badge
    const badge = document.createElement("div");
    badge.className = "hero-badge";
    badge.innerHTML = `
      <span class="hero-label">HERO</span>
      <span class="hero-score">${score % 1 === 0 ? score : score.toFixed(2)}</span>
      <span class="hero-formula">${HERO_ROOT} ÷ ${position}</span>
    `;

    // Style the badge
    badge.style.cssText = `
      display: inline-flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 4px;
      font-family: 'Google Sans', sans-serif;
      font-size: 11px;
    `;

    const label = badge.querySelector(".hero-label");
    label.style.cssText = `
      background: #1a73e8;
      color: #fff;
      font-weight: 700;
      font-size: 10px;
      letter-spacing: 0.08em;
      padding: 2px 6px;
      border-radius: 3px;
    `;

    const scoreEl = badge.querySelector(".hero-score");
    scoreEl.style.cssText = `
      font-weight: 700;
      font-size: 13px;
      color: #1a73e8;
    `;

    const formulaEl = badge.querySelector(".hero-formula");
    formulaEl.style.cssText = `
      color: #5f6368;
      font-size: 11px;
    `;

    // Insert badge at the top of the result
    result.insertBefore(badge, result.firstChild);

    position++;
  });
}

// Run on load
applyHeroContext();

// Re-run if Google loads more results dynamically
const observer = new MutationObserver(() => applyHeroContext());
observer.observe(document.body, { childList: true, subtree: true });
